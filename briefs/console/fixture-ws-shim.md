# Brief: console harness fixture, websockets compatibility shim (fix round)

- Branch `deepsignal/console-harness-fixture`, base 12ca077 (fixture, attempt 2). Lane: cloud, Sol medium.
- Problem (verified on the MacBook): contrib master's 2024 `server/cached_data_server.py` (line ~967) calls
  `websockets.serve(handler_with_two_args, host, port)` using the legacy (websocket, path) handler signature. With
  websockets 14+ (installed: 17.4) the CDS thread dies with `TypeError: serve() missing 1 required positional argument:
  'handler'`, so the fixture never listens (`TimeoutError: CachedDataServer did not listen within 10 seconds`).
- Rule (D-UPSTREAM0): do NOT edit any upstream core file. `server/cached_data_server.py` stays untouched.

## Build exactly this
1. A small module in our harness, `contrib/deepsignal/test/harness/ws_compat.py`, that, when websockets >= 14 is
   installed, wraps `websockets.serve` so a handler written for the legacy `(websocket, path)` signature works:
   detect the handler's arity; for a two-argument handler call it as `handler(connection, connection.request.path)`;
   pass one-argument handlers through unchanged. On websockets < 14 it is a no-op. Applying it twice is harmless.
   Also cover the call form the 2024 CDS uses (positional handler, host, port; and keyword forms), whichever the
   current websockets API needs (the legacy module path or the new asyncio server), without silently dropping options.
2. Apply the shim in the fixture before the CDS starts, in the fixture process only (never globally at import of
   unrelated modules). It must not change any data the CDS serves.
3. Unit tests in `contrib/deepsignal/test/harness/test_ws_compat.py`: a one-argument handler and a two-argument
   (legacy) handler both receive a message over a real local websocket and see the right path; idempotent apply;
   no-op behaviour is documented for websockets < 14.
4. README in the harness folder: one paragraph on why the shim exists and that the clean long-term answer is a
   websockets<14 pin or a CDS fix, proposed upstream only after Eugene's approval (D-UPSTREAM0).

## Acceptance (exact commands, from repo root)
```
python3.12 -m pytest contrib/deepsignal/test/harness/ -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/test/harness/
```

## Scope
Only `contrib/deepsignal/test/harness/**`. No core files, no other modules.

## Non-goals and banned
No loosened or deleted tests, no bare except, no sleeps for ordering, no sub-agents.
