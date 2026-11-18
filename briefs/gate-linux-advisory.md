# Brief: gate-linux-advisory (replaces r5 per D-GATE1)

- Risk tier: medium (workflow file only, no verdict logic). Cloud lane, Sol medium, attempts 1. Branch `gate/linux-advisory` in the DESK repo (eugenevivino/openrvdas-desk), base desk main.
- Goal: a GitHub Actions workflow `.github/workflows/linux-advisory.yml` that checks out a given fork ref (workflow_dispatch input `ref`, default `dev`, repo eugenevivino/openrvdas, recursive submodules OFF), sets up Python 3.12 on ubuntu-22.04, installs the pinned deps (flake8 7.5.0, pytest-timeout 2.4.0, pyyaml, pytest, plus the repo's own requirements as the existing installer does), then runs and uploads RAW results as artifacts and a job summary:
  1. `python -m pytest test/ -p no:cacheprovider --timeout=120 -q --junitxml=pytest.xml || true`, with the exit code, collected, passed, failed, skipped, deselected counts printed.
  2. `flake8` on the .py files changed versus the fork's `dev` (or all of contrib/deepsignal when ref is dev), raw output, exit code printed.
  3. A final line "ADVISORY: raw results above, no GREEN or RED verdict". Never write the words GREEN or RED. Never fail the job because tests fail (the human reads the output); fail only if the workflow itself cannot run.
- NO decision logic, no shell evidence parsing beyond printing counts. Reuse the pinned action SHAs from `gate/linux-actions` `.github/workflows/linux-gate.yml` (copy them exactly; do not use floating tags). Timeout 45 minutes, 120 s per-test timeout.
- Submodules: do not init (web_backend and web_frontend are gitlinks on dev); that was the r5 P1.
- Acceptance: `python3 -c "import yaml;yaml.safe_load(open('.github/workflows/linux-advisory.yml'))"` parses; actionlint if available; no secrets; no network beyond pip and the checkout.
- Merge: to desk main only after Eugene approves (workflow on the default branch is needed for dispatch); queued in MORNING.
