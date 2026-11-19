# Brief: CDS gate redesign, slice 3 of 3 (D-PILOT1; CRITICAL, security)

- Branch `deepsignal/sec-cds-joint` (the checked-out branch; base 82c8f3d). Design: desk `research/2026-11-19-cds-gate-redesign.md` (read it; it is the spec). Prior reviews: `research/2026-11-19-sec-cds-joint-review.md` and `-review-r2.md`. Lane: Mac, `gpt-6.2-sol` high, slices 1, 2, 3 in order. Push-only, never auto-merged; Eugene approves the merge.
- Every behavior below needs a regression test that fails at 82c8f3d. Fail closed on anything unparseable or unexpected. No sleeps, no new dependencies, no sub-agents, no deleted or loosened tests (a test that asserted the old static-parsing behavior may be replaced only by a test of the new behavior that covers the same risk; say which).

## Slice 3: the runtime black-box probe
One small probe (`contrib/deepsignal/security/probe_cds.py`), run at install (after the reload), by a `--check` command for Self-test, and in the Linux CI runner. From a non-loopback address of the host (or a second address given on the command line) it asserts:
1. TCP 8766 is refused, and every configured CDS UDP port (read from the CDS supervisor config, all of them) is unreachable (review r2 findings 1 and 4).
2. A WebSocket upgrade on `/cds-ws` with a foreign Origin gets 403, including on the default vhost with a matching Host (finding 3), and no other route reaches 8767 (finding 2).
3. A subscribe through `/cds-ws` returns a fresh nonce value written for this run through the loopback CDS (finding 7; the nonce changes every run and the probe checks its timestamp and value).
4. A publish through `/cds-ws` is refused and the cache is unchanged.
5. The served `dist` bundle (fetched through nginx) uses the same-origin `/cds-ws` URL (finding 10).
Any failure exits non-zero with a one-line reason per check. Rename or extend the live nginx test so it runs this probe against real installer output for the Django and React templates; keep the name prefix `test_real_197_`.

## Scope
`contrib/deepsignal/security/probe_cds.py` (new), `contrib/deepsignal/console/install/**`, `contrib/deepsignal/test/security/**`, `contrib/deepsignal/docs/security-cds.md`, `contrib/deepsignal/console/docs/install.md`.

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
