# Brief: p2-release-policy (Data release policy (privacy, EEZ hold-back))

- Decision: D-PARITY1, IDEAS #116 (Eugene approved building #104-#124, 2026-11-18)
- Risk tier: high
- Module: exactly one. Branch `deepsignal/p2-release-policy` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 3/4/4
- Depends on: core `GeofenceTransform` (exists) or any boolean field for "inside EEZ"; #115 roles later decides who sees what
- Needs Eugene: The policy content (which fields are restricted, what EEZ agreements require) is ship and cruise specific. The module ships an example only; Eugene or the ship writes the real policy.

## Goal
Data leaving the ship (shore stream, public pages, ERDDAP) follows a written release policy, including
holding back listed fields inside another nation's EEZ, while raw logging on the ship is never affected.

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
- Core `GeofenceTransform` (on the base, `logger/transforms/geofence_transform.py`) already detects
  entering and leaving an EEZ polygon. This module does not repeat that geometry: it reads a boolean field.

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/release_policy/`, class `ReleasePolicyTransform` in `transform.py`.
- Placed ONLY in front of outbound writers (shore, public). The docs must say in bold: never put it in
  front of the raw logfile writer.
- Policy YAML (example `contrib/deepsignal/configs/release_policy_example.yaml`):
  ```yaml
  audience: public              # this instance's audience: public | science | shore_ops
  levels:                       # field glob -> lowest audience allowed
    'S330*': public
    'TSG_*': science
    'Knud*': shore_ops
  default_level: science        # fields matching no glob
  eez:
    inside_field: eez_inside    # boolean field set by GeofenceTransform or by hand
    hold_back: ['TSG_*', 'Knud*', 'S330*']   # withheld while inside, for every audience
    position_fields: ['S330Latitude', 'S330Longitude']
    position_rounding_deg: 0.1  # positions still shown inside the EEZ, rounded
  ```
- Audience order: public < science < shore_ops. A field passes if the instance audience is at or above the
  field's level.
- EEZ: while the last seen `inside_field` is true, drop `hold_back` fields; round `position_fields` to
  `position_rounding_deg`. Unknown EEZ state (never seen the field) counts as INSIDE: fail closed, and log
  one warning saying so.
- Output record keeps timestamp and adds `release_policy` = policy file sha256 short form, so any shore
  file can be traced to the policy that shaped it. Drops never raise; a record left with no fields is
  dropped (returns None).
- `python -m contrib.deepsignal.release_policy explain <policy> <field>` prints in plain English who can
  see the field, inside and outside the EEZ.

## Failing test first
`contrib/deepsignal/test/release_policy/test_transform.py`: audience ordering; glob precedence (first
match wins, in file order); default level; EEZ inside, outside, unknown (fail closed); position rounding;
record emptied becomes None; policy hash field; explain output; config errors (unknown audience, bad glob).

## Module contract
Docs `contrib/deepsignal/docs/release_policy.md` with the warning, an example placement in a logger config,
and what it does NOT do (legal advice, deleting data, retention). Depends on no other module.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/release_policy -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/release_policy contrib/deepsignal/test/release_policy
```

## Scope
Create or change only: `contrib/deepsignal/release_policy/**`, `contrib/deepsignal/test/release_policy/**`, `contrib/deepsignal/docs/release_policy.md`, `contrib/deepsignal/configs/release_policy_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

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
Review: high risk tier. A separate fresh reviewer checks the fail-closed paths before merge.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Acceptance tails:
- Open questions:
