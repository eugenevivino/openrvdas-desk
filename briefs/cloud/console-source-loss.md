You are building ONE piece of the DeepSignal Console, a display overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/console-harness-source-loss` from `origin/deepsignal/console-harness-fixture` (if `deepsignal/console-harness-source-loss` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/console-harness-source-loss`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. Add no dependency of any kind. No network.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------

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
