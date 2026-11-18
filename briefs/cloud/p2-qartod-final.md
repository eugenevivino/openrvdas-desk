# Brief: qartod-flags final round (one unit, D-UNITS1; Eugene chose one more round at 15:09Z)

- Branch `deepsignal/qartod-flags` at 1660680 (the checked-out branch). One job closes both blocking findings below. Cloud, Sol medium.
- The parent brief is desk `briefs/deepsignal-qartod-flags.md`; its rules hold. The cloud cannot see the desk, so this brief is the whole spec.
- Module: the QARTOD flag transform `contrib/deepsignal/logger/transforms/qartod_flag_transform.py` and its test module `contrib/deepsignal/test/logger/transforms/test_qartod_flag_transform.py`; docs `contrib/deepsignal/docs/qartod_flags.md`.

## Fix exactly these (each with a regression test written first that fails at 1660680, then green)
1. Dropped history, false pass (blocking, stock CSV). With gross range `[0,20]`, tolerance `1`, and both flat-line durations `1` second, rows `100,10` then `100,99` then `101,10` give the last reading overall flag 1. The rejected `99` clears valid flat-line history because it repeats a timestamp. Commit c243788 gave 4 for the same sequence. Fix: update the flat-line timestamp and its queues only for history-eligible readings (readings that pass the gross-range check and have a usable timestamp). Test: that exact sequence gives overall flag 4 on the last reading, and a variant where the repeated-timestamp row is valid keeps today's behavior.
2. Dropped record (blocking, stock parse path). With `record_format='{field_string}'` and field pattern `{T:of},{S:of}`, `ParseTransform` turns `10,30` into `{'fields': {'T': 10.0, 'S': 30.0}}` with no `timestamp` key. QARTOD raises `KeyError('timestamp')` and the record is lost. Fix: read the timestamp with `record.get('timestamp')` (and the equivalent for DASRecord), treat a missing timestamp exactly like the existing None timestamp path (time checks give flag 2, NOT_EVALUATED; record passes through, never dropped), and keep the key absent in the output. Test: run that exact ParseTransform output through the transform; the record survives, fields and values unchanged, the timestamp key stays absent, and time-dependent checks give 2.

## Not in this round (they become tickets; do not change them)
- Reciprocal companions citing each other in AMBIGUOUS reasons.
- The huge `spike.window` diagnostic wording.

## Acceptance (exact commands, from repo root)
```
python3.12 -m unittest contrib.deepsignal.test.logger.transforms.test_qartod_flag_transform -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal
```

## Scope
Only the three files named above. Everything else is read-only.

## Non-goals and banned
No new features, no refactors, no deleted, skipped or loosened tests (all 48 existing tests keep passing), no bare except, no sleeps, stdlib only, no sub-agents.

## Stop rule
Report any finding that needs a change to the parent brief's design instead of changing it.
