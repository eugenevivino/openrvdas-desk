Implemented the Linux gate on `gate/linux-actions`. Desk HEAD is `3ed64edbf51b2fbb913dff9e776b6897e63a7167`. The three files are ready for the lead to commit.

**VERIFIED**

- Added a manual Ubuntu 22.04 workflow with Python 3.12, read-only checkout permissions, and receipt uploads for GREEN, RED, and REFUSED runs. [linux-gate.yml](/private/tmp/deepsignal/gate-linux/.github/workflows/linux-gate.yml)
- Added a runner that checks the exact fork SHA, runs pytest, Django, and flake8, and uses the Mini gate’s receipt format and exact-name exceptions. [gate-linux.sh](/private/tmp/deepsignal/gate-linux/gate/gate-linux.sh)
- Test-first RED output from `python3 -m unittest discover gate/tests` was `FAILED (failures=7)`. Each assertion reported `gate-linux.sh: No such file or directory`. [test_gate_linux.py](/private/tmp/deepsignal/gate-linux/gate/tests/test_gate_linux.py)

| Added test | RED assertion |
|---|---|
| `test_linux_gate_refuses_missing_end` | `AssertionError: 127 != 2` |
| `test_linux_gate_refuses_wrong_checkout_sha` | `AssertionError: 127 != 2` |
| `test_linux_gate_refuses_failed_dependency_install` | `AssertionError: 127 != 2` |
| `test_linux_gate_excuses_exact_macos_failure` | `AssertionError: 127 != 0` |
| `test_linux_gate_rejects_macos_failure_prefix` | `AssertionError: 127 != 1` |
| `test_linux_gate_preserves_unexcused_django_failure` | `AssertionError: 127 != 1` |
| `test_linux_gate_refuses_interrupted_pytest` | `AssertionError: 127 != 2` |

- GREEN output was `Ran 28 tests` and `OK`. Bash syntax and workflow YAML checks passed. An offline lint fixture produced all three verdicts.

**INFERRED**

- The new Python file appears flake8-clean by inspection. `flake8 gate` was unavailable locally, and existing gate files contain lines over 79 columns.
- Fork SHA `1a6f1edb786771c9dceeeeaf02e9d11d12bad6a9` is expected to return RED on Django `TestDjangoServerAPI.test_basic` alone. The hosted RED receipt, verdict, and receipt SHA-256 are pending the lead’s dispatch.

**Workflow run link**