# Target parity: CORIOLIX + MetAcq + our own plan

One scorecard of everything OpenRVDAS plus DeepSignal must do. Eugene's goal
(2026-11-18): do at least most of what CORIOLIX does, plus what MetAcq does,
plus everything already planned, but better, easier to set up, and fully open
source.

Written 2026-11-18 by the parity thread. Tables and percentages are generated
by `tools/target-parity/gen.py` from its row data and
`tools/target-parity/template.md`, so the arithmetic is reproducible; the
judgement is in each row's status and value scores. Edit the rows there, then
run `python3 tools/target-parity/gen.py build` from the desk root. Do not
hand-edit the tables below.

## 1. Headline

{SUMMARY}

- **Today** means code that runs now: OpenRVDAS core plus DeepSignal modules
  that are built and tested (only vector wind, #4).
- **Planned** counts every row an existing IDEAS row or brief would close,
  whatever its status. **+Drafts** adds the unnumbered draft ideas in
  section 7.
- Scoring: Have = 1, Partial = 0.5, Gap = 0. Every row weighs the same; the
  value ranking in section 4 is where importance shows up.
- Measurable goal proposed: **"most of CORIOLIX" = at least 80% of CORIOLIX
  rows fully covered (score 1), and every gap valued 12 or more closed.**
  Fully covered today: 6 of 42 (14%). With work planned before this scorecard:
  23 of 42 (55%). With #104-#124 (now numbered and briefed, phase 2): 40 of 42
  (95%). Re-scored 2026-11-18 07:45Z after finding that fork `dev` already has
  round-robin polling, per-file log headers and CDS HTTP routes.

What this says plainly: OpenRVDAS core already owns acquisition, parsing,
logging, derived values and data push (the bottom of both stacks). Everything
people see and touch above that is the gap: QC flags, the sensor registry,
displays, data delivery, alerts. That is DeepSignal's job, and the console,
QARTOD and instrument-history briefs already point at most of it.

## 2. Sources

CORIOLIX has no public source code or license that we found. Its public
documentation is MIT-adjacent prose in
[R-DESC/CORIOLIX_docs](https://github.com/R-DESC/CORIOLIX_docs) (commit
1398bb8, 2026-09-29), plus UNOLS RVTEC talks and the Sikuliaq public site.
Public CORIOLIX code we found: example notebooks
([R-DESC/CORIOLIX_notebooks](https://github.com/R-DESC/CORIOLIX_notebooks),
MIT) and a regex library (R-DESC/sensor_regex). The 2022 talk planned to "open
the CORIOLIX GitHub repo by Taani delivery (September 2023)"; we found no such
repo.

| Key | Source |
|---|---|
| `cx:<page>` | CORIOLIX_docs page, linked in each row |
| RVTEC 2025 | [CORIOLIX part 2, Nov 2025]({R25}) (slide titles, no numbers) |
| RVTEC 2023 | [CORIOLIX, Oct 2023]({R23}) |
| RVTEC 2022 | [CORIOLIX, Nov 2022]({R22}) |
| RVTEC 2020 | [OpenRVDAS to CORIOLIX integration]({R20}) |
| RVTEC 2019 | [CORIOLIX, 2019]({R19}) |
| Sikuliaq site | [coriolix.sikuliaq.alaska.edu]({SKQ}) |
| MetAcq 2.15 | [MetAcq Operator's Manual Rev 2.15, Aug 2019]({MA}) |
| MetAcq 2.12 | [Rev 2.12, Apr 2014]({MA12}) (calibration method list) |
| MetSpecs | [MetSpecs Rev 1.18]({MS}) (sensor list) |
| OpenVDM #408 | [$WICOR parser issue]({OVDM}) |

MetAcq rows come from the desk's MetAcq gap map
(`research/README.md` links it), which read the manual mirrors above. Its
sections 10, 11 and Appendix A were read only in summary; the $WICOR writer
brief must read them first (D-METACQ1). OpenRVDAS status was checked against
fork `master` 3f3d0c3 (v2.7.2).

Status words in the DeepSignal column: **Built** (code and tests exist),
**Building** (brief plus branch, work running), **Briefed** (brief written),
**Designed** (IDEAS row marked DESIGNED or a design doc), **Idea** (IDEAS row
PROPOSED), **none**.

## 3. The matrix

### 3a. CORIOLIX (42 rows)

{CTABLE}

### 3b. MetAcq (43 rows)

{MTABLE}

### 3c. Already planned (IDEAS.md and briefs)

IDEAS.md holds 103 numbered ideas: 1 BUILDING, 18 DESIGNED, 84 PROPOSED,
none DONE. Parity rows above already credit the ones that close a CORIOLIX or
MetAcq gap. The rest are where we beat both systems, because neither does them.
They are the reason to choose this stack, so they are scored here too.

| Area | IDEAS rows | Brief or branch | Status | In CORIOLIX? | In MetAcq? |
|---|---|---|---|---|---|
| Vector wind averaging | 4 | branch `deepsignal/vector-wind` | Built (31 tests), parked on fork | yes (circular mean) | yes |
| DeepSignal Console core, bridge, charts, health, night mode, freshness | 12-14 | `briefs/deepsignal-console-*` | Building | partly (no night mode, no freshness states) | partly (MetBig) |
| QARTOD flags, plus "cannot tell" verdict | 8, 55 | `briefs/deepsignal-qartod-flags.md` | Briefed, waiting on Eugene's Mac approval | global limits only | range digit only |
| Instrument history graph | 52, 7 | `briefs/deepsignal-instrument-history.md`, cloud prompt | Briefed | sensor logs, no contradiction checks | metadata only |
| Correction ledger with sign-off | 56 | `briefs/deepsignal-correction-ledger.md` | Briefed | no | no |
| Fault-injection benchmark | 53 | `briefs/deepsignal-fault-bench.md` | Briefed, running on Mac | no | no |
| Post-cruise drift review | 54 | `briefs/deepsignal-post-cruise-drift.md` | Briefed | no | no |
| Ship-coupling discovery | 78 | `briefs/deepsignal-ship-coupling.md` | Briefed | no | no |
| Dependency-graph fault detector | 79 | `briefs/deepsignal-dependency-graph.md` | Briefed | no | no |
| Read-only MCP gateway and AI audit trail | 20-23, 62, 64-69 | design docs | Designed | no | no |
| Old-data reanalysis | 59, 63 | `research/2026-11-18-reanalysis-program.md` | Designed | no | no |
| Physics referee, clock forensics, provenance, replay | 25, 31-33 | none | Idea | no | no |
| Signals of opportunity (waves, current, rain, PWV, machinery) | 38-43, 80-103 | none | Idea | no | no |
| Linux gate | 49 | `briefs/gate-linux*.md` | Building | n/a | n/a |

## 4. Gaps ranked by value

Value is techs + science + shore, each scored 1 to 5 by how much that group
would miss it on a normal cruise (5 = asks for it on day one). Only rows not
already at 1 today are ranked. Ties break toward rows the plan does not cover
yet. Scores are judgement; argue with them in this file.

{GAPS}

### Top 5 gaps (merged across duplicate CORIOLIX and MetAcq rows)

1. **QC flags that travel with every value** (C5, M19; value 15). Brief done
   (#8). Blocked only on Eugene's approval to run it on the Mac. Unblock first.
2. **Sensor registry, calibration and instrument history** (C15-C17, M10,
   M11, C35, C36; value 13). Brief #52 done; calibration records (#7) need a
   brief that reads the MetAcq method list and CORIOLIX's calibration file
   page. Add a document store and vessel geometry (drafts) to #52's follow-up.
3. **Live displays: status board, plots and the map** (C1, C3, C11, M36-M42;
   value 13). Console modules 1-4 are building. **The map has no brief**;
   make it console module 5.
4. **Data delivery to science and shore: binned statistics, downloads,
   ERDDAP, REST** (C6-C9; value 11-13). #16 is designed but **ERDDAP and a
   data REST API are not planned at all**. Generating ERDDAP `datasets.xml`
   from the registry is the cheapest way to match CORIOLIX's whole download
   stack, because ERDDAP (Apache-style open license) does the formats.
5. **Alerts with subscriptions** (C24; value 13). #9 is designed; extend it
   with CORIOLIX's proximity and calibration-due alert types.

Top unplanned gaps (now drafts in section 6): flowthrough state tagging (12),
ERDDAP generator (12), SAMOS file and met report formats (11), winch and CTD
cast view (11), best-source selector with GPS failover (11).

## 5. "Easier to set up": the target

### Definitions

- **T0, first light:** clean supported Linux box (Ubuntu 24.04, network up,
  sudo user) to the web console showing live simulated data updating. Count
  wall-clock minutes and **human actions** (commands typed, prompts answered,
  browser clicks).
- **T1, first real sensor:** from T0, plug in one NMEA GPS (serial or UDP) to
  parsed, logged, displayed, with a QC flag and a freshness state. Count the
  same two numbers, plus lines of YAML typed by hand.
- **T2, ship-ready:** a full underway suite. Tracked, not targeted yet.

### Baseline today

| | OpenRVDAS (counted from code, fork master 3f3d0c3) | CORIOLIX (public docs) |
|---|---|---|
| Servers per ship | 1 | 2 ship (OpenRVDAS + CORIOLIX) and 2 shore, 4 total (RVTEC 2025, System Requirements) |
| Prerequisites | Python 3.11+, sudo | signed certificates, DNS records, firewall rules, satcom (RVTEC 2025) |
| Install guide | `INSTALL.md`, complete | `INSTALL_coriolix.md` is a stub ("change testing"); source not public |
| T0 commands | 2 (download, run) + 1 to start the simulator | not possible from public sources |
| T0 prompts | 17 on the default Ubuntu path, plus the sudo password; 1 more to install the simulator, whose default is `no` (INSTALL.md shows `yes`: docs drift) | unknown |
| T0 browser actions | about 4 (log in, load cruise file, pick mode, open display) | unknown |
| T0 total human actions | **about 25** | unknown |
| Live data display after T0 | no maintained one: widgets are deprecated, Grafana is a separate install | built in |
| T0 wall-clock | **not yet measured** (brief below) | "setup takes effort" (RVTEC 2025); no number published |
| T1 | hand-write a logger config (and a device definition if the instrument is new), reload the cruise; no QC flag, no freshness; unmeasured, likely 30-90 min for an expert | 5-step web workflow plus two config scripts on two machines (`cx:HT_sensor_onboard`) |
| Upgrade | rerun installer | `UPGRADE_coriolix.md` is empty |

### Targets (proposed as D-SETUP1)

| Measure | Target | Why this number |
|---|---|---|
| T0 wall-clock | **10 minutes or less** on a GitHub `ubuntu-24.04` runner and on a 4 GB VM | install plus first data, network-bound; anything longer gets abandoned |
| T0 human actions | **3 or fewer**: one command, one password, open the URL. Zero-prompt default with a `--defaults` flag; questions only for what has no safe default | today about 25 |
| T0 result | console shows live simulated data with freshness states, no extra install | today no maintained display |
| T1 | **15 minutes or less, 10 or fewer actions, zero YAML typed** | matches the existing "add a new sensor" metric in IDEAS.md |
| Servers | **1 per ship**, shore mirror optional | CORIOLIX needs 2 per ship |
| Upgrade and recovery | upgrade in 5 minutes with rollback; a non-author recovers from docs alone (#71) | CORIOLIX upgrade page is empty |
| Footprint | core runs on a Raspberry Pi class box; full stack in 4 GB RAM | CORIOLIX asks 24 GB plus 8 GB |

### How we measure

`briefs/install-clock.md` (cloud lane, Sol medium): a GitHub Actions workflow
on fork branch `ci/install-clock` that runs the real installer on clean
Ubuntu 22.04 and 24.04 runners, counts prompts, and times install and first
data. Fork only. Run it now for the baseline, then on every installer change.

## 6. Home: core vs DeepSignal

The package decision (DeepSignal as a separate MIT package with thin adapters
versus `openrvdas_contrib`) is still open with Eugene. Note: the adoption
report calls it D-ARCH3, but D-ARCH3 in DECISIONS.md is already a DECIDED
entry about contrib branches; give the open one a new number. This table does
not decide it. It only says which work is generic plumbing that belongs in
OpenRVDAS core (small upstream fixes, under D-ARCH1's "core fix" exception) and
which is DeepSignal either way.

**Core (small, generic, upstream-shaped):** RS485 round-robin polling (M2),
ADAM ASCII reader (M3), device definitions for the UNOLS met suite (M7),
best-source selector and GPS failover (M8, C18, C19), met and seawater
formula library (M13, M14), lever-arm transform (M15), header-on-new-file in
`LogfileWriter` (M22), emulated flag in the simulators (M28), retention
policy (C28), zero-prompt installer (section 5). The installer change is
Eugene's call because OPERATIONS.md lists traps there.

**DeepSignal (everything a person sees, plus metadata and QC):** console and
all displays, map and routes, QC flags, registry, calibration records,
instrument history, documents, vessel geometry, alerts, event log, cruise
metadata, downloads, ERDDAP generator, REST API, roles, data release policy,
ship-to-shore, SAMOS and met report writers, $WICOR, scoreboard, R2R package,
onboarding wizard, vocabularies.

## 7. Draft ideas from this scorecard

Unnumbered, per the IDEAS numbering rule. Numbers assigned 2026-11-18: P-ERDDAP=#104, P-REST=#105, P-BEST=#106, P-MAP=#107, P-ROUTE=#108, P-CAST=#109, P-FLOW=#110, P-SAMOS=#111, P-METLIB=#112, P-GEOM=#113, P-WIZARD=#114, P-ROLES=#115, P-RELEASE=#116, P-VOCAB=#117, P-DOCS=#118, P-HOST=#119, P-CRUISE=#120, P-DEVPACK=#121, P-CORESMALL=#122, P-SNAP=#123, P-INSTALL=#124.
Also listed in IDEAS.md under "Drafts from the parity scorecard".

| Draft | Idea | Closes | Home |
|---|---|---|---|
| P-ERDDAP | Generate ERDDAP `datasets.xml` from the registry and database so ERDDAP serves subsets, every format and OGC | C7, C9 | DS |
| P-REST | Read-only REST data and metadata API (same tables MCP reads) | C8 | DS |
| P-BEST | Best-source selector: primary sensor per role by model and location, automatic failover, ancillary source assignment | C18, C19, M8 | core |
| P-MAP | Console map: track, clickable points, underway data colored on track, events, cached OSM, GMRT, NOAA ENC, SST and Chl layers, works offline | C11 | DS |
| P-ROUTE | Routes and waypoints: draw route, distance, ETA at speed, time to go, bearing, off-course warning | C12, M16, M40 | DS |
| P-CAST | Winch and CTD cast view: wire out, speed, tension with safe-working-load bands, CTD depth, altimeter; CTD package config | C21, M39 | DS |
| P-FLOW | Flowthrough state tagging: valve schedule tags every underway value with what was flowing (seawater, filtered, calibration, off), feeds QC and #55 | C23 | DS |
| P-SAMOS | SAMOS daily file and met report writers (NOAA hourly ship weather, OPSUM, SHIPTRACK, PCO2), byte-checked against real samples | C33, M26, M34 | DS |
| P-METLIB | Met and seawater formula library as named functions (dew point, wet bulb, sea-level pressure, PSS-78 and TEOS-10, sigma, sound speed) | M13, M14, M31 | core |
| P-GEOM | Vessel geometry: sensor positions, survey monuments, heights, lever-arm correction of positions | C36, M15 | DS + core transform |
| P-WIZARD | Sensor onboarding wizard with one-button deploy: identify stream, pick device, map CF names and limits, attach calibration, preview diff, deploy; no YAML typed | C29, C30 | DS (extends #29) |
| P-ROLES | Roles and accounts: public, science, tech, admin; ship and shore share accounts | C25 | DS |
| P-RELEASE | Data release policy: privacy level, restricted fields, EEZ hold-back using core `GeofenceTransform`, retention | C27, C28 | DS |
| P-VOCAB | Standard vocabularies in the registry: CF names, SeaVoX L22, L35, EL1, EL2, R2R device types, ICES ship codes, UN/LOCODE | C32 | DS |
| P-DOCS | Document store linked to instruments (manuals, calibration certificates) | C35 | DS |
| P-HOST | Host health on the health board: disk, CPU, RAM, NTP offset, process restarts | C4 | DS |
| P-CRUISE | Cruise metadata page (dates, ports, participants) with optional UNOLS schedule, MFP and MOMS import | C14, C41 | DS |
| P-DEVPACK | Device definitions for the MetSpecs sensor list | M7 | core (`contrib/devices`) |
| P-CORESMALL | Small core fixes: RS485 round-robin polling, ADAM ASCII reader, header on new file, emulated flag | M2, M3, M22, M28 | core |
| P-SNAP | Low-bandwidth shore snapshot page: static image plus compact JSON every N seconds | M43 | DS |
| P-INSTALL | Zero-prompt installer default plus install clock CI (section 5) | setup target | core (installer), fork (CI) |

## 9. Config assist coverage: every OpenRVDAS component

Eugene (2026-11-18): the "auto stuff" that helps people configure OpenRVDAS must cover all of it, UDP,
MQTT and the rest, not just serial. Inventory from fork `dev` 1a6f1ed: 19 readers, 22 writers, 34
transforms, plus the servers. The plan has three layers:

- **Forms for everything (#128 component catalog):** every component's settings become a form with
  defaults, checks and typo suggestions, generated from its code. This is what makes "no YAML" true for
  all of OpenRVDAS, not just the guided cases. Guided labels for the 15 most used components.
- **Guided setup (#114 wizard, #126 generator):** capture, identify, propose, diff, accept, for
  instruments; whole cruise definitions from the inventory.
- **Auto-detection (#125 discovery):** read-only, local or named targets only.

| Component | Kind | No-YAML setup | Auto-detect | Notes |
|---|---|---|---|---|
| SerialReader | reader | guided (#114, #126) | yes: port and baud scan (#125) | never writes to the port |
| PolledSerialReader | reader | form (#128); ADAM recipe (#121); init profiles (#130) | partial: reported as "silent, may need polling" | polling and init commands come from a reviewed profile, never from probing |
| UDPReader | reader | guided (#114, #126) | yes: passive listen on local ports (#125) | |
| TCPReader | reader | form (#128) | named target only (#125) | no network scanning, by design |
| NetworkReader, SocketReader | reader | form (#128) | named target only | older network readers |
| MQTTReader | reader | form (#128), guided label | yes: subscribe `#` on a named broker (#125) | needs the `mqtt` extra (paho-mqtt) |
| RedisReader | reader | form (#128), guided label | yes: channels and keys on a named server (#125) | needs the `redis` extra |
| CachedDataReader | reader | form (#128), guided label | yes: cache field list (#125) | |
| WebsocketReader | reader | form (#128) | named target only | |
| HTTPReader | reader | form (#128) | named URL only (#125) | |
| DatabaseReader | reader | form (#128) | no (needs credentials; listing tables is a later option) | needs a database extra |
| ModbusReader, ModbusSerialReader | reader | form (#128) | no: register maps cannot be guessed safely, and probing writes requests | |
| SealogReader | reader | form (#128) | named URL only | |
| LogfileReader, TextFileReader | reader | form (#128); wizard trial runs use them | yes: growing files in a named folder (#125) | |
| ComposedReader, TimeoutReader | reader | form (#128) | n/a | wrappers |
| CachedDataWriter, LogfileWriter | writer | automatic in every generated config (#126) | n/a | |
| UDPWriter, TCPWriter, SerialWriter, NetworkWriter, SocketWriter | writer | form (#128); $WICOR and nav repeat recipes (#6) | n/a | |
| MQTTWriter, RedisWriter, WebsocketWriter | writer | form (#128), guided labels for MQTT | n/a | optional extras |
| DatabaseWriter, InfluxDBWriter, GrafanaLiveWriter | writer | form (#128) | n/a | |
| EmailWriter, GoogleSheetsWriter, SealogWriter | writer | form (#128) | n/a | |
| FileWriter, TextFileWriter, RegexLogfileWriter, RecordScreenWriter | writer | form (#128) | n/a | |
| TimeoutWriter, ComposedWriter, LoggerManagerWriter | writer | form (#128) | n/a | TimeoutWriter feeds alerts (#9) |
| ParseTransform, ParseNMEATransform, RegexParseTransform | transform | automatic: chosen by the wizard's fingerprint (#114) | yes: device type identified from samples | |
| PrefixTransform, TimestampTransform | transform | automatic in generated configs (#126) | n/a | |
| TrueWindsTransform, ComputedFieldsTransform, SubsampleTransform, QC transforms | transform | form (#128); suggested when inputs exist (#129) | n/a | |
| All other transforms (format, select, convert, geofence, JSON, XML, Sealog, ...) | transform | form (#128) | n/a | |
| CachedDataServer, LoggerManager | server | installer (#124) and console install | n/a | already configured by the installer |
| Cruise definition as a whole | config | generated (#126), checked by core `validate_config` plus lint (#127) | n/a | |

Status: #114, #124, #125, #126, #127 and #128 are briefed (phase 2). Console auto-pages (display built
from what loggers publish) is in the console MVP. #129 and the console wizard page are next.

## 8. Next actions

1. Eugene: approve the QARTOD Mac run (gap 1).
2. Build lead: number the drafts; brief the map (P-MAP) as console module 5
   and calibration records (#7).
3. Run `briefs/install-clock.md` in the cloud lane for the measured baseline.
4. Eugene: decide the package question; then P-BEST, P-METLIB and the small
   core fixes can be briefed for core.
5. Re-score this file after each module lands.
