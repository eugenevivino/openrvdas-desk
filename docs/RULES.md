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

## Who builds (D-TEAM5)
23. Claude manages; Codex does all hands-on work (code, tests, fixes, scripts,
    long reads), cloud or Mac. Right-size the model; Astra approved for hard
    work. See `docs/BUILDERS.md`.
24. DeepSignal is tightly scoped, independent modules: one module per branch
    (`deepsignal/<module>`), per PR and per brief, each with its own tests, a
    sample logger config and a short README section, few dependencies between
    modules, each usable alone in a stock OpenRVDAS logger config.
25. Linux only. DeepSignal targets Linux (Ubuntu 22.04+, Debian 12+ and Raspberry
    Pi OS, Rocky 9+). macOS is a dev convenience: a macOS-only test failure never
    blocks. A module uses OpenRVDAS's own interfaces (Reader, Transform, Writer,
    DASRecord, logger YAML, CachedDataServer), is pure Python, and adds no
    dependency beyond OpenRVDAS requirements unless Eugene approves. No PR before
    its tests pass in a real Linux run on Python 3.12 (`gate/gate-linux`).
26. Everything user-facing is exceptional and easy for a ship tech who is not a
    software expert. A module is not done until it passes the checklist in
    `docs/USABILITY.md`, and every PR review includes it.

## Talking to Eugene

18. Recommendation first, short, checklists. One command per code block, no
    placeholders. No em dashes. Verified separate from inferred. Drop no ask.

## Lean sessions and proof (Eugene 2026-11-18, adopted from ProjectArchitect, D-PA1)

19. Retrievers. A session never reads a long log, gate TSV, junit file, big
    source file or research page whole. A cheap fresh helper reads it for one
    stated question and returns pointers (`path:line`) in at most 40 lines, or
    `NOT FOUND: <what was searched>`. Brief = QUESTION, SCOPE, CAP, REPORT.
20. Machine-checked milestones. Every roadmap phase and every brief defines
    done as a command and its expected result (a test, the gate, a count). A
    phase closes only when that check passes on the exact sha and Eugene says so.
21. Cost ledger. Every Claude and Codex job adds one row to
    `docs/COST-LEDGER.tsv` (date, brief, tool, model, effort, wall seconds,
    tokens in, out, cached, note). Read from local session logs, never from
    account credentials. Weekly rollup goes in `docs/WORKLOG.md`.
22. Plain-English recap at every phase close, in `docs/recaps/<phase>.md`: what
    changed for a crew member, what was proven (with the check), what is not
    proven, what comes next. Written for Eugene, not for engineers.
