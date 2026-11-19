# Brief: <area>-<slug>

Copy to `briefs/<area>-<slug>.md`. A builder reads only this file, AGENTS.md,
and the files listed under Scope. If it needs more, the brief was too vague:
stop and ask the lead.

- Decision: D-<id> this implements
- Risk tier: low | medium | high (OPERATING-SYSTEM section 6)
- Module: exactly one (rule 24). Branch `deepsignal/<module>` for overlay work, `<area>/<slug>` for core fixes
- Mac scratch path: `/private/tmp/deepsignal/<module>/` only (docs/CODEX.md rule 1b)
- Base: fork `dev` (core) or `contrib/master` (overlay) at <sha>
- Lane: `cloud` (Sol medium, fixed) or `mac` (rule 27: model id for `-m` and effort, e.g.
  `gpt-6.2-sol` high or `gpt-6.2-astra` xhigh, tier from docs/CODEX.md section 2)
- Fresh session, under 40 turns
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
No writes, deletes or moves in `/private/tmp` outside `/private/tmp/deepsignal/`; never `/private/tmp/kalon` (rule 28).
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

## Done-line rules (D-PIPE1 rule 7) and claims (rule 5)
- Done-lines must work on macOS: `git status --short -uall`; never `grep -P`; pipe `wc -l` through `tr -d ' '`; no Swift unless the unit has Swift.
- The `## Acceptance` heading starts its own line; each command is on its own line in a fenced block (a brief with zero parsed commands is not launched).
- Jobs are launched only by the detached launcher, which takes a claim file per job; never launch the same job from a second loop.

## Design note (D-DESIGN1)
- Design note: `docs/designs/<unit>.md` (required before a build; reviewers judge against it).
