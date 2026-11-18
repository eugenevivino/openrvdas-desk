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
12. `openrvdas-mcp` phase 1, read-only (D-MCP1).

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

**Dated plan (Pacific dates; each step ends with something usable):**
| Date | Milestone | Done when |
|---|---|---|
| Wed 11-19 | Console core builds, MVP scope frozen with the dashboard thread | modules 1 to 4 briefed or built, "added functionality" list approved by Eugene |
| Fri 11-21 | Console runs on the sample config | test 1 passes on the Mini; health page and a QARTOD flag column visible |
| Tue 11-25 | All pages and red night mode | usability checklist walked; independent Astra review of the console (ultra) |
| Fri 11-28 | 24-hour soak starts (must start by 11-29 to finish) | soak harness records memory every minute |
| Mon 12-01 | Soak and source-loss results | tests 2 and 3 pass or a fix round is queued |
| Tue 12-02 | MVP candidate | Linux gate GREEN on the sha; Eugene reviews; nothing goes upstream (D-ARCH6) |

**Dependencies in build order:** console core, Health page, QARTOD flags on the console (branch
`deepsignal/qartod-flags`, built, needs independent review), instrument history lookup on the console (#52,
cloud task running), fault bench (#53, built) as the soak and failure driver, the Linux gate fix round
(r3) so the console tests are covered by a real gate. "Added good functionality" list: from the dashboard
thread, to be approved by Eugene (pending).

