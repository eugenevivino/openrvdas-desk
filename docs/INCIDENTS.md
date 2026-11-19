# Incidents

Same day for every break, stall, or rule change. Format:

```
## YYYY-MM-DDTHH:MMZ short title
Cause:
Fix:
Guard: (the test, check, or rule that stops a repeat)
```

A repeat without a new guard is itself an incident.

## 2026-11-18 Codex sub-agent ran Astra without the opt-in (job #56)
`multi_agent` is on by default in codex-cli 0.169.0 and a spawned sub-agent can pick any model,
so a Sol job started an Astra xhigh sub-agent (about 1.06M input tokens) to review its own work
and then edited code from it. This bypassed the Astra opt-in (rule 27) and the rule that the
author never reviews its own work. Fix: `tools/ds-codex.sh` now disables multi_agent,
multi_agent_v2, multi_agent_v2_dynamic_tools, multi_agent_mode, enable_fanout and
runtime_agent_instances and refuses `--enable` for them (desk 2ad92c6). Kalon's codex-run has the
same gap; reported to Eugene, not edited. Code kept (tests and flake8 pass) and still gets an
independent fresh review. Check each job's session folder for `thread_spawn` sessions.

Carry-over for Kalon (Eugene's hard separation: this desk does not edit Kalon's files): `~/bin/codex-run`'s
connector guard has no `multi_agent`, `multi_agent_v2`, `multi_agent_v2_dynamic_tools`,
`multi_agent_mode`, `enable_fanout` or `runtime_agent_instances` entries, so a Kalon job can also
spawn a sub-agent on any model. The fix we used is the same list added to the guard's disable set and
its `--enable` refusals (see `tools/ds-codex.sh`). Eugene decides whether Kalon wants sub-agents off.

## 2026-11-19 console-mvp received the joint security commits (build lead)
The joint #197 work was built in a clone whose local branch was still named `deepsignal/console-mvp`. The hourly sync pushes every local `deepsignal/*` branch ahead of origin, so it pushed edec001 (merge of #197, which changes core) and f38b52e onto fork `deepsignal/console-mvp`. Effect: console-mvp head is f38b52e instead of 0fd4dee. Nothing was merged anywhere; the UI pilot was built from 0fd4dee directly. Fix applied: that clone is detached; other clones audited. Restoring console-mvp to 0fd4dee needs a force push, which is Eugene-only; until then use 0fd4dee or `deepsignal/integration` for the console. Rule: build on a local branch with the same name as the branch you push to, or detach.

## 2026-11-18 and 19 snags and their guards (D-PIPE1 rule 9, build lead)
- The cloud dispatch draft allowed caller-supplied state to hide canonical WIP refusals and job claims. Guard: `preflight-and-claims` exercises both refusals through the normal launcher with an alternate caller state and a fake host.
- Acceptance heading glued to the previous line, so 0 commands were parsed (fault-bench fix2, ship-coupling fix3). Guard: mac-build.sh refuses to launch a brief with 0 parsed acceptance commands; template says the heading starts its own line.
- A manual push went out before flake8 finished (console fix3-c, E501). Guard: /private/tmp/deepsignal/lead-push.sh runs flake8 on contrib/deepsignal before any manual push.
- Orphaned fixture processes from old acceptance runs caused flaky scripted runs. Guard: heartbeat.sh reports orphaned fixture processes (ppid 1) every 15 minutes; the lead stops them (a soak legitimately runs 24 h, so nothing is killed automatically).
- A chain recorded the previous CI run id instead of the new one (sec-cds-joint r2). Guard: chains record the previous run id and wait for a different one before reading results.
- The session dropped during an 18:01Z to 20:34Z network outage. Guard: detached heartbeat.sh plus a session cron that does not need re-arming.
- 2026-11-19 Rule 8 (shared machine) was enforced only through the memory gate. Guard: machine-wide heavy-job count (D-PIPE1a) in ds-codex and the launcher, with a sandboxed test that the counter writes nothing outside /private/tmp/deepsignal.

## 2026-11-19: first scanner-policy test wrote a desk receipt

The baseline entrypoint ignored the test harness's proposed scratch path. One test wrote a RED pre-review receipt for 8f0794e in the live receipt directory and attempted the unrelated pip-audit lookup. The original output is preserved under pilot-bandit-policy/initial-harness-red.txt. The corrected harness relocates the entire desk in its fixture and runs the real Bandit there. Only the subsequently admitted, installed self-check is evidence for the hardening commit. The live gate code was unchanged.
