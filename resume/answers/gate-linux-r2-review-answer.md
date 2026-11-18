**Findings**

- **P1 VERIFIED** [gate/gate-linux.sh:81](/private/tmp/deepsignal/gate-linux/gate/gate-linux.sh:81) filters out Git type changes (`T`), so replacing a symlink with a regular Python file can produce GREEN without linting the new code.
- **P1 VERIFIED** [gate/gate-linux.sh:124](/private/tmp/deepsignal/gate-linux/gate/gate-linux.sh:124) treats flake8’s `E902 FileNotFoundError` as a lint violation, so a file that disappears before lint produces RED even though flake8 never read it and the required verdict is REFUSED.
- **P1 INFERRED** [gate/gate-linux.sh:79](/private/tmp/deepsignal/gate-linux/gate/gate-linux.sh:79) checks only for shared ancestry with `origin/dev`, so a fetchable contributor commit outside the fork’s own branches can pass the check and run with write access to its receipt.
- **P2 VERIFIED** [gate/gate-linux.sh:127](/private/tmp/deepsignal/gate-linux/gate/gate-linux.sh:127) writes filenames verbatim into TSV, so a valid Python filename containing a tab makes a passing lint row malformed and the gate returns REFUSED.

**Workflow and pins**

- **VERIFIED** Yes. `git diff --exit-code 16669b1..292117e -- .github/workflows/linux-gate.yml` returned 0 with no diff. I also read the workflow at `292117e` and found checkout `11bd719` in both checkout steps, setup-python `a26af69`, and upload-artifact `ea165f8`.
- **VERIFIED** `flake8==7.5.0` and `pytest-timeout==2.4.0` match the supplied Mini freeze. The fork’s `dev` extra at `1a6f1ed` pins neither tool. Flake8 7.5.0 allows `pycodestyle>=2.15.0,<2.16.0` and `pyflakes>=4.1.0,<4.2.0`.
- **INFERRED** A later patch within either range could change a lint verdict. `pip-freeze.txt` records the versions used, so the drift is traceable. Exact transitive pins were outside the r2 brief.

**Must-fix coverage and checks**

- **VERIFIED** No requested behavioral test is missing. The tests cover real changed paths, flake8 PASS/RED/crash, all four input and environment refusals, missing final `__END__` after every stage passes, both suites’ exit-status disagreements, Ubuntu release metadata, pins, and freeze output. The trust comment and unchanged workflow pins were verified by inspection. I read the r2 brief from commit `6d6150f` because it is absent from the review branch.
- **VERIFIED** `bash -n` passed. All 43 tests errored during fixture setup because the read-only sandbox provides no writable temporary directory. Commit `f9282e5` records six failures or errors on the old script and 43 passes on Python 3.12 after r2. I could not independently reproduce that run.

**HOLD (VERIFIED)** A changed Python file can escape lint and still receive a GREEN gate verdict.