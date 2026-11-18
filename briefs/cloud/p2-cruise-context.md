You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-cruise-context` from commit `3b4b76e` (the contrib master tree; it is in this fork's history, for example `git merge-base origin/deepsignal/vector-wind origin/deepsignal/instrument-history`) (if `deepsignal/p2-cruise-context` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-cruise-context`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML is already an OpenRVDAS dependency; add no other dependency. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-cruise-context (Cruise context from OpenVDM and Sealog)

- Decision: IDEAS #132, from Eugene's 2026-11-18 asks (config assist, sensor init, ecosystem and compression); build per D-NIGHT1
- Risk tier: low
- Module: exactly one. Branch `deepsignal/p2-cruise-context` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 4/3/3
- Depends on: writes the #120 cruise-meta file format (see origin/deepsignal/p2-cruise-meta)

## Goal
Nobody types the cruise id, dates and ports a third time: DeepSignal reads them from OpenVDM (or Sealog)
and fills its cruise metadata, and every DeepSignal report names the same cruise and lowering.

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
- OpenVDM API (GET, read-only): `api/warehouse/getCruiseConfig` returns the current cruise config as
  written to `cruise_config.json`: cruise ID, name, description, PI, start and end dates, start and end
  ports, location, plus the `vessel` block (name, operator, and `r2r` vessel, operator and scheduler ids
  when set) since 2.17. Also `api/warehouse/getLoweringID`, `getLoweringStartDate`, `getLoweringEndDate`.
  Field names in the JSON: read them from a fixture you write from these facts and mark it
  `# shape from OpenVDM 2.17 source, verify on a live system`.
- Sealog API: `GET /api/v1/cruises` (cruise_id, start_ts, stop_ts, cruise_location, cruise_additional_meta)
  with a JWT.
- #120 cruise metadata file format: `git show origin/deepsignal/p2-cruise-meta` (if missing, the brief
  `briefs/p2/120-cruise-meta.md` design applies).

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/cruise_context/`:
- `from_openvdm(cfg: dict) -> dict` and `from_sealog(cruise: dict) -> dict`: pure mappers into the #120
  format. Unknown or empty fields stay null; never invent.
- `fetch(source, url, token_env=None)`: one GET, 10 s timeout, stdlib `urllib`; no writes to any server.
- CLI `python -m contrib.deepsignal.cruise_context pull --openvdm URL [--out cruise.yaml] [--diff existing]`:
  refuses to overwrite; prints a diff against an existing file.
- `CruiseContextReader`: polls the source every `interval` (default 300 s) and emits `cruise_id`,
  `lowering_id`, `cruise_active`, so loggers and reports can tag data; a source outage keeps the last value
  and marks it stale.

## Failing test first
`contrib/deepsignal/test/cruise_context/test_context.py`: OpenVDM fixture maps to the #120 fields; Sealog
fixture maps; missing fields stay null; no overwrite; diff output; reader keeps last value and marks
stale on outage (fake fetch); token never logged.

## Module contract
Docs `contrib/deepsignal/docs/cruise_context.md`. A lead-run check against a live OpenVDM happens outside
the sandbox.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/cruise_context -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/cruise_context contrib/deepsignal/test/cruise_context
```

## Scope
Create or change only: `contrib/deepsignal/cruise_context/**`, `contrib/deepsignal/test/cruise_context/**`, `contrib/deepsignal/docs/cruise_context.md`, `contrib/deepsignal/configs/cruise_context_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

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
