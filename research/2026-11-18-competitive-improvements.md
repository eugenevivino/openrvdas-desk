# OpenRVDAS competitive analysis and roadmap

As of 2026-11-17. Prepared for Eugene. Live, editable version: https://claude.ai/artifact/H3523sKMcYXJK6bsjRfTpN

## Recommendation

Build an open, cruise-aware application layer on top of OpenRVDAS, called here the **Cruise Console**, and ship it in three phases. The acquisition core is not the gap. The gap is everything people touch: sensor metadata, health, event logging, QC flags, clean downloads, and a display that a bridge officer or a chief scientist can read in two seconds.

Why this, and not more acquisition features:

- **CORIOLIX already runs on OpenRVDAS.** OSU's own 2025 tutorial says CORIOLIX "uses OpenRVDAS for core data collection" and "wraps a lot of handy cruise management tools around it" ([RVTEC 2025](https://www.unols.org/sites/default/files/2025-12/202511rvtec_cohn_david_openrvdas_coriolix_1.pdf)). The value users praise lives in that wrapper, and no public license for it was found.
- **OpenRVDAS' own display story is a hole.** Its docs call the native widgets "by and large deprecated" and point users to Grafana ([quickstart GUI](https://davidpablocohn.github.io/openrvdas-docs/quickstart_gui/)). Grafana is a strong generic tool but knows nothing about cruises, stations, sensors, or watch handovers.
- **Commercial systems compete on polish, not physics.** Kongsberg Blue Insight and Werum DSHIP sell maps, preconfigured bridge/winch/weather displays, action logs, and shore archives ([Kongsberg](https://www.kongsberg.com/news/news-archive/2025/transforming-ocean-data-management/), [DSHIP](https://www.werum.de/files/werum/documents/download/Werum_BR-E_DSHIP_Information-Management-for-Earth-Science-Data.pdf)). An MIT-licensed equivalent would be unique.

First three moves, in order:

1. **Health board plus sensor registry** (4 to 6 weeks). One screen that says which instruments are live, stale, or out of range, backed by a sensor table with calibration dates. Technicians feel it on day one.
2. **Role-based display kit** (6 to 10 weeks). A cruise-aware web UI with four ready layouts: bridge, science, tech, shore. Open-source charting only.
3. **QC flags, 1-minute binning, and downloads** (6 to 8 weeks). Matches CORIOLIX's most-used data products and feeds R2R and SAMOS.

Before writing code, talk to OSU's CORIOLIX team and David Cohn. If CORIOLIX is open or about to be, contribute and interoperate. If not, design the data model so a ship can move between the two without retyping its sensor list.

## Glossary

Terms used once and then assumed.

| Term | Plain meaning |
| --- | --- |
| DAS | Data acquisition system: software that reads every sensor on the ship, timestamps it, logs it, and shows it. |
| Underway data | Continuous measurements taken while the ship moves: position, weather, sea surface temperature, salinity, depth, and so on. |
| UNOLS | University-National Oceanographic Laboratory System, the US academic research fleet (about 17 ships). |
| R2R | Rolling Deck to Repository, the NSF program that archives every US academic cruise's underway data and checks its quality. |
| NMEA 0183 | The plain-text serial sentence format most marine instruments speak, for example `$GPGGA,...` for GPS position. |
| SCS | Scientific Computer System, NOAA's long-running shipboard DAS. |
| MetAcq | Scripps' meteorological acquisition system, run on its ships. |
| CORIOLIX | A web-based cruise data system built at Oregon State and used on several UNOLS ships. |
| Logger | In OpenRVDAS, one pipeline of readers, transforms, and writers for one data stream. |
| Cache data server (CDS) | OpenRVDAS' in-memory websocket server that live displays read from. |
| Event log | A structured, timestamped record of science activity: CTD casts, net tows, station arrivals. |
| Headless | Runs without its own screen; you reach it from a browser. |
| Bandwidth-aware sync | Sending ship data to shore in a way that fits a thin, costly satellite link. |

## Landscape

Seven systems matter. Three are open or free, three are commercial, one is the generic dashboard everyone falls back on.

| System | Who runs it | What it is good at | UX: pleasant | UX: painful |
| --- | --- | --- | --- | --- |
| [OpenRVDAS](https://davidpablocohn.github.io/openrvdas-docs/about/) | OceanDataTools, MIT license, since 2017 | Flexible reader/transform/writer pipelines, modes (Port, EEZ, Underway), websocket cache | Mode switch is one dropdown; YAML is diffable | GUI is a logger table; native widgets deprecated and Highcharts-based; displays require Grafana setup |
| [CORIOLIX](https://coriolix.sikuliaq.alaska.edu) | Oregon State, on Sikuliaq, Endeavor, Point Sur; planned Taani, Savannah | Cruise tools, event log, sensor/parameter status, metadata, QC flags, binned downloads, REST and ERDDAP, ship-shore sync, alerts | Purpose-built menus (Flowthrough, Met, Nav, CTD plots); dark mode added in 3.0 | Inference: menu-heavy admin feel; 3.0 broke backward compatibility ([release notes](https://coriolix.sikuliaq.alaska.edu/about/release)) |
| [NOAA SCS](https://scsshore.noaa.gov/) | NOAA, since 1989 | Acquisition, delta and range checks, browser displays, shore portal | Mature, documented, video tutorials | Inference: Windows/.NET heritage; NOAA-centric |
| [MetAcq](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf) | Scripps STS | Met acquisition, calibrations, true wind, SAMOS email | Fixed modes (strip charts, MetBig, Winch, Tabulated-GPS with ETA) are instantly legible | LabVIEW runtime, Windows-first, web view is a 10-second image refresh |
| [Werum DSHIP](https://www.werum.de/files/werum/documents/download/Werum_BR-E_DSHIP_Information-Management-for-Earth-Science-Data.pdf) | German fleet: Meteor, Polarstern, Sonne | Plug-and-play devices, Action Log, preconfigured nav/winch/weather displays, multi-ship archive, redundancy | Ready-made displays per role | Proprietary, vendor-dependent |
| [Kongsberg Blue Insight Geomatics](https://www.kongsberg.com/news/news-archive/2025/transforming-ocean-data-management/) (replacing [MDM 500](https://kongsberg.com/maritime/products/information-management-system/mdm-500)) | Kongsberg, launched 2025 | Georeferenced dashboards, maps, time-series, cloud mirroring, uncrewed vessels | Modern map-first design | Proprietary; MDM needed Windows clients and SQL Server |
| Grafana + InfluxDB | Generic, open source | Time-series panels, alerting, huge plugin ecosystem | Fast to build a panel; good dark theme | Inference from common use: no concept of cruise, station, sensor, or calibration; dashboards drift per ship; edit mode is easy to break at sea |

Adjacent open tools in the same family: **Sealog** (event logging for ROV and science ops) and **OpenVDM** (file transfer and cruise data packaging), both part of OceanDataTools ([about](https://davidpablocohn.github.io/openrvdas-docs/about/)). NOAA's [hybrid data management](https://oceanexplorer.noaa.gov/about/what-we-do/media/hybrid-approach-data-acquisition-management.pdf) work on Okeanos Explorer is OpenVDM's ancestor.

## Comparison table

OpenRVDAS leads on open pipelines and loses on everything a non-programmer touches. Yes = documented on a page cited here. Partial = exists but limited. No = not found in docs read. Grafana is scored as it ships with OpenRVDAS.

| Capability | OpenRVDAS | CORIOLIX | SCS | MetAcq | DSHIP | Kongsberg | Grafana |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Open-source license | Yes (MIT) | Not found | Free, license not stated | Not stated | No | No | Yes |
| Serial/UDP acquisition | Yes | Via OpenRVDAS | Yes | Yes | Yes | Yes | No |
| Cruise as a first-class object | Partial (cruise YAML) | Yes | Unknown | No | Yes | Unknown | No |
| Sensor registry with calibrations | No | Yes | Unknown | Partial (config file) | Yes | Unknown | No |
| Health / status board | Partial (logger status) | Yes | Partial (I/O monitor) | Partial (CHK MOD) | Yes | Yes (MDM alarms) | Partial |
| Science event log | No (Sealog separate) | Yes | No | No | Yes (Action Log) | Yes (cataloguing) | No |
| QC flags on every value | No | Yes | Partial (delta/range) | Partial (range) | No | No | No |
| Binned products (1-min) | No | Yes | Unknown | Yes | Unknown | Unknown | Partial |
| Ship track map | Deprecated widget | Yes | Unknown | No | Yes | Yes | Plugin |
| Role-specific ready displays | No | Partial (plot groups) | Partial | Yes | Yes | Yes | No |
| Alerts (station arrival, thresholds) | No | Yes | No | No | No | Yes | Yes |
| Ship-to-shore sync | Partial (replication writer) | Yes, bidirectional | Yes | Email | Yes | Yes (cloud) | No |
| REST API / ERDDAP | Partial (CDS HTTP GET) | Yes / Yes | API listed | No | Web services | Unknown | API |
| SAMOS / R2R export | No | Yes | Unknown | Yes (SAMOS) | Unknown | Unknown | No |

Sources for each cell are the pages linked in Landscape. "Unknown" means the page did not say, not that the feature is missing.

## Opportunities by user group

Each group needs a different first screen. Effort assumes one experienced developer: S under 2 weeks, M 2 to 6 weeks, L 2 to 3 months.

### Science party

They want to know: are my instruments logging, where are we, and can I get clean data tonight.

| Need | Competitors | OpenRVDAS gap | Proposed feature | Effort |
| --- | --- | --- | --- | --- |
| Log a CTD cast or net tow in 10 seconds | CORIOLIX event log, DSHIP Action Log | None built in | Event buttons with auto-filled position, time, depth; Sealog bridge | M |
| Download what I need, not raw files | CORIOLIX date/parameter/resolution/format picker | Raw logfiles only | Download builder: CSV, NetCDF; raw or 1-min binned; flagged | M |
| Trust the numbers | CORIOLIX flags on every value | No flags | QC flag column plus colored badges in every plot | M |
| See the section, not a line | Kongsberg map-first views | No section view | Along-track section plot (variable vs distance) and map color by variable | M |

GUI concept, **Science Home**: left half is the live map with ship track colored by the variable you pick (SST, salinity, chlorophyll). Right half is a stack of sparklines, one per instrument, each with a green, amber, or red dot. A big "Log event" button sits top right.

### Bridge

They want a glanceable, night-safe display that never makes them hunt.

| Need | Competitors | OpenRVDAS gap | Proposed feature | Effort |
| --- | --- | --- | --- | --- |
| Wind, heading, speed, depth at a glance | MetAcq MetBig, DSHIP nav/weather displays | Build-your-own Grafana | Fixed bridge layout with huge numerals | S |
| No night-vision damage | ECDIS night palettes (common practice) | None | Red/dim night mode with one tap, auto by sun elevation | S |
| ETA and distance to station | MetAcq Tabulated-GPS, CORIOLIX proximity alerts | None | Waypoint list with ETA, distance, bearing; arrival chime | M |
| Wire out and tension during deployments | MetAcq Winch mode, DSHIP winch display | None | Winch panel with tension limits and big red over-limit state | S |

GUI concept, **Bridge Wall**: dark, four quadrants, numerals at least 15 percent of screen height, true wind arrow on a compass rose, a single amber strip at the bottom listing anything stale. No menus visible. Kiosk mode by URL.

### Technicians

They want to find a dead sensor before the scientist does, and fix it without SSH.

| Need | Competitors | OpenRVDAS gap | Proposed feature | Effort |
| --- | --- | --- | --- | --- |
| What is broken right now | CORIOLIX sensor/parameter/system status, SCS I/O monitor | Logger running is not data flowing | Health board: last-seen age, rate, range check per field | M |
| Sensor registry and calibrations | CORIOLIX sensor list, cal docs, import/export between instances | YAML only | Sensor registry UI that generates OpenRVDAS config (CORIOLIX does this) | L |
| Add an instrument without writing YAML | DSHIP "plug, configure and play" | Hand-edited YAML | Add-instrument wizard with live raw-line preview and parser test | M |
| Change log | CORIOLIX sensor log | Git, if used | Audit trail of config, cal, and mode changes, with who and why | S |

GUI concept, **Tech Board**: a grid of instrument tiles. Each tile shows name, last raw line, records per second, and a 10-minute sparkline. Click a tile to see raw serial, parsed fields, and calibration due date side by side.

### Shore support

They want to help a ship without a VPN session and without eating bandwidth.

| Need | Competitors | OpenRVDAS gap | Proposed feature | Effort |
| --- | --- | --- | --- | --- |
| See what the ship sees | CORIOLIX shore mirror, SCS shore, Kongsberg cloud | Replication writer, no shore UI | Shore mirror of the same UI fed by binned sync | L |
| Fit the satellite link | CORIOLIX ships 1-min bins; MetAcq emails | No budget control | Bandwidth budget: bins over the link, raw at port | M |
| Fleet overview | DSHIP multi-ship archive | None | Fleet page: every ship's position, health score, last sync | M |
| Feed SAMOS and R2R automatically | CORIOLIX, MetAcq | None | Daily SAMOS file and end-of-cruise R2R package | M |

GUI concept, **Shore Ops**: a world map with one dot per ship, colored by health. Click a ship to open its Tech Board, read-only, showing the age of the last sync in large type so nobody mistakes stale for live.

## Ranked roadmap

Ranked by value per week of effort and by how many user groups each item serves. Phase gates are the criteria to pass before starting the next phase.

| Rank | Item | Serves | Effort | Why this rank |
| --- | --- | --- | --- | --- |
| 1 | Health board (last-seen, rate, range per field) | Tech, bridge, shore | M | Highest pain, reuses the cache data server, no schema change |
| 2 | Design system plus Bridge Wall layout with night mode | Bridge | S | Small, visible, proves the GUI direction |
| 3 | Sensor registry with calibrations and change log | Tech, shore | L | Foundation for QC, metadata export, R2R |
| 4 | Replace Highcharts widgets with an open library (ECharts or uPlot) | All | M | Removes license risk; CORIOLIX made the same move in 3.0 |
| 5 | Event log with Sealog bridge | Science | M | Most-cited CORIOLIX and DSHIP feature |
| 6 | QC flags and 1-minute binning | Science, shore | M | Unlocks downloads, SAMOS, shore sync |
| 7 | Download builder and REST endpoints | Science | M | Ends "email me a CSV" requests |
| 8 | Live map with colored track and waypoint ETA | Science, bridge | M | Replaces deprecated map widget |
| 9 | Shore mirror with bandwidth budget | Shore | L | Needs 3 and 6 first |
| 10 | SAMOS and R2R exporters | Shore, science | M | Program compliance; easy once 3 and 6 exist |
| 11 | Add-instrument wizard | Tech | M | Highest polish payoff once registry exists |
| 12 | Fleet page | Shore | M | Only after two or more ships run the mirror |

Phases:

1. **Phase 1, Visible wins (about 3 months): items 1, 2, 4.** Gate: one ship's tech uses the health board through a full cruise and reports a dead sensor caught earlier than before.
2. **Phase 2, CORIOLIX parity core (about 4 months): items 3, 5, 6, 7, 8.** Gate: a science party downloads flagged 1-minute data without help.
3. **Phase 3, Ship to shore (about 4 months): items 9, 10, 11, 12.** Gate: shore sees health within one sync interval on a real satellite link.

Architecture rule for all phases: the console reads OpenRVDAS through the cache data server and a time-series store, never by patching logger internals. That keeps it a separate, optional package the upstream maintainer can accept without risk.

## Bold ideas (go wild)

These are deliberately ambitious and unranked. Each is labeled with its biggest risk.

| Idea | What it does | Biggest risk |
| --- | --- | --- |
| **Ask the ship** | Natural-language questions over live and logged data: "When did salinity drop below 33 today?" returns a plot and the query used. Runs on a local model when offline. | Wrong answers stated confidently; must always show the query |
| **Anomaly sentinel** | Learns each sensor's normal behavior and flags drift, spikes, or a frozen value before range checks trip. Catches a fouled thermosalinograph intake. | False alarms train people to ignore it |
| **Watch handover card** | Auto-generated one-page summary every 4 hours: events, alarms, sensor changes, weather trend. Printable for the log. | Low, mostly design |
| **Cruise replay** | Scrub a timeline and every panel, map, and event replays as it happened. Great for incident review and teaching. | Storage and indexing cost |
| **Science opportunity alerts** | "Front ahead: SST gradient 0.5 C per km in 8 nm" from live data plus satellite overlays. | Satellite data needs bandwidth |
| **Digital twin view** | 3D ship model with sensor locations; click the anemometer to see its data and calibration. | Effort; per-ship models |
| **Public outreach page** | Safe, delayed public feed for classrooms and families: map, photos, weather. | Security review; must be one-way |
| **Offline-first shore sync** | Treat the link as a queue that heals itself, CRDT-style, so ship and shore never conflict. | Hard to get right; test on real links |
| **Fleet benchmark** | Compare sensor uptime and data completeness across ships running the console. | Needs adoption first |
| **Instrument library** | Shared, versioned parser and metadata packs per instrument model, installable in one click. | Governance of contributions |

The two worth prototyping early are the watch handover card (cheap, loved) and the anomaly sentinel (genuinely beyond Grafana and CORIOLIX).

## Facts, inferences, open questions, sources

**Verified on the pages cited:** CORIOLIX uses OpenRVDAS for collection and auto-generates its configs; CORIOLIX 3.0 (March 2026) moved to ECharts and TimescaleDB; OpenRVDAS is MIT and its native widgets are deprecated; MetAcq is LabVIEW-based; DSHIP has an Action Log and preconfigured displays; Kongsberg launched Blue Insight Geomatics in 2025 to replace MDM.

**Inference, not verified:** the UX pain points marked "Inference" in Landscape; effort estimates; that Grafana dashboards drift per ship.

**Open questions:**

- [ ] Is CORIOLIX source public, and under what license? A 2022 milestone planned to open its repo by September 2023; no repo was found.
- [ ] Would OSU accept shared data models (sensor registry, event schema) so ships can move between systems?
- [ ] Does David Cohn want the console in the main repo, a sibling repo, or a plugin?
- [ ] Which ship can host the Phase 1 pilot?
- [ ] Not reviewed yet: Schmidt Ocean Institute pipeline (page needs JavaScript), SCS display screens, Grafana's OpenRVDAS dashboards.

**Sources opened:**

- [OpenRVDAS + CORIOLIX tutorial, RVTEC 2025](https://www.unols.org/sites/default/files/2025-12/202511rvtec_cohn_david_openrvdas_coriolix_1.pdf)
- [CORIOLIX, Sikuliaq](https://coriolix.sikuliaq.alaska.edu) and [release notes](https://coriolix.sikuliaq.alaska.edu/about/release)
- [CORIOLIX data format](https://hmsc-cms.dri.oregonstate.edu/data/format/)
- [UNOLS RVTEC 2023 CORIOLIX slides](https://www.unols.org/sites/default/files/2023-11/202310rvt_apxxxvi.pdf) and [2022 slides](https://www.unols.org/sites/default/files/202211rvt_apXXIV.pdf)
- OpenRVDAS docs: [about](https://davidpablocohn.github.io/openrvdas-docs/about/), [display widgets](https://davidpablocohn.github.io/openrvdas-docs/display_widgets/), [cached data server](https://davidpablocohn.github.io/openrvdas-docs/cached_data_server/), [Django interface](https://davidpablocohn.github.io/openrvdas-docs/django_interface/), [quickstart GUI](https://davidpablocohn.github.io/openrvdas-docs/quickstart_gui/)
- [NOAA SCS shore](https://scsshore.noaa.gov/)
- [MetAcq operator's manual, rev 2.15](https://downloads.psl.noaa.gov/psd3/cruises/ASTRAL_2023/Revelle/docs/MetAcq.pdf)
- [Kongsberg Blue Insight Geomatics](https://www.kongsberg.com/news/news-archive/2025/transforming-ocean-data-management/) and [MDM 500](https://kongsberg.com/maritime/products/information-management-system/mdm-500)
- [Werum DSHIP brochure](https://www.werum.de/files/werum/documents/download/Werum_BR-E_DSHIP_Information-Management-for-Earth-Science-Data.pdf)
- [NOAA hybrid data acquisition and management](https://oceanexplorer.noaa.gov/about/what-we-do/media/hybrid-approach-data-acquisition-management.pdf)
