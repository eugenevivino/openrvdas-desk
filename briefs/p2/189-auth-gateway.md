# Brief: sec-auth-gateway (#189 Auth gateway)

- Decision: D-SEC1 section 3.1, D-SEC2 (login layer = Django accounts; **pending Eugene**). IDEAS #189
- Risk tier: high (security-critical; merge waits for Eugene, queued in MORNING.md)
- Module: exactly one. Branch `deepsignal/sec-auth-gateway`
- Base: fork `contrib/master` at the head of `deepsignal/sec-cds-lockdown` once its tests are green (needs the #197 gateway). Until then do not start.
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: fork only for now
- Value (techs/science/shore): 5/5/5
- Depends on: #197 (gateway and nginx snippets), #115 roles engine (`contrib/deepsignal/roles/`). Hold launch until D-SEC2 is approved; if Eugene picks another login layer, this brief is rewritten, not adapted.

## Goal
Every DeepSignal screen, live-data stream and API asks who you are once, at one door, and knows
your role everywhere after that.

## Background facts (do not re-derive)
- OpenRVDAS Django GUI already has `django.contrib.auth` users, sessions and the admin site; the
  install script serves it through nginx and uWSGI.
- nginx `auth_request` makes a subrequest to an internal location for each protected request:
  2xx allows, 401/403 denies; `auth_request_set` copies response headers into variables.
- #115 engine: `Policy.load(path)`, `policy.can(role, action)`, `policy.role_for(identity)`. Change
  request D-SEC3: lowest role is `viewer` (authenticated). If #115 still says `public`, map
  `public` to `viewer` in this module and flag it in the report; do not edit #115 files.
- #197 gateway reads `X-DS-User` and `X-DS-Role`; this brief makes them mandatory.

## Design (lead decisions; flag disagreement in the report)
1. Small Django app `contrib/deepsignal/security/authgw/` (installed into the existing Django
   project through a documented settings snippet, not by editing `django_gui/settings.py`):
   - `GET /auth/check` (internal only, nginx `internal;`): reads the Django session; returns 200
     with `X-DS-User` (username) and `X-DS-Role` (from #115 `role_for`) when logged in and the
     account is active and not expired; 401 otherwise. Optional `X-DS-Action` request header from
     nginx (for example `view.live`): 403 if `policy.can` says no.
   - Login and logout pages reuse Django auth views with a plain template matching the console
     design tokens; `next` redirect only to same-origin relative paths (open-redirect test).
   - Session settings snippet: `SESSION_COOKIE_SECURE`, `HTTPONLY`, `SAMESITE='Strict'`,
     `CSRF_COOKIE_SECURE`, idle timeout 30 min (tech/admin 15), absolute 12 h, enforced in
     middleware so both are honored (Django alone gives only one expiry).
   - Lockout: 5 failures in 15 min per account -> 15 min lock plus 1 s, 2 s, 4 s progressive
     delay per source address. Never applies to kiosk identities (#191 later). Admin unlock command.
2. nginx snippet `contrib/deepsignal/security/nginx/auth.conf`: `location = /auth/check` internal;
   `auth_request /auth/check` on console static path, `/cds-ws`, `/api/ds/` (REST #105) and MCP
   HTTP; `auth_request_set` the two headers and pass them upstream; strip client copies; 401
   redirects browsers to `/accounts/login/?next=...`, returns plain 401 for API clients.
3. #197 gateway change: refuse the upgrade (close 1008) when `X-DS-User` is empty, except when the
   gateway runs with `--allow-anonymous` (dev fixture only; logs a warning every minute).
4. Audit hook: emit one JSON line per login success, failure, lockout, logout and denied check to
   `contrib.deepsignal.security.audit_emit.emit(event)`. In this brief `emit` writes JSONL to a
   configured path; #193 replaces the body with the hash-chained signer. Keep the call sites.
5. TLS is assumed on (nginx); `check_auth` command reports FAIL if the server block is plain HTTP.
6. No MFA here (#190), no break-glass or kiosk (#191). Leave clear extension points.

## Failing test first
`contrib/deepsignal/test/security/test_authgw.py` (Django test client, sqlite):
- `test_check_401_without_session`, `test_check_200_sets_user_and_role_headers`
- `test_check_403_when_policy_denies_action`, `test_unknown_action_denied`
- `test_inactive_or_expired_account_401`
- `test_idle_timeout_and_absolute_timeout` (frozen clock, no sleeps)
- `test_lockout_after_5_failures_and_admin_unlock`
- `test_login_next_rejects_offsite_redirect`
- `test_cookie_flags_secure_httponly_samesite_strict`
- `test_audit_lines_for_login_fail_lockout_logout`
`contrib/deepsignal/test/security/test_cds_gateway_auth.py`: gateway refuses upgrade without
`X-DS-User`; accepts with it; `--allow-anonymous` logs the warning.
`contrib/deepsignal/test/security/test_nginx_snippets.py`: parses the snippets as text and asserts
every protected location has `auth_request`, client identity headers are cleared, `/cds-ws`
targets the gateway port.

## Integration and platform
New dependencies: none in this brief (allauth arrives with #190; note it there). Python 3.11+,
Django version as pinned by the fork. Linux target.

## Acceptance (exact commands, repo root, Linux, no browser)
```
python3.12 -m pytest contrib/deepsignal/test/security -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/security contrib/deepsignal/test/security
```
```
bash gate/remote.sh <head sha>
```

## Scope
Create or change only: `contrib/deepsignal/security/authgw/**`,
`contrib/deepsignal/security/audit_emit.py`, `contrib/deepsignal/security/nginx/auth.conf`,
`contrib/deepsignal/security/check_auth.py`, the auth-check part of
`contrib/deepsignal/security/cds_gateway.py`, the test files above,
`contrib/deepsignal/docs/security-auth.md`. Read-only: `django_gui/**`, install script, #115 files.

## Usability
Answer each line of `docs/USABILITY.md`. Login errors never reveal whether a username exists.
Lockout message says how long and who can unlock. Session expiry returns the user to the page
they were on after login.

## Trust boundaries and data integrity
Identity comes only from the Django session via nginx; never from a query parameter, body field
or client header. Backends trust `X-DS-*` only on loopback. Fail closed: if `/auth/check` errors
or times out, nginx denies. Acquisition is never affected by auth failures.

## Non-goals and banned
No MFA, kiosk, break-glass, tokens, LDAP or OIDC. No edits to `django_gui/**` or the install
script. No new dependencies. No refactors or default changes elsewhere. No skipped or loosened
tests, no sleeps. No writes in `/private/tmp` outside `/private/tmp/deepsignal/`.

## Report format
Diff summary, test names, RED and GREEN output, the settings snippet as shipped, anything
uncertain. Under 80 lines.

## Stop rule
Two fix rounds still red: stop and send to the decision desk through the lead.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Gate receipt sha256 and verdict:
- What changed, in three lines:
- Open questions:
