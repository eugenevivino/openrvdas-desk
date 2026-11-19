# Shared header, prepend to every cloud prompt (D-UPSTREAM0)

- Work only on the fork eugenevivino/openrvdas, on your deepsignal/* branch. Never push to dev or master.
- gh and git may touch OceanDataTools only for a read-only fetch by URL. No pushes, PRs, issues or comments to any OceanDataTools repo, ever.
- Touch only the files your brief names. No secrets, no .env edits, no new dependencies unless the brief says so.
- No em dashes in any text you write.

## Done-line rules (D-PIPE1 rule 7) and claims (rule 5)
- Done-lines must work on macOS: `git status --short -uall`; never `grep -P`; pipe `wc -l` through `tr -d ' '`; no Swift unless the unit has Swift.
- The `## Acceptance` heading starts its own line; each command is on its own line in a fenced block (a brief with zero parsed commands is not launched).
- Jobs are launched only by the detached launcher, which takes a claim file per job; never launch the same job from a second loop.

Design first (D-DESIGN1): this task has a design note on the desk (fixed target, acceptance tests, out of scope). Build only to it; anything outside it is out of scope.
