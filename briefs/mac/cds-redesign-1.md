# Brief: CDS gate redesign, slice 1 of 3 (D-PILOT1; CRITICAL, security)

- Branch `deepsignal/sec-cds-joint` (the checked-out branch; base 82c8f3d). Design: desk `research/2026-11-19-cds-gate-redesign.md` (read it; it is the spec). Prior reviews: `research/2026-11-19-sec-cds-joint-review.md` and `-review-r2.md`. Lane: Mac, `gpt-6.2-sol` high, slices 1, 2, 3 in order. Push-only, never auto-merged; Eugene approves the merge.
- Every behavior below needs a regression test that fails at 82c8f3d. Fail closed on anything unparseable or unexpected. No sleeps, no new dependencies, no sub-agents, no deleted or loosened tests (a test that asserted the old static-parsing behavior may be replaced only by a test of the new behavior that covers the same risk; say which).

## Slice 1: loopback-only CDS and a hardened gateway
1. CDS binds TCP 8766 on 127.0.0.1 only by default (the #197 `--host` change), and UDP only on the named instrument interface (`--udp_interface`); every configured UDP port honors it. The shipped supervisor config for CDS uses these. Test: the CDS refuses to start on a wildcard or non-loopback TCP host unless an explicit override flag is given, and each configured UDP port binds only the named interface.
2. The gateway (`contrib/deepsignal/security/cds_gateway.py`) listens on 127.0.0.1:8767 only (or a Unix socket), and only nginx reaches it. Test: a non-loopback listen address is refused.
3. Gateway receive limit: the WebSocket server sets `max_size=65536`, so an oversized browser message is refused before it is buffered (review r2 finding 8). Test: a 65537-byte message is refused and memory is not consumed for the whole message.
4. Wildcard cap: the gateway expands or refuses wildcard subscriptions before counting against the 200-field cap (review r2 finding 9). Test: one wildcard that matches more than 200 fields is refused.

## Scope
`server/cached_data_server.py` (only the #197 bind behavior), `test/server/test_cached_data_server_host.py`, `contrib/deepsignal/security/cds_gateway.py`, `contrib/deepsignal/security/supervisor/**`, `contrib/deepsignal/test/security/**`, `contrib/deepsignal/docs/security-cds.md`.

## Acceptance (exact commands, from repo root)
```
python3.12 -m pytest -p no:cacheprovider contrib/deepsignal/test/security contrib/deepsignal/console/install contrib/deepsignal/test/console/test_install.py test/server/test_cached_data_server_host.py -v -k "not real_197"
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal
```
The Mac has no nginx; tests that need it must be named `test_real_197_*` (the lead runs those on a Linux runner).

## Stop rule
Report any finding that needs a change to the design note instead of changing it.
