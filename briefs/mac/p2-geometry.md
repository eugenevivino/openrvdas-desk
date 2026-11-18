Mac lane job (rule 8, rule 27, rule 28). Launch through `~/bin/ds-codex` only, one DeepSignal job per Mac, RAM rule applies (hold if free RAM under 4 GB or swap over 3.8 GB).

Model and effort, named explicitly: `KALON_ALLOW_ASTRA=1 ~/bin/ds-codex -m gpt-6.2-astra -c model_reasoning_effort=high` (set KALON_ALLOW_ASTRA only for this job).
Scratch: `/private/tmp/deepsignal/p2-geometry/` only (clone in `repo/`, `gc.auto=0`, `maintenance.auto=false`). Never write outside it; never touch `/private/tmp/kalon`.
Review: a separate fresh Astra session, read-only, re-derives every pinned test vector before anything merges.

You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-geometry` from commit `3b4b76e` (the contrib master tree; it is in this fork's history, for example `git merge-base origin/deepsignal/vector-wind origin/deepsignal/instrument-history`) (if `deepsignal/p2-geometry` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-geometry`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML is already an OpenRVDAS dependency; add no other dependency. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-geometry (Vessel geometry and lever-arm correction)

- Decision: D-PARITY1, IDEAS #113 (Eugene approved building #104-#124, 2026-11-18)
- Risk tier: high
- Module: exactly one. Branch `deepsignal/p2-geometry` from `3b4b76e`
- Lane: `mac`: `gpt-6.2-astra`, `model_reasoning_effort=high`, `KALON_ALLOW_ASTRA=1` (math; Eugene rule 2026-11-18)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 2/3/2
- Depends on: none; #52 instrument history may later reference sensor position ids
- Mac scratch path: `/private/tmp/deepsignal/p2-geometry/` only (rule 28)

## Goal
Every sensor's position on the ship is written down once, and GNSS positions are corrected from the
antenna to the ship's reference point, so position-dependent products line up to the metre.

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
Package `contrib/deepsignal/geometry/`:
- `vessel_geometry.yaml` (example `contrib/deepsignal/configs/geometry_example.yaml`): ship frame with
  origin at the reference point, x forward, y starboard, z up, metres. Entries:
  `positions: [{id: gnss_primary, x: 12.3, y: -1.1, z: 25.0, surveyed: 2025-03-02, by: "survey firm"}]`,
  `monuments: [{id: BM1, x: 0, y: 0, z: 3.2, note: "main deck benchmark"}]`.
  `check()`: duplicate ids, missing coordinates, a position more than 200 m from origin (warning).
- `LeverArmTransform` in `transform.py`: config `lat_field`, `lon_field`, `heading_field`,
  `antenna` (a position id), `target` (default the origin), output fields `<prefix>Latitude` and
  `<prefix>Longitude` added; inputs untouched. Uses the latest heading seen; heading older than
  `heading_timeout` (default 2 s) means no output and one warning.
- Heading only in v1 (roll and pitch ignored; the docs say the error this leaves, about z sin(roll), is
  under 0.5 m for a 25 m mast at 1 degree).

## Pinned math (implement exactly)
Offset from antenna to target in the ship frame: dx = x_target - x_antenna, dy = y_target - y_antenna.
Heading h (degrees true, clockwise from north):
- dN = dx cos h - dy sin h
- dE = dx sin h + dy cos h
WGS84: a = 6378137.0, f = 1/298.257223563, e2 = f (2 - f). At latitude phi:
- M = a (1 - e2) / (1 - e2 sin^2 phi)^1.5 (meridian radius), N = a / (1 - e2 sin^2 phi)^0.5
- lat' = lat + degrees(dN / M); lon' = lon + degrees(dE / (N cos phi)); wrap lon' to [-180, 180).
Refuse (no output, one warning) for |lat| over 89.5 degrees.

## Test vectors (computed from the pinned formulas; tolerance 1e-9 degrees)
`(lat, lon, heading, dx, dy) -> (lat', lon')`, dN, dE in metres (tolerance 1e-4):
| lat | lon | h | dx | dy | lat' | lon' | dN | dE |
|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 0 | 10 | 0 | 0.000090437 | 0.000000000 | 10.0000 | 0.0000 |
| 0 | 0 | 90 | 10 | 0 | 0.000000000 | 0.000089832 | 0.0000 | 10.0000 |
| 0 | 0 | 0 | 0 | 10 | 0.000000000 | 0.000089832 | 0.0000 | 10.0000 |
| 0 | 0 | 90 | 0 | 10 | -0.000090437 | 0.000000000 | -10.0000 | 0.0000 |
| 45 | -125 | 30 | -20 | 5 | 44.999821649 | -125.000071910 | -19.8205 | -5.6699 |
| 60 | 10 | 225 | 15 | -3 | 59.999885758 | 9.999847934 | -12.7279 | -8.4853 |
Radii: M(0) = 6335439.3273, N(0) = 6378137.0000, M(45) = 6367381.8156, N(45) = 6388838.2901 (1e-4 m).
Also test: lon wrap at 179.99995 with dE = +10 m; heading stale gives no output; |lat| 89.6 refused.

## Failing test first
`contrib/deepsignal/test/geometry/test_geometry.py`: every vector and radius above; wrap; stale heading;
polar refusal; check findings; input untouched.

## Module contract
Docs `contrib/deepsignal/docs/geometry.md` (frame convention drawn as a small text diagram, the roll and
pitch limit stated plainly). Depends on no other module.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/geometry -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/geometry contrib/deepsignal/test/geometry
```

## Scope
Create or change only: `contrib/deepsignal/geometry/**`, `contrib/deepsignal/test/geometry/**`, `contrib/deepsignal/docs/geometry.md`, `contrib/deepsignal/configs/geometry_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

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
Review: a separate fresh Astra session re-derives every vector before merge.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Acceptance tails:
- Open questions:
