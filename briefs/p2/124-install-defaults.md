# Brief: p2-install-defaults (Installer `--defaults` (zero-prompt install, core fix))

- Decision: D-PARITY1, IDEAS #124 (Eugene approved building #104-#124, 2026-11-18)
- Risk tier: high
- Module: exactly one. Branch `deepsignal/p2-install-defaults` from `1a6f1ed`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: core, fork only (D-ARCH6)
- Value (techs/science/shore): 4/2/3
- Depends on: validated on real runners by `ci/install-clock` (briefs/install-clock.md); rerun that workflow on this branch
- Needs Eugene: The installer is the riskiest file in the repo (OPERATIONS.md section 5: needs real machines). Eugene approved #124 with the batch; the change stays on the fork until install-clock is green on both Ubuntu legs and a Mac run is done by hand.

## Goal
`bash utils/install_openrvdas.sh --defaults` installs OpenRVDAS with no questions except the sudo
password, so first light (D-SETUP1) needs three actions, not twenty-five.

## Background facts (do not re-derive; read OPERATIONS.md section 5 first)
- About 2,500 lines, `#!/bin/bash -e`, must run on macOS bash 3.2: no heredoc with `;;` inside `$(...)`,
  no `read -r -d ''` (both abort the install).
- Prompts are `yes_no "<question>" $DEFAULT` (function near line 89) and about 30 `read -p` lines between
  lines 2100 and 2450, each with a `DEFAULT_*` variable. A preferences file
  `.install_openrvdas_preferences` is sourced to override defaults.
- Runs as a sudo-capable normal user, never as root (macOS exits if EUID is 0).

## Design (lead decisions; flag disagreement in the report)
- Parse `--defaults` (and `--help`) at the top, before anything else runs. Unknown flags print usage and
  exit 2. No other behavior change without the flag.
- Add one helper `prompt_value VAR "<question>" "$DEFAULT"` between marker comments
  `# BEGIN prompt helpers` and `# END prompt helpers`, together with `yes_no`. With `ACCEPT_DEFAULTS=yes`,
  both print the question with "(default accepted: X)" and set the result without calling `read`.
  Without it, they behave byte-for-byte as today.
- Replace each `read -p "...($DEFAULT_X) " X` followed by `X=${X:-$DEFAULT_X}` with `prompt_value`, keeping
  question text identical. Do not touch the SSL, firewall or password branches' logic; with
  `--defaults`, SSL stays off, firewall stays off, and the database password default is used, and the end
  of the install prints a bold line "Installed with defaults: change the web password now with ...".
- `--defaults` also turns on the simulator install so first light shows data (the D-SETUP1 goal);
  say so in the usage text.

## Failing test first
`test/utils/test_install_defaults.py` (pytest, Linux): extracts the text between the two marker comments,
runs it under `bash` with `ACCEPT_DEFAULTS=yes` and stdin closed, and asserts every helper returns its
default without reading; without the flag, feeding "n\n" to `yes_no` gives `no`. A second test greps the
script: no `read -p` remains outside the helpers; every question string from the base is still present
(list them from the base file in the test, so a reworded question fails).

## Acceptance (exact commands, from repo root, Linux)
```
python3.12 -m pytest test/utils/test_install_defaults.py -v
```
```
bash -n utils/install_openrvdas.sh
```
```
shellcheck -S error utils/install_openrvdas.sh || echo "shellcheck not installed: say so"
```
Real-machine proof is outside this sandbox: the lead reruns `ci/install-clock` against this branch with
`--defaults` and records install seconds, first-data seconds and prompts shown (target 0 besides sudo).

## Scope
`utils/install_openrvdas.sh`, `test/utils/test_install_defaults.py` (create `test/utils/` with an empty
`__init__.py` if needed), and a short `--defaults` section in `INSTALL.md`. Nothing else.

## Trust boundaries and data integrity
Existing behavior and output bytes of every current config stay identical unless the new option is set.
Default values of existing classes do not change.

## Non-goals and banned
No upstream PR or issue (D-ARCH6, fork only). No refactors, renames or formatting outside the listed
files. No new dependency. No loosened, skipped or deleted tests, no swallowed errors, no sleeps for test
ordering.

## Stop rule
No code change needed: stop and report. Two fix rounds still red: stop and report.
Review: high risk tier. A separate fresh reviewer reads the whole diff against OPERATIONS.md section 5.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Acceptance tails:
- Open questions:
