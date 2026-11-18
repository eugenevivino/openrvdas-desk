# Brief: p2-shore-snapshot (Low-bandwidth shore snapshot)

- Decision: D-PARITY1, IDEAS #123 (Eugene approved building #104-#124, 2026-11-18)
- Risk tier: low
- Module: exactly one. Branch `deepsignal/p2-shore-snapshot` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 2/3/5
- Depends on: none; #116 release policy goes in front of it for public use

## Goal
Shore staff on a slow link see a tiny, current picture of the ship (key values, age and quality) that
updates every minute and costs a few kilobytes.

## Background facts (do not re-derive)
- Base is the contrib `master` tree at `3b4b76e`: it carries a 2024 core tree (old Transform base class,
  no BaseModule). Copy the import-compatibility approach of
  `git show origin/deepsignal/vector-wind:contrib/deepsignal/logger/transforms/vector_wind_average_transform.py`
  so the module also works on current core. If that branch is unreadable, write plain absolute imports
  and say so.
- Create empty `__init__.py` files only where missing, byte-identical to the wind branch (empty), so
  parallel branches merge cleanly.
- OpenRVDAS loads classes from a config with `class:` plus `module:` (for example
  `module: contrib.deepsignal.<module>.<file>`). Records may arrive as a DASRecord, a dict with
  `timestamp` and `fields`, a list of either, or None; handle all, pass None through.
- File ownership is disjoint across phase 2 tasks: you own ONLY the paths under Scope.

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/shore_snapshot/`, class `ShoreSnapshotWriter` (an OpenRVDAS Writer).
- Config: `fields` (list, each `{name, label, units, decimals}`), `period_s` (default 60), `out_dir`,
  `ship`, `max_bytes` (default 4096).
- Keeps the latest value and time per field. Every `period_s` of record time writes, atomically (write to
  a temp file, then rename), `snapshot.json` and `snapshot.svg` into `out_dir`.
- JSON: `{"ship", "time", "fields": [{"n", "v", "u", "age_s", "q"}]}` with values rounded to
  `decimals`, `q` from `<field>_QC` if present, compact separators. Over `max_bytes`: drop trailing fields
  and add `"truncated": N`.
- SVG: a plain card, one line per field ("Air temp 21.4 degC, 12 s"), stale fields (age over 3x period)
  say "STALE" in words, dark background, no scripts, no external references, text escaped.
- Never sends anything itself; core network writers or rsync carry the files.

## Failing test first
`contrib/deepsignal/test/shore_snapshot/test_writer.py`: rounding; age; QC passthrough; stale wording;
byte cap truncation; atomic write (no partial file visible); SVG has no `<script>` and escapes `<` in a
label; period boundary uses record time.

## Module contract
Docs `contrib/deepsignal/docs/shore_snapshot.md` with a sample logger config and a sample of both files.
Depends on no other module.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/shore_snapshot -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/shore_snapshot contrib/deepsignal/test/shore_snapshot
```

## Scope
Create or change only: `contrib/deepsignal/shore_snapshot/**`, `contrib/deepsignal/test/shore_snapshot/**`, `contrib/deepsignal/docs/shore_snapshot.md`, `contrib/deepsignal/configs/shore_snapshot_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

## Usability (anything a tech sees or edits)
Answer each line of desk `docs/USABILITY.md` in the report, or N/A with a reason. Every config error is one
plain-English line naming the setting, what it saw, what it expected, and a good example.

## Trust boundaries and data integrity
Config and input files are hand-edited and untrusted: `yaml.safe_load` only, no `eval`. Never change or
drop an incoming value; only add fields or write new files. Missing or stale inputs are shown as such,
never guessed.

## Non-goals and banned
No core changes. No new dependency. No network. No refactors, renames or formatting outside Scope. No
loosened, skipped or deleted tests, no swallowed errors, no sleeps for test ordering.

## Stop rule
No code change needed: stop and report. Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Acceptance tails:
- Open questions:
