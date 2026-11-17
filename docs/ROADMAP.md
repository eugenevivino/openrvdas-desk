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

## Phase 1: small, high-value upstream PRs

5. Vector wind averaging transform (D-METACQ1). Small, fixes a real error,
   good first PR to build trust with the maintainer.
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

## Bold bets (kept, not scheduled)

- Drift detection against independent references across instruments.
- Change-point segmentation of a cruise into stations and transits.
- AI narrator for shore support: "what changed on the ship in the last 6 h".
- Replay lab: any recorded cruise replayed through new transforms with a diff
  report, used as the high-risk review check.
