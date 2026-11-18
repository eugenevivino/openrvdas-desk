# Using Codex on this desk

Ported from Kalon's Codex rules (`l2audio`, read 2026-11-18, read-only). Where
the Kalon rule is about Swift, audio, or its pipeline, it is translated, not
copied. Kalon's model names and tiers are theirs; confirm each one exists on
our Macs before relying on it (`codex --help`, `~/bin/codex-run --help`).

Sources, all in `eugenevivino/l2audio` on branch `claude/desk-astra-ultra-20261117`
unless noted:
- C1 `docs/process/codex-cost-rules.md` (on main too)
- C2 `docs/process/CODEX-MODEL-TIERS.md`
- C3 `docs/process/RULES-V2.md`, rules 2, 2b, 3, 3b, 3g
- C4 `docs/process/OPERATING-SYSTEM.md`, sections 0b, 8
- C5 `docs/project-files/research/desk/2026-10-21-smarter-code-practices.md`, Part 4 (brief template, banned patterns, review checklist)
- C6 `docs/project-files/program/DRAFTING-RULES-FIX-ROUND-BRIEFS.md`
- C7 `docs/pipeline-gh/CODEX-LED.md` and `docs/program/REBUILD-FROM-ZERO.md`, "Builder sandbox"

## 1. Honest status

The 2026-11-18 Codex trial (research note `2026-11-18-django-test-basic.md`)
did **not** follow C1: it ran bare `codex exec` instead of `~/bin/codex-run`,
on the MacBook's default model (gpt-6-astra, set to low effort), with no launch
log. It was one read-only job, 50 s, about 41k tokens, so the harm was small,
but the rules below apply from the next run on.

## 2. Rules that apply

**Launch and safety** (C1 rule 1, C7)
1. Launch Codex on the Macs only through `~/bin/codex-run`. It refuses the
   priciest model without an explicit env flag, refuses full-access and bypass
   flags, forces approvals off with the sandbox on, and logs every launch to
   `~/.codex/launch-log.txt`. If `codex-run` is missing on a Mac, stop and ask
   Eugene; do not fall back to bare `codex`.
1b. Scratch path (Eugene, 2026-11-18): on his Macs, every DeepSignal Codex job
   works only under `/private/tmp/deepsignal/<module>/` (clone in `repo/`,
   brief in `brief.md`, patches in `patches/`). The Kalon project also uses
   `/private/tmp`; never read, write or delete any other folder there. Every
   brief names this path. Standing approval: Codex may build in these scratch
   copies and push to `deepsignal/*` fork branches for a module and its fix
   rounds; pull requests still need Eugene.
1c. Model flag and ids (verified 2026-11-18 05:2x Z, both Macs): `~/bin/codex-run`
   (Kalon's, identical on both Macs, new version since 05:19Z) refuses an exec with
   no model (exit 7) and maps old ids to 6.2: any sol id runs `gpt-6.2-sol`, any
   astra id `gpt-6.2-astra` (needs `KALON_ALLOW_ASTRA=1`; set it only for the job
   Eugene approved, D-TEAM5). Luna `gpt-6-luna` passes through; other ids refused.
   We still pass `-m <id>` ourselves (rule 27). Its clean-up now touches only
   `/private/tmp/kalon*`, skips `deepsignal` paths. Mini CLI is 0.170.0 via
   codex-run; its plain `codex` is an older 0.163.0. Efforts: low to ultra.
2. Read-only (`--sandbox read-only`) for diagnosis and review. Workspace-write
   only for a Builder, never `danger-full-access`. The sandbox blocks `.git`
   writes by design: Codex edits files, the lead (or a script) commits.
3. No network, no installs, no model logins from a Codex job. Packages go in
   only on Eugene's yes, into an isolated venv, pinned (C1 last line).

**Right-size the model** (C1 rule 2, C2, C3 rule 2)
Current picks (D-TEAM6): **Sol 6.2**, **Astra 6.2** (ids in 1c); "Sol" and "Astra"
below mean these. A running job finishes on its model.
Cheapest model with a good chance of success; a stronger check only where
risk is high. Mapped to our work:

| Work | Model tier | Effort |
|---|---|---|
| Mechanical: lint, file moves, header or portability checks, fuzz and sanitizer sweeps, test scaffolding | Luna if present, else Sol | medium |
| Normal code: a reader, transform or writer; FIX jobs with a reproduction; tests; diagnosis with a reproduction (this Django bug) | Sol | high |
| Reviews, brief drafting, design notes, audits that judge | Astra | high (xhigh for high-risk tier: listener core, logger manager, data values, timestamps, QC flags, live-control paths) |
| Hard math and rulings that bind the design: clock-forensics estimator, drift statistics, root causes with no reproduction | Astra | ultra, decision desk only |

Rules: Ultra is never for reviews, briefs, or yes/no questions (C2 "Right-size
Astra"). A job over 45 minutes at Ultra was mis-tiered. Eugene approved Astra for
harder work on 2026-11-18 (D-TEAM5); locally it still goes through `codex-run`,
which needs its env flag for that job (C1 rule 2). A Medium result on high-risk code is a
first draft: re-run at xhigh and compare (C2 "What a Medium result means").

**Context hygiene** (C1 rules 4 and 5, C3 rules 2b and 3g, C4 section 0b)
4. One bounded task per job, a fresh session, under about 40 turns. Never
   resume a long session; write a result file and stop. Cost grows with session
   length because every step rereads the context.
5. Briefs are short and name only the files the job needs (`briefs/TEMPLATE.md`,
   C5 template). Paste facts (failing test, traceback, line numbers at a named
   sha), not the whole repo or chat history. Never line numbers without a sha.
6. Cap the output in the prompt ("under 25 lines", "unified diff only") and ask
   for verified-vs-inferred markers. Keep logs out of the prompt: campaigns
   (test sweeps, replays, soak runs) are plain scripts that write a summary
   file, and Codex reads only the summary (C1 rule 5).
7. The decision desk and its Codex or Claude sessions are fresh about every
   200k tokens of context (C3 rule 3g).

**Concurrency and cost** (C1 rules 3, 6, 7; C3 rules 3, 3b; C4 section 1)
8. Lanes (Eugene 2026-11-18, D-TEAM7). Codex cloud always runs Sol at medium. Cloud
   is the default lane for standard, well-specified code modules, in parallel, to
   keep load off the Macs. Astra work (math, reviews, root causes) and anything
   needing Sol high or more runs on a Mac via codex-run with `-m` (rule 27).
   Every brief names its lane. Kalon's cap is 3 bounded jobs across both Macs.
   DeepSignal always gets ONE Codex slot on the MacBook, whatever Kalon is running
   (Eugene, "unblock it"), one DeepSignal job at a time in queue order. If the
   MacBook is overloaded (critical memory pressure, swap near full) the slot moves
   to the Mini; never on the Mini during a Kalon gate.
9. Check real load before launch, counting real Codex processes only. A
   `pgrep codex` count can hit Kalon git commands with `codex/` in a branch
   name (it did on 2026-11-18). Use `pgrep -x codex` and the launch log.
   The Mini runs a long-lived Codex cloud host (`codex exec-server`) and the
   desktop app; neither is a job, but both are capacity Kalon owns.
10. Stop new Codex jobs near 5% of the plan left; kill jobs that loop or pass
    2 hours (C3 rule 3).
11. Cost logging: every run records in `docs/WORKLOG.md` the brief id, tier,
    wall time and tokens from the Codex log. Kalon's `~/bin/codex-model-audit.sh`
    reproduces cost per session; run it weekly and flag any Astra session
    outside an approved job (C1 rule 6).

**Quality guardrails** (C5 Part 4, C6, C3 rules 2b and 18a)
12. The locking test exists before the build and is never relaxed. A fix brief
    names the failing test, the files in scope, the acceptance commands, and a
    stop rule: no executable change means stop; at most 2 fix rounds, then the
    decision desk.
13. Banned in Codex output (reject in review): loosening, skipping or deleting
    a test; bare `except:` or `except Exception: pass`; sleeps or arbitrary
    timeouts to fix ordering; rewriting a value without logging it; changes to
    a ship's `local/` device definitions; unrequested refactors, renames or
    formatting; copy-pasting an existing function for a new case.
14. Reviewer checklist (60 seconds): stays inside the listed files; a test
    fails without the fix (ask for the before output); no new swallowed errors;
    every new path logs or surfaces failure; no duplicate of an existing
    helper; behavior matches the brief's stated lines.
15. Author never reviews its own work. Review tier follows risk
    (OPERATING-SYSTEM section 6). Tests and the gate decide, not models.

## 3. How the next Codex run will go

A concrete example, the fix for the Django bug, on a topic branch:
1. Lead writes `briefs/fix-django-logger-config.md` from the template: goal,
   failing test first, files in scope (`django_gui/django_server_api.py`, its
   test file), acceptance commands, stop rule. Tier: normal code, Sol high.
2. On the MacBook (or in Codex cloud, see `docs/BUILDERS.md`): `~/bin/codex-run` with Sol, workspace-write, fresh session,
   one job, the brief piped in, output capped to a diff plus the test result.
3. Lead commits, pushes the topic branch, runs `gate/remote.sh`.
4. A fresh Astra high review reads the diff and the gate receipt.
5. WORKLOG line with tier, time and tokens. Eugene sends any upstream PR.

## 4. Open items for Eugene

- `~/bin/codex-run` exists and is identical on both Macs (verified 2026-11-18).

## 5. Retrievers and the ledger (rules 19 and 21)

- A retriever is a read-only, fresh, cheap job (Luna or Sol medium on Codex, or a
  small Claude model). Tools: read, grep, glob, one write for an optional report
  file. Brief: QUESTION, SCOPE, CAP (default 40 lines), REPORT yes or no. Grep
  first, read by offset and limit, answer by the 20th tool call with what it has.
- Typical retriever jobs here: a gate `results.tsv` or junit file, a pytest log, a
  device definition, a long research note, "where is X called".

