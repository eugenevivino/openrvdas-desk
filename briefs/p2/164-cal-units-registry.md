# Brief: p2-cal-units-registry (Calibration and units registry with effective dates)

- Decision: IDEAS #164, from Eugene's 2026-11-18 asks (config assist, sensor init, ecosystem and compression); build per D-NIGHT1
- Risk tier: high
- Module: exactly one. Branch `deepsignal/p2-cal-units-registry` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 5/5/3
- Depends on: extends #7 (designed) and links #52 instrument history ids; #118 doc store holds certificates

## Goal
There is one authoritative place for each sensor's coefficients and units: effective dates, certificate,
who changed them and which outputs depend on them. Wrong coefficients or units are caught before they reach
SAMOS or R2R. Evidence: desk `docs/PAIN-POINTS.md` (Deep Research, 2026-11-18); mapping in `docs/PAIN-POINTS-MAP.md`. (pain points 1, 9; opportunity "Calibration/units registry"; the OpenRVDAS request
for calibration storage).

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
- Raw is never changed: a calibration applies only to derived fields, and the record keeps the version
  used.

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/cal_registry/`:
- `registry.yaml`, one entry per calibration:
  - Fields: `sensor_id`, `serial`, `field`, `units_in`, `units_out`, `form` (`linear`, `polynomial` up to
    order 5, `steinhart_hart`, `table` with linear interpolation), `coefficients`, `valid_from`,
    `valid_to?`, `certificate` (path or #118 id), `entered_by`, `checked_by?`, `note`.
  - Overlapping validity for the same sensor and field is an error.
- `CalibrationTransform`: adds `<field>_cal` and `<field>_cal_version` using the entry valid at the
  record time. With no valid entry it adds nothing and sets `<field>_cal_state: none` (never guesses).
- Units: a small table of allowed units per quantity (temperature degC, K; conductivity S/m, mS/cm;
  pressure dbar, hPa, kPa; speed m/s, kn; and so on). The check flags fields whose observed range implies
  the wrong unit, for example "conductivity values about 40 look like mS/cm, but units say S/m". This is
  a warning, never a change.
- `affected(sensor_id) -> list`: derived outputs depending on the sensor, from the cruise configs.
- Changes are recorded through #163 when it is importable, else into its own append-only log.
  `checked_by` must differ from `entered_by` for the entry to show as verified.
- Pinned math: linear `y = a0 + a1 x`; polynomial `sum ai x^i`; Steinhart-Hart
  `1/T = A + B ln R + C (ln R)^3` with T in K. Test vectors: A = 1.129148e-3, B = 2.34125e-4,
  C = 8.76741e-8, R = 10000 ohm gives T = 298.15 K within 0.01 K. Check that vector with the formula
  before relying on it, and report it if it differs.

## Failing test first
`contrib/deepsignal/test/cal_registry/test_cal_registry.py`:
- Each form.
- The Steinhart-Hart vector.
- Effective-date selection at boundaries.
- An overlap error.
- No entry adds nothing.
- The raw field is untouched.
- The unit-suspicion warning.
- Affected outputs from NBP1406 configs.
- The verified rule.

## Module contract
Docs `contrib/deepsignal/docs/cal_registry.md`.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/cal_registry -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/cal_registry contrib/deepsignal/test/cal_registry
```

## Scope
Create or change only: `contrib/deepsignal/cal_registry/**`, `contrib/deepsignal/test/cal_registry/**`, `contrib/deepsignal/docs/cal_registry.md`, `contrib/deepsignal/configs/cal_registry_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

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
