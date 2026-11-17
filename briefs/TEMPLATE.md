# Brief: <area>-<slug>

Copy to `briefs/<area>-<slug>.md`. A builder reads only this file, AGENTS.md,
and the files listed under Scope. If it needs more, the brief was too vague:
stop and ask the lead.

- Decision: D-<id> this implements
- Risk tier: low | medium | high (OPERATING-SYSTEM section 6)
- Base: fork `dev` at <sha>, branch `<area>/<slug>`
- Model: <cheapest likely to succeed>
- Upstream home: core | openrvdas_contrib | separate package | fork only

## Goal
One sentence a crew member would recognize.

## Failing test first
Test file and test names. It must fail on the base sha before any code
changes. Paste the RED output into the result.

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

## Stop rule
No code change needed: stop and report. Two fix rounds still red: stop and
send to the decision desk through the lead.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Gate receipt sha256 and verdict:
- What changed, in three lines:
- Open questions:
