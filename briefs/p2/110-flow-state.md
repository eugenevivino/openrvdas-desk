# Brief: p2-flow-state (Flowthrough state tagging)

- Decision: D-PARITY1, IDEAS #110 (Eugene approved building #104-#124, 2026-11-18)
- Risk tier: medium
- Module: exactly one. Branch `deepsignal/p2-flow-state` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 4/5/3
- Depends on: none (QC #8 and #55 consume its field later)

## Goal
Every underway seawater value carries a tag saying what was actually flowing through the sensor
(seawater, filtered, calibration, off or switching), so QC and scientists stop mistaking a valve change
for an ocean signal.

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
Package `contrib/deepsignal/flow_state/`, class `FlowStateTransform` in `transform.py`.
- Config (example `contrib/deepsignal/configs/flow_state_example.yaml`):
  ```yaml
  valves:
    - id: tsg_filter_valve
      tags_fields: [TSG_Temp, TSG_Cond, Fluorometer]   # fields this valve affects
      mode: schedule            # or: field
      schedule:
        anchor: 2026-11-18T00:00:00Z   # a time the valve OPENED
        open_minutes: 50
        closed_minutes: 10
        transition_seconds: 90
        open_content: seawater
        closed_content: filtered
      # mode: field  ->  state_field: valve_state, values: {1: seawater, 0: filtered}
  ```
- For each record, for each valve whose `tags_fields` appear in the record, add
  `<valve_id>_flow_state` (one of the content words, `transition`, or `unknown`) and
  `<valve_id>_flow_state_age_s` (seconds since the last switch). Use the record timestamp only, never
  the wall clock.
- Schedule mode: period = open + closed; phase = (t - anchor) mod period; open if phase < open; the first
  `transition_seconds` after each switch is `transition`. Times before the anchor still follow the
  periodic schedule.
- Field mode: the latest `state_field` value seen (from any record) sets the state; a change starts a
  transition window; a state value not in `values` gives `unknown` plus one warning per new value; no
  state seen yet gives `unknown`.
- Never changes or drops incoming fields. Records without any tagged field pass through unchanged.

## Failing test first
`contrib/deepsignal/test/flow_state/test_transform.py`: schedule phases at exactly open, exactly close,
inside the transition window, one period later, before the anchor; field mode change and transition;
unknown value; no state yet; list input; None passes through; config errors (closed_minutes 0, unknown
mode, transition longer than a phase).

## Module contract
Sample config that runs alone on NBP1406 sample TSG fields; docs `contrib/deepsignal/docs/flow_state.md`.
Depends on no other module.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/flow_state -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/flow_state contrib/deepsignal/test/flow_state
```

## Scope
Create or change only: `contrib/deepsignal/flow_state/**`, `contrib/deepsignal/test/flow_state/**`, `contrib/deepsignal/docs/flow_state.md`, `contrib/deepsignal/configs/flow_state_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

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
