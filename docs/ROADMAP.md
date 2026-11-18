# Roadmap

The full idea list, with status and source, is `docs/IDEAS.md`. This file
ranks what is next. Ranked. Unblockers first. Each line becomes a brief when it is next. Every
phase ends with something a science party, bridge, technician, or shore
support person can use.

## Phase 0: the desk works (this week)

1. Create the desk repo and push this tree (Eugene).
2. Mini setup and first green gate receipt on fork `dev` (mini/SETUP.md).
3. Confirm the Django `test_basic` failure on `dev` under 3.12. If real,
   draft an upstream issue with a failing test (Eugene sends).
4. Fork `openrvdas_contrib` (Eugene), read its layout and rules, and plan the
   overlay package and gate around it (D-ARCH2).

## Phase 1: the overlay package, first modules (D-ARCH1)

All of this lands in `openrvdas-overlay`, not in core. Core gets only small
bug-fix PRs (the Django `test_basic` failure is the first candidate).

5. Overlay skeleton: package, CachedDataServer client, config examples that
   load overlay modules by `module:` path, its own gate. Then the vector wind
   averaging transform (D-METACQ1): small, fixes a real error.
6. ScoreboardWriter with one real board (D-SCORE1), after the make and model
   are known.
7. $WICOR writer (D-METACQ1), after the manual close read.
8. Per-sensor calibration records (schema plus transform).

## Phase 2: the layer people see

9. Health board: every sensor, last value, age, QC flag, alarm state.
10. Night-safe bridge display: huge readouts, relative wind, night mode,
    stale shown as stale.
11. QC flags as data (QARTOD-style tests emitting flags) (D-AI1).
12. MCP, superseding D-MCP1 (see D-MCP2). Design: https://claude.ai/artifact/VtfCM7KR2oRVa1BXiqnbFb
    - (a) MCP read core in `contrib/deepsignal/mcp/`: tools fields, values (CDS window only), status; proposal store; `setup-client` and `doctor` commands. Codex, Sol medium.
    - (b) Setup engine facade `contrib/deepsignal/setup/` with detect/propose/diff/validate, after #125, #114, #126, #127, #128 land. Integration work.
    - (c) MCP setup tools detect, propose, diff, validate on top of (b). Codex, Sol medium.
    - `apply` (approval, rollback, init commands) is phase 3, after a high-risk review.

## Phase 3: Cruise Console (D-CONSOLE1)

13. Sensor registry and event log.
14. Binned downloads and ship-to-shore snapshots sized for the satellite link.
15. Alerts with acknowledgement.

## Ultra-novel capabilities (Eugene 2026-11-18: "ULTRA novel")

Things no shipboard DAS we found does today (CORIOLIX, SCS, MetAcq, Grafana
stacks). Each is an overlay module. Novelty claims are inferred from the
competitive research, not exhaustively verified; check before saying "first"
anywhere public.

1. Sensor consensus engine. Redundant and physically linked sensors check
   each other live: two anemometers plus GPS plus gyro for true wind; gyro
   heading vs GPS course at speed; hull SST vs TSG intake with the plumbing
   lag fitted. Disagreement becomes a QC flag with the physics that failed.
2. Clock forensics. Ship roll and heave show up in many instruments;
   cross-correlating them measures each instrument's clock skew and latency
   continuously, and flags a drifting serial timestamp before it corrupts a
   cruise.
3. Provenance on every value. Each record carries a short lineage hash (raw
   line, parser, transform chain, calibration version). Daily signed
   manifests make a cruise dataset reproducible and tamper-evident.
4. Time-travel bridge. Scrub the whole ship state to any past second, and
   re-run new transforms over recorded raw data with a diff against what was
   logged (also our high-risk review check).
5. Plug-and-identify. Fingerprint an unknown serial or UDP stream (NMEA
   talker IDs, sentence shapes, rates) and propose a parser config for a
   technician to accept.
6. Automatic event log. Change-point detection marks stations, CTD casts,
   transits and weather shifts into the event log as suggestions a watch
   stander confirms.
7. Plain-language alarms, deterministic at runtime. "Wind over 30 kn on the
   bow while the CTD is in the water" is compiled once by an LLM into a
   reviewed rule; the ship runs the rule, not the model.
8. Semantic ship-to-shore. Send changes, anomalies and model parameters
   instead of raw streams; shore rebuilds the picture and asks for detail on
   demand. Sized for a constrained satellite link.
9. Calibration foresight. Forecast drift per sensor against independent
   references and say which sensor will leave spec before the next port.
10. Cruise narrator. Shore support asks "what changed on the ship in the last
    6 hours" and gets an answer built from flags, events and alarms, with
    every claim linked to the data.

## Bold bets (kept, not scheduled)

- Fleet view: the same overlay on several ships, compared side by side on
  shore (sensor health and calibration across the fleet).
- Open sensor-fingerprint library shared between ships and institutions.

## Parked: MCP gateway and shadow pilot (not scheduled)

From the 2026-11-18 research notes. MCP v1 is read-only plus proposal-only with a
separate approval and apply service (#64-#69). Shadow pilot and packaging question: #70,
#71, D-ADOPT1 (open for Eugene). Nothing here starts until he picks it.

## MVP #1: the Console display (Eugene 2026-11-18, target Tue 2026-12-02)

Eugene: "MVP first is the console display", wanted in one to two weeks, with some added good
functionality and stable integration into OpenRVDAS. Everything below ranks ahead of non-console
modules (#78, #79, #54, correction ledger follow-up). Cloud tasks already running finish; no new
non-console cloud or Mac jobs start until the console path is unblocked.

**"Stable integration" is a test, not a feeling (all must pass):**
1. A stock OpenRVDAS logger (no core changes) with a sample config (NBP1406 replay) feeds the console on Linux
   (Ubuntu 22.04, Python 3.12), started from the documented 5-minute steps only.
2. 24-hour soak on a replay at real rate: no crash, no restart, resident memory growth under 5 percent
   after warm-up, no unbounded queue, no log growth over the stated cap.
3. Source loss test: kill the logger mid-run, the console shows STALE within 10 s and recovers without a
   restart when data returns. Garbage and out-of-order input never crash it.
4. The Linux gate (receipt on the exact sha) covers the console tests; stock OpenRVDAS tests stay green
   (only the known `test_basic` Django RED, excused by name).
5. A usability pass on the checklist (`docs/USABILITY.md`) with the night RED mode one tap away on every page.

**Dated plan v2 (parallel cloud build, Eugene 2026-11-18 "I want it FAST"; Pacific dates, estimates):**
Cloud runs 6 to 8 Sol-medium tasks at once on disjoint files, each on its own fork branch (briefs in
`briefs/console/`, prompts in `briefs/cloud/`). The Mac is for Astra reviews, Playwright and RAM-safe work only.
| Date | Milestone | Done when |
|---|---|---|
| Tue 11-18 night | Wave 0 submitted | test harness pieces (logger fixture, soak runner, source-loss test) and core v2 running in cloud |
| Wed 11-19 | Wave 1 submitted and landing | charts, health, bridge, auto pages, stale banner, kiosk and Night, install.sh and self-test, each on its branch |
| Thu 11-20 | Integration branch `deepsignal/console-mvp` | all pieces merged on the fork, vitest green on Linux Node 22, Astra review (ultra) running |
| Fri 11-21 | Test 1 and the gate | console runs on the sample config; Linux gate GREEN on the sha; usability checklist walked |
| Sat 11-22 | 24-hour soak starts | harness records memory every minute |
| Mon 11-24 | Soak and source-loss results | tests 2 and 3 pass or a fix round is queued |
| Tue 11-25 | MVP candidate (one week earlier than Dec 2) | Eugene reviews; nothing goes upstream (D-ARCH6) |
Risks that can move dates: core v2 landing late (everything branches from it), the cloud env needing Node 22,
the Linux gate fix round (r3) and its review, Mac RAM pressure for the reviews, and the soak needing a quiet Mac or the Mini.

**Dependencies in build order:** console core, Health page, QARTOD flags on the console (branch
`deepsignal/qartod-flags`, built, needs independent review), instrument history lookup on the console (#52,
cloud task running), fault bench (#53, built) as the soak and failure driver, the Linux gate fix round
(r3) so the console tests are covered by a real gate. "Added good functionality" list: from the dashboard
thread, to be approved by Eugene (pending).

## Phase 2: parity build-out, 21 ideas (#104 to #124), approved by Eugene 2026-11-18

Goal (Eugene): close the scorecard gaps to about 98 percent of CORIOLIX and MetAcq features. The
number comes from the scorecard generator (`tools/target-parity/gen.py`, `docs/TARGET-PARITY.md`),
not from a claim: every gap valued 12 or more closed, remaining rows scored as covered. Console MVP keeps
top priority through 2026-11-25: phase 2 may use cloud capacity but must not take merge or review capacity
from the console. Everything is built on the fork, one branch per item, nothing upstream (D-ARCH6).

**Order (scorecard gap ranking, independent Linux-only items first):** #104 ERDDAP generator, #105 REST API,
#110 flow tagging, #111 SAMOS and met report writers, #112 formula library (core-fork), #113 vessel geometry,
#117 standard vocabularies, #120 cruise metadata, #123 shore snapshot, then #106 best-source selector
(core-fork), #108 routes, #109 cast view, #114 sensor wizard, #115 roles, #116 release policy, #118 document
store (on #52), #119 host health (console health page), #121 device pack, #122 small core fixes. #107 map is
console module 5, #124 install clock is submitted.

**Dated estimate (Pacific, estimates, cloud-parallel):**
| Date | Milestone |
|---|---|
| Wed 11-19 to Thu 11-20 | briefs for all 21 written; first batch (9 independent items) submitted to cloud |
| Fri 11-21 to Mon 11-24 | second batch submitted; acceptance runs batched on the Mac behind the RAM gate; console reviews go first |
| Tue 11-25 | console MVP candidate (priority 1) |
| Wed 11-26 to Tue 12-01 | phase 2 reviews (Astra high, one at a time), fix rounds, integration branch `deepsignal/p2-integration` |
| Fri 12-04 | phase 2 candidate: all items built, each reviewed, Linux gate GREEN, scorecard regenerated |
Real limits: Astra review capacity on the Macs (RAM gate, one job at a time), merge conflicts (disjoint files rule),
and the Linux gate fix round (r3) landing. If reviews run behind, date moves, review is never skipped.


- Design-polish pass 11-22 to 11-24, after integration: one Codex job (Sol 6.2 high, Mac, build-side) running Impeccable critique, typeset, polish, audit, then re-run V1 to V9. Expect a few V3 spacing hits from tasks briefed before the 4 px rule; the polish pass fixes them. The 11-25 MVP report attaches the contact sheet and V5 to V7 numbers.
