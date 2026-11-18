You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-time-health` from commit `3b4b76e` (the contrib master tree; it is in this fork's history, for example `git merge-base origin/deepsignal/vector-wind origin/deepsignal/instrument-history`) (if `deepsignal/p2-time-health` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-time-health`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML is already an OpenRVDAS dependency; add no other dependency. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-time-health (Time health service: host clock, source timestamps, skew)

- Decision: IDEAS #165, from Eugene's 2026-11-18 asks (config assist, sensor init, ecosystem and compression); build per D-NIGHT1
- Risk tier: medium
- Module: exactly one. Branch `deepsignal/p2-time-health` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 5/5/3
- Depends on: feeds the #162 Time stage; complements #31 clock forensics and #142 time and motion alignment (not built)

## Goal
Time is treated as a dependency every stream shares. The console shows the host clock's sync state, and
for each stream its timestamp source, confidence, latency, backward steps and skew against the reference.
Evidence: desk `docs/PAIN-POINTS.md` (Deep Research, 2026-11-18); mapping in `docs/PAIN-POINTS-MAP.md`. (pain point 3; opportunity "Authoritative time-health service").

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
Package `contrib/deepsignal/time_health/`:
- `host.py`: read the sync state without root.
  - chrony: `chronyc -c tracking`; parse system offset, RMS offset, stratum, leap status and reference.
  - systemd-timesyncd: `timedatectl show-timesync`.
  - Otherwise: "unknown".
  - Each command runs with a 2 s timeout behind an injectable runner.
- `streams.py`, `TimeHealthTransform`: per configured stream, compare the record timestamp (host arrival
  time in OpenRVDAS) with any embedded source time field (for example the GGA UTC time or the ZDA date and
  time) and reports:
  - latency (median and p95 over a window)
  - backward steps
  - repeats
  - jumps over `jump_s`
  - the stream's timestamp source (`host`, `embedded`)
  - confidence (`good`, `degraded`, `bad`) by fixed rules: host unsynced or offset over 0.5 s is bad;
    p95 latency over 2 s is degraded; any backward step in the last 10 minutes is degraded.
  - The GGA time-of-day roll at midnight is handled using the record date.
- Inter-stream skew: for pairs of streams that embed source times (for example two GNSS feeds), the
  median difference.
- Publishes `ds_time:host:*` and `ds_time:<stream>:*` fields.

## Failing test first
`contrib/deepsignal/test/time_health/test_time_health.py`:
- chrony parse fixtures (synced, unsynced, unreachable).
- timesyncd parse.
- Latency stats.
- Backward step and repeat detection.
- The midnight roll.
- Confidence rules.
- Skew between two fake GNSS streams.
- The runner timeout handling.

## Module contract
Docs `contrib/deepsignal/docs/time_health.md` (what each state means and the first thing to check).

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/time_health -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/time_health contrib/deepsignal/test/time_health
```

## Scope
Create or change only: `contrib/deepsignal/time_health/**`, `contrib/deepsignal/test/time_health/**`, `contrib/deepsignal/docs/time_health.md`, `contrib/deepsignal/configs/time_health_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

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
