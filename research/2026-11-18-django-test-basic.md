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
