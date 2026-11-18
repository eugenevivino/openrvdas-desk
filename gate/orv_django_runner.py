"""Django test runner that records one row per test for the gate.

Used as: python manage.py test test.django_gui --testrunner=orv_django_runner.Runner
with this directory on PYTHONPATH and ORV_DJ_ROWS set to the output file.
Writes `django::<test id><TAB>PASS|FAIL|SKIP` rows, then
`django::__COMPLETE__<TAB>PASS` only if every started test was recorded.
An early stop leaves the run incomplete even when the recorded counts agree.
Structured results instead of parsing verbose text: Django tests log to the
console mid-line, which makes text parsing unreliable.
"""
import os
import unittest

from django.test.runner import DiscoverRunner


class _Recording(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rows = {}

    def _set(self, test, status):
        name = "django::" + test.id()
        # FAIL is sticky: a failed subtest fails its parent test.
        if self.rows.get(name) != "FAIL":
            self.rows[name] = status

    def addSuccess(self, test):
        super().addSuccess(test)
        self._set(test, "PASS")

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._set(test, "FAIL")

    def addError(self, test, err):
        super().addError(test, err)
        self._set(test, "FAIL")

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._set(test, "SKIP")

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self._set(test, "PASS")

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self._set(test, "FAIL")

    def addSubTest(self, test, subtest, err):
        super().addSubTest(test, subtest, err)
        if err is not None:
            self.rows["django::" + test.id()] = "FAIL"


class Runner(DiscoverRunner):
    def get_resultclass(self):
        return _Recording

    def run_suite(self, suite, **kwargs):
        result = super().run_suite(suite, **kwargs)
        out = os.environ["ORV_DJ_ROWS"]
        rows = getattr(result, "rows", {})
        with open(out, "w", encoding="utf-8") as f:
            for name in sorted(rows):
                f.write("%s\t%s\n" % (name, rows[name]))
            # Error holders (setUpClass failures) are recorded but not counted
            # in testsRun, so require at least testsRun rows.
            if result.shouldStop:
                f.write("django::__INTERRUPTED__\tFAIL\n")
            elif result.testsRun > 0 and len(rows) >= result.testsRun:
                f.write("django::__COMPLETE__\tPASS\n")
            else:
                f.write("django::__COUNT_MISMATCH__ ran=%d rows=%d\tFAIL\n" % (result.testsRun, len(rows)))
        return result
