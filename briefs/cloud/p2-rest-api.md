You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-rest-api` from commit `3b4b76e` (the contrib master tree; it is in this fork's history, for example `git merge-base origin/deepsignal/vector-wind origin/deepsignal/instrument-history`) (if `deepsignal/p2-rest-api` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-rest-api`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML is already an OpenRVDAS dependency; add no other dependency. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-rest-api (Read-only REST data API)

- Decision: D-PARITY1, IDEAS #105 (Eugene approved building #104-#124, 2026-11-18)
- Risk tier: medium
- Module: exactly one. Branch `deepsignal/p2-rest-api` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 2/4/5
- Depends on: none (shares query-budget idea with #67; reads the CachedDataServer)
- Needs Eugene: Exposure: binds to 127.0.0.1 by default. Serving it to the ship LAN or shore needs Eugene to pick the auth story (#115 roles) first.

## Goal
Scientists pull latest values and recent time series into MATLAB, R or Python with one plain URL, with
no write path to anything.

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
- The CachedDataServer (CDS) answers websocket JSON requests: `{"type": "fields"}`,
  `{"type": "describe", "fields": [...]}`, `{"type": "subscribe", "fields": {name: {"seconds": N}}}`
  then `{"type": "ready"}`. Read `server/cached_data_server.py` on the base for the exact shapes; do not
  guess. The `websockets` package is already an OpenRVDAS dependency.

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/rest_api/`:
- `server.py`: stdlib `http.server.ThreadingHTTPServer`, GET only (any other method returns 405),
  default bind `127.0.0.1:8770`, `--host`/`--port` flags.
- `source.py`: a `DataSource` protocol with `fields()`, `describe(names)`, `series(name, seconds)`; the
  real `CDSSource` talks to the CDS; tests use a `FakeSource`.
- Endpoints (JSON, UTF-8, `Cache-Control: no-store`):
  - `/api/v1/fields` list of names with any metadata the CDS describes.
  - `/api/v1/latest?fields=a,b` latest value, timestamp and age in seconds per field.
  - `/api/v1/series?field=a&seconds=600&max_points=2000` time series from the CDS back-buffer;
    if more points than `max_points`, return every k-th point and say `"decimated": k`.
  - `/api/v1/health` source reachable yes or no.
- Budgets: `seconds` at most 86400, `max_points` at most 20000, at most 20 fields per call. Over budget
  returns 400 with a plain message naming the limit.
- Unknown field returns 404 naming it. CDS unreachable returns 503 with a plain message.
- `?format=csv` on `series` returns `time,value` CSV with ISO 8601 UTC times.

## Failing test first
`contrib/deepsignal/test/rest_api/test_server.py`: start the server on port 0 with `FakeSource`; each
endpoint's shape; CSV output; decimation; every budget refusal; 404 and 405 and 503; no write method
works; a field name with `<script>` comes back JSON-escaped.

## Module contract
Docs `contrib/deepsignal/docs/rest_api.md` with curl, MATLAB `webread` and Python examples, and a plain
warning that it has no login yet and binds to localhost by default. Depends on no other module.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/rest_api -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/rest_api contrib/deepsignal/test/rest_api
```

## Scope
Create or change only: `contrib/deepsignal/rest_api/**`, `contrib/deepsignal/test/rest_api/**`, `contrib/deepsignal/docs/rest_api.md`, `contrib/deepsignal/configs/rest_api_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

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
