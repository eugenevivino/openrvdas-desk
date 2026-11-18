# Brief: harness `source-loss` (kill and restart a logger)

- Decision: D-CONSOLE1, MVP #1 stable integration. Risk tier: low. Python only. Depends on the fixture (your base branch has it).

## Goal
Prove that when a data source dies, the stack makes it visible within 10 seconds and recovers on its own.

## Build
`contrib/deepsignal/test/harness/test_source_loss.py`, using the fixture's Python API:
1. Wait until `mwx1` fields are LIVE, judged at the data level: new MwxAirTemp records arrive at about 1 Hz.
2. Kill the `mwx1` logger process (SIGKILL).
3. Assert:
   - No new MwxAirTemp record arrives after the kill, with a 2 s allowance for in-flight records.
   - Using the console's freshness rule, ported as a small pure Python function in the test (age > 5T with T learned from the last 20 intervals is STALE), the field becomes STALE within 10 s of the kill.
   - `status:logger_status` shows `mwx1` as not RUNNING, or the manager restarts it, within 15 s.
   - The manager restarts it, and MwxAirTemp records resume within 60 s (stock LoggerManager restarts dead loggers).
4. A second case: stop the cache server. The client sees the connection drop. When it is restarted on the same port, a reconnecting client receives data again within 30 s.

Also add a browser variant `contrib/deepsignal/test/console/test_source_loss_browser.py`, marked `@pytest.mark.lead_run`. It loads the console against the fixture, kills `mwx1`, and asserts the tile shows STALE within 10 s, then LIVE after recovery.

## Scope
The two test files above, plus `contrib/deepsignal/test/harness/SOURCE-LOSS.md` (what it proves, how to run).

## Acceptance (repo root)
```
python3 -m pytest contrib/deepsignal/test/harness/test_source_loss.py -v
```
```
flake8 contrib/deepsignal/test/harness/test_source_loss.py contrib/deepsignal/test/console/test_source_loss_browser.py
```
