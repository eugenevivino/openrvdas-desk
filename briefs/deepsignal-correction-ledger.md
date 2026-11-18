# Brief: deepsignal-correction-ledger

- Decision: D-SOII1 (IDEAS #56, pairs with #32; Eugene approved 2026-11-18)
- Risk tier: high (produces corrected data values)
- Module: exactly one, correction ledger plus apply transform. Branch `deepsignal/correction-ledger`
- Base: `OceanDataTools/openrvdas_contrib` `master` at 3b4b76e (fork branch already created at 3b4b76e)
- Mac scratch path: `/private/tmp/deepsignal/correction-ledger/` only (docs/CODEX.md rule 1b)
- Lane: `mac`. Model id for `-m` (rule 27) and effort: `gpt-6.2-sol`, high, fresh session, under 40 turns. Review: fresh `gpt-6.2-astra` xhigh, read-only (high-risk tier).
- Upstream home: openrvdas_contrib (Eugene sends the PR)

## Goal
Every fix to sensor data is a separate, signed, undoable record with its
evidence; the raw value is never touched, and anyone can see which corrected
value came from which approved fix.

## Background facts (do not re-derive)
- Copy the 2024/current import-compatibility approach from the wind branch
  (`git show origin/deepsignal/vector-wind:contrib/deepsignal/logger/transforms/vector_wind_average_transform.py`).
- Post-cruise review (#54) will write `proposed` entries in this format, so the format is a contract: document it.
- On the MacBook use `python3.12 -m unittest`.

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/corrections/`:
- Ledger: append-only JSON Lines file. Every line is an event; nothing is
  ever edited or deleted. Each line carries `prev_hash` and `hash`
  (sha256 of the canonical JSON of the line without `hash`), so any edit
  breaks the chain.
- Event `propose`: `id` (uuid4), `field`, optional `instrument` (id from the
  instrument history module, not imported), `start`, `end` (UTC ISO),
  `method` one of `offset` (`value`), `linear_drift` (`rate_per_day`,
  `t0`), `polynomial` (coefficients, lowest order first), `time_shift`
  (`seconds`, applies to the corrected field's timestamp only in a new field
  `<field>_corr_time`), `uncertainty` (same units as the field, required),
  `evidence` (list of free-text refs or file paths), `author`, `code_version`, `reason`.
- Events `approve`, `reject`, `rollback`: `id`, `by`, `reason`, `time`. Only
  a `proposed` entry can be approved or rejected; only `approved` can be rolled
  back. `by` must differ from the proposal's `author` (two people).
- `Ledger.load(path)` verifies the hash chain; a broken chain is an error
  naming the line. `Ledger.active(field, t)` returns the approved, not rolled
  back entries covering t.
- `CorrectionApplyTransform(ledger_path, fields)`: for each listed field in a
  record, if exactly one active entry covers the timestamp, add
  `<field>_corr` and `<field>_corr_id`; if none, add nothing; if more than
  one overlap, add nothing and log a warning once per pair (overlap is an
  error a human resolves). Re-reads the ledger when its mtime changes.
- CLI `python -m contrib.deepsignal.corrections {propose,approve,reject,rollback,list,verify}`
  with required `--by` or `--author`. `list` prints plain-English rows.

## D-REAN2 additions (drift report, 2026-11-18; lead decisions)
- New method `gain_offset` (`offset`, `gain`): corrected = (raw - offset) / gain.
- `propose` gains fields: `standard_uncertainty` (replaces `uncertainty`;
  accept the old name on load as an alias), optional `coverage_interval`
  ([low, high]), `correction_state` (must be `CORRECTABLE`, else reject the
  proposal with a plain message), `model_id` (C0 to C5), `fit_refs` and
  `validation_refs` (lists of ids), optional `independence_score` (0 to 1).
- Rule: `fit_refs` and `validation_refs` must not overlap. An overlap is
  rejected at `propose`, naming the shared ids. This is the ledger's guard
  against circular validation.
- `CorrectionApplyTransform` also adds `<field>_corr_u` (the standard
  uncertainty) next to `<field>_corr`.
- Tests add: overlapping refs rejected; non-CORRECTABLE state rejected;
  gain_offset applies correctly; `_corr_u` present.

## Failing test first
`contrib/deepsignal/test/corrections/test_ledger.py` and `test_apply.py`. RED first.
Cover: each method's math on known numbers, state machine (every legal and
illegal transition), same person cannot approve own proposal, tampered line
detected, rollback removes the effect, overlap gives no correction plus one
warning, raw fields and timestamp byte-identical and input not mutated,
DASRecord, dict, list and None inputs, ledger reload on change, CLI round trip.

## Module contract
- Sample config `contrib/deepsignal/configs/correction_apply_logger.yaml`
  reading NBP1406 sample data with a sample ledger holding one approved and
  one rolled-back entry. Runs as is with `listen --config_file`.
- Docs `contrib/deepsignal/docs/correction_ledger.md`: purpose, "Turn it on
  in 5 minutes", the ledger format as a contract, the approval rule, what it
  does NOT do (never overwrites raw, never auto-approves).
- Depends on no other DeepSignal module.

## Acceptance (exact commands, from repo root)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/corrections -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal
```

## Scope
Create or change only files under `contrib/deepsignal/` listed above. Do not commit.

## Trust boundaries and data integrity
Ledger is untrusted input: validate every line, fail loudly on a broken
chain, never repair it. Never change, round, drop or reorder any existing
field or the timestamp. Never mutate the input record.

## Non-goals and banned
No auto-approval, no GUI, no database, no core changes. No writes outside
`/private/tmp/deepsignal/correction-ledger/` (rule 28). docs/CODEX.md rule 13 applies.

## Report format
Under 40 lines: files, test names, RED then GREEN tail, flake8, design points you disagree with, verified vs inferred.

## Stop rule
Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Linux check:
- What changed, in three lines:
- Open questions:
