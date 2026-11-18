# Brief: deepsignal-fault-bench

- Decision: D-SOII1 (IDEAS #53; Eugene approved 2026-11-18)
- Risk tier: medium (test tooling that will judge QC modules; wrong scoring misleads)
- Module: exactly one, fault-injection benchmark. Branch `deepsignal/fault-bench`
- Base: `OceanDataTools/openrvdas_contrib` `master` at 3b4b76e (fork branch already created at 3b4b76e)
- Mac scratch path: `/private/tmp/deepsignal/fault-bench/` only (docs/CODEX.md rule 1b)
- Lane: `cloud` (Sol medium, fixed, so no `-m`; rules 8 and 27, D-TEAM7), fresh task, under 40 turns. Review: fresh `gpt-6.2-astra` high on a Mac, read-only.
- Upstream home: openrvdas_contrib (Eugene sends the PR)

## Goal
Prove, with numbers, how fast a quality or drift module catches a broken
sensor and how often it cries wolf, by replaying clean sample data with known
faults injected.

## Background facts (do not re-derive)
- Sample data: NBP1406 in the contrib tree at `test/NBP1406/mwx1` (2024 tree;
  current core uses `test/NBP1406/data/mwx1`). Support both paths.
- Detectors under test are OpenRVDAS Transforms that add flag fields
  (QARTOD convention `<field>_QC`: 1 good, 2 not checked, 3 suspect, 4 bad,
  9 missing). The QARTOD module is on another branch; do NOT depend on it.
- On the MacBook use `python3.12 -m unittest`.

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/bench/`:
- `faults.py`: pure functions over a list of `(timestamp, value)`, each
  deterministic given `seed`, each returning the new series plus a truth
  label list `[(start, end, fault_name)]`: `drift` (linear, units per hour),
  `step` (bias), `lag` (first-order, time constant seconds), `hysteresis`
  (different offset rising vs falling), `clock_jump` (timestamps shift by N s),
  `clock_reset` (timestamps go backwards), `spikes` (count, size), `flatline`
  (stuck value), `dropout` (values become None).
- `traps.py`: real-world events that must NOT be flagged: `front` (a step
  applied consistently to two physically linked fields at once, e.g. two
  temperature fields), `turn` (smooth heading sweep). Truth label `trap`.
- `scenarios.yaml`: named scenarios = source field, fault or trap, parameters, seed.
- `run.py`: `run(scenario, detector_module, detector_class, kwargs)` builds
  DASRecords, feeds them through the detector in time order, reads
  `<field>_QC`, and scores: detection latency (first 3 or 4 after fault start),
  missed (no flag before fault end), false flags per hour outside faults and
  on traps, flags during traps. "Flag" threshold configurable (default 3).
- CLI `python -m contrib.deepsignal.bench run --scenarios <yaml> --detector <module:Class> --kwargs <json>`
  writes `results.json` and a short `summary.md` table (one row per scenario).
- Include `StubThresholdDetector` in `bench/stub.py` (flags value outside a
  range) so the bench is testable with no other module.

## Failing test first
`contrib/deepsignal/test/bench/test_faults.py` and `test_run.py`. RED first.
Cover each fault's exact numbers on a tiny series, same seed gives same
output, truth labels, trap labels, scoring on hand-built flag sequences
(latency, missed, false-flag rate, trap flags), the stub end to end, both
sample-data paths.

## Module contract
- Sample `contrib/deepsignal/bench/scenarios.yaml` with at least one scenario
  per fault and per trap on NBP1406 fields.
- Docs `contrib/deepsignal/docs/fault_bench.md`: purpose, "Run it in 5
  minutes", each fault and trap in one line, how to read the summary, what
  it does NOT prove (sample data is one cruise; injected faults are idealized).
- Depends on no other DeepSignal module.

## Acceptance (exact commands, from repo root)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/bench -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal
```
```
python3.12 -m contrib.deepsignal.bench run --scenarios contrib/deepsignal/bench/scenarios.yaml --detector contrib.deepsignal.bench.stub:StubThresholdDetector --kwargs '{}'
```

## Scope
Create or change only files under `contrib/deepsignal/` listed above. Output files go to a path given on the command line, default current dir. Do not commit.

## Trust boundaries and data integrity
Never modify the sample data files; work on copies in memory. Truth labels
come only from the injector, never from the detector.

## Non-goals and banned
No numpy (pure stdlib plus PyYAML). No plots. No core changes. No writes
outside `/private/tmp/deepsignal/fault-bench/` (rule 28). docs/CODEX.md rule 13 applies.

## Report format
Under 40 lines: files, test names, RED then GREEN tail, flake8, the stub's summary table, verified vs inferred.

## Stop rule
Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Linux check:
- What changed, in three lines:
- Open questions:
