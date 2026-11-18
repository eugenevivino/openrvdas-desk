# Brief: p2-runbooks (Alarm-linked vessel runbooks)

- Decision: IDEAS #167, from Eugene's 2026-11-18 asks (config assist, sensor init, ecosystem and compression); build per D-NIGHT1
- Risk tier: low
- Module: exactly one. Branch `deepsignal/p2-runbooks` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 5/2/2
- Depends on: stream ids from #162; #118 documents and #52 history linked by id; console and MCP read its JSON

## Goal
Every alarm opens the vessel's own runbook for that stream: expected wiring, endpoint, baud and format,
power source, spare location, last known fix, likely causes in order and escalation. A new tech knows what
the last one knew. Evidence: desk `docs/PAIN-POINTS.md` (Deep Research, 2026-11-18); mapping in `docs/PAIN-POINTS-MAP.md`. (pain points 7, 10, 15; opportunity "Integrated operator runbooks").

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
Package `contrib/deepsignal/runbooks/`:
- One Markdown file per stream, `runbooks/<stream>.md`, with YAML front matter:
  - Fields: `stream`, `endpoint`, `baud`, `format`, `power`, `spare_location`, `escalation`, `causes`
    (ordered, each with `check` and `fix`), `owner`.
  - Free text below the front matter.
- `load_all(dir) -> dict` and `for_alarm(stream, stage) -> dict`, which returns the causes relevant to the
  failing stage (each cause tagged with stages it applies to).
- `record_fix(stream, what, who)`: appends to a `fixes.jsonl` beside the runbook. The latest three show as
  "Last fixes". This is the only write path.
- `draft(stream, cruise_dict, history?)`: pre-fills a new runbook from the cruise definition (endpoint, baud,
  device type) and #52 history (serial, location), marked DRAFT until an owner edits it.
- `check`: flags missing runbooks for configured streams, missing owners, stale drafts (over 30 days) and
  causes without a check.
- CLI: `draft`, `check`, `show <stream> [--stage X]`. Setup engine: `for_alarm` is pure and JSON-safe.

## Failing test first
`contrib/deepsignal/test/runbooks/test_runbooks.py`:
- Front matter parse.
- Stage filtering.
- Fix append and latest three.
- Drafts from NBP1406.
- Check findings.
- A malicious Markdown string stays text (no HTML rendering here).

## Module contract
Docs `contrib/deepsignal/docs/runbooks.md` with one complete example runbook (TSG).

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/runbooks -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/runbooks contrib/deepsignal/test/runbooks
```

## Scope
Create or change only: `contrib/deepsignal/runbooks/**`, `contrib/deepsignal/test/runbooks/**`, `contrib/deepsignal/docs/runbooks.md`, `contrib/deepsignal/configs/runbooks_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only. Example runbooks go in `contrib/deepsignal/configs/runbooks_example/`.

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
