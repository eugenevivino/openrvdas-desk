<!-- Eugene's Deep Research report, pasted in the reanalysis thread 2026-11-18. Stored verbatim. Citations are leads, not verified. Folded into D-REAN2 and the reanalysis plan section 10. -->

Detecting and Correcting Calibration Drift in Shipboard Underway Sensors
Executive synthesis
For DeepSignal, the strongest architecture is not a single drift detector. It is a layered evidence system that separates four questions that are often conflated: Is something wrong? What changed? Can the error be attributed to a particular sensor or process? Is there enough independent information to justify a correction? Operational ocean programs already embody this distinction. R2R and QARTOD emphasize automated flagging without silently altering original observations; SAMOS combines automated tests with contextual and visual review; Argo delayed-mode QC explicitly separates drift detection from the decision that a statistically recommended adjustment is physically defensible. 

The practical conclusion is that detection can often be automated much more aggressively than correction. Range, rate-of-change, flat-line, redundant-sensor residuals, changepoints, physical identities, flow diagnostics, and weak-reference residuals can run continuously. Automatic correction should require stronger conditions: either an independent reference, a physically identifiable model, or multiple independent evidence channels whose uncertainties make one calibration hypothesis substantially more probable than plausible environmental alternatives. This is especially important near fronts, plumes, rain lenses, upwelling, and ice edges, where the ocean itself can generate changes that resemble sensor failures. Argo delayed-mode practice is a useful precedent: statistical recommendations are accompanied by error estimates and expert judgment because ocean variability and instrument drift are fundamentally confounded in some regimes. 

The best general-purpose model for DeepSignal is therefore a latent-state model with explicit calibration states, augmented by changepoint hypotheses, physics-based residuals, external references treated as noisy observations rather than truth, and hard abstention logic. A minimal model is

[ y_i(t)=a_i(t)+b_i(t)x(t)+g_i(\mathbf z(t))+\epsilon_i(t), ]

where (x(t)) is the unknown environmental quantity, (a_i(t)) is an additive offset, (b_i(t)) is gain, (g_i) represents known environmental or installation effects such as temperature sensitivity, ship heating, pressure response or airflow distortion, and (\epsilon_i) is measurement noise. Slowly varying (a_i,b_i) can be random walks or integrated Ornstein-Uhlenbeck processes; abrupt calibration changes are separate changepoint variables. This structure directly encodes the main calibration failure modes instead of asking an anomaly detector to discover them implicitly. Gaussian/Kalman state-space methods are computationally cheap enough for continuous shipboard use, while smoothing and fuller Bayesian inference can be rerun post-cruise. Python implementations are readily available through pykalman, FilterPy and PyMC state-space tooling. 

The deepest design constraint is identifiability. If two instruments observe the same unknown (x(t)),

[ y_1=x+a_1,\qquad y_2=x+a_2, ]

their difference identifies (a_1-a_2), not (a_1) and (a_2) separately. If both drift together, their agreement is meaningless. Adding a third device helps only if its error process is sufficiently independent. Likewise, correcting one variable using another and then using their agreement as proof of correction is circular. DeepSignal should therefore maintain an explicit measurement-dependency graph and score the independence of each piece of evidence before allowing it to contribute to correction confidence. This principle is consistent with operational recommendations favoring genuinely redundant measurements and independent calibration standards when real-time drift correction is required. 

A useful system-level policy is:

DeepSignal state	Meaning	Automated action
GOOD	No material inconsistency detected	Publish raw and nominally calibrated value
SUSPECT	Anomaly evidence exists, attribution weak	Flag, retain raw value, widen uncertainty
FAULT_LIKELY	Multiple independent diagnostics implicate sensor/process	Flag and alert operator
CORRECTABLE	Error model is identifiable and correction uncertainty acceptable	Publish corrected value plus correction and uncertainty
AMBIGUOUS_ENVIRONMENT_OR_SENSOR	Instrument error and real feature cannot be separated	Do not correct
UNCORRECTABLE	Known malfunction invalidates measurement physics	Preserve raw, mark unusable
POSTHOC_REVIEW	Future/reference information may resolve ambiguity	Queue for smoother/reference reanalysis

That last pair is essential. A failed pump, blocked conductivity cell, contaminated optical path, severe anemometer wake, or pCO₂ equilibrator malfunction may destroy the measurement relationship rather than merely change its offset. Operational manuals explicitly warn that some pump and conductivity-cell failures cannot be reliably corrected after the fact. 

Method families and what they can actually identify
Cross-sensor redundancy and physically coupled variables
Duplicate sensors are most powerful when their failure modes differ, not merely when their model numbers differ. Two thermistors in the same warmed pipe share plumbing error. Two anemometers mounted in the same wake share flow distortion. Salinity and conductivity derived from the same conductivity cell do not constitute independent observations. Conversely, an intake SBE38 and a laboratory TSG temperature sensor provide useful information because the difference responds to pipe heating and transit effects, while bottle salinity provides a genuinely different reference for conductivity-derived salinity. Operational ship systems routinely use intake temperature sensors near the hull, TSG measurements downstream, and discrete salinity samples for this reason. 

A robust consistency architecture should preserve raw primitive channels. For a TSG, retain conductivity (C), internal temperature (T_{\rm TSG}), intake temperature (T_{\rm hull}), pump/flow state, derived practical salinity (S(C,T)), and any bottle results separately. Testing only derived salinity throws away diagnostic structure. Sea-Bird conductivity errors frequently manifest primarily as scale/span changes rather than simple offsets, while contamination generally drives conductivity and hence salinity low; electrical or geometry changes can cause more complex or abrupt behavior. 

The same principle generalizes:

Sensor system	High-value independent residuals
TSG	C/T-derived salinity vs bottle salinity; primary vs secondary C/T; intake T vs downstream T conditional on flow
Oxygen	optode vs Winkler-calibrated CTD/O₂; in-air optode calibration; duplicate optodes
Fluorescence	raw fluorescence vs discrete extracted chlorophyll only when biology/calibration relation is appropriate; reference standards; paired optical channels
Transmissometer	beam attenuation vs clean-water/reference readings; duplicate path or post-cleaning response
pCO₂	analyzer response to certified gases; seawater/air cycles; equilibrator T and P consistency
Pressure	duplicate barometers at different sites; ERA5 only as weak check
RH/T	dewpoint physical inequality; duplicated aspirated sensors; radiation and apparent-wind dependence
Wind	port/starboard or fore/aft anemometer residual versus relative-wind direction; CFD correction; vessel motion/navigation closure
Radiometry	paired/duplicate radiometers; solar geometry; pitch/roll; shading masks; nighttime zero behavior for shortwave/PAR
Heading	gyro vs dual-antenna GNSS; ADCP bottom-track closure where available
Sound speed	head-mounted SVS vs contemporaneous SVP/CTD at transducer depth

SAMOS already applies physically linked tests such as dewpoint not exceeding air temperature and validation of calculated true winds; R2R similarly distinguishes basic instrument QA from scientific QC and preserves failed observations with flags rather than deleting them. 

To prevent circular correction, DeepSignal should attach provenance to every residual. If corrected salinity (S^*) used bottle samples to estimate a conductivity gain, then (S^*-)bottle is a fit residual, not independent validation. Likewise, an ERA5-based pressure adjustment should not later cite ERA5 agreement as evidence that the correction is valid. A correction should be validated against held-out samples, another independent instrument, future post-calibration results, or physics not used in fitting.

State-space and Kalman models
For slow drift, a state-space model is the best default statistical engine because calibration parameters can be represented explicitly and updated sequentially. Linear-Gaussian versions support efficient Kalman filtering in real time and Rauch-Tung-Striebel smoothing post-cruise. Python libraries such as pykalman and FilterPy implement filters and smoothers directly, while PyMC can represent richer Bayesian state-space models with unknown parameters and posterior uncertainty. 

For example, an offset-plus-drift state could be

[ \begin{aligned} a_{t+1}&=a_t+d_t\Delta t+w_a,\ d_{t+1}&=d_t+w_d,\ y_t&=x_t+a_t+\epsilon_t. \end{aligned} ]

A gain error can be added as (b_t x_t). Cleaning or sensor-replacement events can reset the prior variance or trigger a new segment. Certified calibration gases, bottle samples, CTDs, air calibrations, dual sensors and climatological products enter as observations with their own uncertainties. Missing references are naturally handled by prediction-only Kalman steps.

The hard part is not filtering. It is choosing a model that prevents the filter from interpreting genuine environmental low-frequency structure as drift. The safest design is therefore to estimate the environmental state jointly from several sensors or an external process model, while assigning drift processes much longer characteristic timescales than plausible fronts. Even then, a slow plume crossing or a long coastal gradient can remain non-identifiable.

Argo delayed-mode salinity calibration provides the closest mature oceanographic analogue. It estimates background salinity statistically, fits float data to that background in potential-conductivity space using weighted least squares, and smooths the time-varying calibration fit across profiles. The method explicitly returns calibration uncertainty because the mapped ocean field itself is uncertain. 

Real-time: excellent for detection and probabilistic drift tracking.

Post-hoc: better still, because a smoother can use future references and determine whether an apparent drift subsequently reversed, persisted, or coincided with a cleaning or sensor change.

Changepoint methods
Offsets and sensor swaps require a different model from slow drift. Bayesian online changepoint detection, or BOCPD, recursively estimates the posterior probability of a new statistical regime and is suitable for streaming data. Adams and MacKay introduced the widely used Bayesian formulation; Fearnhead and Liu developed related online inference for multiple changepoints. 

Offline segmentation is more powerful when the whole cruise is available. The Python package ruptures implements multiple offline segmentation algorithms and cost functions. In 2026, newer Python implementations such as focus-cpt, gridcp, and skchange are appearing for fast online and structural-change detection, but they have much less oceanographic operational history than established statistical approaches. 

The correct input to a changepoint detector is usually not the raw ocean variable. Run it on diagnostics such as:

[ r(t)=y_1(t)-y_2(t), ]

or the innovation from a state-space predictor, or a calibration-gas residual. That reduces false detections from ocean fronts.

A cleaning event often produces a discontinuity followed by a new slow-drift regime; a sensor swap produces a discontinuity plus a metadata change; electronics resets can produce instantaneous steps with no corresponding environmental signatures. A model with both continuous drift states and discrete regime changes is therefore preferable to forcing either mechanism to explain everything.

Robust regression
Robust regression is one of the highest-value tools for sparse calibration samples. If bottle salinities, Winklers, certified gases or independent CTD casts are occasionally available, fit offset/gain versus time, temperature, pressure or other affecting variables using Huber, Tukey, Theil-Sen or robust spline regression rather than ordinary least squares.

This matches long-standing hydrographic practice. Scripps ODF describes polynomial calibration corrections based on differences between bottle and CTD measurements or between primary and secondary sensors as functions of time/station, pressure, temperature or conductivity. Individual cruise processing commonly uses piecewise linear TSG corrections separated by cleaning events. 

Robust regression is especially attractive because its assumptions are visible and diagnosable. It does not solve non-identifiability, but it does prevent a handful of bad reference samples from dominating a correction.

Gaussian processes
Gaussian processes, or GPs, model an unknown function together with uncertainty and are useful when drift is smooth but nonlinear. GP sensor-calibration literature shows how an environmental response and calibration drift can be modeled probabilistically and how uncertainty can guide recalibration decisions. 

For DeepSignal, GP use is most defensible in post-hoc calibration of residuals such as

[ r=f(t,T,\text{flow},\text{relative wind direction})+\epsilon, ]

rather than unconstrained reconstruction of the environmental variable itself. Sparse and inducing-point GPs can operate online, but a full GP scales poorly with the number of observations, so minute-resolution multiweek cruises require subsampling, local windows, state-space GP approximations or inducing points.

GPs become dangerous when the kernel is allowed to absorb both ocean structure and drift. A smooth GP does not know whether a 12-hour salinity trend is an instrument effect or an estuarine plume. Physics and reference structure still have to identify the calibration term.

Functional data analysis
Functional data analysis is most valuable when there is a repeating natural unit: repeated transects, daily loops, casts, station approaches, or reciprocal survey lines. Each transect can be treated as a function, and calibration anomalies appear as coherent departures from the family of functions. This is promising for repeated ferry/merchant tracks or survey vessels but much weaker for unconstrained research-vessel trajectories. Compared with state-space modeling and change detection, direct evidence for FDA-based calibration correction of heterogeneous shipboard underway sensors is limited; it should therefore be treated as a specialized post-hoc method rather than a core DeepSignal dependency.

External references: useful, weak and sometimes not independent
The safe model for climatology, satellite data and reanalysis is “noisy external observation”, never “truth.”

If (z) is an external reference, use

[ z=x+\eta_{\rm product}+\eta_{\rm represent}, ]

with

[ \sigma_{\rm ref,total}^2= \sigma_{\rm product}^2+ \sigma_{\rm represent}^2+ \sigma_{\rm matchup}^2+ \sigma_{\rm dependence}^2. ]

Then use weight

[ w=\frac{1}{\sigma_{\rm sensor}^2+\sigma_{\rm ref,total}^2}. ]

The representativeness term is usually the dominant unknown. It accounts for the fact that the ship samples a point at intake depth while an external product represents another depth, footprint, averaging interval and sometimes an entire water mass.

A practical covariance model is

[ C=\exp\left[ -\frac{\Delta x^2}{L_x^2} -\frac{\Delta y^2}{L_y^2} -\frac{\Delta t^2}{L_t^2} \right], ]

with (L_x,L_y,L_t) estimated regionally rather than hard-coded globally. Argo calibration experience strongly supports this. Earlier objective-mapping approaches used open-ocean horizontal decorrelation scales around 5° longitude and 3° latitude, roughly 300 km in the study region, and a 30-day temporal e-folding scale; operational Argo discussions have used default spatial pairs of approximately 8°/4° and 4°/2° in relatively stable open-ocean regions while explicitly warning that the subpolar North Atlantic, Arabian Sea and other variable regions need different scales. 

Those numbers must not be transplanted to surface underway data. They arose from relatively stable subsurface θ-S relationships. Surface SST, SSS, winds and atmospheric variables decorrelate much faster near fronts, rivers, rain, coastal boundaries and diurnal warming. Use such scales as an upper-bound precedent for stable water masses, not as surface calibration parameters.

World Ocean Atlas
WOA23 supplies objectively analyzed climatologies and uncertainty-related statistics for temperature, salinity and oxygen. Its objective analysis deliberately uses broad spatial influence radii: for its uncertainty calculation, the second radius is 669 km on the 1° product and 267 km on the 0.25° product; WOA also exposes standard deviations and standard errors of analysis. 

Therefore, WOA is appropriate for detecting gross implausibility and long-term regional bias, not for forcing high-resolution underway observations toward climatology. A ship crossing the Gulf Stream, an estuary, upwelling zone or rain-freshened tropical surface layer can legitimately disagree with WOA by far more than a precision sensor's calibration error.

WOA is also not guaranteed to be statistically independent of ship/Argo observations because it is built from the World Ocean Database, which contains extensive profile observations from modern observing systems. 

Argo
Nearby delayed-mode Argo profiles are among the best external salinity/temperature references if depth, time and water-mass matching are sensible. Argo delayed-mode salinity explicitly carries adjusted-error estimates; real-time salinity is less suitable because drifting conductivity cells may still be present. 

Argo's delayed-mode calibration itself demonstrates the central limitation: contemporary ship data are valuable precisely because historical climatology cannot always distinguish genuine ocean change from sensor drift. 

For underway matching, I would use a water-mass-aware gate rather than a single kilometer threshold. Near-surface Argo data within tens of kilometers and a few days can be strong evidence in homogeneous open ocean; the same separation may be unusable across a front or coastal plume. DeepSignal should estimate local gradients from the ship track and inflate matchup uncertainty as (|\nabla x|\Delta r).

OISST
NOAA OISST v2.1 is daily at 0.25° resolution and provides an analysis-error field intended to indicate confidence in the interpolation. 

It is useful for SST drift detection over multi-hour to multi-day scales, but independence is a serious issue: OISST assimilates buoy and ship SST and bias-adjusts satellite observations toward the in-situ record. A vessel whose observations enter the GTS could therefore contribute to the product being used to assess it. 

DeepSignal should label OISST evidence potentially_dependent unless the ship's data-flow provenance proves otherwise. It should also retain a separate satellite-only SST option when practical.

SMAP and SMOS
Satellite salinity provides a genuinely different sensing modality, but at coarse spatial resolution and much poorer point accuracy than a properly calibrated TSG. The RSS SMAP v6 standard mapped product is approximately 70 km resolution; published SMAP/SMOS comparisons against open-ocean in-situ data show RMS differences of roughly 0.2 practical salinity units, orders of magnitude larger than high-quality shipboard salinity precision. 

That makes satellite SSS useful for detecting large sustained TSG biases, not corrections of hundredths of a salinity unit. Coastal land contamination, radio-frequency interference, rain and sea-ice effects further reduce usefulness. SMAP validation itself uses Argo, moorings and TSG observations, although the radiometric retrieval is physically independent of an individual ship sensor. 

ERA5
ERA5 offers hourly atmospheric fields at roughly 31 km resolution and an ensemble-based uncertainty indicator available at lower resolution and 3-hourly intervals. The ensemble spread measures relative synoptic uncertainty and does not fully represent systematic model bias. 

ERA5 is useful for detecting multi-hour gross biases in pressure, temperature, humidity and wind and for identifying meteorological forcing associated with genuine ocean events. It is not an independent reference for all ship observations: ERA5 assimilates SHIP observations including surface pressure, temperature, wind and humidity. 

Thus a ship-to-ERA5 residual can be evidence, but not proof. If the ship observation was assimilated, common-mode agreement is possible.

Practical reference-distance rule
Do not encode fixed global rules such as “Argo within 100 km” or “ERA5 within 3 hours.” Instead:

[ \sigma_{\rm repr}^2 = \sigma_{\rm local}^2+ (\Delta r,|\nabla x|)^2+ (\Delta t,|\partial x/\partial t|)^2+ \sigma_{\rm vertical}^2. ]

Estimate (|\nabla x|) from ship data, satellite fields or neighboring observations. When the ship enters a front, (|\nabla x|) rises and the external reference automatically loses weight. This converts “How far away is too far?” from a brittle threshold into an uncertainty calculation.

Sensor-specific failure modes and the front-versus-drift problem
The central operational distinction is between a sensor diagnostic signature and an environmental signature. A front can change multiple physically related quantities coherently. Instrument drift more often violates relationships, appears in only one redundant path, follows maintenance events, depends on sensor temperature/flow, or evolves on an implausible calibration timescale.

Thermosalinograph, conductivity and intake temperature
TSG systems have unusually good diagnostic structure because salinity is derived from conductivity and temperature and because many ships have a separate near-intake temperature sensor. The laboratory temperature can differ from intake temperature because of shipboard heating, residence time and flow. SAMOS documentation notes that sufficiently high flow minimizes internal heating but that near-surface vertical gradients and hull flow can still produce several-tenths-of-a-degree differences under daytime stratification. 

Biofouling: typically progressive conductivity bias, often toward low conductivity/fresh salinity for contaminated electrode cells; cleaning may generate an abrupt recovery. Argo experience documents pollution-driven fresh bias and trend reversal when contamination washes off. 

Bubbles: produce abrupt conductivity/salinity noise and often occur in rough weather or inadequate debubbling systems. Real cruise reports document persistent TSG salinity noise from trapped bubbles and pump transitions. 

Pump failure/blockage: expect reduced or zero flow, delayed response, thermal disequilibrium, conductivity jumps and altered T-C phase relationships. Pump-failure guidance warns that resulting thermal-inertia errors can be uncorrectable. 

Cleaning: use the event timestamp as an explicit changepoint prior. Cruise processing has successfully fitted separate piecewise-linear salinity corrections before and after cleaning events. 

Front versus drift: a real front should usually be coherent in intake temperature, conductivity/salinity and often satellite/Argo context. A conductivity-cell drift may alter C-derived salinity without a corresponding independent intake-T change. A rain lens is harder: true surface salinity can change rapidly while intake temperature changes weakly, so satellite precipitation/radar/meteorology and duplicate conductivity measurements become important. Never “correct” a sharp salinity feature merely because climatology dislikes it.

Dissolved oxygen
Optical oxygen sensors usually exhibit gain-like drift and can also have pressure- and time-dependent behavior. Recent best-practice work on 60 GOHSNAP optodes found average irreversible drift around 1% per year and optode-specific pressure-response differences substantial enough that a generic correction can leave percent-level errors at depth. 

For underway systems, in-air calibration is particularly attractive because atmospheric oxygen provides a recurring physical reference without Winkler sampling. An underway study specifically developed periodic in-air optode calibration to correct drift and biofouling where frequent manual recalibration was impractical. 

A DeepSignal oxygen model should therefore prefer a time-varying multiplicative gain with optional offset and environmental dependence. Winkler samples, air calibrations and duplicate optodes become calibration observations.

Fluorometers and transmissometers
Fluorescence is difficult because the relationship between fluorescence and chlorophyll is itself environmentally variable. Sensor drift, quenching, physiology and community composition can all change the fluorescence-to-chlorophyll relationship. Therefore, an apparent gain change against extracted chlorophyll is not automatically an instrument gain error.

Operational optical guidance recommends pre/post calibration, reference standards, side-by-side sensor checks and explicit documentation before and after cleaning. 

USGS fluorometry guidance supports zero plus multiple calibration standards to diagnose offset, gain and nonlinear drift, with interpolation of measured calibration drift between checks when justified. 

Biofouling: progressive attenuation or fluorescence distortion, often followed by a jump after cleaning.

Bubble entrainment: spikes and erratic optical path interruptions correlated with sea state and seawater-system flow.

Front versus drift: a phytoplankton bloom or river plume can legitimately create dramatic fluorescence/transmission structure. Correction requires standard checks or independent optical/biological evidence, not climatological smoothing.

pCO₂
Underway pCO₂ systems are unusually favorable because certified gases provide direct calibration information. SOCAT requires detailed calibration metadata and ties quality categories to calibration-gas coverage, temperature accuracy and pressure accuracy. 

A strong DeepSignal model should expose separate states for analyzer zero/span, equilibrator temperature, absolute pressure, water-flow/equilibration behavior, gas-flow status and seawater-to-equilibrator lag. Certified-gas residuals identify analyzer gain/offset independently of real ocean pCO₂. The seawater measurement can then be corrected only after the analyzer state is established.

This is a case where autonomous correction can be more aggressive because the reference gases are true independent standards.

Atmospheric pressure, air temperature and humidity
Pressure drift is relatively straightforward when duplicated barometers exist. ERA5 can supply weak contextual evidence, but its possible assimilation of ship observations means it should never be the sole calibration reference. 

Air temperature is more difficult because the ship changes the measurand. Solar heating of instruments and superstructure can create warm daytime bias. Modern work has extended heat-budget methods for correcting shipboard marine-air-temperature heating biases, while older analytical models show explicit dependence on radiation and ventilation. 

Therefore, DeepSignal should not interpret all slowly varying air-temperature disagreement as calibration drift. Fit diagnostics against solar irradiance, apparent wind speed/direction and ship heading first. A bias that grows with shortwave radiation and weak ventilation is an installation/environmental effect, not necessarily sensor calibration.

Humidity should similarly be tested jointly with temperature and dewpoint; physical inconsistency such as dewpoint above air temperature is stronger evidence than disagreement with reanalysis. SAMOS already uses such relationship tests. 

Radiometers
Shortwave, longwave and PAR measurements are vulnerable to shadowing, tilt, salt deposits, sensor temperature effects and ship structures. Shipboard radiometer designs have historically included attitude sensors specifically because pitch, roll and azimuth matter to irradiance measurement. 

For shortwave/PAR, solar ephemeris gives a strong physical predictor. DeepSignal can detect:

impossible positive shortwave/PAR during astronomical night;
shading tied reproducibly to relative solar azimuth and ship heading;
gain changes using clear-sky envelopes only as weak references;
cleaning steps;
tilt-response errors using pitch/roll.
Longwave lacks the nighttime-zero constraint and needs comparison to air temperature, cloud conditions and redundant radiometers.

Anemometers and superstructure flow distortion
This family should be modeled differently from ordinary sensor drift. Flow distortion is a direction-dependent transfer function caused by the vessel geometry.

CFD studies on research vessels show that ship structures can produce substantial wind-speed biases and that the error depends strongly on relative wind direction. CFD validation studies have achieved agreement with well-exposed reference measurements on the order of a few percent outside severe wake regions. 

OpenFOAM-based modeling of the RV Celtic Explorer demonstrated practical mapping of distortion across relative wind direction and speed. 

For vessels with port/starboard anemometers, DeepSignal can infer a relative-wind-direction-dependent differential correction from long-term data, but absolute correction remains non-identifiable unless one anemometer enters a clean sector or CFD/wind-tunnel information is available. This is a prime example where two agreeing sensors can both be wrong.

Ship motion correction must also be treated separately from airflow correction. SAMOS derives Earth-relative wind from relative wind plus vessel speed, course and heading; a gyro or GNSS heading error can therefore masquerade as anemometer error. 

GNSS and gyro heading
Heading sensors have excellent cross-check opportunities. Dual-antenna GNSS heading is independent of vessel velocity, unlike course over ground, and 2026 experimental work found sub-degree RMSE for multi-meter GNSS antenna baselines relative to postprocessed reference solutions. 

Older shipboard ADCP work showed that gyro errors can be heading-dependent rather than a constant offset; comparing bottom-track ADCP vessel velocity with DGPS vessel velocity revealed corrections of several degrees and materially reduced residual velocity error. 

DeepSignal should represent heading calibration as a circular function,

[ \Delta\psi=f(\psi,t), ]

not assume a single constant bias. Fit Fourier terms or a circular spline, with explicit segmentation across gyro maintenance or replacement.

Multibeam surface sound velocity
NOAA hydrographic guidance recommends comparing the surface sound-speed sensor at the sonar head against a full profile and tracking discrepancies greater than 1 m/s; critically, it warns that dynamic water chemistry can produce false positives and recommends a static cast to distinguish sensor drift from real water change. 

This is almost exactly the DeepSignal philosophy: detect automatically, attribute conservatively, correct only when independent evidence exists.

Recent hydrographic work also emphasizes that profile sampling can be much slower than surface sound-speed sampling and that spatiotemporal water-column variability itself produces sounding error. 

A sound-speed correction should therefore include uncertainty from both the surface sensor and representativeness of the nearest SVP/CTD.

Machine learning: where it helps, where it has not earned authority
The strongest evidence for ML in ocean QC is for anomaly candidate detection, not autonomous calibration correction.

Castelão's 2021 study used anomaly detection on 13 years of hydrographic-profile data and reported at least a 50% reduction in classification error relative to the automatic QC approaches evaluated. The method is implemented in the open-source Python package CoTeDe. This is credible evidence that multivariate anomaly features can improve QC, but the dataset consisted of hydrographic profiles, not heterogeneous underway research-vessel sensor streams, and the task was bad-data classification rather than attribution of drift. 

A more directly relevant 2024 marine-stream benchmark evaluated 36 anomaly-detection algorithms on approximately 200,000 observations from three real marine sensor datasets, including data from the One Ocean Expedition. None of the tested existing methods achieved the performance level the participating marine organizations regarded as operationally adequate, motivating a concept-drift-adaptive method. 

The broader aquatic-sensor literature is similarly cautionary. In the pyhydroqc study, classical ARIMA models consistently outperformed the deep-learning models tested for anomaly detection/correction on technician-reviewed environmental sensor data, and ensembles improved performance further. 

A 2026 coastal-buoy study gives perhaps the cleanest demonstration of the front-versus-fault problem. Prediction residual magnitude alone was nearly useless for separating sensor-like anomalies from real upwelling/typhoon events, with AUC only about 0.52-0.56; physically interpretable spatial, vertical and atmospheric coherence carried much more discriminating information. 

There are new 2026 graph/transformer efforts. DriftGuard reports ROC-AUC around 0.84 on its evaluated marine datasets and earlier gradual-drift detection than an Argo QC baseline, while other 2026 work applies heterogeneous graph neural networks or self-supervised transformer representations to ocean sensor data. These are interesting research directions, but they do not yet establish that end-to-end ML correction beats physically structured statistical calibration on real shipboard underway systems, and the strongest claims remain individual-study results without broad operational replication. 

I found no convincing published benchmark through November 2026 showing physics-informed neural networks outperforming state-space, robust-regression or reference-calibration methods for correction of slow calibration drift across real research-vessel underway sensor suites. PINNs are therefore not a sensible first-line DeepSignal implementation. They may become useful for strongly mechanistic subsystems such as ship airflow or seawater-system thermal response, but only if benchmarked against simpler models.

The best ML role in DeepSignal is consequently:

Generate anomaly scores or learned residual features.
Never allow a black-box anomaly score alone to trigger calibration correction.
Feed ML scores into the same evidence graph as physics tests, redundancy and references.
Require held-out vessel/cruise validation because sensor placement and failure distributions shift substantially between ships.
Comparison table and recommended DeepSignal implementation
Method comparison
Method	Applicable sensors	Streaming / hindsight	Data required	Reported performance, where actually published	Compute	Open-source implementation	Maturity
QARTOD/SAMOS rule QC	Nearly all	Streaming	Single stream + metadata, optionally coupled variables	Operational programs use bounds, spike, gradient, flat-line, physical-consistency and climatology tests; not a calibration-accuracy estimator. 
Very low	ioos_qc 
Operational
Duplicate-sensor residuals	All duplicated sensors	Streaming + post-hoc	Synchronized independent sensors	CFD/research-ship wind studies show paired well-exposed anemometers can constrain distortion to few-percent levels in favorable sectors, but residuals identify relative rather than absolute bias. 
Very low	NumPy/SciPy	Operational principle
Physical identity/closure tests	TSG, RH/T, wind, navigation, sound speed, pCO₂	Streaming	Primitive variables and equations	Widely used operationally by SAMOS, hydrographic and carbon programs. 
Very low	gsw, ioos_qc, NumPy	Operational
Robust regression to sparse standards	TSG, O₂, pCO₂, optics, pressure	Both	Occasional independent standards	Cruise TSG workflows successfully use bottle residuals and piecewise time regressions; performance is cruise-specific. 
Low	SciPy, statsmodels, scikit-learn	Operational
Linear state-space / Kalman drift states	Almost all	Both	Continuous data + occasional reference or redundancy	Mature general estimator; no universal shipboard correction accuracy. Argo-like drift estimation supports the model concept. 
Low, roughly O(state³) per update but tiny states	pykalman, FilterPy 
High
Kalman smoother / Bayesian state-space	Almost all	Post-hoc primarily	Whole cruise + references	Better endpoint/drift inference because future observations contribute; uncertainty naturally available.	Low to moderate	PyMC, pykalman	High
Bayesian online changepoint	Steps, swaps, cleanings, pump/electronic events	Streaming	Residual/innovation stream	Foundational online Bayesian method; application accuracy depends entirely on signal/model. 
Low to moderate	bayesian_changepoint_detection; 2026 focus-cpt/gridcp 
High method maturity, medium marine maturity
Offline changepoint segmentation	Same	Post-hoc	Whole cruise	No universal calibration accuracy; excellent for piecewise regimes	Low to moderate	ruptures 
High
Objective mapping / climatological calibration	T/S especially	Post-hoc	Historical profiles / Argo	Mature Argo delayed-mode approach; uncertainty depends strongly on reference coverage and water-mass stability. 
Moderate	Argo DMQC tooling is less turnkey in Python	Operational for Argo, experimental for surface underway
Gaussian-process drift model	Most scalar sensors	Both with sparse approximation; strongest post-hoc	Residuals + covariates + sparse references	Sensor-calibration studies demonstrate probabilistic drift estimation; no broad shipboard benchmark. 
Moderate to high	PyMC GP / GPyTorch / scikit-learn	Medium
CFD flow-distortion map	Anemometers	Correction table can stream; model generated offline	Ship geometry, anemometer position, CFD	Research-ship studies report CFD/in-situ wind agreement of roughly 2-4% outside wake extremes. 
High offline, trivial online	OpenFOAM plus Python lookup	High for serious wind work
Certified-standard cycling	pCO₂, optics, some gas/sensor systems	Streaming	Standard gas/solution cycles	SOCAT explicitly bases higher-quality pCO₂ categories on traceable calibration gases and ancillary-sensor accuracy. 
Very low	System-specific	Gold standard
Weak satellite/reanalysis residual	SST, SSS, met	Both	Position/time + external grids	SMAP open-ocean RMSD vs in situ roughly 0.2 S; OISST provides analysis error; ERA5 ~31-km hourly. 
Low after data retrieval	xarray, cfgrib, netCDF4	High as context, low as sole calibration
ML anomaly detector	Most	Both	Training or baseline feature data	Castelão: ≥50% classification-error reduction on hydrographic profiles. Marine-stream benchmark: 36 algorithms failed stated industry target. 
Moderate	CoTeDe, PyOD, sklearn	Medium for detection; low for correction
Deep transformer/GNN/self-supervised	Multivariate networks	Usually offline/heavy streaming	Large labeled/unlabeled corpus	Promising 2025-26 buoy/ocean studies, but limited cross-vessel external validation. 
High	PyTorch ecosystems	Research
GUM / Monte Carlo uncertainty propagation	Every corrected product	Both	Measurement model + uncertainty distributions	Formal metrology standard, not a detector. 
Low to moderate	NumPy/SciPy/PyMC	Metrology standard

Ranked implementation priorities
First: dependency-aware residual and evidence engine.

This should be the DeepSignal foundation. Implement every sensor as nodes and transformations in a directed acyclic graph:

text
Copy
raw sensor
   ↓
engineering conversion
   ↓
physical correction
   ↓
derived variable
   ↓
QC / calibration estimate
Every diagnostic records which raw channels and references contributed. Evidence used to fit a correction cannot later count as independent validation.

Include QARTOD tests via ioos_qc, physical identities, duplicate residuals, maintenance/event metadata, flow/pump state, vessel motion and derived-variable consistency. This is computationally negligible and immediately useful aboard ship. QARTOD already has an actively maintained Python implementation. 

Second: hybrid Kalman drift estimator with explicit offset and gain states.

For each calibratable sensor, define only physically plausible states:

text
Copy
environmental state x(t)
sensor offset a(t)
sensor gain b(t)
optional sensor-specific environmental coefficient c(t)
Use random-walk drift priors derived from calibration history, not arbitrary tuning. Sparse references update the calibration state. During reference gaps, uncertainty expands automatically.

Run filtering live and smoothing post-cruise. Store correction as a separate variable, never overwrite raw data.

Third: changepoint/event model layered on the Kalman residual.

Use BOCPD for live alarms and ruptures or skchange for post-cruise segmentation. Candidate changepoints should be reconciled with:

text
Copy
maintenance log
pump state
cleaning
power/reset
sensor serial number
calibration coefficient change
valve state
ship mode
A documented sensor swap should force a new calibration segment instead of asking the algorithm to “discover” continuity that does not exist.

Fourth: uncertainty-weighted weak-reference adapter.

Build adapters for WOA23, delayed-mode Argo, OISST v2.1, SMAP/SMOS and ERA5. Every matchup should return:

python
Copy
ReferenceObservation(
    value,
    uncertainty,
    space_offset,
    time_offset,
    vertical_offset,
    product_resolution,
    independence_class,
    representativeness_uncertainty,
)
Do not expose “nearest climatology value” directly to a corrector. The adapter's main job is to inflate uncertainty when the matchup is poor.

Fifth: robust post-hoc calibration model selection.

For each sensor segment, fit a small model set:

[ \begin{array}{ll} M_0 &: y^*=y\ M_1 &: y^*=y-a\ M_2 &: y^*=(y-a)/b\ M_3 &: a=a_0+a_1t\ M_4 &: b=b_0+b_1t\ M_5 &: a=f(t,T,\text{flow},\ldots). \end{array} ]

Compare models by held-out reference residuals, posterior predictive checks and physical plausibility. Prefer the simpler correction unless a more complex model materially improves independent validation.

Deployment order should be flagging → attribution → shadow correction → reviewed correction → automated correction only for well-identified subsystems. pCO₂ standard-gas calibration and some pressure/heading corrections may reach automated correction early; fluorometry, surface salinity near freshwater features and shipboard airflow should remain more conservative.

Uncertainty, provenance and honest abstention
For every corrected value,

[ y_{\rm corr}=f(y_{\rm raw},\theta,\mathbf z), ]

DeepSignal should propagate uncertainty from the raw sensor, calibration parameters (\theta), ancillary variables (\mathbf z), and reference/representativeness uncertainty.

The GUM framework distinguishes statistically evaluated Type A components from Type B components derived from calibration certificates, manufacturer specifications and other knowledge. It also requires correlated inputs to be treated as correlated rather than blindly added in quadrature. 

For approximately linear models,

[ u_c^2= J\Sigma J^T, ]

where (J) is the Jacobian of the correction model and (\Sigma) is the covariance matrix of inputs.

For nonlinear corrections, bounded parameters, multimodal calibration hypotheses or changepoint uncertainty, use Monte Carlo propagation, which is explicitly standardized in JCGM 101. 

A corrected DeepSignal record should ideally carry:

text
Copy
raw_value
corrected_value
correction
standard_uncertainty
coverage_interval
qc_flag
correction_state
model_id/version
reference_ids
independence_score
changepoint_segment
correction_probability
abstention_reason
Bayesian models can publish posterior means/medians and credible intervals directly, but Bayesian uncertainty should still distinguish parameter uncertainty from model inadequacy and representativeness uncertainty. Bayesian treatments of GUM-style measurement models show that priors can materially reduce or distort uncertainty when data are sparse, so prior sensitivity should be tested rather than hidden. 

A useful abstention rule is:

[ P(\text{instrument error}\mid D) < p_{\rm correct} \quad\Longrightarrow\quad \text{flag but do not alter}. ]

Even stronger: require the proposed correction magnitude to exceed its uncertainty by a configurable factor and require independent attribution evidence. Otherwise return AMBIGUOUS_ENVIRONMENT_OR_SENSOR.

That is more scientifically defensible than returning a visually smoother product.

Programs, key literature, codebases and publishable gaps
Operational programs and codebases
SAMOS, the Shipboard Automated Meteorological and Oceanographic System initiative, has collected and quality-controlled research-vessel meteorological and near-surface oceanographic observations since 2005, including automated QC followed by trained analyst review. Its archive paper is Smith et al., Geoscience Data Journal, 2018, DOI 10.1002/gdj3.59. 

Rolling Deck to Repository, R2R, provides fleet-wide archiving and programmatic QA/QC of academic research-vessel underway data, including GPS, multibeam, CTD, XBT, meteorology and TSG products. Its QA intentionally identifies suspicious acquisition without modifying the original files. 

GO-SHIP publishes repeat-hydrography and ship-of-opportunity best practices, including thermosalinograph operations and high-accuracy hydrographic procedures. 

Argo delayed-mode QC is the strongest precedent for statistically estimating calibration drift against sparse and imperfect ocean references while explicitly propagating mapping uncertainty. The current conceptual lineage comes from Wong, Johnson and Owens and later Owens-Wong refinements. 

IOOS QARTOD provides variable-specific real-time QC manuals for temperature/salinity, dissolved oxygen, wind, ocean optics and other variables, with the Python ioos_qc package implementing QARTOD tests. 

OpenRVDAS is already architecturally compatible with this approach: it is modular Python 3 software built around readers, transforms and writers for streaming research-vessel sensors. DeepSignal fits naturally as transforms or a parallel analysis/annotation pipeline rather than as destructive preprocessing. 

Useful Python codebases include ioos_qc, pykalman, FilterPy, ruptures, PyMC, and OpenRVDAS itself. 

Particularly important papers and standards
Wong, A. P. S., G. C. Johnson, and W. B. Owens. 2003. “Delayed-Mode Calibration of Autonomous CTD Profiling Float Salinity Data by θ-S Climatology.” Journal of Atmospheric and Oceanic Technology 20:308-318. This is the foundational Argo drift-calibration method. 

Owens, W. B., and A. P. S. Wong. 2009. “An Improved Calibration Method for the Drift of the Conductivity Sensor on Autonomous CTD Profiling Floats by θ-S Climatology.” Deep-Sea Research Part I 56:450-457. 

Wong, A. P. S., J. Gilson, and C. Cabanes. 2023. “Argo Salinity: Bias and Uncertainty Evaluation.” Earth System Science Data 15:383-393. DOI 10.5194/essd-15-383-2023. 

Adams, R. P., and D. J. C. MacKay. 2007. “Bayesian Online Changepoint Detection.” arXiv:0710.3742. 

Fearnhead, P., and Z. Liu. 2007. “On-Line Inference for Multiple Changepoint Problems.” Journal of the Royal Statistical Society Series B 69:589-605. DOI 10.1111/j.1467-9868.2007.00601.x. 

Castelão, G. 2021. “A Machine Learning Approach to Quality Control Oceanographic Data.” Computers & Geosciences 155:104803. DOI 10.1016/j.cageo.2021.104803. 

O'Sullivan, N., S. Landwehr, and B. Ward. 2013. “Mapping Flow Distortion on Oceanographic Platforms Using Computational Fluid Dynamics.” Ocean Science 9:855-866. DOI 10.5194/os-9-855-2013. 

Moat, B. I. et al. foundational ship-CFD work includes “Quantifying the Airflow Distortion over Merchant Ships. Part I: Validation of a CFD Model.” Journal of Atmospheric and Oceanic Technology 23, DOI 10.1175/JTECH1858.1. 

Earp, A. et al. 2011. “Review of Fluorescent Standards for Calibration of In Situ Fluorometers.” Optics Express 19:26768-26782. DOI 10.1364/OE.19.026768. 

Bittig-related optode practice is complemented by the 2024 GOHSNAP best-practice paper “Oxygen Optodes on Oceanographic Moorings: Recommendations for Deployment and In Situ Calibration,” which documents irreversible drift, pressure response and cross-platform validation. 

“In-Air One-Point Calibration of Oxygen Optodes in Underway Systems.” Limnology and Oceanography: Methods, 2021. DOI 10.1002/lom3.10423. 

Hersbach, H. et al. 2020. “The ERA5 Global Reanalysis.” Quarterly Journal of the Royal Meteorological Society 146:1999-2049. DOI 10.1002/qj.3803. 

Huang, B. et al. 2021. “Improvements of the Daily Optimum Interpolation Sea Surface Temperature Version 2.1.” Journal of Climate 34:2923-2939. DOI 10.1175/JCLI-D-20-0166.1. 

JCGM 100:2008, Evaluation of Measurement Data: Guide to the Expression of Uncertainty in Measurement. DOI 10.59161/JCGM100-2008E; JCGM 101:2008, Propagation of Distributions Using a Monte Carlo Method, DOI 10.59161/JCGM101-2008. The GUM suite received a 2026 amendment addressing nonlinearity in measurement models. 

For current shipboard examples, 2026 AWI/PANGAEA releases for Heincke and Polarstern explicitly document TSG correction using post-season manufacturer recalibration, showing that even modern research-vessel workflows still rely heavily on independent post-deployment calibration rather than autonomous algorithmic correction. 

Research gaps with credible publication potential
Reference-independent identifiability scoring is the clearest gap. Existing systems generally provide QC flags or statistical correction recommendations, but there is no widely adopted shipboard framework that explicitly models the dependency graph among sensors, derived variables, reanalyses, assimilating products and calibration references and then computes whether a proposed correction is actually identifiable. A formal “independence-aware calibration evidence graph” validated on multiple research vessels would be novel and operationally valuable.

Joint front-versus-drift inference is still unsolved. Current QC often detects anomalous residuals without formally representing competing hypotheses such as sensor drift, front, rain lens, plume, upwelling and biofouling. The 2026 buoy study showing that raw prediction residuals cannot distinguish real events from faults reinforces this opening. A Bayesian competing-hypothesis model combining spatial coherence, T-C-S physics, meteorological forcing and maintenance events would be publishable if evaluated on expert-labelled vessel data. 

Event-conditioned calibration dynamics are underdeveloped. Cleaning, pump restart, sensor removal, valve switching and power cycling are normally treated as metadata or manually interpreted. A hybrid dynamical model in which engineering events alter state-transition priors could outperform generic changepoint detection while remaining interpretable.

Cross-vessel transfer of calibration priors is promising. Large archives such as SAMOS and R2R contain years of vessel-specific behavior. Hierarchical Bayesian models could learn distributions of drift rates, cleaning effects, heating coefficients and failure signatures by sensor model and installation class while retaining vessel-specific adaptation. This would be much more defensible than a universal neural network because the transferred quantities have physical meaning. SAMOS and R2R provide the observational foundation for such studies. 

Uncertainty-calibrated abstention needs benchmarking. Most anomaly studies report classification metrics. A more useful operational metric is selective risk: as the system abstains on uncertain cases, how rapidly does the error rate of automatically corrected observations fall? Conformal prediction, Bayesian posterior probabilities and GUM-style measurement uncertainty could be compared directly on real cruises.

Flow-distortion learning from dual anemometers plus CFD is a strong specialized project. Use CFD as the physical prior and long-term port/starboard sensor discrepancies as observations to update a direction-dependent distortion map. The key research question is whether sparse operational data can refine CFD without accidentally learning real atmospheric asymmetry. Existing CFD work gives a mature baseline against which to test this. 

Sparse-reference calibration benchmark datasets are missing. The field lacks a widely used public benchmark consisting of raw high-rate shipboard streams, maintenance logs, sensor swaps, bottle/Winkler/reference-gas checks, pre/post calibrations, independent remote-sensing products and expert correction decisions. DeepSignal could make a major contribution simply by publishing such a benchmark with synthetic injection protocols for known offsets, gains, steps and nonlinear drift while preserving real fronts.

The strongest publishable DeepSignal contribution would therefore not be “another anomaly detector.” It would be an uncertainty-aware, independence-aware calibration inference framework that knows when correction is identifiable and when it must abstain, demonstrated across several sensor families and several vessels. That is a materially different problem from conventional QC, and current operational practice plus the 2024-2026 ML literature show that it remains unsolved.