# Mining Eugene's proposals for unbuilt ideas (2026-11-18)

Thread: "Mine DeepSignal proposal for unbuilt ideas". Two sources were mined
against the desk backlog (IDEAS.md, ROADMAP.md, briefs/, the Console design and
the modules in flight: vector wind, QARTOD flags, scoreboard, MCP server, MetAcq
replication, AI drift and correlation methods).

1. **SOII/DeepSignal leadership proposal** (NSF 26-512 AIDatasets:Impact,
   Scripps, 12 Oct 2026, not funded). Source tag T-SOII. IDEAS #52 to #62.
2. **Deep Research report #2, "High-Value Signals of Opportunity in Routine
   Research-Vessel Data"**. Source tag T-SIG. IDEAS #78 to #103.

Rule for both: novelty and citations are leads to verify, not facts.

## Part 1. SOII proposal

### What the proposal was
A $2.0M, 36-month plan to make archived ocean data more trustworthy. It would
link each measurement to its instrument history, calibration, clock and
processing, use "retrospective lookahead" to separate sensor drift from real
ocean change, fuse sensors, and publish versioned derived datasets. Most of it
targets archives. Its lasting value for DeepSignal is its **rigor**: proving a
sensor drifted, and proving a fix is honest.

### Principles carried into every DeepSignal module
- Raw data is immutable. Every enhancement is a separate layer linked to its
  inputs, method, code version, uncertainty, reviewer and release decision.
- AI and math may suggest and show evidence. They never silently rewrite data
  and never command ship systems.
- Live mode can never use future data. Retrospective (post-cruise) mode may,
  and the two are evaluated separately.
- Abstain when the data cannot separate a sensor change from an ocean change.

### New or stronger ideas added (IDEAS #52 to #62)

| # | Idea | What it is | Who it helps | Fits |
|---|---|---|---|---|
| 52 | Instrument history graph | Per sensor: serial, firmware, calibrations, repairs, swaps, position, acquisition software, clock source, dated and linked to data; contradiction checker. Extends #7 | Techs (one true story per sensor), shore, drift and MCP tools | Module, Phase 1 |
| 53 | Fault-injection benchmark | Replay real data with injected drift, step, lag, hysteresis, clock resets, spikes; real fronts as traps; score detection time and false flags | Everyone indirectly: makes "bad sensor found in under 1 hour" measurable | Test tooling for all QC and AI modules |
| 54 | Post-cruise drift review | Two-sided state-space smoothing using later data (post-cal, later casts, bottles) | Science, shore data managers | AI, offline |
| 55 | "Cannot tell" verdict | Drift tests may answer UNDECIDED instead of forcing a flag | Bridge (fewer false alarms), science (no wrong fixes) | QARTOD and drift modules |
| 56 | Correction ledger with sign-off | Reversible correction layer with evidence, uncertainty, reviewer; raw never changes. Pairs with #32 | Science, shore, techs | Module |
| 57 | Uncertainty on every value | Stated error bar per derived value, checked against references | Science | AI/QC |
| 58 | End-of-cruise R2R-ready package | One button: raw, flags, ledger, instrument history, provenance, changelog | Techs, shore | Module, Phase 3 |
| 59 | Legacy archive readers | Read SCS, MetAcq, R2R files into OpenRVDAS records | Science, shore; feeds replay #33, search #27, bench #53 | Readers |
| 60 | Sensor response correction | Undo characterized lags (TSG plumbing, time constants), output marked reconstructed | Science | Transform |
| 61 | Instrument diagnostic channels | Log health fields instruments send but parsers drop (voltage, pump, signal) | Techs | Health board |
| 62 | AI audit trail | Log every MCP/AI question, tool call, answer and data read | Shore, ship ops, security | MCP |

Skipped as already covered: digital twin (#26), cross-sensor fusion (#25),
provenance hashes (#32). Skipped as not product work: NSF budget, staffing,
governance and IP sections.

### Recommendation and what happened
Top picks: #52, #53, #56, #55, #54. Eugene approved building them
(2026-11-18, D-SOII1). Briefs written in desk `briefs/`:
`deepsignal-instrument-history.md` (#52), `deepsignal-fault-bench.md` (#53),
`deepsignal-correction-ledger.md` (#56), `deepsignal-post-cruise-drift.md`
(#54, Astra, after #53 and #56). #55 went to the QARTOD thread (now its
AMBIGUOUS verdict). Fork branches exist at contrib base 3b4b76e. Queue is owned
by the build lead (cloud lane for #52 and #53, Mac lane for #56 and #54).

UI follow-up: three Console pages proposed and handed to the dashboard thread:
calibration age board (from #52), Corrections approve and roll back (#56), and
Drift report with drifted / fine / cannot tell (#54). #53 has no UI.

## Part 2. Signals-of-opportunity report (T-SIG)

### Core ideas of the report
- **Redundant physics**: the ship already measures the same process several
  ways (waves in IMU, GNSS, acoustics, propulsion; moisture in GNSS delay,
  MET, radiometry, link loss). Agreement between them is internal validation
  a single-stream ML detector cannot give.
- **The ship as a forcing function**: turns, speed changes and thrusters are
  natural experiments that show which sensors are measuring the ship.
- **Two tiers**: R = reproducible from R2R archive streams; V = needs on-vessel
  telemetry (machinery, DP, modem, hydrophone, raw GNSS) that R2R normally lacks.
- **Statistical control**: ship data are autocorrelated, so per-second
  p-values are invalid. Use effective sample size, block bootstrap, surrogate
  nulls, BH/BY false-discovery control per family, and demand replication on
  held-out cruises. Ship-coordinate invariance is the key negative control.
- **Alert rule**: score plus persistence or corroboration plus a plain
  explanation naming the supporting streams. The contaminant is an observation:
  output a probability and explanation, never delete.

### Added to the backlog (IDEAS #78 to #103; N/S/F are the report's scores)

| # | Idea | N/S/F, tier |
|---|---|---|
| 78 | Ship-coupling discovery engine (report rank 1) | 5/5/5, R |
| 79 | Dependency-graph fault detector (rank 3) | 5/5/5, R |
| 80 | Directional wave spectrum from motion (rank 2) | 3/5/5, R if MRU |
| 81 | Self-calibrating ship wave buoy | 4/5/4, R |
| 82 | Current from SOG minus STW | 3/5/5 R; 4/5/4 V |
| 83 | GNSS precipitable water vapor | 2/5/3, R with RINEX |
| 84 | GNSS reflectometry for sea ice | 3/5/3, R with raw GNSS |
| 85 | Ionosphere TEC and scintillation | 3/4/3, R with raw GNSS |
| 86 | GNSS interference sentinel (rank 6) | 3/5/5, R plus AIS |
| 87 | Satellite-link rain gauge (rank 10, paper candidate) | 5/4/5, V |
| 88 | Joint environmental inversion | not scored |
| 89 | Scattering-layer and migration atlas | 2/5/5, R |
| 90 | Acoustic mixed-layer depth | 2/5/5, R |
| 91 | Gas-seep discovery | 3/5/3, R |
| 92 | Echosounder noise floor as machinery monitor (rank 4, paper candidate) | 5/4/5, R then V |
| 93 | Rain and wind from underwater sound | 3/4/3, V |
| 94 | Incidental marine-mammal detection | 2/4/2 active, 3/5/4 passive, V |
| 95 | Live air-sea bulk fluxes (COARE) | 1/5/5, R |
| 96 | Mixing-state product | 4/5/4, R |
| 97 | Submesoscale front detector (rank 7) | 3/5/5, R |
| 98 | Vessel-performance digital twin | 3/4/5, R proxy, V full |
| 99 | Environment-conditioned machinery health | 3/4/4, V |
| 100 | Fuel and route counterfactual | 2/3/4, V |
| 101 | Masked multirate ship encoder (rank 9) | 4/5/4, R |
| 102 | Physics-conditioned representations | 5/5/3, R |
| 103 | Cross-vessel sensor ontology | 5/5/3, R |

Existing rows strengthened rather than duplicated: #9 (alert rule), #39
(reciprocal-maneuver flow distortion fit), #42 (GNSS-R needs raw SNR), #43
(points to #92 and #99). The report's "ship contamination supervisor" is the
live half of #78, not a separate row.

### Briefed (D-SIG1)
Both are a live OpenRVDAS transform plus an offline archive runner, cloud lane
(Sol medium, formulas pinned in the brief), Astra xhigh review, scored on the
fault bench #53. The bench brief gained a configurable flag suffix, plug-in
injectors and false alarms per ship-day.
- `briefs/deepsignal-ship-coupling.md` (#78): lagged dependency atlas,
  effective sample size, block bootstrap, circular-shift nulls, BH/BY per
  family, discovery vs holdout replication, reciprocal-leg and time-shift
  invariance controls, polar contamination tables; live transform adds
  `<field>_SHIP`, `_SHIP_why`, `_SHIP_QC` from a frozen atlas.
- `briefs/deepsignal-dependency-graph.md` (#79): declared physics edges plus
  learned edges on healthy data per regime, CUSUM on standardized residuals,
  node attribution with "cannot tell" for two-node cases, persistence gate;
  adds `<field>_DG` and `_DG_why`.

### Next candidates by report rank
#80 wave spectrum from motion, #92 echosounder noise as machinery monitor,
#90 and #96 acoustic MLD and mixing state, #86 GNSS integrity sentinel.
