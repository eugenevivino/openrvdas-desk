You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-onboard-wizard` from commit `3b4b76e` (the contrib master tree; it is in this fork's history, for example `git merge-base origin/deepsignal/vector-wind origin/deepsignal/instrument-history`) (if `deepsignal/p2-onboard-wizard` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-onboard-wizard`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML is already an OpenRVDAS dependency; add no other dependency. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-onboard-wizard (Sensor onboarding wizard (engine and CLI))

- Decision: D-PARITY1, IDEAS #114 (Eugene approved building #104-#124, 2026-11-18)
- Risk tier: medium
- Module: exactly one. Branch `deepsignal/p2-onboard-wizard` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 5/2/3
- Depends on: none; the console wizard page is a later console module that calls this engine; extends #29

## Goal
A tech captures a minute of an unknown instrument's output, runs one command, and gets a proposed,
tested logger config to accept, with no YAML typed by hand.

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
- Device definitions live in `contrib/devices/*.yaml` and `local/devices/` on the base: read their format
  from the files (device types with `format` patterns). Do not change any of them.

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/onboard/`:
- `fingerprint.py`: `identify(lines) -> list[Candidate]`. Strips OpenRVDAS timestamps if present, then
  scores each device type: share of lines that parse with that type's patterns, NMEA checksum validity
  where applicable, and sentence ids seen. Candidates sorted by score, each with the evidence ("142 of 150
  lines parsed as Seapath2200 PSXN,20") and fields seen. Never claims a match under 0.8 parse share; then it
  says "No known device matched" and proposes a regex-free raw logger only.
- `propose.py`: `propose(candidate, transport) -> dict` where transport is
  `{serial: {port, baudrate}}` or `{udp: {port}}`. Output: a logger entry with `-off`, `-net`,
  `-net+file` configs in the same style as `test/NBP1406/NBP1406_cruise.yaml` (reader, prefix, parse,
  `CachedDataWriter`, `LogfileWriter`), written as YAML text with a header comment saying it was proposed
  by the wizard, from which capture, on which date.
- `trial.py`: runs the proposed parse chain over the capture with `LogfileReader`/`TextFileReader` and
  reports records parsed, fields and units, and lines that failed (first 5).
- `diff.py`: given a cruise definition file and the proposal, prints a unified diff of what would be
  added. It never writes the cruise file; `--write <path>` writes the proposal to a NEW file only.
- CLI: `python -m contrib.deepsignal.onboard <capture.txt> --serial /dev/ttyUSB0 --baud 9600 [--cruise f.yaml]`.

## Failing test first
`contrib/deepsignal/test/onboard/test_onboard.py`: captures cut from NBP1406 sample data for two known
devices are identified first with evidence; a shuffled-junk capture gives "No known device matched"; the
proposal YAML loads and validates with the base's config reader; trial counts match; diff shows only
additions; `--write` refuses to overwrite an existing file.

## Setup engine interface (MCP, console and CLI all call this)
A shared facade `contrib/deepsignal/setup/` (built separately; do not create it) exposes detect, propose, diff, validate and apply to the MCP gateway, the console and the CLI. It imports this module and never shells out. So, next to the CLI, provide pure functions that take plain dicts and return JSON-serializable dicts, with no printing, no prompts and no side effects beyond what the name says: `propose(capture_lines: list[str], hints: dict|None) -> dict`: device type candidates with scores, the proposed logger config as a dict and its YAML, and the diff. Nothing is written or sent. The CLI calls these same functions. Test that each return value survives `json.dumps`.

## Module contract
Two small captures under `contrib/deepsignal/test/onboard/data/` (cut from NBP1406 files on the base, under
200 lines each). Docs `contrib/deepsignal/docs/onboard.md` with the 5-minute walkthrough. Depends on no
other module.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/onboard -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/onboard contrib/deepsignal/test/onboard
```

## Scope
Create or change only: `contrib/deepsignal/onboard/**`, `contrib/deepsignal/test/onboard/**`, `contrib/deepsignal/docs/onboard.md`, `contrib/deepsignal/configs/onboard_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

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
