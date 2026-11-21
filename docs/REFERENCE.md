# DeepSignal reference: every feature and its status

**This is the canonical feature list for DeepSignal.** If a feature is not here, it is not tracked.
Updated 2026-11-18 08:45Z (ship systems section 11). Keep-current rule: AGENTS.md "Reference doc" (any change to a feature's
status updates this file in the same commit). Check: `python3 tools/reference-check.py`.

Other desk files go deeper: `docs/IDEAS.md` (every idea, one row each), `docs/ROADMAP.md` (ranking and
dates), `docs/TARGET-PARITY.md` (scorecard), `docs/DECISIONS.md` (why). This file is the index of what
DeepSignal does, and where each piece stands.

## Status key

| Status | Meaning |
|---|---|
| DONE | Built, independently reviewed, gate green on the fork |
| BUILT | Code pushed to its fork branch and passed lead acceptance (tests, flake8); independent review still owed |
| BUILDING | Brief written and a Codex task running or queued; branch exists, may still sit at its base commit |
| BRIEFED | Brief written, not launched yet |
| DESIGNED | Design or decision exists, no brief yet |
| PROPOSED | Idea only, kept in IDEAS.md |
| WAITING | Blocked on an input from Eugene or the outside world (named in the row) |

Links: `fork:<branch>` means `https://github.com/eugenevivino/openrvdas/tree/<branch>`. Brief paths are in this repo.

## 1. What DeepSignal is

DeepSignal is an open-source layer on top of OpenRVDAS (the Open Research Vessel Data Acquisition
System) that makes a ship's underway data easier to set up, see, trust and fix. OpenRVDAS stays
unmodified; DeepSignal adds modules that plug in through its standard interfaces.

**Positioning:** DeepSignal is the vessel's operational truth layer: interoperate with UHDAS, SIS and SCS,
don't replace them.

**Goals (Eugene, 2026-11-17 to 18):**
1. A console a non-expert tech can run on the bridge and in the lab, better than Grafana on ease (D-UX1).
2. Parity with MetAcq and most of CORIOLIX, measured by the scorecard, not claimed (D-PARITY1).
3. Setup measured in minutes and actions, not days (D-SETUP1).
4. Data you can trust: QC flags, drift detection, reversible corrections with sign-off.
5. Optional AI (MCP server, user-supplied key) that never touches ship systems without approval.
6. Reanalysis of old cruise data, and "ULTRA novel" capabilities no shipboard DAS has today.

**Architecture:**
- Overlay on unmodified OpenRVDAS core (D-ARCH1). Core gets only small bug-fix PRs.
- Tightly scoped independent modules, one branch each, disjoint files (D-ARCH4).
- Standard interfaces only: Reader, Transform, Writer, CachedDataServer, configs. Pure Python plus a
  Node console. Linux is the target (D-ARCH5); the Linux gate is GitHub Actions.
- Folder `contrib/deepsignal/` on the fork (D-NAME1, D-ARCH3). Everything is MIT-licensed open source.
- Built on Eugene's fork first; nothing goes upstream until Eugene says (D-ARCH6).
- **Open:** ship as a separately versioned package, or as a contrib code drop (D-ADOPT1, also
  called the D-ARCH3 question). Recommendation on file: build module by module now, decide packaging
  before anything goes upstream.

## 2. Headline numbers

| Measure | Today | Planned (briefed work lands) | Target | Source |
|---|---|---|---|---|
| Parity, CORIOLIX plus MetAcq combined | 46% | 72% | 98% | `docs/TARGET-PARITY.md` |
| Parity, CORIOLIX | 38% | 70% | 98% | same |
| Parity, MetAcq | 55% | 74% | 98% | same |
| First light (clean Ubuntu to live data in the console) | about 25 actions, no live display | 10 min or less, 3 actions or fewer | same | D-SETUP1, #124 |
| First real sensor | not measured | 15 min or less, 10 actions or fewer, no YAML typed | same | D-SETUP1, #114 |

Today's numbers are "core plus built DeepSignal". Re-score with `tools/target-parity/gen.py` when a feature lands.

## 3. MVP #1: the Console (target Tue 2026-11-25, Pacific)

2026-11-20 checkpoint: Console and Stream Health view are QUALIFIED and FINISHED
as fixture pilots at b67f3072, now on fork deepsignal/integration. All 272 frontend
checks, both full native design gates and Linux 44732250214 all 3 jobs PASS. Fresh
independent Astra Ultra R9 PASS cleared the final P1 and recommended integration.
Live deployment, installer activation and24-hour soak remain separate held gates.
Evidence and current status: CODEX-HANDOVER.md and research/2026-11-20-relay-pilots.

Native console (React, TypeScript, Vite, Tailwind, uPlot) reading CachedDataServer. Quality bar: "gorgeous
and functional" (D-VISUAL1, checks V1 to V9). "Stable integration" is five tests, all must pass (ROADMAP "MVP #1").
Rulebook: `design/console-DESIGN.md`. Task table: `briefs/console/INDEX.md`. Integration: `briefs/console/INTEGRATION.md`.

| Feature | What it does | Status | Target | Link |
|---|---|---|---|---|
| Console core (plugin host, data adapter) | App shell, module plugin host, CachedDataServer adapter, page files, freshness LIVE / AGING / STALE / NO DATA | QUALIFIED FIXTURE PILOT (integration b67f3072) | 11-20 | fork:deepsignal/console-core, `briefs/console/core-v2.md` |
| Console contract | Shared types and module interface every console module builds against | BUILT/QUALIFIED (b67f3072) | done | fork:deepsignal/console-contract |
| Charts | Time-series charts with uPlot, scrub, multiple fields | QUALIFIED FIXTURE PILOT (integration b67f3072) | 11-19 | fork:deepsignal/console-mod-chart, `briefs/console/charts.md` |
| Health page | Every sensor: last value, age, QC flag, alarm state (#12) | QUALIFIED FIXTURE PILOT (integration b67f3072) | 11-19 | fork:deepsignal/console-mod-health, `briefs/console/health.md` |
| Bridge page | Night-safe huge readouts, relative wind, stale shown as stale (#13) | QUALIFIED FIXTURE PILOT (integration b67f3072) | 11-19 | fork:deepsignal/console-mod-bridge, `briefs/console/bridge.md` |
| Auto pages | Builds starter pages from whatever fields the ship publishes | QUALIFIED FIXTURE PILOT (integration b67f3072) | 11-19 | fork:deepsignal/console-mod-auto-pages, `briefs/console/auto-pages.md` |
| Stale banner | Page-wide banner when a source goes stale or silent | QUALIFIED FIXTURE PILOT (integration b67f3072) | 11-19 | fork:deepsignal/console-mod-stale-banner, `briefs/console/stale-banner.md` |
| Kiosk with auto night | Locked bridge kiosk; night palette switches automatically, one tap always; red default (D-CONSOLE2) | QUALIFIED FIXTURE PILOT (integration b67f3072) | 11-19 | fork:deepsignal/console-mod-kiosk-night, `briefs/console/kiosk-night.md` |
| One-command install plus self-test | `install.sh` then open `/console/` then read the self-test page: the 3 actions of D-SETUP1 | HELD, CRITICAL: installer stays on fork:deepsignal/sec-cds-joint; redesign per research/2026-11-19-cds-gate-redesign.md (D-PILOT1) | 11-19 | fork:deepsignal/console-install, `briefs/console/install.md` |
| Map (#107) | Offline map, track, data colored on track, events, cached basemaps | QUALIFIED FIXTURE PILOT (integration b67f3072) | 11-21 | fork:deepsignal/console-mod-map, `briefs/console/map.md` |
| Stream health chain view v0 (#162) | Console view of each stream's stages and root cause; stretch on the same rule as the map (MVP only if green by 11-21) | QUALIFIED/FINISHED fixture pilot, integration b67f3072; independent R9 PASS | 11-21 | section 12, `docs/PAIN-POINTS-MAP.md`, `research/2026-11-20-relay-pilots/combined-astra-r9-pass.md` |
| Test fixture | Stock OpenRVDAS logger on NBP1406 replay feeding the console | PILOT CANDIDATE (D-PILOT1) | 11-19 | fork:deepsignal/console-harness-fixture, `briefs/console/fixture.md`, `briefs/console/fixture-ws-shim.md` |
| 24-hour soak | Real-rate replay, memory sampled every minute; growth under 5% after warm-up | BUILT runner (in pilot candidate); 24 h run NOT DONE | 11-22 to 11-24 | `briefs/console/soak.md`, D-SOAK1 |
| Source-loss test | Kill the logger: STALE within 10 s, recover with no restart, garbage input never crashes | BUILT; recovery after a manager restart (D-RECOVER1); flaky under load (T-CON-6) | 11-24 | `briefs/console/source-loss.md` |
| Visual gate | V1 to V9 checks plus contact sheet review before the MVP merge | BUILDING | 11-24 | fork:deepsignal/console-visual-gate, `briefs/console/visual-gate.md`, `design/console-VISUAL-GATE.md` |
| Design polish pass | Impeccable critique, typeset, polish, audit after integration | BRIEFED | 11-22 to 11-24 | ROADMAP "Design-polish pass" |
| Integration branch | All modules merged, full suite, Astra review | QUALIFIED FIXTURE PILOTS: Console and Stream Health view integrated at b67f3072 under D-REVIEW1; live production remains separate | 11-20 | fork:deepsignal/integration, `docs/TICKETS.md` |

Planned console follow-ups (after MVP): calibration view (#52), corrections approve and roll back (#56),
drift view (#54), host health tiles (#119), emulated badge, routes on the map (#108), setup wizard pages
(section 6), roles wired into pages (#115).

## 4. Data-quality and science modules

| Feature | What it does | Status | Target | Link |
|---|---|---|---|---|
| Vector wind averaging (#4) | Averages wind as vectors (359 and 1 degrees give 0, not 180); 31 tests | DONE, parked for upstream | done | fork:deepsignal/vector-wind, D-DSWIND1 |
| QARTOD QC flags (#8) | Range, spike, flat-line, rate-of-change tests emit `<field>_QC` flags; never deletes data | BUILT (2724f07a, 19 tests); review running | review | fork:deepsignal/qartod-flags, `briefs/deepsignal-qartod-flags.md` |
| "Cannot tell" verdict (#55) | Drift tests answer AMBIGUOUS when data cannot separate sensor change from real ocean change | DESIGNED (QARTOD brief carries it) | v2 | `briefs/deepsignal-qartod-flags.md` |
| Instrument history (#52) | Per sensor: serial, firmware, calibration, repairs, swaps, mount, clock source, each dated | BUILT (973a87a3, 7 tests); review owed | review | fork:deepsignal/instrument-history, `briefs/deepsignal-instrument-history.md` |
| Fault-injection bench (#53) | Replays real data with injected drift, steps, lag, clock resets, spikes; scores detectors | BUILT (9d87d99a, 17 tests); review queued | review | fork:deepsignal/fault-bench, `briefs/deepsignal-fault-bench.md` |
| Correction ledger with sign-off (#56) | Every correction is a reversible, signed layer; reviewer allowlist and trusted checkpoint (D-LEDGER1) | BUILT (99c01919, 25 tests); review plus D-LEDGER1 fix round owed | review | fork:deepsignal/correction-ledger, `briefs/deepsignal-correction-ledger.md` |
| Post-cruise drift review (#54) | Two-sided smoothing with later references (post-cal, casts, bottles) after the cruise | BRIEFED, held | v2 | fork:deepsignal/post-cruise-drift, `briefs/deepsignal-post-cruise-drift.md` |
| Ship-coupling discovery (#78) | Lagged dependency atlas between all streams with false-discovery control | BUILT (67440a40, 7 tests); Astra review queued | review | fork:deepsignal/ship-coupling, `briefs/deepsignal-ship-coupling.md` |
| Dependency-graph fault detector (#79) | Learns normal sensor relationships; flags a sensor whose relationships break | BRIEFED, held | v2 | fork:deepsignal/dependency-graph, `briefs/deepsignal-dependency-graph.md` |
| Scoreboard writer (#5) | Latest-value boards with per-model formatter, framing, pacing; stale shown as stale | WAITING: first board make, model, protocol manual, stale threshold (Eugene) | after inputs | D-SCORE1 |
| $WICOR writer (#6) | MetAcq-compatible one-line met broadcast | DESIGNED | v2 | D-METACQ1 |
| Sensor calibration records (#7) | Coefficients per sensor applied by a versioned transform | DESIGNED (overlaps #52) | v2 | D-METACQ1 |

## 5. Phase 2: parity build-out (candidate Fri 2026-12-04)

Twenty-seven items, ranked by scorecard gap. Full table with bases, lanes and dependencies: `briefs/p2/INDEX.md`.

| Feature | What it does | Status | Target | Link |
|---|---|---|---|---|
| #104 ERDDAP generator | Builds ERDDAP `datasets.xml` so ERDDAP serves subsets in every format | BUILT (a4f8e4c) | 12-04 | fork:deepsignal/p2-erddap, `briefs/p2/104-erddap.md` |
| #105 REST data API | Read-only data and metadata over REST for MATLAB, R and scripts | BUILT (8756fed) | 12-04 | fork:deepsignal/p2-rest-api, `briefs/p2/105-rest-api.md` |
| #106 Best-source selector (core fix) | Primary sensor per role with automatic failover | BUILT a1 (090e208); a2 BUILDING | 12-04 | fork:deepsignal/p2-best-source, `briefs/p2/106-best-source.md` |
| #107 Console map | See section 3 | BUILDING | 11-21 | `briefs/console/map.md` |
| #108 Routes and waypoints | Route, ETA, bearing, off-course warning | BRIEFED (Mac queue) | 12-04 | `briefs/p2/108-route-eta.md` |
| #109 Winch and CTD cast view | Wire out, speed, tension with SWL bands, CTD depth on one night-safe page | BUILDING; SWL values WAITING on Eugene | 12-04 | fork:deepsignal/p2-cast-view, `briefs/p2/109-cast-view.md` |
| #110 Flowthrough state tagging | Tags every underway value with what was flowing | BUILT (2df7bd5) | 12-04 | fork:deepsignal/p2-flow-state, `briefs/p2/110-flow-state.md` |
| #111 SAMOS and met report writers | SAMOS daily file and public met formats, byte-checked (D-111A) | BUILDING | 12-04 | fork:deepsignal/p2-met-reports, `briefs/p2/111-met-reports.md` |
| #112 Met and seawater formulas (core fix) | Dew point, SLP, PSS-78, TEOS-10, sound speed as named functions | BRIEFED (Mac, Astra) | 12-04 | `briefs/p2/112-met-formulas.md` |
| #113 Vessel geometry and lever arms | Sensor positions and lever-arm correction | BRIEFED (Mac, Astra) | 12-04 | `briefs/p2/113-geometry.md` |
| #114 Sensor onboarding wizard | Identify stream, pick device, map names and limits, preview diff, deploy; no YAML | BUILDING (fix round 1) | 12-04 | fork:deepsignal/p2-onboard-wizard, `briefs/p2/114-onboard-wizard.md` |
| #115 Roles and accounts | Public, science, tech, admin roles (engine only) | BUILDING; login layer WAITING on Eugene | 12-04 | fork:deepsignal/p2-roles, `briefs/p2/115-roles.md` |
| #116 Data release policy | Privacy level, restricted fields, EEZ hold-back | BUILT a1 (6b19de4); policy content WAITING on Eugene | 12-04 | fork:deepsignal/p2-release-policy, `briefs/p2/116-release-policy.md` |
| #117 Standard vocabularies | CF, SeaVoX, R2R, ICES, UN/LOCODE in the registry | BUILT (9749bdb) | 12-04 | fork:deepsignal/p2-vocab, `briefs/p2/117-vocab.md` |
| #118 Instrument document store | Manuals and cal certificates attached to instruments | BUILDING | 12-04 | fork:deepsignal/p2-doc-store, `briefs/p2/118-doc-store.md` |
| #119 Host health | Disk, CPU, RAM, NTP offset, restarts on the health board | BUILDING | 12-04 | fork:deepsignal/p2-host-health, `briefs/p2/119-host-health.md` |
| #120 Cruise metadata | Dates, ports, participants, optional schedule import | BUILDING; MFP and MOMS access WAITING | 12-04 | fork:deepsignal/p2-cruise-meta, `briefs/p2/120-cruise-meta.md` |
| #121 UNOLS met device pack (core fix) | Device definitions for the MetSpecs sensor list | BRIEFED (Mac, needs manuals) | 12-04 | `briefs/p2/121-device-pack.md` |
| #122 Small core fixes | Two of four parts already on fork `dev`; rest folded into #121 and a console badge | DESIGNED (not briefed, see INDEX) | 12-04 | `briefs/p2/INDEX.md` |
| #123 Low-bandwidth shore snapshot | Image plus compact JSON every N seconds for slow links | BUILT (159240c) | 12-04 | fork:deepsignal/p2-shore-snapshot, `briefs/p2/123-shore-snapshot.md` |
| #124 Zero-prompt installer plus install clock | `--defaults` install; CI measures time to live data | Install clock BUILT (f3b7437, CI running); `--defaults` BUILDING | 12-04 | fork:ci/install-clock, fork:deepsignal/p2-install-defaults, `briefs/p2/124-install-defaults.md`, `briefs/install-clock.md` |
| #125 Stream auto-discovery | See section 6 | BUILDING | 12-04 | `briefs/p2/125-stream-discovery.md` |
| #126 Config from inventory | See section 6 | BUILDING | 12-04 | `briefs/p2/126-config-from-inventory.md` |
| #127 Config linter | See section 6 | BUILDING | 12-04 | `briefs/p2/127-config-lint.md` |
| #128 Component catalog | See section 6 | BUILDING | 12-04 | `briefs/p2/128-component-catalog.md` |
| #129 Derived-product suggester | Proposes transforms (true wind, salinity, dew point, QC ranges) when inputs exist | PROPOSED (backlog) | later | `docs/IDEAS.md` |
| #137 EEZ mode | Auto-detects EEZ crossings from ship position and offline Marine Regions polygons; warns at 24, 12, 6 nm and 60, 15 min out; sets each instrument to log, quarantine or stop per the cruise clearance record; strictest action when position is lost; one-tap override with reason and expiry; audit log to a cruise-report table; console banner and Sealog events | BRIEFED | 12-04 | `briefs/p2/137-eez-mode.md` |

## 6. Setup automation: one engine, three front doors

One setup engine does the work; three front doors call it: a **wizard** (console pages), a **CLI**, and
an **MCP** server for AI clients. Same engine, same validation, same diff, whichever door is used.

| Feature | What it does | Status | Target | Link |
|---|---|---|---|---|
| Setup engine | Shared core the three doors call: discover, identify, generate, lint, diff, apply | DESIGNED | 12-04 | this section |
| #125 Stream auto-discovery | Read-only scan of serial (baud detection), UDP, MQTT, Redis, cache fields, growing files | BUILDING | 12-04 | fork:deepsignal/p2-stream-discovery, `briefs/p2/125-stream-discovery.md` |
| #114 Sniffing and onboarding | Identify a captured stream, pick device, map CF names and limits, preview the config diff | BUILDING | 12-04 | fork:deepsignal/p2-onboard-wizard, `briefs/p2/114-onboard-wizard.md` |
| #128 Forms for all 75 components | Every reader, writer and transform introspected into a JSON Schema form with plain labels | BUILDING | 12-04 | fork:deepsignal/p2-component-catalog, `briefs/p2/128-component-catalog.md` |
| #126 Cruise config generation | One acquisition file plus #52 history generates the whole cruise definition with modes | BUILDING | 12-04 | fork:deepsignal/p2-config-from-inventory, `briefs/p2/126-config-from-inventory.md` |
| #127 Config lint | Ship-sense checks beyond schema: shared ports, loggers missing from modes, nothing feeding the cache | BUILDING | 12-04 | fork:deepsignal/p2-config-lint, `briefs/p2/127-config-lint.md` |
| #130 Instrument init profiles | Per-instrument, reviewed start-up command profiles sent on connect (MetAcq parity) | BRIEFED | 12-04 | `briefs/p2/130-instrument-init.md` |
| Setup MCP | About 5 high-level tools; read-only by default; any write needs approval plus a dry-run diff | DESIGNED | after engine | D-MCP1, #64, #65, `research/2026-11-18-mcp-reference-architecture.md` |
| Wizard pages | Console pages over #114, #125, #126, #128 | PROPOSED (console follow-up) | after MVP | `briefs/p2/INDEX.md` "What is left" |

## 7. AI and MCP

November 21 master directive: the six-workspace product and mandatory Grafana/InfluxDB
visualization service are tracked in [22 implementation tickets](MASTER-PRODUCT-TICKETS.md).
M1 fixture services, four Console routes and actual official-SDK MCP are in progress
on `deepsignal/workspace-m1`; the full platform and Grafana are not complete.


| Feature | What it does | Status | Target | Link |
|---|---|---|---|---|
| MCP analytical gateway (#20, #64) | Shared UI/CLI/MCP evidence, analysis, drafts and investigations; controls separately authorized | M1 IMPLEMENTATION/TESTING; full scope T-PROD-10 | after v2 | D-MCP1, `research/2026-11-18-mcp-reference-architecture.md` |
| Approval and apply service (#65) | Validator, diff, policy, human approval record, separate apply identity | PROPOSED | after v2 | `docs/IDEAS.md` |
| Provenance on every answer (#66) and query budgets (#67) | Each result carries source ids, bounds, counts, units, flags, computation; capped per call | PROPOSED | after v2 | `docs/IDEAS.md` |
| AI audit trail (#62) | Every AI question, tool call and answer logged with the data it read | PROPOSED | after v2 | `docs/IDEAS.md` |
| Console AI help | Ask for a view; works with no key, key server-side, provider-pluggable | DESIGNED | after MVP | `design/console-DESIGN.md` |
| #188 AI watch assistant (AI triage) | Runs only on events, never continuously (cost near zero); small on-ship model by default, works offline; optional capped cloud second opinion via MCP, off by default; evidence-linked causes and next checks; advises only, fixes go through approval; outcomes feed the runbooks (#167) | BRIEFED | 12-04 | `briefs/p2/188-ai-triage.md` |

## 8. Reanalysis of old cruise data (D-REAN1, D-REAN2)

Run DeepSignal over archived cruises in scored passes; flags and corrections are reversible ledger layers;
a pass is kept only if it beats the last on independent holdouts and the fault bench, with a person signing off
every value change. 21 modules over milestones M0 to M5. Pilot: three Revelle GO-SHIP cruises, TSG confirmed in RR2205.

| Feature | What it does | Status | Target | Link |
|---|---|---|---|---|
| Reanalysis loop (#63) | Scored, reversible passes over the raw archive | DESIGNED; Eugene's open choices in plan section 9 | after v2 | `research/2026-11-18-reanalysis-program.md` |
| Pilot cruises | Three Revelle GO-SHIP cruises from R2R | DESIGNED | after v2 | `research/2026-11-18-r2r-pilot-cruises.md` |
| Legacy archive readers (#59) | Read SCS, MetAcq and R2R files into the same records | PROPOSED | after v2 | `docs/IDEAS.md` |

## 9. Ecosystem: OceanDataTools integrations

How DeepSignal plugs into the rest of the OceanDataTools stack. Detail: `docs/ECOSYSTEM.md`.

| Feature | What it does | Status | Target | Link |
|---|---|---|---|---|
| #131 OpenVDM bridge | Quality day files plus a Data Dashboard plugin with pass, warning and fail tests | BRIEFED | v2 | `docs/ECOSYSTEM.md` |
| #132 Cruise context | Cruise id, dates and ports pulled from OpenVDM or Sealog | BRIEFED | v2 | `docs/ECOSYSTEM.md` |
| #133 Sealog bridge | Quality events, plus the quality state attached to every Sealog event | BRIEFED | v2 | `docs/ECOSYSTEM.md` |
| #134 Grafana quality pack | Mandatory shared visualization service, verified source mappings, drafts and independently approved publication | REQUIRED/OPEN T-GRAF-01–06 | G1–G6 | `docs/ECOSYSTEM.md` |
| #135 Archive and compression | Lossless zstd or xz with a verified manifest, plus prioritized shore bundles for OpenVDM ship-to-shore | BRIEFED | v2 | `docs/ECOSYSTEM.md` |
| #136 QA tool adapters | Adapters for external QA tools | PROPOSED (backlog) | later | `docs/ECOSYSTEM.md` |

## 10. Platform, gate and tooling

| Feature | What it does | Status | Target | Link |
|---|---|---|---|---|
| Linux gate (GitHub Actions) | Full suite on Linux for an exact sha, receipt per run | BUILDING r3 (da72a75 RED, 10 failures verified); review queued | 11-21 | desk branch `gate/linux-actions`, `briefs/gate-linux-r3.md` |
| Django shared-config-name fix (#1, core fix) | `test_basic` gets two LoggerConfigs; fix plus test | BUILT (ad10eb1), parked: nothing upstream yet (D-ARCH6) | when Eugene says | fork:django-gui/shared-config-names, `pr/django-shared-config-names.md` |
| Gate contrib mode (#49) | Runs `contrib/deepsignal/` tests, not only core `test/` | PROPOSED | 11-21 | `docs/IDEAS.md` |
| Target-parity scorecard generator | Generates `docs/TARGET-PARITY.md` from scored rows | DONE | done | `tools/target-parity/gen.py` |
| Reference check | Flags IDEAS numbers and briefs missing from this file | DONE | done | `tools/reference-check.py` |
| Public sample data catalog | Real-format sample files for tests (data stays on the shared mount, not in git) | DONE | done | `docs/SAMPLE-DATA.md` |
| ds-codex launcher | RAM-gated Mac launcher, separate Codex home, pinned sub-agents | DONE (desk 2c228e2, not yet on main) | done | D-SEP1, D-SUB1, `docs/CODEX.md` |
| Fork integration branch (D-INTEG1) | Merge target for non-critical modules that pass Astra ultra review (D-REVIEW1); one merge commit per module; never fork dev or master | CREATED 2026-11-18 from contrib master 3b4b76e (fork-only; recreated from dev 1a6f1edb before any merge) | done | fork:deepsignal/integration |

## 11. Ship systems, sonars, link health and instrument configuration (D-SHIP1, D-NOC1)

Passive first: DeepSignal listens to sonars, motion systems, the bridge and engineering, and never changes
their settings. Instrument configuration is propose, approve, apply, verify, roll back, for science sensors
only. Full design, ranked table, security and risk tables: `docs/SHIP-SYSTEMS.md`.

| Feature | What it does | Status | Target | Link |
|---|---|---|---|---|
| #139 Kongsberg datagram tap | Read-only KMALL and `.all` summaries: nadir depth, ping rate, swath, valid beams, SV applied, clock offset, runtime changes | BRIEFED (mac lane; reads two public format documents, approved) | v2 | `briefs/p2/139-kongsberg-tap.md` |
| #140 Sound velocity consistency | Probe vs TSG vs sonar-applied vs cast SV; names the odd one out | BRIEFED | v2 | `briefs/p2/140-sv-consistency.md` |
| #138 IEC 61162-450 bridge reader | Clean NMEA plus source id from bridge multicast, receive only | BRIEFED | v2 | `briefs/p2/138-iec450-bridge.md` |
| #141 Depth consensus | Multibeam nadir vs single-beam vs grid; lost bottom and step flags | BRIEFED | v2 | `briefs/p2/141-depth-consensus.md` |
| #156 Link health with NOC integration | One verdict per instrument link on top of OpenRVDAS logger status, stderr and cache timestamps; `/health` for Uptime Kuma, Zabbix or LibreNMS; their alerts in via webhook | BRIEFED | v2 | `briefs/p2/156-link-health.md` |
| #157 Serial device servers (Moxa, Pepperl+Fuchs and similar) | Vendor-neutral drivers; finds them, reads every port (settings, clients, bytes, errors), maps ports to loggers, writes reader configs, flags mismatches; changes only through #153 with approval | BRIEFED | v2 | `briefs/p2/157-device-servers.md` |
| #158 Seismic shot and source QC | Gun timing, missed shots, spacing, fire time vs GPS, shot positions from ship nav, P1/11-subset file; listen-only | BRIEFED | v2 | `briefs/p2/158-seismic-shot-qc.md` |
| #159 Streamer and bird QC | Bird depth and heading, SEG-D or SEG-Y channel health (vendor documents needed for live bird data) | PROPOSED | later | `docs/SHIP-SYSTEMS.md` |
| #160 Protected-species and mitigation view | PSO page with gun state, ramp-up, EEZ distance; events to Sealog | PROPOSED | later | `docs/SHIP-SYSTEMS.md` |
| #142 Time and motion alignment | Motion lag, sonar clock offset, sonar vs nav position | PROPOSED | v2 | `docs/SHIP-SYSTEMS.md` |
| #143 Sonar health board | Ping rate, swath, file-growth heartbeat, runtime changes as events | PROPOSED | v2 | same |
| #144 Acoustic transmit awareness | Who pings when; overlap detection; never controls a synchronizer | PROPOSED | later | same |
| #145 ADCP health and cross-checks | UHDAS and PD0, listen-only: cadence, self-test, heading vs gyro and GNSS (frozen heading), SV vs TSG, bottom track vs multibeam, ping overlap | BRIEFED | v2 | `briefs/p2/145-adcp-health.md` |
| #146 Motion and position status | POS MV Group status and Seapath quality, data port only | PROPOSED | v2 | same |
| #147 Sound-speed profile manager | Ingest, clean and extend every cast; age, distance and quality; new-cast advice; SIS `.asvp`, CSV and template exports (operator loads them) | BRIEFED (mac lane) | v2 | `briefs/p2/147-sv-manager.md` |
| #161 Sound-speed fusion and inferred error | Argo, climatology and model profiles weighted by quality and age; outer-beam bias as evidence (D-FUSE1) | PROPOSED | later | `docs/SHIP-SYSTEMS.md` |
| #148 Guarded Modbus adapter | Read codes 1 to 4 only, register catalog | PROPOSED | later | same |
| #149 NMEA 2000 via read-only gateway | PGN decode | PROPOSED (backlog) | later | same |
| #150 ECDIS route import | RTZ or RTE/WPL into #108 | PROPOSED | later | same |
| #151 OT network safety kit | Placement checklist, connection register, receive-only tests, lint rule | PROPOSED | v2 | same |
| #152 Instrument config reader | Tier R snapshots into #52 history | PROPOSED | later | same |
| #153 Config advisor | Explainable change proposals, advice only | PROPOSED | later | same |
| #154 Approved change apply with rollback | Tier A, science sensors only, on the #130 engine and #65 approvals | PROPOSED | later | same |
| #155 Scoped SSH access kit | Forced-command keys or short-lived certificates, full logging | PROPOSED | later | same |
| Sonar, bridge, DP, motion control, engine, winch writes | Never built (D-SHIP1) | BANNED | never | same |

### Sonar science (#170 to #181, T-SONAR)

More science and QC from the multibeam (bathymetry, backscatter, water column), SBP29, EK80 and ADCP, listen-only. Ranked research, math, validation plans and decisions: `docs/SONAR-SCIENCE.md`.

| Feature | What it does | Status | Target | Link |
|---|---|---|---|---|
| #170 Quality-weighted depth | Robust shared-error fit across MB nadir, single-beam, ADCP bottom track and SBP first return (NOVEL, live + replay) | BRIEFED | v2 | `briefs/p2/170-weighted-depth.md` |
| #171 Observable sound-speed error from crossing swaths | Ray-derivative test of which part of the sound-speed profile a crossing or repeat swath can actually constrain (NOVEL, live at crossings + post) | BRIEFED | v2 | `briefs/p2/171-swath-refraction.md` |
| #172 Crossline-tested sounding uncertainty | Per-beam vertical and horizontal uncertainty from measured inputs, with the dominant term named (ADAPTED, live + post calibration) | BRIEFED | v2 | `briefs/p2/172-sounding-uncertainty.md` |
| #173 Sub-bottom reflectors with multiple-echo competition | Path search for coherent shallow reflectors in SBP29 SEG-Y, competing against water-bottom multiple hypotheses so a geologist reviews the right traces (NOVEL, post) | BRIEFED | v2 | `briefs/p2/173-subbottom-reflectors.md` |
| #174 Seabed-anchored flares and repeat-pass strength | Tests whether repeat passes support a flare rising from the same seabed spot and whether its relative strength changed under comparable conditions (NOVEL, post) | BRIEFED | v2 | `briefs/p2/174-seep-repeatability.md` |
| #175 Scattering-layer motion after accounting for advection | Diel and layer motion with ADCP current advection removed (NOVEL, post) | PROPOSED | later | `docs/SONAR-SCIENCE.md` |
| #176 Relative backscatter drift on repeat ground | Gain and calibration drift between surveys from repeat ground, kept separate from facies so calibration stays identifiable (NOVEL, post) | PROPOSED | later | `docs/SONAR-SCIENCE.md` |
| #177 Acoustic facies across frequency and incidence | Angular-response and multi-frequency seafloor classes with physics priors, anchored to grabs and cores (ADAPTED, post) | PROPOSED | later | `docs/SONAR-SCIENCE.md` |
| #178 Excess receiver noise conditioned on transmit timing | Self-noise and interference map from the sonars themselves, conditioned on who was transmitting (NOVEL, live + replay) | PROPOSED | later | `docs/SONAR-SCIENCE.md` |
| #179 Hull aeration versus widespread echo loss | Separates bubble sweep-down (weather, heading, speed) from system faults when echoes drop out across sonars (NOVEL, live + replay) | PROPOSED | later | `docs/SONAR-SCIENCE.md` |
| #180 Opportunistic patch-test evidence | Roll, pitch, heading and latency bias evidence from ordinary survey lines, advice only (ADAPTED, post) | PROPOSED | later | `docs/SONAR-SCIENCE.md` |
| #181 Relative sediment attenuation tied to acoustic facies | Relative attenuation from SBP29 spectra, tied to facies (NOVEL, post) | PROPOSED | later | `docs/SONAR-SCIENCE.md` |

## 12. Operational truth layer (pain-points study)

From the RVTEC pain-points study. Ranked, phase 2 first. Sources: `docs/PAIN-POINTS-MAP.md`, `research/RVTEC-SURVEY.md`.

| Feature | What it does | Status | Target | Link |
|---|---|---|---|---|
| #162 Stream health chain | Per-stream stages (port, parse, cache, write), root cause, alerts on state transitions; console view v0 is an MVP stretch | BRIEFED | 12-04 | `docs/PAIN-POINTS-MAP.md` |
| #163 Config provenance | Every config change recorded with a semantic diff (what changed in ship terms, not just lines) | BRIEFED | 12-04 | `docs/PAIN-POINTS-MAP.md` |
| #164 Calibration and units registry | One registry of calibrations and units per channel, checked against the data | BRIEFED | 12-04 | `docs/PAIN-POINTS-MAP.md` |
| #165 Time health | Clock source, offset and timestamp sanity per instrument and host | BRIEFED | 12-04 | `docs/PAIN-POINTS-MAP.md` |
| #166 Continuous archive readiness | Shows at any moment whether the cruise archive would pass hand-off (R2R-ready) | BRIEFED | 12-04 | `docs/PAIN-POINTS-MAP.md` |
| #167 Alarm-linked runbooks | Each alarm opens the steps to fix it, written for a non-expert tech | BRIEFED | 12-04 | `docs/PAIN-POINTS-MAP.md` |
| #168 Unified event timeline and daily digest | One timeline of alarms, config changes, events and gaps, plus a daily summary | BRIEFED | 12-04 | `docs/PAIN-POINTS-MAP.md` |
| #169 Science trust view | Per-variable answer to "can I use this data now", with the evidence | BRIEFED | 12-04 | `docs/PAIN-POINTS-MAP.md` |

## 13. Novel and backlog ideas

Everything else in `docs/IDEAS.md` that is not yet in a table above. Status from IDEAS. Promote a row into a
table above when it gets a design, brief or branch.

<!-- backlog-index: generated from docs/IDEAS.md by tools/reference-check.py --backlog; edit IDEAS, not here -->
- #2 macOS UDP and timing test failures (PROPOSED)
- #3 Overlay package skeleton (PROPOSED)
- #9 State-aware alarms with watch verdicts (PROPOSED)
- #10 Redundant-sensor CUSUM drift (DESIGNED)
- #11 Drift vs independent references (DESIGNED)
- #14 Science, tech and shore views (PROPOSED)
- #15 Event log (DESIGNED)
- #16 Binned downloads (DESIGNED)
- #17 Ship-to-shore sync, bulk (PROPOSED)
- #18 Ship-to-shore sync, live (PROPOSED)
- #19 Bandwidth-aware link profiles (PROPOSED)
- #21 MCP issue-finding tools (PROPOSED)
- #22 MCP precision and calibration tools (PROPOSED)
- #23 Multi-AI-client support (PROPOSED)
- #24 Codex as a builder (PROPOSED)
- #25 Physics referee (sensor consensus) (PROPOSED)
- #26 Sensor digital twin (PROPOSED)
- #27 Cruise memory search (PROPOSED)
- #28 Self-writing cruise log (PROPOSED)
- #29 Plug-and-identify (PROPOSED)
- #30 Scientist co-pilot (PROPOSED)
- #31 Clock forensics (PROPOSED)
- #32 Provenance hashes (PROPOSED)
- #33 Time-travel replay (PROPOSED)
- #34 Plain-language alarms (PROPOSED)
- #35 Semantic ship-to-shore (PROPOSED)
- #36 Calibration foresight (PROPOSED)
- #37 Cruise narrator (PROPOSED)
- #38 Roll and heave cross-correlation (PROPOSED)
- #39 Ship turns for flow distortion (PROPOSED)
- #40 Diurnal solar heating bias (PROPOSED)
- #41 Tides and ADCP bottom track (PROPOSED)
- #42 GNSS reflectometry (PROPOSED)
- #43 Engine and pump vibration health (PROPOSED)
- #44 Fleet view (PROPOSED)
- #45 Open sensor-fingerprint library (PROPOSED)
- #46 Cost and savings status line (PROPOSED)
- #47 Agent bench (PROPOSED)
- #48 Retriever brief library (PROPOSED)
- #50 Wind averages for the bridge and $WICOR (PROPOSED)
- #51 Two-anemometer wind consensus (PROPOSED)
- #57 Uncertainty on every value (PROPOSED)
- #58 End-of-cruise R2R-ready package (PROPOSED)
- #60 Sensor response correction (PROPOSED)
- #61 Instrument diagnostic channels (PROPOSED)
- #68 Target MCP spec 2026-07-28 (PROPOSED)
- #69 Golden-cruise MCP eval suite and local model tiers (PROPOSED)
- #70 Read-only shadow pilot on Revelle or Sally Ride (PROPOSED)
- #71 Operator-from-docs install test (PROPOSED)
- #72 Non-OpenRVDAS stream adapters (CORIOLIX, SCS, MetAcq files) (PROPOSED)
- #73 Publication and funding track (PROPOSED)
- #74 Independence-aware calibration evidence graph (PROPOSED)
- #75 Public sparse-reference drift benchmark (PROPOSED)
- #76 Front-versus-drift competing hypotheses (PROPOSED)
- #77 Cross-vessel calibration priors (PROPOSED)
- #80 Directional wave spectrum from motion (PROPOSED)
- #81 Self-calibrating ship wave buoy (PROPOSED)
- #82 Current from SOG minus STW (PROPOSED)
- #83 GNSS precipitable water vapor (PROPOSED)
- #84 GNSS reflectometry for sea ice (PROPOSED)
- #85 Ionosphere TEC and scintillation (PROPOSED)
- #86 GNSS interference sentinel (PROPOSED)
- #87 Satellite-link rain gauge (PROPOSED)
- #88 Joint environmental inversion (PROPOSED)
- #89 Scattering-layer and migration atlas (PROPOSED)
- #90 Acoustic mixed-layer depth (PROPOSED)
- #91 Gas-seep discovery (PROPOSED)
- #92 Echosounder noise floor as machinery monitor (PROPOSED)
- #93 Rain and wind from underwater sound (PROPOSED)
- #94 Incidental marine-mammal detection (PROPOSED)
- #95 Live air-sea bulk fluxes (PROPOSED)
- #96 Mixing-state product (PROPOSED)
- #97 Submesoscale front detector (PROPOSED)
- #98 Vessel-performance digital twin (PROPOSED)
- #99 Environment-conditioned machinery health (PROPOSED)
- #100 Fuel and route counterfactual (PROPOSED)
- #101 Masked multirate ship encoder (PROPOSED)
- #102 Physics-conditioned representations (PROPOSED)
- #103 Cross-vessel sensor ontology (PROPOSED)
- #200 Side-effect-free CDS gate probe (ticket from the joint #197 run) (?)
<!-- /backlog-index -->

| Scoreboard writer (#5) | Latest-value boards: cache, layout, render loop; uses #182-#186 | BRIEFED, waits for #182-#186 to merge; stale threshold (Eugene) | after inputs | `briefs/deepsignal-scoreboard-writer.md`, D-SCORE1, D-SCORE2 |
| Scoreboard profiles (#182) | YAML profile per board model, strict schema, starter profiles | BRIEFED, wave 1 | p2 | fork:deepsignal/p2-scoreboard-profiles, `briefs/p2/182-scoreboard-profiles.md`, D-SCORE2 |
| Scoreboard transports (#183) | Serial, RS-485, TCP, UDP, Modbus RTU and TCP | BRIEFED, wave 1 | p2 | fork:deepsignal/p2-scoreboard-transports, `briefs/p2/183-scoreboard-transports.md` |
| Scoreboard text codec (#184) | Templated frames with address and checksum | BRIEFED, wave 1 | p2 | fork:deepsignal/p2-scoreboard-text-codec, `briefs/p2/184-scoreboard-text-codec.md` |
| Scoreboard Alpha codec (#185) | Alpha Protocol LED signs | BRIEFED, wave 1 | p2 | fork:deepsignal/p2-scoreboard-alpha-codec, `briefs/p2/185-scoreboard-alpha-codec.md` |
| Scoreboard Modbus codec (#186) | Register writes for Modbus-only large displays | BRIEFED, wave 1 | p2 | fork:deepsignal/p2-scoreboard-modbus-codec, `briefs/p2/186-scoreboard-modbus-codec.md` |
| Scoreboard bench tool (#187) | Check a profile's bytes, send a test frame | BRIEFED, wave 2 (after #182-#186 merge to `deepsignal/scoreboard-integ`) | p2 | fork:deepsignal/p2-scoreboard-bench, `briefs/p2/187-scoreboard-bench.md` |

## 13. Security architecture (D-SEC1 to D-SEC5, T-SEC)

Security-first design for the console, CDS, REST and MCP. Full design: `docs/SECURITY-ARCHITECTURE.md`. Security code merges wait for Eugene.

| Item | What | Status | Phase | Where |
|---|---|---|---|---|
| #189 Auth gateway | nginx TLS plus auth_request, one identity everywhere | DESIGNED | MVP | `docs/SECURITY-ARCHITECTURE.md` |
| #190 MFA | TOTP for admin (MVP), WebAuthn/FIDO2 later | DESIGNED | see doc | `docs/SECURITY-ARCHITECTURE.md` |
| #191 Break-glass, kiosk and service identities | Sealed emergency access and non-human identities | DESIGNED | see doc | `docs/SECURITY-ARCHITECTURE.md` |
| #192 Secrets vault | One AES-256-GCM envelope vault; #188 AI stays off until it lands | DESIGNED | see doc | `docs/SECURITY-ARCHITECTURE.md` |
| #193 Tamper-evident audit log | Hash-chained JSONL | DESIGNED | see doc | `docs/SECURITY-ARCHITECTURE.md` |
| #194 Approval service and signed config history | Trusted approvals and receipts (answers MCP review F1/F2) plus content-addressed signed config versions; `docs/APPROVALS.md`; branch `deepsignal/sec-approvals`, Mac Astra high, v2 | DESIGNED | see doc | `docs/SECURITY-ARCHITECTURE.md` |
| #195 Crypto profile and FIPS path | One approved-algorithm profile; RHEL 9 reference platform | DESIGNED | see doc | `docs/SECURITY-ARCHITECTURE.md` |
| #196 STIG-aligned policy profile | Standard versus STIG profile | DESIGNED | see doc | `docs/SECURITY-ARCHITECTURE.md` |
| #197 Trust zones and CDS write lockdown | Bind CDS to localhost, refuse unauthenticated publish | DESIGNED | MVP | `docs/SECURITY-ARCHITECTURE.md`, D-SEC0 |
| #198 Supply chain | Pinned dependencies, signed releases | DESIGNED | see doc | `docs/SECURITY-ARCHITECTURE.md` |
| #199 MCP read-filtered CDS broker | Field filtering, admission limits, quotas, reserved logging disk before any remote MCP use | DESIGNED | later | `research/2026-11-18-mcp-design.md`, `research/2026-11-18-mcp-design-review.md` |
