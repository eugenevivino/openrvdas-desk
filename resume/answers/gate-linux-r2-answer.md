**Verified**

- Head SHA `e4a07c2ac52a43fcaeaa9fa1f5ac9812eb782ef3` on `gate/linux-actions`, with uncommitted edits.
- RED receipt, Python 3.12.16, gate code identical to `16669b1`: `Ran 43 tests in 9.037s` → `FAILED (failures=5, errors=1)`. [RED log](/private/tmp/deepsignal/gate-linux-r2.mU5LBW/red.log)
- GREEN receipt, Python 3.12.16: `Ran 43 tests in 9.720s` → `OK`. [GREEN log](/private/tmp/deepsignal/gate-linux-r2.mU5LBW/green.log)
- flake8 7.5.0 passed on the edited test file. `flake8 gate` reported 30 pre-existing E501 violations. `bash -n` and `git diff --check` passed. [Flake8 log](/private/tmp/deepsignal/gate-linux-r2.mU5LBW/flake8.log)

**What changed**

- The gate records `/etc/os-release` `ID` and `VERSION_ID` in `meta.txt`, requires Ubuntu 22.04, and documents that fork code can forge receipts.
- It pins `flake8==7.5.0` and `pytest-timeout==2.4.0` from the Mini’s 2026-11-18 venv snapshot, writes `pip-freeze.txt`, and records NUL-delimited lint paths in `changed.txt`. [Gate script](/private/tmp/deepsignal/gate-linux/gate/gate-linux.sh)
- The lint stub now returns two paths that exist in the fixture checkout. Fifteen tests cover lint rows, refusal paths, receipt evidence, and `finish()` rejecting a missing `__END__` after every stage passed. [Tests](/private/tmp/deepsignal/gate-linux/gate/tests/test_gate_linux.py:182)

**New tests** (all names start with `test_linux_gate_`)

- `records_flake8_pass_and_changed_paths`, `records_flake8_violation_as_red`, `refuses_flake8_crash_with_empty_output`
- `finish_refuses_missing_end_after_all_stages_pass`
- `refuses_wrong_python`, `refuses_non_linux_uname`, `refuses_malformed_sha`, `refuses_existing_receipt_directory`
- `refuses_pytest_exit_status_disagreeing_with_rows`, `refuses_django_exit_status_disagreeing_with_rows`
- `records_runner_release`, `refuses_unsupported_release`, `refuses_unsupported_distribution`
- `pins_lint_and_timeout_and_records_pip_freeze`, `refuses_failed_pip_freeze`

**Inferred / pending**

- The existing `*.txt` glob should upload both evidence files. Verified the three pinned action SHAs in the workflow. Real Ubuntu Actions run and artifact upload: **NOT RUN**.