# Brief: p2-config-provenance (Config provenance: versioned history with semantic diffs)

- Decision: IDEAS #163, from Eugene's 2026-11-18 asks (config assist, sensor init, ecosystem and compression); build per D-NIGHT1
- Risk tier: medium
- Module: exactly one. Branch `deepsignal/p2-config-provenance` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 5/3/4
- Depends on: #126 generator and #127 lint outputs are inputs; #154 apply records reference these versions

## Goal
Every change to the cruise definition, device definitions and DeepSignal settings is kept as a version.
The diff is in ship words: "GPS source changed from /dev/ttyS1 to UDP 6224", "baud 4800 to 9600",
"calibration coefficient changed", "units changed", "stream renamed", "parser changed". A note is required
for high-risk changes. Evidence: desk `docs/PAIN-POINTS.md` (Deep Research, 2026-11-18); mapping in `docs/PAIN-POINTS-MAP.md`. (pain point 2; opportunity "Configuration provenance and drift detection").

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
Package `contrib/deepsignal/config_provenance/`:
- Store: a plain directory (default `/var/lib/deepsignal/config-history/`, set by option). It holds
  content-addressed snapshots `sha256.yaml` and an append-only `history.jsonl` with time, who, note, files,
  hashes and parent. No git dependency; a git export is optional docs-only.
- `snapshot(paths, who, note) -> version`. It refuses a high-risk change with no note. High risk means a
  change to reader ports or hosts, baud, parser device type, calibration or units fields, writer paths,
  the removal of a logger, or EEZ and release policy files.
- `semantic_diff(old, new) -> list` of `{kind, logger, what, from, to, risk}`:
  - Kinds: `source_changed`, `serial_setting`, `parser_changed`, `transform_added`, `transform_removed`,
    `writer_changed`, `logger_added`, `logger_removed`, `renamed` (same reader, new name), `mode_changed`,
    `calibration_changed`, `units_changed`.
  - Plus a raw unified diff fallback.
- `drift(baseline, current)`: compares the running cruise with a vessel baseline and reports only the
  semantic differences.
- `watch`: polls the cruise file and the device definitions every 30 s, records a version on change
  (who = "unknown, detected"), and emits a timeline record.
- CLI: `snapshot`, `log`, `diff A B`, `drift --baseline B`. Setup engine: `semantic_diff` is pure and
  JSON-safe.

## Failing test first
`contrib/deepsignal/test/config_provenance/test_provenance.py`:
- Each diff kind on NBP1406-derived fixtures.
- A rename is detected as a rename.
- A note is required for high risk.
- History is append-only.
- Content addressing dedupes.
- Watch records an external edit.
- Drift ignores comment and order changes.

## Module contract
Docs `contrib/deepsignal/docs/config_provenance.md`.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/config_provenance -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/config_provenance contrib/deepsignal/test/config_provenance
```

## Scope
Create or change only: `contrib/deepsignal/config_provenance/**`, `contrib/deepsignal/test/config_provenance/**`, `contrib/deepsignal/docs/config_provenance.md`, `contrib/deepsignal/configs/config_provenance_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

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
