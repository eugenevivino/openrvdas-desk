You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-erddap` from commit `3b4b76e` (the contrib master tree; it is in this fork's history, for example `git merge-base origin/deepsignal/vector-wind origin/deepsignal/instrument-history`) (if `deepsignal/p2-erddap` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-erddap`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML is already an OpenRVDAS dependency; add no other dependency. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-erddap (ERDDAP dataset generator)

- Decision: D-PARITY1, IDEAS #104 (Eugene approved building #104-#124, 2026-11-18)
- Risk tier: low
- Module: exactly one. Branch `deepsignal/p2-erddap` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 2/5/5
- Depends on: none (reads #117 vocab files if present, optional)

## Goal
A tech runs one command and gets an ERDDAP `datasets.xml` fragment that serves the ship's data files, so
science and shore get subsets in every ERDDAP format without anyone hand-writing XML.

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
- ERDDAP is a separate open-source Java server. This module only writes its configuration text; it never
  runs or ships ERDDAP. ERDDAP's `EDDTableFromAsciiFiles` reads a directory of CSV files with a header row.

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/erddap/`:
- Input `erddap_datasets.yaml` (example in `contrib/deepsignal/configs/erddap_example.yaml`):
  ```yaml
  institution: Scripps Institution of Oceanography
  ship: {name: Roger Revelle, call_sign: KAOU}
  datasets:
    - id: revelle_met_1min          # ERDDAP datasetID: letters, digits, underscore
      title: R/V Revelle 1-minute meteorology
      directory: /data/openrvdas/binned/met
      file_regex: '.*\.csv'
      time_column: time            # ISO 8601 UTC strings
      reload_minutes: 10
      variables:
        - {column: air_temperature, units: degree_C, long_name: Air temperature,
           standard_name: air_temperature, ioos_category: Meteorology}
        - {column: air_temperature_flag, units: "1", long_name: Air temperature QARTOD flag,
           flag_of: air_temperature}
  ```
- `generate.py`: `generate(config) -> str` returns XML text for one `<dataset type="EDDTableFromAsciiFiles">`
  per dataset, with `fileDir`, `fileNameRegex`, `reloadEveryNMinutes`, global `addAttributes`
  (`cdm_data_type=Other`, `Conventions=COARDS, CF-1.10, ACDD-1.3`, `institution`, `title`,
  `summary`, `platform=ship`, `infoUrl`, `license` from config with default "See ship data policy"),
  and one `<dataVariable>` per column; the time column becomes `destinationName=time`,
  `units=yyyy-MM-dd'T'HH:mm:ssZ`. Flag variables get `flag_values="1 2 3 4 9"` and
  `flag_meanings="pass not_evaluated suspect fail missing"`.
- Build XML with `xml.etree.ElementTree` (no string concatenation of values), so every value is escaped.
- `check(config)` returns plain findings: bad datasetID, duplicate ids, missing units, a `flag_of` that
  names no column, a `standard_name` not in the optional CF list (warning only, and only if
  `contrib/deepsignal/vocab/` data from #117 exists; otherwise skip silently and say so in docs).
- CLI: `python -m contrib.deepsignal.erddap generate <yaml> > datasets_fragment.xml` and
  `python -m contrib.deepsignal.erddap check <yaml>` (exit 1 on any error).

## Failing test first
`contrib/deepsignal/test/erddap/test_generate.py`: golden XML for the example config (normalize whitespace
before comparing); XML parses; special characters in title are escaped; time column attributes; flag
attributes; each check finding; CLI exit codes.

## Module contract
Sample config, docs `contrib/deepsignal/docs/erddap.md` ("Turn it on in 5 minutes": where to paste the
fragment in ERDDAP's `datasets.xml`, how to test with ERDDAP's `DasDds` tool, what it does NOT do).
Depends on no other module. A lead-run check (outside the sandbox) loads the fragment in a real ERDDAP.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/erddap -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/erddap contrib/deepsignal/test/erddap
```
```
python3.12 -m contrib.deepsignal.erddap check contrib/deepsignal/configs/erddap_example.yaml
```

## Scope
Create or change only: `contrib/deepsignal/erddap/**`, `contrib/deepsignal/test/erddap/**`, `contrib/deepsignal/docs/erddap.md`, `contrib/deepsignal/configs/erddap_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

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
