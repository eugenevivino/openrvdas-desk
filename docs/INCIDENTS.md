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
- Acceptance heading glued to the previous line, so 0 commands were parsed (fault-bench fix2, ship-coupling fix3). Guard: mac-build.sh refuses to launch a brief with 0 parsed acceptance commands; template says the heading starts its own line.
- A manual push went out before flake8 finished (console fix3-c, E501). Guard: /private/tmp/deepsignal/lead-push.sh runs flake8 on contrib/deepsignal before any manual push.
- Orphaned fixture processes from old acceptance runs caused flaky scripted runs. Guard: heartbeat.sh reports orphaned fixture processes (ppid 1) every 15 minutes; the lead stops them (a soak legitimately runs 24 h, so nothing is killed automatically).
- A chain recorded the previous CI run id instead of the new one (sec-cds-joint r2). Guard: chains record the previous run id and wait for a different one before reading results.
- The session dropped during an 18:01Z to 20:34Z network outage. Guard: detached heartbeat.sh plus a session cron that does not need re-arming.
- 2026-11-19 Rule 8 (shared machine) was enforced only through the memory gate. Guard: machine-wide heavy-job count (D-PIPE1a) in ds-codex and the launcher, with a sandboxed test that the counter writes nothing outside /private/tmp/deepsignal.

## 2026-11-19: first scanner-policy test wrote a desk receipt

The baseline entrypoint ignored the test harness's proposed scratch path. One test wrote a RED pre-review receipt for 8f0794e in the live receipt directory and attempted the unrelated pip-audit lookup. The original output is preserved under pilot-bandit-policy/initial-harness-red.txt. The corrected harness relocates the entire desk in its fixture and runs the real Bandit there. Only the subsequently admitted, installed self-check is evidence for the hardening commit. The live gate code was unchanged.

## 2026-11-20 Relay v6 admission dry-run could mutate a foreign lock
Cause: installed `ds-codex` dry-run lines 183-187 could remove an ambiguous foreign lock.
Fix: lead cancelled only owned v6 prelaunch waits; no native build started; immutable runtime/evidence retained.
Guard: nonmutating admission, per-job identity/invalidation and retry/recovery fixes are underway and require qualification before resumption; ambiguous claims remain reserved.

## 2026-11-20 Relay pilot Linux fixture and evidence measurement

Console candidate5b892601: Linux run44708749952 passed pilot/hardening, frontend
failed one Self-test handshake assertion. The fixture observed Disconnected before
its current socket existed. Retained raw failure at relay-20261120/evidence/
linux-console-136194786053-failed.log; correction waits for a new socket identity
and preserves every operator-warning assertion. Qualification remains pending.
Stream candidate75a71c1: Linux run44709129369 PASS; independent cloud review
task_e_6b000f9fd45c832fa1e37fecce36b4e7 HOLD on lost expired-report display.
No HOLD was converted to PASS. Durable retry-event intervals now correct latency
accounting; raw waits remain and host availability is not inferred.


### 2026-11-20: combined pilot review and publication baseline

Independent native Astra Ultra review2ea3e609 HOLD found outage-navigation history
loss, delayed-report cadence distortion and QC-name misclassification. Preserve
its original answer in research/2026-11-20-relay-pilots/combined-astra-hold.md;
targeted production-route regressions are active. Individual source reviews and
green tests cannot clear these findings. Combined Linux44714303424 attempt1 ran
no tests: checkout could not find the not-yet-published candidate. The source hook
correctly refused a push lacking a named remote baseline. Added named publish
remote, fetched verified integrationbff54ec, then published the same candidate with
the hook intact; only failed jobs were retried. Source identity was unchanged.

Relay38baeff replaces mutable kern.boottime microseconds with validated stable
boot-session UUID for the local swap-observation cache. Versioned cache starts
with an ordinary five-minute warmup; pressure, swap, job and ownership guards
remain. Focused19 admission/measurement checks passed; live performance benefit
is not yet measured.


### 2026-11-20: plan interpreter and repair qualification

Compiling a plan with macOS default Python3.9 pinned that interpreter into the
adapter command even though the controller ranPython3.12. Its process-relative
monotonic values prevented cross-worker swap evidence reuse. Relay247f58f adds
an early Python3.12 minimum at plan compilation; the new test first failed then
passed. Owned prelaunch22797/22798 was cancelled and retirement verified before
replacement; no native command or claim had started. Runtime-v11 now uses3.12.

Final repair9935ed82 passes223frontend tests, both existing native acceptance
contracts and exact Linux44718633913. Old failures, fixture synchronization errors
and the temporary QC-only cache regression remain recorded. Fresh Astra Ultra
review is active; original HOLD is still authoritative until explicit clearance.

## 2026-11-20: independent pilot review R3/R4 data variations
Fresh native Astra Ultra held4f28b56d thena284c1c7 despite exact native/Linux PASS.
R3's four cases reproduced in8tests. R4's five cases reproduced in10production-mode
tests atd6253b3a; earlier fixture-mode evidence is retained, not claimed equivalent.
Repair01e83671 excludes return-cache intervals, preserves ordered logger replay,
requests manager QC, avoids catalog QC recursion and retains accepted null reports.
Two complete per-test catalog variants remain RED at1490e537 before the last fix.
Strict request expectations now include mandatory manager QC; no assertion was
removed or weakened. Unknown/unpublished companion fields still count toward the
existing200-field gateway budget; catalogs beyond that effective budget are not
qualified by these tests. Full frontend/native/Linux and independent re-review
are still required before integration. All HOLDs and raw failures are preserved.

## 2026-11-20: pilot history provenance after repeated cursor replay
R6-R8 independent reviews remained HOLD despite exact native/Linux PASS. Corrected
production fixtures reproduced all findings; raw initial fixture failures retained.
Cadence now distinguishes cached timestamps across replay and derives bounded
interval endpoints. Self-test explicitly requests raw catalog fields; normal
measurements always request QC. Raw updates preserve shared history. R8's sole
remaining QC correction error reproduced twice atab1d6560;73d97e74 retains its
original observation epoch. All272frontend/lint/type checks PASS; full qualification
and fresh independent review still required. No target integration or gate change.
