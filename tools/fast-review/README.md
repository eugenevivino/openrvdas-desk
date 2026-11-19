# Fast review pipeline (D-FASTREV1)

Installed copies live in `/private/tmp/deepsignal/` on the MacBook; these are the desk copies. Target: one review
round in about 10 to 20 minutes.

1. `self-check.sh <repo> <base> <design-note>`: the builder runs the reviewers' checklist on its own head. It runs
   `pre-review.sh` (flake8; console oxlint, tsc and vitest when touched; changed test files; bandit and pip-audit if
   installed; npm audit offline as advisory), the design note's acceptance commands, and a static checklist (no new
   skips, no sleeps in tests, no bare except, no em dashes). Receipt: `receipts/self-check-<sha>.txt`.
2. `fast-review.sh <unit> <branch> <base> <design-note> <out>`: refuses without GREEN self-check and pre-review
   receipts for the head (exit 7). Splits the diff by path (logic, ui, install-security), runs one Codex cloud
   reviewer per part in parallel (Sol low; Astra high for install-security and for any part that escalates), each
   writing only `REVIEW-<part>.md`, judged only against the design note and D-P1DEF1. Merges to one verdict, collects
   `TICKET:` lines for `docs/TICKETS.md`, and records timing (queue, per part, merge, total).
3. `cloud-review.sh`: one cloud review task; any file other than its review file rejects the review.
4. `ds-launch-when-ok.sh`: the Mac launcher (claims, WIP cap, heavy-job cap, review routing, design-note check).
