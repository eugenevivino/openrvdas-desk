# Brief: <area>-<slug>

Copy to `briefs/<area>-<slug>.md`. A builder reads only this file, AGENTS.md,
and the files listed under Scope. If it needs more, the brief was too vague:
stop and ask the lead.

- Decision: D-<id> this implements
- Risk tier: low | medium | high (OPERATING-SYSTEM section 6)
- Module: exactly one (rule 24). Branch `deepsignal/<module>` for overlay work, `<area>/<slug>` for core fixes
- Mac scratch path: `/private/tmp/deepsignal/<module>/` only (docs/CODEX.md rule 1b)
- Base: fork `dev` (core) or `contrib/master` (overlay) at <sha>
- Model and effort: <tier from docs/CODEX.md section 2>, fresh session, under 40 turns
- Upstream home: core | openrvdas_contrib | separate package | fork only

## Goal
One sentence a crew member would recognize.

## Failing test first
Test file and test names. It must fail on the base sha before any code
changes. Paste the RED output into the result.

## Module contract (overlay work)
Own tests, a sample logger config that runs the module alone, a README
section, and the list of other modules it depends on (default: none).

## Integration and platform (overlay work)
Which OpenRVDAS interfaces it implements, dependencies added (default: none),
and the Linux test command that must pass before any PR (rule 25).

## Usability (anything a tech sees or edits)
Answer each line of `docs/USABILITY.md` in the result, or mark N/A with a reason.

## Acceptance (exact commands)
```
pytest <test file>
```
```
flake8 <changed files>
```
```
bash gate/remote.sh <head sha>
```

## Scope
Files the builder may change. Everything else is read-only.
Dependents of the changed code (callers, configs, docs) to check.

## Trust boundaries and data integrity
What input is untrusted here. How stale, missing, and bad values are shown.
What must never change (timestamps, field names, existing output bytes).

## Non-goals and banned
No refactors, renames, formatting, or default changes. No loosened, skipped or
deleted tests, no swallowed errors, no sleeps for ordering (docs/CODEX.md rule 13).

## Report format
Diff summary, test names, before and after test output, anything uncertain,
verified claims separate from inferred. Keep it under the line cap set here: <N> lines.

## Stop rule
No code change needed: stop and report. Two fix rounds still red: stop and
send to the decision desk through the lead.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Gate receipt sha256 and verdict:
- What changed, in three lines:
- Open questions:
