# Brief: sec-cds-lockdown (#197 Trust zones and CDS lockdown)

- Revision: r2, 2026-11-18, folds the Astra ultra review (desk `research/2026-11-18-security-architecture-review.md`, eb61677), SECURITY-ARCHITECTURE.md v2 sections 2.3 (T1, T14, T15) and 9.2.

- Decision: D-SEC0 (CDS exposure), D-SEC1 section 9.2. IDEAS #197
- Risk tier: high (security-critical; merge waits for Eugene, queued in MORNING.md)
- Module: exactly one. Branch `deepsignal/sec-cds-lockdown`
- Base: fork `contrib/master` at `3b4b76e` for the overlay part; the two-line core change below rides on the same branch and is listed separately in the report so it can be split later
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: fork only for now (nothing goes to OceanDataTools)
- Value (techs/science/shore): 5/5/5
- Depends on: nothing to build. Extends, does not duplicate, the D-SEC0 check in `briefs/console/INTEGRATION.md` (install-level bind, read-only proxy, publish-refusal test, self-test warning). #189 later puts this gateway behind login.

## Goal
Nobody on the ship LAN can push fake data into the live displays, and the live-data server is only
reachable through one guarded door.

## Background facts (verified 2026-11-18 on fork at v2.7.2, do not re-derive)
- `server/cached_data_server.py` calls `websockets.serve(..., host='', port=...)`: all interfaces.
  There is no `--host` argument. Message types handled: `fields`, `describe`, `publish`,
  `subscribe`, `ready`. `publish` needs no auth.
- `--udp` makes the CDS read JSON records through `UDPReader(port=..., mc_group=...)` with no
  `interface`, which means INADDR_ANY: a second unauthenticated injection path.
- **Both** install-script nginx templates (Django UI and React UI) proxy `location /cds-ws`
  straight to `http://localhost:${CACHED_DATA_SERVER_PORT}` with no auth.
- The console currently defaults to `ws://<host>:8766` (`contrib/deepsignal/console/src/pages.ts`).
  Changing that default is the console module's job (release blocker), not this brief's; this
  brief's check command reports it.
- The previous acceptance run of this brief had no passing attempt: CDS tests failed with
  connection errors. Before writing code, run `test/server/test_cached_data_server.py` on the base
  sha and paste the result, so a pre-existing gate-host problem is separated from new failures.
- **nginx cannot inspect WebSocket frames.** A "subscribe only" rule cannot live in nginx. If the
  INTEGRATION.md check was read that way, this brief is the mechanism that makes it true.
- `logger/writers/cached_data_writer.py` publishes to the CDS over a websocket. Local loggers must
  keep working unchanged.

## Design (lead decisions; flag disagreement in the report)
1. **Core change (small, backward compatible):** add `--host` to `cached_data_server.py`, default
   `''` (unchanged behavior), passed to `websockets.serve`. Add `--udp_interface`, default `None`
   (unchanged), passed to `UDPReader(interface=...)`. No other core edits.
2. **Read-only gateway (overlay):** `contrib/deepsignal/security/cds_gateway.py`, a small asyncio
   websocket relay listening on a Unix socket `/run/deepsignal/cds-gateway.sock` (mode 0660,
   group of the nginx user; path configurable) so only nginx can reach it and identity headers
   cannot be forged from a local TCP client. A `--tcp 127.0.0.1:8767` option exists for the test
   fixture only. For each browser connection it
   opens one upstream connection to the CDS at `127.0.0.1:8766` and forwards only client messages
   whose `type` is in an allowlist: `fields`, `describe`, `subscribe`, `ready`. Anything else
   (including `publish`, unknown types, non-JSON, frames over 64 KiB) gets
   `{"type": <type>, "status": 403, "error": "read-only connection"}` and is not forwarded.
   Server-to-client messages pass through unchanged, byte for byte, **when the field policy is
   allow-all** (the default in this brief).
   **Field policy hook (T15):** `FieldPolicy.allowed(identity, field) -> bool`, loaded from a
   callable path in config. When a non-allow-all policy is set, the gateway filters
   `subscribe` requests (wildcards are expanded against the CDS `fields` list first, then
   filtered), filters `describe` metadata, and drops disallowed fields from server-to-client data
   messages, re-serialized as JSON. Caps: back-history request (`seconds`) capped at 3600, at most
   500 fields after wildcard expansion. #189 supplies the real policy (roles, pages, kiosks,
   held-back fields).
3. Per-connection limits: max 4 messages/second sustained (burst 20), max 200 subscribed fields,
   max 50 concurrent connections. Over a limit: close with code 1008 and a plain reason.
4. Gateway reads two optional request headers set by nginx: `X-DS-User`, `X-DS-Role`. In this
   brief it only logs them (one line per connect/disconnect, no field values). #189 makes them
   mandatory. Headers are trusted only because the gateway binds 127.0.0.1; the README says so.
5. **nginx snippet template** `contrib/deepsignal/security/nginx/cds-ws.conf`: `location /cds-ws`
   proxies to the gateway on 8767 (never 8766), sets `proxy_set_header X-DS-User ""` and
   `X-DS-Role ""` (strip client copies), `client_max_body_size 64k`, Origin check against the
   configured server name. Plus `security-headers.conf`: CSP `default-src 'self'`,
   `frame-ancestors 'none'`, `X-Content-Type-Options nosniff`, `Referrer-Policy no-referrer`.
5b. A second snippet `cds-ws-react.conf` for the React UI server block, identical behavior.
   Both are tested.
6. **Check command** `python -m contrib.deepsignal.security.check_cds` prints one plain line per
   check and exits non-zero on any FAIL: CDS listening only on loopback (read `ss -ltnu` output
   through an injectable runner); UDP feed (if configured) bound to a named interface, not
   0.0.0.0, with a documented nftables allowed-source rule; Supervisor web UI off or loopback;
   console default URL is same-origin `/cds-ws` (WARN, owned by the console module); nginx
   `/cds-ws` in **both** templates points at the gateway socket; a live `publish` through the gateway is
   refused; a live `subscribe` through the gateway returns data. The console self-test from the
   install module calls this.
7. Sample supervisord program block for the gateway in `contrib/deepsignal/security/supervisor/`.
   Do not edit the install script; the install module adopts these files.

## Failing test first
`contrib/deepsignal/test/security/test_cds_gateway.py` (runs a real CDS on a free loopback port in
the test, as `test/server/test_cached_data_server.py` does):
- `test_publish_refused_through_gateway`: publish via gateway gets 403, CDS cache unchanged.
- `test_subscribe_passes_through`: a value published directly to the CDS reaches a gateway client
  byte-identical.
- `test_unknown_type_and_non_json_refused`, `test_oversize_frame_refused`.
- `test_rate_limit_closes_1008`, `test_field_cap`.
- `test_local_writer_still_publishes`: `CachedDataWriter` to the CDS port works as before.
- `test_policy_filters_subscribe_describe_and_data`, `test_wildcard_expanded_then_filtered`,
  `test_history_and_field_caps`, `test_allow_all_is_byte_identical`.
- `test_unix_socket_mode_0660`.
- Tests start the CDS with `--host 127.0.0.1` on a free port and wait for readiness with a
  bounded connect retry (max 5 s), never a fixed sleep.
`test/server/test_cached_data_server_host.py`: `--host 127.0.0.1` refuses a connection on a
non-loopback address of the test machine (skip with a reason if the runner has only loopback);
default `''` keeps old behavior.
`contrib/deepsignal/test/security/test_check_cds.py`: each check PASS and FAIL with a fake runner.

## Integration and platform
New dependencies: none (`websockets` is already required by the CDS). Python 3.11+, Linux target.

## Acceptance (exact commands, repo root, Linux, no browser)
```
python3.12 -m pytest contrib/deepsignal/test/security test/server/test_cached_data_server_host.py test/server/test_cached_data_server.py -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/security contrib/deepsignal/test/security server/cached_data_server.py test/server/test_cached_data_server_host.py
```
```
bash gate/remote.sh <head sha>
```

## Scope
Create or change only: `contrib/deepsignal/security/**` (except files owned by #189), 
`contrib/deepsignal/test/security/test_cds_gateway.py`, `contrib/deepsignal/test/security/test_check_cds.py`,
`contrib/deepsignal/docs/security-cds.md`, `server/cached_data_server.py` (only the two arguments),
`test/server/test_cached_data_server_host.py`, empty `__init__.py` where missing (byte-identical
empty files). Everything else read-only. Check dependents: `server/supervisord/*` templates,
`logger/writers/cached_data_writer.py`, console `bridge` module's websocket URL (must be `/cds-ws`).

## Usability
Answer each line of `docs/USABILITY.md`. Every refusal and every check line is one plain sentence,
for example: "FAIL: live-data server is listening on all network addresses (0.0.0.0:8766). Anyone
on the ship network can change what displays show. Fix: start it with --host 127.0.0.1."

## Trust boundaries and data integrity
Everything from a browser is untrusted. The gateway never alters server-to-client bytes and never
alters field names or timestamps. It must fail closed: if the allowlist cannot be loaded, refuse
every client message. A gateway crash must not affect the CDS or loggers.

## Non-goals and banned
No auth or login (that is #189). Only the field policy hook and allow-all default; real policies come from #189 and #137. No UDP source-address tagging (v2; needs a reader change). No change to CDS
default behavior. No edits to the install script. No new dependencies. No refactors, renames or
formatting outside the two new arguments. No skipped or loosened tests, no sleeps for ordering.
No writes in `/private/tmp` outside `/private/tmp/deepsignal/`.

## Report format
Diff summary with the core change listed separately, test names, RED and GREEN output, the exact
check_cds output on the test host, anything uncertain. Under 80 lines.

## Stop rule
Two fix rounds still red: stop and send to the decision desk through the lead.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Gate receipt sha256 and verdict:
- What changed, in three lines:
- Open questions:
