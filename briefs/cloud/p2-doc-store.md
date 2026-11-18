You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-doc-store` from commit `3b4b76e` (the contrib master tree; it is in this fork's history, for example `git merge-base origin/deepsignal/vector-wind origin/deepsignal/instrument-history`) (if `deepsignal/p2-doc-store` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-doc-store`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML is already an OpenRVDAS dependency; add no other dependency. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-doc-store (Instrument document store)

- Decision: D-PARITY1, IDEAS #118 (Eugene approved building #104-#124, 2026-11-18)
- Risk tier: low
- Module: exactly one. Branch `deepsignal/p2-doc-store` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 4/2/3
- Depends on: #52 instrument history for instrument ids and cal ids: reads its YAML file by path, does not import its code, so it builds in parallel

## Goal
Manuals and calibration certificates live next to the instruments they belong to, with checksums, so a tech
at sea finds the right certificate in seconds and shore can verify nothing was swapped.

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
- Instrument history (#52, branch `deepsignal/instrument-history`) keeps instruments in a YAML file with
  `instruments: [{id, serial, events: [{type: calibration, cal_id, certificate}]}]`. Read that shape with
  `yaml.safe_load` only; do not import #52's code.

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/doc_store/`:
- Store layout: `<root>/<instrument_id>/<file>` plus one index `<root>/index.yaml`:
  `documents: [{path, instrument, kind: manual|calibration_certificate|photo|other, cal_id?, title,
  added, sha256, bytes}]`.
- CLI `python -m contrib.deepsignal.doc_store`:
  `add <root> <file> --instrument tsg1 --kind calibration_certificate [--cal-id X] [--title T]` copies the
  file in (never moves or deletes the original), records sha256; refuses a duplicate sha256 with a message
  naming the existing entry. `list <root> [--instrument]`. `verify <root>`: every index entry exists and
  matches its sha256; files on disk not in the index are listed. `crosscheck <root> <history.yaml>`:
  certificates whose `cal_id` is unknown in history, and history calibration events whose `certificate`
  has no document.
- Paths are confined to `<root>`: any path with `..` or absolute paths in the index is an error.
- Exit codes: 0 clean, 1 findings, 2 usage error.

## Failing test first
`contrib/deepsignal/test/doc_store/test_store.py` in a temp dir: add, duplicate refusal, list, verify
(missing file, changed bytes, stray file), crosscheck both directions with a small history fixture, path
traversal refused, original file untouched after add.

## Module contract
Docs `contrib/deepsignal/docs/doc_store.md`. Depends on #52's file format only.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/doc_store -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/doc_store contrib/deepsignal/test/doc_store
```

## Scope
Create or change only: `contrib/deepsignal/doc_store/**`, `contrib/deepsignal/test/doc_store/**`, `contrib/deepsignal/docs/doc_store.md`, `contrib/deepsignal/configs/doc_store_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

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
