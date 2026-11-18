# Brief: joint #197 CDS lockdown plus console installer gate (CRITICAL, security)

- Branch `deepsignal/sec-cds-joint` at edec001 (the checked-out branch) = console-mvp 0fd4dee plus a clean merge of `deepsignal/sec-cds-lockdown` eadb0a2. CRITICAL: security and a core change (`server/cached_data_server.py`). Push-only; never auto-merged; Eugene decides.
- Lane: Mac, `gpt-6.2-sol` high. Then one Astra ultra review limited to this diff.
- Why (console final re-review, row 3, VERIFIED): the installer fails closed without #197, but with #197 present the installer classifies its own `127.0.0.1:8767` relay route as unsafe, and `check_cds.py` exits 2 on the installer's `--nginx-react-config` and `--console-source` arguments. The positive gate test skipped. On this branch it now runs and fails (RED baseline): `contrib/deepsignal/console/install/test_nginx_site.py::InstallTests::test_real_197_gate_through_django_and_react_nginx`.

## Fix exactly this
1. `contrib/deepsignal/security/check_cds.py`: accept `--nginx-react-config PATH` (the React nginx template; check it like `--nginx-config`) and `--console-source PATH` (the console checkout the installer deploys; read-only use, document what is checked). Unknown arguments still exit 2.
2. Classify the `/cds-ws` location that proxies to the #197 gateway on `127.0.0.1:8767` as the allowed read-only relay in BOTH nginx templates (Django and React). Any route that reaches publish-capable CDS (port 8766 or the CDS UDP bind) directly stays unsafe. Fail closed on anything unparseable.
3. Installer side (`contrib/deepsignal/console/install/install.sh`, `nginx-site.awk`): call the checker with exactly the arguments it supports, from the trusted root-owned location the round already introduced; keep failing closed when the checker is absent.
4. Keep D-SEC0: the browser path is only the same-origin `/cds-ws` relay; subscribe works, publish is refused, the cache stays unchanged.

## Regression tests (each fails at edec001, passes after)
- The real checker runs against the REAL installer output (the nginx site files the installer writes in a temp root) for the Django and the React template: relay accepted, subscribe succeeds, publish refused, cache unchanged.
- A template whose `/cds-ws` points at 8766 (direct CDS) or that exposes the UDP bind is rejected, through the installer, with a non-zero exit and no nginx change.
- `check_cds.py` accepts `--nginx-react-config` and `--console-source`, and still exits 2 on an unknown argument.
- `test_real_197_gate_through_django_and_react_nginx` passes without skipping.

## Acceptance (exact commands, from repo root)
```
python3.12 -m pytest -p no:cacheprovider contrib/deepsignal/test/security contrib/deepsignal/console/install contrib/deepsignal/test/console/test_install.py test/server/test_cached_data_server_host.py -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal
```

## Scope
Only `contrib/deepsignal/security/**`, `contrib/deepsignal/test/security/**`, `contrib/deepsignal/docs/security-cds.md`, `contrib/deepsignal/console/install/**`, `contrib/deepsignal/test/console/test_install.py`, `contrib/deepsignal/console/docs/install.md`. Do not change `server/cached_data_server.py` beyond what #197 already did; no console UI source.

## Non-goals and banned
No new features, no deleted, skipped or loosened tests, no sleeps, no new dependencies, no sub-agents, no weakening of fail-closed behavior.

## Stop rule
Report any finding that needs a change to the #197 or console design instead of changing it.
