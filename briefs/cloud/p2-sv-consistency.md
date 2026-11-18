You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-sv-consistency` from commit `3b4b76e` (the contrib master tree; it is in this fork's history, for example `git merge-base origin/deepsignal/vector-wind origin/deepsignal/instrument-history`) (if `deepsignal/p2-sv-consistency` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-sv-consistency`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML is already an OpenRVDAS dependency; add no other dependency. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-sv-consistency (Sound velocity consistency monitor)

- Decision: IDEAS #140, D-SHIP1, from Eugene's 2026-11-18 ask to interface with sonars; build per D-NIGHT1
- Risk tier: low (reads fields, writes new fields only)
- Module: exactly one. Branch `deepsignal/p2-sv-consistency` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 5/5/3
- Depends on: none to build. In use it reads #139 field `MB_SVTransducer` and `MB_SVProbe`, a probe field,
  a TSG sound-speed field (SBE45 outputs one; #112 computes one), and a cast surface value (#147 or manual)

## Goal
When the sound speed the multibeam is using at its transducer disagrees with the hull probe, the
thermosalinograph or the last cast, the tech gets one plain alarm that says which source is the odd one out,
instead of finding refraction artifacts in the swath hours later.

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

- No sound-speed math in this module: every input is already in m/s. (Formulas live in #112.)

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/sv_consistency/`, class `SVConsistencyTransform(Transform)`:
- kwargs: `sources` mapping a role name to `{field, max_age_s}`, for example
  `{probe: {field: SVP_Velocity, max_age_s: 30}, tsg: {field: TSG_SoundVelocity, max_age_s: 120},
  sonar: {field: MB_SVTransducer, max_age_s: 30}, cast: {field: CAST_SurfaceSV, max_age_s: null}}`;
  `threshold_ms` (default 2.0 m/s), `persist_s` (120), `clear_s` (60), `prefix` (`SV`), `valid_range`
  (1400 to 1600 m/s; outside is reported as invalid, not used).
- Keeps the latest value and record timestamp per role; on each record emits only when an input changed.
- Output fields: `<prefix>_Spread` (max minus min of fresh valid sources), `<prefix>_Diff_<a>_<b>` for each
  fresh pair, `<prefix>_OddOne` (with three or more fresh sources: the role whose distance to the median of
  the others exceeds the threshold, else empty), `<prefix>_Alarm` (0 or 1), `<prefix>_AlarmText`,
  `<prefix>_Fresh` (count), `<prefix>_Stale`, `<prefix>_CastAge_s` when a cast role exists.
- Alarm logic (shared shape across ship-system monitors; implement locally, no shared module): a
  condition must hold continuously for `persist_s` of record time before the alarm field goes to 1, and must
  stay below 0.75 of the threshold for `clear_s` before it clears (hysteresis). Use record timestamps, never
  the wall clock, so replays and reanalysis give identical output.
- Freshness: each source has `max_age_s`; a stale source is excluded and reported in `<prefix>_Stale` as a
  comma-separated list of source names, never treated as zero.
- Alarm text example: "Sonar is using 1503.2 m/s at the transducer; probe reads 1509.8 and TSG 1509.5
  (2.0 m/s limit, 3 minutes). Check the SV input in SIS or take a cast." Advice only; never acts.

## Failing test first
`contrib/deepsignal/test/sv_consistency/test_sv.py`: agreement gives no alarm; one source off raises only
after `persist_s`; hysteresis clear; odd-one-out naming with 3 and 4 sources; 2 sources give spread but no
odd one; stale source excluded and listed; out-of-range value excluded; cast age; replay determinism (same
input twice gives identical output); `None` and list inputs; DASRecord and dict inputs.

## Module contract
Docs `contrib/deepsignal/docs/sv_consistency.md` (why SV at the transducer matters, in plain words; every
field; what to check first). Sample config `contrib/deepsignal/configs/sv_consistency_demo.yaml`. Depends on
no other module.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/sv_consistency -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/sv_consistency contrib/deepsignal/test/sv_consistency
```

## Scope
Create or change only: `contrib/deepsignal/sv_consistency/**`, `contrib/deepsignal/test/sv_consistency/**`,
`contrib/deepsignal/docs/sv_consistency.md`, `contrib/deepsignal/configs/sv_consistency_*.yaml`, and empty `__init__.py`
files where missing. Everything else is read-only.

## Trust boundaries and data integrity
Inputs are untrusted numbers: reject NaN, inf, non-numeric. Never change incoming fields; only add the new
fields above. Missing or stale sources are shown as such, never guessed.

## Non-goals and banned
No sending anything to the sonar or SIS. No sound-speed formulas. No core changes, no new dependency, no
refactors outside Scope. No loosened, skipped or deleted tests, no swallowed errors.

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
