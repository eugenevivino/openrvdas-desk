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
