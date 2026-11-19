# Brief: CDS gate redesign, slice 2 of 3 (D-PILOT1; CRITICAL, security)

- Branch `deepsignal/sec-cds-joint` (the checked-out branch; base 82c8f3d). Design: desk `research/2026-11-19-cds-gate-redesign.md` (read it; it is the spec). Prior reviews: `research/2026-11-19-sec-cds-joint-review.md` and `-review-r2.md`. Lane: Mac, `gpt-6.2-sol` high, slices 1, 2, 3 in order. Push-only, never auto-merged; Eugene approves the merge.
- Every behavior below needs a regression test that fails at 82c8f3d. Fail closed on anything unparseable or unexpected. No sleeps, no new dependencies, no sub-agents, no deleted or loosened tests (a test that asserted the old static-parsing behavior may be replaced only by a test of the new behavior that covers the same risk; say which).

## Slice 2: the installer owns the nginx config
1. The installer renders ONE fixed nginx site from a template in the repo: console static files plus one `/cds-ws` location to the gateway on 127.0.0.1:8767, with an explicit allowed-origin list (the console's configured origin or origins), not a comparison with `Host`. Test: the rendered file is byte-identical to the template with the parameters filled in.
2. Before writing, it inventories the effective nginx config (`nginx -T` when nginx is present; parse the files otherwise) and REFUSES to install if it finds any vhost or include it did not render that proxies to or listens near CDS ports, any `stream` block referencing a CDS TCP or UDP port, or anything it cannot classify. It prints the list and stops; no file changes. Test: each such case refuses with a non-zero exit and no nginx change.
3. It always reloads nginx after writing, and confirms the reload (an idempotent run also reloads). Test: an idempotent run reloads (review r2 finding 6).
4. `check_cds.py` static parsing is retired. Keep only a small guard that the installed site still matches the rendered template; mismatch fails. Remove the console source parsing (the probe in slice 3 checks the served bundle instead).

## Scope
`contrib/deepsignal/console/install/**`, `contrib/deepsignal/security/check_cds.py`, `contrib/deepsignal/security/nginx/**`, `contrib/deepsignal/test/security/**`, `contrib/deepsignal/test/console/test_install.py`, `contrib/deepsignal/console/docs/install.md`, `contrib/deepsignal/docs/security-cds.md`.

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
