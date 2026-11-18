You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-seismic-shot-qc` from commit `3b4b76e` (the contrib master tree; it is in this fork's history, for example `git merge-base origin/deepsignal/vector-wind origin/deepsignal/instrument-history`) (if `deepsignal/p2-seismic-shot-qc` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-seismic-shot-qc`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML is already an OpenRVDAS dependency; add no other dependency. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-seismic-shot-qc (Seismic shot and source QC, listen-only)

- Decision: IDEAS #158, D-SHIP1, from Eugene's 2026-11-18 ask: "handle seismic (digibird, geoeel, hotshot)"; build per D-NIGHT1
- Risk tier: low (parses text streams already captured by OpenRVDAS; writes new fields and files only)
- Module: exactly one. Branch `deepsignal/p2-seismic-shot-qc` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 4/5/3
- Depends on: none to build. In use: OpenRVDAS nav fields (GGA or Seapath), a time source (ZDA), and the
  gun controller's shot log arriving as text on serial or UDP

## Goal
During a seismic line, the watchstander sees every shot checked as it happens: did it fire on time, did
each gun fire within its timing window, is the shot interval or spacing as planned, where exactly was the
ship at fire time, and how many shots were missed, and gets a standard shot navigation file at the end of
the line without hand work.

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

- Gun controllers (Real Time Systems HotShot, Seamap GunLink, Sercel and others) emit a per-shot ASCII
  record (shot number, fire time, per-gun timing error, sometimes pressure) on serial or UDP. Those formats
  are vendor documents, not public, and differ by firmware: so this module does NOT hard-code any vendor
  format. Core OpenRVDAS already parses text with device definitions (`ParseTransform` plus YAML device
  files) and regexes (`RegexParseTransform`). This module consumes the parsed fields by configured names.
- Public formats used here: NMEA 0183 time and position (already parsed by core), IOGP P1/11 (public
  positioning data exchange format, published by IOGP; the builder may not fetch it: use only the subset
  described in Design and say so in the docs), SEG-D and SEG-Y headers are out of scope for v1.

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/seismic/`:
- Example device definitions (not real vendor formats; clearly labelled "template, replace with the
  ship's capture") in `contrib/deepsignal/configs/seismic_shotlog_template.yaml`, showing a tech how to map
  a shot log to the field names below with core `ParseTransform`.
- `ShotQCTransform(Transform)`: kwargs map roles to field names: `shot_number`, `fire_time` (UNIX s, or a
  time-of-day string plus a date source), `gun_errors` (list of per-gun timing-error fields, ms),
  `lat`, `lon` (nav fields), `nav_time` (optional); thresholds: `gun_tolerance_ms` (default 1.0),
  `interval_s` (planned shot interval, optional), `spacing_m` (planned distance, optional),
  `interval_tolerance_pct` (5), `nav_max_gap_s` (2). Prefix `SHOT`.
- Keeps a short nav history (last 120 s) and, for each shot record, emits: `SHOT_Number`, `SHOT_FireTime`,
  `SHOT_Lat`, `SHOT_Lon` (linear interpolation in time between the two nav fixes around fire time; empty
  and `SHOT_NavGap` set when the gap exceeds `nav_max_gap_s`; never extrapolate), `SHOT_Interval_s`,
  `SHOT_Spacing_m` (great-circle distance from the previous shot; use the haversine formula with a fixed
  Earth radius 6371008.8 m, documented as approximate), `SHOT_GunsOut` (count over tolerance),
  `SHOT_WorstGun_ms`, `SHOT_Missed` (gaps in shot numbers), `SHOT_ClockOffset_s` (fire time minus record
  timestamp), `SHOT_Alarm`, `SHOT_AlarmText`. Persistence and hysteresis on alarms as in #140 and #141
  (record time, never wall clock).
- `P111Writer(Writer)`: writes one shot-position file per line in a documented minimal P1/11-style CSV
  subset (header block with CRS, units, ship name from config; one record per shot with shot number, time,
  lat, lon). Mark it "P1/11 subset, verify with the processing team before delivery" in the header and docs.
- Listen-only: the module never sends anything to a gun controller, streamer controller or nav system.

## Failing test first
`contrib/deepsignal/test/seismic/test_shot_qc.py`: on-time shots with no alarm; one gun out of tolerance;
missed shot numbers; interval and spacing off plan; nav interpolation at fire time with a hand-computed
expected position; nav gap gives empty position, never extrapolation; clock offset; alarm persistence and
clear; replay determinism; `None`, list, DASRecord and dict inputs; P1/11 writer output against a golden file
written by hand in the test folder; the template device file parses its own sample line with core
`ParseTransform`.

## Module contract
Docs `contrib/deepsignal/docs/seismic.md`: what is checked and why, how to capture and map the ship's
shot log, the listen-only rule, what P1/11 subset is written. Depends on no other module.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/seismic -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/seismic contrib/deepsignal/test/seismic
```

## Scope
Create or change only: `contrib/deepsignal/seismic/**`, `contrib/deepsignal/test/seismic/**`,
`contrib/deepsignal/docs/seismic.md`, `contrib/deepsignal/configs/seismic_*.yaml`, and empty `__init__.py`
files where missing. Everything else is read-only.

## Usability (anything a tech sees or edits)
Answer each line of desk `docs/USABILITY.md` in the report, or N/A with a reason. Alarm text names the
shot, the gun or measure, the value, the limit and what to check ("Shot 1042: gun 3 fired 2.4 ms late (limit
1.0 ms), third shot in a row. Check gun 3 timing in the controller.").

## Trust boundaries and data integrity
Inputs are untrusted: reject NaN, inf, non-numeric; bound the nav history. Never change incoming fields;
only add the fields above and write the new file. Missing nav or time is shown as missing, never guessed.

## Non-goals and banned
No vendor format hard-coded, no streamer or bird decoding (that is #159), no protected-species logic (that
is #160). No writes to any seismic system. No core changes, no new dependency, no refactors outside Scope.
No loosened, skipped or deleted tests, no swallowed errors.

## Stop rule
No code change needed: stop and report. Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Acceptance tails:
- Open questions:
