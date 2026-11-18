# Brief: harness `soak` (24 h soak runner)

- Decision: D-CONSOLE1, MVP #1 stable integration. Risk tier: low. Python only. Depends on the fixture (your base branch has it).

## Goal
Prove the stack the console depends on runs for 24 hours without leaking memory or backing up queues.

## Build
`contrib/deepsignal/test/harness/soak.py`:
- Command: `python3 -m contrib.deepsignal.test.harness.soak --hours 24 --report soak.json [--warmup-min 30] [--sample-s 60] [--clients 3]`.
- Starts the fixture.
- Opens N websocket clients that subscribe the way the console does (all fields, 300 s history on connect, then live), and one that reconnects every 10 min.
- Each minute it records the RSS of the cache server, the logger manager and each logger process (use `ps -o rss= -p` so there is no new dependency), messages per second received by the clients, and the clients' max receive lag (record timestamp vs receive time).
- The JSON report has the samples, a summary and a verdict. FAIL if any process RSS grows more than 5% from the end of warm-up to the end (compare medians of the first and last 10 samples after warm-up), if client lag median exceeds 5 s, or if any process died. The reason is given in plain words.
- A `--hours 0.05 --warmup-min 0.5 --sample-s 5` smoke mode used by tests.
- Exit code 0 PASS, 1 FAIL, 2 could not run.

## Tests first
`test_soak.py`:
- The smoke run completes with a PASS report and the right JSON shape.
- The verdict logic, unit-tested on synthetic samples: 4% growth passes, 6% fails, a dead process fails, high lag fails.

## Scope
`contrib/deepsignal/test/harness/soak.py`, `contrib/deepsignal/test/harness/test_soak.py`, `contrib/deepsignal/test/harness/SOAK.md`.

## Acceptance (repo root)
```
python3 -m pytest contrib/deepsignal/test/harness/test_soak.py -v
```
```
flake8 contrib/deepsignal/test/harness/soak.py contrib/deepsignal/test/harness/test_soak.py
```
Note: the real 24 h run is done by the lead on the Linux gate, not in this task.
