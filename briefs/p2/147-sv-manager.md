# Brief: p2-sv-manager (Sound-speed profile manager: ingest, clean, extend, track, advise, export)

- Decision: IDEAS #147 (was "SVP cast tracker", expanded), D-SHIP1, D-FUSE1, from Eugene's 2026-11-18 asks:
  "handle sound-speed" and "use all available good data within reason"; build per D-NIGHT1
- Risk tier: medium (produces files that an operator loads into the multibeam; DeepSignal never loads them)
- Module: exactly one. Branch `deepsignal/p2-sv-manager` from `3b4b76e`
- Lane: `mac` (`gpt-6.2-astra` high: profile math). Mac scratch path `/private/tmp/deepsignal/p2-sv-manager/` only
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 5/5/3
- Depends on: none to build. Optional imports when present: #112 `sound_speed_mackenzie` (XBT casts), #140
  fields (`SV_Alarm`, probe and TSG roles). Model and float profiles (#161) arrive later as extra sources
  in the same profile format

## Goal
Every sound-speed profile on the ship lives in one place: each cast is read, cleaned, extended to full ocean
depth, labelled with its age, place and quality, and turned into the file the multibeam operator loads, and
the watchstander is told plainly when a new cast is needed and why.

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

- Cast formats (all text; parse defensively, never assume column order from position alone):
  - Sea-Bird `.cnv` (Seasave): header lines start `*` or `#`; `# name <i> = <short>: <long>` lines name the
    columns (depth `depSM`, sound speed `svCM` or `svDM`, temperature `t090C`, salinity `sal00`);
    `# bad_flag` gives the missing value; data after `*END*`.
  - Sippican XBT `.EDF` (ASCII export): header `key : value` lines (date, time, latitude, longitude,
    probe type), then depth and temperature columns. XBT has no salinity: SV needs a salinity source (TSG
    surface value held constant, or a climatology profile) and #112; without #112, ingest as
    temperature-only and mark "needs SV conversion".
  - SVP and MVP sondes (Valeport, AML) and generic CSV: a column-mapping profile in YAML
    (`sv_manager/formats/*.yaml`) maps headers to depth, SV, T, S, pressure; add a format by data file.
- Multibeam profile requirements (lead summary; verify by loading a produced file into SIS or its offline
  tools on the pilot ship before anyone relies on it): depth strictly increasing from the surface, extended to
  12000 m, a capped number of points, with position and time in the header.

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/sv_manager/`:
- `Profile` dataclass: `source` (cast id, type), `time`, `lat`, `lon`, `depth_m[]`, `sv_ms[]`, optional
  `t_c[]`, `s_psu[]`, `quality` (0 to 1 with reasons), `max_cast_depth_m`, `extended_from` (what filled
  below the cast), `history` (every processing step with parameters, so a profile can be reproduced).
- Ingest: `ingest(path) -> Profile` for each format; read-only on the input file; a watched drop folder
  `SVManagerReader(Reader)` emits a record per new cast (fields `SVM_NewCast`, `SVM_CastId`).
- Clean (each step recorded in `history`): keep the downcast (depth increasing), drop values outside
  1400 to 1650 m/s, remove spikes (jump over `spike_ms` (5) within `spike_dz_m` (1)), bin to `bin_m`
  (1 m to 100 m, then 5 m, then 25 m below 1000 m: configurable), fill the top from the latest probe or TSG
  surface SV when the cast starts below 3 m (recorded as "surface filled from probe").
- Extend below the cast: with a climatology profile file for the region (CSV depth and SV, prepared ashore;
  #161 builds it), blend from the cast's deepest value into climatology with an exponential taper
  (`offset * exp(-(z - z0) / taper_m)`, taper 200 m); without climatology, extend at the cast's deepest
  gradient to the depth where pressure effect dominates, then by the constant 0.017 s^-1 pressure gradient,
  and mark quality lower. To 12000 m.
- Thin to `max_points` (default 1000; verify the SIS limit on the pilot ship) keeping the shape (largest
  deviation first), report the maximum SV error introduced by thinning.
- Track and advise: `SVMonitorTransform(Transform)` holds the active profile (chosen by the operator in
  config or by the latest export) and emits `SVM_Age_h`, `SVM_Distance_km`, `SVM_SurfaceDiff_ms` (active
  profile's surface SV vs live probe or TSG), `SVM_Quality`, `SVM_CastAdvice` (0 or 1) and
  `SVM_CastAdviceText` naming every reason (age over 12 h, distance over 50 km, surface difference over 2 m/s
  for 10 minutes, #140 alarm active, water depth now deeper than the cast and the extension is climatology).
  Thresholds are kwargs. Record time only.
- Export: `export(profile, fmt, out_dir)` writes `asvp` (Kongsberg SIS and K-Controller), `csv` (depth,
  sound speed), and `template` (a Jinja-free string template file, so Qinsy, Hypack or any other package is
  added by a template a tech saves from a known-good sample). Each file gets a sidecar `.json` with the
  profile's history and hashes. Writes only into the configured export folder, never into the SIS PC.
- Listen-only rule: loading a profile into the multibeam is the operator's action. A later direct push is a
  tier A write (#154) and needs Eugene's sign-off; not in this brief.
- UHDAS: no export. Ocean Surveyor phased-array velocities need only the transducer sound speed, which #145
  checks; say this in the docs.

## Failing test first
`contrib/deepsignal/test/sv_manager/test_sv_manager.py`: each format parsed from small fixtures written in
the test folder (including a `.cnv` with a bad flag and an upcast); cleaning steps each on their own
fixture; surface fill; extension with and without climatology (continuity at the join, monotonic depth, to
12000 m); thinning error bound; advice reasons each alone and together; asvp and csv golden files; template
export; sidecar history reproduces the profile; replay determinism; XBT without #112 marked, with #112 when
importable.

## Module contract
Docs `contrib/deepsignal/docs/sv_manager.md`: the workflow on watch (cast, drop file, review, export, load
in SIS), every advice reason, the "verify the asvp on your SIS before relying on it" warning. Sample config
`contrib/deepsignal/configs/sv_manager_demo.yaml`. Depends on no other module.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/sv_manager -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/sv_manager contrib/deepsignal/test/sv_manager
```

## Scope
Create or change only: `contrib/deepsignal/sv_manager/**`, `contrib/deepsignal/test/sv_manager/**`,
`contrib/deepsignal/docs/sv_manager.md`, `contrib/deepsignal/configs/sv_manager_*.yaml`, and empty
`__init__.py` files where missing. Everything else is read-only.

## Usability (anything a tech sees or edits)
Answer each line of desk `docs/USABILITY.md` in the report, or N/A with a reason. Advice text example:
"New cast advised: profile is 14 h old (limit 12 h) and surface sound speed has moved 3.1 m/s from the
cast (limit 2.0). Last cast CTD 017 at 33.2 N 118.9 W."

## Trust boundaries and data integrity
Cast files are hand-made and untrusted: bounded reads, no `eval`, `yaml.safe_load` only. Never modify an
input file. Every derived value carries its history. Missing data is shown as missing, never invented
beyond the documented extension, which is always labelled.

## Non-goals and banned
No downloads (climatology, Argo and models arrive as files from #161). No writes to the multibeam, SIS or
any instrument. No core changes, no new dependency, no refactors outside Scope. No loosened, skipped or
deleted tests, no swallowed errors. No writes, deletes or moves in `/private/tmp` outside `/private/tmp/deepsignal/`.

## Stop rule
No code change needed: stop and report. Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Acceptance tails:
- Open questions:
