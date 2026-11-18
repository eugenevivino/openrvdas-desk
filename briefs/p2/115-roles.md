# Brief: p2-roles (Roles and access policy (engine only))

- Decision: D-PARITY1, IDEAS #115 (Eugene approved building #104-#124, 2026-11-18)
- Risk tier: high
- Module: exactly one. Branch `deepsignal/p2-roles` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 3/3/4
- Depends on: none to build; #105 REST, #116 release policy and console pages adopt it later
- Needs Eugene: How people log in is Eugene's call: reuse the Django accounts OpenRVDAS already has, the FastAPI JWT backend, or a reverse proxy (e.g. nginx basic auth or SSO). This task builds only the role model and policy check, which all three can use; it ships no login.

## Goal
One small, tested rulebook decides what a public visitor, a scientist, a technician and an admin may see
and do, so every DeepSignal page and API asks the same question and gets the same answer.

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
Package `contrib/deepsignal/roles/`:
- Roles, ordered: `public` < `science` < `tech` < `admin`. A higher role has everything a lower one has.
- Policy YAML (example `contrib/deepsignal/configs/roles_example.yaml`):
  ```yaml
  actions:                          # action -> lowest role allowed
    view.live: public
    view.health: science
    download.binned: science
    download.raw: tech
    corrections.approve: tech       # used by #56 ledger
    config.deploy: admin
  users:                            # optional local mapping; real identity comes from the login layer
    alice: tech
  default_role: public
  ```
- `Policy.load(path)`; `policy.can(role, action) -> bool`; unknown action returns False and logs once
  (fail closed); unknown role is a load error.
- `policy.role_for(identity)`: from `users`, else `default_role`. Identity strings come from the login
  layer, never from a request parameter. The docs say this in bold.
- `explain(policy)` prints a plain table of actions by role.
- No passwords, tokens, sessions or crypto in this module.

## Failing test first
`contrib/deepsignal/test/roles/test_policy.py`: ordering; every action in the example; unknown action is
False; unknown role fails load with a plain message; default role; explain output; a policy that grants
`config.deploy` to `public` loads but `check()` warns "admin action open to public".

## Module contract
Docs `contrib/deepsignal/docs/roles.md`: the role ladder, how a page or API calls `can()`, and the three
login options as an open decision. Depends on no other module.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/roles -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/roles contrib/deepsignal/test/roles
```

## Scope
Create or change only: `contrib/deepsignal/roles/**`, `contrib/deepsignal/test/roles/**`, `contrib/deepsignal/docs/roles.md`, `contrib/deepsignal/configs/roles_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

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
Review: high risk tier. A separate fresh reviewer checks every fail-closed path before merge.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Acceptance tails:
- Open questions:
