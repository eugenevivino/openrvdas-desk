# Brief: p2-device-servers (Serial device servers, vendor-neutral: Moxa and Pepperl+Fuchs first, read-only)

- Decision: IDEAS #157, D-SHIP1, D-NOC1, from Eugene's 2026-11-18 ask: "integrate VERY well with Moxas and
  Pepperl+Fuchs devices"; build per D-NIGHT1
- Risk tier: medium (talks to devices on the instrument LAN: SNMP and HTTP reads, optional discovery broadcast)
- Module: exactly one. Branch `deepsignal/p2-device-servers` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 5/2/3
- Depends on: none to build. Publishes fields that #156 link health folds into each link verdict; reads
  the cruise definition the same way #127 config lint does (YAML by path, no import)

## Goal
Every serial instrument on the ship goes through a Moxa NPort or a Pepperl+Fuchs Comtrol DeviceMaster. A
tech sees, per port: which logger uses it, the port's real settings (baud, data bits, parity, stop bits,
mode), whether a client is connected, bytes in and out, and framing, parity and overrun error counts, with a
plain warning when they disagree with what OpenRVDAS expects. For a new device server, DeepSignal writes the
reader config for each port.

## Background facts (do not re-derive)
- Base is the contrib `master` tree at `3b4b76e`: it carries a 2024 core tree (old Transform base class,
  no BaseModule). Copy the import-compatibility approach of
  `git show origin/deepsignal/vector-wind:contrib/deepsignal/logger/transforms/vector_wind_average_transform.py`
  so the module also works on current core. If that branch is unreadable, write plain absolute imports
  and say so.
- Create empty `__init__.py` files only where missing, byte-identical to the wind branch (empty), so
  parallel branches merge cleanly.
- OpenRVDAS loads classes from a config with `class:` plus `module:` (for example
  `module: contrib.deepsignal.<module>.<file>`). Records may arrive as a DASRecord, a dict with
  `timestamp` and `fields`, a list of either, or None; handle all, pass None through.
- File ownership is disjoint across phase 2 tasks: you own ONLY the paths under Scope.
- Design and safety context: desk `docs/SHIP-SYSTEMS.md` section 11 and decisions D-SHIP1, D-NOC1. This module
  READS device servers only. It never changes a port setting; changes go through #153 and #155 later.

- Device facts (leads from vendor documentation; verify on the pilot ship, never hard-code):
  - Moxa NPort: SNMP agent (v1, v2c, v3) with MIB-II plus a Moxa private MIB for port settings and serial
    statistics; web console pages for serial port status, line status and counters; Moxa's Device Search
    Utility finds devices by UDP broadcast; newer models (for example NPort 6000-G2) add a RESTful API. In
    TCP server mode, data ports default to 4001 for port 1 and count up. TCP server mode allows a small
    number of clients (often 1 by default), so a probe on a data port can drop the logger.
  - Pepperl+Fuchs Comtrol DeviceMaster: SNMP (MIB-II), web pages with per-port statistics, PortVision DX
    discovery, socket-server mode per port, NS-Link driver giving local tty devices.
  - OUI (first three bytes of the MAC address) identifies the vendor with no traffic at all: Moxa `00:90:E8`,
    Comtrol `00:C0:4E` (confirm both, and add the other vendors' prefixes, from the public IEEE registry
    as an offline data file; never guess a prefix).
  - Other vendors on ships (Digi PortServer and ConnectPort, Lantronix, Perle, B&B and Advantech,
    Brainboxes, Sena) almost all answer SNMP MIB-II, and many implement the standard RS-232-like MIB
    (RFC 1659: per-port speed, and framing, parity and overrun error counters). That is the generic fallback.
  Eugene 2026-11-18: "and other similar devices". So the design is vendor-neutral (below), with the OID
  tables and HTTP paths in YAML data files (`device_servers/drivers/*.yaml`), not in code, so a ship fixes a
  firmware difference or adds a vendor without a code change.

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/device_servers/`:
- Driver interface `DeviceServerDriver`: `identify(facts) -> confidence` (facts: OUI, SNMP `sysObjectID`
  and `sysDescr`, HTTP banner), `read_ports(device) -> list[PortStatus]`, `capabilities()` (which fields it
  can fill). `PortStatus` is one vendor-neutral dataclass; a field a driver cannot read is None, shown as
  "not reported", never zero. Drivers in v1: `moxa`, `pepperl_fuchs` (Comtrol DeviceMaster),
  `generic_snmp` (MIB-II plus RFC 1659 RS-232-like MIB; used for every other vendor and as the fallback
  when a vendor driver fails). Selection: highest `identify` confidence, then `generic_snmp`.
- Telnet fallback: interface and docs only, NOT built in v1. Telnet sends the admin password in clear
  text, opens an admin session that can change settings, and on some models ends another admin's session.
  If a later brief adds it: opt-in per device, allowlisted read commands only, credentials from the secrets
  file, full transcript logged, and only where the device offers neither SNMP nor HTTP.
- Inventory `device_servers.yaml` (written by discovery, edited by a tech): per device `name`, `vendor`,
  `host`, `model`, `driver` (auto or a name), `ports` count, `read_via` (`snmp` or `http`), credentials reference (`secret: <name>`
  pointing into a file outside the repo, mode 600, never in configs or logs).
- Discovery, in order, all opt-in by flag:
  1. Passive: read the host ARP and neighbor table (`/proc/net/arp`, `ip neigh` output) and match OUIs.
  2. Config: hosts named by `TCPReader`, `SocketReader` or `UDPReader` configs in the cruise definition.
  3. Active, off by default: one vendor discovery broadcast on an interface the tech names, on a subnet
     listed in the #151 OT connection register file if present. No sweeps, no port scans (same rule as #125).
- Reader: `DeviceServerReader(Reader)` polls each device every `interval_s` (default 60, minimum 30) with
  SNMP GET or HTTP GET only and returns one record with fields `ds:<device>:<port>:baud`, `:framing` (like
  `8N1`), `:mode`, `:clients`, `:rx_bytes`, `:tx_bytes`, `:rx_rate`, `:err_frame`, `:err_parity`,
  `:err_overrun`, `:err_rate_5m`, `:reachable`, `:read_error`. SNMP: implement only GET and GETNEXT for v2c
  in pure Python over UDP (BER encoding is small; no new dependency); v3 is a later item, so document it.
  HTTP: stdlib `urllib`, read-only GET, never a login that could end another admin's session; if a vendor
  page needs a login, report "needs SNMP or credentials" instead of trying.
- Mapper: `map_ports(cruise: dict, inventory: dict) -> dict` joins each port to the logger and reader that
  use it (TCP host and port, UDP port, or a local tty from Real COM or NS-Link listed in the inventory).
- Checks (advice only, never applied): baud or framing on the device differs from the logger's device
  definition or reader kwargs; framing or parity errors rising (classic baud mismatch); logger RUNNING but
  device port has 0 clients (logger not connected); clients 1 and bytes flowing but cache field stale
  (parsing problem, not wiring); rx bytes flat while logger RUNNING (instrument or cable); two readers
  targeting one single-client port; port in use by no logger.
- Config generator: `generate_readers(inventory, port_map, device_defs) -> dict` emits reader configs
  (TCPReader for TCP server mode, UDPReader for UDP mode, SerialReader for a Real COM or NS-Link tty) with a
  diff against the current cruise definition. Writes a new file; never edits the cruise file.
- Pure, JSON-safe functions for the setup engine (detect, propose, diff), same pattern as #127.
- No writes to devices. The later apply path (#153, #155) will add port-setting changes with backup export,
  a named approval, verify and rollback; leave a `proposals` list in check output for it.

## Failing test first
`contrib/deepsignal/test/device_servers/test_device_servers.py`: SNMP BER encode and decode against
hand-built packets; a fake SNMP agent and a fake HTTP server on 127.0.0.1 per driver (moxa, pepperl_fuchs, generic_snmp with
RFC 1659 counters); driver selection and fallback when a vendor driver fails; unknown fields shown as None; OUI matching from a
sample ARP table; config-based discovery from the NBP1406 cruise; port mapping; every check fires on its
fixture and stays quiet on a healthy fixture; generated readers and diff; secrets never appear in output
or logs; active discovery refuses to run without the flag and a named interface; poll interval floor;
read errors reported, never raised.

## Module contract
Docs `contrib/deepsignal/docs/device_servers.md`: what to enable on each vendor (SNMP read-only community
or v3 user, which MIBs), why SNMP is preferred over web login, the single-client warning, each check with
what to do. Sample configs `contrib/deepsignal/configs/device_servers_demo.yaml` and
`contrib/deepsignal/configs/device_servers_inventory.yaml`. Depends on no other module.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/device_servers -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/device_servers contrib/deepsignal/test/device_servers
```

## Scope
Create or change only: `contrib/deepsignal/device_servers/**`, `contrib/deepsignal/test/device_servers/**`,
`contrib/deepsignal/docs/device_servers.md`, `contrib/deepsignal/configs/device_servers_*.yaml`, and empty
`__init__.py` files where missing. Everything else is read-only.

## Usability (anything a tech sees or edits)
Answer each line of desk `docs/USABILITY.md` in the report, or N/A with a reason. Every check names the
device, port, logger, what it saw, what it expected and the first thing to try ("Moxa NPort lab-1 port 3
(logger gyro) runs 4800 8N1; the gyro device definition expects 9600. Framing errors rising. Set the
port to 9600 in the NPort web console, or approve the change when apply ships.").

## Trust boundaries and data integrity
Device replies are untrusted: bound every BER length, cap OID walks at 2000 rows, `json.loads` only, size
caps on HTTP bodies, no `eval`, no shell interpolation. Credentials only from the secrets file; redact in
all output. Never change incoming fields.

## Non-goals and banned
No writes to any device (no SNMP SET, no HTTP POST, no Telnet). No probes of data ports. No subnet sweeps or
port scans. No new dependency, no core changes, no refactors outside Scope. No loosened, skipped or deleted
tests, no swallowed errors, no sleeps for ordering.

## Stop rule
No code change needed: stop and report. Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Acceptance tails:
- Open questions:
