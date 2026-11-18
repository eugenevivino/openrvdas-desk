# Automated QC and Calibration Drift Detection for Research Vessel Underway Data

Scope note: research done 2026-11-17 with a limited tool budget (about 20 fetches). Every item under "Cited Findings" was read on the cited page. Items I could not open are listed under "Gaps" or labeled "unverified lead" so the report writer does not over-claim. No em dashes are used.

## 1. What IOOS QARTOD specifies, and open-source implementations (ioos_qc, CoTeDe)

### Takeaway
QARTOD defines a tiered set of real-time tests (required, strongly recommended, suggested) and a 1/2/3/4/9 flag scheme, but it explicitly says real-time automated QC generally cannot detect slow calibration drift. ioos_qc (Python, Apache-2.0, v3.1.x) implements the core tests plus streaming wrappers and is the obvious drop-in for OpenRVDAS; CoTeDe (Python, BSD-3) adds profile-oriented presets, fuzzy logic and an anomaly-detection method.

### Cited Findings
- The IOOS QARTOD page lists manuals for: in-situ temperature and salinity, in-situ currents, wind, dissolved oxygen, phytoplankton, pH, ocean optics, dissolved nutrients, water level, surface waves, HF radar, stream flow, passive acoustics, plus a Data Quality Control Flags manual (v1.2, 2020). No pCO2/carbonate-system manual is listed, and fluorescence has no standalone manual (closest are phytoplankton and ocean optics). The landing page shows no 2024 to 2026 manual updates (page metadata modified 2024-04-18). [IOOS QARTOD](https://ioos.noaa.gov/project/qartod/)
- QARTOD manual URLs (from the QARTOD page): T/S https://ioos.noaa.gov/ioos-in-action/temperature-salinity/ ; currents https://ioos.noaa.gov/ioos-in-action/currents/ ; wind https://ioos.noaa.gov/ioos-in-action/wind-data/ ; phytoplankton https://ioos.noaa.gov/ioos-in-action/phytoplankton/ ; pH https://ioos.noaa.gov/ioos-in-action/ph/ ; optics https://ioos.noaa.gov/ioos-in-action/oceanic-optics/ ; DO https://ioos.noaa.gov/ioos-in-action/manual-real-time-quality-control-dissolved-oxygen-observations/ ; flags manual https://cdn.ioos.noaa.gov/media/2020/07/QARTOD-Data-Flags-Manual_version1.2final.pdf . [IOOS QARTOD](https://ioos.noaa.gov/project/qartod/)
- The current T/S manual is "Update 2", file dated 2020-03-24. [QARTOD T/S page](https://ioos.noaa.gov/ioos-in-action/temperature-salinity/)
- T/S manual test tiers (13 tests). Required: 1 Timing/Gap, 2 Syntax, 3 Location, 4 Gross Range, 5 Climatology. Strongly recommended: 6 Spike, 7 Rate of Change, 8 Flat Line. Suggested: 9 Multi-Variate, 10 Attenuated Signal, 11 Neighbor, 12 TS Curve/Space, 13 Density Inversion. [QARTOD T/S Manual Update 2 (PDF)](https://cdn.ioos.noaa.gov/media/2020/03/QARTOD_TS_Manual_Update2_200324_final.pdf)
- The T/S manual covers "manned vessels of opportunity" as mobile surface platforms sampling at fixed depth along a track; tests may be run along path distance or x/y; mobile sensors need response-time and thermal-mass corrections before real-time tests. It does not name thermosalinographs explicitly. [QARTOD T/S Manual](https://cdn.ioos.noaa.gov/media/2020/03/QARTOD_TS_Manual_Update2_200324_final.pdf)
- Key drift statement: gradual calibration changes and long-term drift generally cannot be detected or corrected by automated real-time QC, and are hard to correct even in post-processing. [QARTOD T/S Manual](https://cdn.ioos.noaa.gov/media/2020/03/QARTOD_TS_Manual_Update2_200324_final.pdf)
- Biofouling: temperature and pressure sensors tolerate moderate fouling, conductivity sensors do not; fouling typically lowers conductivity and salinity, degrades gradually and usually goes unnoticed until sensor replacement. [QARTOD T/S Manual](https://cdn.ioos.noaa.gov/media/2020/03/QARTOD_TS_Manual_Update2_200324_final.pdf)
- Flags: 1 Pass, 2 Not evaluated, 3 Suspect or of high interest, 4 Fail, 9 Missing. Real-time flags should not be overwritten; post-processing should produce a new flag set. Operators choose and document thresholds; manual example values are illustrative only. [QARTOD T/S Manual](https://cdn.ioos.noaa.gov/media/2020/03/QARTOD_TS_Manual_Update2_200324_final.pdf)
- ioos_qc: "IOOS QARTOD and other Quality Control tests implemented in Python", Apache-2.0, conda-forge package, about 892 commits. [GitHub ioos/ioos_qc](https://github.com/ioos/ioos_qc)
- ioos_qc docs (version 3.1.1.post0) list qartod functions: gross_range_test, climatology_test, spike_test, rate_of_change_test, flat_line_test, attenuated_signal_test, location_test, density_inversion_test, pressure_test, impossible_date_test, data_reception_test, time_gap_test, syntax_test, percentile_range_test, qartod_compare (flag aggregation); argo module (duplicate_timestamp_test, pressure_increasing_test, speed_test); axds valid_range_test; Streams (NumpyStream, PandasStream, XarrayStream, NetcdfStream) and Stores (PandasStore, CFNetCDFStore, NetcdfStore). [ioos_qc docs](https://ioos.github.io/ioos_qc/)
- Notably absent from the ioos_qc function list: no dedicated neighbor test or multivariate test function, and no drift test. [ioos_qc docs](https://ioos.github.io/ioos_qc/)
- CoTeDe: Python QC framework, BSD-3, presets for GTSPP, EuroGOOS, XBT, Argo and QARTOD; two fuzzy-logic approaches (Timms et al. 2011 / Morello et al. 2014 style and bisector defuzzification); an anomaly-detection approach (Castelao 2021, Computers and Geosciences, doi:10.1016/j.cageo.2021.104803); framework paper Castelao 2020 JOSS doi:10.21105/joss.02063. [GitHub castelao/CoTeDe](https://github.com/castelao/CoTeDe)

### Inferences
- The QARTOD tests that are "suggested" (multivariate, neighbor, attenuated signal) are exactly the ones closest to drift detection, and they are the least standardized and least implemented. A ship deployment that wants drift detection must build these itself.
- Because QARTOD says real-time flags must not be overwritten and delayed-mode results get a new flag set, an OpenRVDAS integration should write real-time flags as separate fields (e.g., `<var>_qc_rt`) and leave room for delayed-mode flags.
- ioos_qc's stateless functions over arrays fit OpenRVDAS transforms if the transform holds a short rolling buffer (spike and rate-of-change need neighbors; flat line needs a window; attenuated signal needs longer windows).

### Gaps
- I did not open the wind, currents, pH, phytoplankton or optics manuals in detail; their test lists and parameter guidance (for example, the currents manual's ADCP-specific tests such as echo intensity, correlation magnitude, percent good) are not verified here.
- No QARTOD manual for underway pCO2 found on the IOOS page.
- ioos_qc latest release date not visible (GitHub release section empty in fetch); docs title shows 3.1.1.post0.

## 2. SAMOS QC: automated and visual flags, delayed mode, known ship sensor biases

### Takeaway
SAMOS (FSU COAPS) receives daily 1-minute met and TSG files from about 30 research vessels, runs automated QC within minutes, merges files after a 10-day delay, and applies visual QC by an analyst only for NOAA vessels and Falkor (too). About 5% of measurements are flagged. Recurrent problems are flow distortion of wind, ship heating of air T/RH, radiometer issues, TSG plumbing, and occasional slow calibration drift.

### Cited Findings
- Flag set (letters A to Z): A units assigned; B outside physical range; C time out of sequence/invalid; D failed T >= Tw >= Td; E failed true-wind recomputation check; F unrealistic platform velocity; G more than 4 standard deviations from ICOADS climatology; H discontinuity/step; I interesting feature (e.g., hurricane); J erroneous, do not use (visual); K suspect, cause unknown; L position over land vs ETOPO; M known instrument malfunction; N in port; O units mismatch; P position uncertain; Q questionable per operator; R interpolated upstream; S spike; T time duplicate; U, V, X, Y from the statistical SASSI test (neighbor threshold, spike, step, suspect between steps), noted as not currently in use; Z passed. [SAMOS quality flags](https://samos.coaps.fsu.edu/html/samos_quality_flag.php)
- 2025 SAMOS annual report: 30 of 31 recruited vessels routinely reported (NOAA 15, SIO 3, IMOS 3, WHOI 2, one each SOI, OPP, USCG, BIOS, UH, UW, UA). 6,611 ship days, 9,095,936 one-minute records, 260,659,626 measurements; 13,182,053 (about 5.0%) received A to Y flags, similar to 2024. [SAMOS 2025 Annual Report](https://samos.coaps.fsu.edu/html/docs/2025SAMOSAnnualReport_final.pdf)
- Workflow: daily packages nominally near 0000 UTC; preliminary data posted within minutes and auto-QC'd; an analyst checks each file for major problems and contacts ship technicians; after a 10-day delay files are merged into daily intermediate files; visual QC by a qualified marine meteorologist yields research-quality products, but only for NOAA vessels and Falkor (too); visual QC funding for other non-NOAA vessels was discontinued from 2013; 14 vessels got automated QC only. SASSI secondary automated QC was absent in 2025. [SAMOS 2025 Annual Report](https://samos.coaps.fsu.edu/html/docs/2025SAMOSAnnualReport_final.pdf)
- Per-vessel flag rates in 2025 ranged widely, e.g., Shimada 2.5%, Atlantic Explorer 3.4%, Bigelow 6.1%, Gordon Gunter 10.8%, Tangaroa 12.0%, Ferdinand Hassler 17.8%. [SAMOS 2025 Annual Report](https://samos.coaps.fsu.edu/html/docs/2025SAMOSAnnualReport_final.pdf)
- Problems reported in 2025: wind flow distortion from superstructure and ship-speed changes, a backward-installed anemometer (Lasker), iced anemometer, flatlining wind data; slightly negative nighttime shortwave flagged out of bounds, longwave flatlining at 0 W/m2 (Nuyina), light contamination of radiometers; TSG restricted flow, port shutdowns, air in plumbing, persistent flagging traced to likely installation issue (Hassler); Bigelow intake SST reading 1 to 2 C high; Oregon II TS3 anomalously high; ship heating affecting air T and RH; Atlantic Explorer forward thermometer drifted off calibration. The report does not mention ML. [SAMOS 2025 Annual Report](https://samos.coaps.fsu.edu/html/docs/2025SAMOSAnnualReport_final.pdf)
- R2R and SAMOS: UNOLS vessels send underway MET and TSG in near real time to SAMOS; checks include file completeness/readability, daily visual monitoring, automated scientific QC assigning one alphabetic flag per value (suspect values flagged, not removed), criteria of physical range, climatology departures, position over water, excessive vessel speed, and physical consistency of atmospheric variables. SAMOS sends all quality-evaluated data to NCEI; QC statistics are available to technicians via a JSON web service (https://samos.coaps.fsu.edu/html/Preliminary_iquality_json.php). [R2R Real-Time Data](https://www.rvdata.us/about/real-time-data)

### Inferences
- SAMOS is the de facto operational baseline for US research-vessel met/TSG QC, and it is mostly rule-based (range, climatology at 4 sigma, physical consistency, platform checks). Its statistical neighbor test (SASSI) is currently inactive, so there is an evident gap in automated step/drift detection that an on-ship tool could fill.
- The flag rates and problem list show that most flagged data come from installation, plumbing and exposure issues rather than slow drift; a drift detector must therefore be robust to these discrete failure modes or it will be swamped.
- The SAMOS 10-day delay and analyst-in-the-loop means drift is typically caught days later; on-ship detection (OpenRVDAS) could shorten this to hours.

### Gaps
- Did not open SAMOS peer-reviewed papers (e.g., Smith et al. on the 2005 to 2017 archive) or quantitative airflow-distortion studies (e.g., Yelland/Moat CFD work); a search returned an NOC report (https://nora.nerc.ac.uk/id/eprint/502829/1/MTD_02_10.pdf) but it was not opened.
- Radiation sensor bias magnitudes (shading, tilt) not verified.

## 3. Calibration drift detection methods and evidence

### Takeaway
Operational practice for underway TSG drift is reference-based: discrete water samples (about daily), co-located CTD casts and Argo profiles, plus climatology/analysis comparisons, with drift fitted in delayed mode (French TSG-QC, NOAA AOML). Statistical methods (state-space/Kalman, CUSUM on residuals) are plausible but I found no operational shipboard deployment. BGC-Argo provides the best-documented drift-adjustment literature and shows that the choice of reference and smoothing can itself introduce errors larger than target accuracy.

### Cited Findings
- NOAA AOML TSG real-time QC applies 8 tests derived from the 10 GOSUD real-time tests: date, location, global SST/SSS range, regional range, spike along track, gradient, constant value, climatology; only data passing all tests are sent to the GTS (TRACKOB) typically within 24 h. Delayed mode adds comparisons against NCEP weekly analysis and near-surface values from profiling floats, XBTs, CTDs and thermistor chains; water samples are collected regularly on selected transects to calibrate TSGs. [NOAA AOML TSG QC](https://www.aoml.noaa.gov/phod/tsg/data/qc.php) (thresholds in https://www.aoml.noaa.gov/phod/tsg/data/qc_sheet.pdf, not opened)
- TSG-QC (IRD/LEGOS US191): MATLAB software for interactive validation of SeaBird TSG SST/SSS; compares with WOA and ISAS climatologies; automatic threshold QC; validates and adjusts against bucket water samples (usually one per day), Argo floats and co-located CTD casts; estimates sensor drift quantitatively; outputs GOSUD CORTSG NetCDF v3.0. The wiki does not state the fitting method. [TSG-QC wiki](https://forge.ird.fr/us191/TSG-QC/-/wikis/home)
- Intake vs surface temperature: Matthews and Matthews (2013) found bucket SST minus 3 m TSG averaged -0.4 +/- 0.2 C (day -0.5, night -0.3) in the central tropical Pacific, with near-surface gradients of about -0.16 C/m by day; OSTIA was about 0.2 C cooler than daily mean 3 m temperature. Their physical model estimates engine-room warming of intake pipes at hundredths, not tenths, of a degree, so they consider it an unlikely major cause of warm intake bias; other cited causes include conduction through fittings and stagnant water near pumps. They recommend pre-cruise calibration to at least 0.01 C. [Matthews and Matthews 2013, Ocean Science 9:695](https://os.copernicus.org/articles/9/695/2013/os-9-695-2013.pdf)
- BGC-Argo drift adjustment (Wimart-Rousseau et al. 2024, Biogeosciences 21:1191): oxygen optodes drift during storage; with in-air referencing accuracies of about 1.5 umol/kg are achievable, without it up to about 3%. pH sensors claim +/-0.05; published adjustments reach +/-0.005 to 0.007. Four reference algorithms (CANYON-B, LIR-pH, ESPER-NN, ESPER-LIR) differ by about 0.003 to 0.04 pH; choice of reference depth shifts results by about 0.005; step-like segment adjustments (SAGE tool) create artificial jumps of about 0.01 pH, and smoother adjustments (linear, running mean, spline) are preferred. The 0.01 pH accuracy needed for surface pCO2 (about 10 uatm) is not consistently achieved; the authors recommend an independent near-surface reference. [Biogeosciences 2024](https://bg.copernicus.org/articles/21/1191/2024/)
- SAMOS 2025 documents a real case of a ship thermometer drifting off calibration (Atlantic Explorer) and an intake SST reading 1 to 2 C high (Bigelow), both caught by data center review rather than onboard automation. [SAMOS 2025 Annual Report](https://samos.coaps.fsu.edu/html/docs/2025SAMOSAnnualReport_final.pdf)

### Inferences
- Method ladder for an OpenRVDAS drift module, from proven to experimental:
  1. Proven/operational (delayed mode): sample-minus-sensor differences from salinometer bottles, CTD surface bins, Argo near-surface matchups, fitted over time (TSG-QC, AOML).
  2. Proven in practice but mostly manual: redundant sensor comparison (primary vs secondary TSG; intake vs hull SST; port vs starboard met sensors) with an analyst watching difference plots.
  3. Plausible, not found operational on ships: automated residual monitoring of those differences with robust statistics (rolling median, MAD), CUSUM or Page-Hinkley on residuals, and a Kalman/state-space model with a random-walk bias state updated by each reference sample.
  4. Experimental: ML predictors (e.g., predicting TSG SST from satellite/reanalysis plus ship context) and flagging growing residuals.
- The BGC-Argo result generalizes: the reference choice (satellite product, reanalysis, climatology) and the adjustment shape (stepwise vs smooth) can produce artifacts comparable to the drift being corrected, so a drift detector should report uncertainty and favor smooth corrections.
- Near-surface stratification (0.4 C mean bucket vs 3 m differences, diurnal warming) means intake SST vs satellite skin/subskin SST comparisons must be restricted to nighttime, well-mixed (wind > about 6 m/s) conditions or use foundation-SST products, or they will flag real physics as drift.
- Data needs: for TSG salinity, at least daily bottle samples or CTD casts; for drift of order 0.01 psu per month, several weeks of matchups are needed before a trend is statistically distinguishable. Compute needs are trivial (scalar filters), so the bottleneck is reference data, not CPU.

### Gaps
- I did not open: SOCAT QC cookbook / flag definitions (A to E dataset flags, WOCE cell flags); Johnson et al. pH and nitrate adjustment papers directly; fluorometer NPQ (quenching) correction papers (e.g., Xing et al. 2012) and fluorometer drift/dark-offset methods; any paper applying Kalman filtering or CUSUM to TSG or ship met drift. These remain unverified.
- No source found (within budget) quantifying how often primary and secondary TSG drift together (common mode).
- ERA5 or buoy matchup methods for ship met bias were not verified in this session.

## 4. Operational systems at sea: what is automatic vs manual

### Takeaway
Verified: SAMOS/R2R (automated rule-based flags within minutes, visual QC only for subset, 10-day delayed merge) and AOML TSG (automated 8-test real-time QC, delayed-mode comparisons and water-sample calibration). OpenRVDAS itself is an acquisition framework of readers, transforms and writers and does not advertise QC or alerting on its main page.

### Cited Findings
- OpenRVDAS: modular framework composed of Readers, Transforms and Writers; reads serial and network sensors, optionally transforms, streams to logfiles, network ports, databases; requires Python 3.11+; about 2,262 commits; the README does not mention quality control or alerting. [GitHub OpenRVDAS](https://github.com/OceanDataTools/openrvdas)
- R2R automatic vs manual: automated file checks and per-value flags; daily visual monitoring; feedback to technicians during the cruise; full sensor-level data reach R2R after the cruise. [R2R Real-Time Data](https://www.rvdata.us/about/real-time-data)
- AOML: real-time is fully automated (8 tests, GTS within 24 h); delayed mode adds reference comparisons and bottle calibration. [NOAA AOML TSG QC](https://www.aoml.noaa.gov/phod/tsg/data/qc.php)
- SAMOS: analyst checks each daily file and contacts ship technicians; visual QC only for NOAA ships and Falkor (too). [SAMOS 2025 Annual Report](https://samos.coaps.fsu.edu/html/docs/2025SAMOSAnnualReport_final.pdf)

### Inferences
- Integration sketch for OpenRVDAS (design proposal, not existing code): (a) a `QartodTransform` wrapping ioos_qc functions with a per-variable YAML config (mirroring ioos_qc's config format) and a rolling buffer, emitting `<field>_qc` values; (b) a `PairDifferenceTransform` that computes primary minus secondary, intake minus hull, or sensor minus reference (CTD surface bin, bottle entry, satellite match) and runs a CUSUM or Kalman bias estimate; (c) a writer or listener that raises alerts to the watchstander only when residual statistics persist, to limit flag fatigue; (d) export of SAMOS-style letter flags for compatibility with SAMOS/R2R. Real-time flags kept immutable per QARTOD.
- Because OpenRVDAS already runs on the ship with full-rate data, it can do checks SAMOS cannot (sub-minute flat-line, pump-flow coupling with TSG flow meter, using ship speed/heading to gate wind QC).

### Gaps
- Not verified this session: Scripps MetAcq, CORIOLIX (Oregon State) QC features, Saildrone QC pipeline, OOI QC (OOI is known to use QARTOD-style tests but this was not opened), UNOLS shipboard technician practices, and R2R navigation QC/BestRes products (the R2R real-time page does not describe them). I could not list OpenRVDAS transform source files (GitHub tree blocked by robots; API access not enabled), so I cannot confirm whether a QC/value-filter transform exists in the codebase.

## 5. ML-based oceanographic QC: evidence and reported metrics

### Takeaway
ML QC is active research, mostly for profiles (Argo, moorings, CTD), not for ship underway streams. Reported ROC-AUC around 0.94 to 0.97 with false positive rates near 20% indicate ML is suitable as a triage/prioritization layer, not as an autonomous flagger. CoTeDe's anomaly-detection method is the most accessible open-source option.

### Cited Findings
- Shao et al. 2025 (Frontiers in Marine Science 12, doi:10.3389/fmars.2025.1661373): semi-supervised bidirectional GRU with attention and Mean Teacher; trained on a RAMA mooring (BL01, about 584,000 samples, 2014 to 2018, 20 to 100 m) and four Argo floats (110,454 records). Temperature ROC-AUC 0.966, PR-AUC 0.952, TPR 97.48%, TNR 80.67%, FPR 19.33%; salinity ROC-AUC 0.940, PR-AUC 0.916, TPR 95.68%, TNR 79.57%, FPR 20.43%. Some salinity false positives were real water-mass intrusions; evaluation used one buoy and four floats; confusion-matrix definitions are nonstandard (TP defined as normal flagged normal). Compared against SalaciaML (MLP, Mediterranean; ROC-AUC 0.952, TPR 89%, TNR 86%), noting results are not strictly comparable. [Frontiers 2025](https://www.frontiersin.org/articles/10.3389/fmars.2025.1661373/full)
- CoTeDe includes an anomaly-detection QC approach (Castelao 2021, Computers and Geosciences) and fuzzy-logic QC. [GitHub CoTeDe](https://github.com/castelao/CoTeDe)

### Inferences
- The roughly 20% false positive rate (in the paper's own terms) would generate unacceptable alert loads if run unfiltered on 1 Hz underway data; ML should rank suspect segments for human review or feed a delayed-mode QC queue.
- Labeled training data for underway ship data could come from SAMOS visually QC'd NOAA vessel files (research-quality flags J, K, etc.), which is a possible but untested training source.

### Gaps
- Unverified leads (seen in search results, not opened): Euro-Argo deliverable D4.4.6 "Machine Learning applied to Argo floats temperature and salinity Delayed-Mode QC" (https://www.euro-argo.eu/content/download/142209/file/D4.4.6%20Machine%20Learning%20applied%20to%20Argo%20floats%20temperature%20and%20salinity%20Delayed-Mode%20Quality%20Control_v1.0.pdf); signature-method Argo QC on arXiv (https://arxiv.org/pdf/1907.00500); an Ifremer Archimer ML QC paper (https://archimer.ifremer.fr/doc/00807/91895); EGU26-11527 abstract (https://meetingorganizer.copernicus.org/EGU26/EGU26-11527.html); "How accurate are salinity measurements around Antarctica? A machine-learning approach" (University of Melbourne). Their metrics are not verified here.
- I found no ML QC paper specific to research vessel underway met/TSG streams within the budget.

## 6. Failure modes

### Takeaway
Documented failure modes are installation and plumbing faults, flow distortion and ship heating, real near-surface stratification masquerading as sensor bias, gradual conductivity fouling that is invisible to real-time tests, and reference-choice artifacts in drift correction. Common-mode drift of redundant sensors and flag fatigue are plausible but I found no quantitative source.

### Cited Findings
- Real-time automated QC generally cannot detect gradual drift; conductivity fouling lowers salinity gradually and usually goes unnoticed until sensor swap. [QARTOD T/S Manual](https://cdn.ioos.noaa.gov/media/2020/03/QARTOD_TS_Manual_Update2_200324_final.pdf)
- Thresholds are operator-selected; manual examples are illustrative, meaning region-mismatched thresholds are an acknowledged risk. [QARTOD T/S Manual](https://cdn.ioos.noaa.gov/media/2020/03/QARTOD_TS_Manual_Update2_200324_final.pdf)
- Physical-range flags trip on benign artifacts such as slightly negative nighttime shortwave radiation; installation errors (backward anemometer) and plumbing issues (air in TSG lines, restricted flow, in-port shutdowns) dominate flags. [SAMOS 2025 Annual Report](https://samos.coaps.fsu.edu/html/docs/2025SAMOSAnnualReport_final.pdf)
- Real near-surface temperature gradients (mean -0.4 C bucket minus 3 m, up to about -1 C) can mimic or cancel intake warm bias, making bias correction unreliable. [Matthews and Matthews 2013](https://os.copernicus.org/articles/9/695/2013/os-9-695-2013.pdf)
- Drift-correction design can inject artifacts (about 0.01 pH jumps from step adjustments; 0.003 to 0.04 pH spread across reference algorithms). [Biogeosciences 2024](https://bg.copernicus.org/articles/21/1191/2024/)
- ML QC flags real oceanographic events (water-mass intrusions) as anomalies. [Frontiers 2025](https://www.frontiersin.org/articles/10.3389/fmars.2025.1661373/full)
- SAMOS's statistical neighbor/step tester (SASSI) is "not currently in use", showing statistical detectors can be retired operationally. [SAMOS quality flags](https://samos.coaps.fsu.edu/html/samos_quality_flag.php)

### Inferences
- Biofouling vs drift: both produce monotonic salinity decrease; they can be distinguished only by reference samples or by the step change at cleaning. A detector should log cleaning/maintenance events (OpenRVDAS could ingest them as a reader) and treat post-cleaning steps as evidence of fouling.
- Common-mode: primary and secondary TSG sharing an intake, pump and plumbing share warming, bubbles and fouling, so their difference is blind to those; at least one independent reference (CTD, bottle, satellite foundation SST) is required.
- Flag fatigue: per-vessel flag rates of 2.5 to 17.8% suggest that naive alerting would overwhelm watchstanders; alert on persistent residual change, not on every flagged value.
- Region-tuned thresholds: climatology tests at 4 sigma from ICOADS (SAMOS) can fail in frontal zones and coastal plumes; the "I" (interesting feature) flag exists precisely for this.

### Gaps
- No quantitative study found on common-mode drift frequency, alert fatigue in shipboard ops, or false alarm rates of SAMOS automated flags versus visual QC.
