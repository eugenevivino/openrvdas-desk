# Pain points to DeepSignal: gap map and reprioritization

Written 2026-11-18 by the parity thread from `docs/PAIN-POINTS.md`, the Deep Research study Eugene ran. Eugene
approved acting on these recommendations the same night ("Do what is recommended"). Item numbers are
from `docs/IDEAS.md`.

## Positioning (proposed D-POSITION1)

**DeepSignal is the vessel's operational truth layer. It interoperates with UHDAS, SIS and SCS and does not
replace them.**

The study finds that the hardest failures sit *between* systems. The sensor, interface, parser,
calibration, timestamp, metadata, store and archive drift apart while every process still shows
"running." DeepSignal answers five questions:

1. Is the data actually healthy?
2. Why do we believe that?
3. What changed?
4. What is affected?
5. Is the cruise package complete?

It must work fully offline. It must never require Kubernetes-class skills, which the study's NERC DAMP
lesson warns against.

Coverage key: **Full** means a briefed or built item does it. **Partial** means part of it is covered.
**Gap** means nothing does it yet. **New** means a brief was written tonight.

## A. The 15 ranked pain points

| # | Pain point (sev) | Covered by | How well | Missing, and where it went |
|---|---|---|---|---|
| 1 | Silent or late-found quality failure (5) | QARTOD flags (#8, built), #79 dependency graph, #10 and #11 drift, #51 wind consensus, console freshness and stale banner (MVP) | Partial | Physical-state context and per-stage chain: **New #162** (engine and console chain view). Wrong calibration or units: **New #164** |
| 2 | Config drift and correctness (5) | #127 lint, #126 diff, #56 correction ledger | Partial | Versioned history, semantic diffs and baseline drift: **New #163** |
| 3 | Time sync and timestamp integrity (5) | #31 clock forensics (idea), #142 time and motion (idea), #119 NTP offset | Gap | Host sync, per-stream timestamp source and confidence, skew: **New #165** |
| 4 | Feed failure and ambiguous fault location (5) | #125 discovery, #157 device servers, #130 TCP client reader, health page (MVP) | Partial | Stage-by-stage localization: **New #162** |
| 5 | Packaging, naming and metadata inconsistency (4) | #58 R2R package (idea), #120 and #132 cruise metadata, #131 OpenVDM, #135 manifests | Partial | Live expected-vs-present readiness: **New #166** |
| 6 | Freshness and state visibility, not "process running" (5) | Console core freshness, stale banner, health, source-loss test (all MVP) | Full for the console | Explicit nulls and age fields for Grafana: in **#162** (`ds_age_s`, timeout null) |
| 7 | Tribal knowledge and rotating staff (4) | #118 doc store, #52 history, stale-banner first-action table | Partial | Vessel runbooks linked to alarms, last fixes: **New #167** |
| 8 | Per-cruise setup too manual (4) | #114 wizard, #125-#128, #126 generator, #132 cruise context, #124 installer | Full (briefed) | Vessel baseline plus cruise-only deltas: **#163** drift |
| 9 | Underway sensors fail physically (4) | #110 flow state, #52 history, #113 geometry, #8 QC | Partial | Intake, orientation and fouling checks recorded as stage facts: **#162** sensor stage plus **#167** checks |
| 10 | Visible fault, hard to interpret (4) | #79, #78 coupling, #140, #141, #145 | Partial | Time-correlated "what changed before": **New #168** timeline |
| 11 | Bandwidth and offline (4) | #17-#19, #123, #135 bundles, #131 S2S | Full (briefed) | none |
| 12 | Closed vendor environments (4) | Open source by design, #72 adapters, #138-#139 read-only taps | Full by architecture | none |
| 13 | Different interfaces per vessel (3) | Console auto pages (MVP), #44 fleet view | Partial | Same console on every ship is the answer; no new item |
| 14 | Backups, disks and storage failures (5) | #119 host health | Partial | A Store stage in **#162** (newest file must grow); backup verification stays in #119 |
| 15 | Staffing limits create gaps (4) | Automation overall | Partial | Daily digest, UHDAS-style: **#168** `digest` |

## B. The 16 opportunity rows

| Opportunity | Covered by | How well | Missing |
|---|---|---|---|
| Universal data-health model | Console freshness (MVP), **#162** | Full once #162 lands | none |
| State-transition alerting | Stale banner (grouped, clears), #9 (idea), **#162** transitions, #133 change-only events | Full once #162 lands | none |
| Config provenance and drift | **#163** | Full (briefed) | Signed history (#32) later |
| Calibration and units registry | #7 (designed), **#164** | Full (briefed) | Certificates through #118 |
| Physical-sensor context | #52, #110, #113 | Partial | A "physical check" checklist per stream (in #167 runbooks); a sensor-presence check (SAMOS "phantom channels") belongs in #127 lint: added as a follow-up note |
| Dependency-aware fault localization | **#162**, #79 | Full once both land | none |
| Time-health service | **#165** | Full (briefed); PTP out of scope (weak evidence) | PTP later |
| Cruise-mode templates | #126, #132, #163 | Full (briefed) | none |
| Continuous archive readiness | **#166**, #135, #131 | Full (briefed) | Repository acceptance status (needs R2R contact) |
| Role-based displays | Bridge and kiosk (MVP), #115, **#169** trust view, #123 shore | Full once #169 lands | none |
| Integrated runbooks | **#167** | Full (briefed) | none |
| Event annotation timeline | **#168**, #15, #133 Sealog | Full (briefed) | none |
| Bandwidth-aware replication | #17-#19, #123, #135, #131 | Full (briefed) | Resumable transfer is OpenVDM's |
| Offline-first security | #115 roles, #151 OT safety kit, #155 scoped SSH, read-only defaults | Partial | Signed audit (#32) and local identity; **critical, in MORNING** |
| PSO and seismic event integration | #160 PSO view, #158, #159 | Partial | The study rates seismic evidence insufficient: hold #158 and #159 for interviews |
| Serial-server inventory and diagnostics | #157, #125, #130 TCP client | Full (briefed or designed) | none |

## C. New briefs (IDEAS #162-#169, written tonight)

All are cloud jobs on Sol medium, fork only, with disjoint paths. The Python items are on contrib base
`3b4b76e`; the console items are on `deepsignal/console-contract`.

| Rank | # | Brief | Kind | Value (techs/science/shore) |
|---|---|---|---|---|
| 1 | #162 | `briefs/p2/162-console-chain.md`: console chain view v0, the **MVP stretch** | node | 5/3/3 |
| 2 | #162 | `briefs/p2/162-stream-health.md`: stream health engine with stages, transitions and timeout nulls | py | 5/4/4 |
| 3 | #164 | `briefs/p2/164-cal-units-registry.md`: calibration and units registry | py (high risk: values) | 5/5/3 |
| 4 | #165 | `briefs/p2/165-time-health.md`: time health | py | 5/5/3 |
| 5 | #163 | `briefs/p2/163-config-provenance.md`: config provenance with semantic diffs | py | 5/3/4 |
| 6 | #168 | `briefs/p2/168-event-timeline.md`: unified event timeline plus daily digest | py | 4/5/4 |
| 7 | #167 | `briefs/p2/167-runbooks.md`: alarm-linked runbooks | py | 5/2/2 |
| 8 | #166 | `briefs/p2/166-archive-readiness.md`: continuous archive readiness | py | 3/4/5 |
| 9 | #169 | `briefs/p2/169-console-trust.md`: science trust view | node | 2/5/4 |

## D. MVP recommendation (console, Tue 11-25)

**Freshness and staleness are already in the MVP.** Console core freshness, the stale banner, the health
page and the source-loss test (STALE within 10 s) are all Wave 1 or 2. Nothing has to move.

**Recommended: add the dependency-chain view to the MVP as a thin v0, on the same stretch rule as the map.**
It ships in the MVP only if it is green by Fri 11-21; otherwise it moves to the first post-MVP drop.

- **Why:** it is the single most-cited gap in the study (pain points 1, 4, 6 and 10). It also turns the
  health page from "process running" into "which stage broke."
- **Why it's cheap:** v0 needs no new backend. It derives five stages (logger, arriving, parsed, fresh,
  quality) from data the console already has. Time and Store show "not monitored yet" until the #162
  engine fills them.
- **Why it's low risk:** it is one new module folder with no contract change, read-only, and its files
  don't overlap any MVP task.

Not recommended for the MVP: the trust view (#169) and everything else in section C. They go first in the
next wave, so the integration date of Thu 11-20 stays safe.

## E. Phase 2 reprioritization (v2)

New order for phase 2 launches after the MVP. Work already running finishes.

1. **Truth-layer core:** #162 engine, #164, #165, #163, #168, then #167, #166, #169.
2. **Ecosystem plumbing that carries truth outward:** #133 Sealog, #131 OpenVDM, #134 Grafana (gains
   `ds_age_s` from #162), #132.
3. **Setup and config assist:** #125-#128, #114, #126, #124.
4. **Parity features:** the rest of #104-#124 and #130, #135 and #137, in their existing value order.
5. **Hold for interviews** (the study rates the evidence insufficient): #158 seismic shot QC and #159
   streamer QC. #137 EEZ mode stays because Eugene asked for it, but its policy defaults get validated in
   interviews.
6. **Backlog unchanged:** the AI and science moonshots (#25-#37, #80-#103) stay ideas until the truth
   layer exists, because they depend on trustworthy inputs.

## F. Critical items, waiting in MORNING (not launched tonight)

- **Offline-first security:** signed audit records, local identity, and the trust-zone model (#32, #115,
  #151 and #155 together). This is security work, so it waits for Eugene.
- **#164 coefficients:** these change derived values. The build runs tonight, but enabling the transform
  on any live config waits for Eugene.

## G. Interview questions

The study's 18 questions are in `research/RVTEC-SURVEY.md`, each mapped to the items it validates.
