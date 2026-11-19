# pipe2-tooling

Status: FIXED
## Fixed target

Harden only the DeepSignal process tools in `/private/tmp/deepsignal`: `ds-launch-when-ok.sh`,
`mac-build.sh`, both review scripts, `lead-push.sh`, `hooks/pre-push`, both detached loops,
and their brief and cloud-header templates.

Briefs declare `network`, `tools`, `disk_gb`, `ram_gb`, and `required_files` in a bounded
front-matter block. Launcher and cloud submission preflight every declaration, time out in
about two minutes, and refuse before creating a claim or consuming either cap.

Every launch carries a unique claim directory and pinned HEAD SHA through
`ds-launch-when-ok.sh`. `mac-build.sh` refuses a mismatched branch HEAD. Heartbeat and
autopilot may request work only through that path and must not race duplicate claims.

Each job writes an atomic receipt keyed by the exact acceptance command, with exit status
and `passed`, `failed`, or `skipped`. `--rerun-skipped` runs only failed or skipped entries.
The normal mode runs the complete acceptance list.

Machine-wide heavy capacity is three, with one slot permanently reserved for Kalon.
DeepSignal therefore holds at most two heavy slots. Kalon is observed only by reading the
process list and is never signaled, opened, or modified.

`lead-push.sh` and `hooks/pre-push` reject a merge commit when its second parent is reachable
from `main`, `dev`, or `integration`. The stated remedy is to re-cut the unit branch at the
trunk tip. Brief and cloud-header templates describe fuzz, mutant, and sanitizer work as:
own code, local only, no network, no exploitation. Swift is not applicable.

## Acceptance tests

Each command is one bash line, runs on macOS bash 3.2, avoids `grep -P`, and pipes `wc -l`
through `tr -d ' '`.
```bash
cd /private/tmp/deepsignal && bash tests/pipe2/preflight-refuses-before-claim.sh
cd /private/tmp/deepsignal && bash tests/pipe2/receipt-rerun-skipped.sh
cd /private/tmp/deepsignal && bash tests/pipe2/pinned-head-and-single-launch.sh
cd /private/tmp/deepsignal && bash tests/pipe2/trunk-merge-guards.sh
cd /private/tmp/deepsignal && bash tests/pipe2/heavy-cap-reserves-kalon-slot.sh
cd /private/tmp/deepsignal && test "$(find templates -type f -exec cat {} + | awk '/own code, local only, no network, no exploitation/{n++} END{print n+0}')" -ge 2
cd /private/tmp/deepsignal && test "$(git status --short -uall | wc -l | tr -d ' ')" = 0
```

## Out of scope

No OpenRVDAS product changes, Swift work, dependency additions, remote pushes, automatic
trunk merges, exploitation, network fuzzing, or changes to Kalon. No redesign beyond the
listed scripts, templates, receipts, claims, guards, caps, and focused test fixtures.

## Prerequisites on trunk

Trunk supplies the detached launcher contract, per-job claim root, cap and lock locations,
brief parser boundary, acceptance runner, review entry points, shared hook installation,
and deterministic local test fixtures that use temporary repositories and stubbed resources.

## Who judges

Eugene accepts the fixed behavior. The listed macOS bash 3.2 commands are the executable
gate, and the DeepSignal lead confirms the race audit and the read-only Kalon boundary.

## Lead note on paths (2026-11-19)
Written by Astra in Codex cloud (task_e_6afe670a9420), which cannot see the Mac. Path mapping, no change to the
target: the tests are `/private/tmp/deepsignal/tests/pipe2/*.sh` (desk copies in `tools/pipe2/tests/`); "templates"
means desk `briefs/TEMPLATE.md` and `briefs/cloud/_HEADER.md`; the clean-tree check runs on the desk clone. This unit is
process tooling, counted outside the D-WIP3 cap by the coordinator's decision (logged in DECISIONS under D-PIPE2).
