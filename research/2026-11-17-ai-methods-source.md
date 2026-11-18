# Simple statistics beat deep models aboard

## Recommendation

**Build a layered, mostly classical QC and drift system as separate OpenRVDAS "derived data" loggers, and treat deep learning, foundation models, causal discovery and LLM agents as optional add-ons that must beat simple baselines on your own cruise data before they ship.** The evidence is unusually one-sided. On honest benchmarks, PCA reconstruction error and nearest-neighbor distance match or beat published deep anomaly detectors ([Sarfraz et al. 2024](https://arxiv.org/html/2405.02678v3)). A NeurIPS 2024 benchmark of 40 algorithms found "simpler architectures and statistical methods often perform better than advanced neural networks" ([TSB-AD](https://thedatumorg.github.io/TSB-AD)). An ICLR 2026 paper found time-series foundation models do not meaningfully beat one-line rolling-variance detectors for anomaly detection ([ICLR 2026](https://iclr.cc/virtual/2026/poster/10010437)). Meanwhile the operational gap is real and specific: the SAMOS data center flags about **5% of 260 million research-vessel measurements** per year, gives analyst visual QC only to NOAA ships and Falkor (too) on a **10-day delay**, and its statistical step/neighbor test (SASSI) was not running in 2025 ([SAMOS 2025 report](https://samos.coaps.fsu.edu/html/docs/2025SAMOSAnnualReport_final.pdf)). Problems such as a thermometer drifting off calibration or an intake SST reading 1 to 2 C high were caught ashore, not aboard ([SAMOS 2025 report](https://samos.coaps.fsu.edu/html/docs/2025SAMOSAnnualReport_final.pdf)).

The highest-value moves, in order, are:

| Order | Do this | Why it pays |
|---|---|---|
| 1 | Add a QARTOD flag logger (ioos_qc logic, flags as new fields, raw untouched) modeled on OpenRVDAS's true-winds logger template | Puts SAMOS-class checks on the ship in real time; trivial compute; standard flags |
| 2 | Add a regime-aware alert layer (cruise mode, pump/flow state, persistence, hysteresis, operator dispositions logged to Sealog) | False alarms, not missed faults, are the dominant operational failure |
| 3 | Monitor residuals between redundant or physically linked sensors (dual TSG, intake vs hull SST, T >= Tw >= Td, true-wind recomputation) with robust statistics and CUSUM | Catches steps and slow drift that single-sensor tests cannot; QARTOD itself says real-time single-channel QC misses drift |
| 4 | Track drift against independent references (bottle salinity, CTD surface bins, Argo, ERA5 wind) with an explicit bias state and uncertainty | The only proven way to separate drift from real ocean change |
| 5 | Add a pre-fitted multivariate PCA monitor (T2 and SPE with per-variable contributions) | Best-evidenced multivariate detector, and it names the faulty sensor |
| 6 | Run change-point detection, gap filling and reprocessing post hoc on stored data; ship results as versioned, flagged products | Fits batch compute; preserves provenance |
| 7 | Use an LLM only to narrate tool-computed facts (daily QC report, alarm context, YAML drafting validated by OpenRVDAS's own loader) | Agents still fail open-ended analysis; grounded tool use is the pattern that works |

What is **proven** here: QARTOD-style rule tests, reference-based drift correction in delayed mode, deterministic virtual sensors (true wind, salinity), reanalysis matchups for wind flow distortion, and PCA-type multivariate monitoring in industrial settings. What is **speculative** for ships: every ML anomaly detector, time-series foundation models, autonomous causal discovery, ML gap filling of long gaps, and LLM agents. No published deployment of statistical or ML anomaly detection inside OpenRVDAS or any comparable shipboard stack was found ([RVTEC 2025 OpenRVDAS slides](https://www.unols.org/sites/default/files/2025-12/202511rvtec_cohn_david_openrvdas_coriolix_1.pdf)). Compute is not the constraint: at 1 Hz and 200 variables, rule tests, online learners and a pre-trained isolation forest all run in a fraction of a second per tick on one CPU core (sandbox measurement during this research, detailed below), and a full 1 Hz stream is a few tens of kbps against a 6 to 30 Mbps Starshield uplink ([HiSeasNet RVTEC 2024](https://unols.org/sites/default/files/2024-11/202410rvt_hsnrvtec.pdf)). The binding constraints are engineering ones: never mutating raw data, timestamp alignment across instruments, isolating heavy dependencies from the acquisition process, model versioning, and operator trust.

## Glossary

| Term | Plain meaning |
|---|---|
| Underway data | Continuous measurements logged while the ship operates: meteorology (wind, air temperature, humidity, pressure, radiation), surface seawater (temperature, salinity, fluorescence), navigation, ship motion, ADCP currents, and engineering/hotel channels. |
| OpenRVDAS | Open-source Python data acquisition framework for research vessels. Data flows Reader -> Transform(s) -> Writer(s), wired by YAML "logger" configs and run by a logger manager under supervisord. |
| DASRecord | OpenRVDAS's record object: a timestamp, a data_id and a dict of named fields. |
| Cached Data Server (CDS) | OpenRVDAS in-memory store of recent values per field, served over websocket; displays and derived-data loggers read from and write back to it. |
| Derived data logger | An OpenRVDAS logger that reads fields from the CDS, computes new fields (e.g., true wind) and writes them back. The natural home for QC. |
| TSG | Thermosalinograph: a flow-through sensor measuring temperature and conductivity (hence salinity) of seawater pumped from a hull intake. |
| CTD | Conductivity, temperature, depth instrument lowered on a cable; its near-surface readings are a reference for the TSG. |
| QARTOD | US IOOS manuals defining real-time QC tests (gross range, spike, rate of change, flat line, climatology, etc.) and a flag scheme: 1 pass, 2 not evaluated, 3 suspect, 4 fail, 9 missing. |
| ioos_qc | Apache-2.0 Python library implementing QARTOD tests. |
| SAMOS | Shipboard Automated Meteorological and Oceanographic System initiative at FSU: shore-side QC of 1-minute research-vessel met and TSG data, using letter flags (B range, S spike, H step, etc.). |
| R2R | Rolling Deck to Repository, the US academic fleet's data archive and QA program. |
| Calibration drift | Slow change in a sensor's offset or gain so its readings wander from truth; biofouling of a conductivity cell is a common cause. |
| Common-mode fault | A fault shared by two "redundant" sensors (same intake, pump or plumbing), so their difference hides it. |
| Robust z-score / MAD / Hampel filter | Outlier scores built on the median and median absolute deviation instead of mean and standard deviation, so spikes do not distort the baseline. |
| CUSUM / Page-Hinkley | Running sums of deviations that grow steadily when a mean shifts; classic cheap detectors for small persistent changes. |
| Change point | A time where the statistical behavior of a series (mean, variance) changes. PELT is a fast offline search for many change points; BOCPD (Bayesian online change-point detection) updates a probability of a recent change at every sample. |
| Kalman filter | A recursive estimator that tracks hidden states (e.g., a sensor bias) and their uncertainty, updating each time a new observation or reference arrives. Its "innovation" is the surprise between prediction and observation. |
| PCA T2 and SPE | Principal component analysis monitoring. T2 measures how unusual a sample is inside the normal pattern; SPE (squared prediction error, also called Q or reconstruction error) measures how far it breaks the normal correlations between sensors. Per-variable SPE contributions point to the culprit. |
| Isolation forest / half-space trees | Tree-based anomaly scorers. Isolation forest is fit in batch; half-space trees (in the river library) learn online. |
| Matrix profile | For each subsequence of a series, the distance to its nearest similar subsequence; a high value (a "discord") is an unusual shape. STUMPY computes it, including incrementally. |
| Virtual (soft) sensor | A model that estimates a quantity from other measurements, deterministically (true wind from relative wind plus navigation) or empirically (CANYON-B or ESPER estimating nutrients and carbon from temperature, salinity, oxygen and position). |
| Gap filling / imputation | Estimating missing values. MNAR (missing not at random) means the gaps happen because of the conditions being measured, for example when the seawater system is shut off in ice. |
| Causal discovery | Algorithms (Granger causality, PCMCI, CCM, DYNOTEARS) that try to infer which variables drive which from observational time series. |
| FDR | False discovery rate: the expected share of "significant" findings that are false; Benjamini-Hochberg control is the usual fix when running thousands of tests. |
| Surrogate test | A significance test that compares a statistic against shuffled or phase-randomized copies of the data that keep its autocorrelation, giving honest p-values for autocorrelated series. |
| TSFM | Time-series foundation model: a model pretrained on large collections of series that forecasts (and sometimes imputes or scores anomalies) on new series without retraining. Examples: Chronos, TimesFM, Moirai, TTM, MOMENT, Toto. |
| Zero-shot | Using a pretrained model on new data without any training on that data. |
| PA-F1, AUPRC, VUS-PR | Anomaly scoring metrics. PA-F1 (point-adjusted F1) inflates scores so much that random detectors look state of the art; AUPRC and VUS-PR are the honest alternatives. |
| LLM agent | A large language model that calls tools (code, SQL, APIs) in a loop to complete a task. |
| MCP | Model Context Protocol: a standard way to expose typed tools and data to an LLM. |
| RAG | Retrieval-augmented generation: the LLM answers using retrieved documents rather than memory alone. |
| ONNX / ONNX Runtime | A portable model file format and a lightweight inference engine that runs scikit-learn and neural models without the training framework. |
| ERA5 / OSTIA | ERA5 is ECMWF's global atmospheric reanalysis; OSTIA is a gap-free daily satellite SST analysis. Both serve as external references. |
| Foundation SST | Sea temperature below the layer affected by daytime warming; the right satellite product to compare with an intake at a few meters depth. |
| Edge / shore tiers | Edge means computation aboard the ship; shore means computation at the operator or data center. |
| Starshield | The Starlink government service now used fleet-wide on US academic research vessels. |

## Ranked opportunities

Ranking weighs value to shipboard and shore users against engineering effort, discounted by evidence. "Proven" means demonstrated operationally or in a rigorous evaluation for this kind of data; "proven components" means the statistics are textbook but no automated shipboard deployment was found; "speculative" means no shipboard evidence.

| Rank | Opportunity | Value | Effort | Maturity | Evidence status | Tier | Main beneficiaries |
|---|---|---|---|---|---|---|---|
| 1 | QARTOD rule tests as a flag-emitting derived logger, with SAMOS letter crosswalk | High | Low | Operational elsewhere (OOI, AOML, SAMOS) | Proven | Edge real time | Technicians, science party, shore |
| 2 | Regime-aware alerting: cruise mode, pump/flow gating, persistence, hysteresis, rate limits, dispositions logged | High | Low to medium | Pattern proven (NASA Telemanom, process industry) | Proven pattern, untested at sea | Edge | Technicians, bridge |
| 3 | Redundant-sensor and physics-consistency residuals (dual TSG, intake vs hull SST, dew point ordering, true-wind recomputation) with robust stats and CUSUM | High | Low to medium | Comparisons done manually today | Proven components | Edge near real time | Technicians, shore support |
| 4 | Reference-based drift tracking (bottle, CTD surface bin, Argo; Kalman random-walk bias state) | High | Medium | Operational in delayed mode (TSG-QC, AOML) | Proven offline, automation speculative | Edge plus shore | Science party, shore, archive |
| 5 | Reanalysis matchups for met sensors (ERA5 wind by relative-wind sector) | Medium to high | Medium | Published method | Proven for wind | Shore | Shore support, science party |
| 6 | Multivariate PCA T2/SPE monitor with per-variable contributions | Medium to high | Medium | Mature in industry | Proven on industrial benchmarks, not ships | Edge near real time | Technicians |
| 7 | Change-point detection: online CUSUM in real time, PELT post hoc on 1-minute means | Medium | Low | Mature libraries | Proven components | Edge batch, shore | Shore, science party |
| 8 | Deterministic virtual sensors (true wind, salinity, calibrated chlorophyll) audited and published with provenance | Medium | Low | Already in OpenRVDAS (true wind) | Proven | Edge | Everyone |
| 9 | Tiered gap filling into a separate flagged product (interpolate short gaps, virtual sensor for medium gaps, leave long gaps missing) | Medium | Low (short) to high (long) | Short gaps mature; ML imputers unvalidated on ships | Proven for short gaps, speculative for long | Shore batch | Science party, archive |
| 10 | LLM for narration and configuration: daily QC report, alarm context, YAML drafting with dry-run validation, log triage | Medium | Medium | Prototypes only (WHOI custom GPT, OceanAI) | Speculative | Shore or edge | Technicians, science party |
| 11 | Empirical virtual sensors (CANYON-B, ESPER) as coarse references for biogeochemical sensors | Medium (if BGC sensors aboard) | Medium | Operational for BGC-Argo | Proven subsurface, weak at surface seasonality | Edge or shore | Science party |
| 12 | Isolation forest / half-space trees as secondary anomaly scores | Low to medium | Low | Mature libraries | Weak evidence over simpler baselines | Edge | Technicians |
| 13 | Covariate-aware TSFM "expected value" bands (TTM, Chronos-Bolt, Chronos-2) | Low to medium | Medium to high | Models mature, ship use none | Speculative | Edge batch or shore | Technicians, shore |
| 14 | Correlation mining and causal discovery (PCMCI, FDR-controlled lagged scans) as hypothesis generators | Low for ops, medium for science | High | Research tools | Speculative on ships | Shore | Science party |
| 15 | Deep anomaly detectors (TranAD, Anomaly Transformer, GDN, USAD) | Low | High | Research | Gains vanish under honest evaluation | Not recommended | None yet |
| 16 | Open-ended LLM analysis or free text-to-SQL over the ship database | Low, risky | Medium | Research | Benchmarks show low accuracy | Avoid | None |

Two candid observations frame the ranking. First, ranks 1 to 4 deliver most of the value and are all classical; an ML team that starts at rank 12 or below will spend most of its effort on the least evidenced work. Second, the supervised exception: when a ship has a modest labeled history (past cruise flags), a small supervised classifier beat unsupervised methods by a wide margin on R/V Isabu CTD profiles (F1 0.882 vs about 0.2 for one-class SVM) ([Kang et al. 2024](https://www.mdpi.com/2077-1312/12/5/807)), so label collection (rank 2) is the precondition for any later ML.

## Deep dives per method

### Automated QC: QARTOD and SAMOS logic belong on the ship, as flags not deletions

**What it does.** QARTOD tests check each value against fixed or climatological limits and against its neighbors in time. The temperature and salinity manual defines 13 tests in three tiers: required (timing/gap, syntax, location, gross range, climatology), strongly recommended (spike, rate of change, flat line) and suggested (multivariate, attenuated signal, neighbor, TS curve, density inversion) ([QARTOD T/S manual](https://cdn.ioos.noaa.gov/media/2020/03/QARTOD_TS_Manual_Update2_200324_final.pdf)). SAMOS applies a similar rule set to 1-minute ship data with letter flags, including physical-consistency checks that matter for ships: D (fails T >= Tw >= Td), E (fails true-wind recomputation), F (unrealistic platform velocity), L (position over land), N (in port) ([SAMOS flags](https://samos.coaps.fsu.edu/html/samos_quality_flag.php)). NOAA AOML's TSG real-time QC uses 8 tests derived from GOSUD (date, location, global range, regional range, spike, gradient, constant value, climatology) ([AOML TSG QC](https://www.aoml.noaa.gov/phod/tsg/data/qc.php)).

**Evidence it works.** This is the operational baseline across US ocean observing. OOI rolled out QARTOD instrument by instrument, storing results in separate `<var>_qartod_results` and `<var>_qartod_executed` variables and stating "QARTOD only Flags data, it does not remove data" ([OOI](https://oceanobservatories.org/2022/11/ooi-launches-qartod/)). SAMOS processed 9,095,936 one-minute records from 30 vessels in 2025 with automated QC posted within minutes ([SAMOS 2025 report](https://samos.coaps.fsu.edu/html/docs/2025SAMOSAnnualReport_final.pdf)). ioos_qc implements gross range, climatology, spike, rate of change, flat line, attenuated signal, location, density inversion, time gap, syntax and flag aggregation, with Numpy, Pandas, Xarray and NetCDF streams and a CF NetCDF store ([ioos_qc docs](https://ioos.github.io/ioos_qc/)). CoTeDe (BSD-3) adds presets for GTSPP, EuroGOOS and Argo, fuzzy-logic QC and an anomaly-detection method ([CoTeDe](https://github.com/castelao/CoTeDe)).

**Maturity.** Production grade for the required and strongly recommended tests. The "suggested" tests closest to drift detection (multivariate, neighbor) have no dedicated ioos_qc functions ([ioos_qc docs](https://ioos.github.io/ioos_qc/)), so ships must build those themselves (see the drift subsection).

**Data and compute.** Thresholds per variable, ideally per region; QARTOD stresses that the manual's example values are illustrative and operators must choose and document their own ([QARTOD T/S manual](https://cdn.ioos.noaa.gov/media/2020/03/QARTOD_TS_Manual_Update2_200324_final.pdf)). OOI derived thresholds from historical data and published them in a lookup repository ([OOI](https://oceanobservatories.org/2022/11/ooi-launches-qartod/)). Compute is negligible: in a sandbox measurement made during this research (ioos-qc 3.1.1, one 2.1 GHz Xeon core, not a published benchmark), four tests recomputed over a 600-sample window took 1.6 ms per variable per tick, about 0.33 s per tick for 200 variables even with naive full-window recomputation. Incremental rolling buffers would cut that by orders of magnitude.

**Failure modes.** Fixed limits trip on benign artifacts (slightly negative night shortwave), and most SAMOS flags trace to installation, plumbing and exposure problems: flow distortion, stack heating of air temperature and humidity, air in TSG lines, a backward-installed anemometer ([SAMOS 2025 report](https://samos.coaps.fsu.edu/html/docs/2025SAMOSAnnualReport_final.pdf)). Per-vessel flag rates ranged from 2.5% to 17.8% in 2025 ([SAMOS 2025 report](https://samos.coaps.fsu.edu/html/docs/2025SAMOSAnnualReport_final.pdf)), so routing every flag to a watchstander would bury them. Climatology tests (SAMOS uses 4 standard deviations from ICOADS) misfire at fronts and plumes, which is why SAMOS keeps an "I, interesting feature" flag. QARTOD explicitly states that gradual calibration change and long-term drift generally cannot be detected by automated real-time QC ([QARTOD T/S manual](https://cdn.ioos.noaa.gov/media/2020/03/QARTOD_TS_Manual_Update2_200324_final.pdf)).

**How it plugs into OpenRVDAS.** OpenRVDAS's only built-in QC transforms are bounds checks. `QCFilterTransform` returns a warning string when values are out of bounds (useful for alerting, not machine-readable flags) and its docstring says it is due to be replaced per issue 406 ([qc_filter_transform.py](https://github.com/OceanDataTools/openrvdas/blob/master/logger/transforms/qc_filter_transform.py)). `ValueFilterTransform` deletes out-of-range fields with `del fields[bound]` ([value_filter_transform.py](https://github.com/OceanDataTools/openrvdas/blob/master/logger/transforms/value_filter_transform.py)), which violates "flag, never remove" and must never sit in a raw-logging path. The right template is the shipped true-winds logger: `CachedDataReader` subscribing to input fields, a `DerivedDataTransform` subclass, `CachedDataWriter` back to the CDS, with an `on+influx` mode adding `InfluxDBWriter` ([true_winds_logger_template.yaml](https://github.com/OceanDataTools/openrvdas/blob/master/contrib/logger_templates/true_winds_logger_template.yaml)). A new `QartodFlagTransform(DerivedDataTransform)` holds per-variable rolling deques, emits `<var>_qc_rt` (1/2/3/4/9), optional per-test fields, and a `qc_algorithm_version` field. Custom classes load from any importable package via the `module:` key, which `listen.py` resolves with `importlib.import_module` ([listen.py](https://github.com/OceanDataTools/openrvdas/blob/master/logger/listener/listen.py)). Because `ComposedWriter` runs transforms serially and assumes they are thread-safe, the transform must guard its rolling state with a `threading.Lock` ([composed_writer.py](https://github.com/OceanDataTools/openrvdas/blob/master/logger/writers/composed_writer.py)). Use ioos_qc as the reference implementation in a test suite so shipboard incremental flags are bit-identical to shore batch flags. OpenRVDAS already describes "Perform basic quality checks and raise alarms" and InfluxDB Tasks that write `qa_alerts` for Grafana as current capabilities ([RVTEC 2025 slides](https://www.unols.org/sites/default/files/2025-12/202511rvtec_cohn_david_openrvdas_coriolix_1.pdf)), so flags can feed the existing display path.

### Calibration drift detection: redundancy finds steps, only independent references find drift

**What it does.** Drift detection compares a sensor to something that should agree with it and watches the difference over time. The options, from strongest to weakest evidence, are: independent references (salinometer bottle samples, CTD surface bins, Argo near-surface values, reanalysis); redundant sensors (primary vs secondary TSG, intake vs hull-mounted SST, port vs starboard met sensors); physics-consistency relations (T >= Tw >= Td, true wind recomputed from components, salinity consistent with conductivity and temperature); and learned predictors of the sensor from other data.

**Evidence it works.** Reference-based drift correction is operational in delayed mode. The IRD/LEGOS TSG-QC software validates and adjusts TSG SST and SSS against bucket samples (usually one per day), Argo floats and co-located CTD casts, compares with WOA and ISAS climatologies, and estimates drift quantitatively ([TSG-QC wiki](https://forge.ird.fr/us191/TSG-QC/-/wikis/home)). AOML adds delayed-mode comparisons with analyses, floats, XBTs and CTDs, plus regular water samples on selected transects ([AOML TSG QC](https://www.aoml.noaa.gov/phod/tsg/data/qc.php)). The best-documented automated drift adjustment is BGC-Argo: SOCCOM software compares sensors with reanalysis and empirical estimators on over 250 floats, reaching about 3 umol/kg oxygen, 0.5 umol/kg nitrate and 0.007 pH, explicitly to replace subjective visual drift assessment ([NSF PAR record](https://par.nsf.gov/biblio/10053799-updated-methods-global-locally-interpolated-estimation-alkalinity-ph-nitrate-lir-global-alkalinity-ph-nitrate-estimates)). Physics-consistency checks are proven in SAMOS (flags D and E) ([SAMOS flags](https://samos.coaps.fsu.edu/html/samos_quality_flag.php)). Automated residual monitoring of redundant ship sensors with CUSUM or a Kalman bias state is textbook statistics, but no operational shipboard deployment was found.

**Maturity.** References: proven, manual or delayed mode. Redundant-sensor comparison: proven practice but done by analysts watching difference plots. Automated residual statistics on ships: proven components, unproven integration. ML predictors of a sensor as its own reference: experimental.

**Data and compute.** References are the bottleneck, not CPU. Salinity drift needs at least daily bottles or CTD casts, and drift of order 0.01 psu per month needs several weeks of matchups before a trend is distinguishable (inference from the notes, not a published figure). Compute is scalar filters.

**Failure modes.** Four documented traps dominate. (1) Real near-surface physics masquerades as bias: in the central tropical Pacific bucket SST minus 3 m TSG averaged -0.4 +/- 0.2 C, with daytime gradients near -0.16 C/m, and OSTIA ran about 0.2 C cooler than the daily mean 3 m temperature ([Matthews and Matthews 2013](https://os.copernicus.org/articles/9/695/2013/os-9-695-2013.pdf)). Satellite or bucket comparisons must be restricted to night and well-mixed conditions or use foundation SST. (2) Fouling looks like drift: conductivity fouling lowers salinity gradually and usually goes unnoticed until sensor swap ([QARTOD T/S manual](https://cdn.ioos.noaa.gov/media/2020/03/QARTOD_TS_Manual_Update2_200324_final.pdf)); logging cleaning events lets the step at cleaning separate fouling from electronic drift. (3) Common mode: two TSGs on one intake, pump and plumbing share warming, bubbles and fouling, so their difference is blind to those; at least one independent reference is mandatory (no quantitative source on how often this occurs was found). (4) The correction can be worse than the drift: in BGC-Argo, four reference algorithms differ by 0.003 to 0.04 pH and step-wise segment adjustments inject artificial jumps of about 0.01 pH, so smooth adjustments are preferred ([Wimart-Rousseau et al. 2024](https://bg.copernicus.org/articles/21/1191/2024/)). A fifth, from reanalysis work: ERA5 assimilates ship reports, so a ship-vs-ERA5 comparison can be circular unless the ship's own observations are excluded ([Landwehr et al. 2020](https://amt.copernicus.org/articles/13/3487/2020/)).

**How it plugs into OpenRVDAS.** Build a `PairResidualTransform(DerivedDataTransform)` that subscribes (via `CachedDataReader`) to sensor pairs, aligns them using the `max_field_age` staleness logic already in `TrueWindsTransform` ([true_winds_transform.py](https://github.com/OceanDataTools/openrvdas/blob/master/logger/transforms/true_winds_transform.py)), emits `<pair>_residual`, a rolling median and MAD of the residual, and a CUSUM or Page-Hinkley statistic, and gates on regime (pump on, flow above threshold, underway). Physics checks fit `ComputedFieldsTransform`, which evaluates equations in a restricted sandbox and is designed to be subclassed with extra functions ([computed_fields_transform.py](https://github.com/OceanDataTools/openrvdas/blob/master/logger/transforms/computed_fields_transform.py)). Reference samples (bottle salinity, CTD surface bin) enter as their own records through a reader (a `text_file` or `database` reader, or `SealogReader` for event logs) and update a Kalman random-walk bias state per sensor, whose estimate and uncertainty are published as `<var>_bias_est` and `<var>_bias_sd`. Final drift corrections are applied ashore in delayed mode as a new flag and value set, never in place.

### Anomaly and fault detection: layered detectors, simplest first

**What it does.** Scores how unusual each sample or window is, univariately (robust z-score, Hampel, flat-line run length, EWMA control chart, Kalman innovation), multivariately (PCA T2/SPE, isolation forest, half-space trees, nearest-neighbor distance), by shape (matrix profile discords), or by forecast residual (Telemanom-style LSTM, TSFMs).

**Evidence it works, and where deep models fail.** The honest-evaluation literature is decisive. Kim et al. showed point-adjusted F1 lets a random score look state of the art and an untrained model match published methods ([Kim et al. AAAI 2022](https://arxiv.org/abs/2109.05257v1)). Sarfraz et al. found a random predictor scores F1_PA 0.963 on SWaT, and with honest metrics PCA reconstruction error was the best single method: SWaT F1 0.833 vs 0.810 for GDN, WADI-127 0.501 vs 0.347, SMD 0.572 vs 0.526; they distilled deep models into linear ones that "perform on par", and found median/IQR normalization beats mean/std ([Sarfraz et al. 2024](https://arxiv.org/html/2405.02678v3)). Wu and Keogh argue much apparent progress on popular benchmarks "may be illusory" ([Wu and Keogh](https://arxiv.org/abs/2009.13807v5)). TSB-AD (1,070 series, 40 algorithms) finds simple and statistical methods often win, with neural nets helping mainly on multivariate cases ([TSB-AD](https://thedatumorg.github.io/TSB-AD)). The most operationally credible deep method, NASA's Telemanom, earned that status from its thresholding and false-positive engineering (EWMA-smoothed errors, dynamic threshold, pruning, per-channel minimum scores learned from confirmed false positives), not from its LSTM; it reached 87.5% precision and 80.0% recall on 82 spacecraft channels ([Hundman et al. 2018](https://ar5iv.arxiv.org/html/1802.04431)). Ocean evidence is thin: a Transformer-BiLSTM forecaster on one Qingdao buoy reached F1 85.8% vs about 81% for Grubbs and 3-sigma, but was not compared to QARTOD or PCA ([Song et al. 2025](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2025.1528587/full)); ML QC on mooring and Argo data reached ROC-AUC 0.94 to 0.97 with false positive rates near 20%, some of them real water-mass intrusions ([Shao et al. 2025](https://www.frontiersin.org/articles/10.3389/fmars.2025.1661373/full)). A 20% false positive rate is fine for ranking segments for review and unusable as an autonomous flagger at 1 Hz.

**Detector-to-fault mapping** (engineering judgment from the notes, not a single published study):

| Fault | Signature | Best first detector |
|---|---|---|
| Spike | One-sample jump | Hampel (rolling median/MAD), QARTOD spike test |
| Stuck / flat line | Zero variance | Run length of identical values (QARTOD flat line) |
| Slow drift | Monotonic offset | CUSUM or Page-Hinkley on residual vs redundant sensor or reference |
| Step / bias | Abrupt level shift | CUSUM, BOCPD, PCA SPE contribution, PELT post hoc |
| Noise increase | Variance change | Rolling variance ratio, BOCPD with variance model |
| Dropout | Missing records | Deterministic time-gap check per instrument |
| Clock offset | Lag between correlated channels | Cross-correlation lag tracking against GPS time |
| GPS jump | Impossible implied speed | Kinematic gate (SAMOS flag F logic) |
| Unusual shape (pump cycling) | Odd subsequence | Matrix profile left discord (STUMPY `stumpi`) |

Stuck values are common in practice: on the Qingdao buoy, stuck-value rates were 8.1% for water temperature and 4.1% for air temperature, with 8.85% of data missing ([Song et al. 2025](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2025.1528587/full)).

**Maturity.** Univariate statistics and PCA monitoring: mature. Isolation forest and half-space trees: mature libraries, weak evidence of advantage. Matrix profile: mature, `stumpi` offers an O(1)-per-update streaming mode at roughly 450+ points per second, and its left profile is never revised, which is right for live alarms ([STUMPY docs](https://stumpy.readthedocs.io/en/stable/Tutorial_Matrix_Profiles_For_Streaming_Data.html)). Deep TSAD: research only.

**Data and compute.** PCA needs a clean training period per regime (a few cruises) and is pure NumPy at scoring time. In the sandbox measurements during this research (not published benchmarks), an isolation forest with 100 trees over 200 features fit 20,000 rows in 0.16 s, scored one row in 6.1 ms with scikit-learn and 1.3 ms after export to ONNX (model about 0.8 MB); river half-space trees scored and learned one 200-feature record in 0.14 ms. Library choice matters for a long-lived open-source system: Merlion was archived in March 2026 ([Merlion](https://github.com/salesforce/Merlion)) and alibi-detect moved to the Business Source License in 2024 ([alibi-detect changelog](https://www.github.com/SeldonIO/alibi-detect/blob/master/CHANGELOG.md)); prefer NumPy/SciPy, ruptures, STUMPY, river and ioos_qc.

**Failure modes.** The dominant one is false alarms from legitimate context changes: port vs underway, on station, heavy weather, intake shut off. Others are thresholds tuned on the test set (Sarfraz et al. note most published methods do this, which is impossible operationally), training on data that already contains the fault, and timestamp jitter between instruments creating spurious multivariate anomalies (score 1-minute aggregates rather than raw 1 Hz for multivariate models).

**How it plugs into OpenRVDAS.** Univariate detectors live inside the rank-1 QC transform. PCA T2/SPE runs as a second derived logger using `CachedDataReader` with `bundle_seconds` (which bundles by system clock time, not record timestamp) ([cached_data_reader.py](https://github.com/OceanDataTools/openrvdas/blob/master/logger/readers/cached_data_reader.py)), emitting `pca_t2`, `pca_spe` and the top three contributing fields. Fitted models are versioned files loaded at start-up; scoring with ONNX Runtime keeps scikit-learn out of the acquisition environment. Alerts go out through `SealogWriter` (which records threshold events and is described as "still new") and Grafana `qa_alerts` ([RVTEC 2025 slides](https://www.unols.org/sites/default/files/2025-12/202511rvtec_cohn_david_openrvdas_coriolix_1.pdf)), with watchstander dispositions (true fault, benign, context) recorded to build labels.

### Change-point detection: online for alarms, offline for segmentation

**What it does.** Finds times where mean or variance changes: sensor swaps, cleaning, plumbing faults, front crossings. Online detectors (CUSUM, Page-Hinkley, BOCPD) give low-latency alarms; offline search (PELT, binary segmentation, kernel CPD in ruptures) segments a record after the fact, structured as cost function plus search method plus penalty ([Truong et al.](https://arxiv.org/abs/1801.00718?context=cs)).

**Evidence it works.** The methods and libraries are mature. SAMOS includes a step flag (H) and its retired SASSI statistical test covered steps and spikes ([SAMOS flags](https://samos.coaps.fsu.edu/html/samos_quality_flag.php)), which shows the need is recognized and also that statistical detectors can be retired when they do not earn their keep. No head-to-head evaluation of CUSUM vs BOCPD vs PELT on underway data was found.

**Maturity.** Proven components; shipboard tuning unproven.

**Data and compute.** In this research's sandbox, ruptures PELT took 1.5 s per variable on one hour of 1 Hz data (about 300 s for 200 variables, so not real time) but only 0.46 s per variable on 24 hours of 1-minute means. Run PELT hourly or daily on 1-minute means as a batch job; use CUSUM or river's drift detectors online.

**Failure modes.** On a moving ship most change points are real oceanography (fronts, plumes), not faults. Change points are only diagnostic on residuals (sensor minus redundant sensor or reference) or on channels with no ocean signal (engineering channels, pump current, flow rate). Penalty choice controls the false alarm rate and must be tuned on labeled cruises. Step-wise corrections built from detected change points can inject artifacts (the 0.01 pH lesson from BGC-Argo ([Wimart-Rousseau et al. 2024](https://bg.copernicus.org/articles/21/1191/2024/))).

**How it plugs into OpenRVDAS.** Online CUSUM on residuals sits in the rank-3 residual transform. PELT runs as a tier-3 job reading logfiles or InfluxDB, writing versioned change-point tables, never inside a logger.

### Autonomous correlation and causal discovery: hypothesis generator, not oracle

**What it does.** Scans many variable pairs for lagged association (correlation, mutual information, distance correlation) or attempts causal graphs (Granger, transfer entropy, PCMCI and variants, convergent cross mapping, DYNOTEARS).

**Evidence it works.** In Earth science generally, Runge et al. argue correlation analyses "often lead to incorrect conclusions" and list the exact problems of underway data: strong autocorrelation, time delays, mixed time scales, heavy-tailed noise, unobserved drivers, nonstationarity, aggregation artifacts and missingness tied to the process; they note that detecting the absence of a link is more robust than detecting its presence ([Runge et al. 2019](https://www.nature.com/articles/s41467-019-10105-3)). Tigramite (GPL-3.0) documents per-method assumptions: PCMCI needs causal stationarity and no hidden variables; LPCMCI tolerates latent confounders; RPCMCI learns regime-dependent graphs; J-PCMCI+ handles context variables; masks for missing data are supported ([Tigramite](https://github.com/jakobrunge/tigramite)). CCM requires a recoverable deterministic attractor and shared drivers produce association without interaction (sardine, anchovy and SST) ([Sugihara et al. 2012](https://www.science.ntu.edu.tw/wp-content/uploads/2012/10/causalityCCM.pdf)). MIC should not be the default: its equitability claim was rebutted, it violates the data processing inequality and ran about 600 times slower than mutual information ([Kinney and Atwal](https://arxiv.org/pdf/1301.7745)). No application of any of these to research-vessel underway data was found.

**Maturity.** Research tools, speculative for ships.

**Data and compute.** Linear PCMCI on tens of variables and thousands of steps is laptop scale; nonlinear tests (CMIknn, GPDC) are permutation or Gaussian-process based and scale much worse, so they belong ashore or overnight.

**Failure modes.** On a ship, position, diurnal cycle and operations confound almost everything: crossing a front will produce "salinity drives fluorescence". A scan of 200 fields over many lags is tens of thousands of tests on heavily autocorrelated data, so naive p-values guarantee false discoveries. Imputing before discovery injects the imputer's assumptions into the graph.

**How it plugs into OpenRVDAS, and where it pays.** Run it shore-side or as an end-of-leg batch on QC-passed data only, conditioning on ship state (speed, heading, solar elevation, position or water-mass class) and separating station from transit regimes, with surrogate p-values, FDR control and replication across legs before anything is shown. Present results as "candidate associations" with lag, effect size, number of tests run and a map of where the relationship holds. The operationally useful variant is relationship monitoring: learn stable, physically known relationships (engine load vs intake warming, pitch and roll vs ADCP error velocity, relative wind direction vs anemometer bias, fluorescence vs PAR quenching) and alert when one breaks. That is fault detection by another name and inherits the rank-3 residual machinery.

### Gap filling: interpolate short gaps, model medium ones, leave long ones missing

**What it does.** Estimates missing values, from linear or spline interpolation and Kalman smoothing to multivariate imputers (MICE, KNN, Gaussian processes) and deep models (BRITS, SAITS, CSDI).

**Evidence it works.** PyPOTS (BSD-3) packages 49 imputation-capable models plus naive baselines ([PyPOTS](https://github.com/WenjieDu/PyPOTS)), and TSI-Bench ran 34,804 experiments over 28 algorithms and 8 datasets ([TSI-Bench](https://arxiv.org/abs/2406.12747)), but no ship benchmark exists. MOMENT's own paper found its zero-shot imputation beat statistical interpolation methods except linear interpolation ([MOMENT](https://arxiv.org/html/2402.03885v3)), a reminder that linear interpolation is a strong baseline for short gaps.

**Maturity.** Short-gap interpolation and Kalman smoothing: proven. ML imputers on ship data: speculative.

**Failure modes.** Ship gaps are mostly MNAR: the seawater system is secured in port, ice or heavy seas, ADCP degrades with bubbles at speed, wind sensors fail in certain relative directions. Imputers trained on normal conditions are biased exactly where gaps occur, and benchmarks use synthetic random masks. Long gaps are spatial: a 6-hour TSG outage at 10 knots is about 110 km of unsampled ocean where a front may sit, which no temporal imputer can know.

**How it plugs into OpenRVDAS.** Keep it out of real time except for display convenience. OpenRVDAS's `InterpolationTransform` (boxcar, nearest, polar averages, and per the docs window statistics and medians since v2.7.0) ([derived data docs](https://davidpablocohn.github.io/openrvdas-docs/derived_data/)) handles resampling. Gap-filled products are built ashore or end-of-day into separate variables with a fill flag (interpolated, modeled, external reference) and uncertainty; raw fields are never overwritten.

### Virtual sensors: proven when deterministic, risky when trained on the sensor they check

**What it does.** Estimates a quantity from other measurements, either from physics (true wind, practical salinity, calibrated chlorophyll) or from empirical models (CANYON-B, ESPER, cruise-local regression).

**Evidence it works.** True wind is the canonical deterministic case, and it is fragile: Smith, Bourassa and Sharp found only 20% of vessels reported all six required inputs and documented sign, convention and averaging errors ([COAPS true wind paper](https://coaps.fsu.edu/WOCE/truewind/paper)). CANYON-B, a Bayesian neural network trained on GLODAPv2 bottles, estimates nutrients and carbonate parameters with local uncertainty and was validated on independent GO-SHIP data ([CANYON-B](https://doaj.org/article/3fecd4262e04431c98a98b65e604271f)); ESPER offers neural and locally interpolated regression variants, with its authors cautioning against using it for surface seasonality ([OA-ICC summary](https://news-oceanacidification-icc.org/2021/10/22/new-and-updated-global-empirical-seawater-property-estimation-routines/)). These estimators are already used as drift references for BGC-Argo ([NSF PAR record](https://par.nsf.gov/biblio/10053799-updated-methods-global-locally-interpolated-estimation-alkalinity-ph-nitrate-lir-global-alkalinity-ph-nitrate-estimates)). For met sensors, Landwehr et al. used ERA5 winds plus COARE drag to predict wind at anemometer height on R/V Akademik Tryoshnikov, finding relative wind speed biases of -37% to +22% by relative-wind sector and correcting true wind to about +/-5% ([Landwehr et al. 2020](https://amt.copernicus.org/articles/13/3487/2020/)). SAMOS asks technicians to report suspected wind direction biases because analysts often cannot detect them ([SAMOS 2025 report](https://samos.coaps.fsu.edu/html/docs/2025SAMOSAnnualReport_final.pdf)), which makes sector-binned reanalysis comparison a concrete shore service.

**Maturity.** Deterministic: proven. Global empirical estimators: proven subsurface, coarse at the surface. Cruise-local ML soft sensors for TSG or fluorometer drift: no peer-reviewed shipboard example found.

**Failure modes.** A virtual sensor trained on the drifting sensor learns the drift and makes it invisible; it must be trained on other cruises, other sensors or external data. Extrapolation into water masses absent from training (coastal, ice edge, plumes) inflates errors. Sensors at different intake depths are measuring different water, not drifting (Matthews and Matthews again).

**How it plugs into OpenRVDAS.** Deterministic sensors stay as `DerivedDataTransform` subclasses like `TrueWindsTransform`, or as `ComputedFieldsTransform` subclasses (its docstring sketches a `GSWComputedFieldsTransform`) ([computed_fields_transform.py](https://github.com/OceanDataTools/openrvdas/blob/master/logger/transforms/computed_fields_transform.py)). Learned estimators emit `<var>_virtual`, `<var>_virtual_unc` and `<var>_residual`, with the residual feeding the CUSUM in the drift transform. External references (ERA5, OSTIA subsets) are pre-downloaded for the planned track, refreshed daily over the satellite link, and interpolated to ship position by a transform reading a local NetCDF cache.

### Time-series foundation models: secondary signal at best, for now

**What it does.** Pretrained forecasters produce expected-value bands for new series without training; some also impute or score anomalies.

**Evidence.** The models are real, small and mostly permissively licensed: IBM TTM-R2 has 805k parameters and runs on CPU-only machines (Apache-2.0, no maintenance commitment) ([TTM-R2 card](https://huggingface.co/ibm-granite/granite-timeseries-ttm-r2)); Chronos-Bolt spans 9M to 205M parameters (Apache-2.0) ([Chronos-Bolt card](https://huggingface.co/amazon/chronos-bolt-small)); Chronos-2 (120M) adds multivariate and covariate support ([Chronos-2](https://arxiv.org/html/2510.15821v1)); TimesFM 2.5 is Apache-2.0 but TimesFM 3.0 weights are non-commercial only ([TimesFM](https://github.com/google-research/timesfm)). On fev-bench, as reported by Chronos-2's own authors, Chronos-2 led with a 47.3% skill score vs 38.9% for the much faster Chronos-Bolt, and benchmark leakage reached 28% for one competitor ([Chronos-2](https://arxiv.org/html/2510.15821v1)). Three findings cut against shipboard QC use. GIFT-Eval found foundation models lag most at second and minute frequency, where Auto_Theta and supervised deep models won ([GIFT-Eval](https://arxiv.org/pdf/2410.10393)), and underway data lives exactly there (finding is for the late-2024 model generation). The ICLR 2026 one-liner paper found TSFM anomaly detection did not meaningfully beat moving-window variance and squared differences, and anomalies are not consistently harder to forecast ([ICLR 2026](https://iclr.cc/virtual/2026/poster/10010437)). MOMENT normalizes each signal, so it cannot see vertical shifts, which is precisely what an offset or drift is ([MOMENT](https://arxiv.org/html/2402.03885v3)). Separately, repurposed text LLMs for forecasting did no better with the LLM removed ([Tan et al.](https://arxiv.org/abs/2406.16964)).

**Maturity.** Mature models, zero shipboard evidence.

**Data and compute.** TTM-class models are CPU scale; a FLOP-matched NumPy proxy (not TTM itself) ran in about 29 ms per forward pass for 200 channels on one core in this research's sandbox. With context 512, feeding 1 Hz data gives only 8.5 minutes of history; 1-minute inputs give 8.5 hours and are more meaningful.

**Failure modes.** Clamping gotchas (TimesFM 2.5 in Transformers can clamp forecasts to non-negative when inputs are non-negative ([HF docs](https://huggingface.co/docs/transformers/model_doc/timesfm2_5))), license traps, heavy dependencies (torch) in the acquisition environment, and univariate residuals that flag real ocean features.

**How it plugs into OpenRVDAS.** Only as a tier-2 consumer process outside the logger environment, using covariate-aware models (predict TSG temperature from hull SST, speed and radiation) whose residual is physically meaningful, published to the CDS as `<var>_tsfm_expected` and `<var>_tsfm_residual`. Gate any promotion on beating ETS/Theta and a rolling median plus MAD on held-out cruises. Gridded AI weather models (ECMWF AIFS, operational since May 2026 with open CC BY 4.0 weights and wave variables ([AIFS card](https://huggingface.co/ecmwf/aifs-single))) are better consumed as downloaded "model-expected" channels than run aboard, since they need global initial conditions from shore anyway.

### LLM agents: narrators over tools, not analysts

**What it does.** Natural-language interface that calls tools to fetch data, run QC, draft configs and write summaries.

**Evidence.** Realistic benchmarks are sobering: the best agent solved 34.12% of DSBench analysis tasks vs 64.06% for humans ([DSBench](https://arxiv.org/html/2409.07703v3)); enterprise text-to-SQL on Spider 2.0 was about 20% to 27% execution accuracy at release, though a later claim of about 80% conflicts and is unresolved ([Spider 2.0 summary](https://www.emergentmind.com/topics/spider-2-0-benchmark)); BLADE found agents "often limited to basic analyses" ([BLADE](https://arxiv.org/abs/2408.09667)). These are 2024 to 2025 era numbers and likely understate current models. The most relevant positive result is OceanAI: a fixed-pipeline agent whose function calls return data plus provenance (source, units, location, time range) answered 7 of 7 structured NOAA data prompts that general chatbots all failed, on a tiny 14-prompt evaluation ([OceanAI](https://arxiv.org/html/2511.01019v2)). In the fleet, WHOI presented "Shipboard Data Mate", a custom GPT for technicians (QC script generation, NetCDF, cruise reports), with no published results ([RVTEC 2025 Mishra](https://www.unols.org/sites/default/files/2025-12/202511rvtec_mishra_rajesh_ai_ml_shipboard_ops.pdf)).

**Maturity.** Speculative for ships; prototypes only.

**Failure modes.** Wrong units and time zones, mixing raw and corrected channels, confident summaries over dropouts, hallucinated sensor names, and open-ended "is this significant?" analyses.

**How it plugs into OpenRVDAS.** A narrow MCP tool set over the CDS and database (`list_channels`, `get_series(channel, t0, t1, qc)`, `get_flags`, `validate_config(yaml)`), each returning provenance (logger, units, UTC window, flag version, code version) and logged. Concrete uses, ranked by value-to-risk: end-of-day QC narrative from tool-computed counts and residuals; alarm context ("TSG flow dropped 30 s before the temperature spike"); OpenRVDAS YAML drafting validated by loading through `listen.py`'s own config parsing in a dry run; log triage of serial timeouts and NMEA checksum failures. All numbers come from tools, all outputs touching cruise reports or archives get human sign-off, and no free text-to-SQL.

### Edge deployment: compute is cheap, bandwidth is ample, isolation and resilience are the job

**What it does.** Decides which computation runs aboard versus ashore.

**Evidence.** OpenRVDAS runs on Python 3.11+ on Linux down to Raspberry Pi OS under supervisord ([INSTALL.md](https://github.com/OceanDataTools/openrvdas/blob/master/INSTALL.md)). The academic fleet moved to Starshield between May 2023 and August 2024 with typical 100 to 250 Mbps down and 6 to 30 Mbps up on 5 TB per month plans, versus about 2 Mbps from the retired Fleet Xpress, with Iridium Certus (100 to 700 kbps) kept as the out-of-band path ([HiSeasNet 2024](https://unols.org/sites/default/files/2024-11/202410rvt_hsnrvtec.pdf); [HiSeasNet 2025](https://www.unols.org/sites/default/files/2025-12/202511rvtec_lockwood_thomas_hiseasnet_update.pdf)). By simple arithmetic, 200 variables at 1 Hz and about 16 bytes each is about 26 kbps, under 0.5% of a 6 Mbps uplink. Comparable stacks offer nothing beyond range and delta checks: NOAA SCS does "delta and range checks" ([SCS overview](https://scsshore.noaa.gov/robohelp/Introduction/Overview.htm)), Scripps MetAcq has range limits and sensor-status indicators ([MetAcq manual](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf)), and CORIOLIX lists flagging and ship-to-shore replication without naming tests ([CORIOLIX RVTEC 2022](https://www.unols.org/sites/default/files/202211rvt_apXXIV.pdf)). NOAA's ship data assembly project was reported paused while NOAA implements CORIOLIX as the SCS successor ([ESSIC](https://essic.umd.edu/?p=27908)).

**Implication.** The edge/shore split should follow latency-to-action and outage resilience, not bandwidth. Package algorithms as a plain Python library operating on (timestamp, field, value) streams, with thin OpenRVDAS adapters, so the same code runs in OpenRVDAS, CORIOLIX and shore pipelines.

## Architecture for OpenRVDAS

The design principle is that raw acquisition never depends on QC code. Every analytic tier reads from the CDS or stored data and writes new, separately named fields.

```
 SHIP (edge)
 ┌──────────────────────────────────────────────────────────────────────────┐
 │ Tier 0  Raw loggers (unchanged)                                          │
 │   SerialReader/UDPReader -> parse transforms -> LogfileWriter,           │
 │                                                 CachedDataWriter         │
 │                         │                                                │
 │                         v                                                │
 │                Cached Data Server (websocket, per-field history)         │
 │        ┌────────────────┼──────────────────────┬──────────────┐          │
 │        v                v                      v              v          │
 │ Tier 1 QC logger   Tier 1 residual logger  Tier 2 consumer   Displays    │
 │ CachedDataReader   CachedDataReader        (own process or   Grafana,    │
 │ -> QartodFlag      -> PairResidual          container):       qa_alerts   │
 │    Transform          Transform             PCA T2/SPE (ONNX)            │
 │ -> CachedData      -> CachedDataWriter,     ref cache interp,            │
 │    Writer,            InfluxDBWriter        TSFM bands,                  │
 │    InfluxDB/Logfile                         publish -> CDS               │
 │        └──────────── alerts ──> SealogWriter, Grafana, EmailWriter       │
 │ Tier 3 Batch on stored data: PELT change points, reprocessing,           │
 │        daily QC summary, store-and-forward queue                         │
 └──────────────────────────────────────────────────────────────────────────┘
                  │ Starshield (store-and-forward, Iridium fallback)
                  v
 SHORE
 ┌──────────────────────────────────────────────────────────────────────────┐
 │ Mirror DB / ERDDAP, SAMOS submission with letter-flag crosswalk          │
 │ Fleet comparisons, ERA5 / OSTIA matchups, drift fits vs bottles and CTD  │
 │ Model training, threshold tables, versioned ONNX pushed back to ship     │
 │ Causal and correlation scans per leg, gap-filled products                │
 │ LLM narration via MCP tools with provenance                              │
 └──────────────────────────────────────────────────────────────────────────┘
```

**Tier 0, raw acquisition.** Existing loggers stay untouched. Transforms run serially inside `ComposedWriter.write()` ([composed_writer.py](https://github.com/OceanDataTools/openrvdas/blob/master/logger/writers/composed_writer.py)), so an exception or latency spike in an inline QC transform would stall raw logging. `ValueFilterTransform` must never appear here.

**Tier 1, real-time edge QC (about 1 Hz, sub-second latency).** Separate loggers built on the true-winds template, which gives them logger-manager on/off modes and supervisord restarts for free ([true_winds_logger_template.yaml](https://github.com/OceanDataTools/openrvdas/blob/master/contrib/logger_templates/true_winds_logger_template.yaml)). A sketch, with hypothetical class and field names:

```yaml
qc_tsg->on:
  name: qc_tsg->on
  readers:
  - class: CachedDataReader
    kwargs:
      data_server: localhost:8766
      subscription:
        fields:
          TSG1Temp: {seconds: 0}
          TSG1Sal: {seconds: 0}
          TSG2Temp: {seconds: 0}
          SBE38Temp: {seconds: 0}
          TSGFlow: {seconds: 0}
  transforms:
  - class: QartodFlagTransform            # hypothetical, subclass of DerivedDataTransform
    module: local.qc.qartod_flag_transform
    kwargs:
      config_file: local/qc/tsg_qartod.yaml   # ioos_qc-style thresholds per field and regime
      gate_field: TSGFlow
      gate_min: 1.5
      version: qartod-0.3.0
  - class: PairResidualTransform          # hypothetical
    module: local.qc.pair_residual_transform
    kwargs:
      pairs: [[TSG1Temp, SBE38Temp], [TSG1Temp, TSG2Temp]]
      max_field_age: 10
      cusum_k: 0.005
      cusum_h: 0.05
  writers:
  - class: CachedDataWriter
    kwargs: {data_server: localhost:8766}
  - class: InfluxDBWriter
    kwargs: {bucket_name: qc}
```

Outputs follow the OOI and QARTOD provenance pattern: `<var>_qc_rt` (1/2/3/4/9), optional per-test fields, `<pair>_residual`, `<pair>_cusum`, and a `qc_algorithm_version` field. Real-time flags are immutable; delayed-mode flags are a new set ([QARTOD T/S manual](https://cdn.ioos.noaa.gov/media/2020/03/QARTOD_TS_Manual_Update2_200324_final.pdf)).

**Tier 2, near-real-time edge analytics (seconds to minutes).** Heavier methods run in a separate process or container with CPU limits: either an OpenRVDAS logger with `bundle_seconds` of 60 or more, or any process using the CDS websocket API (`subscribe` with back-fill, `publish` to write results back) ([cached_data_server.py](https://github.com/OceanDataTools/openrvdas/blob/master/server/cached_data_server.py)). This isolates onnxruntime or torch from the core logger environment. Note the CDS default history is 86,400 s and `max_records` 2,880 per field, so windows longer than that need the database, and the server warns that high-frequency HTTP polling delays websocket delivery.

**Tier 3, edge batch.** Hourly or daily jobs on logfiles or InfluxDB: PELT on 1-minute means, reprocessing with new algorithm versions, the daily QC summary, and CF/NetCDF export with flags as `ancillary_variables`. A store-and-forward queue (InfluxDB replication, MQTT persistent sessions or rsync of logfiles) covers outages.

**Shore tier.** Fleet-wide comparisons, ERA5 and satellite matchups (excluding periods where the ship's own reports were assimilated), drift fits against bottles and CTD casts, model and threshold training, SAMOS letter-flag crosswalk for submission, and versioned models pushed back down over the ample downlink. The 5 TB monthly downlink allowance easily covers model and reference updates.

**Who gets what.**

| User | Surface | Content |
|---|---|---|
| Technicians | Grafana panels, alerts via Sealog/email | Flag status per instrument, "intake off" style regime states, residual and CUSUM trends, PCA top contributors, daily QC summary |
| Science party | Displays, end-of-day report, archive | Flags alongside data, bias estimates with uncertainty, change-point tables, candidate associations clearly labeled as such |
| Bridge | Minimal, high-confidence alerts | Wind and navigation sensor failures affecting true wind or position, no statistical noise |
| Shore support | Mirror DB, fleet dashboards | Cross-ship comparisons, reanalysis matchups, model versions in use per ship, alert disposition statistics |

## Phased roadmap

Each phase ends only when its exit criteria are met on replayed data from real past cruises and, where stated, on a live cruise. Numeric targets below are proposed starting points, to be tuned once Phase 0 measures the baseline.

| Phase | Duration (indicative) | Scope | Exit criteria |
|---|---|---|---|
| 0. Baseline and labels | 1 to 2 months | Replay harness that feeds stored logfiles through OpenRVDAS loggers deterministically; inventory of redundant pairs and reference sources per ship; labeled event set built from past SAMOS flags, technician logs and maintenance records; metric definitions (AUPRC, range-F1, VUS-PR, never PA-F1; alerts per watch; detection lead time vs SAMOS) | Harness reproduces identical outputs on repeat runs; at least 3 past cruises replayable; labeled set with a documented count of events per fault class; baseline alert rate of existing bounds checks measured |
| 1. Edge rule QC and alerting | 2 to 3 months | `QartodFlagTransform` logger, regime gating from cruise mode and pump/flow state, persistence and hysteresis, Sealog disposition logging, SAMOS crosswalk | Shipboard flags bit-identical to ioos_qc batch on the same replayed data; added CPU below 5% of one core at the ship's full channel count; zero raw-logging gaps attributable to QC over a 30-day live trial; median actionable alerts per 4-hour watch at or below an agreed cap (start at 2); at least 80% of SAMOS range, spike and step flags on replayed cruises reproduced aboard, with lead time measured |
| 2. Drift and multivariate | 3 to 6 months | `PairResidualTransform` with CUSUM, Kalman bias state updated by bottle and CTD entries, PCA T2/SPE consumer scored via ONNX, nightly PELT | On replayed cruises with documented drift or offset events (SAMOS-reported cases where data exist), detection earlier than the shore discovery date in a majority of cases; false alarms at or below 1 per day per ship after gating; bias estimates agree with post-cruise bottle-based corrections within their stated uncertainty; PCA top-contributor correct on at least 70% of labeled single-sensor faults |
| 3. Shore services and narration | 3 to 6 months, overlapping | ERA5 sector-binned wind comparison, OSTIA night-time SST comparison, flagged gap-fill product, MCP tool set and LLM daily QC narrative, versioned model push | Every number in LLM output traceable to a logged tool call (100% on audit of 30 reports); technician survey shows the report is read and preferred to the status quo; gap-fill beats linear interpolation on MNAR-style masks (gaps placed at real outage conditions) or the product ships with linear interpolation only; ERA5 comparison reproduces known flow-distortion sectors on at least one ship |
| 4. Experimental gate | Ongoing | TSFM expected bands, isolation forest and half-space trees, causal and correlation scans, supervised classifiers on accumulated dispositions | Pre-registered: a candidate is promoted only if it beats both PCA-SPE and robust z/MAD on held-out cruises by an agreed margin on AUPRC or VUS-PR without raising alert rate; causal or correlation findings shown to scientists only after FDR control, surrogate testing and replication on a second leg; otherwise the candidate is dropped and the result documented |

## Risks, open questions and how to verify

| Risk or question | Why it matters | How to verify or mitigate |
|---|---|---|
| Alert fatigue | Telemanom's authors stress that even low false positive rates overwhelm reviewers at scale ([Hundman et al.](https://ar5iv.arxiv.org/html/1802.04431)); SAMOS flag rates of 2.5% to 17.8% per vessel would bury a watchstander | Alert on persistent residual change, not individual flags; track alerts per watch and disposition ratios from Sealog as a standing metric; per-channel thresholds raised from confirmed false positives |
| Regime changes mistaken for faults | Port, station, ice and seawater shutdowns are routine | Gate every detector on cruise mode and flow/pump state; separate PCA models per regime; measure alert rate per regime in Phase 1 |
| Common-mode drift in "redundant" sensors | Shared intake and plumbing hide shared faults | Require at least one independent reference per critical variable; no quantitative source on frequency was found, so log and count cases |
| Reference circularity and reference error | ERA5 assimilates ship reports ([Landwehr et al.](https://amt.copernicus.org/articles/13/3487/2020/)); reference algorithms disagree by more than target accuracy in BGC-Argo ([Wimart-Rousseau et al.](https://bg.copernicus.org/articles/21/1191/2024/)) | Exclude assimilated periods; report bias with uncertainty; prefer smooth corrections; compare at least two references |
| Real ocean structure flagged as drift or anomaly | Near-surface gradients of about 0.4 C ([Matthews and Matthews](https://os.copernicus.org/articles/9/695/2013/os-9-695-2013.pdf)); ML QC flags water-mass intrusions ([Shao et al.](https://www.frontiersin.org/articles/10.3389/fmars.2025.1661373/full)) | Restrict SST comparisons to night and mixed conditions; detect on residuals, not raw values; keep an "interesting feature" disposition |
| Virtual sensor learns the drift | Model trained on the drifting sensor hides it | Train on other cruises or sensors; monitor residual trend against an independent reference |
| Spurious correlations presented as science | Autocorrelation and confounding guarantee false hits in large scans ([Runge et al.](https://www.nature.com/articles/s41467-019-10105-3)) | Surrogate p-values, FDR, conditioning on ship state, cross-leg replication; label as "candidate association" |
| Benchmark-driven model choice | PA-F1 and flawed benchmarks inflate deep methods ([Kim et al.](https://arxiv.org/abs/2109.05257v1)) | Evaluate only on own cruises with AUPRC, range-F1 or VUS-PR; use TSB-AD as a harness ([TSB-AD on PyPI](https://pypi.org/project/TSB-AD/)) |
| Timestamp alignment | `TrueWindsTransform`'s own docstring flags the unsolved interpolation problem; `bundle_seconds` bundles by system clock | Align by record timestamp with `max_field_age`; add a clock-offset detector; score multivariate models on 1-minute aggregates |
| Acquisition destabilized by analytics | Serial transform execution and heavy dependencies | Separate loggers and processes, CPU limits, ONNX instead of torch at the edge, chaos test in Phase 1 |
| Licensing and maintenance | TimesFM 3.0 non-commercial, alibi-detect BSL, Merlion archived, Tigramite GPL-3.0, TTM without maintenance commitment | Keep edge dependencies to permissive, maintained libraries; run GPL tools in shore analysis environments rather than bundling them into permissively licensed add-ons (inference, check with counsel); re-verify every license card before adoption |
| Model versioning at sea | No precedent for MLOps on research vessels was found | Version string emitted with every flag; model files signed and pushed with rollback; reprocessing on shore with new versions writes a new flag set |
| Status of upstream OpenRVDAS QC work (issue 406) | A general value-matching transform may already be in progress | Read issue 406 and recent PRs; coordinate with maintainers before building in parallel |
| Fleet adoption | Unknown how many UNOLS ships run OpenRVDAS vs CORIOLIX in 2026 | Survey via RVTEC; keep core algorithms framework-agnostic |
| Real TSFM CPU latency | Only a FLOP proxy was measured here | Benchmark TTM and Chronos-Bolt on actual ship server hardware in Phase 4 |
| LLM accuracy today | Benchmark numbers are 2024 to 2025 era; Spider 2.0 figures conflict | Run a ship-specific evaluation set of 50 or more questions with known answers before any science-facing deployment |
| SAMOS automated flag false alarm rate vs visual QC | Needed to set realistic targets | Request flag-versus-visual comparisons from SAMOS for NOAA ships where both exist |

The candid open question underneath all of this is labels. No public, labeled research-vessel underway fault dataset was found, and every ML claim in this report hinges on one. Phase 1's disposition logging is therefore not a nicety: it is the mechanism that turns watchstander judgment into the training and evaluation data that would let later ML phases prove themselves or be retired.

## References

**OpenRVDAS code and documentation**
- OpenRVDAS repository: https://github.com/OceanDataTools/openrvdas
- Listener: https://github.com/OceanDataTools/openrvdas/blob/master/logger/listener/listener.py
- listen.py (YAML class and module loading): https://github.com/OceanDataTools/openrvdas/blob/master/logger/listener/listen.py
- ComposedWriter: https://github.com/OceanDataTools/openrvdas/blob/master/logger/writers/composed_writer.py
- Transform base class: https://github.com/OceanDataTools/openrvdas/blob/master/logger/transforms/transform.py
- DerivedDataTransform: https://github.com/OceanDataTools/openrvdas/blob/master/logger/transforms/derived_data_transform.py
- QCFilterTransform: https://github.com/OceanDataTools/openrvdas/blob/master/logger/transforms/qc_filter_transform.py
- ValueFilterTransform: https://github.com/OceanDataTools/openrvdas/blob/master/logger/transforms/value_filter_transform.py
- ComputedFieldsTransform: https://github.com/OceanDataTools/openrvdas/blob/master/logger/transforms/computed_fields_transform.py
- TrueWindsTransform: https://github.com/OceanDataTools/openrvdas/blob/master/logger/transforms/true_winds_transform.py
- True winds logger template: https://github.com/OceanDataTools/openrvdas/blob/master/contrib/logger_templates/true_winds_logger_template.yaml
- CachedDataServer: https://github.com/OceanDataTools/openrvdas/blob/master/server/cached_data_server.py
- CachedDataReader: https://github.com/OceanDataTools/openrvdas/blob/master/logger/readers/cached_data_reader.py
- CachedDataWriter: https://github.com/OceanDataTools/openrvdas/blob/master/logger/writers/cached_data_writer.py
- InfluxDBWriter: https://github.com/OceanDataTools/openrvdas/blob/master/logger/writers/influxdb_writer.py
- GrafanaLiveWriter: https://github.com/OceanDataTools/openrvdas/blob/master/logger/writers/grafana_live_writer.py
- INSTALL.md: https://github.com/OceanDataTools/openrvdas/blob/master/INSTALL.md
- Derived data documentation: https://davidpablocohn.github.io/openrvdas-docs/derived_data/
- Cohn, OpenRVDAS/CORIOLIX, RVTEC Nov 2025: https://www.unols.org/sites/default/files/2025-12/202511rvtec_cohn_david_openrvdas_coriolix_1.pdf
- OpenRVDAS, RVTEC 2024: https://unols.org/sites/default/files/2024-11/202410rvt_openrvdas.pdf

**QC standards, operational systems and fleet context**
- IOOS QARTOD: https://ioos.noaa.gov/project/qartod/
- QARTOD T/S Manual Update 2: https://cdn.ioos.noaa.gov/media/2020/03/QARTOD_TS_Manual_Update2_200324_final.pdf
- QARTOD Data Flags Manual v1.2: https://cdn.ioos.noaa.gov/media/2020/07/QARTOD-Data-Flags-Manual_version1.2final.pdf
- ioos_qc documentation: https://ioos.github.io/ioos_qc/
- ioos_qc repository: https://github.com/ioos/ioos_qc
- CoTeDe: https://github.com/castelao/CoTeDe
- SAMOS quality flags: https://samos.coaps.fsu.edu/html/samos_quality_flag.php
- SAMOS 2025 Annual Data Quality Report: https://samos.coaps.fsu.edu/html/docs/2025SAMOSAnnualReport_final.pdf
- R2R real-time data: https://www.rvdata.us/about/real-time-data
- NOAA AOML TSG QC: https://www.aoml.noaa.gov/phod/tsg/data/qc.php
- TSG-QC wiki (IRD/LEGOS): https://forge.ird.fr/us191/TSG-QC/-/wikis/home
- OOI launches QARTOD: https://oceanobservatories.org/2022/11/ooi-launches-qartod/
- CORIOLIX documentation: https://hmsc-cms.dri.oregonstate.edu/docs/
- CORIOLIX, RVTEC 2022: https://www.unols.org/sites/default/files/202211rvt_apXXIV.pdf
- Scripps MetAcq manual: https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf
- NOAA SCS overview: https://scsshore.noaa.gov/robohelp/Introduction/Overview.htm
- ESSIC, NOAA Ship Data Assembly Center: https://essic.umd.edu/?p=27908
- HiSeasNet, RVTEC 2024: https://unols.org/sites/default/files/2024-11/202410rvt_hsnrvtec.pdf
- HiSeasNet update, RVTEC Nov 2025: https://www.unols.org/sites/default/files/2025-12/202511rvtec_lockwood_thomas_hiseasnet_update.pdf

**Drift, references and virtual sensors**
- Matthews and Matthews 2013, Ocean Science: https://os.copernicus.org/articles/9/695/2013/os-9-695-2013.pdf
- Wimart-Rousseau et al. 2024, Biogeosciences: https://bg.copernicus.org/articles/21/1191/2024/
- Landwehr et al. 2020, AMT: https://amt.copernicus.org/articles/13/3487/2020/
- Smith, Bourassa and Sharp, true wind: https://coaps.fsu.edu/WOCE/truewind/paper
- CANYON-B (Bittig et al. 2018): https://doaj.org/article/3fecd4262e04431c98a98b65e604271f
- ESPER summary (Carter et al. 2021): https://news-oceanacidification-icc.org/2021/10/22/new-and-updated-global-empirical-seawater-property-estimation-routines/
- PyESPER: https://pypi.org/project/PyESPER/
- LIR and SOCCOM QC software (NSF PAR): https://par.nsf.gov/biblio/10053799-updated-methods-global-locally-interpolated-estimation-alkalinity-ph-nitrate-lir-global-alkalinity-ph-nitrate-estimates

**Anomaly and change-point detection**
- Sarfraz et al. 2024: https://arxiv.org/html/2405.02678v3 and https://proceedings.mlr.press/v235/sarfraz24a.html
- Kim et al. AAAI 2022: https://arxiv.org/abs/2109.05257v1
- Wu and Keogh: https://arxiv.org/abs/2009.13807v5
- TSB-AD: https://thedatumorg.github.io/TSB-AD and https://pypi.org/project/TSB-AD/
- Hundman et al. 2018, Telemanom: https://ar5iv.arxiv.org/html/1802.04431 and https://www.github.com/khundman/telemanom
- STUMPY streaming tutorial: https://stumpy.readthedocs.io/en/stable/Tutorial_Matrix_Profiles_For_Streaming_Data.html
- Truong et al., offline change point review (ruptures): https://arxiv.org/abs/1801.00718
- Song et al. 2025, Frontiers in Marine Science: https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2025.1528587/full
- Kang, Kim and Lim 2024, JMSE: https://www.mdpi.com/2077-1312/12/5/807
- Shao et al. 2025, Frontiers in Marine Science: https://www.frontiersin.org/articles/10.3389/fmars.2025.1661373/full
- Merlion (archived): https://github.com/salesforce/Merlion
- alibi-detect changelog: https://www.github.com/SeldonIO/alibi-detect/blob/master/CHANGELOG.md
- river README: https://cdn.jsdelivr.net/gh/online-ml/river@main/README.md
- sklearn-onnx supported models: https://onnx.ai/sklearn-onnx/supported.html

**Causal discovery, correlation and gap filling**
- Runge et al. 2019, Nature Communications: https://www.nature.com/articles/s41467-019-10105-3
- Tigramite: https://github.com/jakobrunge/tigramite
- Sugihara et al. 2012, CCM: https://www.science.ntu.edu.tw/wp-content/uploads/2012/10/causalityCCM.pdf
- Pamfil et al. 2020, DYNOTEARS: https://proceedings.mlr.press/v108/pamfil20a.html
- Kinney and Atwal, MIC critique: https://arxiv.org/pdf/1301.7745
- PyPOTS: https://github.com/WenjieDu/PyPOTS
- TSI-Bench: https://arxiv.org/abs/2406.12747

**Foundation models and LLM agents**
- Chronos-2: https://arxiv.org/html/2510.15821v1
- Chronos-Bolt model card: https://huggingface.co/amazon/chronos-bolt-small
- TimesFM: https://github.com/google-research/timesfm
- TimesFM 2.5 in Transformers: https://huggingface.co/docs/transformers/model_doc/timesfm2_5
- Moirai 2.0: https://arxiv.org/html/2511.11698v3
- TTM-R2 model card: https://huggingface.co/ibm-granite/granite-timeseries-ttm-r2
- TTM paper: https://arxiv.org/html/2401.03955v8
- Toto and BOOM: https://arxiv.org/html/2505.14766v2
- MOMENT: https://arxiv.org/html/2402.03885v3
- fev-bench: https://arxiv.org/abs/2509.26468v2
- GIFT-Eval: https://arxiv.org/pdf/2410.10393
- Tan et al., are LLMs useful for forecasting: https://arxiv.org/abs/2406.16964
- When Foundation Models are One-Liners, ICLR 2026: https://iclr.cc/virtual/2026/poster/10010437
- ECMWF AIFS Single: https://huggingface.co/ecmwf/aifs-single
- XiHe ocean model: https://arxiv.org/html/2402.02995v4
- DSBench: https://arxiv.org/html/2409.07703v3
- Spider 2.0 summary: https://www.emergentmind.com/topics/spider-2-0-benchmark
- BLADE: https://arxiv.org/abs/2408.09667
- OceanAI: https://arxiv.org/html/2511.01019v2
- OceanGPT: https://aclanthology.org/2024.acl-long.184
- Mishra, AI/ML for shipboard operations, RVTEC 2025: https://www.unols.org/sites/default/files/2025-12/202511rvtec_mishra_rajesh_ai_ml_shipboard_ops.pdf

**Note on unpublished measurements.** Latency figures for ioos_qc, ruptures, scikit-learn, ONNX Runtime and river, and the TTM-scale proxy, were measured during this research in a 4 vCPU cloud sandbox (ioos-qc 3.1.1, ruptures 1.1.10, scikit-learn 1.9.1, river 0.27.0, onnxruntime 1.32.0). They are order-of-magnitude indications, not published benchmarks, and should be re-measured on ship hardware.
