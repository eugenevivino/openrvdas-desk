You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-stream-health` from commit `3b4b76e` (the contrib master tree; it is in this fork's history, for example `git merge-base origin/deepsignal/vector-wind origin/deepsignal/instrument-history`) (if `deepsignal/p2-stream-health` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-stream-health`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML is already an OpenRVDAS dependency; add no other dependency. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-stream-health (Stream health engine: dependency chain and state transitions)

- Decision: IDEAS #162, from Eugene's 2026-11-18 asks (config assist, sensor init, ecosystem and compression); build per D-NIGHT1
- Risk tier: medium
- Module: exactly one. Branch `deepsignal/p2-stream-health` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 5/4/4
- Depends on: feeds the console chain view; #165 time health and #135 or #166 storage facts plug in as stage sources

## Goal
Every stream has a health state per stage of its chain:
sensor, endpoint, raw traffic, parser, time, calibration, derived, store.
Alerts fire on transitions (healthy to degraded to failed, and recovery), not on every bad sample.
Evidence: desk `docs/PAIN-POINTS.md` (Deep Research, 2026-11-18); mapping in `docs/PAIN-POINTS-MAP.md`. (pain points 1, 4, 6, 10, 14; opportunities "Universal data-health model",
"State-transition alerting", "Dependency-aware fault localization").

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
- OpenRVDAS has open requests for transition-based QC alerts and timeout nulls. Do not change core.
  This runs as a separate reader and writer pair: read the CachedDataServer, write `ds_chain:*` fields
  back to it.

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/stream_health/`:
- `chain.yaml` (example `contrib/deepsignal/configs/stream_health_example.yaml`): per stream, the logger,
  key fields, expected period (or learned), and optional stage sources:
  - `endpoint`: a serial port or host:port, checked only by reading OS facts like port existence; never
    opened.
  - `time`: from #165 fields.
  - `calibration`: from #164 fields.
  - `store`: a directory whose newest file must grow.
- `evaluate(snapshot, now) -> dict`: a pure function returning per stream, per stage, `{state, since,
  evidence}`. States are OK, DEGRADED, FAILED, UNKNOWN, OFF.
  - The first not-OK stage is the stream's root cause; later stages are "affected".
  - The derived variables the stream feeds are listed as "affected outputs".
- `TransitionTracker`: hysteresis (`hold_s` default 10) and a rate cap per stream. It emits transition
  records `{stream, stage, from, to, at, evidence}` that #133 Sealog and the timeline (#168) consume.
- `StreamHealthWriter`: publishes `ds_chain:<stream>:<stage>` and `ds_chain:<stream>:root` to the CDS each
  second. It also writes an explicit `null` plus `ds_age_s:<field>` once a field passes its timeout, which
  covers the OpenRVDAS request for timeout nulls so Grafana can tell a dead feed from a steady value.
- Setup engine: `evaluate` and `describe_chain(cfg) -> dict` are pure and JSON-safe.

## Failing test first
`contrib/deepsignal/test/stream_health/test_stream_health.py`:
- Each stage failing gives the right root and affected outputs.
- Flapping inside hold gives no transition.
- Recovery transition.
- The rate cap holds.
- Timeout null and age fields.
- The endpoint check never opens the port: assert the fake opener is never called.
- A missing store dir gives UNKNOWN, not FAILED.

## Module contract
Docs `contrib/deepsignal/docs/stream_health.md` with the chain drawn as a text diagram.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/stream_health -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/stream_health contrib/deepsignal/test/stream_health
```

## Scope
Create or change only: `contrib/deepsignal/stream_health/**`, `contrib/deepsignal/test/stream_health/**`, `contrib/deepsignal/docs/stream_health.md`, `contrib/deepsignal/configs/stream_health_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

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
