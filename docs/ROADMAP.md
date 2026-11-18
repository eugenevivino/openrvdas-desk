# Roadmap

Ranked. Unblockers first. Each line becomes a brief when it is next. Every
phase ends with something a science party, bridge, technician, or shore
support person can use.

## Phase 0: the desk works (this week)

1. Create the desk repo and push this tree (Eugene).
2. Mini setup and first green gate receipt on fork `dev` (mini/SETUP.md).
3. Confirm the Django `test_basic` failure on `dev` under 3.12. If real,
   draft an upstream issue with a failing test (Eugene sends).
4. Ask upstream the three placement questions in one message: scoreboard
   writer, vector wind averaging, MCP server: core, contrib, or separate?

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

## Phase 3: Cruise Console (gated on the OSU conversation, D-CONSOLE1)

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

- Drift detection against independent references across instruments.
- Change-point segmentation of a cruise into stations and transits.
- AI narrator for shore support: "what changed on the ship in the last 6 h".
- Replay lab: any recorded cruise replayed through new transforms with a diff
  report, used as the high-risk review check.
