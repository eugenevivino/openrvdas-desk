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

Not written yet: #115, #118, #119, #120, #124, #113, #121, #122.

File ownership is disjoint: Python modules own `contrib/deepsignal/<module>/`, its test folder, one docs file and `configs/<module>_*.yaml`; console modules own `src/modules/<id>/**` and one docs file; core tasks own only their new files. Empty `__init__.py` files are byte-identical across branches.

Environments: py and core tasks need Python 3.12 plus OpenRVDAS requirements, pytest and flake8. node tasks need the console environment (Node 22, `npm ci` in `contrib/deepsignal/console`). mac tasks run through `~/bin/ds-codex` with Astra high.
