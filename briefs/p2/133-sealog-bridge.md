# Brief: p2-sealog-bridge (Sealog bridge: quality events and quality aux data)

- Decision: IDEAS #133, from Eugene's 2026-11-18 asks (config assist, sensor init, ecosystem and compression); build per D-NIGHT1
- Risk tier: medium
- Module: exactly one. Branch `deepsignal/p2-sealog-bridge` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 4/5/3
- Depends on: reads QARTOD flag fields (`<field>_QC`, `_reason`) from origin/deepsignal/qartod-flags docs; #110 flow state and #130 init audit are optional inputs

## Goal
Science sees data-system quality in the event log they already use: a flagged sensor, a stale feed, the
flowthrough going off, an instrument re-initialized, each becomes a Sealog event, and every event a
watchstander logs carries the quality state of the relevant sensors at that moment.

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
- OceanDataTools sources were read at these commits (read-only; D-UPSTREAM0: nothing is sent to
  OceanDataTools): openvdm `5d163fc` (2.17.0, 2026-11-12), sealog-server `46ccbf0` (2.4.9). You have no
  network: the facts below are the interface. Do not guess beyond them; list anything you needed but
  lacked under open questions.
- Core OpenRVDAS `SealogWriter` (fork `dev`, `logger/writers/sealog_writer.py`) posts event dicts to the
  Sealog API with a JWT and a YAML `config_file` keyed by `data_id` (`event_value`, `event_author`,
  `event_free_text`, `event_options`, `field_map`, `_default`). Reuse it: this module only produces the
  records it consumes. Do not write another HTTP client for events.
- Sealog event shape (`lib/validations.js`): `event_author`, `ts` (ISO), `event_value`, `event_options`
  (list of `{event_option_name, event_option_value}`), `event_free_text`.
- Sealog aux data shape: `{event_id, data_source (1-100 chars), data_array: [{data_name, data_value,
  data_uom?}]}`, POST `/api/v1/event_aux_data`. Sealog's own inserters (`misc/sealog_aux_data_inserter*.py`)
  listen on the Sealog websocket for new events and add aux data; follow that pattern.
- Quality fields: `<field>_QC` with QARTOD values 1 pass, 2 not evaluated, 3 suspect, 4 fail, 9 missing,
  and `<field>_QC_reason` for 3 and 4 (see `git show origin/deepsignal/qartod-flags:contrib/deepsignal/docs/qartod_flags.md`).

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/sealog_bridge/`:
- `QualityEventTransform`: input records with `_QC` fields (and optional freshness, flow state, init audit
  records). Emits one Sealog-ready record (data_id `deepsignal_quality`) only on a CHANGE: a field's flag
  moves between {1,2} and {3,4,9}, a stream goes stale or recovers (`stale_after_s`, default 30), flow
  state changes, an init sequence fails or recovers. Debounce: the new state must hold `hold_s` (default
  10 s) before an event; at most `max_per_hour` (default 30) per field, then one summary event. Event value
  `DEEPSIGNAL`; options `kind` (qc, stale, flow, init), `field`, `from`, `to`, `reason`.
- `configs/sealog_bridge_writer.yaml`: the `SealogWriter` config_file for `deepsignal_quality`.
- `configs/sealog_event_template.json`: a Sealog event template for `DEEPSIGNAL` so humans can filter it.
- `aux_inserter.py`: `build_aux(event, snapshot, fields) -> dict` (pure, tested) and a small runner that
  listens to the Sealog websocket for new events (any websocket client already in core requirements; else
  poll `GET /api/v1/events?startTS=` every 5 s) and posts one aux record with `data_source:
  "deepsignal_quality"` holding each configured field's value, `_QC` flag, flag name and age in seconds,
  read from the CachedDataServer. It never edits or deletes an event. Token from an env var only.

## Failing test first
`contrib/deepsignal/test/sealog_bridge/test_bridge.py`: flag change emits one event after hold; flapping
inside hold emits none; rate cap and summary; stale and recover; flow and init kinds; output passes through
core `SealogWriter`'s record handling with a fake HTTP layer (if `SealogWriter` is not on the contrib base,
assert against the documented shape); `build_aux` exact output; token never logged.

## Module contract
Docs `contrib/deepsignal/docs/sealog_bridge.md`: setup in five steps, event examples, how to filter in the
Sealog client. A lead-run check against a Sealog 2.4.9 demo server happens outside the sandbox.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/sealog_bridge -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/sealog_bridge contrib/deepsignal/test/sealog_bridge
```

## Scope
Create or change only: `contrib/deepsignal/sealog_bridge/**`, `contrib/deepsignal/test/sealog_bridge/**`, `contrib/deepsignal/docs/sealog_bridge.md`, `contrib/deepsignal/configs/sealog_bridge_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

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
