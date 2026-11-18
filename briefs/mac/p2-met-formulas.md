Mac lane job (rule 8, rule 27, rule 28). Launch through `~/bin/ds-codex` only, one DeepSignal job per Mac, RAM rule applies (hold if free RAM under 4 GB or swap over 3.8 GB).

Model and effort, named explicitly: `KALON_ALLOW_ASTRA=1 ~/bin/ds-codex -m gpt-6.2-astra -c model_reasoning_effort=high` (set KALON_ALLOW_ASTRA only for this job).
Scratch: `/private/tmp/deepsignal/p2-met-formulas/` only (clone in `repo/`, `gc.auto=0`, `maintenance.auto=false`). Never write outside it; never touch `/private/tmp/kalon`.
Review: a separate fresh Astra session, read-only, re-derives every pinned test vector before anything merges.

You are making ONE small, test-first change to OpenRVDAS core on Eugene's own fork (fork only, never upstream). Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-met-formulas` from commit `1a6f1ed` (fork `dev`) (if `deepsignal/p2-met-formulas` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-met-formulas`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: use `python3.12` if it exists, otherwise `python3` (3.11 or newer). Install the repository's Python requirements if pytest cannot import `logger`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. Add no dependency. Read CLAUDE.md and OPERATIONS.md first. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-met-formulas (Met and seawater formula library (core fix))

- Decision: D-PARITY1, IDEAS #112 (Eugene approved building #104-#124, 2026-11-18)
- Risk tier: high
- Module: exactly one. Branch `deepsignal/p2-met-formulas` from `1a6f1ed`
- Lane: `mac`: `gpt-6.2-astra`, `model_reasoning_effort=high`, `KALON_ALLOW_ASTRA=1` (math; Eugene rule 2026-11-18)
- Fresh session, under 40 turns
- Upstream home: core, fork only (D-ARCH6)
- Value (techs/science/shore): 3/4/3
- Depends on: none
- Mac scratch path: `/private/tmp/deepsignal/p2-met-formulas/` only (rule 28)

## Goal
Dew point, wet bulb, sea-level pressure, salinity, density and sound speed come from one tested library,
callable by name in `ComputedFieldsTransform` expressions, instead of hand-typed formulas per ship.

## Background facts (do not re-derive)
- On fork `dev`, `logger/transforms/computed_fields_transform.py` evaluates safe expressions with a
  whitelisted `SAFE_FUNCTIONS` table, and a subclass may widen its `FUNCTIONS` table (see the comment near
  line 197 and `validate_expression(..., functions=...)`). Use that; do not change the base class.

## Design (lead decisions)
- `logger/utils/met_formulas.py`: plain functions, floats in, float out, no numpy. Out-of-range inputs
  return `None` (never raise inside a running logger) and the docstring states the valid range.
- `logger/transforms/met_computed_fields_transform.py`: `MetComputedFieldsTransform(ComputedFieldsTransform)`
  with `FUNCTIONS = {**ComputedFieldsTransform.FUNCTIONS, 'dew_point': ..., ...}`. A `None` result leaves
  the output field absent for that record.
- Optional TEOS-10: if `gsw` imports, also expose `gsw_SA` and `gsw_CT` wrappers; tests for them skip with
  reason "gsw not installed". Never add `gsw` as a dependency.

## Pinned formulas (implement exactly)
1. `sat_vapor_pressure(t_c)` hPa, Alduchov and Eskridge (1996) Magnus form:
   es = 6.1094 exp(17.625 t / (t + 243.04)). Valid -40 to 50 degC.
2. `dew_point(t_c, rh_pct)` degC: g = ln(rh/100) + 17.625 t / (243.04 + t); td = 243.04 g / (17.625 - g).
   Valid rh in (0, 100], t -40 to 50.
3. `wet_bulb(t_c, rh_pct)` degC, Stull (2011):
   tw = t atan(0.151977 (rh + 8.313659)^0.5) + atan(t + rh) - atan(rh - 1.676331)
        + 0.00391838 rh^1.5 atan(0.023101 rh) - 4.686035. Valid rh 5 to 99, t -20 to 50.
4. `sea_level_pressure(p_hpa, t_c, h_m)` hPa: p (1 - 0.0065 h / (t + 0.0065 h + 273.15))^-5.257.
   Valid h 0 to 100 m (ship barometer heights).
5. `salinity_pss78(c_ratio, t90_c, p_dbar)` PSU, UNESCO 1983 (Tech. Paper 44). Input temperature is
   ITS-90; convert t68 = 1.00024 t90 first. With t = t68, R = c_ratio:
   rt = c0 + c1 t + c2 t^2 + c3 t^3 + c4 t^4, c = [0.6766097, 2.00564e-2, 1.104259e-4, -6.9698e-7, 1.0031e-9];
   Rp = 1 + p (e1 + e2 p + e3 p^2) / (1 + d1 t + d2 t^2 + (d3 + d4 t) R),
   e = [2.070e-5, -6.370e-10, 3.989e-15], d = [3.426e-2, 4.464e-4, 4.215e-1, -3.107e-3];
   Rt = R / (Rp rt);
   S = sum_i a_i Rt^(i/2) + (t - 15) / (1 + k (t - 15)) sum_i b_i Rt^(i/2), i = 0..5,
   a = [0.0080, -0.1692, 25.3851, 14.0941, -7.0261, 2.7081], b = [0.0005, -0.0056, -0.0066, -0.0375,
   0.0636, -0.0144], k = 0.0162. Valid S 2 to 42.
   Also `conductivity_ratio(c_ms_cm)` = c / 42.914.
6. `density_eos80_surface(s, t_c)` kg/m3, UNESCO 1981 one-atmosphere (t on IPTS-68 as in the source; state
   this in the docstring):
   rho_w = 999.842594 + 6.793952e-2 t - 9.095290e-3 t^2 + 1.001685e-4 t^3 - 1.120083e-6 t^4 + 6.536332e-9 t^5;
   rho = rho_w + s (0.824493 - 4.0899e-3 t + 7.6438e-5 t^2 - 8.2467e-7 t^3 + 5.3875e-9 t^4)
         + s^1.5 (-5.72466e-3 + 1.0227e-4 t - 1.6546e-6 t^2) + 4.8314e-4 s^2.
   `sigma_t(s, t_c)` = rho - 1000.
7. `sound_speed_mackenzie(t_c, s, depth_m)` m/s, Mackenzie (1981):
   c = 1448.96 + 4.591 t - 5.304e-2 t^2 + 2.374e-4 t^3 + 1.340 (s - 35) + 1.630e-2 D + 1.675e-7 D^2
       - 1.025e-2 t (s - 35) - 7.139e-13 t D^3. Valid t 2 to 30, s 25 to 40, D 0 to 8000.

## Test vectors (published check values marked *; others computed from the pinned formulas)
| Function | Inputs | Expected | Tolerance |
|---|---|---|---|
| salinity_pss78 * | R=1.888091, t68=40 (so t90 = 40/1.00024), p=10000 | 40.0000 | 1e-4 |
| salinity_pss78 * | R=1, t68=15 (t90 = 15/1.00024), p=0 | 35.0000 | 1e-4 |
| salinity_pss78 | R=1, t90=15, p=0 | 34.9968 | 1e-4 |
| sound_speed_mackenzie * | t=25, s=35, D=1000 | 1550.744 | 1e-3 |
| density_eos80_surface * | s=0, t=5 | 999.96675 | 1e-5 |
| density_eos80_surface * | s=35, t=5 | 1027.67547 | 1e-5 |
| density_eos80_surface | s=35, t=25 | 1023.34306 | 1e-5 |
| sat_vapor_pressure | t=20 | 23.3344 | 1e-4 |
| dew_point | t=20, rh=50 | 9.2611 | 1e-4 |
| dew_point | t=30, rh=80 | 26.1709 | 1e-4 |
| dew_point | t=10, rh=100 | 10.0000 | 1e-4 |
| wet_bulb * (Stull's example, 13.7) | t=20, rh=50 | 13.6993 | 1e-4 |
| wet_bulb | t=30, rh=80 | 27.1297 | 1e-4 |
| sea_level_pressure | p=1000, t=15, h=20 | 1002.3740 | 1e-4 |
| sea_level_pressure | p=1013.25, t=20, h=0 | 1013.2500 | 1e-6 |

Out-of-range cases return None: dew_point rh=0, wet_bulb rh=2, salinity R=0, mackenzie D=9000.

## Failing test first
`test/logger/utils/test_met_formulas.py` (every row above, the None cases) and
`test/logger/transforms/test_met_computed_fields_transform.py` (an expression `dew_point(AirTemp, RH)`
produces the field; unknown function still rejected with the base class message; None result omits the
field; base `ComputedFieldsTransform` still rejects `dew_point`).

## Acceptance (exact commands, from repo root, Linux)
```
python3.12 -m pytest test/logger/utils/test_met_formulas.py -v
```
```
python3.12 -m pytest test/logger/transforms/test_met_computed_fields_transform.py -v
```
```
python3.12 -m flake8 --config .flake8 logger/utils/met_formulas.py logger/transforms/met_computed_fields_transform.py test/logger/utils/test_met_formulas.py test/logger/transforms/test_met_computed_fields_transform.py
```
```
python3.12 -m pytest test/logger -q
```

## Scope
New files only: the four listed above, plus `docs/met_formulas.md` (each function, units, valid range,
source citation, an example logger config). No change to existing files.

## Trust boundaries and data integrity
Existing behavior and output bytes of every current config stay identical unless the new option is set.
Default values of existing classes do not change.

## Non-goals and banned
No upstream PR or issue (D-ARCH6, fork only). No refactors, renames or formatting outside the listed
files. No new dependency. No loosened, skipped or deleted tests, no swallowed errors, no sleeps for test
ordering.

## Stop rule
No code change needed: stop and report. Two fix rounds still red: stop and report.
Review: a separate fresh Astra session re-derives every vector above from the cited sources before merge.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Acceptance tails:
- Open questions:
