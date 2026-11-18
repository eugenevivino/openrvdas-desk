You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-depth-consensus` from commit `3b4b76e` (the contrib master tree; it is in this fork's history, for example `git merge-base origin/deepsignal/vector-wind origin/deepsignal/instrument-history`) (if `deepsignal/p2-depth-consensus` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-depth-consensus`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML is already an OpenRVDAS dependency; add no other dependency. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-depth-consensus (Multibeam vs single-beam vs grid depth cross-check)

- Decision: IDEAS #141, D-SHIP1, from Eugene's 2026-11-18 ask to interface with sonars; build per D-NIGHT1
- Risk tier: low (reads fields, writes new fields only)
- Module: exactly one. Branch `deepsignal/p2-depth-consensus` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 5/4/3
- Depends on: none to build. In use it reads #139 `MB_NadirDepth`, a single-beam field (for example core
  device `Knudsen3260` `HFDepth` and `LFDepth`, or an EK80 `DPT`), and optionally a grid-depth field

## Goal
When the multibeam, the echosounders and the expected seafloor disagree, the tech sees which one is wrong in
seconds (lost bottom lock, wrong draft, wrong sound speed, a side lobe), instead of after the cruise.

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
- Design and safety context: desk `docs/SHIP-SYSTEMS.md` and decision D-SHIP1. This module is PASSIVE:
  it never opens a socket, never sends a byte to any ship system, and never changes a setting.


## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/depth_consensus/`, class `DepthConsensusTransform(Transform)`:
- kwargs: `sources` mapping a name to `{field, offset_m, max_age_s, role}` where `offset_m` is added to
  convert the value to metres below the waterline (single-beam depth below transducer plus transducer
  depth), and `role` is `sonar` or `reference` (a grid is a `reference`: it can mark a sonar "suspicious"
  but never outvotes two agreeing sonars); `threshold_pct` (2.0), `min_depth_m` (5), `persist_s` (60),
  `clear_s` (60), `prefix` (`DEPTH`).
- Output fields: `<prefix>_Consensus` (median of fresh sonar sources), `<prefix>_SpreadPct`,
  `<prefix>_Dev_<name>` (percent from consensus), `<prefix>_OddOne`, `<prefix>_Alarm`,
  `<prefix>_AlarmText`, `<prefix>_Stale`, `<prefix>_LostBottom` (comma list: a source that is None, zero
  or invalid for `persist_s` while at least one other sonar is fresh), `<prefix>_Step` (comma list: a source
  that jumps more than 4 times `threshold_pct` between consecutive values while the others hold steady).
- Alarm logic (shared shape across ship-system monitors; implement locally, no shared module): a
  condition must hold continuously for `persist_s` of record time before the alarm field goes to 1, and must
  stay below 0.75 of the threshold for `clear_s` before it clears (hysteresis). Use record timestamps, never
  the wall clock, so replays and reanalysis give identical output.
- Freshness: each source has `max_age_s`; a stale source is excluded and reported in `<prefix>_Stale` as a
  comma-separated list of source names, never treated as zero.
- With one sonar plus a reference: report deviation and set the alarm only with the "suspicious" text.

## Failing test first
`contrib/deepsignal/test/depth_consensus/test_depth.py`: agreement; offset applied; one sonar off;
persistence and hysteresis; lost bottom; step; reference-only suspicion; shallow-water floor
(`min_depth_m`); stale handling; replay determinism; `None`, list, DASRecord and dict inputs.

## Module contract
Docs `contrib/deepsignal/docs/depth_consensus.md` (why depths differ, what each alarm means, what to check).
Sample config `contrib/deepsignal/configs/depth_consensus_demo.yaml` using the NBP1406 Knudsen data if the
base tree has it plus a synthetic multibeam field. Depends on no other module.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/depth_consensus -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/depth_consensus contrib/deepsignal/test/depth_consensus
```

## Scope
Create or change only: `contrib/deepsignal/depth_consensus/**`, `contrib/deepsignal/test/depth_consensus/**`,
`contrib/deepsignal/docs/depth_consensus.md`, `contrib/deepsignal/configs/depth_consensus_*.yaml`, and empty `__init__.py`
files where missing. Everything else is read-only.

## Trust boundaries and data integrity
Inputs are untrusted numbers: reject NaN, inf, negative and non-numeric. Never change incoming fields; only
add the new fields above. Missing or stale sources are shown as such, never guessed.

## Non-goals and banned
No grid lookup in this module (a later provider fills the reference field). No writes to any sonar. No core
changes, no new dependency, no refactors outside Scope. No loosened, skipped or deleted tests, no swallowed
errors.

## Usability (anything a tech sees or edits)
Answer each line of desk `docs/USABILITY.md` in the report, or N/A with a reason. Every config error is one
plain-English line naming the setting, what it saw, what it expected, and a good example. Every alarm text
names the source, the two values, the threshold, and the first thing to check.

## Stop rule
No code change needed: stop and report. Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Acceptance tails:
- Open questions:
