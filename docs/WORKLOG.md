# Worklog

One line per finished item: `YYYY-MM-DD | what | branch or PR | PASS, FAIL, or PARKED`.

2026-11-17 | Desk scaffolding drafted from the Kalon operating system | none yet | PASS
2026-11-17 | Cloud baseline of fork master 3f3d0c3: 631 pass, 59 skip, Django 1 error | none | PASS (fast check, not gate)
2026-11-18 | Mini setup: clone, venv-3.12, deps; baseline 4 macOS-only pytest fails + Django test_basic | none | PASS
2026-11-18 | Gate fix: only lock-w0..2 count as live Kalon locks (retained leftover blocked setup) | desk | PASS
2026-11-19 | Supervised pilot console, T-CON-11 and T-CON-1 to T-CON-3. Mac and Linux passed all ten Chromium module checks and 150 Python tests each. Linux passed two additional source recovery runs. Machine review blocked as recorded in STATE.md. | fork deepsignal/console-supervised-pilot 8652862 | PARKED
2026-11-17 | gate.sh dry run in cloud on dev 1a6f1ed: RED on Django test_basic only; locking test 20 OK | none | PASS (dry run, not Mini)
2026-11-18 | DeepSignal VectorWindAverageTransform: 23 tests pass on contrib master and core master 3f3d0c3, flake8 clean, sample config run on NBP1406 data | fork claude/project-thread-un3kq6 558e45b, PR not sent | PASS (fast check, gate NOT RUN)

2026-11-19 | Supervised pilot passed all nine design commands, 190 frontend tests, 158 Python tests on each OS, ten browser modules on both, and the live HTTP and HTTPS workstation demo. The only red gate is inherited Bandit. Owner proposal is on desk main. | fork deepsignal/console-supervised-pilot fc31b54 | PARKED before release review

2026-11-19 | Pilot hardening: 204 Mac and 206 Ubuntu tests passed, including live Supervisor and both nginx configurations on Ubuntu. Installed Bandit remains RED with 188 findings. Separate policy tests passed on Mac (43) and Ubuntu (four scenarios). Security-owner decisions pending on both drafts. | fork PR #1 8f0794e, desk PR #3 d06ad2d, desk issue #2 | PARKED before release approval
2026-11-19 | Pilot cloud verification dispatcher built and exercised through the isolated desk launcher. Owner review and hosted overlap pending. | desk deepsignal/cloud-verification-dispatch candidate at ba5d407 | local PASS, hosted NOT RUN
