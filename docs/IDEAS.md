# Ideas backlog (master list)

Every idea in one place. ROADMAP.md ranks what is next; this file keeps
everything, so nothing raised in a thread is lost. Add a row the day an idea
comes up. Never delete a row: mark it DROPPED with a reason.


**Numbering: the build lead owns IDEAS numbers (next free: 182; 161 fusion, 162-169 operational truth layer, 170-181 reserved for the sonar-science thread); 162-173 reserved for the sonar-science thread). Other threads do not
assign numbers. Write ideas as unnumbered drafts in your patch notes and ask the build
lead for a range, to avoid collisions (three-way collision on 2026-11-18).**
Status: PROPOSED (idea only), DESIGNED (design doc exists), BUILDING (brief
and branch exist), DONE, DROPPED. Phase matches ROADMAP.md (N = novel, not
yet phased). Every new capability is an overlay module (D-ARCH1) unless the
row says "core fix".

"Novel" means we found no shipboard DAS doing it in today's competitive
research (CORIOLIX, SCS, MetAcq, Grafana stacks). **All novelty claims are
unverified.** Check prior art before saying "first" anywhere public.

Sources: T-SCORE scoreboard thread, T-METACQ MetAcq thread, T-COMP
competitive analysis thread, T-MCP MCP thread, T-AI AI methods research
(`research/2026-11-17-ai-methods.md`), T-DESK this setup thread, EUG Eugene's
own message, T-SOII Eugene's Oct 2026 SOII/DeepSignal leadership proposal, T-REAN the reanalysis planning thread. Design docs are linked in `research/README.md`.

## Success metrics (proposed, not yet agreed)

| Metric | Target | How we would measure |
|---|---|---|
| Bad sensor detected | under 1 hour from onset | Replay recorded faults and injected faults through the overlay; time from onset to flag |
| Add a new sensor | under 15 minutes | Timed run by a technician: plug in, identify, accept config, data flowing with QC |
| Data fixed on shore after the cruise | under 1% of values | Share of values changed in post-cruise processing, compared with today's baseline |

## Phase 0 and 1: foundation and first modules

| # | Idea | One line | Status | Phase | Source |
|---|---|---|---|---|---|
| 1 | Django LoggerConfig bug fix | `TestDjangoServerAPI.test_basic` gets two LoggerConfigs on master and dev, both platforms; fix plus test, upstream PR (core fix) | PROPOSED | 0 | T-DESK |
| 2 | macOS UDP and timing test failures | 3 UDP tests read packets out of order, 1 timing test is slow on macOS only; find cause, file issues (core fix if real) | PROPOSED | 0 | T-DESK |
| 3 | Overlay package skeleton | `openrvdas-overlay`: package, CachedDataServer client, `module:` config examples, its own gate | PROPOSED | 1 | EUG, T-DESK |
| 4 | Vector wind averaging | Average wind as vectors so 359 and 1 degree give 0, not 180. Built as DeepSignal `VectorWindAverageTransform` on fork branch `claude/project-thread-un3kq6` (558e45b), 23 tests pass; PR to contrib not yet sent | BUILDING | 1 | T-METACQ |
| 5 | Scoreboard writer | Latest-value cache, page and cell layout, per-model formatter, Serial/TCP/UDP transport, stale shown as stale | DESIGNED | 1 | T-SCORE |
| 6 | $WICOR writer | MetAcq-compatible one-line met broadcast, after close read of the manual's format chapter | DESIGNED | 1 | T-METACQ |
| 7 | Sensor calibration records | Serial number, calibration date and coefficients per sensor, applied by a transform with version tracking | DESIGNED | 1 | T-METACQ |

## Phase 2: quality and alarms

| # | Idea | One line | Status | Phase | Source |
|---|---|---|---|---|---|
| 8 | QARTOD-style QC flags | Range, spike, flat-line, rate-of-change tests emit flags that travel with values, never delete data | DESIGNED | 2 | T-AI, T-METACQ |
| 9 | State-aware alarms with watch verdicts | Alarms that know ship state (on station, transit, CTD in water), and a watch stander marks each real or false so thresholds improve T-SIG adds: an alert needs a high score, persistence or corroboration, and a plain explanation naming the supporting streams (IMO bridge alert management style) | PROPOSED | 2 | T-COMP, T-AI |
| 10 | Redundant-sensor CUSUM drift | CUSUM on the difference between paired sensors finds steps and slow drift between them | DESIGNED | 2 | T-AI |
| 11 | Drift vs independent references | Compare sensors with CTD casts, bottle samples and ERA5 reanalysis to find drift that redundancy cannot | DESIGNED | 2 | T-AI |

## Phase 3: Cruise Console and AI access

| # | Idea | One line | Status | Phase | Source |
|---|---|---|---|---|---|
| 12 | Health board | Every sensor: last value, age, QC flag, alarm state, on one page | DESIGNED | 3 | T-COMP |
| 13 | Night-safe bridge view | Huge readouts, wind relative to the bow, true night mode, stale shown as stale | DESIGNED | 3 | T-COMP, T-METACQ |
| 14 | Science, tech and shore views | Role views over the same data: science party, technicians, shore support | PROPOSED | 3 | T-COMP |
| 15 | Event log | Stations, casts, deployments and notes, timestamped and linked to data | DESIGNED | 3 | T-COMP |
| 16 | Binned downloads | Science-ready averaged files on request, any interval, with QC flags | DESIGNED | 3 | T-COMP |
| 17 | Ship-to-shore sync, bulk | Globus or rsync for files, resumable, scheduled around the link | PROPOSED | 3 | T-COMP |
| 18 | Ship-to-shore sync, live | Buffered, compressed MQTT or websocket stream that survives outages | PROPOSED | 3 | T-COMP |
| 19 | Bandwidth-aware link profiles | Different send plans for Starlink and VSAT, chosen automatically from measured link | PROPOSED | 3 | T-COMP |
| 20 | MCP server, read-only | `openrvdas-mcp`: query, config help to a drafts folder, analysis computed on the ship | DESIGNED | 3 | T-MCP |
| 21 | MCP issue-finding tools | Tools that list suspect sensors, gaps, stale feeds and flag spikes with evidence | PROPOSED | 3 | T-MCP |
| 22 | MCP precision and calibration tools | Tools that report each sensor's precision, calibration age, and drift estimate | PROPOSED | 3 | T-MCP |
| 23 | Multi-AI-client support | Same MCP server for Claude, Codex and other MCP clients, tested with each | PROPOSED | 3 | T-MCP |
| 24 | Codex as a builder | Codex joins the team as a Builder role through `codex mcp-server`, same briefs and gate | PROPOSED | 3 | T-DESK |

## Novel capabilities (unverified novelty)

| # | Idea | One line | Status | Phase | Source |
|---|---|---|---|---|---|
| 25 | Physics referee (sensor consensus) | Linked sensors check each other live (anemometers plus GPS plus gyro, gyro vs GPS course, hull SST vs TSG with lag); disagreement is a flag naming the physics that failed | PROPOSED | N | T-DESK, T-AI |
| 26 | Sensor digital twin | A model per sensor of what it should read now, from its neighbours and physics; residuals feed QC and drift | PROPOSED | N | T-AI |
| 27 | Cruise memory search | Search every past cruise by situation ("last time wind and swell looked like this", "every CTD cast deeper than 3000 m") | PROPOSED | N | T-COMP |
| 28 | Self-writing cruise log | Drafts the daily log from events, alarms and data for the watch to edit and sign | PROPOSED | N | T-COMP |
| 29 | Plug-and-identify | Fingerprint an unknown serial or UDP stream and propose a parser config for a technician to accept | PROPOSED | N | T-DESK |
| 30 | Scientist co-pilot | Ask in plain words, get plots and numbers computed on the ship, every claim linked to data | PROPOSED | N | T-MCP, T-COMP |
| 31 | Clock forensics | Measure each instrument's clock skew and latency continuously from shared motion signals | PROPOSED | N | T-DESK |
| 32 | Provenance hashes | Every value carries a lineage hash; daily signed manifests make the dataset reproducible and tamper-evident | PROPOSED | N | T-DESK |
| 33 | Time-travel replay | Scrub the ship state to any past second; re-run new transforms over recorded raw data with a diff | PROPOSED | N | T-DESK |
| 34 | Plain-language alarms | An LLM compiles a sentence once into a reviewed deterministic rule; the ship runs the rule, not the model | PROPOSED | N | T-DESK |
| 35 | Semantic ship-to-shore | Send changes, anomalies and model parameters instead of raw streams; shore asks for detail on demand | PROPOSED | N | T-DESK |
| 36 | Calibration foresight | Forecast which sensor leaves spec before the next port | PROPOSED | N | T-DESK, T-AI |
| 37 | Cruise narrator | "What changed on the ship in the last 6 hours", answered from flags, events and alarms with links | PROPOSED | N | T-DESK, T-AI |

## Signals of opportunity (free measurements hidden in existing data)

| # | Idea | One line | Status | Phase | Source |
|---|---|---|---|---|---|
| 38 | Roll and heave cross-correlation | Shared ship motion seen by many sensors gives clock offset and response time per sensor (feeds 31) | PROPOSED | N | T-AI, T-DESK |
| 39 | Ship turns for flow distortion | Each turn sweeps relative wind across the bow; compare anemometers to map and correct the superstructure's flow distortion T-SIG: fit residual vs relative wind angle only in short stationary windows on reciprocal or circular maneuvers; N3/S5/F5, tier R | PROPOSED | N | T-AI |
| 40 | Diurnal solar heating bias | Separate radiative heating of air temperature and SST sensors from real signal using solar elevation and wind | PROPOSED | N | T-AI |
| 41 | Tides and ADCP bottom track | Use bottom track and known tides to check ADCP alignment and speed log calibration | PROPOSED | N | T-AI |
| 42 | GNSS reflectometry | Estimate significant wave height from sea-reflected GNSS signals already reaching the antennas T-SIG: N3/S5/F3; needs raw 10-20 Hz SNR, rarely archived, so tier R only where raw GNSS exists, else a cheap raw-GNSS sidecar | PROPOSED | N | T-AI |
| 43 | Engine and pump vibration health | Spot developing machinery faults from vibration in motion and acoustic sensors T-SIG: see #92 (echosounder noise floor) and #99 (environment-conditioned machinery model) | PROPOSED | N | T-AI |

## Kept for later

| # | Idea | One line | Status | Phase | Source |
|---|---|---|---|---|---|
| 44 | Fleet view | The overlay on several ships, compared on shore (health and calibration across the fleet) | PROPOSED | later | T-DESK |
| 45 | Open sensor-fingerprint library | Shared fingerprints between ships and institutions (feeds 29) | PROPOSED | later | T-DESK |
| 46 | Cost and savings status line | A small local script that shows tokens and spend per job and what retrievers kept out of context, from local logs only | PROPOSED | 0 | T-PA |
| 47 | Agent bench | A fixed set of small tasks that scores our briefs, models and retrievers over time, results saved as files | PROPOSED | later | T-PA |
| 48 | Retriever brief library | Reusable QUESTION/SCOPE/CAP briefs for gate TSVs, junit, device definitions, research notes | PROPOSED | 0 | T-PA |
| 49 | Gate contrib mode | `gate.sh` runs only core `test/`, so it never runs `contrib/deepsignal/test/`; add a mode that drops the contrib folder into a current core checkout and runs its tests plus flake8 | PROPOSED | 0 | T-DSWIND |
| 50 | Wind averages for the bridge and $WICOR | Feed DeepSignal one-minute and ten-minute true-wind averages (with gust and steadiness) to the night-safe bridge view (#13) and the $WICOR writer (#6) | PROPOSED | 1 | T-DSWIND |
| 51 | Two-anemometer wind consensus | Average port and starboard true wind, but prefer the upwind sensor (the one not in the ship's wind shadow) per window, and flag when they disagree | PROPOSED | N | T-DSWIND |

## From the SOII/DeepSignal proposal (Oct 2026)

Mined 2026-11-18 from Eugene's unfunded SOII leadership proposal. Only ideas
the backlog did not already have, or that make an existing row stronger.
Proposal rule kept for all of them: raw data is immutable; AI and math may
suggest and show evidence, never silently rewrite data or command the ship.

| # | Idea | One line | Status | Phase | Source |
|---|---|---|---|---|---|
| 52 | Instrument history graph | Per sensor: serial, firmware, calibration, repairs, swaps, mount position, acquisition software version and clock source, each dated and linked to data; contradiction checks for a tech to resolve (extends #7, feeds #11, #22, #36) Brief `briefs/deepsignal-instrument-history.md` | DESIGNED | 1 | T-SOII |
| 53 | Fault-injection benchmark | Replay real cruise data with injected drift, step bias, lag, hysteresis, clock resets and spikes, plus real fronts as traps; scores every QC and drift module on detection time and false-flag rate (makes the "bad sensor under 1 hour" metric measurable; gate for #8-#11, #25) Brief `briefs/deepsignal-fault-bench.md` | DESIGNED | 2 | T-SOII |
| 54 | Post-cruise drift review (lookahead) | After the cruise, use later data (post-cal, later casts, bottles, other sensors) with two-sided state-space smoothing to judge drift; strictly separate from live mode, which can never use the future Brief `briefs/deepsignal-post-cruise-drift.md` | DESIGNED | N | T-SOII |
| 55 | "Cannot tell" verdict | Drift and drift-vs-front tests may answer UNDECIDED when the data cannot separate a sensor change from a real ocean change (front, water mass), instead of forcing a flag; stated as such to the watch and on shore | PROPOSED | 2 | T-SOII |
| 56 | Correction ledger with sign-off | Every proposed correction stored as a separate, reversible layer: inputs, method, code version, uncertainty, evidence plot, reviewer, approve or roll back; raw never changes (pairs with #32) Brief `briefs/deepsignal-correction-ledger.md` | DESIGNED | 2 | T-SOII |
| 57 | Uncertainty on every value | Each derived value carries a stated uncertainty from calibration, sensor spec and processing; periodically checked against independent references to prove the error bars are honest | PROPOSED | N | T-SOII |
| 58 | End-of-cruise R2R-ready package | One button builds the cruise dataset: raw plus QC flags, corrections ledger, instrument history, provenance manifest, changelog, in archive-ready layout for R2R hand-off | PROPOSED | 3 | T-SOII |
| 59 | Legacy archive readers | Read-only readers that load past cruises from SCS, MetAcq and R2R files into the same records, so replay (#33), cruise memory search (#27) and the benchmark (#53) work on years of history | PROPOSED | N | T-SOII |
| 60 | Sensor response correction | Fit and undo known response lags (TSG plumbing delay, sensor time constants) as a reversible transform, only where the response is characterized; output marked as reconstructed (builds on #25, #38) | PROPOSED | N | T-SOII |
| 61 | Instrument diagnostic channels | Log the health fields instruments already send but parsers drop (supply voltage, pump state, signal strength, internal temperature) and show them on the health board (#12) | PROPOSED | 2 | T-SOII |
| 62 | AI audit trail | Every MCP/AI question, tool call and answer is logged with the data it read; AI tools stay read-only with no path to ship systems (hardens #20, #30) | PROPOSED | 3 | T-SOII |
| 63 | Old-data reanalysis loop | Run DeepSignal modules over archived cruises in scored passes; flags and corrections as signed, reversible ledger layers; keep a pass only if it beats the last on holdout references and the fault bench; stop on no gain or noise floor. Plan `research/2026-11-18-reanalysis-program.md` (uses #52-#60) | DESIGNED | N | EUG, T-REAN |
| 64 | MCP analytical gateway, read-only plus proposal-only v1 | MCP server in front of OpenRVDAS exposing typed domain tools only (query_timeseries, summarize_timeseries, get_instrument_metadata, validate_logger_config, render_plot); no execute_python/sql/shell; state changes only as proposals. Research `research/2026-11-18-mcp-reference-architecture.md` | PROPOSED | 3 | EUG |
| 65 | Separate approval and apply service | Proposals (config, dashboard patches) get a validator, diff, authorization policy and human approval record; a distinct-identity apply service executes and runs postcondition tests; MCP annotations are advisory, enforcement lives in code | PROPOSED | 3 | EUG |
| 66 | Provenance on every computed answer | Each MCP result carries query fingerprint, source ids, time bounds, sample counts, units, quality flags and the exact computation; the model picks the calculation, deterministic code computes it (extends #62) | PROPOSED | 3 | EUG |
| 67 | Time-series query budgets | Cap rows, time span, resolution and compute per MCP call and per identity; refuse or downsample with a stated reason | PROPOSED | 3 | EUG |
| 68 | Target MCP spec 2026-07-28 | Build the server stateless on the 2026-07-28 spec (Mcp-Method/Mcp-Name headers, cacheable lists, explicit handles), not older SSE/session patterns | PROPOSED | 3 | EUG |
| 69 | Golden-cruise MCP eval suite and local model tiers | Fixed questions with known answers on archived cruises, scored per model and quantized build; qualify Qwen3.5-9B and Qwen3.8-27B (plus a cloud model) behind one interface | PROPOSED | N | EUG |
| 70 | Read-only shadow pilot on Revelle or Sally Ride | Run DeepSignal alongside acquisition for a full cruise, raw preserved independently, removable with no change to acquisition; instrument the trial so the data proves benefit. Needs Scripps technical leadership agreement. Research `research/2026-11-18-adoption-strategy.md` | PROPOSED | N | EUG |
| 71 | Operator-from-docs install test | Success test: a non-author installs, diagnoses, upgrades and recovers DeepSignal from docs alone; second milestone is a vessel at another institution | PROPOSED | N | EUG |
| 72 | Non-OpenRVDAS stream adapters (CORIOLIX, SCS, MetAcq files) | Let the QC model ingest other vessel software's streams without coupling to their internals; pairs with #59 | PROPOSED | N | EUG |
| 73 | Publication and funding track | JTECH operational validation after first sea trial; JOSS after six months public history, tagged release and tests; funding order per adoption research (dates unverified) | PROPOSED | N | EUG |
| 74 | Independence-aware calibration evidence graph | Dependency graph of channels, references and fits that scores whether a correction is identifiable and refuses when it is not. **Paper candidate** (drift report gap list). Module `evidence-graph` | PROPOSED | N | EUG (drift report), T-REAN |
| 75 | Public sparse-reference drift benchmark | Publish raw shipboard streams plus maintenance logs, swaps, bottle and reference checks, pre and post cals and injected faults as an open benchmark; seed with the Revelle pilot (paper candidate) | PROPOSED | N | EUG (drift report), T-REAN |
| 76 | Front-versus-drift competing hypotheses | Bayesian model weighing drift, front, rain lens, plume, upwelling and fouling using spatial coherence, T-C-S physics, weather and maintenance events (paper candidate) | PROPOSED | N | EUG (drift report) |
| 77 | Cross-vessel calibration priors | Hierarchical priors for drift rates, cleaning effects and heating by sensor model and installation, learned from R2R and SAMOS archives | PROPOSED | later | EUG (drift report) |

## From the signals-of-opportunity report (Deep Research #2, 2026-11-18)

Source T-SIG: Eugene's report "High-Value Signals of Opportunity in Routine
Research-Vessel Data". Scores are the report's own, subjective: N novelty,
S science value, F real-time feasibility on modest Linux, 1 to 5. Tier R =
reproducible from R2R archive streams (nav, MET, TSG, ADCP, sonar); tier V =
needs on-vessel telemetry (machinery, DP, modem, hydrophone, raw GNSS) that
R2R normally lacks. **Every citation in the report is a lead to verify, not a
fact.** Rule from the report: a contaminant is an observation; output a
probability and an explanation, never delete data.

| # | Idea | One line | N/S/F, tier | Status | Phase | Source |
|---|---|---|---|---|---|---|
| 78 | Ship-coupling discovery engine | Cross-stream lagged dependency atlas with effective sample size, block bootstrap, BH/BY false-discovery control per family, cross-cruise replication and a ship-coordinate invariance negative control; finds sensors that "measure the ship"; live transform applies the frozen atlas as a contamination score with explanation. Report rank 1. Brief `briefs/deepsignal-ship-coupling.md` | 5/5/5, R | DESIGNED | N | T-SIG |
| 79 | Dependency-graph fault detector | Learn normal relationships between sensors on healthy data per regime; flag a sensor when its relationships break even though its values look plausible. Report rank 3. Brief `briefs/deepsignal-dependency-graph.md` | 5/5/5, R | DESIGNED | N | T-SIG |
| 80 | Directional wave spectrum from motion | Hs, period and direction from IMU/MRU motion through response-amplitude operators (RAOs). Report rank 2 | 3/5/5, R if MRU logged | PROPOSED | N | T-SIG |
| 81 | Self-calibrating ship wave buoy | Learn slowly varying RAO corrections across cruises against buoys or wave radar, hold out whole cruises | 4/5/4, R | PROPOSED | N | T-SIG |
| 82 | Current from SOG minus STW | GNSS velocity minus speed-log velocity gives near-surface current, checked against top-bin ADCP; later infer STW from propulsion when the log drifts | 3/5/5 R; 4/5/4 V | PROPOSED | N | T-SIG |
| 83 | GNSS precipitable water vapor | Kinematic PPP wet delay plus pressure and temperature gives PWV over the ocean; check against radiosondes. Needs raw GNSS | 2/5/3, R only with RINEX | PROPOSED | N | T-SIG |
| 84 | GNSS reflectometry for sea ice | Reflected-signal power and interference patterns map ice concentration and edges on polar cruises | 3/5/3, R with raw GNSS | PROPOSED | N | T-SIG |
| 85 | Ionosphere TEC and scintillation | Dual-frequency GNSS on the ship as a moving ionosphere probe; ship-fixed azimuth dependence as negative control | 3/4/3, R with raw GNSS | PROPOSED | N | T-SIG |
| 86 | GNSS interference sentinel | Common-mode C/N0 drops, PPP residuals and GNSS vs INS/DVL disagreement, cross-checked with nearby AIS ships, give a GNSS integrity score for the bridge. Report rank 6 | 3/5/5, R plus AIS | PROPOSED | N | T-SIG |
| 87 | Satellite-link rain gauge | VSAT or LEO modem signal loss beyond a dry-link baseline becomes along-track rain rate; also explains link outages. Report rank 10, paper candidate | 5/4/5, V | PROPOSED | N | T-SIG |
| 88 | Joint environmental inversion | One vessel model in which GNSS, DVL, IMU, apparent wind and propulsion all observe latent current, wind and waves; prove identifiability on synthetic data first | not scored, R/V | PROPOSED | N | T-SIG |
| 89 | Scattering-layer and migration atlas | Detect layers in ADCP or echosounder backscatter and track dawn and dusk vertical migration; random solar phase as control | 2/5/5, R | PROPOSED | N | T-SIG |
| 90 | Acoustic mixed-layer depth | Echosounder interfaces plus ADCP shear give continuous MLD, scored only at independent CTD casts | 2/5/5, R | PROPOSED | N | T-SIG |
| 91 | Gas-seep discovery | Vertically coherent bubble flares in multibeam or split-beam water column, georeferenced and clustered; blind test on known seeps | 3/5/3, R | PROPOSED | N | T-SIG |
| 92 | Echosounder noise floor as machinery monitor | Track sonar background noise against speed, heading, thruster and RPM as a cavitation and drivetrain health signature. Report rank 4, paper candidate | 5/4/5, R discovery, V proof | PROPOSED | N | T-SIG |
| 93 | Rain and wind from underwater sound | Five-minute noise spectra from a hydrophone or passive sonar mode; separate stopped, DP and underway states | 3/4/3, V | PROPOSED | N | T-SIG |
| 94 | Incidental marine-mammal detection | Only with a real passive hydrophone; active sonar disturbs animals so is context only | 2/4/2 active, 3/5/4 passive, V | PROPOSED | later | T-SIG |
| 95 | Live air-sea bulk fluxes | COARE-class latent, sensible and momentum flux from 1-min MET and TSG, validated by recreating SAMOS fluxes; value is live QC and wind-bias correction | 1/5/5, R | PROPOSED | 2 | T-SIG |
| 96 | Mixing-state product | Acoustic MLD plus buoyancy flux, wind stress and ADCP shear say when the mixed layer deepens or restratifies | 4/5/4, R | PROPOSED | N | T-SIG |
| 97 | Submesoscale front detector | Sharp T, S and fluorescence gradients confirmed by ADCP shear; separates real fronts from intake lag artifacts; event catalog over decades. Feeds #55 and #54 trap logic. Report rank 7 | 3/5/5, R | PROPOSED | N | T-SIG |
| 98 | Vessel-performance digital twin | Expected SOG, STW, power and motion per operating regime; residual is the anomaly; proxy version on R2R | 3/4/5, R proxy, V full | PROPOSED | N | T-SIG |
| 99 | Environment-conditioned machinery health | Machinery signatures modeled against sea state, current and load, so weather is not mistaken for wear (extends #43) | 3/4/4, V | PROPOSED | N | T-SIG |
| 100 | Fuel and route counterfactual | "What would this leg have burned at another speed or heading"; beware captains slowing for weather | 2/3/4, V | PROPOSED | later | T-SIG |
| 101 | Masked multirate ship encoder | Self-supervised model over 50 Hz motion, 1 Hz nav, 1 min MET; hide a stream and reconstruct it; failure to reconstruct is an anomaly. Only after physical baselines. Report rank 9 | 4/5/4, R | PROPOSED | later | T-SIG |
| 102 | Physics-conditioned representations | Train embeddings to ignore heading for the same sea state, so heading artifacts stand out; pairs from real reciprocal tracks | 5/5/3, R | PROPOSED | later | T-SIG |
| 103 | Cross-vessel sensor ontology | Map each ship's field names to semantic roles (attitude.roll, seawater.temperature.intake) so models transfer between ships; feeds #29 and #45 | 5/5/3, R | PROPOSED | later | T-SIG |


## From the parity scorecard (2026-11-18, numbered #104 to #124 by the build lead)

Unnumbered drafts from `docs/TARGET-PARITY.md` section 7. Each closes a
CORIOLIX or MetAcq row that no numbered idea covers. Numbers assigned 2026-11-18 (draft id in the Idea column of `docs/TARGET-PARITY.md` section 7: P-ERDDAP=#104, P-REST=#105, P-BEST=#106, P-MAP=#107, P-ROUTE=#108, P-CAST=#109, P-FLOW=#110, P-SAMOS=#111, P-METLIB=#112, P-GEOM=#113, P-WIZARD=#114, P-ROLES=#115, P-RELEASE=#116, P-VOCAB=#117, P-DOCS=#118, P-HOST=#119, P-CRUISE=#120, P-DEVPACK=#121, P-CORESMALL=#122, P-SNAP=#123, P-INSTALL=#124). Source T-PARITY (the parity thread). Value
is techs/science/shore, 1 to 5 each, from the scorecard.

| # | Idea | One line | Value | Status | Phase | Source |
|---|---|---|---|---|---|---|
| 104 | ERDDAP generator | Build ERDDAP `datasets.xml` from the registry and database so ERDDAP serves subsets, every file format and OGC; matches CORIOLIX's whole download stack cheaply | 2/5/5 | PROPOSED | 3 | T-PARITY |
| 105 | Read-only REST data API | Data and metadata over plain REST for MATLAB, R and scripts, reading the same tables as the MCP gateway (#64) | 2/4/5 | PROPOSED | 3 | T-PARITY |
| 106 | Best-source selector (core fix) | Primary sensor per role by model and location, automatic failover (MetAcq ONEGPS2FILE), and ancillary source assignment for derived values | 4/4/3 | PROPOSED | 2 | T-PARITY |
| 107 | Console map | Offline map: track, clickable points, underway data colored on track, events, cached OSM, GMRT and NOAA ENC basemaps, SST and Chl layers; console module 5 | 3/5/5 | PROPOSED | 3 | T-PARITY |
| 108 | Routes and waypoints | Draw a route, distance, ETA at speed, time to go, bearing, off-course warning (MetAcq CHK WPT) | 3/4/3 | PROPOSED | 3 | T-PARITY |
| 109 | Winch and CTD cast view | Wire out, speed, tension with safe-working-load bands, CTD depth and altimeter on one night-safe page; CTD package config | 5/4/2 | PROPOSED | 3 | T-PARITY |
| 110 | Flowthrough state tagging | Valve schedule tags every underway value with what was flowing (seawater, filtered, calibration, off); QC and #55 use it to avoid false flags | 4/5/3 | PROPOSED | 2 | T-PARITY |
| 111 | SAMOS and met report writers | SAMOS daily file plus NOAA hourly ship weather, OPSUM, SHIPTRACK and PCO2 formats, byte-checked against real samples | 3/4/4 | PROPOSED | 2 | T-PARITY |
| 112 | Met and seawater formula library (core fix) | Named functions for dew point, wet bulb, sea-level pressure, PSS-78 and TEOS-10, sigma, sound speed, usable from `ComputedFieldsTransform` | 3/4/3 | PROPOSED | 1 | T-PARITY |
| 113 | Vessel geometry and lever arms | Sensor positions, survey monuments and heights in the registry; small core transform corrects positions for antenna lever arm | 2/3/2 | PROPOSED | 2 | T-PARITY |
| 114 | Sensor onboarding wizard | Identify stream, pick device, map CF names and limits, attach calibration, preview the config diff, deploy with one button; no YAML typed (extends #29) | 5/2/3 | PROPOSED | 3 | T-PARITY |
| 115 | Roles and accounts | Public, science, tech and admin roles; ship and shore share accounts | 3/3/4 | PROPOSED | 3 | T-PARITY |
| 116 | Data release policy | Privacy level, restricted fields, EEZ hold-back driven by core `GeofenceTransform`, retention durations | 3/4/4 | PROPOSED | 3 | T-PARITY |
| 117 | Standard vocabularies | CF names, SeaVoX L22, L35, EL1, EL2, R2R device types, ICES ship codes, UN/LOCODE in the registry and event log (pairs with #103) | 2/4/4 | PROPOSED | 3 | T-PARITY |
| 118 | Instrument document store | Manuals and calibration certificates attached to instruments in #52 | 4/2/3 | PROPOSED | 3 | T-PARITY |
| 119 | Host health | Disk, CPU, RAM, NTP offset and process restarts on the health board | 4/1/4 | PROPOSED | 3 | T-PARITY |
| 120 | Cruise metadata | Dates, ports and participants page, optional UNOLS schedule, MFP and MOMS import | 2/3/4 | PROPOSED | 3 | T-PARITY |
| 121 | UNOLS met device pack (core fix) | Device definitions for the MetSpecs list: RM Young 05103 and 85106, Vaisala HMP155 and PTB, Eppley PSP and PIR, SBE45, SBE43, QSR, LCI90 | 4/2/1 | PROPOSED | 1 | T-PARITY |
| 122 | Small core fixes | RS485 round-robin polling with per-device timeout, ADAM ASCII reader, header on each new log file, "emulated" flag from simulators | 3/2/1 | PROPOSED | 1 | T-PARITY |
| 123 | Low-bandwidth shore snapshot | Static image plus compact JSON every N seconds for slow links (MetAcq 10 s PNGs) | 2/3/5 | PROPOSED | 3 | T-PARITY |
| 124 | Zero-prompt installer plus install clock | `--defaults` install to live data in 10 minutes and 3 actions; CI measures it on clean runners (`briefs/install-clock.md`) | 4/2/3 | PROPOSED | 0 | T-PARITY |

## Config assist and automation (2026-11-18, parity thread; numbers 125-129 taken from the build lead's next free)

Eugene asked that "all the auto stuff" that helps people configure OpenRVDAS be covered, across every
OpenRVDAS input and output, not just serial. Coverage table: `docs/TARGET-PARITY.md` section 9.

| # | Idea | One line | Value | Status | Phase | Source |
|---|---|---|---|---|---|---|
| 125 | Stream auto-discovery | Read-only scan of local serial ports (baud detection), UDP ports, MQTT topics, Redis channels, cache fields and growing files; captures feed the wizard (#114). No LAN scanning. Brief `briefs/p2/125-stream-discovery.md` | 5/2/3 | DESIGNED | 2 | T-PARITY, EUG |
| 126 | Config generator from the instrument inventory | One acquisition file (plus #52 history) generates the whole cruise definition with modes, byte-stable, with a diff against what runs now (CORIOLIX does this from its sensor database). Brief `briefs/p2/126-config-from-inventory.md` | 5/2/3 | DESIGNED | 2 | T-PARITY |
| 127 | Cruise config linter | Ship-sense checks beyond schema validation: shared ports, loggers missing from modes, nothing feeding the cache, no logfile in log modes. Brief `briefs/p2/127-config-lint.md` | 5/1/2 | DESIGNED | 2 | T-PARITY |
| 128 | Component catalog | Introspect every reader, writer and transform into JSON Schema forms with plain labels, availability of optional dependencies and kwarg checks, so nothing in OpenRVDAS needs hand-written YAML. Brief `briefs/p2/128-component-catalog.md` | 5/2/3 | DESIGNED | 2 | T-PARITY, EUG |
| 129 | Derived-product suggester | When the fields for true wind, vector averages, salinity, dew point or QC ranges are present, propose the transform (#106, #112, #4, #8) with a preview, for a tech to accept | 4/4/2 | PROPOSED | 3 | T-PARITY |
| 130 | Instrument init profiles | Per-instrument, reviewed command profiles sent over the wire: startup and setup (mode, rate, units), optional instrument clock set, reply checks with timeouts and retries, re-init after silence or reconnect, and an append-only log of every byte sent and every reply. Only commands listed in a profile are ever sent; no probing. Extends core `start_cmd`, which sends once at open, never checks a reply and is not resent after a power cycle. Wizard (#114) and device pack (#121) supply profiles. Brief `briefs/p2/130-instrument-init.md`. Eugene 2026-11-18: "sensor initiation stuff over the wire. We need to do that too." | 5/3/1 | DESIGNED | 2 | Eugene, T-PARITY M44 |

## OceanDataTools ecosystem and compression (2026-11-18, parity thread; numbers 131-136)

Eugene: compression "industry standard", integrate with OpenVDM, "maybe even sealog and grafana ... let's do
something great." Design and source evidence: `docs/ECOSYSTEM.md`; scorecard rows E1-E10.

| # | Idea | One line | Value | Status | Phase | Source |
|---|---|---|---|---|---|---|
| 131 | OpenVDM bridge | DeepSignal products and quality flags written into the OpenVDM cruise package as a collection system, plus an OpenVDM Data Dashboard plugin that turns them into `qualityTests` and `stats`; File Naming Guide friendly names. Brief `briefs/p2/131-openvdm-bridge.md` | 4/4/4 | DESIGNED | 2 | Eugene, E2 |
| 132 | Cruise context | One read-only source of the current cruise and lowering (OpenVDM `api/warehouse/getCruiseConfig`, Sealog cruises, or the OpenRVDAS cruise definition) for every DeepSignal module and report. Brief `briefs/p2/132-cruise-context.md` | 4/3/3 | DESIGNED | 2 | E3 |
| 133 | Sealog bridge | Alerts, QC changes, flow state (#110) and init results (#130) become Sealog events through core `SealogWriter`, and an aux-data inserter attaches the quality state of the relevant sensors to every new Sealog event. Brief `briefs/p2/133-sealog-bridge.md` | 4/5/3 | DESIGNED | 2 | Eugene, E4, E5 |
| 134 | Grafana quality pack | QC flags, freshness and health into InfluxDB as fields and tags; Grafana dashboards generated from the cruise definition with the ODT compass and attitude panels, flag colors and alert rules. Brief `briefs/p2/134-grafana-quality.md` | 4/3/4 | DESIGNED | 2 | Eugene, E6 |
| 135 | Archive and compression | Closed raw logs compressed losslessly (zstd when the `zstd` tool exists, else xz), with sha256 manifest, round-trip verify, originals kept by default; prioritized shore bundles for OpenVDM ship-to-shore. NetCDF4/CF export comes from ERDDAP (#104); offline NetCDF and Parquet are phase 2b. Brief `briefs/p2/135-archive-compress.md` | 3/4/5 | DESIGNED | 2 | Eugene, E7-E9 |
| 136 | QA tool adapters | Surface verdicts of ODT nav-qa-processing, sbe-qa-processing and winch-data-processing (run as OpenVDM post hooks) in the console and Sealog; #109 cast view should read winch wire logs from it rather than re-derive RVSS rules | 3/4/3 | PROPOSED | backlog (tools are "under heavy development") | E10 |

## EEZ mode (2026-11-18, parity thread; number 137)

| # | Idea | One line | Value | Status | Phase | Source |
|---|---|---|---|---|---|---|
| 137 | EEZ mode made easy | Position checked against offline Marine Regions EEZ polygons (pure Python, no geopandas), pre-alerts at distance and ETA, per-instrument log, quarantine or stop driven by the cruise clearance record, fail-safe on position loss, one-tap override with reason and expiry, append-only audit with a cruise-report table, console banner and Sealog events. Feeds `eez_inside` to #116. Brief `briefs/p2/137-eez-mode.md`. Eugene 2026-11-18: "an EEZ mode, which OpenRVDAS kind of already has just not that easy" | 5/4/4 | DESIGNED | 2 | Eugene, C27, C43 |

## Sonars, ship systems and instrument configuration (2026-11-18, ship-systems thread; numbers 138-156)

Eugene: interface with "other sonars and systems ... passive through reading their data, or actively", and
"help configure instruments, perhaps even dynamically ... even if it means ssh'ing in". Design, ranked table,
security and risk tables: `docs/SHIP-SYSTEMS.md`. Decision D-SHIP1: passive first; sonar, bridge, DP, motion
control, engine and winch settings are never changed by DeepSignal, automatically or on approval.

| # | Idea | One line | Value | Status | Phase | Source |
|---|---|---|---|---|---|---|
| 138 | IEC 61162-450 bridge reader | Transform for 450 multicast datagrams from core `UDPReader`: strip `UdPbC` header, verify tag block, keep source id and bridge time as fields, drop non-sentence datagrams; receive only. Brief `briefs/p2/138-iec450-bridge.md` | 4/3/2 | DESIGNED | 2 | Eugene, T-SHIP |
| 139 | Kongsberg datagram tap | Read-only parser for KMALL (SIS 5) and `.all` (SIS 4) datagrams arriving as raw UDP bytes: per-type rates, PU clock vs host, nadir depth, swath width, valid-beam fraction, SV at transducer as applied, runtime-parameter hash. Summaries only, no bathymetry. Brief `briefs/p2/139-kongsberg-tap.md` | 5/5/3 | DESIGNED | 2 | Eugene, T-SHIP |
| 140 | Sound velocity consistency monitor | Probe SV vs TSG-derived SV vs sonar-applied SV vs last cast surface SV; persistent mismatch alarm with a plain explanation. Brief `briefs/p2/140-sv-consistency.md` | 5/5/3 | DESIGNED | 2 | Eugene, T-SHIP |
| 141 | Depth consensus | Multibeam nadir vs single-beam (after transducer depth and draft) vs optional grid; disagreement and bottom-lock-loss flags. Brief `briefs/p2/141-depth-consensus.md` | 5/4/3 | DESIGNED | 2 | Eugene, T-SHIP |
| 142 | Time and motion alignment monitor | Lag between the motion feed and the attitude the sonar recorded (cross-correlation), sonar and motion clock offset vs NTP, sonar position vs nav after lever arms (#113); pairs with #31 and #38 | 5/5/2 | PROPOSED | 2 | T-SHIP |
| 143 | Sonar health board | Ping rate, swath and valid-beam trends, file-growth heartbeat for `.kmall`, `.all`, `.raw`, SEG-Y, runtime-parameter changes as events (#133) | 5/3/3 | PROPOSED | 2 | T-SHIP |
| 144 | Acoustic transmit awareness | Ping-time timeline of multibeam, echosounders, ADCP and SBP; overlap and interference detection; read-only awareness of a synchronizer, never control | 3/4/1 | PROPOSED | 3 | T-SHIP |
| 145 | ADCP health and cross-checks | Listen-only: UHDAS speed log plus PD0 from a receive-only copy (layout as a data table): ensemble cadence, self-test word, heading vs gyro and GNSS with frozen-heading detection, sound speed vs TSG and probe, bottom track vs multibeam, ping overlap with multibeam and EK80 for K-Sync awareness. Brief `briefs/p2/145-adcp-health.md` | 4/5/2 | DESIGNED | 2 | Eugene, T-SHIP |
| 146 | Motion and position system status | POS MV Group messages on the data port (RMS errors, GNSS status, general status and faults, heave) and Seapath quality; never the control port | 5/4/2 | PROPOSED | 2 | T-SHIP |
| 147 | Sound-speed profile manager | Ingest CTD, XBT, SVP, MVP and CSV casts; clean, surface-fill from the probe, extend to 12000 m on climatology; track age, distance and quality; advise a new cast with reasons; export SIS `.asvp`, CSV and template formats into a folder (operator loads them; direct push needs Eugene). Brief `briefs/p2/147-sv-manager.md` | 5/5/3 | DESIGNED | 2 | Eugene, T-SHIP |
| 148 | Guarded Modbus engineering adapter | Function codes 1 to 4 only, enforced and tested; register-map catalog with units and scaling for engine, power and tanks; feeds #43, #98 to #100 | 3/1/3 | PROPOSED | 3 | T-SHIP |
| 149 | NMEA 2000 through a read-only gateway | Decode PGNs from a receive-only CAN gateway into DAS records | 2/2/1 | PROPOSED | backlog | T-SHIP |
| 150 | ECDIS route import | Read RTZ files or `RTE`/`WPL` sentences as the active route for #108 | 3/2/2 | PROPOSED | 3 | T-SHIP |
| 151 | OT network safety kit | Placement checklist (61162-460 gateway, diode, mirror port), connection register shown in the console, receive-only socket tests, config lint rule for writers aimed at OT subnets (#127) | 5/1/4 | PROPOSED | 2 | T-SHIP |
| 152 | Instrument config reader | Tier R: read config and status by #130 query commands, vendor read APIs or allowlisted SSH (#155); hashed snapshots into #52 history; diff since last cruise | 5/2/2 | PROPOSED | 3 | Eugene, T-SHIP |
| 153 | Config advisor | Tier R: explainable findings with a proposed change (rate, units, sentence set, clock drift, lever arm vs #113, cal coefficients vs #52, wrong SV source from #140); advice only | 5/3/2 | PROPOSED | 3 | Eugene, T-SHIP |
| 154 | Approved change apply with rollback | Tier A, science-sensor allowlist only: dry-run diff, backup, single-change named approval with expiry, apply through #130, verify on the live stream, auto and one-click rollback, byte log; shares the #65 approval service and MCP apply flow (D-MCP2) | 4/2/1 | PROPOSED | 3 | Eugene, T-SHIP |
| 155 | Scoped SSH access kit | Per-host keys or short-lived OpenSSH certificates, `restrict` plus `from=` plus forced-command allowlist wrapper, no root, no passwords, separate apply key, full command logging into #62 | 4/1/2 | PROPOSED | 3 | Eugene, T-SHIP |
| 156 | Link health with NOC integration | One verdict per instrument link (reachability by opt-in ping or management-port probe, freshness and rate from the cache, errors from logger stderr), reusing OpenRVDAS logger status, stderr fields and cache timestamps; read-only `/health` and `/metrics` for Uptime Kuma, Zabbix or LibreNMS to poll, and a token-guarded webhook that brings their alerts in. Not an Intermapper clone. Brief `briefs/p2/156-link-health.md` | 5/2/4 | DESIGNED | 2 | Eugene, T-SHIP |
| 157 | Serial device servers (Moxa, Pepperl+Fuchs and similar) | Vendor-neutral driver interface (Moxa, Pepperl+Fuchs, generic SNMP with RFC 1659 for Digi, Lantronix, Perle, Advantech, Brainboxes, Sena). Find units (MAC prefix, cruise config, opt-in vendor broadcast), read each port by SNMP or HTTP (settings, clients, bytes, errors), map ports to loggers, generate reader configs, flag baud and wiring mismatches into #156; port changes only through #153 with approval. Brief `briefs/p2/157-device-servers.md` | 5/2/3 | DESIGNED | 2 | Eugene, T-SHIP |
| 158 | Seismic shot and source QC | Listen-only: per-shot checks from the gun controller log (mapped with core device files, no vendor format hard-coded): gun timing, missed shots, interval and spacing, fire time vs GPS, shot position interpolated from ship nav; P1/11-subset shot file. Brief `briefs/p2/158-seismic-shot-qc.md` | 4/5/3 | DESIGNED | 2 | Eugene, T-SHIP |
| 159 | Streamer and bird QC | Bird depth, wing and heading from the streamer controller output (vendor documents needed), GeoEel and other digital streamers through SEG-D or SEG-Y file headers and traces: dead and noisy channels, depth and feather | 3/5/2 | PROPOSED | 3 | Eugene, T-SHIP |
| 160 | Protected-species and mitigation view | Read-only PSO page: gun state, ramp-up timer, shutdowns, distance to EEZ edge (#137), transmit timeline (#144); PSO events to Sealog (#133); never powers guns down | 4/4/3 | PROPOSED | 3 | Eugene, T-SHIP |
| 161 | Sound-speed fusion and inferred error | Weight casts, probe, TSG, nearby Argo floats, WOA climatology and RTOFS or HYCOM forecasts by quality, age and distance; use multibeam outer-beam depth bias as evidence of a wrong profile; prepares the climatology and model files #147 uses (ashore or when bandwidth allows) | 4/5/3 | PROPOSED | 3 | Eugene (D-FUSE1), T-SHIP |

## Operational truth layer (2026-11-18, parity thread; numbers 162-169, from docs/PAIN-POINTS-MAP.md)

Eugene approved acting on the pain-points map recommendations (2026-11-18 08:46Z).

| # | Idea | One line | Value | Status | Phase | Source |
|---|---|---|---|---|---|---|
| 162 | Stream health chain | Per-stream stages (sensor, endpoint, arriving, parsed, time, calibration, derived, store) with root cause, affected outputs, transition alerts and timeout nulls; console chain view v0 ships as MVP stretch. Briefs `briefs/p2/162-stream-health.md`, `briefs/p2/162-console-chain.md` | 5/4/4 | DESIGNED | 2 | PAIN-POINTS |
| 163 | Config provenance | Versioned cruise and device configs with semantic diffs in ship words, required notes for high-risk changes, baseline drift. Brief `briefs/p2/163-config-provenance.md` | 5/3/4 | DESIGNED | 2 | PAIN-POINTS |
| 164 | Calibration and units registry | Authoritative coefficients and units with effective dates, certificates, two-person verify, affected outputs and unit-suspicion warnings (extends #7). Brief `briefs/p2/164-cal-units-registry.md` | 5/5/3 | DESIGNED | 2 | PAIN-POINTS |
| 165 | Time health | Host chrony or timesyncd state, per-stream timestamp source and confidence, latency, backward steps, inter-stream skew. Brief `briefs/p2/165-time-health.md` | 5/5/3 | DESIGNED | 2 | PAIN-POINTS |
| 166 | Continuous archive readiness | Live expected-versus-present datasets, coverage, gaps, checksums, metadata and transfer status, so nothing is found missing at cruise end. Brief `briefs/p2/166-archive-readiness.md` | 3/4/5 | DESIGNED | 2 | PAIN-POINTS |
| 167 | Alarm-linked runbooks | Per-stream vessel runbooks (wiring, endpoint, power, spares, causes by stage, escalation) opened from alarms, with recorded fixes. Brief `briefs/p2/167-runbooks.md` | 5/2/2 | DESIGNED | 2 | PAIN-POINTS |
| 168 | Unified event timeline | One timeline of config changes, transitions, init, EEZ, overrides, fixes, Sealog events and notes; "what changed before this" query and daily digest. Brief `briefs/p2/168-event-timeline.md` | 4/5/4 | DESIGNED | 2 | PAIN-POINTS |
| 169 | Science trust view | Read-only console page: per variable freshness, QC, calibration, source, units, chain root and a plain verdict; never "looks good" without a QC flag. Brief `briefs/p2/169-console-trust.md` | 2/5/4 | DESIGNED | 2 | PAIN-POINTS |
