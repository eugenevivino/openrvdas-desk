You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-config-from-inventory` from commit `3b4b76e` (the contrib master tree; it is in this fork's history, for example `git merge-base origin/deepsignal/vector-wind origin/deepsignal/instrument-history`) (if `deepsignal/p2-config-from-inventory` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-config-from-inventory`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML is already an OpenRVDAS dependency; add no other dependency. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-config-from-inventory (Cruise config generator from the instrument inventory)

- Decision: D-PARITY1, IDEAS #126 (Eugene approved building #104-#124, 2026-11-18)
- Risk tier: medium
- Module: exactly one. Branch `deepsignal/p2-config-from-inventory` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 5/2/3
- Depends on: reads #52 instrument history YAML by path and device types from contrib/devices; no code imports

## Goal
The ship's instrument inventory is the single source of truth: one command turns it into a complete
OpenRVDAS cruise definition (loggers, configs, modes), and shows the diff against what is running now,
the way CORIOLIX generates OpenRVDAS configs from its sensor database.

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
- Cruise definition shape: read `test/NBP1406/NBP1406_cruise.yaml` on the base (loggers with configs,
  modes, configs with readers, transforms, writers). Generated output must load with the base's config
  reader and pass the base's `validate_config` if that module exists on the base.

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/config_gen/`:
- Input `acquisition.yaml` (example `contrib/deepsignal/configs/config_gen_example.yaml`):
  ```yaml
  cruise: {id: RR2205, start: 2022-04-01, end: 2022-05-10}
  defaults: {logfile_root: /data/openrvdas, cds: localhost:8766}
  instruments:                     # ids match the #52 history file if one is given
    - {id: s330, device_type: Seapath330, transport: {serial: {port: /dev/ttyS0, baudrate: 115200}}}
    - {id: mwx1, device_type: RMYoung85106, transport: {udp: {port: 6224}}, enabled: false}
  modes: [off, monitor, log]       # off; monitor = parse to CDS only; log = monitor plus logfile
  ```
- `generate(acq, history=None) -> dict`: one logger per enabled instrument with configs `<id>-off`,
  `<id>-net`, `<id>-net+file`; modes map to them; each config is reader, `PrefixTransform` with the id,
  `ParseTransform` with the device definitions path, `CachedDataWriter`, and for `log` a `LogfileWriter`
  under `<logfile_root>/<id>/raw/<id>`. Disabled instruments appear only in `off`.
- If a history file is given: warn for an enabled instrument not installed today, and for an installed
  instrument with no acquisition entry.
- `render(dict) -> str`: YAML with a header comment (generated by, from which inputs, sha256 of inputs,
  UTC time) and a stable key order, so regenerating with unchanged inputs gives identical bytes.
- CLI: `python -m contrib.deepsignal.config_gen <acq.yaml> [--history h.yaml] [--diff current_cruise.yaml]
  [--out new_cruise.yaml]`. `--out` refuses to overwrite an existing file. `--diff` prints a unified diff.

## Failing test first
`contrib/deepsignal/test/config_gen/test_generate.py`: example generates the expected loggers and modes;
disabled instrument only in off; output loads with the base config reader (and validates if available);
byte-identical regeneration; history warnings both ways; unknown device type is a plain error naming the
nearest known type; `--out` refuses to overwrite.

## Module contract
Docs `contrib/deepsignal/docs/config_gen.md`. Depends on #52's file format only (optional input).

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/config_gen -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/config_gen contrib/deepsignal/test/config_gen
```

## Scope
Create or change only: `contrib/deepsignal/config_gen/**`, `contrib/deepsignal/test/config_gen/**`, `contrib/deepsignal/docs/config_gen.md`, `contrib/deepsignal/configs/config_gen_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

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
