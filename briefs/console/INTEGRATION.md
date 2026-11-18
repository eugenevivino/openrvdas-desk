# Console MVP integration plan (lead-run)

Branch: `deepsignal/console-mvp`, created from the `deepsignal/console-core-v2` head once that task is green.
Everything below is git plus test runs. No code is written during integration. If a merge needs a code change, it goes back to that module's branch as a fix task.

## 1. Gate before any merge (per branch)
- The branch's own acceptance tails are green in its task report.
- `git diff --stat origin/deepsignal/console-contract...origin/<branch>` touches only that brief's Scope paths. Any other path is rejected and sent back.
- No `dist/` changes, except on core-v2.

## 2. Merge order
All merges use `git merge --no-ff --no-edit`, one branch at a time. After each merge, run from `contrib/deepsignal/console`:
`npx oxlint && npx tsc -b --noEmit && npx vitest run`.
If a merge goes red, revert it (`git reset --hard HEAD~1` on the integration branch only), open a fix task on the module branch, and continue with the next one.

1. `deepsignal/console-core-v2`. This is the base and holds the registry and the testkit.
2. `deepsignal/console-mod-health`, then `-mod-chart`, then `-mod-bridge`. These are the pages other modules reference.
3. `deepsignal/console-mod-auto-pages`. Its references to wind-dial, chart and number now resolve.
4. `deepsignal/console-mod-stale-banner`, then `-mod-kiosk-night`.
5. `deepsignal/console-install`.
6. `deepsignal/console-mod-map`, only if it is green by 11-21. Otherwise it stays a stretch branch.
7. `deepsignal/console-harness-fixture`, then `-harness-soak`, then `-harness-source-loss`. These are Python only and use disjoint paths.

Expected conflicts: none, because file ownership is disjoint. The only shared touchpoint is `contrib/deepsignal/console/docs/`, where each task adds its own file.

## 3. After all merges (one commit: "Console MVP integration")
1. Register the pytest markers `lead_run` and `slow` in `contrib/deepsignal/test/conftest.py`, if core-v2 did not. This is a two-line config change, which is allowed here.
2. Science preset: add a map tile if map merged. That is a one-line YAML change in the chart module's preset, done as a fix task on the chart branch, not here.
3. `npm run build` once, then commit `dist/`. Check the build is reproducible by building twice and comparing `sha256sum` of `dist/**`.
4. README: add a "Modules" list linking `docs/*.md`. This is a docs-only fix task, given to core-v2 if needed.

## 4. Tests the MacBook runs outside the sandbox (lead_run)
Run from the repo root, in the scratch venv (Playwright 1.64.1, Chromium headless shell), at the integration head:
```
python3 -m pytest contrib/deepsignal/test/ -v -m "lead_run or not lead_run"
```
That covers:
- `test_console_live.py`: value, SUSPECT while LIVE, AGING to STALE, Night red pixel scan, no light first frame.
- `test_bridge_browser.py`: Bridge in Night red with no G or B > 0.15 R, and no vertical scroll at 1366x768.
- `test_source_loss_browser.py`: kill mwx1, the tile shows STALE within 10 s, then LIVE after the restart.
- Harness: `test_fixture.py`, `test_source_loss.py`, `test_soak.py` (smoke).
- Install: `test_install.py`.

Then these manual checks, recorded with screenshots in `/private/tmp/deepsignal/console-mvp/`:
- USABILITY 1: the demo starts from the README.
- USABILITY 4: time a cold install plus self-test (D-SETUP1: 10 minutes or less, 3 actions).
- USABILITY 12: 400 px phone width, 1366x768 laptop, and a 1920x1080 bridge screen.
- Impeccable audit in Day, Dusk, Night red and Night neutral.

## 5. Soak wiring
- 6 h soak on Linux (rule 25 target), using a GitHub Actions workflow in the desk repo. GitHub caps a job at 6 h, so the run uses `--hours 5.5`. Command: `python3 -m contrib.deepsignal.test.harness.soak --hours 5.5 --warmup-min 30 --report soak-linux.json`. Upload the report as an artifact.
- 24 h soak on the Mac Mini, under `~/OpenRVDAS-Work/` and only when Kalon is idle. Command: `--hours 24 --report soak-24h.json`. macOS is treated as an approximation, so a failure there that does not reproduce on Linux does not block.
- Pass: both reports say PASS (under 5% RSS growth after warm-up, median lag of 5 s or less, no dead processes).

## 6. Review and sign-off
- Astra 6.2 high, read-only, fresh session, reviews `origin/deepsignal/console-contract...deepsignal/console-mvp` against the briefs, DESIGN.md, CONTRACT.md and the CODEX.md rule 13 banned list. Output: findings by severity with file:line, each marked verified or inferred.
- Fix tasks go to the owning module branches. Re-merge them, then re-run sections 2 to 4.
- PR text is drafted in the desk under `pr/deepsignal-console-mvp.md`. Eugene sends it (openrvdas_contrib, `master`).
