# Brief: p2-archive-readiness (Continuous archive-readiness manifest)

- Decision: IDEAS #166, from Eugene's 2026-11-18 asks (config assist, sensor init, ecosystem and compression); build per D-NIGHT1
- Risk tier: low
- Module: exactly one. Branch `deepsignal/p2-archive-readiness` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 3/4/5
- Depends on: #135 manifests and #131 OpenVDM paths optional; #120 or #132 cruise metadata for dates

## Goal
At any hour of the cruise, a data manager can see whether the package would pass R2R: which datasets are
expected and present, the coverage and gaps, checksums, metadata completeness and transfer status.
Nothing is found missing at the end. Evidence: desk `docs/PAIN-POINTS.md` (Deep Research, 2026-11-18); mapping in `docs/PAIN-POINTS-MAP.md`. (pain point 5; opportunity "Continuous archive-readiness").

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
Package `contrib/deepsignal/archive_ready/`:
- `expected.yaml`: per dataset, a glob, expected cadence, a time field or file-name date pattern, and
  `required: true|false`. `generate_expected(cruise_dict)` proposes one from the cruise definition's
  `LogfileWriter` paths.
- `scan(root, expected, cruise_meta) -> manifest dict` and `manifest.jsonl` (append-only, one line per
  file). The manifest records:
  - path, size, sha256 (computed once per closed file, cached by mtime and size), first and last
    timestamp, record count, gaps over 3 cadences
  - config version (from #163 if present) and parser
  - whether the file was transferred (from an OpenVDM transfer log path if given, else unknown)
- Readiness checks, each with an explanation:
  - a required dataset is absent
  - coverage under 95 percent of the cruise so far
  - files outside the cruise dates
  - inconsistent file naming within a dataset
  - a cruise id or ports missing in the metadata
  - a checksum changed on a closed file (an error: closed files must not change)
- `report` CLI: a summary table, and JSON for the console.

## Failing test first
`contrib/deepsignal/test/archive_ready/test_archive_ready.py`:
- Expected generated from NBP1406.
- Coverage and gap math on synthetic files.
- A closed file whose checksum changes is detected.
- Out-of-dates files.
- Naming inconsistency.
- The cache avoids rehashing.
- Append-only manifest.

## Module contract
Docs `contrib/deepsignal/docs/archive_ready.md` with an example report.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/archive_ready -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/archive_ready contrib/deepsignal/test/archive_ready
```

## Scope
Create or change only: `contrib/deepsignal/archive_ready/**`, `contrib/deepsignal/test/archive_ready/**`, `contrib/deepsignal/docs/archive_ready.md`, `contrib/deepsignal/configs/archive_ready_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

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
