# Brief: gate-linux-r2 (fix round 1 after independent review)

- Decision: D-ARCH5 (Linux only). Parent brief: briefs/gate-linux.md (built, branch `gate/linux-actions` 16669b1)
- Risk tier: medium
- Module: none (desk tooling). Branch: continue `gate/linux-actions` in the desk repo
- Lane: `mac`. `-m gpt-6.2-sol` high (rule 27), fresh session, under 40 turns, 45 minute cap
- Mac scratch path: `/private/tmp/deepsignal/gate-linux/` (rule 28). Re-clone or `git pull` the branch there first.
- Base: `gate/linux-actions` at 16669b1

## Goal
Close the review's must-fix items so the Linux gate can be merged to `main` and run for real.

## Failing test first
Add tests to `gate/tests/test_gate_linux.py` that FAIL on 16669b1, show the RED output, then fix:
1. flake8 loop: a changed file that passes (PASS row), a file that fails with an E or W code (FAIL row, verdict RED), and flake8 crashing with empty output (REFUSED). The `git diff` stub must return real changed paths so the loop runs.
2. Refusals: wrong Python (not 3.12), non-Linux `uname`, malformed sha such as `zz`, and an existing receipt directory.
3. A run where every stage passes but `__END__` is never appended must end REFUSED through `finish()` (the gate_lib check), not through an incomplete suite.
4. pytest or Django exit status that disagrees with its rows is REFUSED.

## Changes required in gate/gate-linux.sh and the workflow
- Pin `flake8` and `pytest-timeout` to exact versions. Use the versions the repo's own `dev` extra pins if it has them, otherwise the versions in `~/OpenRVDAS-Work/venv-3.12` on the Mini (read only, record which). After the install write `pip freeze` to `$rec/pip-freeze.txt` (the `*.txt` upload glob picks it up).
- Rename `changed.paths` to `changed.txt` (or add it to the upload glob) so the evidence shows which files were linted. Keep NUL separation internally if needed.
- Record `/etc/os-release` ID and VERSION_ID in `meta.txt`, and refuse unless it is Ubuntu 22.04.
- Add a short comment block in the script header: receipts are written by the same job that runs fork code, so a hostile fork could forge them; acceptable for our own fork only.
- Do NOT change the pinned action SHAs (verified against upstream tags: checkout 11bd719, setup-python a26af69, upload-artifact ea165f8).

## Acceptance (exact commands)
```
python3 -m unittest discover gate/tests
```
Report RED (new tests failing on 16669b1) and GREEN (all passing) on Python 3.12. flake8 is not installed on the MacBook: if you can run it from `~/OpenRVDAS-Work/venv-3.12/bin/python -m flake8 gate` on the MacBook (read only use of that venv), do; otherwise say NOT RUN.

## Scope
`gate/gate-linux.sh`, `gate/tests/test_gate_linux.py`, `.github/workflows/linux-gate.yml` (only if the artifact glob needs it). Everything else read-only. `gate/gate.sh`, `gate/gate_lib.py` and `gate/expected-failures.txt` are not to be edited.

## Non-goals and banned
No loosened or deleted tests, no swallowed errors, no sleeps. No changes outside `/private/tmp/deepsignal/`. No git commit or push by Codex (the lead commits).

## Report format
Diff summary, test names, RED then GREEN output, verified separate from inferred, under 40 lines.

## Stop rule
Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- GREEN receipt:
- What changed, in three lines:
- Open questions:
