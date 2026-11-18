# State (rewritten each session, 60 lines max)

Updated 2026-11-18 07:20Z by the build lead. Mac reboot pending; resume steps in `resume/RESUME.md`.

## Now
- PRIORITY (Eugene): MVP #1 is the console display, target Tue 2026-11-25, parallel cloud build
  (ROADMAP "MVP #1"). Cloud cap removed: run as many disjoint-file tasks as the work splits into.
- Rules: build on the fork first, nothing upstream until Eugene says (D-ARCH6). Kalon is hard
  separate: DeepSignal uses `~/.codex-deepsignal` and `~/bin/ds-codex` only (D-SEP1).
- Cloud lane LIVE: env `deepsignal` (id in team memory, not here), Sol medium, `--env deepsignal`,
  run from a fork clone under `CODEX_HOME=$HOME/.codex-deepsignal`. Prompts inline: `briefs/cloud/`.
- Sub-agents: off by default; `ds-codex --sub-agents` pins the model (D-SUB1, verified). Top reasoning
  effort is `ultra` (Sol, Astra). Astra needs KALON_ALLOW_ASTRA=1 on the Mac.
- RAM: Mac launches hold until pressure is normal and swap is free; one DeepSignal job per Mac.

## Code (all on the fork eugenevivino/openrvdas, base contrib 3b4b76e unless noted)
- qartod-flags 2724f07a: built, 19 tests, flake8 clean. Needs independent review.
- correction-ledger 99c01919: built, 25 tests; self-review by an unauthorized sub-agent
  (INCIDENTS). Needs independent review and a D-LEDGER1 fix round.
- fault-bench 9d87d99a: built, 17 tests. Needs independent review.
- vector-wind 558e45b (`claude/project-thread-un3kq6`): done, parked.
- console-core 5682671: built, Vitest 8/8; v2 update briefed, not launched.
- Cloud tasks in flight at 07:15Z: #52 instrument-history (`task_e_6afd4ea8c79c832f80d646d43a49f24b`),
  #78 ship-coupling (`task_e_6afd4edf411c832fb8c3f162adce11c9`). #79 and #54 held.
- Django fix: fork branch `django-gui/shared-config-names` ad10eb1, parked.
- Gate: desk `gate/linux-actions` 539080e. r2 review HOLD (4 findings); r3 brief `briefs/gate-linux-r3.md`.
  Workflow not on main yet; first real Linux run pending.

## Mac queue after reboot (one at a time, behind the RAM gate)
1. gate-linux-r3. 2. r3 review (Astra ultra, read-only). 3. qartod-flags review. 4. #53 review. 5. #56 review.
Before that: `CODEX_HOME=$HOME/.codex-deepsignal codex login status`, then RESUME.md step 2.

## IDEAS and decisions
- IDEAS 1 to 103; the build lead owns numbering, next 104. Decisions through D-LEDGER1, D-SUB1,
  D-SEP1; open for Eugene: D-ADOPT1 (separate package vs contrib).

## Sync (D-SYNC1)
- Last sync 2026-11-18T09:44:50Z: fork branches pushed ok; upstream fetched ok (core dev 1a6f1edb, contrib master 3b4b76e6); desk main pushed after this line.
- Desk pushes at once. Fork upstream fetch not done today (fork dev 1a6f1ed, contrib master 3b4b76e).

## Open asks for Eugene
- Cloud env: add CODEX_ENV_NODE_VERSION=22 and CODEX_ENV_PYTHON_VERSION=3.12 (console is Node 22).
- Approve or change the console MVP additions (a to d approved by the build lead under the "recommended" rule).
- Night red default card (console thread). Kalon carry-over note in INCIDENTS (sub-agents).
- First scoreboard make, model, protocol; stale threshold.
