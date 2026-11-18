# Worklog

One line per finished item: `YYYY-MM-DD | what | branch or PR | PASS, FAIL, or PARKED`.

2026-11-17 | Desk scaffolding drafted from the Kalon operating system | none yet | PASS
2026-11-17 | Cloud baseline of fork master 3f3d0c3: 631 pass, 59 skip, Django 1 error | none | PASS (fast check, not gate)
2026-11-18 | Mini setup: clone, venv-3.12, deps; baseline 4 macOS-only pytest fails + Django test_basic | none | PASS
2026-11-18 | Gate fix: only lock-w0..2 count as live Kalon locks (retained leftover blocked setup) | desk | PASS
2026-11-17 | gate.sh dry run in cloud on dev 1a6f1ed: RED on Django test_basic only; locking test 20 OK | none | PASS (dry run, not Mini)
2026-11-18 | DeepSignal VectorWindAverageTransform: 23 tests pass on contrib master and core master 3f3d0c3, flake8 clean, sample config run on NBP1406 data | fork claude/project-thread-un3kq6 558e45b, PR not sent | PASS (fast check, gate NOT RUN)
