# Brief: deepsignal-qartod-flags

- Decision: D-AI1 (foundation for alarms, drift checks and AI work), D-ARCH3 (contrib home)
- Risk tier: high (QC flags and data values, OPERATING-SYSTEM section 6)
- Module: exactly one, `QartodFlagTransform`. Branch `deepsignal/qartod-flags`
- Base: `OceanDataTools/openrvdas_contrib` `master` at 3b4b76e (already pushed as fork branch `deepsignal/qartod-flags`)
- Mac scratch path: `/private/tmp/deepsignal/qartod-flags/` only (docs/CODEX.md rule 1b)
- Model and effort: Codex Astra 6.2 high (Eugene 2026-11-18: Astra 6.2 and Sol 6.2 replace earlier picks), fresh session, under 40 turns. Math-heavy QC design, approved by Eugene 2026-11-18. Review: separate fresh Astra xhigh, read-only.
- Upstream home: openrvdas_contrib (Eugene sends the PR)

## Goal
Each configured sensor value gets a standard quality flag (1 good, 3 suspect,
4 bad, 9 missing, 2 not checked) written as a new field next to it, so techs,
alarms and later AI modules can see bad data without the raw value ever being
changed or removed.

## Background facts (do not re-derive)
- IOOS QARTOD flag scheme: 1 pass, 2 not evaluated, 3 suspect, 4 fail, 9 missing.
- Core `ValueFilterTransform` deletes out-of-range values. Do NOT use or copy it.
- contrib `master` carries a 2024 core tree: old Transform base class, no
  `BaseModule`, sample data at `test/NBP1406/mwx1` (current core uses
  `test/NBP1406/data/mwx1`). The module must import and work on BOTH. The
  already-built wind module solved this; read it with
  `git show origin/deepsignal/vector-wind:contrib/deepsignal/logger/transforms/vector_wind_average_transform.py`
  and copy its compatibility approach, not its math.
- On the MacBook pytest is not installed; run tests with `python3.12 -m unittest`.

## Design (lead decisions; flag anything you think is wrong in the report, do not silently change it)
Class `QartodFlagTransform` in
`contrib/deepsignal/logger/transforms/qartod_flag_transform.py`, module path
`contrib.deepsignal.logger.transforms.qartod_flag_transform`.

kwargs:
- `fields` (required): map of field name to a dict of tests. Example:
  `{SeaTemp: {gross_range: {fail_span: [-2, 40], suspect_span: [0, 32]}, spike: {suspect: 0.5, fail: 2.0}}}`.
- `flag_suffix` (default `_QC`): aggregate flag field is `<field><suffix>`.
- `per_test_flags` (default false): when true also add `<field><suffix>_<test>`.

Input: DASRecord, a dict with `timestamp` and `fields`, a list of either, or
None. Return the same type. Raw strings: return unchanged, log one warning the
first time (not per record) saying to put a parse transform before it.
None returns None.

Data integrity (rule 9, hard requirements, each locked by a test):
- Never change, round, drop or reorder any existing field or the timestamp.
- Never mutate the input record; return a new record with flags added.
- A configured field absent from a record: add no flag (it is another
  instrument's record). Present but None, NaN or empty: flag 9.
- Non-numeric value (string, bool) where a number is expected: flag 4 (QARTOD syntax test).

Tests, each on by listing it under a field, each giving 1, 3, 4 or 2:
1. `gross_range`: `fail_span` [min, max] required, `suspect_span` optional. Outside fail span 4, outside suspect span 3, else 1.
2. `climatology`: either `suspect_span` [min, max] or `months`: list of `{months: [1..12], suspect_span: [min, max]}`, month from the record timestamp in UTC. Outside 3, no span for that month 2.
3. `spike` (real-time, no-delay variant): compare value to the median of the last `window` good values (default 3). Deviation over `suspect` gives 3, over `fail` gives 4. Fewer than `window` prior good values gives 2. Document plainly that this differs from the centered QARTOD form because a logger cannot wait for the next sample.
4. `rate_of_change`: abs(value minus previous good value) / seconds between them over `max_rate` (units per second) gives 3. Non-positive time step gives 2 for this test.
5. `flat_line`: value has stayed within `tolerance` of the current value for at least `suspect_seconds` gives 3, `fail_seconds` gives 4.
6. `timing`: record timestamp not later than the previous one gives 4; more than `max_future_seconds` (default 60) ahead of wall clock gives 4; gap since previous record over `max_gap_seconds` gives 3. Applies to every configured field present in the record.

"Cannot tell" verdict, formal name AMBIGUOUS (IDEAS #55, Eugene approved
2026-11-18; vocabulary from research/2026-11-18-reanalysis-program.md 10.1,
where AMBIGUOUS maps to QARTOD flag 3). A big jump can be a sensor fault or a
real ocean front; a single stream cannot always tell.
- Module constant `VERDICT_AMBIGUOUS = 'AMBIGUOUS'` (a shared verdict module
  will own it later).
- Optional per field: `front_check: {companions: [FieldA, ...], min_change: {FieldA: 0.2}}`.
  Companions are other fields in the same record that should also move at a
  real front (salinity for temperature, a second thermosalinograph).
- When `spike` or `rate_of_change` would give 4 or 3 and at least one companion
  changed by at least its `min_change` since its previous good value, the test
  gives 3 (never 4) and the transform adds `<field><suffix>_reason` =
  `AMBIGUOUS: jump matches a change in <FieldA>; may be a real front, check before trusting or discarding`.
- When no companion moved, the original 4 or 3 stands and the reason field
  names the test that failed (for example `FAIL: spike 2.4 over limit 2.0`).
- When `front_check` is not configured, behavior is unchanged and no reason
  field is written unless the aggregate is 3 or 4 (then the reason names the test).
- Companion missing or bad in that record: no AMBIGUOUS; say so in the reason.
- gross_range, syntax and timing are never softened by front_check.
- Tests: front with companion moving gives 3 plus AMBIGUOUS, same jump with
  companion flat gives 4, companion missing, config error for an unknown
  companion name, reason field text for each case.
- Docs: a short "Sensor fault or real front?" section in plain words.

History for spike, rate_of_change and flat_line uses only values that were
numeric and not flagged 4 by gross_range or syntax. History is bounded
(count or time), kept per field, and reset on restart (say so in the docs).

Aggregate flag: 9 if missing; else 4 if any test 4; else 3 if any 3; else 2
if every test 2; else 1.

Config check at construction (usability rule 5): unknown test name, missing
required key, min not below max, negative or zero thresholds, bad months. The
error names the field and setting, what it saw, what it expected, and a good
example. Plain English, one line.

## Failing test first
`contrib/deepsignal/test/logger/transforms/test_qartod_flag_transform.py`.
Write it first and paste the RED output (import error is acceptable RED).
At minimum: each test's 1/3/4/2 cases, aggregate rule, flag 9 for None and
NaN, absent field adds nothing, raw values and timestamp byte-identical and
input not mutated, non-numeric gives 4, history skips bad values, DASRecord,
dict and list inputs, None passthrough, raw string passthrough with one
warning, each config error message, per_test_flags on and off.

## Module contract
- Sample config `contrib/deepsignal/configs/qartod_flags_logger.yaml`: reads
  NBP1406 sample data shipped in the tree, parses it, flags at least two
  fields, writes to stdout. Must run as is with `listen --config_file` (or
  `python logger/listener/listen.py --config_file`) on contrib master.
- Docs: `contrib/deepsignal/docs/qartod_flags.md` (NOT the shared README, to
  avoid a merge clash with the wind branch). Sections: what it does in one
  sentence, "Turn it on in 5 minutes" (three steps, how to see it working,
  how to turn it off), flag meanings table, every setting with its default,
  how to pick thresholds, what it does NOT do (no stale alarm during silence:
  a transform only runs when data arrives; no centered spike; no data
  removal; state lost on restart).
- Also create empty `__init__.py` files needed for imports
  (`contrib/deepsignal/`, `logger/`, `logger/transforms/`, `test/...`),
  identical to the wind branch (empty) so the branches merge cleanly.
- Depends on no other DeepSignal module.

## Integration and platform
Implements the OpenRVDAS Transform interface. Pure Python standard library;
no numpy, no ioos_qc, no new dependency. Must pass on Linux Python 3.12.

## Acceptance (exact commands, from repo root)
```
python3.12 -m unittest contrib.deepsignal.test.logger.transforms.test_qartod_flag_transform -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal
```
(If flake8 is not installed on the Mac, say so; the lead runs it on Linux.)

## Scope
May create or change only files under `contrib/deepsignal/` listed above.
Everything else is read-only. Do not commit (sandbox blocks .git); the
operator commits.

## Non-goals and banned
No changes to core, no refactors, no edits outside scope, no loosened or
skipped tests, no bare except, no sleeps, no rewriting values (docs/CODEX.md rule 13).
No stale-data watchdog (separate future module).

## Report format
Under 40 lines: files changed, test names, RED then GREEN output tail,
flake8 result, design points you disagree with, verified vs inferred.

## Stop rule
Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Linux check:
- What changed, in three lines:
- Open questions:
