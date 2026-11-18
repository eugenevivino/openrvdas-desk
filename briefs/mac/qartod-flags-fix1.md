# Brief: qartod-flags fix round 1 (after the independent Astra xhigh review: BLOCK)

- Module: `QartodFlagTransform` only. Branch `deepsignal/qartod-flags`, base 47da03b (fix on top; do not rewrite history)
- Lane: `mac`. `-m gpt-6.2-sol` high via `~/bin/ds-codex`, fresh session, under 40 turns, 45 minute cap
- Mac scratch path: `/private/tmp/deepsignal/qartod-fix1/` (clone in `repo/`)
- Review that produced this brief: `/private/tmp/deepsignal/qartod-flags/review.md` (read it first; it has file:line for each item)
- Parent brief: desk `briefs/deepsignal-qartod-flags.md` (front_check version). Its design and data-integrity rules still hold.
- Risk tier: high (QC flags). Non-critical for merging under D-REVIEW1 unless the re-review says otherwise.

## Goal
Close every finding in the review so a fresh re-review can PASS. Raw values, timestamps and field order are never changed.

## Failing tests first
Add one regression test per finding (names `test_review_<n>_<short>`), run them and show RED on 47da03b, then fix:
1. Output-name collision (`{T: null, T_QC: 1}`, companion carrying `S_QC: 4`): detect collisions before updating history or
   emitting flags; never mark a missing reading good; the error names a free suffix.
2. `Decimal('NaN')` gives 9; finite `Decimal('1.5')` is numeric (no syntax failure); original values preserved.
3. Overflow: values `1` then `10**400` one second apart with `max_rate: 1` must not raise; gross range still reports.
4. Boundaries with roundoff: `30.0 -> 30.2` meets `min_change: 0.2`; `1.0 -> 1.1` in 1 s does not exceed `max_rate: 0.1`.
   Test both directions.
5. Even-window median overflow (`window: 2`, three `1e308`): overflow-safe midpoint, no `inf`.
6. Unusable timestamp (`100, None, 120`, `max_gap_seconds: 10`): clear the gap baseline; future-time check still runs.
7. Companion chains (A checks B, B checks C): resolve independently corroborated companions first; no circular confirmation.
8. Hard failure plus missing companion: hard failure first in the reason, then the companion explanation.
9. Config: unknown kwargs (`per_test_flag`) go through the validator with a plain-English message; setting names escaped
   (no raw newlines); the suffix example fixes the reported configuration.
10. Input immutability test: snapshot the full input (timestamp, values, key order) for dict and DASRecord, assert after.
11. Regressions for: flat-history eviction, rate companion window uses the right sample, companion movement cannot create a
    jump or soften flat-line, duplicate months refused, empty suffix refused, steady target with moving companion.
12. Docs: put the path choice before the command; show the message and corrected YAML for `max_rate: 0`.
13. Timestamp `-10**20`: surface the UTC conversion failure with a rate-limited diagnostic; timestamp preserved.

## Acceptance (exact commands, from repo root)
```
python3.12 -m unittest contrib.deepsignal.test.logger.transforms.test_qartod_flag_transform -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal
```

## Scope
Only `contrib/deepsignal/logger/transforms/qartod_flag_transform.py`, its test file and `contrib/deepsignal/docs/qartod_flags.md`.

## Non-goals and banned
No new features, no loosened or deleted tests, no bare except, no sleeps, no rewriting values. No sub-agents.

## Stop rule
If any finding cannot be fixed without changing the parent brief's design, stop and report that finding instead.
