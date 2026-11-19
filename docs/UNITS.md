# Units and superseded branches (D-PIPE1 rules 2 and 3)

Stamps and counts: `python3 tools/finish-line.py` (manifest `docs/units.json`). Regenerate the manifest
only from logged evidence at the exact head; never mark a stamp without evidence.

## Work in progress (D-WIP3, cap 3, all on the Nov 25 path)

| Unit | Branch | Head | Status |
|---|---|---|---|
| console-ui | `deepsignal/integration` | 7c60dbf | ACTIVE (D-WIP3 slot 1: console pilot and follow-ups) |
| console-soak-24h | `deepsignal/integration` | 7c60dbf | ACTIVE (D-WIP3 slot 3: 24 h soak of the pilot candidate; not started) |
| sec-cds-joint | `deepsignal/sec-cds-joint` | 82c8f3d | ACTIVE (D-WIP3 slot 2: security redesign) |

## PAUSED (D-WIP3: launch nothing new; in-flight jobs finish as they are)

| Unit | Branch | Head |
|---|---|---|
| app-ia | `deepsignal/app-ia` | 7c166e0 |
| correction-ledger | `deepsignal/correction-ledger` | 59b061b |
| dependency-graph | `deepsignal/dependency-graph` | 3b4b76e |
| docs-journeys | `deepsignal/docs-journeys` | 449d0ea |
| fault-bench | `deepsignal/fault-bench` | 58e66c8 |
| instrument-history | `deepsignal/instrument-history` | 973a87a |
| p2-adcp-health | `deepsignal/p2-adcp-health` | b3ccabc |
| p2-ai-triage | `deepsignal/p2-ai-triage` | 7a572e7 |
| p2-archive-compress | `deepsignal/p2-archive-compress` | 0fa1d53 |
| p2-archive-readiness | `deepsignal/p2-archive-readiness` | 72e6d7a |
| p2-best-source | `deepsignal/p2-best-source` | 090e208 |
| p2-cal-units-registry | `deepsignal/p2-cal-units-registry` | 5792924 |
| p2-cast-view | `deepsignal/p2-cast-view` | 8f55b51 |
| p2-component-catalog | `deepsignal/p2-component-catalog` | a226798 |
| p2-config-from-inventory | `deepsignal/p2-config-from-inventory` | fe54b5d |
| p2-config-lint | `deepsignal/p2-config-lint` | 2f15cb8 |
| p2-config-provenance | `deepsignal/p2-config-provenance` | d73939a |
| p2-console-chain | `deepsignal/p2-console-chain` | 4bfd755 |
| p2-console-trust | `deepsignal/p2-console-trust` | 4bfd755 |
| p2-cruise-context | `deepsignal/p2-cruise-context` | 6037a9d |
| p2-cruise-meta | `deepsignal/p2-cruise-meta` | 4550458 |
| p2-depth-consensus | `deepsignal/p2-depth-consensus` | 4e606db |
| p2-device-pack | `deepsignal/p2-device-pack` | 1a6f1ed |
| p2-device-servers | `deepsignal/p2-device-servers` | 3b4b76e |
| p2-doc-store | `deepsignal/p2-doc-store` | 3f8322a |
| p2-eez-mode | `deepsignal/p2-eez-mode` | 3b4b76e |
| p2-erddap | `deepsignal/p2-erddap` | a4f8e4c |
| p2-event-timeline | `deepsignal/p2-event-timeline` | a5a9e0f |
| p2-flow-state | `deepsignal/p2-flow-state` | 2df7bd5 |
| p2-geometry | `deepsignal/p2-geometry` | 7b024d7 |
| p2-grafana-quality | `deepsignal/p2-grafana-quality` | b7d4daf |
| p2-host-health | `deepsignal/p2-host-health` | 683398a |
| p2-iec450-bridge | `deepsignal/p2-iec450-bridge` | 3b4b76e |
| p2-install-defaults | `deepsignal/p2-install-defaults` | 21e6bf8 |
| p2-instrument-init | `deepsignal/p2-instrument-init` | f5f8c95 |
| p2-link-health | `deepsignal/p2-link-health` | 3b4b76e |
| p2-met-formulas | `deepsignal/p2-met-formulas` | 371284a |
| p2-met-reports | `deepsignal/p2-met-reports` | ceb5c8b |
| p2-onboard-wizard | `deepsignal/p2-onboard-wizard` | 9533ff6 |
| p2-openvdm-bridge | `deepsignal/p2-openvdm-bridge` | 81b7748 |
| p2-release-policy | `deepsignal/p2-release-policy` | 6b19de4 |
| p2-rest-api | `deepsignal/p2-rest-api` | 8756fed |
| p2-roles | `deepsignal/p2-roles` | 0fffb9b |
| p2-route-eta | `deepsignal/p2-route-eta` | 2a8037e |
| p2-runbooks | `deepsignal/p2-runbooks` | 357fd03 |
| p2-scoreboard-alpha-codec | `deepsignal/p2-scoreboard-alpha-codec` | f9f42eb |
| p2-scoreboard-modbus-codec | `deepsignal/p2-scoreboard-modbus-codec` | 6ec287c |
| p2-scoreboard-profiles | `deepsignal/p2-scoreboard-profiles` | dd3f23a |
| p2-scoreboard-text-codec | `deepsignal/p2-scoreboard-text-codec` | b989dfa |
| p2-scoreboard-transports | `deepsignal/p2-scoreboard-transports` | 4c113f7 |
| p2-sealog-bridge | `deepsignal/p2-sealog-bridge` | 3b4b76e |
| p2-seep-repeatability | `deepsignal/p2-seep-repeatability` | 01dd803 |
| p2-seismic-shot-qc | `deepsignal/p2-seismic-shot-qc` | 0310dc6 |
| p2-shore-snapshot | `deepsignal/p2-shore-snapshot` | 159240c |
| p2-sounding-uncertainty | `deepsignal/p2-sounding-uncertainty` | cde3852 |
| p2-stream-discovery | `deepsignal/p2-stream-discovery` | 9a9e183 |
| p2-stream-health | `deepsignal/p2-stream-health` | 0f2137c |
| p2-subbottom-reflectors | `deepsignal/p2-subbottom-reflectors` | 7e2a0e9 |
| p2-sv-consistency | `deepsignal/p2-sv-consistency` | cfead37 |
| p2-sv-manager | `deepsignal/p2-sv-manager` | 57391de |
| p2-swath-refraction | `deepsignal/p2-swath-refraction` | a337760 |
| p2-time-health | `deepsignal/p2-time-health` | e1b0e14 |
| p2-vocab | `deepsignal/p2-vocab` | 9749bdb |
| p2-weighted-depth | `deepsignal/p2-weighted-depth` | 6c3e518 |
| post-cruise-drift | `deepsignal/post-cruise-drift` | 3b4b76e |
| qartod-flags | `deepsignal/qartod-flags` | 736ef2e |
| ship-coupling | `deepsignal/ship-coupling` | 4882b47 |
| vector-wind | `deepsignal/vector-wind` | 03ca54c |

## SUPERSEDED-BY-UNIT

These branches never block a unit. Fold one in only if its unit needs the fix; retire after the unit lands.

| Branch | Head | Status | Unit |
|---|---|---|---|
| `deepsignal/console-contract` | 4bfd755 | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-core` | 82ec7ca | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-core-v2` | 2ebdf91 | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-core-v2-a` | 82ec7ca | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-core-v2-b` | 82ec7ca | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-core-v2-c` | 82ec7ca | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-harness-fixture` | 307ba2b | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-harness-soak` | ca98149 | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-harness-source-loss` | 307ba2b | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-install` | c32b6c9 | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-mod-auto-pages` | bc6c864 | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-mod-bridge` | 585ca4c | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-mod-chart` | f24f23b | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-mod-health` | 991e456 | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-mod-kiosk-night` | ed61d5f | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-mod-map` | 8f6a226 | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-mod-stale-banner` | 8e1c58b | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-mvp` | f38b52e | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/console-visual-gate` | 4bfd755 | SUPERSEDED-BY-UNIT | console-ui |
| `deepsignal/sec-cds-lockdown` | eadb0a2 | SUPERSEDED-BY-UNIT | sec-cds-joint |
