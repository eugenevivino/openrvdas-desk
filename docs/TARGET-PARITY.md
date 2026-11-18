# Target parity: CORIOLIX + MetAcq + our own plan

One scorecard of everything OpenRVDAS plus DeepSignal must do. Eugene's goal
(2026-11-18): do at least most of what CORIOLIX does, plus what MetAcq does,
plus everything already planned, but better, easier to set up, and fully open
source.

Written 2026-11-18 by the parity thread. Tables and percentages are generated
by `tools/target-parity/gen.py` from its row data and
`tools/target-parity/template.md`, so the arithmetic is reproducible; the
judgement is in each row's status and value scores. Edit the rows there, then
run `python3 tools/target-parity/gen.py build` from the desk root. Do not
hand-edit the tables below.

## 1. Headline

| Scope | Rows | Core today | Core + built DeepSignal today | With briefed and planned work | With this doc's drafts |
|---|---|---|---|---|---|
| CORIOLIX | 43 | 38% | 38% | 71% | 98% |
| MetAcq | 44 | 52% | 55% | 75% | 98% |
| Combined | 87 | 45% | 47% | 73% | 98% |
| Ecosystem (OceanDataTools) | 10 | 40% | 40% | 90% | 100% |

- **Today** means code that runs now: OpenRVDAS core plus DeepSignal modules
  that are built and tested (only vector wind, #4).
- **Planned** counts every row an existing IDEAS row or brief would close,
  whatever its status. **+Drafts** adds the unnumbered draft ideas in
  section 7.
- Scoring: Have = 1, Partial = 0.5, Gap = 0. Every row weighs the same; the
  value ranking in section 4 is where importance shows up.
- Measurable goal proposed: **"most of CORIOLIX" = at least 80% of CORIOLIX
  rows fully covered (score 1), and every gap valued 12 or more closed.**
  Fully covered today: 6 of 43 (14%). With briefed and planned work (including
  #104-#137): 24 of 43 (56%) scored fully, 41 of 43 (95%) once every draft in
  section 7 lands. C43 (easy EEZ mode, #137) added 2026-11-18 08:30Z. Re-scored 2026-11-18 07:45Z after finding that fork `dev` already has
  round-robin polling, per-file log headers and CDS HTTP routes.

What this says plainly: OpenRVDAS core already owns acquisition, parsing,
logging, derived values and data push (the bottom of both stacks). Everything
people see and touch above that is the gap: QC flags, the sensor registry,
displays, data delivery, alerts. That is DeepSignal's job, and the console,
QARTOD and instrument-history briefs already point at most of it.

## 2. Sources

CORIOLIX has no public source code or license that we found. Its public
documentation is MIT-adjacent prose in
[R-DESC/CORIOLIX_docs](https://github.com/R-DESC/CORIOLIX_docs) (commit
1398bb8, 2026-09-29), plus UNOLS RVTEC talks and the Sikuliaq public site.
Public CORIOLIX code we found: example notebooks
([R-DESC/CORIOLIX_notebooks](https://github.com/R-DESC/CORIOLIX_notebooks),
MIT) and a regex library (R-DESC/sensor_regex). The 2022 talk planned to "open
the CORIOLIX GitHub repo by Taani delivery (September 2023)"; we found no such
repo.

| Key | Source |
|---|---|
| `cx:<page>` | CORIOLIX_docs page, linked in each row |
| RVTEC 2025 | [CORIOLIX part 2, Nov 2025](https://www.unols.org/sites/default/files/2025-12/202511rvtec_romsos_chris_openrvdas_coriolix_2.pdf) (slide titles, no numbers) |
| RVTEC 2023 | [CORIOLIX, Oct 2023](https://www.unols.org/sites/default/files/2023-11/202310rvt_apxxxvi.pdf) |
| RVTEC 2022 | [CORIOLIX, Nov 2022](https://www.unols.org/sites/default/files/202211rvt_apXXIV.pdf) |
| RVTEC 2020 | [OpenRVDAS to CORIOLIX integration](https://www.unols.org/sites/default/files/202010rvt_ap09.pdf) |
| RVTEC 2019 | [CORIOLIX, 2019](https://www.unols.org/sites/default/files/201910rvt_ap27.pdf) |
| Sikuliaq site | [coriolix.sikuliaq.alaska.edu](https://coriolix.sikuliaq.alaska.edu) |
| MetAcq 2.15 | [MetAcq Operator's Manual Rev 2.15, Aug 2019](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) |
| MetAcq 2.12 | [Rev 2.12, Apr 2014](https://calcofi.org/downloads/underway/2017/1711SR/met/docs/MetAcq.pdf) (calibration method list) |
| MetSpecs | [MetSpecs Rev 1.18](https://calcofi.org/downloads/underway/2021/2107SR/met/docs/MetSpecs.pdf) (sensor list) |
| OpenVDM #408 | [$WICOR parser issue](https://github.com/OceanDataTools/openvdm/issues/408) |

MetAcq rows come from the desk's MetAcq gap map
(`research/README.md` links it), which read the manual mirrors above. Its
sections 10, 11 and Appendix A were read only in summary; the $WICOR writer
brief must read them first (D-METACQ1). OpenRVDAS status was checked against
fork `master` 3f3d0c3 (v2.7.2).

Status words in the DeepSignal column: **Built** (code and tests exist),
**Building** (brief plus branch, work running), **Briefed** (brief written),
**Designed** (IDEAS row marked DESIGNED or a design doc), **Idea** (IDEAS row
PROPOSED), **none**.

## 3. The matrix

### 3a. CORIOLIX (43 rows)

| # | Capability | Source | OpenRVDAS core today | DeepSignal | Today | Planned | +Drafts | Home |
|---|---|---|---|---|---|---|---|---|
| C1 | Live plots per sensor class (flowthrough, met, nav, sonar, CTD), zoom, pan, save PNG | [PAGES_plots](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/PAGES_plots.md), [Sikuliaq site](https://coriolix.sikuliaq.alaska.edu) | Partial: Highcharts/D3 widgets deprecated (`display/README.md`); Grafana via `GrafanaLiveWriter`, installed separately | Console charts (#12-14) (Building) | 0.5 | 1 | 1 | DS |
| C2 | Custom and combination plots (any range, up to 4 parameters, saved per user) | [PAGES_plots](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/PAGES_plots.md) | Partial: Grafana can, but by hand | Console page files (D-CONSOLE1) (Designed) | 0.5 | 1 | 1 | DS |
| C3 | Sensor/parameter status board, color per parameter, grouped by class | [PAGES_status](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/PAGES_status.md), [Sikuliaq site](https://coriolix.sikuliaq.alaska.edu) | Partial: Django shows per-logger state, not per-parameter freshness | Console health (#12) (Building) | 0.5 | 1 | 1 | DS |
| C4 | System (host) health page | [PAGES_status](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/PAGES_status.md) | Partial: supervisord status only | none | 0.5 | 0.5 | 1 | DS |
| C5 | Automated QC flag on every value (global limits), flag kept with value | [Sikuliaq site](https://coriolix.sikuliaq.alaska.edu), [RVTEC 2025](https://www.unols.org/sites/default/files/2025-12/202511rvtec_romsos_chris_openrvdas_coriolix_2.pdf), [export_data](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/export_data.md) | Partial: `QCFilterTransform` drops or warns; no flag travels with the value | QARTOD flags (#8) (Briefed) | 0.5 | 1 | 1 | DS |
| C6 | One-minute bins with statistics (mean, circular mean, std, min, max, median, count, spot; QC-filtered; composite flag) | [export_data](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/export_data.md), [RVTEC 2023](https://www.unols.org/sites/default/files/2023-11/202310rvt_apxxxvi.pdf) | Partial: `SubsampleTransform` boxcar; `contrib/logger_templates/averaging_logger_template.yaml` | Vector wind (#4) built; binned downloads (#16) (Designed) | 0.5 | 1 | 1 | DS |
| C7 | Download UI: high-res, binned, binned+stats, native raw; by date, parameter, resolution; CSV, TSV, JSON, GeoJSON, MAT, netCDF, OPeNDAP; zip plus metadata file | [export_data](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/export_data.md), [PAGES_data](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/PAGES_data.md), [Sikuliaq site](https://coriolix.sikuliaq.alaska.edu) | Gap: none | Binned downloads (#16) (Designed) | 0 | 1 | 1 | DS |
| C8 | REST API for data and metadata | [API_endpoints](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/API_endpoints.md), [Sikuliaq site](https://coriolix.sikuliaq.alaska.edu) | Partial: CachedDataServer HTTP `/fields` and `/latest/` (fork `dev`); no history or metadata routes | REST API (#105) (Briefed) | 0.5 | 1 | 1 | DS |
| C9 | ERDDAP server (subset, format translation, OGC) | [TS_erddap_data_download](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/TS_erddap_data_download.md), [RVTEC 2025](https://www.unols.org/sites/default/files/2025-12/202511rvtec_romsos_chris_openrvdas_coriolix_2.pdf), [RVTEC 2020](https://www.unols.org/sites/default/files/202010rvt_ap09.pdf) | Gap: none | none | 0 | 0 | 1 | DS |
| C10 | Pushed real-time data services (UDP, MQTT, websockets) | [HT_data_access](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/HT_data_access.md), [RVTEC 2025](https://www.unols.org/sites/default/files/2025-12/202511rvtec_romsos_chris_openrvdas_coriolix_2.pdf) | Have: `UDPWriter`, `MQTTWriter`, `CachedDataServer` | - | 1 | 1 | 1 | core |
| C11 | Map: track, clickable trackpoints, underway data colored on track, events, cached OSM/GMRT/NOAA ENC basemaps, SST and Chl overlays | [PAGES_map](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/PAGES_map.md), [Sikuliaq site](https://coriolix.sikuliaq.alaska.edu) | Gap: none maintained | Console map (in console plan, no brief) (Idea) | 0 | 0.5 | 1 | DS |
| C12 | Route tools: draw route, distance, time at chosen speed | [PAGES_map](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/PAGES_map.md) | Gap: none | none | 0 | 0 | 1 | DS |
| C13 | Cruise event log (casts, stations) with standard vocabularies, shown on map | [PAGES_tools](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/PAGES_tools.md), [Sikuliaq site](https://coriolix.sikuliaq.alaska.edu), [RVTEC 2025](https://www.unols.org/sites/default/files/2025-12/202511rvtec_romsos_chris_openrvdas_coriolix_2.pdf) | Partial: Sealog reader/writer integration (Sealog is a separate app) | Event log (#15) (Designed) | 0.5 | 1 | 1 | DS |
| C14 | Cruise list and metadata (dates, ports, participants); schedule import | [PAGES_tools](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/PAGES_tools.md), [RVTEC 2025](https://www.unols.org/sites/default/files/2025-12/202511rvtec_romsos_chris_openrvdas_coriolix_2.pdf) | Partial: cruise definition YAML holds id and dates | none | 0.5 | 0.5 | 1 | DS |
| C15 | Sensor registry: sensors and parameters, enable/disable, tech-editable, vendor list | [PAGES_sensors](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/PAGES_sensors.md), [Sikuliaq site](https://coriolix.sikuliaq.alaska.edu), [RVTEC 2025](https://www.unols.org/sites/default/files/2025-12/202511rvtec_romsos_chris_openrvdas_coriolix_2.pdf) | Partial: device definition YAMLs, no UI, no registry | Instrument history (#52) (Briefed) | 0.5 | 1 | 1 | DS |
| C16 | Sensor logs: history, configuration, issues, calibration dates | [Sikuliaq site](https://coriolix.sikuliaq.alaska.edu), [RVTEC 2025](https://www.unols.org/sites/default/files/2025-12/202511rvtec_romsos_chris_openrvdas_coriolix_2.pdf) | Gap: none | Instrument history (#52) (Briefed) | 0 | 1 | 1 | DS |
| C17 | Calibration files per instrument and calibration transforms (SBE 3/4/9/38/43/45, ECO, SUNA, QSR ...) | [HT_sensor_onboard_step3](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/HT_sensor_onboard_step3.md), [RVTEC 2025](https://www.unols.org/sites/default/files/2025-12/202511rvtec_romsos_chris_openrvdas_coriolix_2.pdf) | Partial: `ComputedFieldsTransform` expressions; no coefficient files per serial | Calibration records (#7), #52 (Designed) | 0.5 | 1 | 1 | DS |
| C18 | Primary-parameter rules: which sensor is primary per parameter, by model and location | [PAGES_sensors](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/PAGES_sensors.md), [RVTEC 2025](https://www.unols.org/sites/default/files/2025-12/202511rvtec_romsos_chris_openrvdas_coriolix_2.pdf) | Gap: none | Two-anemometer consensus (#51) is one case (Idea) | 0 | 0.5 | 1 | core |
| C19 | Post-processing source assignment (which GPS feeds salinity, by location) | [PAGES_sensors](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/PAGES_sensors.md) | Partial: chosen by hand in config | none | 0.5 | 0.5 | 1 | core |
| C20 | Derived products (true wind, SI units) | [RVTEC 2022](https://www.unols.org/sites/default/files/202211rvt_apXXIV.pdf) | Have: `TrueWindsTransform`, `ConvertFieldsTransform` | - | 1 | 1 | 1 | core |
| C21 | CTD package configuration and CTD plot page | [HT_CTD_Configuration](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/HT_CTD_Configuration.md), [PAGES_sensors](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/PAGES_sensors.md) | Gap: none | none | 0 | 0 | 1 | DS |
| C22 | Sensor groups (parent and child sensors shown together) | [PAGES_sensors](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/PAGES_sensors.md) | Gap: none | Console page files (Designed) | 0 | 1 | 1 | DS |
| C23 | Flowthrough valve schedule (open/closed content and durations) tied to the data | [PAGES_settings](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/PAGES_settings.md) | Gap: none | none | 0 | 0 | 1 | DS |
| C24 | Alerts: threshold (2 parameters), proximity (stations, ports), temporal (cal due, warranty), global, subscriptions | [HT_account](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/HT_account.md), [Sikuliaq site](https://coriolix.sikuliaq.alaska.edu), [RVTEC 2019](https://www.unols.org/sites/default/files/201910rvt_ap27.pdf), [RVTEC 2022](https://www.unols.org/sites/default/files/202211rvt_apXXIV.pdf) | Partial: `TimeoutReader`/`TimeoutWriter` plus `EmailWriter` cover silence only | State-aware alarms (#9), plain-language alarms (#34) (Designed) | 0.5 | 1 | 1 | DS |
| C25 | Accounts and roles (public, scientist, technician, admin); ship and shore share accounts | [HT_account](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/HT_account.md), [PAGES_settings](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/PAGES_settings.md), [RVTEC 2025](https://www.unols.org/sites/default/files/2025-12/202511rvtec_romsos_chris_openrvdas_coriolix_2.pdf) | Partial: Django login: viewer vs logged-in; FastAPI JWT for the React UI | Console role pages (#14), no role model (Idea) | 0.5 | 0.5 | 1 | DS |
| C26 | Ship-to-shore replication: data under 1 s, metadata both ways, shore mirror with same UI | [Sikuliaq site](https://coriolix.sikuliaq.alaska.edu), [RVTEC 2019](https://www.unols.org/sites/default/files/201910rvt_ap27.pdf), [RVTEC 2022](https://www.unols.org/sites/default/files/202211rvt_apXXIV.pdf), [RVTEC 2023](https://www.unols.org/sites/default/files/2023-11/202310rvt_apxxxvi.pdf) | Partial: network writers can send; no store-and-forward or shore mirror | Sync bulk/live, link profiles, semantic sync (#17-19, #35) (Idea) | 0.5 | 1 | 1 | DS |
| C27 | Data release policy: privacy level, restricted content, EEZ mode | [PAGES_settings](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/PAGES_settings.md) | Partial: `GeofenceTransform` switches modes at EEZ boundaries | none | 0.5 | 0.5 | 1 | DS |
| C28 | Retention settings (raw files, backup, database) | [PAGES_settings](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/PAGES_settings.md) | Partial: files kept forever; no policy | none | 0.5 | 0.5 | 0.5 | core |
| C29 | GUI logger configuration and one-button deploy (writes OpenRVDAS config, updates alerts, ERDDAP, restarts) | [RVTEC 2025](https://www.unols.org/sites/default/files/2025-12/202511rvtec_romsos_chris_openrvdas_coriolix_2.pdf), [RVTEC 2020](https://www.unols.org/sites/default/files/202010rvt_ap09.pdf), [RVTEC 2023](https://www.unols.org/sites/default/files/2023-11/202310rvt_apxxxvi.pdf) | Partial: Django loads a cruise YAML and switches modes; YAML is hand-written | Plug-and-identify (#29) (Idea) | 0.5 | 0.5 | 1 | DS |
| C30 | Sensor onboarding workflow (create sensor, parameters with CF names and limits, cal files, network logger, data logger) | [HT_sensor_onboard](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/HT_sensor_onboard.md), [HT_sensor_onboard_step1](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/HT_sensor_onboard_step1.md), [HT_sensor_onboard_step2](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/HT_sensor_onboard_step2.md) | Gap: edit YAML by hand | Plug-and-identify (#29) (Idea) | 0 | 0.5 | 1 | DS |
| C31 | Regex parsing with a public regex library | [RegExGuide](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/RegExGuide.md), [RVTEC 2025](https://www.unols.org/sites/default/files/2025-12/202511rvtec_romsos_chris_openrvdas_coriolix_2.pdf) | Have: `RegexParseTransform`, `ParseTransform`, `contrib/devices/` | - | 1 | 1 | 1 | core |
| C32 | Standard vocabularies (CF names, SeaVoX L22/L35/EL1/EL2, R2R device types, ICES ship codes, UN/LOCODE) | [PAGES_about](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/PAGES_about.md), [RVTEC 2025](https://www.unols.org/sites/default/files/2025-12/202511rvtec_romsos_chris_openrvdas_coriolix_2.pdf) | Gap: none | Cross-vessel ontology (#103) (Idea) | 0 | 0.5 | 1 | DS |
| C33 | SAMOS daily file (1-min subset) sent from shore | [RVTEC 2023](https://www.unols.org/sites/default/files/2023-11/202310rvt_apxxxvi.pdf) | Gap: none | none (#95 only validates against SAMOS) | 0 | 0 | 1 | DS |
| C34 | End-of-cruise R2R package (raw plus metadata) | [RVTEC 2023](https://www.unols.org/sites/default/files/2023-11/202310rvt_apxxxvi.pdf), [Sikuliaq site](https://coriolix.sikuliaq.alaska.edu), [export_data](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/export_data.md) | Partial: raw logfiles exist; no package | R2R-ready package (#58) (Idea) | 0.5 | 1 | 1 | DS |
| C35 | Documents catalog (manuals, calibration certificates) | [PAGES_documents](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/PAGES_documents.md), [Sikuliaq site](https://coriolix.sikuliaq.alaska.edu) | Gap: none | #52 links cal records (Briefed) | 0 | 0.5 | 1 | DS |
| C36 | Vessel metadata: dimensions, codes, survey monuments and benchmarks | [PAGES_vessel](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/PAGES_vessel.md) | Gap: none | #52 has mount position (Briefed) | 0 | 0.5 | 1 | DS |
| C37 | Public and remote-participant view | [Sikuliaq site](https://coriolix.sikuliaq.alaska.edu) | Partial: Django anonymous viewer | Shore view (#14) (Idea) | 0.5 | 1 | 1 | DS |
| C38 | Raw archive, timestamped, one file per sensor per day; backup | [HT_data_access](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/HT_data_access.md), [RVTEC 2023](https://www.unols.org/sites/default/files/2023-11/202310rvt_apxxxvi.pdf) | Have: `LogfileWriter` | - | 1 | 1 | 1 | core |
| C39 | Time-series database storage | [RVTEC 2025](https://www.unols.org/sites/default/files/2025-12/202511rvtec_romsos_chris_openrvdas_coriolix_2.pdf), [RVTEC 2020](https://www.unols.org/sites/default/files/202010rvt_ap09.pdf) | Have: `DatabaseWriter` (MySQL, PostgreSQL), `InfluxDBWriter` | - | 1 | 1 | 1 | core |
| C40 | Playback of recorded data for development | [RVTEC 2025](https://www.unols.org/sites/default/files/2025-12/202511rvtec_romsos_chris_openrvdas_coriolix_2.pdf) | Have: `LogfileReader`, `simulate_*.py` | - | 1 | 1 | 1 | core |
| C41 | UNOLS planning integration (MFP, MOMS) as metadata source of truth | [RVTEC 2025](https://www.unols.org/sites/default/files/2025-12/202511rvtec_romsos_chris_openrvdas_coriolix_2.pdf), [RVTEC 2022](https://www.unols.org/sites/default/files/202211rvt_apXXIV.pdf) | Gap: none | none | 0 | 0 | 0.5 | DS |
| C42 | Site-wide message banner | [PAGES_settings](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/PAGES_settings.md) | Gap: none | Console core (trivial) (Building) | 0 | 1 | 1 | DS |
| C43 | EEZ mode made easy: automatic detection from position against offline EEZ polygons, pre-alerts, per-instrument log, quarantine or stop from the clearance record, override with reason, audit for the cruise report | [PAGES_settings](https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/PAGES_settings.md) | Partial: `GeofenceTransform` switches the whole cruise mode on entering and leaving one GML boundary; needs geopandas and shapely; buffer in degrees; no pre-alert, position-loss rule, override or audit. CORIOLIX itself is a manual on/off toggle | EEZ mode (#137) (Briefed) | 0.5 | 1 | 1 | DS |

### 3b. MetAcq (43 rows)

| # | Capability | Source | OpenRVDAS core today | DeepSignal | Today | Planned | +Drafts | Home |
|---|---|---|---|---|---|---|---|---|
| M1 | RS232/RS422 serial input | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Have: `SerialReader` | - | 1 | 1 | 1 | core |
| M2 | RS485 multidrop polling, per-address round robin with timeouts | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Have: `PolledSerialReader` `pre_read_cmd` dict: round-robin polling with per-command timeout (fork `dev`) | - | 1 | 1 | 1 | core |
| M3 | ADAM/DGH analog-to-RS485 modules (ASCII protocol) | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Partial: `ModbusSerialReader` (ADAM-4000 ASCII is not Modbus) | none | 0.5 | 0.5 | 1 | core |
| M4 | NI DAQ / USB analog input | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Gap: none | none | 0 | 0 | 0 | core |
| M5 | UDP input, NMEA and non-NMEA | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Have: `UDPReader`, `ParseNMEATransform` | - | 1 | 1 | 1 | core |
| M6 | NMEA sentence set (GGA ... PASHR, PKEL99) | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Have: NMEA parser plus `contrib/devices` (verify PASHR, PKEL99) | - | 1 | 1 | 1 | core |
| M7 | Device definitions for the MetSpecs sensor list (RM Young, Vaisala, Eppley, SBE45/43, QSR, LCI90) | [MetSpecs](https://calcofi.org/downloads/underway/2021/2107SR/met/docs/MetSpecs.pdf) | Partial: some devices in `contrib/devices` | none | 0.5 | 0.5 | 1 | core |
| M8 | GPS failover (write one GPS, fail over to next) | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Gap: none | none | 0 | 0 | 1 | core |
| M9 | Clock sync to NTP or GPS | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Have: host chrony/NTP | Clock forensics (#31) (Idea) | 1 | 1 | 1 | core |
| M10 | Calibration chain, 45 named methods (polynomial, thermistor, RTD, SBE T/C, Eppley, SBE43, optode) | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf), [MetAcq 2.12](https://calcofi.org/downloads/underway/2017/1711SR/met/docs/MetAcq.pdf) | Partial: expressions only; no named methods or coefficient files | Calibration records (#7) (Designed) | 0.5 | 1 | 1 | DS |
| M11 | Sensor metadata per module (make, model, serial, cal date, lab, location) | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Gap: none | Instrument history (#52) (Briefed) | 0 | 1 | 1 | DS |
| M12 | True wind | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Have: `TrueWindsTransform` | - | 1 | 1 | 1 | core |
| M13 | Dew point, wet bulb, sea-level pressure | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Partial: hand-written expressions | none | 0.5 | 0.5 | 1 | core |
| M14 | Salinity, sigma-t, sound velocity | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Partial: expressions; `gsw` hook | none | 0.5 | 0.5 | 1 | core |
| M15 | Antenna lever-arm correction of position | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Gap: none | none | 0 | 0 | 1 | core |
| M16 | Waypoint ETA, EDA, time to go, bearing; off-course warning | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Gap: only `GeofenceTransform` in/out | none | 0 | 0 | 1 | DS |
| M17 | Boxcar averaging per sensor | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Have: `SubsampleTransform` | - | 1 | 1 | 1 | core |
| M18 | Vector averaging of wind direction | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Gap: none in core | Vector wind (#4) (Built) | 1 | 1 | 1 | DS |
| M19 | Range checks with per-value quality digit carried downstream | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Partial: drop or warn only | QARTOD flags (#8) (Briefed) | 0.5 | 1 | 1 | DS |
| M20 | Parallel uncorrected and corrected streams | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Have: two chains in one config | Correction ledger (#56) goes further (Briefed) | 1 | 1 | 1 | core |
| M21 | Daily files rolling at 0000Z | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Have: `LogfileWriter` | - | 1 | 1 | 1 | core |
| M22 | .MET/.UCR column files with headers on each new file | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Have: `FormatTransform` plus `LogfileWriter` `header`/`header_file` on each new file | - | 1 | 1 | 1 | core |
| M23 | .COR/.UNC $WICOR/$WIUNC files with quality digits | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf), [OpenVDM #408](https://github.com/OceanDataTools/openvdm/issues/408) | Gap: none | $WICOR writer (#6) (Designed) | 0 | 1 | 1 | DS |
| M24 | Configuration copied next to each day of data | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Partial: `server/config_snapshot.py` (verify per day) | Provenance (#32) (Idea) | 0.5 | 1 | 1 | core |
| M25 | Daily operations log | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Have: logging | - | 1 | 1 | 1 | core |
| M26 | SAMOS daily exchange file | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Gap: none | none | 0 | 0 | 1 | DS |
| M27 | Playback and regenerate corrected files from raw | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Have: `LogfileReader` plus same chain | Time-travel replay (#33) (Idea) | 1 | 1 | 1 | core |
| M28 | Emulation mode with "emulated" flag | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Partial: `simulate_*.py`, no flag in output | none | 0.5 | 0.5 | 1 | core |
| M29 | $WICOR UDP broadcast every second | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf), [OpenVDM #408](https://github.com/OceanDataTools/openvdm/issues/408) | Partial: `UDPWriter`, no formatter | $WICOR writer (#6) (Designed) | 0.5 | 1 | 1 | DS |
| M30 | Serial repeat of nav to MRU, Seatel, multibeam | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Have: `SerialWriter`, `UDPWriter` | - | 1 | 1 | 1 | core |
| M31 | Sound velocity to multibeam (per-target format) | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Partial: format strings by hand | none | 0.5 | 0.5 | 1 | core |
| M32 | User-defined outputs (printf format, leader, CRC, NMEA checksum) | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Have: `FormatTransform`, `NMEAChecksumTransform` | - | 1 | 1 | 1 | core |
| M33 | Winch data to signboards | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Gap: none | Scoreboard writer (#5) (Designed) | 0 | 1 | 1 | DS |
| M34 | Email products: SAMOS zip, OPSUM hourly, PCO2, SHIPTRACK, NOAA hourly ship weather | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Partial: `EmailWriter`, formats missing | none | 0.5 | 0.5 | 1 | DS |
| M35 | Cascade (second PC mirrors primary) | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Have: `UDPReader`, `CachedDataServer` | - | 1 | 1 | 1 | core |
| M36 | Strip charts with history scroll and per-plot scale | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Partial: deprecated widgets; Grafana | Console charts (Building) | 0.5 | 1 | 1 | DS |
| M37 | Tabulated big numbers plus position | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Partial: `text_widget.js` (deprecated) | Console core (Building) | 0.5 | 1 | 1 | DS |
| M38 | MetBig: huge met values for the bridge, night-safe | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Gap: none | Console bridge (#13) (Building) | 0 | 1 | 1 | DS |
| M39 | Winch screen: wire out, speed, tension, CTD depth, altimeter | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Gap: none | none | 0 | 0 | 1 | DS |
| M40 | GPS and waypoint screen (ETA, TTG, bearing) | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Gap: none | none | 0 | 0 | 1 | DS |
| M41 | Diagnostic screen: raw strings per port, INOP per value | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Partial: Django logger stderr view | Console health (#12) (Building) | 0.5 | 1 | 1 | DS |
| M42 | Status bar: scans per second, current file, silent sensors (CHK MOD) | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Partial: logger status, no per-sensor silence list | Console health (#12) (Building) | 0.5 | 1 | 1 | DS |
| M43 | Web snapshots (PNG every 10 s) for shore and slow links | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Gap: none | Shore view (#14), link profiles (#19) (Idea) | 0 | 0.5 | 1 | DS |
| M44 | Sensor initialization over the wire: startup and setup commands, reply checks, re-init after power loss or reconnect, audit log of what was sent | [MetAcq 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Partial: `PolledSerialReader` `start_cmd` (sent once at open, reply not checked, not resent after a power cycle), `stop_cmd`, `pre_read_cmd`, `__PAUSE__`; serial only. MetAcq 2.15 documents only per-module poll commands (CMD, CMD2, CMD3 in the .ACQ file); init is silent in its manual | Instrument init profiles (#130) (Briefed) | 0.5 | 1 | 1 | DS |

### 3b2. OceanDataTools ecosystem (10 rows)

How DeepSignal fits OpenVDM, Sealog and the Grafana tooling. Design: `docs/ECOSYSTEM.md`. The Combined
headline stays CORIOLIX plus MetAcq so it is comparable over time; this group is scored on its own line.

| # | Capability | Source | OpenRVDAS core today | DeepSignal | Today | Planned | +Drafts | Home |
|---|---|---|---|---|---|---|---|---|
| E1 | Raw logs land in the OpenVDM cruise package and plot on its Data Dashboard | [OpenVDM 2.17](https://github.com/OceanDataTools/openvdm), [OpenVDM docs](https://www.oceandatatools.org/openvdm-docs/) | Have: OpenVDM collection system transfer copies OpenRVDAS log files; OpenVDM ships `openrvdas_plugin.py.dist` with GGA, met, SSV, TSG and true wind parsers | - | 1 | 1 | 1 | core |
| E2 | DeepSignal quality flags, freshness and products in the OpenVDM package and Data Dashboard (qualityTests, stats) | [OpenVDM 2.17](https://github.com/OceanDataTools/openvdm), [OpenVDM docs](https://www.oceandatatools.org/openvdm-docs/) | Partial: OpenVDM parsers count bad rows only; no QC flags | OpenVDM bridge (#131) (Briefed) | 0.5 | 1 | 1 | DS |
| E3 | One cruise and lowering identity across OpenRVDAS, OpenVDM, Sealog and DeepSignal | [OpenVDM 2.17](https://github.com/OceanDataTools/openvdm), [Sealog server 2.4.9](https://github.com/OceanDataTools/sealog-server) | Partial: Sealog creates its cruise from OpenVDM (`sealog_create_cruise_from_openvdm.py.dist`); the OpenRVDAS cruise definition is separate | Cruise context (#132) (Briefed) | 0.5 | 1 | 1 | DS |
| E4 | Sealog events from data-system alerts, QC changes, flow state and instrument init results | [Sealog server 2.4.9](https://github.com/OceanDataTools/sealog-server) | Partial: core `SealogWriter` maps records to events with a field map; nothing produces quality events | Sealog bridge (#133) (Briefed) | 0.5 | 1 | 1 | DS |
| E5 | Every Sealog event carries the quality state of the sensors at that moment (aux data) | [Sealog server 2.4.9](https://github.com/OceanDataTools/sealog-server) | Partial: Sealog inserters attach raw values from InfluxDB, CORIOLIX or OpenRVDAS, never their quality | Sealog bridge (#133) (Briefed) | 0.5 | 1 | 1 | DS |
| E6 | Grafana dashboards for QC flags, freshness and system health, provisioned from the cruise definition | [Grafana compass panel](https://github.com/OceanDataTools/grafana-compass-panel) | Partial: `InfluxDBWriter`, `GrafanaLiveWriter`, compass and attitude panels; dashboards built by hand, no quality views | Grafana quality pack (#134) (Briefed) | 0.5 | 1 | 1 | DS |
| E7 | Lossless compressed archive of closed raw logs (zstd or xz) with checksum manifest, byte-reproducible | [OpenVDM 2.17](https://github.com/OceanDataTools/openvdm) | Gap: plain text logs only; OpenVDM keeps an MD5 manifest but compresses nothing | Archive and compression (#135) (Briefed) | 0 | 1 | 1 | DS |
| E8 | Science exports in NetCDF4/CF with chunked compression (Parquet if cheap) | [OpenVDM docs](https://www.oceandatatools.org/openvdm-docs/) | Gap: none in core | ERDDAP (#104) serves netCDF on request; offline export in #135 phase 2 (Briefed) | 0 | 0.5 | 1 | DS |
| E9 | Compressed, prioritized ship-to-shore transfer over satellite | [OpenVDM docs](https://www.oceandatatools.org/openvdm-docs/) | Partial: OpenVDM ship-to-shore has priorities 1 to 5 and a bandwidth cap; no compression found in its transfer code | Shore bundles (#135) plus snapshot (#123) (Briefed) | 0.5 | 1 | 1 | DS |
| E10 | Verdicts from OceanDataTools QA tools (nav QA, CTD QA, winch wire logs) shown in the console and Sealog | [nav-qa-processing](https://github.com/OceanDataTools/nav-qa-processing), [sbe-qa-processing](https://github.com/OceanDataTools/sbe-qa-processing), [winch-data-processing](https://github.com/OceanDataTools/winch-data-processing) | Gap: separate tools, run by hand or as OpenVDM post hooks | QA tool adapters (#136) (Idea) | 0 | 0.5 | 1 | DS |

### 3c. Already planned (IDEAS.md and briefs)

IDEAS.md holds 103 numbered ideas: 1 BUILDING, 18 DESIGNED, 84 PROPOSED,
none DONE. Parity rows above already credit the ones that close a CORIOLIX or
MetAcq gap. The rest are where we beat both systems, because neither does them.
They are the reason to choose this stack, so they are scored here too.

| Area | IDEAS rows | Brief or branch | Status | In CORIOLIX? | In MetAcq? |
|---|---|---|---|---|---|
| Vector wind averaging | 4 | branch `deepsignal/vector-wind` | Built (31 tests), parked on fork | yes (circular mean) | yes |
| DeepSignal Console core, bridge, charts, health, night mode, freshness | 12-14 | `briefs/deepsignal-console-*` | Building | partly (no night mode, no freshness states) | partly (MetBig) |
| QARTOD flags, plus "cannot tell" verdict | 8, 55 | `briefs/deepsignal-qartod-flags.md` | Briefed, waiting on Eugene's Mac approval | global limits only | range digit only |
| Instrument history graph | 52, 7 | `briefs/deepsignal-instrument-history.md`, cloud prompt | Briefed | sensor logs, no contradiction checks | metadata only |
| Correction ledger with sign-off | 56 | `briefs/deepsignal-correction-ledger.md` | Briefed | no | no |
| Fault-injection benchmark | 53 | `briefs/deepsignal-fault-bench.md` | Briefed, running on Mac | no | no |
| Post-cruise drift review | 54 | `briefs/deepsignal-post-cruise-drift.md` | Briefed | no | no |
| Ship-coupling discovery | 78 | `briefs/deepsignal-ship-coupling.md` | Briefed | no | no |
| Dependency-graph fault detector | 79 | `briefs/deepsignal-dependency-graph.md` | Briefed | no | no |
| Read-only MCP gateway and AI audit trail | 20-23, 62, 64-69 | design docs | Designed | no | no |
| Old-data reanalysis | 59, 63 | `research/2026-11-18-reanalysis-program.md` | Designed | no | no |
| Physics referee, clock forensics, provenance, replay | 25, 31-33 | none | Idea | no | no |
| Signals of opportunity (waves, current, rain, PWV, machinery) | 38-43, 80-103 | none | Idea | no | no |
| Linux gate | 49 | `briefs/gate-linux*.md` | Building | n/a | n/a |

## 4. Gaps ranked by value

Value is techs + science + shore, each scored 1 to 5 by how much that group
would miss it on a normal cruise (5 = asks for it on day one). Only rows not
already at 1 today are ranked. Ties break toward rows the plan does not cover
yet. Scores are judgement; argue with them in this file.

| Rank | Row | Gap | Techs | Science | Shore | Value | Covered by plan? | Home |
|---|---|---|---|---|---|---|---|---|
| 1 | C5 | Automated QC flag on every value (global limits), flag kept with value | 5 | 5 | 5 | 15 | yes | DS |
| 2 | M19 | Range checks with per-value quality digit carried downstream | 5 | 5 | 5 | 15 | yes | DS |
| 3 | C11 | Map: track, clickable trackpoints, underway data colored on track, events, cached OSM/GMRT/NOAA ENC basemaps, SST and Chl overlays | 3 | 5 | 5 | 13 | partly | DS |
| 4 | C1 | Live plots per sensor class (flowthrough, met, nav, sonar, CTD), zoom, pan, save PNG | 4 | 5 | 4 | 13 | yes | DS |
| 5 | C13 | Cruise event log (casts, stations) with standard vocabularies, shown on map | 4 | 5 | 4 | 13 | yes | DS |
| 6 | C15 | Sensor registry: sensors and parameters, enable/disable, tech-editable, vendor list | 5 | 4 | 4 | 13 | yes | DS |
| 7 | C16 | Sensor logs: history, configuration, issues, calibration dates | 5 | 4 | 4 | 13 | yes | DS |
| 8 | C17 | Calibration files per instrument and calibration transforms (SBE 3/4/9/38/43/45, ECO, SUNA, QSR ...) | 5 | 5 | 3 | 13 | yes | DS |
| 9 | C24 | Alerts: threshold (2 parameters), proximity (stations, ports), temporal (cal due, warranty), global, subscriptions | 5 | 4 | 4 | 13 | yes | DS |
| 10 | C3 | Sensor/parameter status board, color per parameter, grouped by class | 5 | 3 | 5 | 13 | yes | DS |
| 11 | C34 | End-of-cruise R2R package (raw plus metadata) | 4 | 4 | 5 | 13 | yes | DS |
| 12 | C43 | EEZ mode made easy: automatic detection from position against offline EEZ polygons, pre-alerts, per-instrument log, quarantine or stop from the clearance record, override with reason, audit for the cruise report | 5 | 4 | 4 | 13 | yes | DS |
| 13 | C6 | One-minute bins with statistics (mean, circular mean, std, min, max, median, count, spot; QC-filtered; composite flag) | 3 | 5 | 5 | 13 | yes | DS |
| 14 | M10 | Calibration chain, 45 named methods (polynomial, thermistor, RTD, SBE T/C, Eppley, SBE43, optode) | 5 | 5 | 3 | 13 | yes | DS |
| 15 | M11 | Sensor metadata per module (make, model, serial, cal date, lab, location) | 5 | 4 | 4 | 13 | yes | DS |
| 16 | C23 | Flowthrough valve schedule (open/closed content and durations) tied to the data | 4 | 5 | 3 | 12 | NO: draft below | DS |
| 17 | C9 | ERDDAP server (subset, format translation, OGC) | 2 | 5 | 5 | 12 | NO: draft below | DS |
| 18 | C26 | Ship-to-shore replication: data under 1 s, metadata both ways, shore mirror with same UI | 3 | 4 | 5 | 12 | yes | DS |
| 19 | C7 | Download UI: high-res, binned, binned+stats, native raw; by date, parameter, resolution; CSV, TSV, JSON, GeoJSON, MAT, netCDF, OPeNDAP; zip plus metadata file | 2 | 5 | 5 | 12 | yes | DS |
| 20 | E2 | DeepSignal quality flags, freshness and products in the OpenVDM package and Data Dashboard (qualityTests, stats) | 4 | 4 | 4 | 12 | yes | DS |
| 21 | E4 | Sealog events from data-system alerts, QC changes, flow state and instrument init results | 4 | 5 | 3 | 12 | yes | DS |
| 22 | E7 | Lossless compressed archive of closed raw logs (zstd or xz) with checksum manifest, byte-reproducible | 3 | 4 | 5 | 12 | yes | DS |
| 23 | M23 | .COR/.UNC $WICOR/$WIUNC files with quality digits | 4 | 4 | 4 | 12 | yes | DS |
| 24 | C33 | SAMOS daily file (1-min subset) sent from shore | 3 | 4 | 4 | 11 | NO: draft below | DS |
| 25 | M26 | SAMOS daily exchange file | 3 | 4 | 4 | 11 | NO: draft below | DS |
| 26 | M39 | Winch screen: wire out, speed, tension, CTD depth, altimeter | 5 | 4 | 2 | 11 | NO: draft below | DS |
| 27 | M8 | GPS failover (write one GPS, fail over to next) | 4 | 4 | 3 | 11 | NO: draft below | core |
| 28 | C18 | Primary-parameter rules: which sensor is primary per parameter, by model and location | 4 | 4 | 3 | 11 | partly | core |
| 29 | C27 | Data release policy: privacy level, restricted content, EEZ mode | 3 | 4 | 4 | 11 | NO: draft below | DS |
| 30 | C8 | REST API for data and metadata | 2 | 4 | 5 | 11 | yes | DS |
| 31 | E5 | Every Sealog event carries the quality state of the sensors at that moment (aux data) | 3 | 5 | 3 | 11 | yes | DS |
| 32 | E6 | Grafana dashboards for QC flags, freshness and system health, provisioned from the cruise definition | 4 | 3 | 4 | 11 | yes | DS |
| 33 | M36 | Strip charts with history scroll and per-plot scale | 4 | 4 | 3 | 11 | yes | DS |
| 34 | M42 | Status bar: scans per second, current file, silent sensors (CHK MOD) | 5 | 2 | 4 | 11 | yes | DS |
| 35 | C21 | CTD package configuration and CTD plot page | 4 | 4 | 2 | 10 | NO: draft below | DS |
| 36 | M16 | Waypoint ETA, EDA, time to go, bearing; off-course warning | 3 | 4 | 3 | 10 | NO: draft below | DS |
| 37 | M40 | GPS and waypoint screen (ETA, TTG, bearing) | 3 | 4 | 3 | 10 | NO: draft below | DS |
| 38 | C25 | Accounts and roles (public, scientist, technician, admin); ship and shore share accounts | 3 | 3 | 4 | 10 | NO: draft below | DS |
| 39 | C29 | GUI logger configuration and one-button deploy (writes OpenRVDAS config, updates alerts, ERDDAP, restarts) | 5 | 2 | 3 | 10 | NO: draft below | DS |
| 40 | C30 | Sensor onboarding workflow (create sensor, parameters with CF names and limits, cal files, network logger, data logger) | 5 | 2 | 3 | 10 | partly | DS |
| 41 | C32 | Standard vocabularies (CF names, SeaVoX L22/L35/EL1/EL2, R2R device types, ICES ship codes, UN/LOCODE) | 2 | 4 | 4 | 10 | partly | DS |
| 42 | E10 | Verdicts from OceanDataTools QA tools (nav QA, CTD QA, winch wire logs) shown in the console and Sealog | 3 | 4 | 3 | 10 | partly | DS |
| 43 | E8 | Science exports in NetCDF4/CF with chunked compression (Parquet if cheap) | 2 | 4 | 4 | 10 | partly | DS |
| 44 | M13 | Dew point, wet bulb, sea-level pressure | 3 | 4 | 3 | 10 | NO: draft below | core |
| 45 | M14 | Salinity, sigma-t, sound velocity | 3 | 4 | 3 | 10 | NO: draft below | core |
| 46 | M34 | Email products: SAMOS zip, OPSUM hourly, PCO2, SHIPTRACK, NOAA hourly ship weather | 3 | 3 | 4 | 10 | NO: draft below | DS |
| 47 | M43 | Web snapshots (PNG every 10 s) for shore and slow links | 2 | 3 | 5 | 10 | partly | DS |
| 48 | C2 | Custom and combination plots (any range, up to 4 parameters, saved per user) | 3 | 4 | 3 | 10 | yes | DS |
| 49 | E3 | One cruise and lowering identity across OpenRVDAS, OpenVDM, Sealog and DeepSignal | 4 | 3 | 3 | 10 | yes | DS |
| 50 | E9 | Compressed, prioritized ship-to-shore transfer over satellite | 2 | 3 | 5 | 10 | yes | DS |
| 51 | C12 | Route tools: draw route, distance, time at chosen speed | 2 | 4 | 3 | 9 | NO: draft below | DS |
| 52 | C14 | Cruise list and metadata (dates, ports, participants); schedule import | 2 | 3 | 4 | 9 | NO: draft below | DS |
| 53 | C35 | Documents catalog (manuals, calibration certificates) | 4 | 2 | 3 | 9 | partly | DS |
| 54 | C36 | Vessel metadata: dimensions, codes, survey monuments and benchmarks | 3 | 3 | 3 | 9 | partly | DS |
| 55 | C4 | System (host) health page | 4 | 1 | 4 | 9 | NO: draft below | DS |
| 56 | C37 | Public and remote-participant view | 1 | 4 | 4 | 9 | yes | DS |
| 57 | M29 | $WICOR UDP broadcast every second | 4 | 3 | 2 | 9 | yes | DS |
| 58 | M37 | Tabulated big numbers plus position | 3 | 3 | 3 | 9 | yes | DS |
| 59 | M41 | Diagnostic screen: raw strings per port, INOP per value | 5 | 1 | 3 | 9 | yes | DS |
| 60 | M44 | Sensor initialization over the wire: startup and setup commands, reply checks, re-init after power loss or reconnect, audit log of what was sent | 5 | 3 | 1 | 9 | yes | DS |
| 61 | C19 | Post-processing source assignment (which GPS feeds salinity, by location) | 3 | 3 | 2 | 8 | NO: draft below | core |
| 62 | M24 | Configuration copied next to each day of data | 2 | 3 | 3 | 8 | yes | core |
| 63 | C41 | UNOLS planning integration (MFP, MOMS) as metadata source of truth | 2 | 2 | 3 | 7 | NO: draft below | DS |
| 64 | M15 | Antenna lever-arm correction of position | 2 | 3 | 2 | 7 | NO: draft below | core |
| 65 | M31 | Sound velocity to multibeam (per-target format) | 3 | 3 | 1 | 7 | NO: draft below | core |
| 66 | M7 | Device definitions for the MetSpecs sensor list (RM Young, Vaisala, Eppley, SBE45/43, QSR, LCI90) | 4 | 2 | 1 | 7 | NO: draft below | core |
| 67 | M33 | Winch data to signboards | 4 | 2 | 1 | 7 | yes | DS |
| 68 | C28 | Retention settings (raw files, backup, database) | 3 | 1 | 2 | 6 | NO: draft below | core |
| 69 | M28 | Emulation mode with "emulated" flag | 2 | 2 | 2 | 6 | NO: draft below | core |
| 70 | M3 | ADAM/DGH analog-to-RS485 modules (ASCII protocol) | 3 | 2 | 1 | 6 | NO: draft below | core |
| 71 | C22 | Sensor groups (parent and child sensors shown together) | 2 | 2 | 2 | 6 | yes | DS |
| 72 | C42 | Site-wide message banner | 2 | 2 | 2 | 6 | yes | DS |
| 73 | M38 | MetBig: huge met values for the bridge, night-safe | 3 | 2 | 1 | 6 | yes | DS |
| 74 | M4 | NI DAQ / USB analog input | 1 | 1 | 0 | 2 | NO: draft below | core |

### Top 5 gaps (merged across duplicate CORIOLIX and MetAcq rows)

1. **QC flags that travel with every value** (C5, M19; value 15). Brief done
   (#8). Blocked only on Eugene's approval to run it on the Mac. Unblock first.
2. **Sensor registry, calibration and instrument history** (C15-C17, M10,
   M11, C35, C36; value 13). Brief #52 done; calibration records (#7) need a
   brief that reads the MetAcq method list and CORIOLIX's calibration file
   page. Add a document store and vessel geometry (drafts) to #52's follow-up.
3. **Live displays: status board, plots and the map** (C1, C3, C11, M36-M42;
   value 13). Console modules 1-4 are building. **The map has no brief**;
   make it console module 5.
4. **Data delivery to science and shore: binned statistics, downloads,
   ERDDAP, REST** (C6-C9; value 11-13). #16 is designed but **ERDDAP and a
   data REST API are not planned at all**. Generating ERDDAP `datasets.xml`
   from the registry is the cheapest way to match CORIOLIX's whole download
   stack, because ERDDAP (Apache-style open license) does the formats.
5. **Alerts with subscriptions** (C24; value 13). #9 is designed; extend it
   with CORIOLIX's proximity and calibration-due alert types.

Top unplanned gaps (now drafts in section 6): flowthrough state tagging (12),
ERDDAP generator (12), SAMOS file and met report formats (11), winch and CTD
cast view (11), best-source selector with GPS failover (11).

## 5. "Easier to set up": the target

### Definitions

- **T0, first light:** clean supported Linux box (Ubuntu 24.04, network up,
  sudo user) to the web console showing live simulated data updating. Count
  wall-clock minutes and **human actions** (commands typed, prompts answered,
  browser clicks).
- **T1, first real sensor:** from T0, plug in one NMEA GPS (serial or UDP) to
  parsed, logged, displayed, with a QC flag and a freshness state. Count the
  same two numbers, plus lines of YAML typed by hand.
- **T2, ship-ready:** a full underway suite. Tracked, not targeted yet.

### Baseline today

| | OpenRVDAS (counted from code, fork master 3f3d0c3) | CORIOLIX (public docs) |
|---|---|---|
| Servers per ship | 1 | 2 ship (OpenRVDAS + CORIOLIX) and 2 shore, 4 total (RVTEC 2025, System Requirements) |
| Prerequisites | Python 3.11+, sudo | signed certificates, DNS records, firewall rules, satcom (RVTEC 2025) |
| Install guide | `INSTALL.md`, complete | `INSTALL_coriolix.md` is a stub ("change testing"); source not public |
| T0 commands | 2 (download, run) + 1 to start the simulator | not possible from public sources |
| T0 prompts | 17 on the default Ubuntu path, plus the sudo password; 1 more to install the simulator, whose default is `no` (INSTALL.md shows `yes`: docs drift) | unknown |
| T0 browser actions | about 4 (log in, load cruise file, pick mode, open display) | unknown |
| T0 total human actions | **about 25** | unknown |
| Live data display after T0 | no maintained one: widgets are deprecated, Grafana is a separate install | built in |
| T0 wall-clock | **not yet measured** (brief below) | "setup takes effort" (RVTEC 2025); no number published |
| T1 | hand-write a logger config (and a device definition if the instrument is new), reload the cruise; no QC flag, no freshness; unmeasured, likely 30-90 min for an expert | 5-step web workflow plus two config scripts on two machines (`cx:HT_sensor_onboard`) |
| Upgrade | rerun installer | `UPGRADE_coriolix.md` is empty |

### Targets (proposed as D-SETUP1)

| Measure | Target | Why this number |
|---|---|---|
| T0 wall-clock | **10 minutes or less** on a GitHub `ubuntu-24.04` runner and on a 4 GB VM | install plus first data, network-bound; anything longer gets abandoned |
| T0 human actions | **3 or fewer**: one command, one password, open the URL. Zero-prompt default with a `--defaults` flag; questions only for what has no safe default | today about 25 |
| T0 result | console shows live simulated data with freshness states, no extra install | today no maintained display |
| T1 | **15 minutes or less, 10 or fewer actions, zero YAML typed** | matches the existing "add a new sensor" metric in IDEAS.md |
| Servers | **1 per ship**, shore mirror optional | CORIOLIX needs 2 per ship |
| Upgrade and recovery | upgrade in 5 minutes with rollback; a non-author recovers from docs alone (#71) | CORIOLIX upgrade page is empty |
| Footprint | core runs on a Raspberry Pi class box; full stack in 4 GB RAM | CORIOLIX asks 24 GB plus 8 GB |

### How we measure

`briefs/install-clock.md` (cloud lane, Sol medium): a GitHub Actions workflow
on fork branch `ci/install-clock` that runs the real installer on clean
Ubuntu 22.04 and 24.04 runners, counts prompts, and times install and first
data. Fork only. Run it now for the baseline, then on every installer change.

## 6. Home: core vs DeepSignal

The package decision (DeepSignal as a separate MIT package with thin adapters
versus `openrvdas_contrib`) is still open with Eugene. Note: the adoption
report calls it D-ARCH3, but D-ARCH3 in DECISIONS.md is already a DECIDED
entry about contrib branches; give the open one a new number. This table does
not decide it. It only says which work is generic plumbing that belongs in
OpenRVDAS core (small upstream fixes, under D-ARCH1's "core fix" exception) and
which is DeepSignal either way.

**Core (small, generic, upstream-shaped):** RS485 round-robin polling (M2),
ADAM ASCII reader (M3), device definitions for the UNOLS met suite (M7),
best-source selector and GPS failover (M8, C18, C19), met and seawater
formula library (M13, M14), lever-arm transform (M15), header-on-new-file in
`LogfileWriter` (M22), emulated flag in the simulators (M28), retention
policy (C28), zero-prompt installer (section 5). The installer change is
Eugene's call because OPERATIONS.md lists traps there.

**DeepSignal (everything a person sees, plus metadata and QC):** console and
all displays, map and routes, QC flags, registry, calibration records,
instrument history, documents, vessel geometry, alerts, event log, cruise
metadata, downloads, ERDDAP generator, REST API, roles, data release policy,
ship-to-shore, SAMOS and met report writers, $WICOR, scoreboard, R2R package,
onboarding wizard, vocabularies.

## 7. Draft ideas from this scorecard

Unnumbered, per the IDEAS numbering rule. Numbers assigned 2026-11-18: P-ERDDAP=#104, P-REST=#105, P-BEST=#106, P-MAP=#107, P-ROUTE=#108, P-CAST=#109, P-FLOW=#110, P-SAMOS=#111, P-METLIB=#112, P-GEOM=#113, P-WIZARD=#114, P-ROLES=#115, P-RELEASE=#116, P-VOCAB=#117, P-DOCS=#118, P-HOST=#119, P-CRUISE=#120, P-DEVPACK=#121, P-CORESMALL=#122, P-SNAP=#123, P-INSTALL=#124.
Also listed in IDEAS.md under "Drafts from the parity scorecard".

| Draft | Idea | Closes | Home |
|---|---|---|---|
| P-ERDDAP | Generate ERDDAP `datasets.xml` from the registry and database so ERDDAP serves subsets, every format and OGC | C7, C9 | DS |
| P-REST | Read-only REST data and metadata API (same tables MCP reads) | C8 | DS |
| P-BEST | Best-source selector: primary sensor per role by model and location, automatic failover, ancillary source assignment | C18, C19, M8 | core |
| P-MAP | Console map: track, clickable points, underway data colored on track, events, cached OSM, GMRT, NOAA ENC, SST and Chl layers, works offline | C11 | DS |
| P-ROUTE | Routes and waypoints: draw route, distance, ETA at speed, time to go, bearing, off-course warning | C12, M16, M40 | DS |
| P-CAST | Winch and CTD cast view: wire out, speed, tension with safe-working-load bands, CTD depth, altimeter; CTD package config | C21, M39 | DS |
| P-FLOW | Flowthrough state tagging: valve schedule tags every underway value with what was flowing (seawater, filtered, calibration, off), feeds QC and #55 | C23 | DS |
| P-SAMOS | SAMOS daily file and met report writers (NOAA hourly ship weather, OPSUM, SHIPTRACK, PCO2), byte-checked against real samples | C33, M26, M34 | DS |
| P-METLIB | Met and seawater formula library as named functions (dew point, wet bulb, sea-level pressure, PSS-78 and TEOS-10, sigma, sound speed) | M13, M14, M31 | core |
| P-GEOM | Vessel geometry: sensor positions, survey monuments, heights, lever-arm correction of positions | C36, M15 | DS + core transform |
| P-WIZARD | Sensor onboarding wizard with one-button deploy: identify stream, pick device, map CF names and limits, attach calibration, preview diff, deploy; no YAML typed | C29, C30 | DS (extends #29) |
| P-ROLES | Roles and accounts: public, science, tech, admin; ship and shore share accounts | C25 | DS |
| P-RELEASE | Data release policy: privacy level, restricted fields, EEZ hold-back using core `GeofenceTransform`, retention | C27, C28 | DS |
| P-VOCAB | Standard vocabularies in the registry: CF names, SeaVoX L22, L35, EL1, EL2, R2R device types, ICES ship codes, UN/LOCODE | C32 | DS |
| P-DOCS | Document store linked to instruments (manuals, calibration certificates) | C35 | DS |
| P-HOST | Host health on the health board: disk, CPU, RAM, NTP offset, process restarts | C4 | DS |
| P-CRUISE | Cruise metadata page (dates, ports, participants) with optional UNOLS schedule, MFP and MOMS import | C14, C41 | DS |
| P-DEVPACK | Device definitions for the MetSpecs sensor list | M7 | core (`contrib/devices`) |
| P-CORESMALL | Small core fixes: RS485 round-robin polling, ADAM ASCII reader, header on new file, emulated flag | M2, M3, M22, M28 | core |
| P-SNAP | Low-bandwidth shore snapshot page: static image plus compact JSON every N seconds | M43 | DS |
| P-INSTALL | Zero-prompt installer default plus install clock CI (section 5) | setup target | core (installer), fork (CI) |

## 9. Config assist coverage: every OpenRVDAS component

Eugene (2026-11-18): the "auto stuff" that helps people configure OpenRVDAS must cover all of it, UDP,
MQTT and the rest, not just serial. Inventory from fork `dev` 1a6f1ed: 19 readers, 22 writers, 34
transforms, plus the servers. The plan has three layers:

- **Forms for everything (#128 component catalog):** every component's settings become a form with
  defaults, checks and typo suggestions, generated from its code. This is what makes "no YAML" true for
  all of OpenRVDAS, not just the guided cases. Guided labels for the 15 most used components.
- **Guided setup (#114 wizard, #126 generator):** capture, identify, propose, diff, accept, for
  instruments; whole cruise definitions from the inventory.
- **Auto-detection (#125 discovery):** read-only, local or named targets only.

| Component | Kind | No-YAML setup | Auto-detect | Notes |
|---|---|---|---|---|
| SerialReader | reader | guided (#114, #126) | yes: port and baud scan (#125) | never writes to the port |
| PolledSerialReader | reader | form (#128); ADAM recipe (#121); init profiles (#130) | partial: reported as "silent, may need polling" | polling and init commands come from a reviewed profile, never from probing |
| UDPReader | reader | guided (#114, #126) | yes: passive listen on local ports (#125) | |
| TCPReader | reader | form (#128) | named target only (#125) | no network scanning, by design |
| NetworkReader, SocketReader | reader | form (#128) | named target only | older network readers |
| MQTTReader | reader | form (#128), guided label | yes: subscribe `#` on a named broker (#125) | needs the `mqtt` extra (paho-mqtt) |
| RedisReader | reader | form (#128), guided label | yes: channels and keys on a named server (#125) | needs the `redis` extra |
| CachedDataReader | reader | form (#128), guided label | yes: cache field list (#125) | |
| WebsocketReader | reader | form (#128) | named target only | |
| HTTPReader | reader | form (#128) | named URL only (#125) | |
| DatabaseReader | reader | form (#128) | no (needs credentials; listing tables is a later option) | needs a database extra |
| ModbusReader, ModbusSerialReader | reader | form (#128) | no: register maps cannot be guessed safely, and probing writes requests | |
| SealogReader | reader | form (#128) | named URL only | |
| LogfileReader, TextFileReader | reader | form (#128); wizard trial runs use them | yes: growing files in a named folder (#125) | |
| ComposedReader, TimeoutReader | reader | form (#128) | n/a | wrappers |
| CachedDataWriter, LogfileWriter | writer | automatic in every generated config (#126) | n/a | |
| UDPWriter, TCPWriter, SerialWriter, NetworkWriter, SocketWriter | writer | form (#128); $WICOR and nav repeat recipes (#6) | n/a | |
| MQTTWriter, RedisWriter, WebsocketWriter | writer | form (#128), guided labels for MQTT | n/a | optional extras |
| DatabaseWriter, InfluxDBWriter, GrafanaLiveWriter | writer | form (#128) | n/a | |
| EmailWriter, GoogleSheetsWriter, SealogWriter | writer | form (#128) | n/a | |
| FileWriter, TextFileWriter, RegexLogfileWriter, RecordScreenWriter | writer | form (#128) | n/a | |
| TimeoutWriter, ComposedWriter, LoggerManagerWriter | writer | form (#128) | n/a | TimeoutWriter feeds alerts (#9) |
| ParseTransform, ParseNMEATransform, RegexParseTransform | transform | automatic: chosen by the wizard's fingerprint (#114) | yes: device type identified from samples | |
| PrefixTransform, TimestampTransform | transform | automatic in generated configs (#126) | n/a | |
| TrueWindsTransform, ComputedFieldsTransform, SubsampleTransform, QC transforms | transform | form (#128); suggested when inputs exist (#129) | n/a | |
| All other transforms (format, select, convert, geofence, JSON, XML, Sealog, ...) | transform | form (#128) | n/a | |
| CachedDataServer, LoggerManager | server | installer (#124) and console install | n/a | already configured by the installer |
| Cruise definition as a whole | config | generated (#126), checked by core `validate_config` plus lint (#127) | n/a | |

Status: #114, #124, #125, #126, #127 and #128 are briefed (phase 2). Console auto-pages (display built
from what loggers publish) is in the console MVP. #129 and the console wizard page are next.

## 8. Next actions

1. Eugene: approve the QARTOD Mac run (gap 1).
2. Build lead: number the drafts; brief the map (P-MAP) as console module 5
   and calibration records (#7).
3. Run `briefs/install-clock.md` in the cloud lane for the measured baseline.
4. Eugene: decide the package question; then P-BEST, P-METLIB and the small
   core fixes can be briefed for core.
5. Re-score this file after each module lands.
