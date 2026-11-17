"""Locking test for the OpenRVDAS gate. Standard library only.

    python3 -I gate/tests/test_gate.py

Covers the verdict rules (GREEN, RED, REFUSED), junit completeness including
subtests, and every gate.sh refusal that can run without a fork clone.
"""
import os
import subprocess
import sys
import tempfile
import unittest

GATE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, GATE)
import gate_lib  # noqa: E402

SHA = "a" * 40


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


class VerdictTest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.exp = write(os.path.join(self.d, "exp.txt"), "# comment\ndjango::known.bad   # issue 1\n")

    def v(self, rows):
        return gate_lib.verdict(write(os.path.join(self.d, "r.tsv"), rows), self.exp)[0]

    def test_green(self):
        self.assertEqual(self.v("a\tPASS\nb\tSKIP\n__END__\tPASS\n"), "GREEN")

    def test_unexcused_fail_is_red(self):
        self.assertEqual(self.v("a\tPASS\nb\tFAIL\n__END__\tPASS\n"), "RED")

    def test_excused_fail_by_exact_name_is_green(self):
        self.assertEqual(self.v("a\tPASS\ndjango::known.bad\tFAIL\n__END__\tPASS\n"), "GREEN")

    def test_prefix_of_excused_name_is_not_excused(self):
        self.assertEqual(self.v("a\tPASS\ndjango::known.ba\tFAIL\n__END__\tPASS\n"), "RED")

    def test_missing_end_refuses_even_with_fails(self):
        self.assertEqual(self.v("a\tPASS\nb\tFAIL\n"), "REFUSED")

    def test_end_not_last_refuses(self):
        self.assertEqual(self.v("a\tPASS\n__END__\tPASS\nb\tPASS\n"), "REFUSED")

    def test_malformed_row_refuses(self):
        self.assertEqual(self.v("a\tPASS\nb\tMAYBE\n__END__\tPASS\n"), "REFUSED")

    def test_no_passing_rows_refuses(self):
        self.assertEqual(self.v("b\tSKIP\n__END__\tPASS\n"), "REFUSED")

    def test_missing_file_refuses(self):
        self.assertEqual(gate_lib.verdict(os.path.join(self.d, "none"), self.exp)[0], "REFUSED")


JUNIT = """<?xml version="1.0"?><testsuites><testsuite name="pytest" tests="%d">
<testcase classname="t.A" name="ok"/>
<testcase classname="t.A" name="sk"><skipped/></testcase>
<testcase classname="t.A" name="bad"><failure/></testcase>
</testsuite></testsuites>"""


class JunitTest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def rows(self, declared, summary):
        x = write(os.path.join(self.d, "p.xml"), JUNIT % declared)
        log = write(os.path.join(self.d, "p.log"), summary + "\n")
        return dict(gate_lib.junit_rows(x, log))

    def test_complete(self):
        r = self.rows(3, "1 passed, 1 failed, 1 skipped in 1.0s")
        self.assertEqual(r["pytest::t.A::bad"], "FAIL")
        self.assertEqual(r["pytest::t.A::sk"], "SKIP")
        self.assertIn("pytest::__COMPLETE__", r)

    def test_subtests_count_toward_declared(self):
        r = self.rows(13, "1 passed, 1 failed, 1 skipped, 10 subtests passed in 1.0s")
        self.assertIn("pytest::__COMPLETE__", r)

    def test_failed_subtests_fail(self):
        r = self.rows(5, "1 passed, 1 failed, 1 skipped, 2 subtests failed in 1.0s")
        self.assertEqual(r["pytest::__SUBTESTS_FAILED__ 2"], "FAIL")

    def test_count_mismatch_fails_and_is_not_complete(self):
        r = self.rows(9, "1 passed, 1 failed, 1 skipped in 1.0s")
        self.assertNotIn("pytest::__COMPLETE__", r)
        self.assertTrue(any(k.startswith("pytest::__COUNT_MISMATCH__") for k in r))

    def test_no_summary_line_is_not_complete(self):
        r = self.rows(3, "Traceback (most recent call last):")
        self.assertIn("pytest::__NO_SUMMARY_LINE__", r)
        self.assertNotIn("pytest::__COMPLETE__", r)


class RefusalTest(unittest.TestCase):
    """gate.sh must exit 2 and say REFUSED before touching any clone."""

    def run_gate(self, sha=SHA, **env):
        work = tempfile.mkdtemp()
        base = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": work,
                "ORV_WORK": os.path.join(work, "w"), "ORV_KALON_HOME": os.path.join(work, "k"),
                "ORV_LOCALHOSTNAME": "EugeneMacMini", "ORV_SKIP_PGREP": "1", "ORV_MIN_FREE_KB": "1"}
        base.update(env)
        p = subprocess.run(["bash", os.path.join(GATE, "gate.sh"), sha], env=base,
                           capture_output=True, text=True, timeout=60)
        return p.returncode, p.stdout + p.stderr, base

    def assertRefused(self, result, words):
        rc, out, _ = result
        self.assertEqual(rc, 2, out)
        self.assertIn("REFUSED", out)
        self.assertIn(words, out)

    def test_short_sha(self):
        self.assertRefused(self.run_gate(sha="abc123"), "40-hex")

    def test_wrong_machine(self):
        self.assertRefused(self.run_gate(ORV_LOCALHOSTNAME="Eugenes-MacBook-Pro"), "WRONG MACHINE")

    def test_kalon_lock(self):
        work = tempfile.mkdtemp()
        os.makedirs(os.path.join(work, "lock-w0"))
        self.assertRefused(self.run_gate(ORV_KALON_HOME=work), "Kalon")

    def test_disk_floor(self):
        self.assertRefused(self.run_gate(ORV_MIN_FREE_KB=str(10 ** 15)), "floor")

    def test_live_lock(self):
        work = tempfile.mkdtemp()
        os.makedirs(os.path.join(work, "gate.lock"))
        write(os.path.join(work, "gate.lock", "pid"), str(os.getpid()))
        rc, out, _ = self.run_gate(ORV_WORK=work)
        self.assertRefused((rc, out, None), "another gate")
        self.assertTrue(os.path.isdir(os.path.join(work, "gate.lock")), "refusal must not remove a live lock")

    def test_dead_lock_is_taken_over_then_no_clone_refuses(self):
        work = tempfile.mkdtemp()
        os.makedirs(os.path.join(work, "gate.lock"))
        write(os.path.join(work, "gate.lock", "pid"), "999999")
        rc, out, _ = self.run_gate(ORV_WORK=work)
        self.assertRefused((rc, out, None), "no clone")
        self.assertFalse(os.path.exists(os.path.join(work, "gate.lock")), "lock released on exit")


if __name__ == "__main__":
    unittest.main(verbosity=1)
