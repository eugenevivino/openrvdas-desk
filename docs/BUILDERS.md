# Who does what: Claude manages, Codex builds

Standing rule from Eugene, 2026-11-18 (rule 23, D-TEAM5): Claude does
management. Codex does all hands-on work: code, tests, fixes, scripts, mechanical
research reads. Right-size the model; Astra at whatever reasoning effort the work
needs is approved for hard work.

## Split

| Claude (management) | Codex (work) |
|---|---|
| Turns asks into briefs, plans, assigns, routes reviews | Writes the failing test, then the fix or module, on a fork branch |
| Reads results and gate receipts, keeps STATE, DECISIONS, WORKLOG, IDEAS | Runs tests and flake8, fixes its own red, reports in the brief's format |
| Writes desk docs and drafts upstream text for Eugene to send | Gate script changes, Mini scripts, anything that is code |
| Talks to Eugene, asks the few blocking questions | Retriever jobs (rule 19): long reads, logs, TSVs |

A Claude session may edit desk Markdown. It may not write production code,
tests, or gate code. If it catches itself doing so, stop and write a brief.
Already done before this rule: the Django fix (ad10eb1) was written by Claude
and independently reviewed; it is the last exception.

## Models (Eugene, 2026-11-18)

Cheapest model that is likely to succeed. Current picks: Sol 6.2 and Astra 6.2
(D-TEAM6). Astra is approved for harder work
(reviews, high-risk tier, root causes, design) at the effort it needs (high,
xhigh, ultra per `docs/CODEX.md` section 2). Say the model and effort in the
brief and record them in `docs/COST-LEDGER.tsv`.

## Two places Codex runs (cloud first, D-TEAM7)

| | Codex cloud (default lane) | Macs via `~/bin/codex-run` |
|---|---|---|
| Good for | Linux-safe Python: modules, tests, fixes, sweeps; many jobs at once | macOS-only checks, serial and USB, the Mini, anything near the gate machine |
| Guard | None of ours: the brief, `-m` model, effort and a ledger row | `codex-run`: model refusal, Astra flag, launch log |
| Output | A task diff or branch on the connected fork | Files in `/private/tmp/deepsignal/<module>/` |
| Gate | Linux gate on the exact sha (a cloud pass is only a quick check) | Same |

Cloud always runs Sol at medium effort (Eugene). So cloud takes standard,
well-specified code modules, in parallel, one brief per task. Astra work (math,
reviews) and anything needing Sol high stays on a Mac (rule 8). Every brief
names its lane. Nobody types code either way.

## Exact cloud invocation (DRAFT, flags unverified)

Verified: subcommands exec, status, list, apply, diff. Unverified: flags. Before
the first job run `codex cloud exec --help` (a plain Codex call, not codex-run)
and fix this block. Cloud's model is fixed (Sol medium), so a cloud brief says
"lane: cloud" and there is no `-m` to set (rule 27).

```
codex cloud exec --env <environment id from Eugene> "$(cat /private/tmp/deepsignal/<module>/brief.md)"
```
```
codex cloud status <task id>
```
```
codex cloud diff <task id> > /private/tmp/deepsignal/<module>/patches/<task id>.diff
```
```
codex cloud apply <task id>
```
Then the lead pushes the result as `deepsignal/<module>` on the fork, runs the Linux
gate on the sha, and routes an Astra 6.2 review. First job on a new environment is a
small Luna smoke test (a one-line change and its test), recorded in the ledger.

Needs Eugene once (account settings): connect `eugenevivino/openrvdas` in Codex
cloud; environment with Python 3.12, dependencies installed in its setup script,
agent internet off after setup; then send the environment id.
