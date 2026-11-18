# Brief: deepsignal-dependency-graph

- Decision: D-SIG1 (IDEAS #79; report T-SIG rank 3)
- Risk tier: high (QC flags on live data)
- Module: exactly one, dependency-graph fault detector (offline learner and replay runner plus live transform). Branch `deepsignal/dependency-graph`
- Base: `OceanDataTools/openrvdas_contrib` `master` at 3b4b76e
- Mac scratch path: `/private/tmp/deepsignal/dependency-graph/` only (docs/CODEX.md rule 1b)
- Lane: `cloud` (Sol medium, fixed, so no `-m`; rules 8 and 27, D-TEAM7), fresh task, under 40 turns. Formulas pinned below. Review: fresh `gpt-6.2-astra` xhigh on a Mac, read-only (QC flags).
- Depends on: `deepsignal/fault-bench` (#53) for evaluation only, through its CLI. No runtime import of any other DeepSignal module.
- Upstream home: openrvdas_contrib (Eugene sends the PR)

## Goal
Catch a sensor that has gone wrong while its numbers still look plausible,
by noticing that it no longer agrees with the other sensors it normally
tracks, and tell the watch which sensor is most likely at fault and why.

## Background facts (do not re-derive)
- contrib `master` carries a 2024 core tree; copy the import-compatibility
  approach of `git show origin/deepsignal/vector-wind:contrib/deepsignal/logger/transforms/vector_wind_average_transform.py`.
- Sample data: NBP1406 at `test/NBP1406/mwx1` (2024 tree) or `test/NBP1406/data/mwx1`.
- QARTOD flag meanings: 1 good, 2 not evaluated, 3 suspect, 4 bad, 9 missing.
  QARTOD flatline and range tests live in another module; do not duplicate them.
- Pure stdlib plus PyYAML. No numpy.

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/depgraph/`:

1. Regimes (same defaults as the ship-coupling module, implemented here,
   config-driven): `station` SOG under 1 kn, `maneuver` heading rate over
   2 deg/s or SOG change over 1 kn/min, else `transit`. One graph per regime.
2. Edges. Two kinds, both in one graph file:
   - `declared` edges from config, for known physics, each `y = a + b * x(t - lag)`
     with given or learned a, b, lag (examples in the sample config: TSG
     temperature vs hull SST with intake lag; port vs starboard true wind
     speed; GNSS SOG vs speed-log STW in low-current transit).
   - `learned` edges: for candidate pairs listed in config (never all pairs by
     default), on healthy training data binned to 10 s: split into blocks of
     30 min; per block fit ordinary least squares y on x at each allowed lag;
     pick the lag with best median |r| across blocks; keep the edge if |r| >= 0.6
     in at least 80% of blocks with the same sign of b. Store a, b, lag,
     residual standard deviation `s` (median absolute deviation * 1.4826 of
     training residuals), and the fraction of passing blocks.
   - Healthy data: config time ranges, or every bin where all fields' `_QC`
     flags (if present) are 1.
3. Graph file `graph.json`: nodes, edges per regime with parameters, training
   ranges, counts, code version. CLI `python -m contrib.deepsignal.depgraph learn --config <yaml>`.
4. Live `DependencyGraphTransform(graph_path, fields=None, k=0.5, h=5.0, align_tolerance_s=5)`:
   - Keep the latest value per node with its timestamp and a bounded history
     long enough for the longest lag (by time).
   - On each record, for each edge whose y is in the record and whose
     lagged x is available within tolerance: z = (y - (a + b * x)) / s.
   - Two-sided CUSUM per edge: S+ = max(0, S+ + z - k), S- = max(0, S- - z - k).
     Edge `broken` when S+ or S- exceeds h; recovers when both return to 0 and
     stay there for `recover_bins` (default 6). Reset CUSUMs on regime change.
   - Attribution per node: broken_fraction = broken edges / evaluated edges.
     A node is `suspect` if it has any broken edge. It is `blamed` if
     broken_fraction >= 0.5 AND every neighbor on its broken edges has
     broken_fraction < 0.5 (the neighbors still agree with the rest of the
     ship). A node whose only edges are with one other node can never be
     blamed alone: verdict `cannot_tell` (which of the two is wrong).
   - Outputs per configured field present in the record: `<field>_DG` flag
     (1 no broken edges, 3 suspect or cannot_tell, 4 blamed, 2 no evaluable
     edge), `<field>_DG_why` one plain sentence, e.g. "Speed log disagrees
     with GNSS speed by 0.48 kn for 11 min; GNSS agrees with ADCP; likely the
     speed log". Never change existing fields or the timestamp; never mutate input.
   - A flag only rises after `persist_bins` (default 3) consecutive broken
     bins, so one bad sample is not an alert (report's alert rule:
     score plus persistence plus explanation).
5. Replay CLI `python -m contrib.deepsignal.depgraph run --graph graph.json --logs <files> --out events.csv`:
   writes one row per edge break and recovery and per blame, with times and z.

## Failing test first
`contrib/deepsignal/test/depgraph/test_learn.py`, `test_transform.py`,
`test_attribution.py`. RED first. Required: OLS and MAD on hand vectors; lag
recovery on synthetic y = 2x(t-3 bins) + noise; edge rejected when sign flips
between blocks; CUSUM fires at the hand-computed bin for a known step and not
on noise; attribution on a 3-node triangle (blame the odd one), a 2-node pair
(`cannot_tell`), and a star (hub broken vs leaf broken); persistence gate;
regime switch resets CUSUM; raw bytes identical and input not mutated;
DASRecord, dict, list, None inputs; missing partner gives flag 2.

## Evaluation on the fault bench (#53)
After #53 is merged into the scratch base (read-only use), learn a graph on
the clean sample, then run
`python -m contrib.deepsignal.bench run --scenarios contrib/deepsignal/depgraph/bench_scenarios.yaml --detector contrib.deepsignal.depgraph.transform:DependencyGraphTransform --kwargs '{"graph_path": "<learned graph>"}' --flag-suffix _DG`
with bias, freeze (flatline), lag and dropout faults plus the front and turn
traps. Report detection delay and false alarms per ship-day; do not tune to
them. If #53 is not yet merged, ship the scenario file and say the run is pending.

## Module contract
- Sample configs `contrib/deepsignal/configs/depgraph_learn.yaml` and
  `contrib/deepsignal/configs/depgraph_logger.yaml` (with a small checked-in
  sample graph). Both run as is.
- Docs `contrib/deepsignal/docs/dependency_graph.md`: purpose in one sentence,
  "Turn it on in 5 minutes", how to choose candidate pairs, how to read
  `_DG_why`, what `cannot_tell` means, what it does NOT do (no correction, no
  live retraining, no range or flatline tests).
- Depends on no other DeepSignal module at runtime.

## Acceptance (exact commands, from repo root)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/depgraph -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal
```
```
python3.12 -m contrib.deepsignal.depgraph learn --config contrib/deepsignal/configs/depgraph_learn.yaml
```

## Scope
Create or change only files under `contrib/deepsignal/depgraph/`, its tests,
its two configs, its doc and needed empty `__init__.py` files. Do not commit.

## Trust boundaries and data integrity
Graph and log files are untrusted: validate on load, plain-English error
naming the edge or line. Bounded memory in the transform. Never write to inputs.

## Non-goals and banned
No automatic correction, no live learning, no all-pairs default, no numpy, no
core changes. No writes outside `/private/tmp/deepsignal/dependency-graph/` if
run on a Mac (rule 28). docs/CODEX.md rule 13 applies.

## Report format
Under 40 lines: files, test names, RED then GREEN tail, flake8, learn smoke
run summary, bench numbers or "pending", design points you disagree with,
verified vs inferred.

## Stop rule
Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Linux check:
- What changed, in three lines:
- Open questions:
