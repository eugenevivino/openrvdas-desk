# Django `TestDjangoServerAPI.test_basic` fails: root cause (lead's diagnosis)

Written before the Codex test run, so the two can be compared blind.

**Answer:** the lookup ignores the logger. The test cruise defines one config
named `off` and lists it under all four loggers (`test/django_gui/
test_django_server_api.py` lines 31 to 67). `load_configuration` saves one
`LoggerConfig` row per (logger, config) pair, so there are four rows named
`off`. Setting the second logger to its default then calls
`_get_logger_config_object_by_name('off')`
(`django_gui/django_server_api.py:180-186`), which does
`LoggerConfig.objects.get(name=config_name)` with no logger or cruise filter
and finds two rows. Verified by reading code and running the test on dev
1a6f1ed (Python 3.13 cloud, Python 3.12 Mini).

**Where the bug is:** in the Django API, not the test data (inferred, not yet
checked): the sqlite and in-memory APIs pass the same `test_basic` style
tests, so shared config names across loggers look intended.

**Minimal fix (proposed):** in `set_active_logger_config`, look up the config
by name and logger, for example
`LoggerConfig.objects.get(name=config_name, logger=logger)`, keeping the
`DoesNotExist` to `ValueError` mapping. Check other callers of
`_get_logger_config_object_by_name` for the same assumption.

**Regression test:** a cruise where two loggers share a config name; loading
it and switching modes must succeed and leave each logger pointing at its own
row.

## Codex check (MacBook, 2026-11-18, dev 1a6f1ed)

Codex (codex-cli 0.169.0, read-only, low effort) ran blind: exit 0, 50 s,
41,419 tokens. Verdict: same root cause as the lead's, same location
(`django_server_api.py:186`), same fix direction (filter by logger).

| | Lead | Codex |
|---|---|---|
| Root cause | name-only `get()` meets four rows named `off` | same, plus cited the row-creation loop (lines 823-838) |
| Bug in code or test data | Django API (inferred) | Django API, and checked sqlite and in-memory APIs (lines 373, 455, 103, 177) |
| Fix | filter by logger | `logger=None` argument, caller passes `logger=logger` |
| Extra | | `get_logger_config("off")` at line 311 is also name-only and stays ambiguous |
| Regression test | two loggers sharing a name | all four loggers select `off`, each row belongs to its logger, switch one and back |

Neither of us ran the fix. Next: apply Codex's diff on a topic branch, run the
new regression test red then green, and check line 311. Verdict on Codex as a
team member: good as Reviewer and for read-only diagnosis; its diagnosis found
one thing the lead missed.

Process note: this run did not go through Kalon's `~/bin/codex-run` wrapper
(which Kalon's cost rules require for Codex launches) and the MacBook default
model was gpt-6-astra, which those rules restrict. Future Codex runs on these
Macs launch through `~/bin/codex-run` with Sol low.
