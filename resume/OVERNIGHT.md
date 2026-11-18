# DeepSignal overnight log (MacBook lane, started 2026-11-18 07:30Z)

Rules: D-NIGHT1. Console first, then phase 2; reviews one at a time; Mac jobs behind the ds-codex RAM gate and lock;
push only deepsignal/* fork branches and desk branches; two failures of the same task means stop and report.

## Done (pushed)
- gate-linux r1 16669b1, r2 f9282e5 (desk gate/linux-actions); r2 review HOLD (3 P1, 1 P2) -> r3 brief.
- qartod-flags 2724f07a, correction-ledger 99c01919, fault-bench 9d87d99a (fork deepsignal/*).
- #78 ship-coupling 67440a40 (cloud, 7 tests OK, flake8 clean, atlas rc 0).
- #52 instrument-history 973a87a3 (cloud, 7 tests OK, flake8 clean, check rc 0).
- ci/install-clock f3b7437 (cloud; pytest 1 passed, flake8 clean); Actions run 44258836868 started 07:26Z.
- ds-codex: desk tools/ds-codex 2c228e2 (RAM gate with lead formula, pressure level 1 required, env floors,
  --wait-ram, --sub-agents pin, multi-agent off). Installed copy on the MacBook is older (b8f4c53 logic); the new one is
  installed atomically once no DeepSignal job is running.

## Running
- MacBook: gate-linux-r3 (ds-codex pid 89102, gpt-6.2-sol high), started 07:25:57Z.
- Cloud (env deepsignal), resubmitted 07:29Z after Eugene's Node 22 fix: auto-pages, bridge (3), charts, health, install,
  kiosk-night, map, stale-banner, p2 cast-view, console core-v2 (3). Ids: console-cloud/submitted.tsv (*-r2 rows).
- Cloud: fixture (python), p2 erddap, flow-state, rest-api, best-source (2), met-reports, release-policy (2),
  onboard-wizard, vocab, shore-snapshot. Ids: console-cloud/submitted.tsv and p2-cloud/submitted.tsv.

## MacBook queue (one Codex job at a time)
1. gate-linux-r3 (running) -> tests, commit, push. 2. r3 review (Astra ultra, read-only).
3. #78 ship-coupling review (Astra ultra, read-only; MacBook because the Mini has no DeepSignal login).
4. qartod-flags review (Astra high). 5. #112 met-formulas build (Astra high). 6. #53 review. 7. #108 route-eta build.
8. #56 review. Console acceptance checks run between jobs as cloud tasks finish (gate only, no lock).

## Open items / blocked
- Mini: ~/.codex-deepsignal does not exist there (only Kalon's ~/.codex); not logged in. mini-finish.sh not run.
- install-clock Actions result pending (review note: actions/checkout@v6 unpinned).
- #79, #54: held for Mac Astra builds when the lead says.
