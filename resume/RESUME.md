# DeepSignal Mac lane: restart guide (first written 2026-11-18 ~07:15Z; a snapshot, check live state first)

Use this after any restart of the Mac, a lost /private/tmp, or a new session taking over the lane. macOS empties
/private/tmp on reboot, so the durable copy is the desk repo `eugenevivino/openrvdas-desk`, folder `resume/` on `main`. Persistent on the Mac: `~/bin/ds-codex`,
`~/.codex-deepsignal/` (login, config, sessions, launch-log). Nothing DeepSignal lives only in /private/tmp: every
code result is pushed (table below).

## Snapshot of state at 2026-11-18 ~07:15Z (all clean, all pushed; heads move, check the branches)
| What | Branch | Head |
|---|---|---|
| gate-linux (r1 + r2, ledger rows) | desk `gate/linux-actions` | 539080e |
| ds-codex wrapper | desk `tools/ds-codex` (tools/ds-codex.sh) | 53c0f80 (= ~/bin/ds-codex) |
| QARTOD flags | fork `deepsignal/qartod-flags` | 2724f07a |
| Correction ledger #56 | fork `deepsignal/correction-ledger` | 99c01919 |
| Fault bench #53 | fork `deepsignal/fault-bench` | 9d87d99a |
| Instrument history #52 | fork `deepsignal/instrument-history` | 3b4b76e6 (base; cloud task in flight) |
| Ship coupling #78 | fork `deepsignal/ship-coupling` | 3b4b76e6 (base; cloud task in flight) |
| Desk main | `main` | resume/ commit on top of b0b03e4 |

At that snapshot (the planned reboot was cancelled; these were restarted afterwards):
- r3 launch waiter (`ds-launch-when-ok.sh`): it was waiting for the DeepSignal lock (held by console-core's ds-codex pid 11793,
  another thread) and for memory to be normal (pressure level 2, swap 439 MB free of 11264). r3 had NOT started.
- #52 cloud poller and the desk briefs/cloud watcher (waiting for console prompts; none had landed at b0b03e4).

## Cloud tasks in flight at the snapshot (they keep running without the Mac)
| # | Task id | Branch | Status at 07:15Z |
|---|---|---|---|
| 52 instrument-history | task_e_6afd4ea8c79c832f80d646d43a49f24b | deepsignal/instrument-history | pending |
| 78 ship-coupling | task_e_6afd4edf411c832fb8c3f162adce11c9 | deepsignal/ship-coupling | pending |
Not submitted on purpose: #79 dependency-graph (held by the lead), #54 (held).

## Ordered restart steps
1. Check the login and memory (first command):
   `CODEX_HOME=$HOME/.codex-deepsignal codex login status; sysctl kern.memorystatus_vm_pressure_level vm.swapusage`
2. Rebuild the scratch tree (fresh clones; never touch Kalon folders):
   ```
   mkdir -p /private/tmp/deepsignal && cd /private/tmp/deepsignal
   git clone -q https://github.com/eugenevivino/openrvdas-desk desk-main
   git clone -q --branch gate/linux-actions https://github.com/eugenevivino/openrvdas-desk gate-linux
   cp -R desk-main/resume RESUME && chmod +x RESUME/tools/*.sh
   for m in qartod-flags correction-ledger fault-bench instrument-history ship-coupling; do mkdir -p $m/patches && git clone -q --branch deepsignal/$m https://github.com/eugenevivino/openrvdas $m/repo; done
   ```
   flake8 7.5.0 lives in console-core's venv under /private/tmp; if that is gone, ask the lead before any install.
3. Cloud status (run from /private/tmp/deepsignal/cloud-logs so the CLI's error.log stays out of repos):
   `CODEX_HOME=$HOME/.codex-deepsignal codex cloud status <task id>`
   When ready: `CODEX_HOME=$HOME/.codex-deepsignal codex cloud diff <task id> > /private/tmp/deepsignal/<module>/patches/<task id>.diff`,
   then `git -C <module>/repo apply --index ../patches/<task id>.diff` (or check whether the cloud agent already pushed the branch:
   `git ls-remote https://github.com/eugenevivino/openrvdas refs/heads/deepsignal/<module>`), run the brief's acceptance commands,
   commit, `git push origin deepsignal/<module>` (that branch only), add a docs/COST-LEDGER.tsv row on desk `gate/linux-actions`.
4. Console cloud prompts: `git -C desk-main pull` and look in briefs/console/ and briefs/cloud/. Submit console work only, no cap
   (lead, 07:14Z), Sol medium, `--attempts 2` or 3 for core v2, harness pieces and contract-dependent pages:
   `CODEX_HOME=$HOME/.codex-deepsignal codex cloud exec --env deepsignal --branch <branch> --attempts N "$(cat <prompt file>)"`
   (create and push the empty fork branch from the brief's base first).
5. Mac queue, one job at a time, each through the RAM and lock gate (MIN_SWAP_FREE_MB=1024 once swap total is 4 GB):
   `RESUME/tools/ds-launch-when-ok.sh <workdir> <prompt> <run-log> 7200 -- <ds-codex args>`
   a. gate-linux-r3: workdir gate-linux, prompt RESUME/prompts/gate-linux-r3-prompt.md,
      args `-m gpt-6.2-sol -c model_reasoning_effort=high --output-last-message /private/tmp/deepsignal/gate-linux-r3-answer.md -`.
      Then run `python3.12 -m unittest discover gate/tests` (not during another job), commit, push gate/linux-actions, ledger row.
   b. Fresh read-only Astra review of r3 at ultra (prompt: copy gate-linux-r2-review-prompt.md, point it at the r3 commit and
      briefs/gate-linux-r3.md): `KALON_ALLOW_ASTRA=1` + `-m gpt-6.2-astra -c model_reasoning_effort=ultra -s read-only`.
   c. qartod-flags review (workdir qartod-flags/repo, RESUME/prompts/qartod-flags-review-prompt.md), Astra high, read-only.
   d. fault-bench #53 review (fault-bench/repo), Astra high, read-only.
   e. correction-ledger #56 review (correction-ledger/repo), Astra high, read-only.
   #54 post-cruise-drift: do NOT launch until the lead says.
   The review prompts point at brief files under /private/tmp/deepsignal/<module>/; if those are gone, give them the desk paths
   briefs/deepsignal-<module>.md (qartod-flags: the front_check version is now briefs/deepsignal-qartod-flags.md on main).
6. After every job: `ls -t ~/.codex-deepsignal/sessions/*/*/*/*.jsonl | head` and check for subagent/thread_spawn sources;
   `grep -ci deepsignal ~/.codex/launch-log.txt` must not grow. Report to the lead.
