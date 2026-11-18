# DeepSignal and the ship's other systems: sonars, motion, bridge, engineering, instrument configuration

Written 2026-11-18 by the ship-systems thread for Eugene's two asks:

1. "Interface with other sonars and systems somehow ... either passive through reading their data, or actively
   through some kind of pathway."
2. "Help configure instruments, perhaps even dynamically. Intelligently, even if it means ssh'ing in."

IDEAS #138 to #160. Decisions D-SHIP1 and D-NOC1. Briefs: `briefs/p2/138-iec450-bridge.md`,
`briefs/p2/139-kongsberg-tap.md`, `briefs/p2/140-sv-consistency.md`, `briefs/p2/141-depth-consensus.md`,
`briefs/p2/156-link-health.md`, `briefs/p2/157-device-servers.md`, `briefs/p2/158-seismic-shot-qc.md`, `briefs/p2/145-adcp-health.md`.

**Evidence level.** Interface facts below come from vendor documentation and fleet practice as known to the
lead; each row marks what is verified in the OpenRVDAS source (V) versus a lead to confirm on a real ship (L).
Ports, multicast groups and datagram versions differ per ship and per software release: every module takes
them as config, never hard-coded. The shadow-pilot ship (#70) is where L rows become V rows.

## 1. The answer in one paragraph

**Recommendation: passive first, and for sonars and the bridge, passive forever.** Almost all of the value
(health, cross-checks, alarms a tech trusts) comes from *listening*: the sonars, the motion systems and the
bridge already broadcast what DeepSignal needs on UDP, serial and files. OpenRVDAS core can already receive
nearly all of it (UDP unicast and multicast, raw bytes, TCP, Modbus, serial). What is missing is the
*understanding*: parsers for the binary sonar and motion formats, and cross-checks between systems that no
single vendor does because no vendor sees all of them. That is DeepSignal's lane. Active pathways exist, but
the sonar and bridge ones are where a mistake costs a survey day or a safety incident, so they stay closed.
The one active pathway worth building is **instrument configuration for science sensors**, done as
"propose, approve, apply, verify, roll back", on the same engine as #130 init profiles.

## 2. Three tiers of interface

| Tier | What DeepSignal does | Where it is allowed |
|---|---|---|
| P: Passive | Receives what a system already emits (multicast join, UDP listen, file tail, serial read, Modbus read) | Everywhere, through the network rules in section 6 |
| R: Read by query | Asks a system for its config or status (serial query command, vendor read API, SSH read command) | Science instruments and DAS hosts. Never bridge, DP or sonar transmit control |
| A: Apply | Changes a setting, only after a human approves that one change, with backup, verify and rollback | Science instruments on the allowlist only (section 7). Never sonar, bridge, DP, ECDIS, engine or winch control |

**Hard rule (D-SHIP1):** DeepSignal never changes sonar, bridge, DP, ECDIS, engine, power or winch settings,
automatically or on approval. It may *recommend* (for example "SIS is using SV 1503.2, the probe reads
1509.8, enter a new value or take a cast"), and a person makes the change in the vendor's own software.

## 3. System by system

Legend: Core = what OpenRVDAS reads today. V = verified in the OpenRVDAS v2.7.2 source; L = lead to confirm.

### 3.1 Multibeam: Kongsberg EM series (EM124, EM304, EM712, EM2040 on SIS 5 / K-Controller; EM122, EM302, EM710 on SIS 4)

- **Emits:** binary datagrams. SIS 5 uses the KMALL format (`#MRZ` ping depths and beam data, `#SPO` position,
  `#SKM` attitude, `#SVT` sound speed at transducer, `#SVP` profile in use, `#IIP` install params, `#IOP`
  runtime params, `#SCL` clock, `#CPO` compatibility position) (L). SIS 4 uses the `.all` format (XYZ88 depth
  `X`, position `P`, attitude `A`/`n`, clock `C`, surface sound speed `G`, SV profile `U`, runtime `R`,
  install `I`) (L). Both go to `.kmall` / `.all` files on the SIS PC and can be distributed live over UDP to
  third parties, set up in SIS / K-Controller by the operator (L). Many installs also send NMEA depth
  (`$KIDPT`, `$xxDPT`) over serial or UDP.
- **Core:** `UDPReader` can join multicast (`mc_group`) and return raw bytes when `encoding` is null, buffer
  65535 bytes (V). `contrib/devices/misc_device_types.yaml` parses `$KIDPT` from an EM122 (V). No KMALL or
  `.all` parser (V).
- **DeepSignal adds:** #139 Kongsberg tap (summary, not bathymetry: nadir depth, ping rate, swath width,
  valid-beam fraction, SV at transducer as used, runtime-parameter hash, PU clock vs host clock). Feeds #140 SV
  consistency, #141 depth consensus, #142 time and motion alignment, #143 sonar health, #144 transmit awareness.
- **Active pathways:** SIS 5 / K-Controller has a remote interface used by third-party survey software and
  K-Sync (L). Risk: **critical**. Wrong settings ruin a survey and transmit settings matter for marine-mammal
  mitigation permits. **Not planned.**

### 3.2 Single-beam and echosounders: Knudsen 3260 and Chirp, Kongsberg EA440/EA640, EK80

- **Emits:** NMEA-like depth strings (Knudsen `$PKEL99` with LF and HF depth, sound speed and position; EA/EK
  `$xxDPT`, `$xxDBT`) on serial or UDP (Knudsen V via device file, EA/EK L). EK80 also offers a network
  subscription interface (bottom detection, sample data) and writes `.raw` files (L).
- **Core:** device type `Knudsen3260` parses all `$PKEL99` variants (V). Generic NMEA depth through the
  parse transforms (V).
- **DeepSignal adds:** depth consensus #141; bottom-lock loss and depth-step detection; echosounder noise
  floor as a machinery and interference signal (#92, needs EK80 subscription or `.raw` tail, later).
- **Active pathways:** EK80 remote interface can change ping settings and start or stop pinging (L);
  Knudsen has a remote control program (L). Risk: **high** (interferes with other sonars and with science
  acquisition). **Not planned.**

### 3.3 Sub-bottom profilers: Knudsen Chirp 3260, Kongsberg SBP29 and SBP120

- **Emits:** mostly files (SEG-Y, Knudsen `.keb`/`.kea`, Kongsberg raw), plus the depth strings above (L).
- **Core:** depth strings only.
- **DeepSignal adds:** file-growth heartbeat (is it logging, ping rate from file size per minute), included
  in #143 sonar health. Ping timing into #144.
- **Active:** none planned.

### 3.4 ADCP: Teledyne RDI Ocean Surveyor and Workhorse via UHDAS or VmDAS

- **Emits:** PD0 binary ensembles on serial (to the acquisition PC). UHDAS (the University of Hawaii system
  on most UNOLS ships) writes raw and processed files, serves status web pages, sends daily status email and
  publishes a speed log string `$PUHAW` (L, `$PUHAW` V in device file). VmDAS writes ENR/ENS/ENX/STA/LTA and
  can re-output NMEA (L).
- **Core:** device type `ADCP_OS75` parses `$PUHAW` and `$VDVBW` (V).
- **DeepSignal adds:** #145 ADCP health: ensemble cadence, bottom-track percent good, ADCP heading versus
  gyro and Seapath (a classic UHDAS failure), built-in test words when PD0 is visible. Never touches the
  ADCP serial line: reads a UHDAS or VmDAS output, or a passive serial tap (Y-cable, receive only).
- **Active:** ADCP command set is rich (Teledyne `CR`, `WP`, `BP`...). Owned by UHDAS. **Not planned.**

### 3.5 Motion and position: Kongsberg Seapath 330/380/385, Applanix POS MV

- **Emits:** Seapath: NMEA (`GGA`, `VTG`, `HDT`, `ZDA`, `$PSXN` attitude) and binary attitude (EM3000 and
  Kongsberg binary formats) at up to 100 Hz on UDP and serial (Seapath NMEA V in device file, binary L). POS
  MV: Ethernet "Group" messages on a display port and a real-time data port (Group 1 navigation, Group 2
  performance RMS, Group 3 GNSS status, Group 10 general status and fault detection, Group 102 and 111
  heave), plus NMEA on serial; a separate control port accepts commands (L, port numbers per ICD).
- **Core:** `Seapath200`, `Seapath330`, `Seapath380` device types parse the NMEA strings (V). No POS MV
  Group parser (V).
- **DeepSignal adds:** #146 motion-system status (RMS errors, GNSS fix type and satellite count, IMU status,
  heave filter state, alignment status), #142 latency and lag between the motion feed and what the sonar
  recorded, attitude dropouts, heading disagreement with gyro.
- **Active:** POS MV control port can reconfigure lever arms, outputs and alignment (L). Risk: **critical**
  (every sonar sounding depends on it). DeepSignal never opens the control port; #151 checks that.

### 3.6 Sound velocity: hull probes and casts

- **Emits:** probes (Valeport miniSVS, AML Micro-X and similar) stream SV on serial at 1 to 20 Hz, usually
  into the multibeam PU and sometimes to the DAS (L). Casts come from CTD (Seasave `.cnv`), XBT (Sippican
  `.EDF`), SVP sondes (Valeport, AML) or an MVP, and are converted to `.asvp` for SIS (L). TSG gives a third,
  independent surface SV through TEOS-10 (#112).
- **Core:** device type `SVP` (single value) and `TSG_SBE45` with an SV field (V).
- **DeepSignal adds:** #140 SV consistency monitor (probe vs TSG-derived vs sonar-applied vs last cast) and
  #147 cast tracker (cast age, distance from the cast, recommend a new cast when surface SV has moved).
- **Active:** loading a new profile into SIS. **Not planned**; the recommendation goes to the operator.

### 3.7 Bridge: NMEA 0183, NMEA 2000, IEC 61162-450, ECDIS, DP, AIS, VDR

- **Emits:** NMEA 0183 on serial (talker per device). IEC 61162-450 carries the same sentences as UDP
  multicast with a `UdPbC` header and a tag block (source, line count, time) on standard groups (navigation,
  targets, time, propulsion, user groups) (L). NMEA 2000 is CAN; it reaches a computer only through a gateway
  (L). ECDIS exports routes (`RTE`/`WPL` sentences, RTZ files) (L). DP systems (Kongsberg K-Pos and others)
  emit status on NMEA or proprietary lines (L). AIS `VDM`/`VDO` (core device type `AIS` V).
- **Core:** serial readers, `UDPReader` multicast join (V). No 61162-450 header or tag-block handling (V);
  a raw 450 datagram would land as one unparsed string.
- **DeepSignal adds:** #138 IEC 61162-450 reader transform (strip header, verify tag-block checksum, keep the
  source id, keep the bridge time as a separate field), #149 NMEA 2000 via a read-only gateway, #150 ECDIS
  route import for #108 routes and ETA.
- **Active:** any write to a 450 network or bridge serial line. Risk: **critical, regulated** (SOLAS
  equipment, IEC 61162-460 network security, IACS UR E26/E27). **Banned.**

### 3.8 Engineering: engine, power, tanks through Modbus

- **Emits:** the alarm and monitoring system or a PLC exposes registers over Modbus TCP or RTU (L).
- **Core:** `ModBusTCPReader` and a serial Modbus reader exist; they read holding and input registers, coils
  and discrete inputs (V).
- **DeepSignal adds:** #148 guarded Modbus adapter: a function-code allowlist (reads only: codes 1 to 4),
  a register-map catalog with units and scaling, and a test that proves no write code can be built. Feeds
  #43 vibration, #98 to #100 vessel performance.
- **Active:** Modbus writes (codes 5, 6, 15, 16) can start pumps or trip breakers. **Banned.**

### 3.9 Winch and CTD deck units

- **Emits:** winch readouts (for example the LCI-90i) stream tension, speed and payout on serial or UDP
  (core device type `Winch` V). CTD deck units (SBE 11plus) feed Seasave, which can re-output scans on serial
  or a socket (L).
- **DeepSignal adds:** already covered: #109 cast view, #136 winch-data-processing adapter. This doc adds
  only the Seasave output as a source for #109 (L, confirm on the pilot ship).
- **Active:** winch control is a safety system. **Banned.**

## 4. Ranked table

Value = techs / science / shore, 1 to 5 each (as in IDEAS). Effort S/M/L. Risk is the worst case if the
module misbehaves. Rank orders passive work by value per effort, then by how many other rows it unlocks.

| Rank | # | Item | Tier | Value | Effort | Risk | Unlocks | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | #139 | Kongsberg datagram tap (KMALL and `.all` summaries) | P | 5/5/3 | M | low | #140 #141 #142 #143 #144 | BRIEFED |
| 2 | #140 | Sound velocity consistency monitor | P | 5/5/3 | S | low | #147 | BRIEFED |
| 3 | #138 | IEC 61162-450 bridge reader | P | 4/3/2 | S | low (receive only) | #142 #150 | BRIEFED |
| 4 | #141 | Depth consensus: multibeam nadir vs single-beam vs grid | P | 5/4/3 | S | low | #143 | BRIEFED |
| 5 | #142 | Time and motion alignment monitor | P | 5/5/2 | M | low | none | PROPOSED |
| 6 | #146 | Motion and position system status (POS MV Groups, Seapath) | P | 5/4/2 | M | low | #142 | PROPOSED |
| 7 | #143 | Sonar health board | P | 5/3/3 | S | low | none | PROPOSED |
| 8 | #147 | SVP cast tracker | P | 4/4/2 | S | low | none | PROPOSED |
| 9 | #145 | ADCP health and cross-checks (UHDAS, PD0; section 13) | P | 4/5/2 | M | low | #144 | BRIEFED |
| 10 | #151 | OT network safety kit | P | 5/1/4 | S | none (docs and lint) | every row | PROPOSED |
| 11 | #144 | Acoustic transmit awareness | P | 3/4/1 | M | low | none | PROPOSED |
| 12 | #148 | Guarded Modbus engineering adapter | P | 3/1/3 | S | medium (OT network) | #43 #98 #99 | PROPOSED |
| 13 | #150 | ECDIS route import | P | 3/2/2 | S | low | #108 | PROPOSED |
| 14 | #149 | NMEA 2000 through a read-only gateway | P | 2/2/1 | M | low | none | PROPOSED |
| 15 | #156 | Link health with NOC integration (section 10) | P, opt-in probes | 5/2/4 | M | low | #143 #145 | BRIEFED |
| 15b | #157 | Serial device servers, vendor-neutral (Moxa, Pepperl+Fuchs first; section 11) | P (reads), A via #153 | 5/2/3 | M | medium | #156 | BRIEFED |
| 15c | #158 | Seismic shot and source QC (section 12) | P | 4/5/3 | S | low | #160 | BRIEFED |
| 15d | #159 | Streamer and bird QC (section 12) | P | 3/5/2 | M | low | none | PROPOSED |
| 15e | #160 | Protected-species and mitigation view (section 12) | P | 4/4/3 | M | low | none | PROPOSED |
| 16 | #152 | Instrument config reader | R | 5/2/2 | M | medium | #153 | PROPOSED |
| 17 | #155 | Scoped SSH access kit | R | 4/1/2 | S | medium | #152 #154 | PROPOSED |
| 18 | #153 | Config advisor | R | 5/3/2 | M | low (advice only) | #154 | PROPOSED |
| 19 | #154 | Approved change apply with rollback | A | 4/2/1 | L | high | none | PROPOSED |
| no | none | Sonar, bridge, DP, POS MV control, engine, winch writes | A | none | none | critical | none | BANNED (D-SHIP1) |

Why this order: #139 is the foundation (five rows read its fields), #140 is the single most common silent
multibeam error on the fleet and is cheap once #139 exists, and #138 opens every modern bridge with a few
hundred lines. #141 is the cross-check a tech understands in five seconds.

## 5. Cross-checks only DeepSignal can do

No vendor sees all of these streams at once. The DAS does.

| Check | Inputs | Alarm when (defaults, configurable) | Row |
|---|---|---|---|
| SV mismatch at transducer | probe SV, TSG-derived SV (#112), SV the sonar applied (#139), last cast surface SV | any pair differs by more than 2 m/s for 2 minutes | #140 |
| Stale SV profile | cast time and position, surface SV now vs at cast | cast older than 12 h, or more than 50 km away, or surface SV moved more than 3 m/s | #147 |
| Depth disagreement | multibeam nadir, single-beam, optional GMRT grid | relative difference over 2 % (after transducer depth and draft) for 1 minute; grid check only as "suspicious" | #141 |
| Motion latency | roll from the motion feed vs roll the sonar recorded | cross-correlation lag over 10 ms, or lag that changes | #142 |
| Clock offset | sonar PU clock, motion ZDA, host NTP | offset over 50 ms or drifting | #142 |
| Position consistency | sonar position vs nav position, with lever arms (#113) | horizontal difference beyond lever-arm geometry plus 1 m | #142 |
| Heading agreement | gyro, Seapath or POS MV, ADCP heading | difference over 0.5 degrees, or a step | #145 #146 |
| Transmit overlap | ping times of multibeam, echosounder, ADCP, SBP | pings overlap with no synchronizer schedule seen | #144 |

All alarms follow the project rule: score plus persistence plus a plain explanation, never a delete.

## 6. Security: these are OT networks

OT (operational technology) means networks that run physical equipment. Treat every ship network beyond the
science LAN as OT.

**Placement rules (#151 turns them into a checklist and a config lint):**
1. DeepSignal sits on the science or DAS network. It reaches bridge data only through what the ship already
   provides for that: an IEC 61162-460 gateway, a one-way data diode, a switch mirror port, or a serial
   splitter that is wired receive-only.
2. Receive-only by construction. Passive modules open receive sockets only; a test in each module proves it
   never calls `send`, `sendto` or `write` on that socket. Multicast join (IGMP) is the only packet a
   passive module causes, and #151 documents it for the ship's IT.
3. No new inbound ports on OT networks. No LAN scanning (same rule as #125).
4. Modbus: function codes 1 to 4 only, enforced in code and, where the ship has one, by a Modbus-aware
   firewall rule.
5. Connection register: every link to another system is listed (system, network, direction, protocol, port,
   owner, who approved it, date). The console shows it. Nothing connects that is not in the register.
6. Egress: the DeepSignal host reaches the internet only through the ship's allowlist; AI features keep
   their key server-side and send no OT data off ship without the release policy (#116).
7. Standards to align with, cited as leads for the IT officer: IEC 61162-460 (450 network security), IACS
   UR E26 and E27 (cyber resilience, ships contracted from July 2024), IMO MSC-FAL.1/Circ.3 and resolution
   MSC.428(98), NIST SP 800-82r3 (OT security), IEC 62443 (zones and conduits).

**Threat model, short form.** Assets: safe navigation, sonar data, science data, crew time. Threats:
DeepSignal bug that writes to a bridge or sonar network (blocked by tiers and receive-only tests); a
compromised DeepSignal host used as a bridge to OT (blocked by placement, no inbound, diode or gateway);
stolen SSH key used on instruments (blocked by #155 forced commands and short-lived certificates); AI
proposes a harmful change (blocked by approval and allowlist; AI never holds an apply credential, #65).

## 7. Instrument configuration: propose, approve, apply, verify, roll back

Eugene's second ask. The design shares the #130 init-profile engine and the MCP apply flow (#65, D-MCP2):
one engine, three front doors (wizard, CLI, MCP), and `apply` is the only write path.

```
 read (tier R)       advise (tier R)          approve (person)        apply (tier A)          verify              roll back
 ─────────────►  ─────────────────────►  ─────────────────────►  ──────────────────►  ─────────────────►  ───────────────────►
 #152 snapshot   #153 finding + reason   dry-run diff shown,     backup captured,     re-read config,      one click: restore
 of config and   + proposed change       per change, named       change sent through  check the stream    backup through the
 status, stored  ("rate 1 Hz, logger     person, expiry          #130 engine, every   (rate, units,       same engine; logged
 in #52 history  expects 4 Hz")                                  byte logged          values sane)
```

**Tier R: read config and status (#152).** Sources, in order of preference: a serial query listed in the
instrument's #130 profile (for example a Sea-Bird `DS` status command); a vendor read API; an SSH read
command through #155. Snapshots are stored with a hash in #52 instrument history, so "what changed since
last cruise" is a diff.

**Tier R: advise (#153).** Rules that explain themselves. Examples: output rate differs from what the logger
expects; units or sentence set differ from the device definition; instrument clock drifts from NTP; lever
arm in the instrument differs from #113 vessel geometry; calibration coefficients differ from the #52
certificate; the sonar is using an SV source that #140 says is wrong (advice only, the operator acts).
Output: finding, evidence, proposed change, risk class. Never applied by #153.

**Tier A: apply with approval (#154).** Only for instruments on an allowlist with risk class "science
sensor" (TSG, met sensors, fluorometers, pCO2 and similar). Every change needs: a dry-run diff; a captured
backup of the prior config; one named person's approval of that single change (no batch approval, approval
expires after 15 minutes); the change sent through the #130 engine; post-change verification (re-read
config, then watch the data stream for a set window); automatic rollback if verification fails, and a
one-click rollback afterwards; an append-only log of every byte sent and received. An AI client can propose
but never approve, and never holds the apply credential.

**SSH, done safely (#155).**
- One key per DeepSignal host per instrument host, generated on the DeepSignal host, private key never leaves it.
- OpenSSH user certificates with short validity (hours) instead of long-lived keys where the host supports
  them; otherwise `authorized_keys` options `restrict,from="<DAS IP>",command="/usr/local/bin/ds-allow"`.
- `ds-allow` is a forced-command wrapper that runs only commands from a per-host allowlist (read commands for
  tier R; the few apply commands for tier A sit in a separate key that the apply service holds).
- Non-root account, password authentication off, no agent or port forwarding, no PTY.
- Full session logging: the wrapper logs command, arguments, exit code and a hash of output; sshd at
  `LogLevel VERBOSE`; logs shipped to the DeepSignal audit trail (#62).

### Risk table for configuration

| Target | Read (R) | Advise | Apply (A) | Why |
|---|---|---|---|---|
| Met sensors, TSG, fluorometer, pCO2 (science sensors) | yes | yes | yes, with approval | Recoverable, low safety impact, frequent setup errors |
| DAS hosts, serial servers (Moxa and similar), data loggers | yes (SSH read) | yes | yes, with approval, port settings only | Wrong baud or mode loses data but harms nothing else |
| CTD deck unit, winch readout | yes | yes | no | Feeds safety-relevant decisions during casts |
| ADCP (UHDAS or VmDAS owned) | yes | yes | no | Owned by UHDAS; changes break processing |
| Motion systems (Seapath, POS MV) | yes (status only) | yes | **never** | Every sonar sounding depends on it |
| Multibeam, echosounders, SBP (SIS, EK80, Knudsen) | yes (datagrams) | yes | **never** | Transmit settings, survey integrity, mitigation permits |
| Bridge, ECDIS, DP, AIS, VDR | receive only | yes (to the bridge, as information) | **never** | SOLAS equipment, regulated, safety of navigation |
| Engine, power, tanks (Modbus) | receive only (codes 1 to 4) | yes | **never** | Physical plant |

## 8. What is not decided (open, non-blocking)

- Which UNOLS ship pilots this (#70). Each L row above needs one real capture. Defaults are configurable,
  so building proceeds now with synthetic fixtures built from the published formats.
- Whether ships allow a mirror-port or diode feed from the bridge 450 network. Most UNOLS ships already pass
  bridge NMEA to the DAS on serial; #138 is for ships that only offer 450.
- Whether to read UHDAS status over its web pages or only its `$PUHAW` output (#145, ask the UHDAS team
  before building; nothing goes to them without Eugene, as with OceanDataTools).

## 9. Sources (leads to verify, not facts)

- Kongsberg EM datagram formats (`.all`), document 160692, Kongsberg and LDEO MB-System mirrors.
- KMALL format examples and reader: github.com/kjerram/kmall.
- Applanix POS MV V5 installation guide and POSv6 user ICD (Group and Message definitions, Ethernet ports).
- IEC 61162-450 and 61162-460 previews (IEC webstore); full texts are paid standards.
- OpenRVDAS v2.7.2 source for every V mark: `logger/readers/udp_reader.py`, `logger/readers/modbus_reader.py`,
  `contrib/devices/*.yaml`.

## 10. Network monitoring and link health (D-NOC1)

Eugene asked for "intermapper-like network monitoring", and agreed to this scope: DeepSignal owns **link
health per instrument**; an existing open-source NOC tool (network operations center tool) owns the network.

**Recommendation: do not build an Intermapper clone.** Topology maps, SNMP polling, switch-port graphs and
device discovery are a whole product, and Uptime Kuma (simplest, one container), Zabbix (most complete) and
LibreNMS (best for SNMP switch fleets) already do them well and openly. What none of them knows is whether
the *data* is right. DeepSignal does, so the two meet in the middle.

**What OpenRVDAS already gives us (reuse, verified in v2.7.2):**

| Need | Already in OpenRVDAS | Gap DeepSignal fills |
|---|---|---|
| Is the logger process alive | `status:logger_status` RUNNING, STARTING, FAILED, EXITED; restarts in `logger_runner.py` | none; console `health` shows it |
| Is data fresh | Cache keeps latest timestamp per field; `/latest` over HTTP; `TimeoutWriter` and `TimeoutReader` alert on silence | per-link threshold and one verdict |
| What went wrong | `stderr:logger:<logger>` fields | classify into serial, parse, timeout errors; count per 5 minutes |
| Record rate | `CountTransform` counts records | rate versus an expected rate |
| Is the device reachable | nothing | opt-in ping or management-port connect |
| Host health | nothing in core | #119 |
| NOC tool can see DAS health | nothing | read-only `/health`, `/health/<link>` (HTTP 200 or 503), `/metrics` |
| DAS can see NOC alerts | nothing | token-guarded webhook into `noc:*` cache fields |

**Flow:**

```
 OpenRVDAS logger manager ─► cache (status, stderr, fields, timestamps)
                                   │ read only (HTTP /latest)
                                   ▼
                       #156 LinkHealthReader ──► link:<name>:state ... ──► console health page, alerts
                         ▲ opt-in ping or                    │
                         │ management-port connect           ▼
                    instruments (science LAN)      /health  /metrics  ◄── Uptime Kuma, Zabbix, LibreNMS poll
                                                   /noc/<source>      ◄── their alert webhooks (token)
```

**Edge case that drives the design:** many serial device servers (Moxa NPort and similar) in TCP server mode
accept one client. A "is port open" probe on the data port can steal the session and drop the logger. So
probes default to off, a TCP probe may only target a management port, and the config check refuses any
probe that matches a reader's host and port. Freshness from the cache is the primary signal; probes only
answer "is it the device or the cable".

## 11. Serial device servers: Moxa, Pepperl+Fuchs and similar (#157)

Eugene: "integrate VERY well with Moxas and Pepperl+Fuchs devices." Nearly every serial instrument on a
UNOLS ship reaches the DAS through a Moxa NPort or a Pepperl+Fuchs Comtrol DeviceMaster, so this is where
most "no data" problems actually live. Eugene added "and other similar devices": Digi, Lantronix, Perle,
B&B and Advantech, Brainboxes, Sena. Brief: `briefs/p2/157-device-servers.md`, `briefs/p2/158-seismic-shot-qc.md`, `briefs/p2/145-adcp-health.md`.

**Vendor-neutral by design.** One driver interface (identify, read ports, say what it can read) and one
port-status shape for every vendor. v1 drivers: Moxa, Pepperl+Fuchs, and a generic SNMP driver (MIB-II plus
the standard RS-232 MIB, RFC 1659, with per-port speed and error counters) that covers most other brands and
backs up the vendor drivers. OID tables and web paths live in data files, so adding a vendor is a file, not
code. A field a device cannot report shows "not reported", never zero. Telnet is deliberately not a v1
fallback: it sends the admin password in clear text and opens a session that can change settings. If a
device has neither SNMP nor web status, it gets a later, opt-in, read-command-only telnet driver.

**What DeepSignal does (read-only, v2):**
1. **Find them.** Passive first: match the vendor's MAC prefix in the DAS host's ARP table, and read hosts
   from the cruise definition. A vendor discovery broadcast is opt-in, on a named interface only.
2. **Read each port** through SNMP (preferred: read-only, no login) or the vendor's HTTP pages or API:
   baud and framing, mode, connected clients, bytes in and out, framing, parity and overrun errors.
3. **Map each port to its logger**, from the reader's host and port or the local tty name.
4. **Write the reader config** for a new device server, as a new file plus a diff, never an edit in place.
5. **Explain mismatches**, folded into each #156 link verdict:

| Seen | Likely cause | First thing to try |
|---|---|---|
| Framing or parity errors rising | Baud or framing mismatch with the instrument | Compare instrument settings with the port |
| Port baud differs from the device definition | Port or config set wrong | Fix whichever side is wrong |
| Logger RUNNING, port has 0 clients | Logger not connected (wrong host or port, or another client holds it) | Check reader host and port |
| Bytes flowing, cache field stale | Parsing problem, not wiring | Check the device definition |
| No bytes in while logger RUNNING | Instrument off or cable fault | Check power and cable |
| Two readers on one single-client port | One logger will keep losing the session | Remove one reader |

**Changing port settings is a write.** It goes through the #153 apply path (#155 for credentials): backup
export of the device config, a dry-run diff, Eugene's named approval of each change, apply, verify on the
live stream, rollback. Device servers sit in the "DAS hosts, serial servers" row of the risk table in
section 7: apply allowed with approval, port settings only. Never SNMP SET or web changes from v2.

**Gotchas that shape the design:** many ports accept one TCP client, so DeepSignal never probes data ports;
a web login can end another admin's session on some models, so SNMP comes first and HTTP reads skip
anything behind a login; SNMP v2c communities travel in clear text, so they stay on the instrument LAN and
v3 is the next step.

## 12. Seismic systems: streamers, birds, gun controllers (#158 to #160)

Eugene: "would be nice to handle seismic (digibird, geoeel, hotshot), etc." Same rule as sonars: **listen
only**. Gun controllers fire air guns and streamer controllers steer birds; nothing from DeepSignal ever goes
to them. Brief: `briefs/p2/158-seismic-shot-qc.md`, `briefs/p2/145-adcp-health.md`.

| System | What it emits | Public format? | DeepSignal use | Row |
|---|---|---|---|---|
| Gun controller (Real Time Systems HotShot, Seamap GunLink, Sercel) | Per-shot ASCII log: shot number, fire time, per-gun timing error, sometimes pressure, on serial or UDP (L) | No: vendor documents, varies by firmware. Capture on the ship and map with a core device file | Shot QC, missed shots, gun timing, shot position | #158 |
| Shot trigger and navigation (nav system or timer) | Trigger time, shotpoint number; position from the ship's GNSS | Yes: NMEA 0183; IOGP P1/11 for shot positions; P2/94 raw nav | Fire time vs trigger and GPS time; shot spacing; P1/11 shot file | #158 |
| Streamer depth and heading birds (DigiCOURSE DigiBIRD and compass birds, via the streamer controller) | Bird depth, wing angle, heading per bird, through the controller's own network or log (L) | No: vendor documents | Streamer depth and feather QC, bird dropouts | #159 |
| Digital streamer (Geometrics GeoEel and similar) | Shot records as SEG-D or SEG-Y files; status and noise in the acquisition software (L) | SEG-D and SEG-Y yes (SEG standards); live status no | File heartbeat, per-channel noise and dead channels from SEG-Y headers and traces | #159 |
| Source and mitigation context | Gun state (firing, ramp-up, shut down), position, EEZ status | Derived | Protected-species observer (PSO) view and event log | #160 |

**Cross-checks only the DAS can do:** fire time against GPS time and the nav system's trigger (a drifting
controller clock misplaces every shot); shot position interpolated from the ship's own nav at fire time,
never extrapolated; shot spacing against the planned interval; missed shots against shot numbers; gun
activity against the EEZ boundary (#137) and the acoustic transmit timeline (#144), so a PSO sees in one
place whether guns are firing, where, and inside which permit area.

**Protected species (#160):** observers keep ramp-up, shutdown and sighting records under the permit. #160
gives them a read-only view (gun state, power-down, ramp-up timer, distance to EEZ edge) and writes their
events to Sealog (#133). It never powers guns down itself; the PSO calls the shutdown, by radio, as today.

**Needs vendor documents:** HotShot, GunLink and Sercel shot-log formats; DigiCOURSE controller output; GeoEel
live status. Until a ship provides a capture, #158 ships with a labelled template device file and works on
any shot log a tech maps with core `ParseTransform`, so no vendor document blocks it.

## 13. ADCP in depth (#145)

Eugene: "We should also loop ADCP into this." Listen-only, like every sonar. Brief: `briefs/p2/145-adcp-health.md`.

| Source | What it gives | Public format? | Notes |
|---|---|---|---|
| UHDAS speed log `$PUHAW` | Ship-relative current and heading | Yes in practice (core device type `ADCP_OS75` parses it) | Already reaches OpenRVDAS on many ships |
| Raw PD0 ensembles (Ocean Surveyor, Workhorse, Pinnacle) | Time, heading, pitch, roll, sound speed, self-test word, bottom track | Yes: Teledyne RDI output format manuals are public | Only from a receive-only copy (serial split or a re-broadcast the ADCP operator sets up); never the ADCP command line |
| UHDAS status pages and daily email | Processing health, heading correction statistics | No formal spec | Later, after asking the UHDAS team (nothing sent without Eugene) |
| VmDAS files (ENR, ENS, ENX, STA, LTA) | Same ensembles, recorded | Teledyne documents | File heartbeat in #143 |

**Cross-checks (all in #145):**

| Check | Why it matters | Default limit |
|---|---|---|
| ADCP heading vs gyro and GNSS heading, and "frozen heading" | A heading error turns straight into a cross-track current error; a dead heading feed is the classic UHDAS failure | 1 degree; frozen if unchanged 60 s while the gyro turns |
| ADCP sound speed vs TSG and probe | Wrong sound speed scales every velocity | 2 m/s (a fixed EC setting shows as a steady offset) |
| Bottom-track depth vs multibeam nadir | Catches bad beams, wrong transducer depth, wrong beam angle | 3 percent |
| Ensemble timing vs multibeam and EK80 pings | Interference shows as noisy bins; tells the tech to check K-Sync | count of overlaps, advice only |
| Self-test word and ensemble cadence | Hardware faults and dropped ensembles | any nonzero bit; interval over 1.5 times normal |

**The PD0 layout is a data table**, not code, so a wrong offset is a one-line fix. Its first real check is
a capture on the pilot ship. Synchronization (K-Sync or UHDAS triggers) is read, never set.
