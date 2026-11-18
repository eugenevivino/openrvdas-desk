# DeepSignal Approval Service and Receipts (#194, extends SECURITY-ARCHITECTURE.md section 8.3)

- Status: DRAFT v1, 2026-11-18. Answers MCP design review findings F1 and F2
  (desk `research/2026-11-18-mcp-design-review.md`, 8699cfe).
- IDEAS: #194 widens from "Signed config history" to "Approval service and signed config history".
  No new number needed.
- Module: `contrib/deepsignal/security/approvals/`. Branch `deepsignal/sec-approvals`.
- Phase: v2 (lands before the first remote or AI-originated write; #56 corrections and #130
  instrument-init are the first users). Merge waits for Eugene.

## 1. Rule

Every write path (MCP `apply`, REST #105 writes, console corrections #56, calibration #164,
instrument init #130, EEZ #137, config deploy) needs a **receipt** issued by one approval service
after a human approves on one console screen. A client can never approve on its own behalf: the
agent identity cannot reach the approval screen, cannot hold a human session, and the service
refuses any approval where approver = proposer or approver is a service identity.

## 2. Components and identities

```
 agent (MCP server, AI, REST client)  -- service user ds-mcp / ds-ai, token only, no web login
      | POST /v1/requests (frozen plan)          Unix socket /run/deepsignal/approvals.sock
      v
 approvals service  -- service user ds-approvals; signing key in vault ns "approvals" (#192)
      ^ human approve/reject                     receipts + consumption ledger (sqlite, WAL)
      |
 console /approvals/  -- behind #189 login, step-up MFA (#190) at the moment of approval
      
 executor (apply service #65) -- service user ds-apply; POST /v1/receipts/consume, then executes,
                                 then POST /v1/outcomes
```

- Socket permissions: `ds-mcp`, `ds-ai`, `ds-rest` may call only `requests` and `GET` status;
  `ds-apply` only `consume` and `outcomes`. Enforced by `SO_PEERCRED` uid checks, not by
  arguments.
- nginx denies `/approvals/` to any request carrying an MCP or REST bearer token, and to kiosk
  identities. Only a browser session can approve.

## 3. Frozen plan and impact statement

The agent submits a **frozen plan**: canonical JSON (RFC 8785 JCS) of exactly what the executor will
commit, per kind schema. The service computes `plan_digest = "sha384:" + hex(SHA-384(JCS bytes))`
and stores the plan. From then on the plan is immutable; any change is a new request.

The console renders the impact statement **from the stored plan only**, never from agent text:

| Kind | Rendered fields |
|---|---|
| `config.deploy`, `mode.change` | before/after values per key, affected loggers, destinations (files, DB, network writers), restart list |
| `correction.approve`, `calibration.set` | field, old/new coefficient or value, effective time range, affected outputs |
| `instrument.init` | device identity (device_id, serial, port), profile digest, **exact bytes** (hex and printable), send triggers with bounds, `irreversible` flag for persistent device commands |
| `eez.set` | zone, hold-back fields, start/end |

Agent free text is shown separately, labelled "Description from the requester (not verified)".
`irreversible: true` shows a red banner and requires typing the device or setting name.
Kinds listed in the two-person rule (SECURITY-ARCHITECTURE.md section 4) need two distinct human
approvals; the receipt is issued only after the second.

## 4. Receipt format (v1)

Envelope (JSON):
```json
{"typ": "ds-approval-receipt", "v": 1, "kid": "approvals-2026-11-a1b2",
 "payload": "<base64url of JCS bytes>", "sig": "<base64url DER ECDSA P-384 / SHA-384 over payload bytes>"}
```

Payload (JCS-canonical before signing):
```json
{
  "receipt_id": "uuid4",
  "vessel": {"call_sign": "KAOU", "install_id": "uuid4 set at install"},
  "request_id": "uuid4",
  "proposer": {"identity": "ds-mcp", "on_behalf_of": "shore user or null"},
  "kind": "instrument.init",
  "action": "instrument.write",
  "plan_digest": "sha384:...",
  "decision": "approve",
  "approvers": [{"user": "jsmith", "role": "tech", "auth": "webauthn", "auth_at": 1763460000}],
  "nonce": "base64url 32 random bytes, minted with the request",
  "idempotency_key": "client-supplied, 16-128 chars [A-Za-z0-9_-]",
  "irreversible": true,
  "device": {"device_id": "ctd-01", "serial": "SBE-1234", "profile_digest": "sha384:...",
             "bytes_digest": "sha384:...",
             "triggers": [{"event": "on_connect", "max_sends": 1, "window_s": 600}]},
  "issued_at": 1763460005,
  "expires_at": 1763460125
}
```
- `device` is required for `instrument.init` and absent otherwise (F2).
- `expires_at = issued_at + 120`. Time from the host clock; issuance refused when time health is
  STALE (receipt says why).
- Signature: ECDSA P-384 with SHA-384 through platform OpenSSL (FIPS profile, section 6.3). Public
  keys published at `/v1/keys` and shipped in `/etc/deepsignal/approvals/keys/` for offline
  verification.

## 5. API (Unix socket, HTTP/1.1, JSON)

| Call | Caller | Behavior |
|---|---|---|
| `POST /v1/requests` `{kind, plan, idempotency_key, description}` | agent | Validates plan against kind schema, stores it, returns `{request_id, plan_digest, approve_url: "/approvals/<request_id>", expires_at}`. Same idempotency key + same digest returns the existing request; same key + different digest is 409. Pending requests expire after 30 min. |
| `GET /v1/requests/{id}` | agent | `{state: pending|approved|rejected|expired|consumed, receipt?: envelope, outcome?}`. The receipt is returned to the agent so `apply` can pass it to the executor. |
| `POST /v1/receipts/consume` `{receipt, plan_digest, idempotency_key}` | executor | Atomic (single sqlite transaction): verify signature and `kid`, vessel matches this install, `decision = approve`, not expired, digest and idempotency key match, not consumed, then mark consumed and return `{ok: true, plan}`. The executor runs the returned plan only, never a plan it got elsewhere. |
| `POST /v1/outcomes` `{receipt_id, outcome, detail}` | executor | Records the result once. |

Retries and guessing:
- **Idempotency:** a `consume` or `requests` call with an idempotency key that already completed
  returns the recorded outcome, never runs twice.
- **Single use:** a consumed receipt returns `409 already_consumed` with the recorded outcome.
- **Guess limit:** 5 failed `consume` attempts (bad signature, wrong digest, wrong key) against one
  request void that request and raise an A2 alert; 20 per caller per hour lock that caller until
  an admin clears it.
- Every call writes an audit record (#193) with request id, digest, caller, result.

## 6. Human approval step (console `/approvals/<id>`)

1. #189 session required; role must allow `action` per #115 policy.
2. Step-up: fresh WebAuthn assertion (or TOTP where WebAuthn is not yet enrolled) at the moment of
   clicking Approve. v3: the WebAuthn challenge is derived from `plan_digest || nonce`, so the
   authenticator signature itself binds the human to that plan; the assertion is stored with the
   receipt.
3. Remote sessions (over VPN) can approve only kinds the ship has enabled for remote approval
   (default none). `instrument.init` is always on-ship only.
4. Reject requires a reason. Both outcomes are audited.

## 7. What the MCP thread does with this

- `apply(request_id)` = poll `GET /v1/requests/{id}` until approved, then hand the receipt to the
  executor. MCP never verifies-and-executes itself; the executor's `consume` is the only gate.
- MCP-side checks are advisory UX (show state, show expiry). Enforcement lives in the approval
  service and executor (matches IDEAS #65).

## 8. Tests the build must include

Self-approval refused (approver = proposer, service identity, kiosk); bearer-token request to
`/approvals/` refused by nginx snippet test; tampered payload, wrong vessel, expired, reused,
mismatched digest each refused; guess limit voids request; idempotent retry returns recorded
outcome without a second execution; two-person kinds need two distinct humans; `instrument.init`
receipt without `device` refused; impact page renders exact bytes from stored plan even when the
agent description lies; clock STALE refuses issuance.
