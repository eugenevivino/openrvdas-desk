# Brief: deepsignal-ship-coupling

- Decision: D-SIG1 (IDEAS #78; report T-SIG rank 1)
- Risk tier: high (statistics that produce QC-style flags; false discoveries mislead)
- Module: exactly one, ship-coupling discovery engine (offline atlas runner plus live transform). Branch `deepsignal/ship-coupling`
- Base: `OceanDataTools/openrvdas_contrib` `master` at 3b4b76e
- Mac scratch path: `/private/tmp/deepsignal/ship-coupling/` only (docs/CODEX.md rule 1b)
- Lane: `cloud` (Sol medium, fixed, so no `-m`; rules 8 and 27, D-TEAM7), fresh task, under 40 turns. Every formula is pinned below with test vectors, so Sol medium builds and does not design. Review: fresh `gpt-6.2-astra` xhigh on a Mac, read-only (statistics and flags).
- Depends on: `deepsignal/fault-bench` (#53) for evaluation only, through its CLI and plug-in injector. No import of any other DeepSignal module at runtime.
- Upstream home: openrvdas_contrib (Eugene sends the PR)

## Goal
Find, with honest statistics, which sensors are partly measuring the ship
itself (heading, speed, roll, pitch) instead of the ocean or air, and show
the watch a live "this reading is ship-contaminated right now, because..."
score without ever changing the data.

## Background facts (do not re-derive)
- Ship data are autocorrelated: per-second p-values are invalid. Use
  effective sample size and block resampling as specified below.
- contrib `master` carries a 2024 core tree; copy the import-compatibility
  approach of `git show origin/deepsignal/vector-wind:contrib/deepsignal/logger/transforms/vector_wind_average_transform.py`.
- Sample data: NBP1406 under `test/NBP1406/mwx1` (2024 tree) or
  `test/NBP1406/data/mwx1` (current core). It is short: good for tests and a
  smoke run, not for real discovery. Real runs use archived cruises (#63).
- Pure stdlib plus PyYAML. No numpy, scipy or statsmodels.
- Report citations (Benjamini-Hochberg 1995, Benjamini-Yekutieli 2001,
  surrogate-data testing) are leads; implement the formulas below, not a
  paper's variant.

## Design (lead decisions; flag disagreement in the report, do not silently change)
Package `contrib/deepsignal/coupling/`:

1. `stats.py` (pure functions, each with a test vector):
   - `pearson(x, y)`, `spearman(x, y)` (average ranks for ties).
   - `acf(x, k)` biased estimator. `decorrelation_lag(x)`: first lag where acf <= 1/e, capped at n/4.
   - `n_eff(x, y, max_lag)`: N / (1 + 2 * sum_{k=1..K} acf_x(k) * acf_y(k)), K = max_lag, floored at 2 (Bretherton-style).
   - `block_bootstrap_ci(x, y, stat, block, reps=1000, seed)`: moving-block bootstrap of paired blocks; 95% percentile interval. Default block = 2 * max(decorrelation_lag(x), decorrelation_lag(y)).
   - `circular_shift_pvalue(x, y, stat, reps=500, min_shift, seed)`: shift y circularly by random offsets of at least `min_shift` (default 2 * block), p = (1 + count(|stat_null| >= |stat_obs|)) / (reps + 1).
   - `bh(pvals, q)` and `by(pvals, q)` returning the rejected index set; BY uses q / sum_{i=1..m} 1/i.
   - `lagged_best(x, y, lags)`: stat at each lag in an allowed list; return best lag and value. When a best lag is chosen, the p-value is computed on the max-over-lags statistic in the surrogate null too (no lag-shopping bias).
2. `prep.py`: align streams to a common bin (default 10 s, mean within bin,
   missing bins left missing); compute ship variables from fields named in
   config: relative heading as sin and cos of (direction field minus ship
   heading), SOG, roll, pitch, heading rate, and RPM or thruster when present
   (tier V). Remove slow environment from each environmental field: subtract a
   centered rolling median (default 30 min) offline; the residual is what gets
   tested. Regime label per bin: `station` (SOG under 1 kn), `maneuver`
   (heading rate over 2 deg/s or SOG change over 1 kn/min), else `transit`.
   Every threshold is config with these defaults.
3. `atlas.py` (offline discovery):
   - Hypotheses = (environmental field, ship variable, regime). Families from
     config, defaults `met_vs_ship`, `ocean_vs_ship`, `acoustic_vs_ship`, `nav_consistency`.
   - Per hypothesis: effect = spearman at best allowed lag, n_eff, block
     bootstrap CI, circular-shift p. Hypotheses with n_eff under 30 get
     `insufficient` and no p-value.
   - FDR: BH within each family at `q` (default 0.05); `method: by` switches to BY.
   - Replication: config splits the input into `discovery` and `holdout`
     sets (by cruise or by named time ranges, never random bins). A coupling is
     `confirmed` only if it passes FDR in discovery AND in holdout with the same
     sign and best lag within one lag step. Else `discovery_only` or `rejected`.
   - Ship-coordinate invariance control, for each confirmed coupling with a
     heading-type ship variable: (a) reciprocal legs: pairs of transit
     segments within `reciprocal_km` (default 10 km) and `reciprocal_hours`
     (default 12 h) whose headings differ by 180 +/- 30 deg; if the field's
     residual difference between the legs follows relative heading (sign flips
     with ship coordinates) the verdict is `ship_artifact`; if it stays fixed in
     Earth coordinates, `environmental`; too few pairs, `cannot_tell`. (b) time
     shift: recompute the effect with the ship variable shifted by 12 h and
     24 h; a ship artifact must vanish under shift. Both results are recorded.
   - Turn events: heading change over 60 deg within 5 min at steady SOG;
     compare field residual median 5 min before vs after; feeds the polar table.
   - Contamination polar table per confirmed field: residual median and IQR by
     relative-heading sector (default 12 sectors of 30 deg) and speed band.
   - Outputs: `atlas.json` (every hypothesis with effect, CI, n_eff, p, q-pass,
     replication and invariance verdict, all parameters and code version),
     `atlas.md` (confirmed couplings first, plain English: "Air temperature
     reads 0.4 C high when the wind comes over the port quarter; replicated on
     2 of 2 holdout cruises; ship-fixed, so likely exhaust or deck heating"),
     and `polar_<field>.csv`.
   - CLI `python -m contrib.deepsignal.coupling atlas --config <yaml>`.
4. `transform.py`: `ShipCouplingTransform(atlas_path, fields, min_verdict='ship_artifact')`.
   Loads only confirmed `ship_artifact` couplings and their polar tables
   (frozen; never learns live). For each record keeps the latest ship state
   (bounded memory) and, for each listed field present, adds
   `<field>_SHIP` (0.0 to 1.0: the sector's |median residual| divided by the
   field's healthy residual spread, clipped) and `<field>_SHIP_why` (one
   plain sentence naming the ship variable, sector and atlas evidence), and a
   QARTOD-style `<field>_SHIP_QC`: 1 under 0.3, 3 from 0.3, 4 from 0.7 (config).
   No ship state yet: add `<field>_SHIP_QC` 2 and no score. Never change
   existing fields or the timestamp; never mutate the input.
5. `bench_injectors.py`: `heading_coupled_bias(series, ship_heading, amplitude, sector, seed)`
   with the bench injector signature, so #53 can score this module.

## Failing test first
`contrib/deepsignal/test/coupling/test_stats.py`, `test_atlas.py`,
`test_transform.py`. RED first. Required: each stats function against hand
computed vectors (include BH and BY on the Benjamini-Hochberg 1995 style
15-p-value example computed by hand in the test); n_eff falls as
autocorrelation rises; synthetic data where field = environment(t) +
0.5*cos(relative heading) + noise is `confirmed` and `ship_artifact`, while
field = environment(t) with a heading-aligned mission track is NOT a ship
artifact (Earth-fixed gradient sampled on reciprocal legs); pure noise over
50 hypotheses gives at most the FDR-expected count; best-lag selection does
not inflate false positives (null data, max-over-lags); transform adds fields,
leaves raw bytes identical, handles DASRecord, dict, list, None.

## Evaluation on the fault bench (#53)
After #53 is merged into the scratch base (operator merges its branch locally,
read-only use), run:
`python -m contrib.deepsignal.bench run --scenarios contrib/deepsignal/coupling/bench_scenarios.yaml --detector contrib.deepsignal.coupling.transform:ShipCouplingTransform --kwargs '{"atlas_path": "<synthetic atlas>"}' --flag-suffix _SHIP_QC`
Scenarios: heading-coupled bias (should flag), front trap and smooth-turn
trap (should not). Report the numbers; do not tune to them. If #53 is not yet
merged, ship the scenario file and say the run is pending.

## Module contract
- Sample config `contrib/deepsignal/configs/ship_coupling_atlas.yaml` (NBP1406
  fields, discovery and holdout split by time) and
  `contrib/deepsignal/configs/ship_coupling_logger.yaml` (live transform with
  a small checked-in sample atlas). Both run as is.
- Docs `contrib/deepsignal/docs/ship_coupling.md`: purpose in one sentence,
  "Run it in 5 minutes", how to read the atlas, what each verdict means, why
  replication and the invariance control exist, what it does NOT do (no
  correction, no deletion, no live learning, short sample data proves nothing).
- Depends on no other DeepSignal module at runtime.

## Acceptance (exact commands, from repo root)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/coupling -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal
```
```
python3.12 -m contrib.deepsignal.coupling atlas --config contrib/deepsignal/configs/ship_coupling_atlas.yaml
```

## Scope
Create or change only files under `contrib/deepsignal/coupling/`, its tests,
its two configs, its doc and needed empty `__init__.py` files. Do not commit.

## Trust boundaries and data integrity
Inputs are untrusted logs: skip unparseable lines with a counted warning.
Every output records its parameters, seeds and code version. Fixed seeds in
tests. Never write to input files.

## Non-goals and banned
No automatic correction, no live discovery, no plots, no numpy, no core
changes. No writes outside `/private/tmp/deepsignal/ship-coupling/` if run on
a Mac (rule 28). docs/CODEX.md rule 13 applies.

## Report format
Under 40 lines: files, test names, RED then GREEN tail, flake8, atlas smoke
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
