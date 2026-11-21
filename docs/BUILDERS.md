# Builders and continuation

## Current allowance override (Eugene, 2026-11-21)

For the current allowance window Eugene explicitly said to use the remaining
allowance, even fully, before the expected refresh in about 12 hours. This
supersedes the earlier 1% reserve for this window only. Continue useful authorized
engineering; no reset purchase, overage or change to monetary limits. Provider
succession remains optional, and Relay remains the execution path.

## Provider succession (Eugene, 2026-11-20)

Product delivery continues now. Codex may work down to a 1% reserve; launch no new
Codex job at <=1% or with unknown/stale quota. Preserve a provider-neutral handoff
so an available authorized provider can resume when tokens run out. Claude is an
option, not a requirement; its authentication is not a dependency of current work.
This authorization permits successor hands-on engineering, including Claude, and
supersedes the historical Claude-only-manager restriction within this scope.

Keep the same deterministic controller, source/evidence identity and acceptance
gates. Existing workers retain ownership until verified terminal state; reconcile
ambiguous claims before replacement and never duplicate live work. A successor
must have verified authentication/readiness and known quota/budget before its own
launch. Keep independent reviews and monetary limits; no new spending or overage
is authorized. The handover records readiness, not a completed provider takeover.

## Historical role split (scoped successor exception above)

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

Outside the successor scope above, the historical rule limits Claude to desk
Markdown and management; production code, tests or gate changes need a builder brief.
Already done before this rule: the Django fix (ad10eb1) was written by Claude
and independently reviewed; the successor directive above is a newer exception.

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

## Exact cloud invocation (flags verified from `codex cloud exec --help`, 2026-11-18)

Usage: `codex cloud exec [OPTIONS] --env <ENV_ID> [QUERY]`. Options: `--branch <BRANCH>`
(git branch to run on, defaults to the current branch), `--attempts <N>` (best-of-N,
default 1), `-c key=value`, `--enable` and `--disable <FEATURE>`. There is no `-m`:
cloud's model is fixed (Sol medium), so a cloud brief says "lane: cloud" (rule 27).
Environment: published as `deepsignal`, both repos, public internet off, package
managers on, an install script. The ENV_ID is Eugene's to give; keep it in
`docs/STATE.md`, not in prompts.

```
codex cloud exec --env <ENV_ID> --branch deepsignal/<module> --attempts 1 "$(cat /private/tmp/deepsignal/<module>/brief.md)"
```
```
codex cloud
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
`codex cloud` with no arguments opens the task browser. The branch must already exist
on the fork (they do, at 3b4b76e). Unverified: what `status`, `diff` and `apply` take
and print; check each with `--help` on first use.
Then the lead pushes the result as `deepsignal/<module>` on the fork, runs the Linux
gate on the sha, and routes an Astra 6.2 review. First job on a new environment is a
small Luna smoke test (a one-line change and its test), recorded in the ledger.

Needs Eugene once (account settings): connect `eugenevivino/openrvdas` in Codex
cloud; environment with Python 3.12, dependencies installed in its setup script,
agent internet off after setup; then send the environment id.

## Math-heavy work goes to Astra on a Mac, never cloud (Eugene 2026-11-18)
Anything with real math (uncertainty, drift, dependency or lag estimation, filtering, geometry,
formula libraries) is built and reviewed by `gpt-6.2-astra` at `high` (or `ultra` for decisions) on the
MacBook or the Mini, with `KALON_ALLOW_ASTRA=1`. Cloud is Sol medium and is for plain code, adapters,
pages, writers and harnesses. The Mini is a second Mac lane (Eugene 2026-11-18): one heavy job, 4 GB free-RAM
floor, own scratch folder `/private/tmp/deepsignal/`, never `/private/tmp/kalon`.

