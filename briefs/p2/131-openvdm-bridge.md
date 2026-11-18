# Brief: p2-openvdm-bridge (OpenVDM bridge: quality products and Data Dashboard plugin)

- Decision: IDEAS #131, from Eugene's 2026-11-18 asks (config assist, sensor init, ecosystem and compression); build per D-NIGHT1
- Risk tier: medium
- Module: exactly one. Branch `deepsignal/p2-openvdm-bridge` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 4/4/4
- Depends on: QARTOD flag fields; #135 manifests optional

## Goal
DeepSignal's quality results become part of the official cruise package and show on the OpenVDM Data
Dashboard techs and shore already use, with no change to OpenVDM itself: OpenVDM collects them like any
other collection system and its plugin turns them into pass, warning and fail tests.

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
- OceanDataTools sources were read at these commits (read-only; D-UPSTREAM0: nothing is sent to
  OceanDataTools): openvdm `5d163fc` (2.17.0, 2026-11-12), sealog-server `46ccbf0` (2.4.9). You have no
  network: the facts below are the interface. Do not guess beyond them; list anything you needed but
  lacked under open questions.
- OpenVDM collects files with Collection System Transfers (web UI form: name, source dir with wildcards,
  destination under `<cruiseID>/`, include, exclude and ignore globs, rsync copy). Its File Naming Guide
  page shows techs the names a transfer accepts.
- Data Dashboard plugins: a module `server/plugins/<transfer name lower>_plugin.py` (installed by copying a
  `.dist`), subclass of `server.lib.openvdm_plugin.OpenVDMPlugin` with `fileTypeFilters` entries
  `{"data_type", "regex" (fnmatch glob), "parser", "parser_options"}` and a `PARSER_MAP`. Parsers subclass
  `OpenVDMCSVParser` and report through `add_visualization_data({label, unit, data: [[ms_epoch, value]]})`,
  `add_quality_test_passed(name)`, `add_quality_test_warning(name)`, `add_quality_test_failed(name)`,
  `add_row_validity_stat`, `add_time_bounds_stat`, `add_bounds_stat(value, name, uom)`,
  `add_total_value_stat`. Output dict keys: `visualizerData`, `qualityTests` (`{testName, results}` with
  `Passed`, `Warning`, `Failed`), `stats`. OpenVDM ships `openrvdas_plugin.py.dist` for raw OpenRVDAS logs.

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/openvdm/`:
- `QualityDayWriter` (OpenRVDAS Writer): writes `<root>/<data_id>/<data_id>-quality-YYYY-MM-DD.csv`
  (UTC days): header `timestamp,field,value,flag,reason`, one row per `_QC` field per record. New file per
  day, append-only, never rewrites a closed day. These are the files the OpenVDM transfer collects.
- `dist/deepsignal_plugin.py.dist` and `dist/deepsignal_quality_parser.py.dist`: written for OpenVDM 2.17,
  stdlib only (no pandas). Per file: one quality test per field (`Failed` if any flag 4 share over
  `fail_share` default 0.01, `Warning` if any 3 or 9 over `warn_share` default 0.05, else `Passed`), row
  validity, time bounds, and a visualizer series of each field's flag share per hour.
- `docs`: the Collection System Transfer form values to type (name `DeepSignal`, source, destination
  `DeepSignal/`, include glob), and the copy commands for the two `.dist` files.
- Tests run the `.dist` code against `test/openvdm_stub.py`, a minimal stand-in exposing exactly the
  methods and output keys above, so the real OpenVDM is not needed.

## Failing test first
`contrib/deepsignal/test/openvdm/test_openvdm.py`: day file naming and rollover; append-only; parser test
results for all-pass, warning and fail fixtures; stats and time bounds; visualizer series shape; plugin
`fileTypeFilters` glob matches the writer's names and nothing else.

## Module contract
Docs `contrib/deepsignal/docs/openvdm.md`. A lead-run check inside a real OpenVDM 2.17 with
`openvdm_sample_data` happens outside the sandbox. Nothing is sent to OceanDataTools.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/openvdm -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/openvdm contrib/deepsignal/test/openvdm
```

## Scope
Create or change only: `contrib/deepsignal/openvdm/**`, `contrib/deepsignal/test/openvdm/**`, `contrib/deepsignal/docs/openvdm.md`, `contrib/deepsignal/configs/openvdm_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

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
