# Ideas backlog (master list)

Every idea in one place. ROADMAP.md ranks what is next; this file keeps
everything, so nothing raised in a thread is lost. Add a row the day an idea
comes up. Never delete a row: mark it DROPPED with a reason.


**Numbering: the build lead owns IDEAS numbers (next free: 104). Other threads do not
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

