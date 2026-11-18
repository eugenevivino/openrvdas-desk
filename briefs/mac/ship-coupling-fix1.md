# Brief: ship-coupling (#78) fix round 1 (after the independent Astra ultra review: HOLD)

- Module: ship-coupling discovery engine only. Branch `deepsignal/ship-coupling`, base 67440a40 (fix on top)
- Lane: `mac`. `-m gpt-6.2-astra` high via `~/bin/ds-codex` with `KALON_ALLOW_ASTRA=1` (statistics; Eugene rule: math is
  Astra on a Mac), fresh session, under 40 turns, 45 minute cap
- Mac scratch path: `/private/tmp/deepsignal/ship-coupling-fix1/` (clone in `repo/`)
- Review that produced this brief: `/private/tmp/deepsignal/ship-coupling-review/answer.md`. Read it first; fix every
  P1 and P2 finding with file:line. Parent brief: desk `briefs/deepsignal-ship-coupling.md`; its pinned formulas hold.
- Risk tier: high (statistics that produce QC-style flags).

## Failing tests first
One regression test per finding (`test_review_<n>_<short>`), shown RED on 67440a40, then fixed. Each test must fail if
the specific formula or rule it guards is changed (test vectors from the parent brief where it gives them).

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
Only files under `contrib/deepsignal/coupling/`, `contrib/deepsignal/test/coupling/`, `contrib/deepsignal/configs/ship_coupling_*`
and `contrib/deepsignal/docs/ship_coupling.md`.

## Non-goals and banned
No new features, no loosened or deleted tests, no bare except, no sleeps, no value rewriting, no sub-agents.

## Stop rule
If a finding needs a change to a pinned formula in the parent brief, stop and report it instead of changing the design.
