# Brief: p2-stream-discovery (Stream auto-discovery (serial, UDP, MQTT, Redis, CDS, files))

- Decision: D-PARITY1, IDEAS #125 (Eugene approved building #104-#124, 2026-11-18)
- Risk tier: medium
- Module: exactly one. Branch `deepsignal/p2-stream-discovery` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 5/2/3
- Depends on: none; its captures feed #114 onboarding wizard

## Goal
A tech runs one command and sees every live data stream the box can hear (serial ports with their baud
rate, UDP ports, MQTT topics, Redis channels, cache fields, growing files), how fast, with sample lines,
without writing anything anywhere.

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
- `pyserial` is already an OpenRVDAS dependency (core `SerialReader` uses it). Use only it and the stdlib.

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/discovery/`:
- `serial_scan.py`: list candidate ports (`serial.tools.list_ports` plus `/dev/ttyS*`, `/dev/ttyUSB*`,
  `/dev/ttyACM*` globs). For each port and each baud rate in `[4800, 9600, 19200, 38400, 57600, 115200]`,
  open read-only with a short timeout, read for `listen_s` (default 3 s), close. NEVER write a byte to a
  port (polled devices that only answer queries are reported as "silent: may need polling"). Skip ports
  another process holds and say so; never steal a lock.
- Scoring per baud: share of printable ASCII, line endings seen, NMEA checksum validity. The best baud
  wins only if its printable share is at least 0.9; otherwise "unreadable at all tried rates".
- `udp_scan.py`: passive listen on a port list or range (default the ports in the cruise definition plus
  `6221-6230`, configurable), `listen_s` per port, report rate and sample lines. Binding a port already in
  use is skipped and reported.
- Other transports, each optional (skipped with a plain note when its library is not installed or no
  target is given), all strictly read-only:
  - `mqtt_scan.py`: with `--mqtt host[:port]` and `paho-mqtt` importable, subscribe to `#` for `listen_s`,
    report topics, message rate and payload samples (first 200 bytes, shown as text if printable). Never
    publish. Credentials only from a file path given on the command line, never echoed.
  - `redis_scan.py`: with `--redis host[:port]` and `redis` importable: `PUBSUB CHANNELS`, then listen
    to each channel for `listen_s`; `SCAN` at most 1000 keys with types. No writes.
  - `cds_scan.py`: with `--cds host:port`: the CachedDataServer field list (HTTP `/fields` on current core,
    else the websocket `fields` request) with latest timestamps, so a tech sees what is already flowing.
  - `file_scan.py`: with `--files DIR`: data files modified in the last hour, growth rate and sample
    lines (for `LogfileReader`/`TextFileReader` setups).
  - TCP and HTTP: only explicit `--tcp host:port` or `--http URL` targets; connect and read, or one GET.
- Banned: scanning address ranges or other hosts' ports on the ship network. Only local serial devices,
  local UDP ports, and targets a person names.
- Output: a table on screen and `discovery.json` with port, transport, baud, lines per second, first 5
  lines, NMEA talker and sentence ids seen; `--capture DIR` saves up to 200 lines per stream as text files
  ready for `python -m contrib.deepsignal.onboard`.
- Every hardware touch is behind an injectable opener, so tests use fakes.

## Failing test first
`contrib/deepsignal/test/discovery/test_discovery.py` with fake serial and UDP sources: picks 4800 for an
NMEA stream at 4800 and rejects garbage at other rates; silent port; busy port skipped; no write method on
the fake is ever called (assert); UDP rate estimate; capture files written; JSON shape.

## Module contract
Docs `contrib/deepsignal/docs/discovery.md` ("plug it in, run this, then run the wizard"), with the
warning that scanning a port a running logger uses is skipped by design. A lead-run check on real
hardware happens outside the sandbox. Depends on no other module.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/discovery -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/discovery contrib/deepsignal/test/discovery
```

## Scope
Create or change only: `contrib/deepsignal/discovery/**`, `contrib/deepsignal/test/discovery/**`, `contrib/deepsignal/docs/discovery.md`, `contrib/deepsignal/configs/discovery_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

## Usability (anything a tech sees or edits)
Answer each line of desk `docs/USABILITY.md` in the report, or N/A with a reason. Every config error is one
plain-English line naming the setting, what it saw, what it expected, and a good example.

## Trust boundaries and data integrity
Config and input files are hand-edited and untrusted: `yaml.safe_load` only, no `eval`. Never change or
drop an incoming value; only add fields or write new files. Missing or stale inputs are shown as such,
never guessed.

## Non-goals and banned
No core changes. No new dependency. No network. No refactors, renames or formatting outside Scope. No
loosened, skipped or deleted tests, no swallowed errors, no sleeps for test ordering.

## Stop rule
No code change needed: stop and report. Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Acceptance tails:
- Open questions:
