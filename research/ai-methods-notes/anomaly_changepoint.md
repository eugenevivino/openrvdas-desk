# Anomaly/fault detection and change-point detection for multivariate research-vessel sensor streams

Scope note: Research done 2026-11-17 with a limited budget of tool calls. Every item under "Cited Findings" comes from a page opened during this session. Items under "Inferences" that come from background knowledge and not from a page opened here are marked **[background, not verified this session]**. Treat them as leads that need checking before citation.

## 1. Classical/statistical methods: which work, which can stream

### Takeaway
On honest benchmarks, simple statistical and linear methods (PCA reconstruction error, nearest-neighbor distance, robust normalization) match or beat recent deep models. Most of them fit naturally into a per-record streaming transform at 1 Hz. Matrix profile has a true incremental streaming mode (STUMPY `stumpi`). Offline change-point search (ruptures/PELT) suits retrospective segmentation, not live alarms.

### Cited Findings
- PCA reconstruction error was the best single method in Sarfraz et al.'s (ICML 2024) re-evaluation. Point-wise F1 vs. the best deep model: SWaT 0.833 vs 0.810 (GDN); WADI-127 0.501 vs 0.347 (GDN); WADI-112 0.655 vs 0.571 (GDN); SMD 0.572 vs 0.526 (GDN). Range-wise F1_T on SWaT was 0.574 vs 0.425 (TranAD). GDN still wins on point-adjusted F1 for WADI-112 (0.833 vs 0.783) and SMD (0.929 vs 0.921). — [Sarfraz et al. 2024, arXiv 2405.02678](https://arxiv.org/html/2405.02678v3); [PMLR v235](https://proceedings.mlr.press/v235/sarfraz24a.html)
- In the same study, L2-norm and 1-NN distance baselines on SWaT (F1 0.782 each) roughly matched OmniAnomaly (0.773) and USAD (0.772). A 1-layer linear MLP on SMD (F1 0.514) beat USAD (0.426) and OmniAnomaly (0.415). — [Sarfraz et al. 2024](https://arxiv.org/html/2405.02678v3)
- Sarfraz et al. distilled trained state-of-the-art deep models into linear models that "still perform on par". They conclude that these models "effectively learn linear mappings". They also note that the normalization choice (median/IQR vs mean/std) changes accuracy. — [Sarfraz et al. 2024](https://arxiv.org/html/2405.02678v3)
- TSB-AD (NeurIPS 2024 Datasets & Benchmarks) uses 40 datasets, 1,070 curated series and 40 algorithms. It reports that "simpler architectures and statistical methods often perform better than advanced neural networks". Neural networks did well on multivariate cases and foundation models did well on point anomalies. Its recommended metric is VUS-PR. — [TSB-AD site](https://thedatumorg.github.io/TSB-AD); [NeurIPS paper PDF](https://proceedings.neurips.cc/paper_files/paper/2024/file/c3f3c690b7a99fba16d0efd35cb83b2c-Paper-Datasets_and_Benchmarks_Track.pdf); [PyPI TSB-AD](https://pypi.org/project/TSB-AD/)
- STUMPY `stumpi` computes the matrix profile incrementally. Each `update(t)` computes only the new distances. The docs call it "essentially O(1)" per update compared with O(n^2) batch, and report roughly 450+ points/s on modest hardware. `egress=True` (the default) keeps a fixed-size sliding window. Past profile values can change when new neighbors arrive. A "left" profile (`left_P_`) uses only past neighbors and is never revised, which is the right choice for live alarms. — [STUMPY streaming tutorial](https://stumpy.readthedocs.io/en/stable/Tutorial_Matrix_Profiles_For_Streaming_Data.html)
- The ruptures library implements offline multiple-change-point detection for multivariate series. Truong, Oudre and Vayatis structure the problem as cost function + search method + constraint on the number of changes. — [Truong et al., Selective review of offline change point detection, arXiv 1801.00718](https://arxiv.org/abs/1801.00718?context=cs)
- Telemanom's thresholding is itself a classical streaming component. It applies a nonparametric dynamic threshold to EWMA-smoothed prediction errors and chooses z from {2.5,...,10}. It prunes near-threshold sequences (p = 0.13; 0.05 < p < 0.20 worked) and can set a per-channel minimum score from past confirmed false positives. — [Hundman et al. 2018, ar5iv 1802.04431](https://ar5iv.arxiv.org/html/1802.04431)
- On a single coastal buoy, simple statistical tests had much lower recall than a learned predictor. Grubbs: F1 81.2%, recall 60.2%. 3-sigma: F1 81.6%, recall 60.1%. The learned model reached F1 85.8% and recall 81.6%. — [Song et al. 2025, Frontiers in Marine Science](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2025.1528587/full)

### Inferences
- Streaming capability, by method **[background, not verified this session]**:
  - **Single pass, O(1) per sample, trivially streaming:** robust z-score/MAD over a rolling window, EWMA control charts, CUSUM, Page-Hinkley, Shewhart/SPC rules, Kalman filter innovation (chi-square on normalized innovation) tests, and online PCA scoring with a fixed fitted model (Hotelling T2 plus SPE/Q).
  - **Streaming with a refit cadence:** Isolation forest (batch fit, cheap scoring; river has a streaming half-space-trees variant), STL residuals (needs a seasonal window, so it is effectively mini-batch), and matrix profile via `stumpi`.
  - **Native online change-point detection:** BOCPD (Adams and MacKay 2007). Each step updates the run-length posterior. Pruning keeps cost bounded.
  - **Offline/retrospective:** PELT/BinSeg/KernelCPD in ruptures. These can run in a sliding batch every N minutes, which suits post-cruise segmentation and not low-latency alarms.
- PCA with T2/SPE is the strongest-evidence multivariate method for this use case. Sarfraz et al. show PCA reconstruction error (which is the SPE statistic) beats deep models on industrial multivariate benchmarks. It is also interpretable through per-variable SPE contributions, which point to the faulty sensor. Classical sensor-validation papers on PCA SPE (e.g., Dunia, Qin et al. 1996, AIChE J.) are **[background, not verified this session]**.
- Normalize with median/IQR, not mean/std. Sarfraz et al. found this mattered, and ship data have heavy-tailed transients.

### Gaps
- I did not open the Adams and MacKay 2007 BOCPD paper, the PELT paper (Killick et al. 2012), the original PCA SPE sensor-validation papers, or Page-Hinkley/CUSUM references this session. Their claims above are background knowledge only.
- I found no head-to-head benchmark of BOCPD vs CUSUM vs PELT on oceanographic underway data.

## 2. Deep learning methods and what honest evaluation says

### Takeaway
Most published deep TSAD gains (USAD, OmniAnomaly, Anomaly Transformer, TranAD, GDN) disappear under honest evaluation. Point-adjust F1 lets a random score look state of the art. The common benchmarks (SMAP/MSL, Yahoo, NAB, SWaT) are flawed. Simple baselines match or beat these models. Telemanom is the most operationally credible deep method because NASA deployed it with a careful thresholding and false-positive design, not because its LSTM is superior.

### Cited Findings
- Kim et al. (AAAI 2022) show that point adjustment (PA) can drive a random U(0,1) anomaly score to F1_PA close to 1 when anomaly segments are long. They write that "even a random anomaly score can easily turn into a state-of-the-art TAD method". An untrained, randomly initialized model scores comparably to existing methods even without PA. They propose PA%K, which credits a segment only if more than K% of its points exceed threshold, and an untrained-model baseline. — [Kim et al., arXiv 2109.05257](https://arxiv.org/abs/2109.05257v1); [ar5iv full text](https://ar5iv.arxiv.org/html/2109.05257); [AAAI version](https://ojs.aaai.org/index.php/AAAI/article/view/20680)
- Sarfraz et al. report that a random predictor scores F1_PA = 0.963 on SWaT, above most published methods. They say SWaT should be discontinued as a benchmark. They exclude SMAP/MSL from their main results as flawed and recommend AUPRC and range-based F1 over PA-F1. — [Sarfraz et al. 2024](https://arxiv.org/html/2405.02678v3)
- Wu and Keogh argue that most exemplars in the popular benchmarks (Yahoo, Numenta, NASA, etc.) have at least one of four flaws, so much apparent progress "may be illusory". They introduce the UCR Time Series Anomaly Archive. The abstract does not name the four flaws; the full paper's flaw list is triviality, unrealistic anomaly density, mislabeled ground truth and run-to-failure bias **[naming from background; the abstract page opened did not list them]**. — [Wu and Keogh, arXiv 2009.13807](https://arxiv.org/abs/2009.13807v5); [NSF PAR copy](https://par.nsf.gov/servlets/purl/10548865)
- Telemanom (Hundman et al., KDD 2018):
  - **Data:** 82 channels (SMAP 55, MSL 27) and 105 labeled anomaly sequences (59% point, 41% contextual).
  - **Model:** one LSTM per channel, 2x80 units, sequence length 250.
  - **Operations:** data in 1-minute windows, evaluated in 70-minute batches that match the downlink schedule.
  - **Results:** precision/recall SMAP 85.5/85.5, MSL 92.6/69.4, total 87.5/80.0, F0.5 = 0.71.
  - **Code:** Apache 2.0, source only, no releases.
  - The authors stress that even a low false-positive rate overwhelms human reviewers at scale. — [Hundman et al., ar5iv](https://ar5iv.arxiv.org/html/1802.04431); [telemanom GitHub](https://www.github.com/khundman/telemanom)
- TSB-AD's large benchmark found statistical and simple methods often beat advanced neural networks overall. Neural networks have an edge mainly on multivariate series. — [TSB-AD](https://thedatumorg.github.io/TSB-AD)

### Inferences
- In practice, any deep model for vessel streams must beat a PCA-SPE and a robust z-score baseline on the vessel's own labeled events, scored with VUS-PR, AUPRC or range-F1 and not PA-F1. Otherwise it should not ship.
- Telemanom's transferable lessons are its per-channel forecaster + EWMA error + dynamic threshold + pruning + per-channel s_min from past false positives. These carry over to any forecaster, including a simple AR model. The forecaster is the least important part.
- Compute: Telemanom-style per-channel LSTMs need offline GPU or CPU training, but inference on 1 Hz, dozens of channels is light on a CPU. TranAD, Anomaly Transformer and GDN add training complexity with no demonstrated honest gain **[inference]**.
- An LSTM autoencoder is a reasonable comparison point only. Kim et al. show that an untrained single-layer LSTM autoencoder is a competitive baseline, which undercuts claims for trained ones.

### Gaps
- I did not open the original USAD, OmniAnomaly, Anomaly Transformer, TranAD, GDN, TimeSeAD or TSB-UAD papers this session. Their performance claims are covered only through Sarfraz et al.'s re-evaluation and TSB-AD.
- I did not retrieve the TSB-AD leaderboard top methods; the page linked out to them.
- I found no deep-vs-simple comparison on shipboard underway data specifically.

## 3. Sensor-fault taxonomy and detector-to-fault mapping

### Takeaway
Ocean/buoy data show the classic fault classes in measurable proportions: missing data and stuck values are common, and spikes and electrical-fault point anomalies also occur. No single detector covers all fault types. A layered design is needed: rule/QARTOD-style gross checks, per-channel temporal detectors, and cross-sensor multivariate consistency.

### Cited Findings
- On one Qingdao buoy (10-minute data, May to Sept 2023, 14,834 samples), 8.85% of data were missing. Stuck-value rates were air temperature 4.1%, water temperature 8.1%, wind speed 0.79% and air pressure 2.69%. Flags used: correct / suspicious / missing / stuck. — [Song et al. 2025](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2025.1528587/full)
- The R/V Isabu CTD anomaly labels were based on valid ranges (e.g., below 0 C or above 35 C), instantaneous rate of change and expert field knowledge. Abnormal patterns included missing values, out-of-range readings, point anomalies from electrical faults and collective anomalies in the mixed layer. — [Kang, Kim and Lim 2024, JMSE 12(5):807](https://www.mdpi.com/2077-1312/12/5/807)
- 59% of the labeled SMAP/MSL anomalies were point anomalies and 41% contextual. — [Hundman et al.](https://ar5iv.arxiv.org/html/1802.04431)
- TSB-AD reports that foundation models do well on point anomalies, while neural models help mainly on multivariate cases. — [TSB-AD](https://thedatumorg.github.io/TSB-AD)

### Inferences (detector-to-fault mapping) **[engineering judgment plus background; not from a single verified source]**
| Fault | Signature | Best-suited detectors |
|---|---|---|
| Spike | Single-sample jump | Rolling median/MAD (Hampel), rate-of-change (QARTOD spike test), Kalman innovation |
| Stuck/flatline | Zero variance over N samples | Rolling variance or run-length of identical values (QARTOD flat-line), matrix profile discord less useful |
| Drift | Slow monotonic offset | CUSUM, Page-Hinkley, EWMA on residual vs. a redundant sensor (e.g., TSG vs. intake temp, dual GPS), PCA SPE contribution |
| Bias/step offset | Abrupt level change | CUSUM, BOCPD, PELT (retrospective), cross-sensor PCA SPE |
| Noise increase | Variance change | BOCPD with variance model, rolling variance ratio, ruptures "normal" cost (mean+variance) |
| Dropout | Missing records/gaps | Timestamp gap checks per instrument (deterministic, no ML) |
| Timing/clock offset | Lag between correlated channels | Cross-correlation lag tracking vs. GPS/NTP reference, compare instrument timestamp to logger receive time |
| GPS jump | Implied speed impossible | Kinematic gate (implied speed/acceleration vs. vessel limits), Kalman innovation with heading/speed log |
| Pattern anomaly (e.g., pump cycling) | Unusual subsequence shape | Matrix profile discords (`stumpi` left profile) |

### Gaps
- I did not open the IOOS QARTOD manuals this session. The QARTOD test names (gross range, spike, rate of change, flat line, attenuated signal, multivariate) are background knowledge.
- I found no quantitative published study mapping detector to fault type on ship underway data.

## 4. Ocean/met-specific applications and results

### Takeaway
The published ocean ML-QC work is small-scale: one buoy or one ship, few labeled anomalies, often unreleased data, and authors comparing against weak baselines. The results are encouraging but not proven at fleet scale. I found no peer-reviewed evaluation of ML anomaly detection inside a ship data-acquisition system such as OpenRVDAS.

### Cited Findings
- Song et al. 2025 (Frontiers in Marine Science) used a Transformer-encoder + BiLSTM forecaster with residual > K sigma (K = 2 to 5) flagging, plus imputation and stuck-value correction, on buoy 0199 near Qingdao. Per-variable F1: air temperature 90.1%, water temperature 81.6%, wind 84.7%, pressure 86.8%. Overall F1 was 85.8%, compared with STL-LSTM 84.5%, CNN-BiGRU-Attention 82.6% and BiLSTM alone 80.2%. Robustness was tested only through regression R2 on two other buoys (0.862, 0.858). There was no comparison against QARTOD or manual QC. — [Song et al. 2025](https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2025.1528587/full)
- Kang, Kim and Lim 2024 (JMSE) used 1,414 CTD temperature profiles from 54 R/V Isabu voyages (2017 to 2023), 196 of them abnormal, labeled manually. Results:
  - Supervised MLP-2 + SMOTE reached F1 0.882, AUROC 0.912.
  - MLP-1 without oversampling reached F1 0.869.
  - The per-depth IQR baseline reached F1 0.168.
  - One-class SVM reached F1 about 0.20 to 0.22, with AUROC at or below about 0.5.
  - Oversampling did not reliably help.
  - Data were not released. — [Kang et al. 2024](https://www.mdpi.com/2077-1312/12/5/807)
- An Ocean Networks Canada / OOI facilities-board update deck exists (May 2025) and an AGU OSM 2020 abstract on ML QC of oceanographic data exists, but I could not open their content this session. — [ONC update to OOI FB (PDF)](https://ooifb.org/wp-content/uploads/2025/07/MP_2025-05-06-ONC-Update-OOI-DSC.pdf); [AGU OSM20 abstract (redirects)](https://agu.confex.com/agu/osm20/preliminaryview.cgi/Paper655672.html)

### Inferences
- Both ocean studies are evidence that supervised or forecast-residual models beat naive single-variable statistics when labeled anomalies exist. Neither compared against PCA-SPE, robust MAD/Hampel or QARTOD, so the honest-baseline question is still open for ocean data.
- The Isabu paper shows that unsupervised one-class methods did poorly on profile data while a small supervised MLP did well. This suggests that a modest labeled set from past cruise QC flags is worth more than a more complex unsupervised model **[inference]**.

### Gaps
- I did not retrieve JTECH or IEEE OCEANS papers on OOI, NDBC or ONC automated fault detection. The NDBC real-time QC system and the OOI QARTOD implementation are background knowledge only.
- I found no published OpenRVDAS deployment of statistical or ML anomaly detection.

## 5. Operational issues: ship context, regime-awareness, labels, alarm fatigue, OpenRVDAS integration

### Takeaway
The dominant real-world failure mode is false alarms from legitimate context changes, not missed detections: port vs. underway, on station, heavy weather, intake shut off. OpenRVDAS already has cruise modes, a Cached Data Server, derived-data transforms with window statistics, Sealog event writers and InfluxDB/Grafana alerting. These are the natural hooks for regime-conditioned detectors.

### Cited Findings
- OpenRVDAS loggers are reader -> transform -> writer chains. The recommended derived-data pattern is `CachedDataReader` -> transforms -> `CachedDataWriter`, reading and writing the Cached Data Server. `DerivedDataTransform` is the base class (e.g., `TrueWindsTransform`). `InterpolationTransform` gained "medians, weighted averages, and window statistics for quality control" in v2.7.0. — [OpenRVDAS derived data docs](https://davidpablocohn.github.io/openrvdas-docs/derived_data/)
- In the Nov 2025 RVTEC material, OpenRVDAS lists "Perform basic quality checks and raise alarms" as a core capability. The material also describes:
  - A Logger Manager with cruise modes (port, EEZ, underway).
  - A `GeofenceTransform` that switches modes at EEZ boundaries.
  - `SealogWriter`/`SealogReader` that record threshold events and trigger state changes ("still new").
  - Writers for TimescaleDB, Redis and Postgres/CORIOLIX.
  - InfluxDB Tasks that write `qa_alerts`, such as heading outside 0 to 360, for display in Grafana.
  - All QC described is rule-based; there is no statistical or ML anomaly detection. — [Cohn, RVTEC Nov 2025 OpenRVDAS/CORIOLIX (PDF)](https://www.unols.org/sites/default/files/2025-12/202511rvtec_cohn_david_openrvdas_coriolix_1.pdf); [RVTEC 2024 OpenRVDAS (PDF)](https://unols.org/sites/default/files/2024-11/202410rvt_openrvdas.pdf)
- Telemanom (NASA) emphasizes that even low false-positive rates overwhelm reviewers, and that thresholds with z < 2 produced too many false positives. Its fix is pruning plus per-channel minimum scores learned from operator-confirmed false positives, a simple human-in-the-loop feedback mechanism. — [Hundman et al.](https://ar5iv.arxiv.org/html/1802.04431)
- Sarfraz et al. note that most published methods choose the best F1 threshold on the test set, which is not available operationally. — [Sarfraz et al. 2024](https://arxiv.org/html/2405.02678v3)

### Inferences
- **Regime-aware design:** use the Logger Manager cruise mode, plus derived context signals (speed over ground, on-station flag, intake flow/pump status, sea state from IMU or wind), as a conditioning variable. Fit separate baselines (separate PCA models or MAD windows) per regime, or suppress specific detectors per regime. A thermosalinograph flow-off state, for example, should mute TSG anomaly alarms and raise a single "intake off" status instead **[inference]**.
- **Alarm fatigue mitigation:**
  - Use a multi-sample persistence requirement.
  - Use hysteresis.
  - Rate-limit per channel.
  - Group alarms by instrument.
  - Log alarms to Sealog as events and record watchstander dispositions (true fault / benign / context) to build labels.
  - Feed confirmed false positives back into per-channel thresholds, as Telemanom does with s_min.
- The alarm-fatigue literature (e.g., ISA-18.2 / EEMUA 191 process-industry alarm management, clinical alarm fatigue studies) is **[background, not verified this session]**.
- **OpenRVDAS integration sketch:**
  1. Implement a custom transform with per-field online state: rolling MAD/Hampel, flat-line counter, CUSUM/Page-Hinkley, kinematic GPS gate, and a timestamp gap/lag check.
  2. Have the transform emit `<field>_qc` flag fields and anomaly scores into the Cached Data Server via a derived-data logger.
  3. Run a second logger that subscribes to many fields and computes a pre-fitted PCA T2/SPE with per-variable contributions every N seconds (NumPy only, microseconds per record at dozens of channels).
  4. Run offline or periodic jobs (ruptures PELT, STUMPY, deep models) against TimescaleDB/InfluxDB rather than inline, so that heavy dependencies stay out of the acquisition path.
  5. Route alerts through the existing Sealog writer and Grafana `qa_alerts` path. **[inference based on documented architecture; the custom-transform API details were not documented on the pages opened]**
- **Compute:** all classical methods run comfortably on the ship's logger host at 1 Hz x dozens of channels. `stumpi`, at roughly 450 points/s per stream on modest hardware, is feasible for a handful of key channels but not for every field without care. Deep models need offline training but cheap inference **[inference]**.

### Gaps
- I did not open published studies quantifying false-alarm rates of automated QC on research vessels, or alarm-fatigue studies in marine operations.
- The OpenRVDAS transform API (`transform(record)` signature, DASRecord structure) was not documented on the pages I could open. The main oceandatatools.org transforms page failed to load.

## 6. Libraries: license and maturity

### Takeaway
For a long-lived open-source ship system, prefer permissively licensed, actively maintained, lightweight libraries: ruptures, STUMPY, river, PyOD, or plain NumPy/SciPy. Avoid depending on Merlion (archived March 2026) and alibi-detect (now Business Source License). Kats, Orion and darts need verification before adoption.

### Cited Findings
- **Merlion (Salesforce):** BSD-3-Clause. Supports univariate and multivariate anomaly detection and change-point detection (added in 2.0), with streaming-mode evaluation that updates state per point. The repository was archived by the owner on March 11, 2026 and is read-only. — [Merlion GitHub](https://github.com/salesforce/Merlion)
- **alibi-detect (Seldon):** changed license from Apache to Business Source License 1.1 in v0.11.5 (2024-01-22). Latest changelog entry is v0.13.0 (2025-12-11, Python 3.12 support). — [alibi-detect CHANGELOG](https://www.github.com/SeldonIO/alibi-detect/blob/master/CHANGELOG.md); [Seldon licensing FAQ](https://seldon.io/resources/licensing-faqs)
- **Telemanom:** Apache 2.0, source-only, no releases, about 1.2k stars and 15 open issues. — [telemanom GitHub](https://www.github.com/khundman/telemanom)
- **STUMPY:** has a documented streaming API (`stumpi`) with egress and a left-only profile. — [STUMPY docs](https://stumpy.readthedocs.io/en/stable/Tutorial_Matrix_Profiles_For_Streaming_Data.html)
- **ruptures:** reference implementation accompanying the Truong et al. review of offline change-point methods. — [arXiv 1801.00718](https://arxiv.org/abs/1801.00718?context=cs)
- **TSB-AD:** pip-installable benchmark suite with 40 algorithms, useful for evaluating candidates on vessel data with VUS-PR. — [PyPI TSB-AD](https://pypi.org/project/TSB-AD/); [TSB-AD site](https://thedatumorg.github.io/TSB-AD)

### Inferences **[background, not verified this session; check each repo before citing]**
| Library | License (believed) | Streaming? | Notes |
|---|---|---|---|
| PyOD | BSD-2-Clause | Mostly batch fit / fast score | Broad detector zoo (IForest, PCA, KNN, ECOD, COPOD, AE). Mature. |
| ruptures | BSD-2-Clause | Offline | PELT, BinSeg, BottomUp, Window, KernelCPD. Mature. |
| river | BSD-3-Clause | Native online | HalfSpaceTrees, online stats. Includes drift detectors such as ADWIN, Page-Hinkley and KSWIN. |
| STUMPY | BSD-3-Clause | `stumpi` incremental | NumFOCUS-affiliated. |
| Kats (Meta) | MIT | CUSUM, BOCPD and other detectors | Maintenance activity uncertain. |
| Orion (MIT DAI Lab) | MIT | Batch pipelines | Includes TadGAN, LSTM-DT (Telemanom-style) and AER. |
| darts | Apache-2.0 | Forecast-residual anomaly scorers | Active. |
| Merlion | BSD-3-Clause (verified) | Streaming eval | Archived Mar 2026 (verified). |
| alibi-detect | BSL 1.1 (verified) | Online drift detectors | Non-open-source license since 2024 (verified). |

### Gaps
- I did not open the PyOD, river, Kats, Orion or darts GitHub pages this session. Their licenses and maintenance status in the table above need verification.
- I did not verify whether Kats is still maintained in 2026.
