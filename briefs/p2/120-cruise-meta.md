# Brief: p2-cruise-meta (Cruise metadata)

- Decision: D-PARITY1, IDEAS #120 (Eugene approved building #104-#124, 2026-11-18)
- Risk tier: low
- Module: exactly one. Branch `deepsignal/p2-cruise-meta` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 2/3/4
- Depends on: none; uses #117 vocab files for port codes if present (optional)
- Needs Eugene: UNOLS schedule, MFP and MOMS import is left out: we found no public API. If Eugene has access or an export format, that becomes a follow-up.

## Goal
Every cruise has one small, checked metadata file (id, ship, dates, ports, people) that the console,
archive package and downloads all read, instead of the cruise id being typed in five places.

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
Package `contrib/deepsignal/cruise_meta/`:
- `cruise.yaml` (example `contrib/deepsignal/configs/cruise_meta_example.yaml`):
  ```yaml
  cruise_id: RR2205
  ship: {name: Roger Revelle, ices_code: null, call_sign: KAOU}
  start: 2022-04-01T00:00Z
  end: 2022-05-10T00:00Z
  departure_port: {name: San Diego, unlocode: USSAN}
  arrival_port: {name: Honolulu, unlocode: null}
  chief_scientist: {name: Example Person}
  participants: []          # names only if they agreed; never emails here
  data_policy: release_policy.yaml   # optional path, #116
  ```
- `load()` and `check()`: end after start; cruise id is letters, digits, dash or underscore; UN/LOCODE is 5
  characters (2 letters plus 3 letters or digits) when given; if #117 vocab files exist, unknown codes are
  warnings; personal emails or phone numbers anywhere in the file are an error ("contact details do not
  belong in cruise metadata").
- `CruiseMetaReader` (OpenRVDAS Reader): every `interval` (default 60 s) emits a record with
  `cruise_id`, `cruise_day` (days since start, 1-based, from the record time), `cruise_active` (bool).
- CLI `python -m contrib.deepsignal.cruise_meta check <file>` and `show <file>`.

## Failing test first
`contrib/deepsignal/test/cruise_meta/test_cruise_meta.py`: valid example; end before start; bad id;
LOCODE shape; email detected; cruise day at start, mid and after end; reader interval with a fake clock.

## Module contract
Docs `contrib/deepsignal/docs/cruise_meta.md`. Depends on no other module.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/cruise_meta -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/cruise_meta contrib/deepsignal/test/cruise_meta
```

## Scope
Create or change only: `contrib/deepsignal/cruise_meta/**`, `contrib/deepsignal/test/cruise_meta/**`, `contrib/deepsignal/docs/cruise_meta.md`, `contrib/deepsignal/configs/cruise_meta_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

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
