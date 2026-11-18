# Brief: p2-config-lint (Cruise config linter)

- Decision: IDEAS #127, from Eugene's 2026-11-18 asks (config assist, sensor init, ecosystem and compression); build per D-NIGHT1
- Risk tier: low
- Module: exactly one. Branch `deepsignal/p2-config-lint` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 5/1/2
- Depends on: none; complements core `validate_config` (schema) with ship-sense checks

## Goal
Before a tech loads a cruise definition, one command lists the mistakes that schema validation cannot see
(two loggers on one port, a logger missing from a mode, nothing writing to the cache), in plain English.

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
- Core `logger/utils/validate_config.py` (if present on the base) checks structure. Do not duplicate it:
  call it first when importable and include its findings, then add the checks below.

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/config_lint/`, `lint(cruise_dict) -> list[Finding]`, each
`{level: error|warning|info, where: "loggers.s330 / config s330-net", message, fix}`:
- error: two configs active in the same mode read the same serial port, or bind the same UDP port.
- error: a mode names a config that does not exist; a logger has no config in some mode.
- warning: a non-off config has no `CachedDataWriter` (nothing reaches displays).
- warning: a non-off config has no `LogfileWriter` in any mode named like `log` or `write`.
- warning: two loggers prefix data with the same data id.
- warning: a serial reader with no timeout; a `LogfileWriter` path outside the configured root
  (option `--root`).
- info: configs defined but used by no mode.
- CLI `python -m contrib.deepsignal.config_lint <cruise.yaml> [--root /data]`, exit 1 on any error.

## Failing test first
`contrib/deepsignal/test/config_lint/test_lint.py`: the NBP1406 cruise file lints with no errors (record
any warnings it has as the expected baseline); one small fixture per finding; core validator findings are
included when importable; exit codes.

## Setup engine interface (MCP, console and CLI all call this)
A shared facade `contrib/deepsignal/setup/` (built separately; do not create it) exposes detect, propose, diff, validate and apply to the MCP gateway, the console and the CLI. It imports this module and never shells out. So, next to the CLI, provide pure functions that take plain dicts and return JSON-serializable dicts, with no printing, no prompts and no side effects beyond what the name says: `lint(cruise: dict) -> dict` (`{findings: [...], errors: N, warnings: N}`). The CLI calls these same functions. Test that each return value survives `json.dumps`.

## Module contract
Docs `contrib/deepsignal/docs/config_lint.md` with each finding, why it matters, and the fix. Depends on no
other module.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/config_lint -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/config_lint contrib/deepsignal/test/config_lint
```
```
python3.12 -m contrib.deepsignal.config_lint test/NBP1406/NBP1406_cruise.yaml
```

## Scope
Create or change only: `contrib/deepsignal/config_lint/**`, `contrib/deepsignal/test/config_lint/**`, `contrib/deepsignal/docs/config_lint.md`, `contrib/deepsignal/configs/config_lint_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

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
