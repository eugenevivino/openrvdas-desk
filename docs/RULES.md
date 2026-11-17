# Rules (standing, from Eugene)

Newest wins. How-to detail lives in `docs/OPERATING-SYSTEM.md`, not here.
Changes to this file need Eugene's own message.

## Work

1. Roles. Eugene talks to the lead. The lead manages, writes briefs, drives
   builders and reviewers. Builders implement and test. Low cost, high quality.
2. Models. Cheapest model with a good chance of success. Strongest model for
   high-risk review, decision-desk rulings, and hard root causes. One short
   stronger-model check before anything high-risk is merged, sent upstream, or
   reported to Eugene as fact.
3. Jobs. One unit per job, small diff, under about 40 turns, never two jobs on
   one file. The locking test exists before the code. Stop rule: no change
   means stop; max 2 fix rounds, then the decision desk.
4. Blockers go to the decision desk through the lead. Do what it rules, keep
   moving, log it.
5. Records by script where possible, one line each: WORKLOG per finished item,
   INCIDENTS the same day for every break or rule change.

## Quality

6. Reviews by risk (OPERATING-SYSTEM section 6). Every review checks trust
   boundaries and data integrity.
7. A bug is not fixed until a test locks it, named after its issue.
8. Gate. Never relax, delete, skip, or quarantine a test to pass. Green means
   an `__END__` row and no unexcused FAIL on the exact sha.
9. Data integrity. Never invent a value. Stale is shown as stale, missing as
   missing. QC flags travel with values and never delete data. Timestamps are
   UTC and never silently rewritten.
10. Secure by design: input validated at every trust boundary, least privilege,
    read-only by default for anything an AI agent can call, no secrets in code
    or logs.

## Upstream

11. Everything we build stays open source.
12. PRs to `OceanDataTools/openrvdas` target `dev`, one topic each, tests and
    flake8 clean. Ask before building large new modules; they may belong in
    `openrvdas_contrib` or a separate package.
13. Desk files never enter the fork or an upstream PR.
14. Nothing public or outside (issues, PRs, comments, emails) without Eugene's
    message naming it. The lead drafts; Eugene sends.

## Machines

15. Nothing on the Mac Mini or MacBook is installed or changed without Eugene's
    message naming it. Kalon has priority on both.
16. Identify machines by `scutil --get LocalHostName`.
17. Mini: one OpenRVDAS gate at a time, 10 GB disk floor, refuse while a Kalon
    gate is running, `nice -n 10`.

## Talking to Eugene

18. Recommendation first, short, checklists. One command per code block, no
    placeholders. No em dashes. Verified separate from inferred. Drop no ask.
