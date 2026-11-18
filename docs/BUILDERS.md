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

## Two places Codex runs

| | Local (Mac, via `~/bin/codex-run`) | Cloud (Codex web or `codex cloud`) |
|---|---|---|
| Good for | macOS-only checks, serial and USB, work needing the Mini, anything that must match the gate machine | Linux-safe Python work: core fixes, overlay modules, tests, mechanical sweeps, several jobs at once |
| Guard | `codex-run`: model flag, sandbox, launch log | None of ours. The brief, an explicit model and effort, and the ledger row replace it |
| Output | Files in the workspace; lead commits and pushes | A task diff, or a branch or PR on the connected GitHub repo |
| Gate | Mini gate on the exact sha | Same. A cloud pass is a fast check, never the gate |

Either way: one bounded brief per fresh task, output capped, no secrets in the
prompt, cloud tasks get no internet beyond installing declared dependencies.

## Practical path (what exists, what is unverified)

Verified: Codex works on the MacBook (2026-11-18 trial). The cloud session
this desk runs in has no Codex login, so Claude cannot start Codex cloud itself.
Unverified, check on the MacBook first: `codex cloud --help` for the exact
subcommands (expected: submit a task with an environment id and a prompt, list
and status, fetch the diff, apply it locally); which Codex plan limits apply.

Needs Eugene, one time (account settings, rule 10):
1. In Codex cloud, connect `eugenevivino/openrvdas` and create an environment:
   Python 3.12, setup script installs the repo's declared dependencies, agent
   internet off after setup.
2. Tell us the environment id.

Then the loop, with nobody typing code:
1. Lead writes `briefs/<area>-<slug>.md` (with model, effort, failing test first).
2. A MacBook session (Eugene's Remote Control or a terminal he opens) runs
   `codex cloud` with the brief as the prompt, or `~/bin/codex-run` locally.
3. The result lands as a diff or a branch on the fork. Lead pushes it as
   `<area>/<slug>`, runs `gate/remote.sh <sha>`, routes an Astra review.
4. Eugene sends any upstream PR (rule 10).

Fallback if cloud is not set up: local `codex-run` on the MacBook, one job at a
time, as in `docs/CODEX.md` section 3.
