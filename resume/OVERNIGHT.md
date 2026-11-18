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

## Pushed since 07:30Z (cloud builds, lead acceptance passed)
- p2: flow-state 2df7bd5, rest-api 8756fed, erddap a4f8e4c, best-source 090e208 (a1 of 2), shore-snapshot 159240c,
  vocab 9749bdb, release-policy 6b19de4 (a1 of 2). Console: auto-pages 62b0ded (a1 of 2).
- desk gate/linux-actions: r3 da72a75 (48 tests OK; RED 10 failures verified), ledger 85f1f37.
- onboard-wizard: failed acceptance (1 test, E501); fix round 1 resubmitted task_e_6afd55dd6ddc832f8b1d0e7dad41f5ce.
- core-v2 came back EMPTY again; diag task task_e_6afd55550514832f98087af3583aa4de on deepsignal/console-core.
- Automation: autopilot.sh polls every 3 min and runs accept.sh (RAM gated, one at a time); results in
  accept-results.log; the lead pushes with push-accepted.sh (only paths in the diff).

## Running
- MacBook: gate-linux-r3 (ds-codex pid 89102, gpt-6.2-sol high), started 07:25:57Z.
- Cloud (env deepsignal), resubmitted 07:29Z after Eugene's Node 22 fix: auto-pages, bridge (3), charts, health, install,
  kiosk-night, map, stale-banner, p2 cast-view, console core-v2 (3). Ids: console-cloud/submitted.tsv (*-r2 rows).
- Cloud batch 4/5: stream-discovery, config-from-inventory, config-lint, component-catalog; visual-gate (2).
- Cloud: fixture (python), p2 erddap, flow-state, rest-api, best-source (2), met-reports, release-policy (2),
  onboard-wizard, vocab, shore-snapshot. Ids: console-cloud/submitted.tsv and p2-cloud/submitted.tsv.

## MacBook queue (one Codex job at a time)
1. gate-linux-r3 (running) -> tests, commit, push. 2. r3 review (Astra ultra, read-only).
3. #78 ship-coupling review (Astra ultra, read-only; MacBook because the Mini has no DeepSignal login).
(qartod-flags review: run by another thread, pid 24840.) 4. #112 met-formulas build (Astra high). 5. #53 review.
6. #108 route-eta build. 7. #113 geometry (Astra high). 8. #121 device-pack (Sol high, needs network). 9. #56 review. Console acceptance checks run between jobs as cloud tasks finish (gate only, no lock).

## Open items / blocked
- Mini: ~/.codex-deepsignal does not exist there (only Kalon's ~/.codex); not logged in. mini-finish.sh not run.
- install-clock Actions result pending (review note: actions/checkout@v6 unpinned).
- #79, #54: held for Mac Astra builds when the lead says.
- #130 instrument-init: task_e_6afd56a1d0a0832fa7f14f0a38c28e1c (deepsignal/p2-instrument-init, high risk, nothing merged)
- docs-journeys: task_e_6afd576de9a0832fb3dbe561bf42b30b (deepsignal/docs-journeys from 1a6f1ed; output goes to desk docs/ after acceptance, lead-handled, not autopilot)
- D-UPSTREAM0 guard (07:52Z): shared pre-push hook /private/tmp/deepsignal/hooks/pre-push (refuses any push whose remote
  name or URL mentions OceanDataTools) set as core.hooksPath in 58 MacBook clones incl. ~/openrvdas, and in the Mini's
  ~/OpenRVDAS-Work/openrvdas; ~/openrvdas remote upstream pushurl set to DISABLED; ds-codex (desk tools 7dc1d7b) exports
  the hook for every git run in a job; accept.sh sets it on new clones. Tested on local bare repos: OceanDataTools pushes
  refused, fork push allowed. Script audit: only read-only upstream fetch by URL in hourly-sync.sh.
- From 07:52Z every cloud prompt I submit is prefixed with desk briefs/cloud/_HEADER.md.
- batch 7 sealog-bridge: task_e_6afd599ec718832fb89bf656786e421c
- batch 7 openvdm-bridge: task_e_6afd59a24b08832fbaee1b0224d6a4f9
- batch 7 archive-compress: task_e_6afd59a492b0832fa3790bf25c1edb51
- batch 7 grafana-quality: task_e_6afd59a72c98832fa64b69ac16f19f83
- batch 7 cruise-context: task_e_6afd59acd1b8832fb3ae8fee1ec93365
- #137 eez-mode: task_e_6afd6053c4bc832f818e13cd12d9b5bc (CRITICAL under D-REVIEW1; push branch, never merge)
- ship batch iec450-bridge: task_e_6afd620303f0832f88db3974cb4d0298
- ship batch sv-consistency: task_e_6afd62068fcc832f91a87368fb15c7b3
- ship batch depth-consensus: task_e_6afd6209b424832fab4d0f6a9ca9e9e1
- ship batch link-health: task_e_6afd620c657c832faf6cce3276ac7579
- #139 kongsberg-tap HELD with #121: downloads need Eugene's own yes (my rule); MORNING line added. Ship batch submitted 08:30Z (iec450-bridge, sv-consistency, depth-consensus, link-health).
- #157 device-servers: task_e_6afd628285f8832fb9cbc0904351bac8
- #158 seismic-shot-qc: task_e_6afd632eba60832f8e3e06e1d7a31509
- #145 adcp-health: task_e_6afd649fb2e4832f840ac759cba32b5a; #147 sv-manager queued on the Mac after chain-3 (Astra high)
- batch 9 console-chain: task_e_6afd674990b4832f8724d88faa43a9e8
- batch 9 stream-health: task_e_6afd674ce358832fb8c13f6002cdc19a
- batch 9 cal-units-registry: task_e_6afd675013e4832fbdd870990a02f5d0
- batch 9 time-health: task_e_6afd675336d0832fb20c6cee76129ea6
- batch 9 config-provenance: task_e_6afd67566524832fa4f4e0448e4bea19
- batch 9 event-timeline: task_e_6afd6759eb2c832fa26a3443ba92b504
- batch 9 runbooks: task_e_6afd675d0580832f860c2646e318bd13
- batch 9 archive-readiness: task_e_6afd675fbe04832fa95f53c419526731
- batch 9 console-trust: task_e_6afd6762b448832f8102f7d2564d3652
- scoreboard profiles: task_e_6afd678117c0832fb1fb0677c6ece69f
- scoreboard transports: task_e_6afd6784cc84832fa3d5b2879813cef7
- scoreboard text-codec: task_e_6afd67877f30832f9beec7117fd5af01
- scoreboard alpha-codec: task_e_6afd678a5c5c832f8763e1513bdcb8c3
- scoreboard modbus-codec: task_e_6afd678db2cc832fb3d24651fd5c7ee5
- #188 ai-triage: task_e_6afd68182320832fa73fbfbe4a0b7349 (CRITICAL: push only, never merge)
- #188 resubmitted task_e_6afd6831ea1c832f8a772812155e141d; first submit task_e_6afd68182320 had only the header (prompt file not pulled yet) and is ignored
- #188 ai-triage HELD: task_e_6afd6831ea1c runs but is not accepted or pushed until the revised brief lands; then a fix round (Sol medium, 1 attempt) on its best attempt
- #188 revised API-first prompt: task_e_6afd6860fe48832f9003e33bf01b4f97; older task_e_6afd6831ea1c (old prompt) marked ignored
- #188 final prompt: task_e_6afd6905e1e0832f88b60411e8f2adf5; task_e_6afd6860fe48 ignored; at most one more resubmit
- docs-journeys: desk docs c217afa; fix round for J-TECH-SETUP-AI-1/MCP-1: task_e_6afd692ea358832f9f86c0448338674f (lead copies to desk)
- #197 cds-lockdown: task_e_6afd6aacc6c8832fa998754243fe2f80 (CRITICAL security; push only). #189 auth-gateway waits for #197 green and D-SEC2. Console install integration to point at #197 (note for INTEGRATION).
- #188 vault fix round: task_e_6afd6aecf954832f88d66b060c32e454
- 10:15Z CONSOLE MVP: deepsignal/console-mvp faba8fe = core-v2 2ebdf91 + health, chart, auto-pages, stale-banner,
  kiosk-night, install (fix c32b6c9: tests no longer assume root), map, bridge (fix 585ca4c). vitest 116 passed,
  oxlint/tsc clean, dist reproducible (22 files), pytest not-lead_run 7 passed, flake8 clean, lead_run browser tests
  2 passed (test_console_live, test_bridge_browser). Pending: harness fixture/soak/source-loss, visual-gate, manual
  checks (USABILITY 1, 4, 12, Impeccable audit), 24 h soak on the Mini, Astra review of the merged diff.
- Reviews: gate r4 HOLD (3 rounds red; r5 rewrite queued, Astra high + ultra review); MCP design review FIX FIRST
  (desk research/2026-11-18-mcp-design-review.md); QARTOD BLOCK -> fix1 queued; #78 HOLD -> fix1 queued; #53 HOLD -> cloud fix1.
- 10:30Z USABILITY 12 on console-mvp faba8fe (vite preview of dist): no horizontal scroll at 400 px, 1366x768, 1920x1080 in Day and Night; only phone Night scrolls vertically (dimmer row). Screenshots /private/tmp/deepsignal/console-mvp-checks/. Pending: cold install timing (needs root on a clean Linux box; GitHub runner via install-clock), D-SEC0 CDS checks (after #197 acceptance), Impeccable audit (polish pass), 24 h soak (needs harness fixture + source-loss).
- install-clock run 44258836868 hung 3 h at the installer's first prompt; cancelled 10:29Z; fix round task_e_6afd7e3d710c832fa298581752677f9c
- #188 opt-in/proxy/redaction fix round: task_e_6afd837388d4832f9fc1616ab7382025
Last sync 2026-11-18T13:45:03Z: fork branches pushed ok; upstream fetched ok (core dev 1a6f1edb, contrib master 3b4b76e6); desk main pushed after this line.
