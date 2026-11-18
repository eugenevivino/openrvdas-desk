# MetAcq manual analysis: feature inventory and OpenRVDAS gap map

Date: 2026-11-17 (filed 2026-11-18). Source thread: "Find and analyze MetAcq manual".
Living copy (Claude Doc): https://claude.ai/artifact/QkQXV3ZZkgHrYJNQrew29B
OpenRVDAS baseline checked: `OceanDataTools/openrvdas` master, commit `3f3d0c3` (2026-11-15).

## Bottom line

**The manual exists and is public.** The "Shipboard Meteorological System MetAcq Operator's Manual" by Scripps Shipboard Technical Support (STS) is mirrored by several science groups. The newest copy found is **Rev 2.15, August 2019** (author Carl Mattson, support sts-cr@ucsd.edu).

**Recommendation:** Do not clone MetAcq's LabVIEW architecture. Replicate its *outputs and behaviors*: the $WICOR stream, daily corrected and uncorrected files, the calibration chain, true wind, vector averaging, emails to SAMOS and NOAA, and sensor health. OpenRVDAS already covers roughly 60% of the plumbing (estimate). The real gaps are five:

1. Calibration-coefficient layer with per-sensor metadata.
2. Vector (wind) averaging.
3. $WICOR / COR / MET writer plus parser.
4. Sensor-health alarms.
5. Operator display layer (strip charts with history, big-number bridge view, winch view, waypoint ETA). This is where we can beat both MetAcq and Grafana.

## Where to get the manual

| Version | Date | Link | Notes |
|---|---|---|---|
| Rev 2.15 | Aug 2019 | https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf | Newest. Linux build, web/Apache, email outputs, cascade, emulation |
| Rev 2.12 | Apr 2014 | https://calcofi.org/downloads/underway/2017/1711SR/met/docs/MetAcq.pdf | Full calibration method list 0 to 44 |
| Rev 1.84 | Apr 2004 | https://calcofi.org/downloads/underway/2005/0501NH/MET/MetAcq.pdf | Only copy where section 10 (file formats) was read verbatim |
| unknown | | https://iop.apl.uw.edu/data/AESOP/AESOP07/underway/met/doc/MetAcq.pdf | Mirror |
| unknown | | https://iop.apl.uw.edu/data/AESOP/AESOP06/underway/met/metacq.doc | Word version |
| unknown | | https://www.coaps.fsu.edu/pub/clivar/rv_orig_data/WECB/metacq.pdf | Mirror |
| unknown | | http://bcodata.whoi.edu/GATEKEEPERS/MetAcq.pdf | Mirror |
| MetSpecs Rev 1.18 | Jun 2013 | https://calcofi.org/downloads/underway/2021/2107SR/met/docs/MetSpecs.pdf | Sensor makes, models, ranges, accuracy |

Related sources:
- OpenVDM issue #408, "Parser for Scripps MetAcq $WICOR sentences": https://github.com/OceanDataTools/openvdm/issues/408. Closed 2026-10-10, merged to OpenVDM `dev` in PR #409. Best public description of the $WICOR tag set. It references SIO's own OpenRVDAS `wicor_params.yaml`, so **SIO already runs OpenRVDAS alongside MetAcq**.
- R/V Revelle handbook section 4: https://scripps.ucsd.edu/ships/revelle/handbook/section-4-ships-and-scientific-equipment-description
- R/V Sproul handbook section 4: https://scripps.ucsd.edu/ships/sproul/handbook/section-4-scientific-equipment-procedures
- CalCOFI underway data format: https://calcofi.info/index.php/ccdata/underway/151-underway-data-format/261-underway-data-format (30 s MET records in daily files; 10 min bin-averaged corrected data).

**Copies:** not saved. The cloud workspace proxy blocks these hosts. Download via a device folder or browser.

**Read coverage (known vs unknown):**
- Read verbatim: Rev 2.15 sections 1 to 4.6; Rev 2.12 sections 1 to 9.3.5; Rev 1.84 sections 1 to 10 including 9.4.0 and 10.1.0.
- Summary only, needs a direct read before building: Rev 2.15 sections 5 to 11 and Appendices A to E (exact $WICOR tag order, column layouts, true wind and dew point formulas, SAMOS format).

## Glossary

- **ACQ file**: MetAcq's single INI-style config. Ports, sensor modules, calibration coefficients, averaging, outputs. Copied next to each day's data.
- **Module**: one sensor instance, named by a 3-letter type plus 2-char ID (for example `WND01`).
- **MSP / MCP**: per-module "sensor parameters" (device type, address, parsing) and "calibration parameters" (where and how each value is corrected).
- **$WICOR / $WIUNC**: MetAcq's NMEA-style line. `$WICOR,ddmmyy,hhmmss,` then `value,TAG` pairs, then `*hh` checksum.
- **Quality flag digit** (last char of each tag): 0 no cal applied, 1 cal in sensor module, 2 cal in acquisition PC, 3 both, 7 out of range, 8 emulated, 9 invalid (value also written as -99).
- **Vector averaging**: averaging wind as u/v components so 359 and 1 degrees average to 0, not 180.
- **SAMOS**: FSU COAPS Shipboard Automated Meteorological and Oceanographic System; MetAcq emails it a daily file.

## Platform facts

- LabVIEW application (MetAcq.exe or Linux build). Needs NI LabVIEW Runtime and NI VISA Runtime.
- Rev 2.15: Windows 7/8/10 64-bit or RedHat/Scientific/CentOS 64-bit, 2+ serial ports (Comtrol Rocketport recommended), 1280x1024 display.
- Paths: Windows `C:\Wbin` (exe), `C:\Wbin\www` (web), `C:\MET` (data/config), `C:\MET\Manuals`. Linux `/opt/met/{bin,www,data,manuals}`.
- Cruise name from `cruisename.txt`. Config example name `SP16A.ACQ`.
- Modes: Acquire, Playback, Cascade (mirror a primary PC over UDP 40119 or serial), Emulate (simulated sensors, flag 8).
- Time sync: NTP if present, else GPS (`GPS_SYNCH`).
- "Rd Acqfile" re-reads config live; port changes need a restart.

## MetAcq feature inventory mapped to OpenRVDAS

Status key: **Have** = exists in OpenRVDAS master. **Partial** = building blocks exist, needs config or a thin wrapper. **Gap** = needs new code.

### 1. Inputs and sensors

| MetAcq feature | OpenRVDAS today | Status |
|---|---|---|
| RS232/RS422 serial, up to 128 logical ports (34 in 2004) | `SerialReader`, `PolledSerialReader` | Have |
| RS485 multidrop polling (up to 32 devices per bus, RD485MINTO/MAXTO timeouts) | `PolledSerialReader` sends query strings | Partial: no per-address round robin with per-device timeout |
| ADAM / DGH analog-to-RS485 modules (volts, 4-20 mA, frequency counts) | `ModbusReader`, `ModbusSerialReader` (ADAM-4000 ASCII protocol is not Modbus) | Partial |
| NI DAQ / USB analog | none | Gap (low priority, legacy) |
| UDP input, NMEA and non-NMEA | `UDPReader`, `ParseNMEATransform`, `ParseTransform` | Have |
| NMEA sentences GGA GNS RMC GLL VTG HDT ZDA MWV VHW VBW DBT DPT DBS GSA MDA HDG XDR PASHR ATT, Knudsen PKEL99 | NMEA parser plus `contrib/devices` (Seapath, Trimble, Garmin, Knudsen) | Have, verify PASHR and PKEL coverage |
| 36 sensor types (list below) | Device definitions per instrument in YAML | Partial: need device YAMLs for the MetSpecs sensor list |
| GPS failover (ONEGPS2FILE: write one GPS, fail over to next) | none built in | Gap: small "best source" transform |
| Time sync to NTP or GPS | host NTP/chrony | Have (OS level) |

### 2. Processing and derived values

| MetAcq feature | OpenRVDAS today | Status |
|---|---|---|
| Calibration chain, 45 named methods (list below) | `ComputedFieldsTransform` (safe expressions, extensible FUNCTIONS), `ConvertFieldsTransform` | Partial: no named methods, no coefficient file per sensor serial, no cal-date tracking |
| Sensor metadata per module (SENSOR, MODEL, MFG, SERIAL, OWNER, CAL_DATE, CAL_LAB, LOCATION, INSTALL_DATE) | none | **Gap** |
| True wind speed and direction from relative wind, heading, COG, SOG | `TrueWindsTransform` | Have |
| Dew point, wet bulb, sea-level pressure | `ComputedFieldsTransform` expressions | Partial (write the formulas once as a library) |
| Salinity, density/sigma-t, sound velocity (PSS-78, Chen and Millero 1977; ITS-90 to ITS-68 conversion) | `ComputedFieldsTransform` plus `gsw` (TEOS-10) subclass hook | Partial |
| Antenna lever-arm offset of lat/lon (methods 32/33) | none | Gap (small) |
| Waypoint ETA, EDA, time to go, distance (nm), bearing; "CHK WPT" when bearing is over 45 deg off COG | `GeofenceTransform` only does in/out | Gap |
| Averaging: normal (boxcar), per sensor window SECSTOAVG | `SubsampleTransform` `boxcar_average` | Have |
| Vector averaging for wind direction (AVGTYPE 2) | none (`logger/utils/subsample.py` has boxcar only) | **Gap**, critical for correct wind |
| Range checks per parameter (RANGE, UCR_RANGE) with flag 7 | `QCFilterTransform`, `ValueFilterTransform` | Partial: filters drop or warn; no per-value flag carried downstream |
| Two parallel streams: uncorrected and corrected | two transform chains in one logger config | Have (by config) |

### 3. Logging and file formats

| MetAcq feature | OpenRVDAS today | Status |
|---|---|---|
| Daily files rolling at 0000Z | `LogfileWriter` (date split) | Have |
| .MET (corrected) and .UCR (uncorrected): 4 header lines (ship title, date/time, data type, column header) then columns, e.g. `#Time AT BP WS WD RH LA LO CR SP`; second sensor shown as `AT-2`; 30 s FileWriteInterval | `FormatTransform` + `LogfileWriter` | Partial: need header-on-new-file support |
| .COR and .UNC: $WICOR / $WIUNC lines with quality-digit tags | none | **Gap**: WICOR formatter plus parser (OpenVDM PR #409 parser to borrow from) |
| ACQ config copied next to each day's data | `server/config_snapshot.py` | Partial: verify per-day snapshot |
| Daily .LOG (MK_LOG, written about 2200 GMT) | standard logging | Have |
| SAMOS daily exchange file | none | Gap |
| Database / time series store | `DatabaseWriter`, `InfluxDBWriter`, `RedisWriter` | Have (MetAcq had none) |
| Playback; regenerate .COR/.MET from .UCR/.UNC with an updated ACQ | `LogfileReader` + same transform chain | Have, better than MetAcq |
| Emulation mode (fake sensors, flag 8, `*`/`E` markers) | `logger/utils/simulate_serial.py`, `simulate_network.py` | Have, but no "emulated" flag in output |

File names: `yymmdd.MET`, `.UCR`, `.COR`, `.UNC`, `.ACQ`, `.LOG` (e.g. `030427.MET`). User output files `.M00`, `.M01`.

### 4. Outputs and broadcasts

| MetAcq feature | OpenRVDAS today | Status |
|---|---|---|
| $WICOR UDP broadcast (e.g. `UNIT65 19 UDP 40019 NONE 40119 10.110.150.255 0`), 1 s | `UDPWriter` | Partial: needs WICOR formatter |
| Serial repeat of nav (GLL/VTG/HDT/DBT) to MRU, Seatel, multibeam | `SerialWriter`, `UDPWriter` | Have |
| Sound velocity to Kongsberg EM / Seabeam | writers + formatter | Partial: per-target format strings |
| User-defined output modules (SERUNITNUM, PARAMETERS, PRECISION, INTERVAL, MK_OUTFILE, ADDCRC, ADDTIMESTAMP, LEADER, NMEA, DELIMITERS, printf FORMAT) | `FormatTransform`, `NMEAChecksumTransform`, `PrefixTransform` | Have |
| Winch data to signboards (code 15, Healy) | none | Gap (scoreboard writer thread) |
| Email: SAMOS daily zip, OPSUM hourly, PCO2, SIO SHIPTRACK (1 WICOR per minute, subject `WICOR_<cruise>`), NOAA hourly ship weather report (subject `ShipTrackerMessage`) | `EmailWriter` | Partial: transport exists, message formats missing |
| Cascade mode (second PC mirrors primary) | `UDPReader` + `CachedDataServer` websockets | Have |

### 5. Displays

| MetAcq screen | What it shows | OpenRVDAS today | Status |
|---|---|---|---|
| Strip Chart6 #1/#2, Strip Chart8 (up to 20 strips, 30 numeric tiles, 24 h default, history scroll, per-plot autoscale/min/max/decimals, choose among redundant sensors) | Rolling time series | Highcharts widgets via `CachedDataServer` (`display/js/widgets`); Grafana | Partial: no history scroll back, no per-strip scale UI |
| Tabulated, Tabulated-GPS | 30 numbers plus position | `text_widget.js`, `display/html/fields.html` | Partial |
| MetBig | Huge met values plus winch for the bridge | none purpose-built | Gap |
| Winch | Wire out (m), speed (m/min), tension (lbs) plus tension strip chart; CTD depth, speed, altimeter; winch names WID1-9 | none | Gap |
| GPS / Waypoints | ETA, TTG, bearing to station | none | Gap |
| Diagnostic | Raw strings per port, INOP per value | Django GUI logger status | Partial |
| Status bar | Scans per second (should stay above 0.5), current file and size, CHK MOD (non-responding sensors), cruise name | Logger manager status | Partial: no per-sensor "not responding" list |
| Web: PNG snapshot of each screen every 10 s (Apache or LabVIEW server) | Shore and low-bandwidth viewing | none | Gap |

### 6. Alarms

MetAcq has **no real alarm system** in any version. Closest features: CHK MOD list of silent sensors, RANGE limits, flag digits 7 and 9. OpenRVDAS has the same ingredients (`TimeoutReader`, `TimeoutWriter`, `QCFilterTransform`) but no alarm manager. Easy place to exceed MetAcq: stale-sensor, out-of-range, and rate-of-change alarms with acknowledge, shown on every display.

## Where Grafana falls short (input for the display layer)

1. **Ship-relative geometry.** No wind rose oriented to ship heading, no relative vs true wind dial, no ship-up compass.
2. **Operational views.** Winch tension with safe working load bands, CTD depth vs altimeter during a cast, ETA to next station.
3. **Big-number readability.** MetBig and signboards need huge, high-contrast, red night-mode values.
4. **Data quality in the picture.** Every value should show its flag (calibrated, out of range, emulated, stale).
5. **Sub-second live updates.** The OpenRVDAS websocket cache is lower latency than Grafana panels.
6. **Low-bandwidth shore view.** Periodic PNG or compact JSON snapshots sized for VSAT.
7. **Event context.** Station, cast, and Sealog events on the same timeline.
8. **Zero-config per ship.** Build screens from the logger config so a new sensor appears without hand-built panels.

## Build checklist, in priority order

1. [ ] Download Rev 2.15 PDF; read sections 10, 11 and Appendix A (exact $WICOR tag list, column layouts, formulas). Get SIO's `wicor_params.yaml`.
2. [ ] Vector averaging: `VectorAverageTransform` or a `vector_average` algorithm in `logger/utils/subsample.py`.
3. [ ] `WicorFormatTransform` plus `WicorParseTransform`; tags and units from YAML; quality digit per value.
4. [ ] Calibration layer: per-sensor YAML (serial, cal date, method, coefficients) applied by `ComputedFieldsTransform`; named methods for the top 10 (offset, slope/offset, polynomial, thermistor, RTD, SBE T/C, Eppley SWR/LWR, SBE43).
5. [ ] Met formula library: dew point, wet bulb, sea-level pressure; salinity/sigma-t/sound speed via `gsw`.
6. [ ] Device YAMLs for the MetSpecs sensor list.
7. [ ] Alarm manager: stale, range, rate-of-change, acknowledge, per-sensor health list.
8. [ ] Daily .MET/.COR writer with headers; SAMOS daily file; NOAA hourly email format.
9. [ ] Display layer: strip charts with history, MetBig/night mode, winch, waypoint ETA, ship-relative wind, quality flags, shore snapshots.

## Open questions

- Is the target one specific ship (Revelle, Sproul, Sally Ride) whose exact $WICOR tag order must match, or a generic replacement?
- Do downstream consumers (bridge PCs, multibeam, CalCOFI) depend on byte-exact legacy formats? If yes, formatters must be byte-exact and tested against real sample files.

---

# Appendix: reference detail extracted from the manuals

## A1. Sensor module types (Rev 2.12 / 2.15, 36 types; Rev 1.84 had 30)

TMP air temp (AT, AF, WC, WF) · HRH humidity (RH, RT, DP) · BPR barometer (BP, comp temp) · PRC precipitation (PR, PT) · WND wind (WS, WD; TW, TI true) · SWR short wave · LWR long wave (dome, body temp, thermopile V) · FLW flowmeter · SST sea surface temp · SSC conductivity · VLT A/D volts · FLU fluorometer · XMS transmissometer · OXY oxygen · TSG thermosalinograph (TT, TF, TC, SA, SD, SV) · USP user defined · PAR surface PAR · AWT aux water temp · AXT aux air temp · IST instrumentation/CTD (IP, IT, IS, IA, IV, IX) · PRS pressure · PDR water depth · NME NMEA nav (LA, LO, GT, CR, SP, ZD, GA, GS) · GYR gyro · ASH Ashtech heading/pitch/roll · TSV time server · WCH winch (wire out, speed, tension) · ALK alkalinity/pH · VRU pitch/roll/heave · SOW speed over water · UCW uncontaminated seawater pump status · MBD multibeam center depth · PCT pCO2 · SND depth sounder · MAG magnetometer · GRV gravimeter.

Each type has default value counts, precision, tags and MIN/MAX range, overridable with TAGS-C, TAGS-R, PRC-C, PRC-R, RANGE.

## A2. NMEA sentence to parameter map (Rev 2.12)

GGA/GNS/GLL to LA LO GT GA GS (NME) · VTG to CR SP · RMC to LA LO GT CR SP ZD GA GS · HDT to GY (GYR) · ZDA to ZD · MWV to WS WD (WND) · PASHR ATT to SH SM SR (ASH) · VHW to SL (SOW) · VBW to SL SX · DBT to BT (PDR) · PKEL99 to LF HF BT (SND) · DPT to MB (MBD).

## A3. MSP device types (Rev 2.12)

0 RS485 sensor · 1 RS485 DGH analog · 2 RS485 ADAM · 3 RS232 continuous · 4 time server (old) · 6 SBE21 TSG · 7 Simrad EM VRU · 8 NMEA RS232 · 9 RS485 DGH digital hex · 10 Hippy 120 VRU (old) · 12 NMEA UDP (old) · 14 NMEA UDP · 15 UDP non-NMEA · 17 ADAM frequency (4080) · 18 NI DAQ/USB · 21 SeaSpy magnetometer · 22 BGM-3 gravimeter.

## A4. Calibration methods (MCP), Rev 2.12

0 none · 1 offset · 2 offset (+/-360 deg) · 3 slope, offset · 4/5 polynomial (with and without X) · 6/7 polynomial with DT · 8 LWR Eppley · 9 thermistor · 10 RTD · 11 Seabird T · 12 Seabird C · 13 slope, offset x Y · 14 slope, offset, DT (BP cal) · 15 dew point · 16 salinity · 17 density · 18 sound velocity · 19 true wind speed · 20 true wind direction · 21/22/34 oxygen SBE13/SBE43 · 23 O2 saturation · 24 beam attenuation (1.84) · 25 pH SBE-18 · 26 SWR · 27 LWR Kipp & Zonen · 30 formula (EVAL/COR with sqrt, log, exp, trig) · 31 Aanderaa optode O2 salinity-corrected · 32/33 lat/lon antenna offset · 35 Seabird C without slope/offset · 37 sea-level pressure · 38/39 transmissometer · 40 Rinko III O2 · 41 wet bulb · 42/44 humidity sensors.

MCP field 1: applied in acquisition program (1) or sensor module (2); then count of computed parameters; then method per parameter. Averaging: AVGTYPE 0 none, 1 normal, 2 wind vector; SECSTOAVG seconds.

## A5. [GENERAL] keys and defaults

TITLE, SHIP, CALL_SIGN, MKCRUISEDIRS, MK_MET (TRUE), MK_UCR (TRUE), MK_COR (FALSE), MK_UNC (FALSE), MK_LOG (FALSE), MK_DCC (FALSE), CHART_RATE (2.0 s in 2.12; 20 s in 2.15 summary), TIMEOUT (300 ms), FileWriteInterval (30 s), SerialWriteInterval (30 s), DCC_INTERVAL (60 s), MAX_SCAN_RATE (10 s), ONEGPS2FILE, SPARSCL, GPS_SYNCH (TRUE), WID1-9, RD485MINTO (0.05), RD485MAXTO (0.32 / 0.5), MAIL_SERVER, MAIL_RETADD, MAIL_RECEP, MAIL_OPSUM, MAIL_PCO2, MAIL_NOAA, OUTPORT_PCO2, SHIPTRACK_RECEP, SOUDPL (60201), SOUDPR (61557), SET_TRACE, WRT_IMAGE.

Per-module keys: SENSOR, MODEL, MFG, SERIAL, OWNER, CAL_DATE, CAL_LAB, LOCATION, INSTALL_DATE, COMMENTS, SENSORTYPE, CMD, MSP, MCP, TAGS-C, TAGS-R, PRC-C, PRC-R, EMULATION, AVGTYPE, SECSTOAVG, ADCALTYPE, UCR_RANGE, ADCAL, EVAL, COR, RANGE, ADDTOFILE, DELIMITERS, EMPTY_TOKS, LABELS-SC, LABELS-TAB, SLD, TLD, DCC, DCC_MASK, SAMOS_LD (numbered CMD2/MSP2/COR2 for multi-source sensors).

Port line: `UNITn <type code> <COM|UDP> <baud|port> <parity> <bits|port> <stop|IP> <interval>`. Defaults 9600 8N1; UDP remote 61553, local 61552, receive 61551.

## A6. Output type codes (Rev 2.12)

2 MET · 3 UNC · 4 COR · 5 Seabeam 2100 SV (5 s) · 6 Seabeam 2100 nav (1 s) · 7 Seabeam 2000 nav · 8 DCC serial · 9 DCC UDP · 10 VTG/HDT to MRU (1 s) · 11 EM120 SV UDP · 12 GLL/HDT to Seatel · 13 EM120 SV serial · 14 surface PAR · 15 winch to signboard (Healy) · 17 CalCOFI 2003 stream (`$WICCI,ddmmyy,hhmmss,AT,BP,TK,TI,TT,SA,FL,LA,LO,T*cs`, 5 s) · 18 GLL/VTG/DBT/HDT · 19 MET corrected UDP · 20 user serial · 21 EM120 SV UDP secondary · 22 nav to mapserver (Healy) · 23 EM120 SV serial secondary · 70 DAQ IO in · 80 UDP in · 81 user UDP out · 82/83 multicast.

## A7. $WICOR tags (from OpenVDM issue #408 and manual)

Format: `$WICOR,ddmmyy,hhmmss,<value>,<TAG><flag>,...*hh`. Tags can repeat for a second sensor; order depends on ship config.

CN cruise ID · AT air temp C · BP pressure mbar · BS sea-level pressure (likely) · RH %RH · RT RH-module temp · DP dew point · PR precip mm · PT precip rate mm/hr · PA PAR uE/s/m2 · WS/WD relative wind m/s, deg from · TW/TI true wind m/s, deg from · TT TSG temp · TC conductivity with slope/offset mS/cm · TG conductivity raw · SA salinity PSU · SD sigma-t · SV sound velocity m/s · FL fluorometer ug/l · OT/OX/OS oxygen temp, ml/l, saturation · FI seawater flow LPM · ST SST · BT bottom depth m · LF/HF echosounder low/high freq depth (likely) · LA/LO decimal deg · GT GPS seconds since midnight · ZD Unix time · CR COG deg · SP SOG kn · GA altitude m · GS GPS status+sat count (211 = status 2, 11 sats) · GY gyro · ZO/ZS/ZT/ZI winch wire out m, speed m/min, tension lbs, winch ID (likely) · IP/IV/IA CTD depth, velocity, altimeter · SW/LW radiation W/m2.

## A8. MetSpecs Rev 1.18 sensor list (New Horizon, Sproul, Revelle, Melville)

| Type | Make/model | Range | Accuracy | Output |
|---|---|---|---|---|
| Air temp | RM Young 41342LC / 41342VC | -50 to 50 C | 0.3 C | 4-20 mA / 0-1 V |
| Precip | RM Young 50202 | 0-50 mm | 1 mm | 0-5 V |
| Wind | RM Young 05103 | 0-60 m/s, 0-360 | 0.3 m/s, 3 deg | V / pulse |
| Wind | Vaisala WS425 | 0-65 m/s | 0.14 m/s, 2 deg | RS232 |
| Wind | RM Young 85000 / 85106 | 0-70 m/s | 0.1 m/s, 2 deg | RS232 |
| RH/temp | Vaisala HMP45A, HMP155; RM Young 41382VC | 0-100% | 2% | 0-1 V / RS232 |
| Barometer | RM Young 61302V; Vaisala PTB101C | 500-1100 mb | 0.2-0.3 mb | V / RS232 |
| LWR | Eppley PIR; Kipp & Zonen CG4 | 3.5-50 um | 1% | 0-10 mV |
| SWR | Eppley PSP, 8-48; Kipp & Zonen CM21 | 285-2800 nm | 0.25-1% | 0-100 mV |
| PAR | Biospherical QSR-240P, QSR-2200 | 400-700 nm | n/s | 0-5 V |
| TSG | Seabird SBE-45 | -5 to 35 C, 0-70 mS/cm | 0.002 C, 0.003 mS/cm | RS232 |
| Fluorometer | WetLabs WetStar; Seapoint SCF | 0.03-75 ug/l | | 0-5 V |
| Oxygen | Seabird SBE-43 | 120% sat | 2% | 0-5 V |
| SST | STS SEG-14 | -2 to 35 C | 0.1 C | RS232 |
| Flow | Signet 515-PO; FLO-CAT C-ES45-B002/B003 | 0-80 GPM / 0.27-37.9 LPM | 1% FS | pulse |

## A9. Version differences (1.84 vs 2.12 vs 2.15)

- Platform: Win2000 only (1.84); Win XP/7/8 + 32-bit Linux (2.12); Win 7/8/10 + 64-bit Linux (2.15).
- Ports: 34 to 128. 2.12 adds UDP in/out codes, multicast, DCC, Healy-specific outputs; drops `$WICCI` CalCOFI stream from the table.
- Displays: 1.84 Strip Chart4/6/8, Fixed, print; 2.12+ Strip Chart6 #1/#2, Strip Chart8, MetBig, Diagnostic; 18 to 20 strips.
- Email section (SAMOS, OPSUM, PCO2, SHIPTRACK, NOAA) added in 2.12.
- Web: 1.84 LabVIEW `.snap`/`.monitor` URLs; 2.12+ Apache or LabVIEW, PNGs every 10 s.
- Alarms: none in any version.
