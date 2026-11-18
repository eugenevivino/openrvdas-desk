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

Not written yet: #116, #108, #112, #114, #117, #123, #115, #118, #119, #120, #124, #113, #121, #122.

File ownership is disjoint: Python modules own `contrib/deepsignal/<module>/`, its test folder, one docs file and `configs/<module>_*.yaml`; console modules own `src/modules/<id>/**` and one docs file; core tasks own only their new files. Empty `__init__.py` files are byte-identical across branches.

Environments: py and core tasks need Python 3.12 plus OpenRVDAS requirements, pytest and flake8. node tasks need the console environment (Node 22, `npm ci` in `contrib/deepsignal/console`). mac tasks run through `~/bin/ds-codex` with Astra high.
