"""Generate docs/TARGET-PARITY.md tables and scores. Rows are data; scores computed."""
import sys

CXD = 'https://github.com/R-DESC/CORIOLIX_docs/blob/master/docs/'
U = 'https://www.unols.org/sites/default/files/'
SRC = {
    'R25': U + '2025-12/202511rvtec_romsos_chris_openrvdas_coriolix_2.pdf',
    'R23': U + '2023-11/202310rvt_apxxxvi.pdf',
    'R22': U + '202211rvt_apXXIV.pdf',
    'R20': U + '202010rvt_ap09.pdf',
    'R19': U + '201910rvt_ap27.pdf',
    'SKQ': 'https://coriolix.sikuliaq.alaska.edu',
    'MA': 'https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf',
    'MA12': 'https://calcofi.org/downloads/underway/2017/1711SR/met/docs/MetAcq.pdf',
    'MS': 'https://calcofi.org/downloads/underway/2021/2107SR/met/docs/MetSpecs.pdf',
    'OVDM': 'https://github.com/OceanDataTools/openvdm/issues/408',
}


def link(k):
    if k.startswith('cx:'):
        f = k[3:]
        return f'[{f}]({CXD}{f}.md)'
    lab = {'R25': 'RVTEC 2025', 'R23': 'RVTEC 2023', 'R22': 'RVTEC 2022',
           'R20': 'RVTEC 2020', 'R19': 'RVTEC 2019', 'SKQ': 'Sikuliaq site',
           'MA': 'MetAcq 2.15', 'MA12': 'MetAcq 2.12', 'MS': 'MetSpecs',
           'OVDM': 'OpenVDM #408'}[k]
    return f'[{lab}]({SRC[k]})'


CS = {'Have': 1.0, 'Partial': 0.5, 'Gap': 0.0}

# id, capability, sources, core, core_note, ds_ref, ds_status, planned, planned_with_drafts, home, T, S, Sh
# today = max(core score, 1 if ds_status == Built else core); planned scores given explicitly.
C = [
 ('C1', 'Live plots per sensor class (flowthrough, met, nav, sonar, CTD), zoom, pan, save PNG', ['cx:PAGES_plots', 'SKQ'],
  'Partial', 'Highcharts/D3 widgets deprecated (`display/README.md`); Grafana via `GrafanaLiveWriter`, installed separately', 'Console charts (#12-14)', 'Building', 1, 1, 'DS', 4, 5, 4),
 ('C2', 'Custom and combination plots (any range, up to 4 parameters, saved per user)', ['cx:PAGES_plots'],
  'Partial', 'Grafana can, but by hand', 'Console page files (D-CONSOLE1)', 'Designed', 1, 1, 'DS', 3, 4, 3),
 ('C3', 'Sensor/parameter status board, color per parameter, grouped by class', ['cx:PAGES_status', 'SKQ'],
  'Partial', 'Django shows per-logger state, not per-parameter freshness', 'Console health (#12)', 'Building', 1, 1, 'DS', 5, 3, 5),
 ('C4', 'System (host) health page', ['cx:PAGES_status'],
  'Partial', 'supervisord status only', 'none', '-', 0.5, 1, 'DS', 4, 1, 4),
 ('C5', 'Automated QC flag on every value (global limits), flag kept with value', ['SKQ', 'R25', 'cx:export_data'],
  'Partial', '`QCFilterTransform` drops or warns; no flag travels with the value', 'QARTOD flags (#8)', 'Briefed', 1, 1, 'DS', 5, 5, 5),
 ('C6', 'One-minute bins with statistics (mean, circular mean, std, min, max, median, count, spot; QC-filtered; composite flag)', ['cx:export_data', 'R23'],
  'Partial', '`SubsampleTransform` boxcar; `contrib/logger_templates/averaging_logger_template.yaml`', 'Vector wind (#4) built; binned downloads (#16)', 'Designed', 1, 1, 'DS', 3, 5, 5),
 ('C7', 'Download UI: high-res, binned, binned+stats, native raw; by date, parameter, resolution; CSV, TSV, JSON, GeoJSON, MAT, netCDF, OPeNDAP; zip plus metadata file', ['cx:export_data', 'cx:PAGES_data', 'SKQ'],
  'Gap', 'none', 'Binned downloads (#16)', 'Designed', 1, 1, 'DS', 2, 5, 5),
 ('C8', 'REST API for data and metadata', ['cx:API_endpoints', 'SKQ'],
  'Partial', 'CachedDataServer HTTP `/fields` and `/latest/` (fork `dev`); no history or metadata routes', 'REST API (#105)', 'Briefed', 1, 1, 'DS', 2, 4, 5),
 ('C9', 'ERDDAP server (subset, format translation, OGC)', ['cx:TS_erddap_data_download', 'R25', 'R20'],
  'Gap', 'none', 'none', '-', 0, 1, 'DS', 2, 5, 5),
 ('C10', 'Pushed real-time data services (UDP, MQTT, websockets)', ['cx:HT_data_access', 'R25'],
  'Have', '`UDPWriter`, `MQTTWriter`, `CachedDataServer`', '-', '-', 1, 1, 'core', 0, 0, 0),
 ('C11', 'Map: track, clickable trackpoints, underway data colored on track, events, cached OSM/GMRT/NOAA ENC basemaps, SST and Chl overlays', ['cx:PAGES_map', 'SKQ'],
  'Gap', 'none maintained', 'Console map (in console plan, no brief)', 'Idea', 0.5, 1, 'DS', 3, 5, 5),
 ('C12', 'Route tools: draw route, distance, time at chosen speed', ['cx:PAGES_map'],
  'Gap', 'none', 'none', '-', 0, 1, 'DS', 2, 4, 3),
 ('C13', 'Cruise event log (casts, stations) with standard vocabularies, shown on map', ['cx:PAGES_tools', 'SKQ', 'R25'],
  'Partial', 'Sealog reader/writer integration (Sealog is a separate app)', 'Event log (#15)', 'Designed', 1, 1, 'DS', 4, 5, 4),
 ('C14', 'Cruise list and metadata (dates, ports, participants); schedule import', ['cx:PAGES_tools', 'R25'],
  'Partial', 'cruise definition YAML holds id and dates', 'none', '-', 0.5, 1, 'DS', 2, 3, 4),
 ('C15', 'Sensor registry: sensors and parameters, enable/disable, tech-editable, vendor list', ['cx:PAGES_sensors', 'SKQ', 'R25'],
  'Partial', 'device definition YAMLs, no UI, no registry', 'Instrument history (#52)', 'Briefed', 1, 1, 'DS', 5, 4, 4),
 ('C16', 'Sensor logs: history, configuration, issues, calibration dates', ['SKQ', 'R25'],
  'Gap', 'none', 'Instrument history (#52)', 'Briefed', 1, 1, 'DS', 5, 4, 4),
 ('C17', 'Calibration files per instrument and calibration transforms (SBE 3/4/9/38/43/45, ECO, SUNA, QSR ...)', ['cx:HT_sensor_onboard_step3', 'R25'],
  'Partial', '`ComputedFieldsTransform` expressions; no coefficient files per serial', 'Calibration records (#7), #52', 'Designed', 1, 1, 'DS', 5, 5, 3),
 ('C18', 'Primary-parameter rules: which sensor is primary per parameter, by model and location', ['cx:PAGES_sensors', 'R25'],
  'Gap', 'none', 'Two-anemometer consensus (#51) is one case', 'Idea', 0.5, 1, 'core', 4, 4, 3),
 ('C19', 'Post-processing source assignment (which GPS feeds salinity, by location)', ['cx:PAGES_sensors'],
  'Partial', 'chosen by hand in config', 'none', '-', 0.5, 1, 'core', 3, 3, 2),
 ('C20', 'Derived products (true wind, SI units)', ['R22'],
  'Have', '`TrueWindsTransform`, `ConvertFieldsTransform`', '-', '-', 1, 1, 'core', 0, 0, 0),
 ('C21', 'CTD package configuration and CTD plot page', ['cx:HT_CTD_Configuration', 'cx:PAGES_sensors'],
  'Gap', 'none', 'none', '-', 0, 1, 'DS', 4, 4, 2),
 ('C22', 'Sensor groups (parent and child sensors shown together)', ['cx:PAGES_sensors'],
  'Gap', 'none', 'Console page files', 'Designed', 1, 1, 'DS', 2, 2, 2),
 ('C23', 'Flowthrough valve schedule (open/closed content and durations) tied to the data', ['cx:PAGES_settings'],
  'Gap', 'none', 'none', '-', 0, 1, 'DS', 4, 5, 3),
 ('C24', 'Alerts: threshold (2 parameters), proximity (stations, ports), temporal (cal due, warranty), global, subscriptions', ['cx:HT_account', 'SKQ', 'R19', 'R22'],
  'Partial', '`TimeoutReader`/`TimeoutWriter` plus `EmailWriter` cover silence only', 'State-aware alarms (#9), plain-language alarms (#34)', 'Designed', 1, 1, 'DS', 5, 4, 4),
 ('C25', 'Accounts and roles (public, scientist, technician, admin); ship and shore share accounts', ['cx:HT_account', 'cx:PAGES_settings', 'R25'],
  'Partial', 'Django login: viewer vs logged-in; FastAPI JWT for the React UI', 'Console role pages (#14), no role model', 'Idea', 0.5, 1, 'DS', 3, 3, 4),
 ('C26', 'Ship-to-shore replication: data under 1 s, metadata both ways, shore mirror with same UI', ['SKQ', 'R19', 'R22', 'R23'],
  'Partial', 'network writers can send; no store-and-forward or shore mirror', 'Sync bulk/live, link profiles, semantic sync (#17-19, #35)', 'Idea', 1, 1, 'DS', 3, 4, 5),
 ('C27', 'Data release policy: privacy level, restricted content, EEZ mode', ['cx:PAGES_settings'],
  'Partial', '`GeofenceTransform` switches modes at EEZ boundaries', 'none', '-', 0.5, 1, 'DS', 3, 4, 4),
 ('C28', 'Retention settings (raw files, backup, database)', ['cx:PAGES_settings'],
  'Partial', 'files kept forever; no policy', 'none', '-', 0.5, 0.5, 'core', 3, 1, 2),
 ('C29', 'GUI logger configuration and one-button deploy (writes OpenRVDAS config, updates alerts, ERDDAP, restarts)', ['R25', 'R20', 'R23'],
  'Partial', 'Django loads a cruise YAML and switches modes; YAML is hand-written', 'Plug-and-identify (#29)', 'Idea', 0.5, 1, 'DS', 5, 2, 3),
 ('C30', 'Sensor onboarding workflow (create sensor, parameters with CF names and limits, cal files, network logger, data logger)', ['cx:HT_sensor_onboard', 'cx:HT_sensor_onboard_step1', 'cx:HT_sensor_onboard_step2'],
  'Gap', 'edit YAML by hand', 'Plug-and-identify (#29)', 'Idea', 0.5, 1, 'DS', 5, 2, 3),
 ('C31', 'Regex parsing with a public regex library', ['cx:RegExGuide', 'R25'],
  'Have', '`RegexParseTransform`, `ParseTransform`, `contrib/devices/`', '-', '-', 1, 1, 'core', 0, 0, 0),
 ('C32', 'Standard vocabularies (CF names, SeaVoX L22/L35/EL1/EL2, R2R device types, ICES ship codes, UN/LOCODE)', ['cx:PAGES_about', 'R25'],
  'Gap', 'none', 'Cross-vessel ontology (#103)', 'Idea', 0.5, 1, 'DS', 2, 4, 4),
 ('C33', 'SAMOS daily file (1-min subset) sent from shore', ['R23'],
  'Gap', 'none', 'none (#95 only validates against SAMOS)', '-', 0, 1, 'DS', 3, 4, 4),
 ('C34', 'End-of-cruise R2R package (raw plus metadata)', ['R23', 'SKQ', 'cx:export_data'],
  'Partial', 'raw logfiles exist; no package', 'R2R-ready package (#58)', 'Idea', 1, 1, 'DS', 4, 4, 5),
 ('C35', 'Documents catalog (manuals, calibration certificates)', ['cx:PAGES_documents', 'SKQ'],
  'Gap', 'none', '#52 links cal records', 'Briefed', 0.5, 1, 'DS', 4, 2, 3),
 ('C36', 'Vessel metadata: dimensions, codes, survey monuments and benchmarks', ['cx:PAGES_vessel'],
  'Gap', 'none', '#52 has mount position', 'Briefed', 0.5, 1, 'DS', 3, 3, 3),
 ('C37', 'Public and remote-participant view', ['SKQ'],
  'Partial', 'Django anonymous viewer', 'Shore view (#14)', 'Idea', 1, 1, 'DS', 1, 4, 4),
 ('C38', 'Raw archive, timestamped, one file per sensor per day; backup', ['cx:HT_data_access', 'R23'],
  'Have', '`LogfileWriter`', '-', '-', 1, 1, 'core', 0, 0, 0),
 ('C39', 'Time-series database storage', ['R25', 'R20'],
  'Have', '`DatabaseWriter` (MySQL, PostgreSQL), `InfluxDBWriter`', '-', '-', 1, 1, 'core', 0, 0, 0),
 ('C40', 'Playback of recorded data for development', ['R25'],
  'Have', '`LogfileReader`, `simulate_*.py`', '-', '-', 1, 1, 'core', 0, 0, 0),
 ('C41', 'UNOLS planning integration (MFP, MOMS) as metadata source of truth', ['R25', 'R22'],
  'Gap', 'none', 'none', '-', 0, 0.5, 'DS', 2, 2, 3),
 ('C42', 'Site-wide message banner', ['cx:PAGES_settings'],
  'Gap', 'none', 'Console core (trivial)', 'Building', 1, 1, 'DS', 2, 2, 2),
]

M = [
 ('M1', 'RS232/RS422 serial input', ['MA'], 'Have', '`SerialReader`', '-', '-', 1, 1, 'core', 0, 0, 0),
 ('M2', 'RS485 multidrop polling, per-address round robin with timeouts', ['MA'], 'Have', '`PolledSerialReader` `pre_read_cmd` dict: round-robin polling with per-command timeout (fork `dev`)', '-', '-', 1, 1, 'core', 0, 0, 0),
 ('M3', 'ADAM/DGH analog-to-RS485 modules (ASCII protocol)', ['MA'], 'Partial', '`ModbusSerialReader` (ADAM-4000 ASCII is not Modbus)', 'none', '-', 0.5, 1, 'core', 3, 2, 1),
 ('M4', 'NI DAQ / USB analog input', ['MA'], 'Gap', 'none', 'none', '-', 0, 0, 'core', 1, 1, 0),
 ('M5', 'UDP input, NMEA and non-NMEA', ['MA'], 'Have', '`UDPReader`, `ParseNMEATransform`', '-', '-', 1, 1, 'core', 0, 0, 0),
 ('M6', 'NMEA sentence set (GGA ... PASHR, PKEL99)', ['MA'], 'Have', 'NMEA parser plus `contrib/devices` (verify PASHR, PKEL99)', '-', '-', 1, 1, 'core', 0, 0, 0),
 ('M7', 'Device definitions for the MetSpecs sensor list (RM Young, Vaisala, Eppley, SBE45/43, QSR, LCI90)', ['MS'], 'Partial', 'some devices in `contrib/devices`', 'none', '-', 0.5, 1, 'core', 4, 2, 1),
 ('M8', 'GPS failover (write one GPS, fail over to next)', ['MA'], 'Gap', 'none', 'none', '-', 0, 1, 'core', 4, 4, 3),
 ('M9', 'Clock sync to NTP or GPS', ['MA'], 'Have', 'host chrony/NTP', 'Clock forensics (#31)', 'Idea', 1, 1, 'core', 0, 0, 0),
 ('M10', 'Calibration chain, 45 named methods (polynomial, thermistor, RTD, SBE T/C, Eppley, SBE43, optode)', ['MA', 'MA12'], 'Partial', 'expressions only; no named methods or coefficient files', 'Calibration records (#7)', 'Designed', 1, 1, 'DS', 5, 5, 3),
 ('M11', 'Sensor metadata per module (make, model, serial, cal date, lab, location)', ['MA'], 'Gap', 'none', 'Instrument history (#52)', 'Briefed', 1, 1, 'DS', 5, 4, 4),
 ('M12', 'True wind', ['MA'], 'Have', '`TrueWindsTransform`', '-', '-', 1, 1, 'core', 0, 0, 0),
 ('M13', 'Dew point, wet bulb, sea-level pressure', ['MA'], 'Partial', 'hand-written expressions', 'none', '-', 0.5, 1, 'core', 3, 4, 3),
 ('M14', 'Salinity, sigma-t, sound velocity', ['MA'], 'Partial', 'expressions; `gsw` hook', 'none', '-', 0.5, 1, 'core', 3, 4, 3),
 ('M15', 'Antenna lever-arm correction of position', ['MA'], 'Gap', 'none', 'none', '-', 0, 1, 'core', 2, 3, 2),
 ('M16', 'Waypoint ETA, EDA, time to go, bearing; off-course warning', ['MA'], 'Gap', 'only `GeofenceTransform` in/out', 'none', '-', 0, 1, 'DS', 3, 4, 3),
 ('M17', 'Boxcar averaging per sensor', ['MA'], 'Have', '`SubsampleTransform`', '-', '-', 1, 1, 'core', 0, 0, 0),
 ('M18', 'Vector averaging of wind direction', ['MA'], 'Gap', 'none in core', 'Vector wind (#4)', 'Built', 1, 1, 'DS', 0, 0, 0),
 ('M19', 'Range checks with per-value quality digit carried downstream', ['MA'], 'Partial', 'drop or warn only', 'QARTOD flags (#8)', 'Briefed', 1, 1, 'DS', 5, 5, 5),
 ('M20', 'Parallel uncorrected and corrected streams', ['MA'], 'Have', 'two chains in one config', 'Correction ledger (#56) goes further', 'Briefed', 1, 1, 'core', 0, 0, 0),
 ('M21', 'Daily files rolling at 0000Z', ['MA'], 'Have', '`LogfileWriter`', '-', '-', 1, 1, 'core', 0, 0, 0),
 ('M22', '.MET/.UCR column files with headers on each new file', ['MA'], 'Have', '`FormatTransform` plus `LogfileWriter` `header`/`header_file` on each new file', '-', '-', 1, 1, 'core', 0, 0, 0),
 ('M23', '.COR/.UNC $WICOR/$WIUNC files with quality digits', ['MA', 'OVDM'], 'Gap', 'none', '$WICOR writer (#6)', 'Designed', 1, 1, 'DS', 4, 4, 4),
 ('M24', 'Configuration copied next to each day of data', ['MA'], 'Partial', '`server/config_snapshot.py` (verify per day)', 'Provenance (#32)', 'Idea', 1, 1, 'core', 2, 3, 3),
 ('M25', 'Daily operations log', ['MA'], 'Have', 'logging', '-', '-', 1, 1, 'core', 0, 0, 0),
 ('M26', 'SAMOS daily exchange file', ['MA'], 'Gap', 'none', 'none', '-', 0, 1, 'DS', 3, 4, 4),
 ('M27', 'Playback and regenerate corrected files from raw', ['MA'], 'Have', '`LogfileReader` plus same chain', 'Time-travel replay (#33)', 'Idea', 1, 1, 'core', 0, 0, 0),
 ('M28', 'Emulation mode with "emulated" flag', ['MA'], 'Partial', '`simulate_*.py`, no flag in output', 'none', '-', 0.5, 1, 'core', 2, 2, 2),
 ('M29', '$WICOR UDP broadcast every second', ['MA', 'OVDM'], 'Partial', '`UDPWriter`, no formatter', '$WICOR writer (#6)', 'Designed', 1, 1, 'DS', 4, 3, 2),
 ('M30', 'Serial repeat of nav to MRU, Seatel, multibeam', ['MA'], 'Have', '`SerialWriter`, `UDPWriter`', '-', '-', 1, 1, 'core', 0, 0, 0),
 ('M31', 'Sound velocity to multibeam (per-target format)', ['MA'], 'Partial', 'format strings by hand', 'none', '-', 0.5, 1, 'core', 3, 3, 1),
 ('M32', 'User-defined outputs (printf format, leader, CRC, NMEA checksum)', ['MA'], 'Have', '`FormatTransform`, `NMEAChecksumTransform`', '-', '-', 1, 1, 'core', 0, 0, 0),
 ('M33', 'Winch data to signboards', ['MA'], 'Gap', 'none', 'Scoreboard writer (#5)', 'Designed', 1, 1, 'DS', 4, 2, 1),
 ('M34', 'Email products: SAMOS zip, OPSUM hourly, PCO2, SHIPTRACK, NOAA hourly ship weather', ['MA'], 'Partial', '`EmailWriter`, formats missing', 'none', '-', 0.5, 1, 'DS', 3, 3, 4),
 ('M35', 'Cascade (second PC mirrors primary)', ['MA'], 'Have', '`UDPReader`, `CachedDataServer`', '-', '-', 1, 1, 'core', 0, 0, 0),
 ('M36', 'Strip charts with history scroll and per-plot scale', ['MA'], 'Partial', 'deprecated widgets; Grafana', 'Console charts', 'Building', 1, 1, 'DS', 4, 4, 3),
 ('M37', 'Tabulated big numbers plus position', ['MA'], 'Partial', '`text_widget.js` (deprecated)', 'Console core', 'Building', 1, 1, 'DS', 3, 3, 3),
 ('M38', 'MetBig: huge met values for the bridge, night-safe', ['MA'], 'Gap', 'none', 'Console bridge (#13)', 'Building', 1, 1, 'DS', 3, 2, 1),
 ('M39', 'Winch screen: wire out, speed, tension, CTD depth, altimeter', ['MA'], 'Gap', 'none', 'none', '-', 0, 1, 'DS', 5, 4, 2),
 ('M40', 'GPS and waypoint screen (ETA, TTG, bearing)', ['MA'], 'Gap', 'none', 'none', '-', 0, 1, 'DS', 3, 4, 3),
 ('M41', 'Diagnostic screen: raw strings per port, INOP per value', ['MA'], 'Partial', 'Django logger stderr view', 'Console health (#12)', 'Building', 1, 1, 'DS', 5, 1, 3),
 ('M42', 'Status bar: scans per second, current file, silent sensors (CHK MOD)', ['MA'], 'Partial', 'logger status, no per-sensor silence list', 'Console health (#12)', 'Building', 1, 1, 'DS', 5, 2, 4),
 ('M43', 'Web snapshots (PNG every 10 s) for shore and slow links', ['MA'], 'Gap', 'none', 'Shore view (#14), link profiles (#19)', 'Idea', 0.5, 1, 'DS', 2, 3, 5),
 ('M44', 'Sensor initialization over the wire: startup and setup commands, reply checks, re-init after power loss or reconnect, audit log of what was sent', ['MA'], 'Partial', '`PolledSerialReader` `start_cmd` (sent once at open, reply not checked, not resent after a power cycle), `stop_cmd`, `pre_read_cmd`, `__PAUSE__`; serial only. MetAcq 2.15 documents only per-module poll commands (CMD, CMD2, CMD3 in the .ACQ file); init is silent in its manual', 'Instrument init profiles (#130)', 'Briefed', 1, 1, 'DS', 5, 3, 1),
]


def today(r):
    core = CS[r[3]]
    return 1.0 if r[6] == 'Built' else core


def pct(rows, f):
    return 100.0 * sum(f(r) for r in rows) / len(rows)


def table(rows):
    out = ['| # | Capability | Source | OpenRVDAS core today | DeepSignal | Today | Planned | +Drafts | Home |',
           '|---|---|---|---|---|---|---|---|---|']
    for r in rows:
        src = ', '.join(link(k) for k in r[2])
        ds = r[5] if r[6] in ('-',) else f'{r[5]} ({r[6]})'
        if r[5] in ('-', 'none') and r[6] == '-':
            ds = r[5]
        core = f'{r[3]}: {r[4]}'
        planned_existing = r[7]
        out.append(f'| {r[0]} | {r[1]} | {src} | {core} | {ds} | {today(r):g} | {planned_existing:g} | {r[8]:g} | {r[9]} |')
    return '\n'.join(out)


def summary():
    lines = ['| Scope | Rows | Core today | Core + built DeepSignal today | With briefed and planned work | With this doc\'s drafts |',
             '|---|---|---|---|---|---|']
    for name, rows in (('CORIOLIX', C), ('MetAcq', M), ('Combined', C + M)):
        core = pct(rows, lambda r: CS[r[3]])
        t = pct(rows, today)
        p = pct(rows, lambda r: r[7])
        d = pct(rows, lambda r: r[8])
        lines.append(f'| {name} | {len(rows)} | {core:.0f}% | {t:.0f}% | {p:.0f}% | {d:.0f}% |')
    return '\n'.join(lines)


def gaps():
    rows = [r for r in C + M if today(r) < 1]
    rows.sort(key=lambda r: (-(r[10] + r[11] + r[12]), -(1 - r[7]), r[0]))
    out = ['| Rank | Row | Gap | Techs | Science | Shore | Value | Covered by plan? | Home |',
           '|---|---|---|---|---|---|---|---|---|']
    for i, r in enumerate(rows, 1):
        plan = 'yes' if r[7] >= 1 else ('partly' if r[7] > today(r) else 'NO: draft below')
        out.append(f'| {i} | {r[0]} | {r[1]} | {r[10]} | {r[11]} | {r[12]} | {r[10]+r[11]+r[12]} | {plan} | {r[9]} |')
    return '\n'.join(out), rows


def build():
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    t = open(os.path.join(here, 'template.md')).read()
    for k, v in SRC.items():
        t = t.replace('{' + k + '}', v)
    t = (t.replace('{SUMMARY}', summary()).replace('{CTABLE}', table(C))
          .replace('{MTABLE}', table(M)).replace('{GAPS}', gaps()[0]))
    out = os.path.join(here, '..', '..', 'docs', 'TARGET-PARITY.md')
    open(out, 'w').write(t)
    print('wrote', os.path.normpath(out))


if __name__ == '__main__':
    what = sys.argv[1]
    if what == 'build':
        build()
    elif what == 'C':
        print(table(C))
    elif what == 'M':
        print(table(M))
    elif what == 'S':
        print(summary())
    elif what == 'G':
        print(gaps()[0])
