# Brief: ci-install-clock

- Decision: D-SETUP1 (proposed in `docs/TARGET-PARITY.md`, section 5). Measurement only, no product change
- Risk tier: low (CI workflow on the fork; installs into a throwaway GitHub runner)
- Module: exactly one, a timed install workflow. Branch `ci/install-clock` cut from fork `dev`
- Mac scratch path: not used (cloud lane)
- Base: fork `dev` at the sha current when the job starts (record it)
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: fork only. Nothing upstream (D-ARCH6)

## Goal
Measure, on a clean Linux box, how long and how many human answers it takes
OpenRVDAS to go from nothing to live simulated data, so "easier to set up" is a
number we can beat.

## What to build
A GitHub Actions workflow `.github/workflows/install-clock.yml` on the fork
branch `ci/install-clock`, triggered by `workflow_dispatch` and on push to that
branch only. Matrix: `ubuntu-24.04`, `ubuntu-22.04`. Each job:

1. Records `T_start` (epoch seconds) and the runner image version.
2. Runs `bash utils/install_openrvdas.sh` from the checkout with every prompt
   answered by its default except: install simulate script = yes, run
   simulate on boot = yes, use existing clone = yes. Feed answers on stdin from
   a checked-in answers file (`ci/install-clock/answers.txt`), one line per
   prompt, so the prompt count is the line count. If the script needs a
   different answer order on a runner, the job fails loudly; do not guess.
3. Counts prompts actually shown (grep the captured stdout for the prompt
   strings listed in `utils/install_openrvdas.sh` lines with `read -p` and
   `yes_no`) and writes `prompts_shown`.
4. Records `T_installed` when the script exits 0.
5. Loads `test/NBP1406/NBP1406_cruise.yaml`, sets mode `no_write` using the
   command-line server API (no browser), and waits until the CachedDataServer
   on port 8766 returns at least one field with a timestamp newer than
   `T_installed` (poll every 2 s, give up at 300 s). Records `T_first_data`.
6. Checks the web console answers HTTP 200 on port 80.
7. Writes `install-clock.json` with: runner image, base sha, `prompts_shown`,
   `install_seconds = T_installed - T_start`,
   `first_data_seconds = T_first_data - T_start`, peak RAM and disk used
   (from `/proc/meminfo` and `df` before and after), and the exit status of each
   step. Uploads it as an artifact and prints it in the job summary.

## Failing test first
`ci/install-clock/test_parse_clock.py`: a unit test for the small parser that
turns the captured install log into `prompts_shown`. Feed it a saved log
excerpt with 3 prompts; expect 3. RED before the parser exists.

## Acceptance (exact commands)
```
python3 -m pytest ci/install-clock/test_parse_clock.py
```
```
flake8 ci/install-clock/
```
Plus one green workflow run on each matrix leg; paste both `install-clock.json`
files into the result.

## Scope
New files only: `.github/workflows/install-clock.yml`, `ci/install-clock/*`.
Read-only: everything else, including `utils/install_openrvdas.sh` (read
OPERATIONS.md first; do not "fix" the installer in this job).

## Trust boundaries and data integrity
The runner is disposable. No secrets. No network calls except package
installs the installer itself makes. Do not change installer defaults.

## Non-goals and banned
No installer changes, no upstream PRs or issues, no macOS leg (later). No
retries that hide a failure: a failed install is a valid measurement; record it.
Sleep only inside the bounded poll in step 5.

## Report format
Under 40 lines: both JSON results, prompts that needed a non-default answer,
anything in INSTALL.md that disagrees with what the script did (known
candidate: INSTALL.md shows "Do you want to install this script? (yes)" for
the simulate script, but the script default is `no`), verified versus inferred.

## Stop rule
Install fails on both legs for a reason outside this brief's scope: stop and
report the log tail. Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- install_seconds / first_data_seconds / prompts_shown per leg:
- Open questions:
