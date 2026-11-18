# Brief: harness `fixture` (stock OpenRVDAS replay into a real cache, one command)

- Decision: D-CONSOLE1, MVP #1 stable integration. Risk tier: low (test tooling only). Python only, no Node.

## Goal
One command starts a real, stock OpenRVDAS stack that replays NBP1406 data into a real CachedDataServer, so the console, the soak runner and the source-loss test all run against the real thing.

## Build
- Package `contrib/deepsignal/test/harness/` (`__init__.py`, `fixture.py`, `cruise.yaml`, `README.md`).
- `python3 -m contrib.deepsignal.test.harness.fixture up [--port 0] [--speed 1.0] [--seconds N]` starts:
  1. `server/cached_data_server.py` on a free loopback port (or the one given).
  2. The stock `server/logger_manager.py` with a small cruise definition `cruise.yaml` and an in-memory or sqlite ServerAPI (whichever stock option works headless; read the manager's argparse and choose; say which in the report). The manager must publish `status:logger_status` to the cache.
- `cruise.yaml` loggers replay NBP1406 files with stock components only: LogfileReader with `use_timestamps: true`, ParseTransform with the repo's device definitions, and CachedDataWriter to the cache. At least these loggers:
  - `mwx1` (met).
  - `s330` (gyro/GNSS).
  - `knud1` (depth).
  - `true_winds`, if the stock true-winds config in test/NBP1406 can be reused.
  - Use the paths that exist on this branch (the contrib tree has NBP1406 at `test/NBP1406/<inst>/...`; list them and pick).
- Prints one line: `READY ws://127.0.0.1:<port> loggers=<n> fields=<n>` once the first records are in the cache; then runs until Ctrl-C or `--seconds`.
- `down` and a Python API `with Fixture(...) as fx: fx.ws_url, fx.kill_logger(name), fx.logger_pids(), fx.stop()` for tests.
- Cleans up every child process on exit, including on exceptions (use process groups).
- No writes outside a temp dir.

## Tests first
`contrib/deepsignal/test/harness/test_fixture.py`:
- `up` reaches READY within 30 s.
- A websocket client subscribed via the cache protocol receives at least one MwxAirTemp, and `status:logger_status` with all loggers RUNNING within 30 s.
- `down` leaves no child processes.

Mark these slow tests `@pytest.mark.slow` (they still run in acceptance).

## Scope
`contrib/deepsignal/test/harness/**` only. Core OpenRVDAS files are read-only.

## Acceptance (repo root)
```
python3 -m pytest contrib/deepsignal/test/harness/ -v
```
```
flake8 contrib/deepsignal/test/harness/
```
