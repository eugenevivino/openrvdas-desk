You are making ONE small, test-first change to OpenRVDAS core on Eugene's own fork (fork only, never upstream). Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-best-source` from commit `1a6f1ed` (fork `dev`) (if `deepsignal/p2-best-source` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-best-source`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: use `python3.12` if it exists, otherwise `python3` (3.11 or newer). Install the repository's Python requirements if pytest cannot import `logger`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. Add no dependency. Read CLAUDE.md and OPERATIONS.md first. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-best-source (Best-source selector with failover (core fix))

- Decision: D-PARITY1, IDEAS #106 (Eugene approved building #104-#124, 2026-11-18)
- Risk tier: medium
- Module: exactly one. Branch `deepsignal/p2-best-source` from `1a6f1ed`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: core, fork only (D-ARCH6)
- Value (techs/science/shore): 4/4/3
- Depends on: none; uses `<field>_QC` flags when #8 is present, works without them

## Goal
Downstream consumers read one "best" position, heading or wind, and the system fails over to the backup
sensor by itself when the primary goes quiet or bad, and says so.

## Design (lead decisions; flag disagreement in the report)
New core transform `logger/transforms/best_source_transform.py`, class `BestSourceTransform`
(subclass the current `Transform` with type hints, like neighbouring transforms on `dev`).
- Config:
  ```yaml
  class: BestSourceTransform
  kwargs:
    roles:
      latitude:  {sources: [s330Latitude, gp02Latitude], timeout: 10}
      longitude: {sources: [s330Longitude, gp02Longitude], timeout: 10}
    return_after: 30        # seconds the primary must be healthy before switching back
    bad_flags: [3, 4, 9]    # values of <source>_QC that count as unhealthy, if present
  ```
- Keeps the latest value and timestamp per source from every record it sees. A source is healthy at time
  t if its last value is at most `timeout` seconds old and its `<source>_QC` (if present in the same
  record) is not in `bad_flags`.
- On each record, for each role: chosen = first healthy source in list order, except that after a
  failover it stays on the backup until the primary has been continuously healthy for `return_after`
  seconds (hysteresis). No healthy source: emit nothing for that role and set `<role>_source` to `none`.
- Output: a DASRecord (or dict, matching input) with `<role>` = chosen value, `<role>_source` = source
  field name, `<role>_age` = seconds old. Original fields pass through untouched.
- Log one warning per switch: "latitude: switched from s330Latitude to gp02Latitude (s330Latitude 12.0 s
  old)". Uses record timestamps only.

## Failing test first
`test/logger/transforms/test_best_source_transform.py`: primary healthy; primary times out; QC flag bad;
hysteresis holds then returns; both dead gives `none`; order of sources matters; input as DASRecord, dict,
list and None; config errors (empty sources, negative timeout).

## Acceptance (exact commands, from repo root, Linux)
```
python3.12 -m pytest test/logger/transforms/test_best_source_transform.py -v
```
```
python3.12 -m flake8 --config .flake8 logger/transforms/best_source_transform.py test/logger/transforms/test_best_source_transform.py
```
```
python3.12 -m pytest test/logger -q
```

## Scope
New files only: `logger/transforms/best_source_transform.py`, its test, and a docs section appended to the
end of `docs/transforms.md` if that file exists on `dev` (else `docs/best_source_transform.md`). Do not edit
`logger/transforms/__init__.py` unless every other transform there is listed; follow what `dev` does.

## Trust boundaries and data integrity
Existing behavior and output bytes of every current config stay identical unless the new option is set.
Default values of existing classes do not change.

## Non-goals and banned
No upstream PR or issue (D-ARCH6, fork only). No refactors, renames or formatting outside the listed
files. No new dependency. No loosened, skipped or deleted tests, no swallowed errors, no sleeps for test
ordering.

## Stop rule
No code change needed: stop and report. Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Acceptance tails:
- Open questions:
