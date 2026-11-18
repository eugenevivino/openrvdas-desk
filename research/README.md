# Research desk

One question per file: `YYYY-MM-DD-<topic>.md`. Lead with the answer, then
evidence. Mark each claim verified (with source) or inferred. Research informs
decisions; it does not make them. A decision goes to `docs/DECISIONS.md`.

Design docs from the project threads (claude.ai artifacts, 2026-11-17):
- Scoreboard writer: https://claude.ai/artifact/XYUFNgc4nP67DBBS7RUviN
- MCP server: https://claude.ai/artifact/VtfCM7KR2oRVa1BXiqnbFb
- Competitive analysis and roadmap: https://claude.ai/artifact/H3523sKMcYXJK6bsjRfTpN
- MetAcq gap map: https://claude.ai/artifact/QkQXV3ZZkgHrYJNQrew29B

Plans written as research files:
- Old-data reanalysis program (D-REAN1): `2026-11-18-reanalysis-program.md`
- Reanalysis pilot cruises from R2R and CCHDO: `2026-11-18-r2r-pilot-cruises.md`
- Adoption strategy (D-ADOPT1 open): `2026-11-18-adoption-strategy.md` (source truncated)
- MCP reference architecture (#64-#69): `2026-11-18-mcp-reference-architecture.md` (source truncated)
- Drift detection and correction report (Eugene, Deep Research; D-REAN2): `2026-11-18-drift-detection-report.md`


## Index of research stored here (2026-11-17 and 2026-11-18)

| File | Date | Source thread | One-line takeaway |
|---|---|---|---|
| `2026-11-17-ai-methods.md` (+ `ai-methods-notes/`, `2026-11-17-ai-methods-source.md`) | 11-17 | AI methods | Simple statistics (robust baselines, changepoints, cross-sensor checks) beat deep models aboard; LLMs only for explanation, with the user's own key. |
| `2026-11-18-drift-detection-report.md` | 11-18 | Reanalysis (Eugene's Deep Research) | How to detect and correct sensor drift in underway data; basis for D-REAN2. |
| `2026-11-18-reanalysis-program.md` | 11-18 | Reanalysis | Improve old cruise data pass by pass (D-REAN1). |
| `2026-11-18-r2r-pilot-cruises.md` | 11-18 | Reanalysis | Three Revelle and GO-SHIP pilot cruises from R2R and CCHDO. |
| `2026-11-18-adoption-strategy.md` | 11-18 | Adoption (source truncated) | How DeepSignal gets used operationally on vessels; D-ADOPT1 open. |
| `2026-11-18-mcp-reference-architecture.md` | 11-18 | MCP (source truncated) | Reference architecture for an OpenRVDAS MCP; superseded in plan by D-MCP2. |
| `2026-11-18-projectarchitect.md` | 11-18 | Build lead | Review of ProjectArchitect (PA3) as a tool for this project. |
| `2026-11-18-django-test-basic.md` | 11-18 | Build lead | Root cause of the Django `test_basic` failure on the fork. |
| `2026-11-18-samos-sample-files.md`, `2026-11-18-samos-ship-format-and-fm13.md`, `samples/` | 11-18 | Met reports (#111) | SAMOS ship text format and FM-13 BBXX facts and sample files; D-111A. |
| `RVTEC-SURVEY.md` | 11-18 | Pain points | 18 interview questions for RVTEC techs mapped to roadmap items. |
| `2026-11-18-scoreboard-research.md` | 11-18 | Scoreboard | Fleet research on deck LED scoreboards and how boards are driven; basis for D-SCORE1, D-SCORE2 and #182-#187. |
| `2026-11-18-competitive-improvements.md` | 11-18 | Competitive analysis | Where OpenRVDAS can improve against CORIOLIX, MetAcq and others; feeds the roadmap and TARGET-PARITY. |
| `2026-11-18-metacq-manual-analysis.md` | 11-18 | MetAcq gap map | What the MetAcq manual implies we must replicate; feeds the parity scorecard. |
| `2026-11-18-proposal-unbuilt-ideas.md` | 11-18 | Proposal mining | Mines the SOII proposal (IDEAS #52-#62, D-SOII1) and signals of opportunity (T-SIG, #78-#103, D-SIG1) for unbuilt ideas. |
| `2026-11-18-mcp-design.md` | 11-18 | MCP design | Design body for the MCP: 11 high-level tools over one setup engine, apply as the only write path (D-MCP2). |

## Reports that live in docs/ (linked, not copied)

| File | Source thread | One-line takeaway |
|---|---|---|
| `../docs/PAIN-POINTS.md`, `../docs/PAIN-POINTS-MAP.md` | Pain points (Deep Research, verbatim) | Gap map and order for the operational truth layer (#162-#169); D-POSITION1. |
| `../docs/TARGET-PARITY.md` | Parity | Scorecard against CORIOLIX and MetAcq plus our own plan. |
| `../docs/ECOSYSTEM.md` | Ecosystem | How DeepSignal fits with OpenVDM, Sealog, QA tools (#131-#136). |
| `../docs/SHIP-SYSTEMS.md` | Ship systems | Passive-first integration with sonars, bridge, engineering, instrument servers (D-SHIP1). |
| `../docs/IDEAS.md`, `../docs/REFERENCE.md` | Build lead, Reference | All ideas and the canonical feature list. |

## Still to land (reports that exist only in chat or as artifacts; owners asked to drop the text on the shared mount)

sample data (catalog at `../docs/SAMPLE-DATA.md`) (`/mnt/project-files/sample-data`, manifest only, large files stay on the mount), sonar science (#170-#181).
