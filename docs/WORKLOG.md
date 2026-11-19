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

2026-11-19 | Pinned cloud console checks and type checking passed during a real Mac slot hold. First fixture lacked a sandboxed PID probe, preserved in pilot-cloud-overlap/attempt-1; the host observed liveness on the successful run. | desk PR #4 95e9edf, Actions 44565419757 | PASS for overlap, critical install pending

2026-11-19 | Stream Health retained historical stage and root reports and verified two recovery variations. Mac and Linux passed 186 frontend tests and Chromium. T-CON-9 hit 26.85 ms in the initial Linux run. The final single-worker run retained the 16 ms limit. T-CON-12 records the startup subscription gap. All design commands passed. Installed Bandit holds release review. | fork PR #2 9f156fa, desk Actions 44571508115 | PARKED before release approval
