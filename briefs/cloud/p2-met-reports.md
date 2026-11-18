You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-met-reports` from commit `3b4b76e` (the contrib master tree; it is in this fork's history, for example `git merge-base origin/deepsignal/vector-wind origin/deepsignal/instrument-history`) (if `deepsignal/p2-met-reports` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-met-reports`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML is already an OpenRVDAS dependency; add no other dependency. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-met-reports (SAMOS daily file and met report writers)

- Decision: D-PARITY1, IDEAS #111 (Eugene approved building #104-#124, 2026-11-18)
- Risk tier: medium
- Module: exactly one. Branch `deepsignal/p2-met-reports` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 3/4/4
- Depends on: none; feeds from 1-minute averages (vector wind #4 for wind)
- Needs Eugene: Byte-exact formats need real samples: one SAMOS daily file the ship sent, and one each of any NOAA, OPSUM, SHIPTRACK or PCO2 message the ship really sends. Until Eugene drops them in, templates ship marked UNVERIFIED and only structure is tested.

## Goal
The ship produces the daily SAMOS file and the routine met messages from OpenRVDAS data, so MetAcq is not
needed for them and every file is checked against a real sample before it is trusted.

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
Package `contrib/deepsignal/met_reports/`:
- A report is a YAML template, not code: `templates/<name>.yaml` with `header` lines, a `row` format
  using `{field:format}` placeholders (Python format spec only, rendered with `str.format_map` over a
  dict of plain floats and strings, never `eval`), `missing` text per field, `period` (`1min`, `hourly`,
  `daily`) and `filename` pattern (`{ship}_{yyyymmdd}.txt`).
- `ReportWriter` (an OpenRVDAS Writer) collects records, writes one file per period into a directory, and
  closes the file at the period boundary using record time, never the wall clock. A missing field writes
  the template's missing text, never a guess or a zero.
- Ship templates: `samos_daily.yaml` and `noaa_hourly.yaml`, both with `status: UNVERIFIED` and a comment
  saying which public description was used. Do NOT invent field order or codes you cannot cite from a
  file in this repository; leave a `TODO(sample)` line instead and list it in the report.
- `verify.py`: `python -m contrib.deepsignal.met_reports verify <template> <sample_file>` renders the
  template from the sample's own values when a parser is defined in the template (`parse:` section) and
  prints a byte diff. Exit 0 only on an exact match. This is how a template moves to `status: VERIFIED`.
- Email or upload is out of scope: write files only. Existing core `EmailWriter` can send them later.

## Failing test first
`contrib/deepsignal/test/met_reports/test_writer.py`: a toy template renders exactly; period boundaries at
00:00Z and at the hour; missing text; format specs; filename pattern; a template with a bad placeholder
fails at load with a plain message; verify reports a one-byte difference; UNVERIFIED templates log a
warning once at start.

## Module contract
Docs `contrib/deepsignal/docs/met_reports.md`: how to add a template, how verification works, which
templates are verified. Depends on no other module.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/met_reports -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/met_reports contrib/deepsignal/test/met_reports
```

## Scope
Create or change only: `contrib/deepsignal/met_reports/**`, `contrib/deepsignal/test/met_reports/**`, `contrib/deepsignal/docs/met_reports.md`, `contrib/deepsignal/configs/met_reports_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

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
