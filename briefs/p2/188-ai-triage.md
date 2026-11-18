# Brief: p2-ai-triage (AI watch assistant: event-triggered triage, local first, advise only)

- Decision: IDEAS #188, from Eugene's 2026-11-18 asks (config assist, sensor init, ecosystem and compression); build per D-NIGHT1
- Risk tier: high
- Module: exactly one. Branch `deepsignal/p2-ai-triage` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 5/3/3
- Depends on: inputs from #162 stream health, #165 time health, QARTOD flags, #167 runbooks, #168 timeline; escalation through the MCP gateway (#64); write fixes only as proposals to #65 and #154; model choice from #69 evals

## Goal
When something goes wrong, the tech gets a short, evidence-linked briefing in seconds:
- what broke in the chain
- the likely causes, ranked
- the matching runbook steps and past fixes
- the exact checks to do next

It costs almost nothing, because AI runs only on events, on a small model on the ship server, and works
with no internet. It only advises. Eugene, 2026-11-18: "have either local or off-prem AI analyze the data
regularly ... and help the techs fix the issue."

## Background facts (do not re-derive)
- Base is the contrib `master` tree at `3b4b76e`: it carries a 2024 core tree (old Transform base class,
  no BaseModule). Copy the import-compatibility approach of
  `git show origin/deepsignal/vector-wind:contrib/deepsignal/logger/transforms/vector_wind_average_transform.py`
  so the module also works on current core. If that branch is unreadable, write plain absolute imports
  and say so.
- Create empty `__init__.py` files only where missing, byte-identical to the wind branch (empty), so
  parallel branches merge cleanly.
- OpenRVDAS loads classes from a config with `class:` plus `module:` (for example
  `module: contrib.deepsignal.<module>.<file>`). Records may arrive as a DASRecord, a dict with
  `timestamp` and `fields`, a list of either, or None; handle all, pass None through.
- File ownership is disjoint across phase 2 tasks: you own ONLY the paths under Scope.
- Two tiers.
  - Tier 1 is the deterministic checks, which already run continuously at no AI cost: QARTOD flags,
    #162, #165, #79 and #10. They are inputs here.
  - Tier 2 is this module. It is never a continuous stream.
- llama.cpp `llama-server` and Ollama both serve an OpenAI-compatible `POST /v1/chat/completions`. Use
  only that HTTP shape through stdlib `urllib`, behind an injectable client. No SDK and no new dependency.
  Tests use a fake client; no network.
- Desk research: `research/2026-11-18-mcp-reference-architecture.md` (typed read-only tools, audit, query
  budgets, local baselines such as Qwen3.5-9B to qualify by #69) and `research/2026-11-17-ai-methods.md`.

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/ai_triage/`.

**Triggers** (`triggers.py`). A briefing is made only on:
- a #162 transition into DEGRADED or FAILED that holds for `hold_s` (default 60)
- an A1 or A2 alert
- a tech pressing "Explain" (`request(stream)`)
- the end-of-watch digest (times in config, default 0400, 0800, 1200, 1600, 2000, 0000 ship time)

Dedupe works by signature: sha256 of the stream, the failing stage and the sorted evidence kinds. The same
signature within `cache_hours` (default 6) reuses the cached briefing and marks it "same as before".

**Context pack** (`context.py`). Deterministic, at most `max_context_tokens` (default 6000, counted as
characters / 4):
- the chain summary for the stream and its affected outputs
- the last 30 minutes of transitions and `timeline.around()` from #168
- the current time-health verdict
- runbook causes for the failing stage from #167
- up to 3 prior incidents with the same or a near signature, with their recorded outcomes

Every item carries a ref id. No raw data streams, and no credentials or tokens, ever go into the pack.

**Model adapters** (`models.py`): `LocalModel(url, model)` and `CloudModel(url, model, token_env)`, the same
interface.
- Local is the default. Cloud is used only when `cloud.enabled`, the link is up (#156 link health field if
  present), today's cloud budget has room, and either the local answer failed schema validation twice or
  a tech asked for "second opinion".
- Cloud calls go through the MCP gateway when configured. Otherwise they go to a plain
  OpenAI-compatible URL the ship sets.
- Budgets in `ai_triage.yaml`:
  - `local.max_calls_per_hour` (default 30)
  - `local.timeout_s` (default 120)
  - `cloud.max_tokens_per_day` (default 200000)
  - `cloud.max_usd_per_month` (default 20, using prices the ship enters)
  - Every spend is metered. Over budget, it falls back to tier 1 output and says so.

**Output contract** (`schema.py`): JSON only. The fields are:
- `summary` (2 sentences at most)
- `causes`: up to 3, each `{cause, likelihood: high|medium|low, evidence: [ref ids]}`
- `checks`: ordered, each `{step, kind: look|read_only_test|write_action, runbook_ref?}`
- `cannot_tell` (bool)
- `confidence`

Validation:
- Any cause or check citing a ref that is not in the pack is dropped.
- A cause with no evidence is dropped.
- `write_action` steps are never executed. They become proposal stubs for #65 and #154, marked "needs
  approval", or plain text when those services are absent.
- An invalid answer after 2 tries falls back.

**Fallback** (no model, timeout or budget hit): a deterministic briefing from tier 1. It names the first
failing stage and lists the runbook causes for that stage in order. So a tech always gets help, and it is
labeled "no AI used".

**Audit and learning**:
- Every briefing goes to the #168 timeline as kind `ai_briefing`. The entry holds the pack hash, model,
  tokens, cost, latency and output.
- `record_outcome(briefing_id, worked: cause_index|none, note, who)` stores what fixed it.
- Weekly, `propose_runbook_updates()` turns confirmed outcomes into suggested runbook edits (a new cause,
  a reordering) as diffs for a person to accept in #167. It never edits a runbook itself.

**Surfaces**: the briefing JSON is published to the CDS as `ds_ai:<stream>:latest`, for the console's
alert detail and the trust view. The setup engine and MCP call `briefing(stream) -> dict`, pure over a
given snapshot.

**Privacy**: ship config decides whether cloud is allowed at all (default false). With the #116 release
policy, held-back fields and EEZ hold-back fields are removed from any pack sent to the cloud.

## Failing test first
`contrib/deepsignal/test/ai_triage/test_triage.py`, with a fake model client:
- Triggers fire only on held transitions, alerts, requests and digest times.
- A repeated signature uses the cache.
- The pack stays under the size limit and holds no secrets. Assert that a fake token string is absent.
- A hallucinated ref is dropped.
- A write action becomes a proposal and is never executed.
- An invalid JSON answer is retried, then falls back.
- The budget stops cloud calls and meters spend.
- Cloud is used only when enabled, the link is up and the budget allows it.
- Release-policy fields are stripped from cloud packs.
- The fallback briefing is correct and labeled.
- Timeline entries are written.
- An outcome is recorded.
- `propose_runbook_updates` emits a diff and never writes the runbook.

## Module contract
Docs `contrib/deepsignal/docs/ai_triage.md`. It covers:
- the two tiers, drawn as a small text diagram
- how to run a local model on the ship server (llama.cpp or Ollama, CPU-only works for event-driven use;
  expect tens of seconds per briefing on a 9B quantized model and say it is an estimate until #69
  measures it)
- the budget settings
- "advise only" in bold

A lead-run check against a real local model happens outside the sandbox.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/ai_triage -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/ai_triage contrib/deepsignal/test/ai_triage
```

## Scope
Create or change only: `contrib/deepsignal/ai_triage/**`, `contrib/deepsignal/test/ai_triage/**`, `contrib/deepsignal/docs/ai_triage.md`, `contrib/deepsignal/configs/ai_triage_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only.

## Usability (anything a tech sees or edits)
Answer each line of desk `docs/USABILITY.md` in the report, or N/A with a reason. Every config error is one
plain-English line naming the setting, what it saw, what it expected, and a good example.

## Trust boundaries and data integrity
Config and input files are hand-edited and untrusted: `yaml.safe_load` only, no `eval`. Never change or
drop an incoming value; only add fields or write new files. Missing or stale inputs are shown as such,
never guessed.

## Non-goals and banned
No core changes. No new dependency. No network. No refactors, renames or formatting outside Scope. No
loosened, skipped or deleted tests, no swallowed errors, no sleeps for test ordering.

## Stop rule
No code change needed: stop and report. Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Acceptance tails:
- Open questions:

## Addendum 2026-11-18 (Eugene: "It might be better if it was an API based model, frankly")
Provider is pluggable behind one OpenAI-compatible client (stdlib HTTP): the default configuration is an API
provider with the ship's own key (never in the repo), with hard daily and monthly caps, a satellite-bandwidth
cap and the 6k-token context pack unchanged. The local model (llama.cpp or Ollama) is the offline fallback
when the link is down or the cap is reached, and the deterministic briefing is the last fallback. Nothing is
sent until a key is configured: with no key the feature runs local or deterministic. Context packs are
redacted (no credentials, no personal names) before leaving the ship and every outbound request is logged
in the #168 timeline. This supersedes the earlier "local default, cloud off" wording; enabling the key and
the budget is still Eugene's call (MORNING), and outputs stay advise-only.
