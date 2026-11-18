# Brief: p2-event-timeline (Unified event timeline)

- Decision: IDEAS #168, from Eugene's 2026-11-18 asks (config assist, sensor init, ecosystem and compression); build per D-NIGHT1
- Risk tier: low
- Module: exactly one. Branch `deepsignal/p2-event-timeline` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 4/5/4
- Depends on: reads #162 transitions, #163 history, #130 init audit, #137 EEZ audit, #167 fixes and Sealog events (#133) when present

## Goal
One synchronized timeline holds config changes, alarms and recoveries, instrument init, EEZ crossings,
overrides, maintenance fixes, science events and operator notes. The question "what changed just before
this went bad" has one answer. Evidence: desk `docs/PAIN-POINTS.md` (Deep Research, 2026-11-18); mapping in `docs/PAIN-POINTS-MAP.md`. (pain points 2, 10, 15; opportunity "Event annotation timeline";
the OpenRVDAS request for one-file state logging).

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
Package `contrib/deepsignal/timeline/`:
- Adapters (each optional, enabled by a path):
  - JSONL tails of #162 transitions, #163 `history.jsonl`, #130 audit, #137 audit and #167 `fixes.jsonl`
  - OpenRVDAS `stderr:logger:*` and `status:logger_status` changes from the CDS
  - Sealog events through a read-only GET (token from env)
  - operator notes (`note(text, who)`)
- `timeline.jsonl` (append-only): each entry is `{t, kind, source, subject, summary, ref}` with a
  stable id (sha256 of source plus ref) so re-reading never duplicates.
- `query(start, end, kinds?, subject?) -> list` and `around(t, minutes=30)`: the "what changed before"
  view, which ranks config changes and transitions first.
- `digest(day) -> dict`: the daily summary UHDAS-style (transitions, open problems, config changes, EEZ,
  fixes) as JSON and plain text, for #28 and email by an existing writer.

## Failing test first
`contrib/deepsignal/test/timeline/test_timeline.py`:
- Each adapter on fixtures.
- Dedupe on re-read.
- Time ordering across sources with different clocks (sorted by `t`, ties by source).
- `around` ranking.
- Digest content.
- Append-only.

## Module contract
Docs `contrib/deepsignal/docs/timeline.md`.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/timeline -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/timeline contrib/deepsignal/test/timeline
```

## Scope
Create or change only: `contrib/deepsignal/timeline/**`, `contrib/deepsignal/test/timeline/**`, `contrib/deepsignal/docs/timeline.md`, `contrib/deepsignal/configs/timeline_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

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
