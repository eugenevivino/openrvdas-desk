# Brief: deepsignal-post-cruise-drift

- Decision: D-SOII1 (IDEAS #54, uses #53 and #56; Eugene approved 2026-11-18)
- Risk tier: high (drift statistics that propose data corrections)
- Module: exactly one, offline post-cruise drift review. Branch `deepsignal/post-cruise-drift`
- Base: `OceanDataTools/openrvdas_contrib` `master` at 3b4b76e, after `deepsignal/fault-bench` and `deepsignal/correction-ledger` are green (read their docs, do not import their code except the bench runner in tests)
- Mac scratch path: `/private/tmp/deepsignal/post-cruise-drift/` only (docs/CODEX.md rule 1b)
- Lane: `mac`. Model id for `-m` (rule 27) and effort: `gpt-6.2-astra`, high (math), with `KALON_ALLOW_ASTRA=1` for this job only, fresh session, under 40 turns. Review: a separate fresh `gpt-6.2-astra` xhigh, read-only.
- Upstream home: openrvdas_contrib (Eugene sends the PR)

## Goal
After a cruise, a tech or data manager runs one command and learns, per
sensor, whether it drifted, by how much, with an honest error bar, or that
the data cannot tell; any drift found becomes a proposed correction a person
must approve.

## Background facts (do not re-derive)
- Retrospective mode may use data after time t to judge time t. This tool is
  offline only and must refuse to run inside a logger (no Transform class).
- References: a paired redundant sensor (same quantity), and sparse points
  (CTD or bottle values) in a CSV `time,value,uncertainty`. Optional pre- and
  post-cruise calibration offsets.
- Correction proposals use the ledger format in `contrib/deepsignal/docs/correction_ledger.md` (#56), status `proposed`, author `post-cruise-drift <version>`.
- Pure stdlib (no numpy). On the MacBook use `python3.12 -m unittest`.

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/drift_review/`:
- Input: OpenRVDAS log files (text, via the existing LogfileReader and a
  parse step, or already-parsed JSON lines), sensor field, reference field
  or points file, time window.
- Model: difference d(t) = sensor minus reference, binned to a fixed
  interval (default 10 min). Local-linear-trend state space (bias and drift
  rate) with a forward Kalman filter and Rauch-Tung-Striebel backward
  smoother. Process and measurement noise from a stated default or estimated
  by maximum likelihood over a small grid; report which.
- Change points: CUSUM on innovations to split segments at steps; each
  segment gets its own bias and rate.
- Verdict per segment: `drift` (rate interval excludes zero and size over a
  configured tolerance), `no_drift` (interval inside tolerance), `cannot_tell`
  (interval spans both, too few reference points, or a trap pattern: the
  reference moved with the sensor). Never force a verdict.
- Pre/post calibration offsets, when given, are a check: report agreement or
  conflict with the smoothed end-point bias.
- Outputs: `report.md` (one row per segment: verdict, bias, rate per day, 95%
  interval, reference points used), `smoothed.csv`, and `proposals.jsonl` for
  `drift` segments only.
- CLI `python -m contrib.deepsignal.drift_review run --config <yaml>`.

## D-REAN2 additions (drift report, 2026-11-18; lead decisions, these win over the Design list above where they differ)
- Verdicts use the seven states in plan section 10.1
  (`research/2026-11-18-reanalysis-program.md`): `no_drift` becomes GOOD,
  `cannot_tell` becomes AMBIGUOUS, `drift` becomes CORRECTABLE only when the
  abstention rule below passes, else SUSPECT; a segment overlapping a
  `pump_off` window is UNCORRECTABLE. Define the states as string constants
  in this package for now; a later `verdict-states` module will own them.
- State: offset and optional gain (C0 to C4 of the model ladder, section
  10.7). Fit each candidate on the fit split of reference points, score on
  the held-out split (every third reference point by time, blocked, stated
  in the report), choose the simplest model unless a richer one lowers
  held-out RMSE by more than its own uncertainty.
- Change points on Kalman innovations (as above), plus forced breaks passed
  in as a list of UTC times (from the instrument history `segment_breaks`).
- Uncertainty: report a standard uncertainty for each proposed correction by
  Monte Carlo over the fitted parameters (stdlib `random`, fixed seed, 2000
  draws by default) and a 95% interval.
- Abstention: CORRECTABLE needs |correction| >= 2 x its standard uncertainty
  AND held-out residuals improve. Otherwise SUSPECT or AMBIGUOUS, never a
  proposal.
- Proposals carry `fit_refs` and `validation_refs` (disjoint lists of
  reference point ids), `model_id` (C0 to C4) and `correction_state`.
- Tests add: gain-only fault picks C2 not C1; held-out split never used in
  the fit (assert on ids); a forced break splits a segment with no visible
  step; a small correction inside 2u is not proposed; pump_off window gives
  UNCORRECTABLE.

## Failing test first
`contrib/deepsignal/test/drift_review/test_*.py`. RED first.
Cover: Kalman and RTS against hand-computed values on a 5-point series;
recovers a known linear drift within its interval; step change split by
CUSUM; no drift gives `no_drift`; sparse references give `cannot_tell`;
front trap gives `cannot_tell` or `no_drift`, never `drift`; proposals match
the ledger format; no Transform exported. Run the #53 bench `drift`, `step`
and `front` scenarios and report the numbers (do not tune to them).

## Module contract
- Sample config `contrib/deepsignal/configs/drift_review_example.yaml` on NBP1406 data.
- Docs `contrib/deepsignal/docs/post_cruise_drift.md`: purpose, "Run it in 5
  minutes", how to read each verdict, why live mode cannot do this, what it
  does NOT do (no automatic correction, no claim when data cannot tell).

## Acceptance (exact commands, from repo root)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/drift_review -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal
```
```
python3.12 -m contrib.deepsignal.drift_review run --config contrib/deepsignal/configs/drift_review_example.yaml
```

## Scope
Create or change only files under `contrib/deepsignal/drift_review/`, its
tests, its config and its doc. Everything else read-only. Do not commit.

## Trust boundaries and data integrity
Never write to input log files or the live ledger; write proposals to the
output folder only. State every assumption (noise values, bin size) in the report.

## Non-goals and banned
No live transform, no numpy or scipy, no auto-approval, no core changes. No
writes outside `/private/tmp/deepsignal/post-cruise-drift/` (rule 28).
docs/CODEX.md rule 13 applies.

## Report format
Under 40 lines: files, test names, RED then GREEN tail, flake8, bench numbers, design points you disagree with, verified vs inferred.

## Stop rule
Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Linux check:
- What changed, in three lines:
- Open questions:
