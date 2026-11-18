You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-ai-triage` from commit `3b4b76e` (the contrib master tree; it is in this fork's history, for example `git merge-base origin/deepsignal/vector-wind origin/deepsignal/instrument-history`) (if `deepsignal/p2-ai-triage` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-ai-triage`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML is already an OpenRVDAS dependency; add no other dependency. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-ai-triage (AI watch assistant: event-triggered triage, API model first, advise only)

- Decision: IDEAS #188, from Eugene's 2026-11-18 asks (config assist, sensor init, ecosystem and compression); build per D-NIGHT1
- Risk tier: high
- Module: exactly one. Branch `deepsignal/p2-ai-triage` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 5/3/3
- Depends on: #192 key vault (AI disabled until it merges); inputs from #162 stream health, #165 time health, QARTOD flags, #167 runbooks, #168 timeline; its `ai_guard` package (redaction, budget, audit) is shared with the inbound MCP gateway (#64); write fixes only as proposals to #65 and #154; model choice from #69 evals

## Goal
When something goes wrong, the tech gets a short, evidence-linked briefing in seconds:
- what broke in the chain
- the likely causes, ranked
- the matching runbook steps and past fixes
- the exact checks to do next

It stays cheap because AI runs only on events, with caching and a per-ship spending cap. It uses an
API-based model: DeepSignal calls the provider's API OUTBOUND through one egress proxy or allowlisted host. It degrades gracefully
offline, and it only advises. Eugene: "It might be better if it was an API based model, frankly." and
"starlink is exceptional though" (2026-11-18): design for connectivity as the normal case, with offline
as the exception path. Eugene, 2026-11-18: "have either local or off-prem AI analyze the data
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
- Two directions; do not mix them up.
  - **Outbound (this module):** DeepSignal calls an AI provider's API, and the ship's network sees one
    HTTPS destination. It does NOT go through the MCP server.
  - **Inbound (the MCP gateway #64, not this module):** an AI client such as Claude Desktop or Claude Code
    connects to DeepSignal's MCP server over the VPN or LAN to query and propose.
  - Both use the same `ai_guard` layer built here.
- Two tiers.
  - Tier 1 is the deterministic checks, which already run continuously at no AI cost: QARTOD flags,
    #162, #165, #79 and #10. They are inputs here.
  - Tier 2 is this module. It is never a continuous stream.
- Provider-pluggable through one small interface. The first adapter speaks the widely used
  OpenAI-compatible `POST /v1/chat/completions` shape. A second adapter speaks the Anthropic Messages API
  shape (`POST /v1/messages`). Both use stdlib `urllib` behind an injectable client, with no SDK and no new
  dependency.
- The optional local fallback (llama.cpp `llama-server` or Ollama) uses the same OpenAI-compatible shape.
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

**Model adapters** (`models.py`): `ApiModel(provider, url, model, key_env)` is the **primary path**, and
`LocalModel(url, model)` is optional. Both share one interface.
- **Enablement:** on by default once the #192 vault is present and a key is stored. Until #192 merges, it
  ships with AI disabled by default, and the tech gets tier 1 and runbook briefings only.
- Calls go directly to the provider URL. The only network path is
  `api.egress_proxy` (an HTTPS proxy URL) when set, else the provider host, which must be in
  `api.allowed_hosts`. Any other host is refused before a socket opens.
- **Keys:** the key is read only through the #192 vault (below). It is never in a config file, git, a
  log, a pack, argv or the environment.
- **Spending cap per ship** in `ai_triage.yaml`:
  - `api.max_usd_per_day` (default 2)
  - `api.max_usd_per_month` (default 30)
  - `api.max_tokens_per_call` (default 8000 in, 1000 out)
  - prices per million tokens entered by the ship
  - Every call is metered before and after. A call that would cross a cap is not sent; the tech gets the
    runbook fallback marked "budget reached".
- **Offline** (#156 link-health field says down, or the call fails to connect): the request goes into a
  disk queue (`queue.jsonl`, at most 50 entries, oldest dropped with a note). The tech gets the
  deterministic runbook briefing at once, marked "AI pending". When the link returns, queued items still
  relevant (the problem is still open) are sent within the caps, and the answer replaces the pending
  mark. If `local.enabled` (default false) and a local model answers, that answer is used meanwhile,
  labeled "local model".
- Retries: one retry on a timeout or 5xx, then fallback. Timeouts default to 60 s.

**Shared guard** (`contrib/deepsignal/ai_guard/`, owned by this task; the MCP gateway imports it later):
- `redact.py`: the redaction described under Privacy, below.
- `budget.py`: the meter, caps per period (day and month) and per-call limits, with a generic unit.
  - `check_and_reserve(cost, unit="usd", scope="default") -> bool` and `settle(reservation, actual)`.
  - Units are any string (`usd`, `tokens`, `requests`, `bytes`), each with its own caps, so the MCP gateway
    can reuse it for request counts and reply byte caps.
  - It persists to a small JSON file, with atomic writes.
- `audit.py`: append-only JSONL, exported to the #168 timeline, and tamper-evident.
  - Each record has a `prev_hash`: the SHA-256 of the previous line's exact bytes. The first record uses
    64 zeros.
  - `verify(path) -> {ok, records, first_break}`, where `first_break` is the line number of the first
    break.
  - Optional `sig`: an HMAC-SHA256 of the line without `sig`, keyed by a key loaded through
    `ai_guard.secrets` when `sign_key` is configured. `verify` checks the signatures too when it is given
    the key. The MCP gateway signs its apply records this way.
- **Keys come from the #192 vault, not `ai_guard`** (security architecture thread, 2026-11-18). `store_key`
  calls `vault.put("ai-triage", provider, value)` and `load_key` calls `vault.get("ai-triage", provider)`.
  - The vault is an AES-256-GCM envelope through platform OpenSSL, with a tpm2 KEK protector or else a 0400
    host-key file owned by the ai-triage service user. It works the same on Ubuntu 22.04, 24.04 and RHEL 9.
  - There is no plaintext path at all. Do not write any fallback that stores a key unencrypted.
  - #192 is not on your base. Code against the interface `put(namespace, name, value)`,
    `get(namespace, name) -> str`, `protector() -> "tpm2" | "hostkey"` through an injectable `vault`
    object. Import the real one lazily by its module path when present. If it is absent, AI assist is
    **disabled** and every surface says plainly: "AI assist needs the key vault (#192), not installed
    yet."
  - Keys are never accepted on the command line (shell history). They are read from stdin or the wizard.
- `secrets.py` keeps only token hashing:
  - `hash_token(token) -> str` and `check_token(token, stored) -> bool`: PBKDF2-HMAC-SHA256 from stdlib
    `hashlib`, at least 200000 iterations, with a random salt and a constant-time compare. Bearer tokens
    such as MCP access tokens are stored only this way, never in plaintext.
  - Both `store_key` and `load_key` run the commands behind an injectable runner for tests.

**Guided setup** (setup engine functions in `ai_triage/setup.py`, pure or behind injectable I/O, which the
wizard, console and CLI all call):
1. `providers() -> list`: the built-in provider choices with their default URLs and request shapes.
2. `store_key(provider, key)`: through the #192 vault.
3. `set_caps(daily_usd, monthly_usd, prices)`: validated, written to `ai_triage.yaml` (no secrets in it).
4. `test_call() -> dict`: one tiny fixed prompt. It reports ok or error in plain words (bad key, host not
   allowed, proxy unreachable, over budget), latency, tokens and cost.
5. `preview(stream) -> dict`: the exact redacted pack that would be sent for a stream right now, with
   counts of what was removed by each rule.
- CLI `python -m contrib.deepsignal.ai_triage setup` walks these five steps in order. It reads the key
  without echo.

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

**Privacy and redaction** (`redact.py`, applied to every pack before it leaves the ship): no raw data
series, only the compact pack. It strips anything that looks like a credential, token, password,
private key, email address or phone number. It removes the #116 held-back fields, and while `eez_inside`
it removes EEZ hold-back fields and rounds positions as #116 does. A ship can turn the API path off
(`api.enabled: false`) for a cruise with stricter terms. It is on by default.

## Failing test first
`contrib/deepsignal/test/ai_triage/test_triage.py`, with a fake model client:
- Triggers fire only on held transitions, alerts, requests and digest times.
- A repeated signature uses the cache.
- The pack stays under the size limit and holds no secrets. Assert that a fake token string is absent.
- A hallucinated ref is dropped.
- A write action becomes a proposal and is never executed.
- An invalid JSON answer is retried, then falls back.
- The daily and monthly caps stop calls before sending, and spend is metered.
- Offline queues the request, gives the runbook fallback at once, sends it on reconnect only if still
  open, and caps the queue at 50.
- The optional local model is used only when enabled.
- Redaction strips secrets, emails, held-back fields and EEZ hold-back fields, and rounds positions.
- `api.enabled: false` sends nothing.
- A host outside `allowed_hosts` is refused before any connection.
- The key is never in the YAML, logs, packs, argv or the environment. Assert it across all written files
  in a temp dir and in the fake process environment.
- A fake vault with each protector (`tpm2`, `hostkey`, using a fake protector runner): the round trip
  works, and the self-test wording names the protector.
- With no vault, AI is disabled, the message is exact, and no call is attempted.
- `test_call` maps a fake 401, a DNS failure and the budget-exceeded case to plain messages.
- `preview` shows removal counts.
- Audit hash chain: verify passes; editing, deleting or reordering a line reports the first break.
- HMAC signatures verify, and a wrong key fails.
- The budget works with units `usd`, `tokens` and `bytes` independently, and `settle` corrects reservations.
- Token hash round trip, a wrong token fails, and the stored form contains no plaintext.
- Both provider adapters build the right request shape.
- The fallback briefing is correct and labeled.
- Timeline entries are written.
- An outcome is recorded.
- `propose_runbook_updates` emits a diff and never writes the runbook.

## Module contract
Docs `contrib/deepsignal/docs/ai_triage.md`. It covers:
- the two tiers, drawn as a small text diagram
- the two directions (outbound API here, inbound MCP in #64), drawn as a small diagram
- the five setup steps
- the spending caps, with a worked cost example: say 40 briefings a day at about 7k tokens each, using
  prices the ship enters, marked as an example only
- what happens offline
- the optional local model
- "advise only" in bold

A lead-run check against a real API model happens outside the sandbox.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/ai_triage -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/ai_triage contrib/deepsignal/test/ai_triage
```
```
python3.12 -m unittest discover -s contrib/deepsignal/test/ai_guard -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/ai_guard contrib/deepsignal/test/ai_guard
```

## Scope
Create or change only: `contrib/deepsignal/ai_triage/**`, `contrib/deepsignal/test/ai_triage/**`, `contrib/deepsignal/docs/ai_triage.md`, `contrib/deepsignal/configs/ai_triage_*.yaml`, and empty `__init__.py` files where missing. Everything else is read-only. Also own `contrib/deepsignal/ai_guard/**` and `contrib/deepsignal/test/ai_guard/**`.

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
