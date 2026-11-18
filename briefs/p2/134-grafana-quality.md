# Brief: p2-grafana-quality (Grafana quality pack: QC and freshness dashboards from the cruise definition)

- Decision: IDEAS #134, from Eugene's 2026-11-18 asks (config assist, sensor init, ecosystem and compression); build per D-NIGHT1
- Risk tier: low
- Module: exactly one. Branch `deepsignal/p2-grafana-quality` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 4/3/4
- Depends on: QARTOD flag fields; core InfluxDBWriter

## Goal
Ships that already run Grafana get quality views for free: every sensor's value colored by its QC flag,
time since last data, and alert rules, generated from the cruise definition instead of clicked together.

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
- Core has `InfluxDBWriter` (bucket, measurement, tags) and `GrafanaLiveWriter` (Grafana Live push with
  line protocol); `utils/install_influxdb.sh` installs InfluxDB and Grafana. OceanDataTools publishes
  Grafana panels `oceandatatools-compass-panel` (heading, true and apparent wind) and an attitude panel
  (roll and pitch).

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/grafana/`:
- `generate(cruise: dict, options) -> dict`: Grafana dashboard JSON (schemaVersion 39) per logger group:
  for each field a time series panel with value mappings and threshold colors keyed on its `_QC` field
  (1 green, 3 amber, 4 red, 9 grey), a stat panel of seconds since last value, and, when heading and wind
  fields exist, a compass panel entry (plugin id `oceandatatools-compass-panel`, marked optional).
  Flux queries against the bucket and measurement the cruise's `InfluxDBWriter` uses.
- `alerts(cruise) -> list`: Grafana alert rule JSON for flag 4 lasting over 5 minutes and stale over
  `stale_after_s`.
- Provisioning files (`dashboards.yaml` provider) so `grafana` loads them from a directory; no Grafana API
  calls in v1.
- CLI `python -m contrib.deepsignal.grafana build <cruise.yaml> --out DIR`.

## Failing test first
`contrib/deepsignal/test/grafana/test_grafana.py`: NBP1406 cruise produces valid JSON with one panel set per
field; thresholds and mappings exact; queries name the right bucket and measurement; compass entry only
when heading exists; alert rules shape; output byte-stable.

## Module contract
Docs `contrib/deepsignal/docs/grafana.md` with a screenshot step marked for the lead (outside sandbox).

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/grafana -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/grafana contrib/deepsignal/test/grafana
```
```
python3.12 -m contrib.deepsignal.grafana build test/NBP1406/NBP1406_cruise.yaml --out /tmp/ds-grafana
```

## Scope
Create or change only: `contrib/deepsignal/grafana/**`, `contrib/deepsignal/test/grafana/**`, `contrib/deepsignal/docs/grafana.md`, `contrib/deepsignal/configs/grafana_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

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
