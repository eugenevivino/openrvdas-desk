You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-component-catalog` from commit `3b4b76e` (the contrib master tree; it is in this fork's history, for example `git merge-base origin/deepsignal/vector-wind origin/deepsignal/instrument-history`) (if `deepsignal/p2-component-catalog` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-component-catalog`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML is already an OpenRVDAS dependency; add no other dependency. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-component-catalog (Component catalog: every reader, writer and transform as a form)

- Decision: IDEAS #128, from Eugene's 2026-11-18 asks (config assist, sensor init, ecosystem and compression); build per D-NIGHT1
- Risk tier: low
- Module: exactly one. Branch `deepsignal/p2-component-catalog` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 5/2/3
- Depends on: none; #114 wizard, #126 generator, console forms and the MCP gateway (#64) all read its output

## Goal
Every OpenRVDAS reader, writer and transform (UDP, TCP, serial, MQTT, Redis, databases, files, the cache,
websockets, email, InfluxDB, Grafana, Sealog and the rest) can be set up from a form with plain labels,
defaults and checks, so no part of OpenRVDAS needs hand-written YAML.

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
Package `contrib/deepsignal/catalog/`:
- `build.py`: import every module under the importable `logger.readers`, `logger.writers` and
  `logger.transforms` packages (walk the package directories; never hard-code the list). For each public
  class that subclasses the Reader, Writer or Transform base: name, module path, kind, first docstring
  paragraph, and each `__init__` parameter with default, type hint (as text) and its docstring line if
  the class docstring documents it. A module that fails to import (missing optional dependency such as
  `paho-mqtt`, `redis`, `mysqlclient`, `geopandas`) is listed with `available: false` and the import
  error text, never crashes the build.
- Output `catalog.json` plus one JSON Schema per class (`type`, `default`, `description`, `required`),
  derived only from the signature and docstring. Unknown types become `string` with a note.
- `check_component(entry) -> findings`: a config entry `{class, module?, kwargs}` is checked against the
  catalog: unknown class (suggest the closest name), unknown kwarg (suggest the closest), missing required
  kwarg, class unavailable because of a missing dependency (name the pip extra from `pyproject.toml` if
  present on the base).
- `guided.yaml` (hand-written, small): plain-English labels and good examples for the 15 most used
  components (serial, polled serial, UDP, TCP, MQTT, Redis, CachedData reader and writer, Logfile writer,
  UDP writer, MQTT writer, Database writer, Parse, Prefix, TrueWinds). Labels override docstring text.
- CLI: `python -m contrib.deepsignal.catalog build > catalog.json`; `... show UDPReader`;
  `... check config.yaml` (checks every reader, transform and writer in a logger config).

## Failing test first
`contrib/deepsignal/test/catalog/test_catalog.py`: catalog count equals the number of public component
classes found by walking the package (no hard-coded number); `UDPReader` has its `port` parameter as
required; a simulated missing dependency yields `available: false`; a typo kwarg gets a suggestion; the
NBP1406 cruise configs check clean; schema output is valid JSON with `required` lists.

## Setup engine interface (MCP, console and CLI all call this)
A shared facade `contrib/deepsignal/setup/` (built separately; do not create it) exposes detect, propose, diff, validate and apply to the MCP gateway, the console and the CLI. It imports this module and never shells out. So, next to the CLI, provide pure functions that take plain dicts and return JSON-serializable dicts, with no printing, no prompts and no side effects beyond what the name says: `catalog() -> dict`, `schema(class_name) -> dict` and `check_component(entry: dict) -> dict`. The CLI calls these same functions. Test that each return value survives `json.dumps`.

## Module contract
Docs `contrib/deepsignal/docs/catalog.md` including the coverage table this produces. Depends on no other
module.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/catalog -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/catalog contrib/deepsignal/test/catalog
```
```
python3.12 -m contrib.deepsignal.catalog check test/NBP1406/NBP1406_cruise.yaml
```

## Scope
Create or change only: `contrib/deepsignal/catalog/**`, `contrib/deepsignal/test/catalog/**`, `contrib/deepsignal/docs/catalog.md`, `contrib/deepsignal/configs/catalog_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

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
