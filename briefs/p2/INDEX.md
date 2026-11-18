# Phase 2 parity tasks (IDEAS #104-#124)

Written 2026-11-18 by the parity thread, ranked by value from docs/TARGET-PARITY.md section 4. #107 (map) is console module `map` in `briefs/console/`. The install clock part of #124 is `briefs/install-clock.md` (already submitted).

| Rank | IDEAS | Task | Branch | Base | Lane | Kind | Batch | Depends on | Needs Eugene |
|---|---|---|---|---|---|---|---|---|---|
| 1 | #104 | [ERDDAP dataset generator](104-erddap.md), prompt `briefs/cloud/p2-erddap.md` | `deepsignal/p2-erddap` | `3b4b76e` contrib tree | cloud | py | 1 | none (reads #117 vocab files if present, optional) | no |
| 2 | #110 | [Flowthrough state tagging](110-flow-state.md), prompt `briefs/cloud/p2-flow-state.md` | `deepsignal/p2-flow-state` | `3b4b76e` contrib tree | cloud | py | 1 | none (QC #8 and #55 consume its field later) | no |
| 3 | #105 | [Read-only REST data API](105-rest-api.md), prompt `briefs/cloud/p2-rest-api.md` | `deepsignal/p2-rest-api` | `3b4b76e` contrib tree | cloud | py | 1 | none (shares query-budget idea with #67; reads the CachedDataServer) | yes |
| 4 | #106 | [Best-source selector with failover (core fix)](106-best-source.md), prompt `briefs/cloud/p2-best-source.md` | `deepsignal/p2-best-source` | `1a6f1ed` fork dev | cloud | core | 1 | none; uses `<field>_QC` flags when #8 is present, works without them | no |
| 5 | #109 | [Winch and CTD cast view](109-cast-view.md), prompt `briefs/cloud/p2-cast-view.md` | `deepsignal/p2-cast-view` | `deepsignal/console-contract` | cloud | node | 1 | console contract branch `deepsignal/console-contract` | yes |
| 6 | #111 | [SAMOS daily file and met report writers](111-met-reports.md), prompt `briefs/cloud/p2-met-reports.md` | `deepsignal/p2-met-reports` | `3b4b76e` contrib tree | cloud | py | 1 | none; feeds from 1-minute averages (vector wind #4 for wind) | yes |
| 7 | #116 | [Data release policy (privacy, EEZ hold-back)](116-release-policy.md), prompt `briefs/cloud/p2-release-policy.md` | `deepsignal/p2-release-policy` | `3b4b76e` contrib tree | cloud | py | 2 | core `GeofenceTransform` (exists) or any boolean field for "inside EEZ"; #115 roles later decides who sees what | yes |
| 8 | #108 | [Routes and waypoints (ETA, bearing, off-course)](108-route-eta.md), prompt `briefs/mac/p2-route-eta.md` | `deepsignal/p2-route-eta` | `deepsignal/console-contract` | mac | node | 2 | console contract; drawing routes on the map is a later change to #107 `map`, not this task | no |
| 9 | #112 | [Met and seawater formula library (core fix)](112-met-formulas.md), prompt `briefs/mac/p2-met-formulas.md` | `deepsignal/p2-met-formulas` | `1a6f1ed` fork dev | mac | core | 2 | none | no |
| 10 | #114 | [Sensor onboarding wizard (engine and CLI)](114-onboard-wizard.md), prompt `briefs/cloud/p2-onboard-wizard.md` | `deepsignal/p2-onboard-wizard` | `3b4b76e` contrib tree | cloud | py | 2 | none; the console wizard page is a later console module that calls this engine; extends #29 | no |
| 11 | #117 | [Standard vocabularies (CF, SeaVoX, R2R, ICES, UN/LOCODE)](117-vocab.md), prompt `briefs/cloud/p2-vocab.md` | `deepsignal/p2-vocab` | `3b4b76e` contrib tree | cloud | py | 2 | none; #104 erddap, #52 registry and #120 cruise metadata read its files later | no |
| 12 | #123 | [Low-bandwidth shore snapshot](123-shore-snapshot.md), prompt `briefs/cloud/p2-shore-snapshot.md` | `deepsignal/p2-shore-snapshot` | `3b4b76e` contrib tree | cloud | py | 2 | none; #116 release policy goes in front of it for public use | no |
| 13 | #115 | [Roles and access policy (engine only)](115-roles.md), prompt `briefs/cloud/p2-roles.md` | `deepsignal/p2-roles` | `3b4b76e` contrib tree | cloud | py | 3 | none to build; #105 REST, #116 release policy and console pages adopt it later | yes |
| 14 | #118 | [Instrument document store](118-doc-store.md), prompt `briefs/cloud/p2-doc-store.md` | `deepsignal/p2-doc-store` | `3b4b76e` contrib tree | cloud | py | 3 | #52 instrument history for instrument ids and cal ids: reads its YAML file by path, does not import its code, so it builds in parallel | no |
| 15 | #119 | [Host health reader](119-host-health.md), prompt `briefs/cloud/p2-host-health.md` | `deepsignal/p2-host-health` | `3b4b76e` contrib tree | cloud | py | 3 | display is the console `health` module: the build lead routes a small follow-up there; this task only publishes fields | no |
| 16 | #120 | [Cruise metadata](120-cruise-meta.md), prompt `briefs/cloud/p2-cruise-meta.md` | `deepsignal/p2-cruise-meta` | `3b4b76e` contrib tree | cloud | py | 3 | none; uses #117 vocab files for port codes if present (optional) | yes |
| 17 | #124 | [Installer `--defaults` (zero-prompt install, core fix)](124-install-defaults.md), prompt `briefs/cloud/p2-install-defaults.md` | `deepsignal/p2-install-defaults` | `1a6f1ed` fork dev | cloud | core | 3 | validated on real runners by `ci/install-clock` (briefs/install-clock.md); rerun that workflow on this branch | yes |
| 18 | #113 | [Vessel geometry and lever-arm correction](113-geometry.md), prompt `briefs/mac/p2-geometry.md` | `deepsignal/p2-geometry` | `3b4b76e` contrib tree | mac | py | 4 | none; #52 instrument history may later reference sensor position ids | no |
| 19 | #121 | [UNOLS met device definitions (core contrib/devices)](121-device-pack.md), prompt `briefs/mac/p2-device-pack.md` | `deepsignal/p2-device-pack` | `1a6f1ed` fork dev | mac | core | 4 | none; needs manufacturer manuals, so it runs where the network allows reading them (Mac) | yes |
| 20 | #125 | [Stream auto-discovery (serial, UDP, MQTT, Redis, CDS, files)](125-stream-discovery.md), prompt `briefs/cloud/p2-stream-discovery.md` | `deepsignal/p2-stream-discovery` | `3b4b76e` contrib tree | cloud | py | 5 | none; its captures feed #114 onboarding wizard | no |
| 21 | #128 | [Component catalog: every reader, writer and transform as a form](128-component-catalog.md), prompt `briefs/cloud/p2-component-catalog.md` | `deepsignal/p2-component-catalog` | `3b4b76e` contrib tree | cloud | py | 5 | none; #114 wizard, #126 generator, console forms and the MCP gateway (#64) all read its output | no |
| 22 | #126 | [Cruise config generator from the instrument inventory](126-config-from-inventory.md), prompt `briefs/cloud/p2-config-from-inventory.md` | `deepsignal/p2-config-from-inventory` | `3b4b76e` contrib tree | cloud | py | 5 | reads #52 instrument history YAML by path and device types from contrib/devices; no code imports | no |
| 23 | #127 | [Cruise config linter](127-config-lint.md), prompt `briefs/cloud/p2-config-lint.md` | `deepsignal/p2-config-lint` | `3b4b76e` contrib tree | cloud | py | 5 | none; complements core `validate_config` (schema) with ship-sense checks | no |
| 24 | #130 | [Instrument init profiles (sensor setup over the wire)](130-instrument-init.md), prompt `briefs/cloud/p2-instrument-init.md` | `deepsignal/p2-instrument-init` | `3b4b76e` contrib tree | cloud | py | 6 | none; #121 and #114 produce profiles | no (hardware check with a tech present, after merge) |
| 25 | #133 | [Sealog bridge: quality events and quality aux data](133-sealog-bridge.md), prompt `briefs/cloud/p2-sealog-bridge.md` | `deepsignal/p2-sealog-bridge` | `3b4b76e` contrib tree | cloud | py | 7 | QARTOD flags | no (live-system check by the lead, see docs/ECOSYSTEM.md) |
| 26 | #131 | [OpenVDM bridge: quality products and Data Dashboard plugin](131-openvdm-bridge.md), prompt `briefs/cloud/p2-openvdm-bridge.md` | `deepsignal/p2-openvdm-bridge` | `3b4b76e` contrib tree | cloud | py | 7 | QARTOD flags | no (live-system check by the lead, see docs/ECOSYSTEM.md) |
| 27 | #135 | [Lossless archive compression and shore bundles](135-archive-compress.md), prompt `briefs/cloud/p2-archive-compress.md` | `deepsignal/p2-archive-compress` | `3b4b76e` contrib tree | cloud | py | 7 | none | no (live-system check by the lead, see docs/ECOSYSTEM.md) |
| 28 | #134 | [Grafana quality pack](134-grafana-quality.md), prompt `briefs/cloud/p2-grafana-quality.md` | `deepsignal/p2-grafana-quality` | `3b4b76e` contrib tree | cloud | py | 7 | QARTOD flags | no (live-system check by the lead, see docs/ECOSYSTEM.md) |
| 29 | #132 | [Cruise context from OpenVDM and Sealog](132-cruise-context.md), prompt `briefs/cloud/p2-cruise-context.md` | `deepsignal/p2-cruise-context` | `3b4b76e` contrib tree | cloud | py | 7 | #120 format | no (live-system check by the lead, see docs/ECOSYSTEM.md) |
| 30 | #137 | [EEZ mode: automatic boundary detection, per-instrument policy, audit](137-eez-mode.md), prompt `briefs/cloud/p2-eez-mode.md` | `deepsignal/p2-eez-mode` | `3b4b76e` contrib tree | cloud | py | 8 | none; feeds #116, #133, console banner | no (recorded-track check by the lead; Marine Regions license check before any EEZ data is committed) |
| 31 | #139 | [Kongsberg multibeam datagram tap](139-kongsberg-tap.md), prompt `briefs/mac/p2-kongsberg-tap.md` | `deepsignal/p2-kongsberg-tap` | `3b4b76e` contrib tree | mac | py | 5 | none; #140, #141, #142, #143 read its field contract | no (read-only fetch of two public format documents approved under the standing rule, 2026-11-18) |
| 32 | #140 | [Sound velocity consistency monitor](140-sv-consistency.md), prompt `briefs/cloud/p2-sv-consistency.md` | `deepsignal/p2-sv-consistency` | `3b4b76e` contrib tree | cloud | py | 5 | none to build; reads #139 field names in use | no |
| 33 | #138 | [IEC 61162-450 bridge reader](138-iec450-bridge.md), prompt `briefs/cloud/p2-iec450-bridge.md` | `deepsignal/p2-iec450-bridge` | `3b4b76e` contrib tree | cloud | py | 5 | none | no |
| 34 | #141 | [Depth consensus](141-depth-consensus.md), prompt `briefs/cloud/p2-depth-consensus.md` | `deepsignal/p2-depth-consensus` | `3b4b76e` contrib tree | cloud | py | 5 | none to build; reads #139 field names in use | no |
| 35 | #156 | [Link health with NOC integration](156-link-health.md), prompt `briefs/cloud/p2-link-health.md` | `deepsignal/p2-link-health` | `3b4b76e` contrib tree | cloud | py | 5 | none; console `health` follow-up shows its fields | no |
| 36 | #157 | [Serial device servers, vendor-neutral (Moxa, Pepperl+Fuchs first)](157-device-servers.md), prompt `briefs/cloud/p2-device-servers.md` | `deepsignal/p2-device-servers` | `3b4b76e` contrib tree | cloud | py | 5 | none; #156 link health folds its fields into link verdicts | no |
| 37 | #158 | [Seismic shot and source QC, listen-only](158-seismic-shot-qc.md), prompt `briefs/cloud/p2-seismic-shot-qc.md` | `deepsignal/p2-seismic-shot-qc` | `3b4b76e` contrib tree | cloud | py | 5 | none; uses core ParseTransform for the ship's shot log | no |
| 38 | #145 | [ADCP health and cross-checks, listen-only](145-adcp-health.md), prompt `briefs/cloud/p2-adcp-health.md` | `deepsignal/p2-adcp-health` | `3b4b76e` contrib tree | cloud | py | 5 | none to build; reads #139 field names in use | no |
| 39 | #147 | [Sound-speed profile manager](147-sv-manager.md), prompt `briefs/mac/p2-sv-manager.md` | `deepsignal/p2-sv-manager` | `3b4b76e` contrib tree | mac | py | 5 | none to build; optional #112 (XBT) and #140 fields | no |
| 40 | #162 | [Console chain view v0 (MVP stretch)](162-console-chain.md), prompt `briefs/cloud/p2-console-chain.md` | `deepsignal/p2-console-chain` | `deepsignal/console-contract` | cloud | node | 9 | see brief | no |
| 41 | #162 | [Stream health engine](162-stream-health.md), prompt `briefs/cloud/p2-stream-health.md` | `deepsignal/p2-stream-health` | `3b4b76e` contrib tree | cloud | py | 9 | see brief | no |
| 42 | #164 | [Calibration and units registry](164-cal-units-registry.md), prompt `briefs/cloud/p2-cal-units-registry.md` | `deepsignal/p2-cal-units-registry` | `3b4b76e` contrib tree | cloud | py | 9 | see brief | no; #164 transform enabled on live configs only after Eugene |
| 43 | #165 | [Time health](165-time-health.md), prompt `briefs/cloud/p2-time-health.md` | `deepsignal/p2-time-health` | `3b4b76e` contrib tree | cloud | py | 9 | see brief | no |
| 44 | #163 | [Config provenance](163-config-provenance.md), prompt `briefs/cloud/p2-config-provenance.md` | `deepsignal/p2-config-provenance` | `3b4b76e` contrib tree | cloud | py | 9 | see brief | no |
| 45 | #168 | [Unified event timeline](168-event-timeline.md), prompt `briefs/cloud/p2-event-timeline.md` | `deepsignal/p2-event-timeline` | `3b4b76e` contrib tree | cloud | py | 9 | see brief | no |
| 46 | #167 | [Alarm-linked runbooks](167-runbooks.md), prompt `briefs/cloud/p2-runbooks.md` | `deepsignal/p2-runbooks` | `3b4b76e` contrib tree | cloud | py | 9 | see brief | no |
| 47 | #166 | [Continuous archive readiness](166-archive-readiness.md), prompt `briefs/cloud/p2-archive-readiness.md` | `deepsignal/p2-archive-readiness` | `3b4b76e` contrib tree | cloud | py | 9 | see brief | no |
| 48 | #169 | [Science trust view](169-console-trust.md), prompt `briefs/cloud/p2-console-trust.md` | `deepsignal/p2-console-trust` | `deepsignal/console-contract` | cloud | node | 9 | see brief | no |

## Not briefed, and why

- #122 small core fixes: two of its four parts already exist on fork `dev` (round-robin polling with per-command timeout in `PolledSerialReader`; per-file headers via `LogfileWriter` `header`/`header_file`). ADAM-4000 polling moved into #121. The emulated flag (value 2/2/2) is parked as a console follow-up: a simulated logger config adds `emulated: 1` and the console shows EMULATED. Decided under D-NIGHT1.
- #107 map: console module `map` (briefs/console/map.md).
- #124 install clock half: briefs/install-clock.md (submitted). The `--defaults` half is #124 above.
- #129 derived-product suggester: backlog, no brief yet.
- #136 OceanDataTools QA tool adapters: backlog; the tools are marked under heavy development.

## What is left after these land

1. Console follow-ups: host health tiles (#119 fields), emulated badge, routes drawn on the map (#108 + #107), wizard page over #114/#125/#126/#128, roles wired into pages (#115).
2. Eugene decisions (MORNING): login layer for #115; release policy content for #116; SWL values for #109; MFP/MOMS access for #120; a hand-downloaded KAOU SAMOS day for #111/#95.
3. Verification outside the sandbox: ERDDAP load of #104 output; real-hardware run of #125; install-clock with `--defaults` (#124) on both Ubuntu legs plus a Mac.
4. Integration: merge order is free (disjoint files); run the desk gate contrib mode (#49) over all p2 branches together, then re-score docs/TARGET-PARITY.md.

File ownership is disjoint: Python modules own `contrib/deepsignal/<module>/`, its test folder, one docs file and `configs/<module>_*.yaml`; console modules own `src/modules/<id>/**` and one docs file; core tasks own only their new files. Empty `__init__.py` files are byte-identical across branches.

Environments: py and core tasks need Python 3.12 plus OpenRVDAS requirements, pytest and flake8. node tasks need the console environment (Node 22, `npm ci` in `contrib/deepsignal/console`). mac tasks run through `~/bin/ds-codex` with Astra high.


## Scoreboard drivers (IDEAS #182-#187, D-SCORE2)

Wave 1 runs in parallel (disjoint files; `contract.py` byte-identical on every branch, sha256 in each brief). Then the build lead merges #182 to #186 into `deepsignal/scoreboard-integ` and launches wave 2.

| IDEAS | Task | Branch | Base | Lane | Wave | Depends on |
|---|---|---|---|---|---|---|
| #182 | [Profile schema and loader](182-scoreboard-profiles.md), prompt `briefs/cloud/p2-scoreboard-profiles.md` | `deepsignal/p2-scoreboard-profiles` | `3b4b76e` | cloud | 1 | none |
| #183 | [Transports](183-scoreboard-transports.md), prompt `briefs/cloud/p2-scoreboard-transports.md` | `deepsignal/p2-scoreboard-transports` | `3b4b76e` | cloud | 1 | none |
| #184 | [Text codec](184-scoreboard-text-codec.md), prompt `briefs/cloud/p2-scoreboard-text-codec.md` | `deepsignal/p2-scoreboard-text-codec` | `3b4b76e` | cloud | 1 | none |
| #185 | [Alpha codec](185-scoreboard-alpha-codec.md), prompt `briefs/cloud/p2-scoreboard-alpha-codec.md` | `deepsignal/p2-scoreboard-alpha-codec` | `3b4b76e` | cloud | 1 | none |
| #186 | [Modbus codec](186-scoreboard-modbus-codec.md), prompt `briefs/cloud/p2-scoreboard-modbus-codec.md` | `deepsignal/p2-scoreboard-modbus-codec` | `3b4b76e` | cloud | 1 | none |
| #187 | [Bench tool](187-scoreboard-bench.md), prompt `briefs/cloud/p2-scoreboard-bench.md` | `deepsignal/p2-scoreboard-bench` | `deepsignal/scoreboard-integ` | cloud | 2 | #182-#186 merged |


| 49 | #188 | [AI watch assistant: event-triggered triage](188-ai-triage.md), prompt `briefs/cloud/p2-ai-triage.md` | `deepsignal/p2-ai-triage` | `3b4b76e` contrib tree | cloud | py | 10 | #162, #167, #168 formats (reads files only) | no; API path on by default with caps (Eugene 2026-11-18) |
