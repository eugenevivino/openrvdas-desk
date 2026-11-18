# Pain points study (verbatim)

Source: Deep Research report run by Eugene, pasted into the project chat 2026-11-18 08:44Z. Saved verbatim below this line; nothing edited. Gap map and reprioritization: `docs/PAIN-POINTS-MAP.md`.

---

Shipboard Data Acquisition and Technical Operations: Evidence-Backed Pain Points, Workarounds, and Product Opportunities
Research method and evidence model
This review prioritizes operator-facing and primary operational evidence over vendor descriptions. The core evidence set includes UNOLS/RVTEC material; Rolling Deck to Repository, or R2R, quality-assurance documentation; SAMOS annual quality reports; Multibeam Advisory Committee, or MAC, technical reports; UHDAS operational and failure-mode documentation; OpenRVDAS/OpenVDM repositories and issue trackers; NERC/BAS/NOC acquisition-system reports; CSIRO voyage archives; Schmidt Ocean Institute operational documentation; official NOAA SCS documentation; and IMO/IACS cybersecurity requirements. Secondary sources were used only where they added operational context not available from a primary source. 

Evidence labels used below: DIRECT EVIDENCE means the source explicitly documents the problem, workaround, requirement, failure, or requested capability. INFERENCE means the product implication is derived from one or more documented operational facts. Severity is my assessment of impact on mission data, ship operations, or technician workload, not a value assigned by the cited source. Frequency is deliberately qualitative. “Frequent” means the same class of issue appears across multiple vessels or independent operational sources; “recurrent” means repeated within a fleet/program or documented failure-mode catalogue; “occasional” means fewer independent observations. The evidence counts in the ranking are minimum counts of independent source artifacts reviewed that materially support the theme, not counts of vessels, incidents, or prevalence estimates.

The strongest systematic dataset in the corpus is SAMOS. Its 2022 report covered 29 routinely reporting vessels and documented major problems spanning bad sensor placement, reversed anemometers, seawater plumbing faults, long-running failed sensors, acquisition channels representing nonexistent sensors, calibration/configuration mistakes, unit errors, environmental contamination of sensors, and transmission failures. The report explicitly notes that 11.4 million of roughly 213 million individual measurements received in 2022 received non-“good” automated or visual quality flags, about 5.4 percent. That percentage is not a shipboard failure rate because the flags include many types of scientific-QC conditions. 

A major limitation is source asymmetry. The U.S. academic fleet, NOAA, BAS/NOC and CSIRO expose far more operational material publicly than JAMSTEC, Ifremer, NIOZ, Canadian Coast Guard and NIWA. Lack of findings for those fleets below should therefore be read as evidence unavailable in this review, not evidence that the problem does not exist.

Executive findings: highest-value pain points
The ranking below combines estimated severity, recurrence across independent sources, and relevance to an OpenRVDAS console/overlay. Evidence counts are conservative minimum numbers of distinct artifacts reviewed.

Rank	Pain point	Severity	Frequency basis	Independent evidence artifacts	Evidence
1	Silent or late-discovered data-quality failure: feeds continue but values are wrong, stale, misconfigured, incorrectly calibrated, wrongly oriented, or temporally invalid	5	Seen fleetwide in SAMOS, R2R, UHDAS, MAC	≥7	DIRECT EVIDENCE. SAMOS documents wrong orientation, erroneous calibration, unit errors and phantom sensor signals; R2R routinely detects gaps, corrupt data, wrong cruise dates and downsampled navigation after acquisition; UHDAS explicitly monitors repeated/backward GPS time, old databases, missing feeds and bad heading. 
2	Configuration drift and configuration correctness are operational hazards	5	Recurrent across UHDAS, NOAA SCS, OpenRVDAS, NERC systems	≥6	DIRECT EVIDENCE. UHDAS warns when ship configs differ from a master list, are internally inconsistent, use incorrect ADCP settings or have swapped feeds. NOAA SCS historically places cruise-specific acquisition and logging parameters in maintained sensor configuration. OpenRVDAS issue history contains explicit requests for state-change auditing and calibration storage. 
3	Time synchronization and timestamp integrity	5	Recurrent failure mode with scientific consequences	≥5	DIRECT EVIDENCE. UHDAS flags GPS timestamps stepping backward, bad computer timestamps, NTP failures, clock drift and position/ADCP timing offsets. Its troubleshooting guidance specifically directs operators to NTP and serial feeds when timestamps fail. 
4	Serial/network feed failure and ambiguous upstream/downstream fault location	5	Common across instrument classes	≥5	DIRECT EVIDENCE. UHDAS lists failed serial ports, corrupted serial feeds, failed GPS/gyro streams and swapped cables; OpenRVDAS added a 2026 request specifically for outbound TCP connections to Moxa/Digi terminal servers, indicating real operational demand around networked serial infrastructure. 
5	Data packaging, naming, metadata and directory inconsistency impose post-cruise cleanup	4	Fleetwide R2R problem	≥5	DIRECT EVIDENCE. R2R reports common problems including inconsistent file formats, naming conventions, incorrect cruise dates/ports, missing datasets and inconsistent directory structures. 
6	Operators need continuous visibility of data freshness and system state, not merely “process running”	5	Recurs in OpenRVDAS, UHDAS, SAMOS, SIS	≥5	DIRECT EVIDENCE. OpenRVDAS has open requests for null records after timeouts and current-value display; UHDAS explicitly distinguishes missing streams, old databases and processes that stopped; SIS advertises immediate reporting of sensor dropouts because this is operationally important. 
7	Rotating personnel face a tribal-knowledge/documentation problem	4	Fleetwide organizational response	≥4	DIRECT EVIDENCE. UNOLS created an RVTEC wiki specifically as a central location for shipboard instrumentation knowledge, SOPs and community “tips & tricks”; RVTEC maintains dedicated tech training and troubleshooting programs. 
8	Per-cruise setup is too manual and too easy to get subtly wrong	4	Recurrent across SCS, UHDAS, OpenVDM and R2R	≥5	DIRECT EVIDENCE. UHDAS requires cruise identifiers and config updates when physical configuration changes; OpenVDM requires operators to define sources, filters, directory mappings, cruise identifiers and transfer behavior; historical NOAA SCS practice includes cruise-specific sensor configuration edits. 
9	Underway environmental sensors frequently fail through plumbing, installation and calibration rather than software alone	4	Many vessels in systematic SAMOS review	≥3	DIRECT EVIDENCE. SAMOS identifies seawater plumbing failures, sensor placement effects, calibration issues, reversed anemometers, bird fouling and lighting interference across named vessels. 
10	A fault can be technically visible yet operationally hard to interpret	4	Recurrent in complex sonar/ADCP chains	≥4	DIRECT EVIDENCE. MAC documented intermittent depth artifacts aboard Atlantis that were not explained by roll, pitch, sound speed, latency or the obvious integration causes; UHDAS has a substantial symptom-to-cause troubleshooting framework because “no velocities” can originate in several independent subsystems. 
11	Ship-to-shore bandwidth and connectivity require prioritization, reduced products and offline operation	4	Common fleet architecture constraint	≥5	DIRECT EVIDENCE. OpenVDM supports priority-ranked ship-to-shore subsets and processing outputs around 5 percent of raw-data size; Schmidt operational guidance requires advance planning for some VPN connectivity; NERC DAMP explicitly separates onboard ingestion from mirrored shore infrastructure. 
12	Closed-source or vendor-controlled acquisition environments inhibit adaptation	4	Explicit NERC design driver; license constraints visible in Kongsberg ecosystem	≥3	DIRECT EVIDENCE. NERC/BAS/NOC state that TECHSAS and SCS being externally maintained and closed-source made third-party modification difficult. Kongsberg SIS Remote requires a vessel license and SIS uses dongle-based licensing. 
13	Different vessels expose different interfaces and workflows for the same scientific task	3	Explicit cross-vessel complaint	≥3	DIRECT EVIDENCE. NERC found that researchers sailing on BAS and NOC ships had to interact with different acquisition systems and considered this a disadvantage. 
14	Backups, disks and storage failures still translate directly into data gaps	5	Recurrent infrastructure class	≥3	DIRECT EVIDENCE. UHDAS monitors failed backups, missing disks, low disk space and I/O errors. BODC documents a cruise where TECHSAS positional data had gaps because acquisition had to be stopped while investigating a virtual-machine storage problem. 
15	Human staffing limits can directly create acquisition gaps	4	Explicit modern example, likely broader but thinly quantified	≥2	DIRECT EVIDENCE. CSIRO states that Investigator voyage IN2025_V07 had only one GSM team member, so 24-hour acquisition was not possible and gaps may exist. INFERENCE: automation that safely reduces watchkeeping effort has direct data-completeness value. 

The broad pattern is that the hardest problems are not simply “logger down.” They are state-integrity problems: the system is running but the relationship among physical sensor, interface, parser, calibration, timestamp, metadata, database, display and archive has drifted. R2R, SAMOS and UHDAS independently expose this same failure shape. 

Findings by operator role
Marine technicians and shipboard computer/electronics technicians
Pain: finding failures before the science party does. Severity 5. Frequency: frequent. DIRECT EVIDENCE. UHDAS explicitly provides red-status panels, automated ticketing, daily diagnostic email and warnings for missing feeds, stale databases, time faults, calibration anomalies, bad settings, failed backups, low disk space and network/computer errors. The existence of these mechanisms demonstrates the breadth of faults a technician is expected to notice and triage. 

Pain: a single science data product depends on many upstream systems. Severity 5. Frequency: recurrent. DIRECT EVIDENCE. For ADCP, loss of ocean-velocity products can originate from the transducer, deck unit, GPS, gyro, serial transport, timestamping, configuration, heading correction or processing. UHDAS specifically advises redundant GPS feeds and alternative heading sources because ancillary-feed loss otherwise affects the final product. 

Pain: configuration maintenance is operational work, not installation-only work. Severity 4. Frequency: frequent. DIRECT EVIDENCE. NOAA’s SCS operational model requires the SCS manager to keep the sensor definition current and apply cruise-specific requested changes; UHDAS requires configuration changes after physical port or feed changes. 

Pain: rotating staff need fleet-level knowledge capture. Severity 4. Frequency: frequent. DIRECT EVIDENCE. RVTEC’s wiki was created specifically because the community wanted a shared location for instrumentation documentation, SOPs and accumulated institutional knowledge. The 2025 RVTEC program separately included troubleshooting methodology, “Tech Sea Stories,” SBE 911 best practices, OpenRVDAS/Coriolix training and an RVTEC Wiki session. 

Product implication, INFERENCE: the console should show a dependency graph rather than a flat process list:

Physical sensor → serial/network endpoint → raw traffic → parser → timestamp → calibration → derived variable → datastore → display/archive

Every stage should expose last-good timestamp, message rate, parse rate, error rate, current value, age, configuration version and provenance.

Chief scientists and science-party users
Pain: inconsistent vessel interfaces. Severity 3. Frequency: recurrent where scientists use multiple ships. DIRECT EVIDENCE. NERC’s acquisition modernization report explicitly says users sailing on BAS and NOC vessels were disadvantaged by having to interact with different acquisition systems. 

Pain: scientists often need technician intervention to determine whether apparently plausible data are trustworthy. Severity 4. Frequency: recurrent. DIRECT EVIDENCE. NOAA cruise instructions describe scientists depending on the SCS manager for determining whether sensors are working and for real-time monitoring that can affect sampling decisions. SAMOS documents errors that can remain numerically plausible, including wrong calibration coefficients, incorrect sensor orientation and suspected wrong units. 

Pain: access to working data during the cruise can become a support burden. Severity 3. Frequency: recurrent. DIRECT EVIDENCE. OpenVDM explicitly describes its read-only cruise-data access model as reducing the need for scientists to wake technicians to retrieve data. 

Product implication, INFERENCE: science users need a read-only “is this trustworthy?” view, not the engineering console. It should expose freshness, QC state, active calibration, source instrument, units, known outages, annotations and a clear raw-data link without giving casual users configuration control.

Data managers and shore-side archivists
Pain: packages arrive incomplete, inconsistent or internally contradictory. Severity 5. Frequency: frequent. DIRECT EVIDENCE. R2R reports gaps, wrong cruise dates, inconsistent file formats/names, corrupted boundary data, missing datasets, incorrect ports and inconsistent directory structures. 

Pain: data acquisition metadata can be wrong even when data files exist. Severity 4. Frequency: recurrent. DIRECT EVIDENCE. SAMOS found acquisition systems reporting sensors that were not physically installed and configuration records containing incorrect calibration or units. 

Pain: downstream QC sometimes detects issues only after collection. Severity 5. Frequency: frequent. DIRECT EVIDENCE. R2R’s QA explicitly exists to identify suspicious originally delivered datasets, including time reversals, missing data and other acquisition problems; SAMOS sends at-sea feedback precisely so faults can be corrected before a cruise ends. 

Product implication, INFERENCE: generate an immutable cruise manifest continuously, not at cruise end. It should include source, file path, checksum, time bounds, record count, gaps, configuration revision, calibration revision, units, parser version, raw/derived relationship and transfer status.

Bridge officers, deck crew and winch operators
The public evidence base is materially thinner here than for marine technicians.

Pain: bridge/deck users need simplified task-specific displays rather than the full acquisition system. Severity 4. Frequency: recurrent but weakly quantified. DIRECT EVIDENCE. Kongsberg SIS supports a separate helmsman display, and UNOLS’s 2026 RVTEC program includes Stream Deck/Bitfocus Companion as an example of building custom operator interfaces, indicating demand for purpose-built control/display surfaces rather than exposing complex back-end systems directly. 

Pain: acoustic acquisition requires coordination between navigation, ship motion and science operation. Severity 5 when wrong. DIRECT EVIDENCE. SIS consumes position, attitude, sound speed and other sensor inputs and continuously monitors their quality; MAC’s Atlantis case shows that bad bathymetric artifacts may persist even after obvious roll, pitch, latency and sound-speed causes are eliminated. 

Evidence gap: I did not find sufficiently strong public 2018–2026 firsthand evidence for MTNW LCI-90i operators or outdoor LED scoreboard failures to make a confident pain-point claim. Interview this group directly.

Protected-species observers on seismic cruises
Pain: mitigation work creates a structured parallel data-recording burden. Severity 4. Frequency: inherent on regulated seismic operations. DIRECT EVIDENCE. NOAA-described monitoring requires recording observer effort, vessel position, source activity, environmental conditions, sightings, behavior and mitigation actions. BOEM-era seismic requirements analyzed in the literature required multiple recurring report types for observer effort, sightings and survey activity. 

Product implication, INFERENCE: if the overlay targets seismic vessels, it should automatically bind observation events to authoritative vessel position, UTC time and source status so PSOs do not transcribe those values manually. Human judgments such as species ID, group size and behavior should remain explicit observer-entered data.

Evidence gap: I found little recent public evidence that directly connects Hotshot, GunLink/Seamap, DigiBIRD/DigiCOURSE, GeoEel or Sercel systems to PSO workflow pain. This is a high-priority interview domain.

Fleet IT and cybersecurity personnel
Pain: science systems increasingly cross the IT/OT boundary. Severity 5. Frequency: fleetwide architectural concern. DIRECT EVIDENCE. IMO cyber guidance identifies bridge, machinery, communications, access-control and other interconnected ship systems as potential cyber-risk surfaces. IACS E26 similarly treats interconnection and COTS systems as part of the ship’s threat surface. 

Pain: compliance has become operational work. Severity 4. Frequency: increasing. DIRECT EVIDENCE. IMO requires cyber risk to be incorporated into safety-management processes, while IACS E26/E27 establish cyber-resilience requirements for applicable new ships; UNOLS now operates dedicated ARFSEC and SURF-IT programs providing monitoring, assessments, security planning, firewall deployment and compliance assistance. 

Pain: security cannot simply mean “no connectivity.” Severity 4. Frequency: recurrent. DIRECT EVIDENCE. Modern operations simultaneously require shore transfer, telepresence, remote support and controlled external connectivity. OpenVDM supports prioritized ship-to-shore delivery; SIS Remote depends on bidirectional network connectivity; SOI documents controlled VPN arrangements requiring prior coordination. 

Product implication, INFERENCE: the acquisition overlay should be secure by architecture: read-only defaults, least privilege, explicit trust zones, offline-capable identity, signed configuration/version history, audit trails, no dependency on cloud availability, and a narrow documented protocol surface.

Findings by system and equipment class
Acquisition systems
OpenRVDAS. Evidence strength: high for desired capabilities, moderate for field-failure prevalence. Open issues include TCP client support for Moxa/Digi terminal servers, suppression of repetitive QC alerts in favor of state transitions, timeout-triggered nulls to InfluxDB, live current-value display, unified state-change logging, calibration-data storage, syslog improvement, NetCDF output and containerized deployment. These are unusually valuable because they are direct statements of operator/developer unmet need rather than inferred vendor-market requirements. 

The issue pattern strongly supports four overlay capabilities: state transition alerts, explicit freshness/staleness semantics, calibration/provenance management, and comprehensive audit/event history. INFERENCE: those should sit above OpenRVDAS rather than be implemented as yet another logger.

NOAA SCS. Evidence strength: moderate. SCS provides acquisition, display, disk logging and basic delta/range monitoring. NOAA continues active releases, including multiple 5.1.x releases through September 2026. The public material shows a configuration-heavy operating model and an architecture whose roots trace to requirements developed in the 1980s, although the current software is web-enabled and actively maintained. 

DIRECT EVIDENCE: NERC/BAS/NOC specifically identified SCS and TECHSAS as difficult for third parties to modify because both were closed source and externally driven by other national-fleet priorities. 

CORIOLIX. Evidence strength: thin. RVTEC 2025 devoted two sessions to OpenRVDAS/Coriolix and UNOLS SURF-IT explicitly lists Coriolix among supported community projects, so it is active in the fleet. Publicly indexed material reviewed here did not provide enough operator failure reports to make system-specific claims. 

MetAcq. Evidence strength: insufficient. No substantive firsthand operational evidence found in the reviewed public corpus.

Legacy DAS/RVDAS and NERC RVDAS. Evidence strength: high. NERC’s modernization history describes decades of acquisition-system replacement and the move from ABC to TECHSAS/SCS to RVDAS and now DAMP. Different systems across ships imposed user inconsistency, and closed external systems limited modifications. 

NERC’s DAMP prototype was explicitly created to address RVDAS limitations using per-sensor containerized components and Kafka. It became the primary logger on RRS Sir David Attenborough before the 2025/26 season after parallel testing. The project records lessons around Kubernetes networking, early IT engagement and the need for “software patchworking” skills to integrate open-source components. 

That finding matters directly to an OpenRVDAS overlay: modularity helps, but operational complexity can simply move from monolithic application configuration into distributed infrastructure complexity. That is an inference from NERC’s documented lessons, not a criticism of DAMP. 

Custom loggers. Evidence strength: moderate. OpenRVDAS itself and NERC’s RVDAS/DAMP history demonstrate why fleets repeatedly build or adapt acquisition systems when vendor or externally maintained systems do not fit local requirements. 

Data handling, dashboards and archives
OpenVDM. Evidence strength: high. Its entire architecture addresses a known operational burden: retrieving data scattered across systems, normalizing them into a cruise package, making them safely available to scientists, backing them up and transmitting selected products ashore. It supports direct, Samba, rsync and SSH sources, include/exclude filters, hooks, plugins and priority-ranked ship-to-shore products. 

DIRECT EVIDENCE: its documentation explicitly describes reducing technician workload and avoiding after-hours requests for scientists’ data. 

R2R. Evidence strength: very high. Its QA routinely exposes missing datasets, bad temporal bounds, corrupt files, inconsistent formats/names and cruise metadata errors. R2R also found historically that multiplexed navigation data followed inconsistent date/time, ordering and delimiter conventions, and that navigation could disappear entirely when the merged acquisition stream was not being created. That older navigation-practice source predates 2015 and should be treated as possibly stale, although its general data-management lessons remain consistent with newer R2R findings. 

SAMOS. Evidence strength: very high. SAMOS is the clearest evidence that real-time or near-real-time shore QC can catch shipboard problems while intervention is still possible. Its workflow combines automated checks with analyst review and technician notification. 

Sealog. Evidence strength: moderate. SOI expedition archives show Sealog-derived event records entering formal data repositories, while the OceanDataTools repositories show active vessel and vehicle clients through 2026. Public issue evidence reviewed here was insufficient to rank specific Sealog pain points. 

Grafana/InfluxDB. Evidence strength: moderate. OpenRVDAS explicitly has an InfluxDB timeout/null requirement, and NERC RVDAS/DAMP architectures use Grafana-class visualization and message-broker pipelines. This supports Grafana as a useful presentation layer but also exposes a gap: a graph cannot distinguish a true steady value from a dead feed unless freshness is modeled explicitly. The last sentence is an INFERENCE grounded in the OpenRVDAS timeout issue. 

Cruise packaging and NetCDF/CF. Evidence strength: high for packaging, moderate for NetCDF. R2R demonstrates persistent package-structure and metadata problems. OpenRVDAS still lists NetCDFWriter as an enhancement request. NERC and BODC examples show structured files are useful but do not remove acquisition-side outages or metadata problems. 

Underway sensors, navigation and ADCP
TSG, fluorometers, meteorological systems. Evidence strength: very high. SAMOS found plumbing failures on Oscar Elton Sette, Rainier, Sikuliaq and others; incorrect anemometer orientation on Okeanos Explorer and Sally Ride; calibration/configuration problems on Atlantic Explorer, Hassler and Thomas Jefferson; long-running failed/missing equipment on Sally Ride, Roger Revelle, Healy, Atlantic Explorer, Pisces and Bell M. Shimada; and environmental contamination from ship lighting and birds. 

This is a critical design warning: the console must represent physical state and metadata, not merely packets. A logger can truthfully show “data arriving” while the sensor is installed backward, fouled, miscalibrated or measuring compromised intake water. That conclusion is an INFERENCE directly supported by SAMOS’s documented failure modes. 

pCO2. Evidence strength: thin. OpenRVDAS includes pCO2 in operational configuration examples, and modern research vessels routinely carry such sensors, but this review did not identify strong system-specific firsthand pCO2 troubleshooting evidence. 

UHDAS/ADCP. Evidence strength: very high. This is the best-documented model of an operator-friendly monitoring system in the corpus. UHDAS monitors feed loss, heading quality, time reversal, missing data, configuration mismatch, incorrect settings, calibration, storage, NTP and backups. It also gives explicit recovery procedures and recommends redundant GPS feeds. 

Gravimeters and magnetometers. Evidence strength: moderate. R2R applies QA to trackline gravity and magnetic datasets and uses navigation quality in downstream processing. Specific current-generation field-failure reports were sparse in the reviewed set. 

GNSS/heading/motion: Seapath, POS MV, PHINS. Evidence strength: high. UHDAS treats accurate heading sources such as Seapath, POS MV and PHINS as critical ancillary feeds and monitors their difference from gyro heading. MAC’s Atlantis investigations also demonstrate how motion-system integration becomes part of sonar troubleshooting. 

Sound velocity. Evidence strength: moderate-to-high. Kongsberg SIS explicitly provides sound-speed-profile management and visualization because these values materially affect multibeam processing; MAC investigations routinely consider sound speed among candidate causes of bathymetric artifacts. 

Sonars
Kongsberg EM multibeams. Evidence strength: high. SIS provides real-time input monitoring, sound-speed display, sensor calibration, health tests and dropout/error notification. MAC exists specifically to improve multibeam quality fleetwide and documents vessel-specific faults. 

A useful real-world example is Atlantis AT42-10 in 2019: intermittent across-swath depth artifacts could not initially be correlated with roll, pitch, sound speed, latency or other obvious sensor-integration errors. This demonstrates the need for time-correlated multi-system diagnostics rather than single-variable alarms. 

PANGAEA documents Meteor cruise M176 multibeam data as erroneous because of technical echosounder problems encountered during the cruise, showing that serious acoustic-system failures still propagate into permanent data archives. 

K-Sync. Evidence strength: thin-to-moderate. RVTEC 2025 included a dedicated K-Sync session, indicating active fleet concern around acoustic synchronization, but the indexed source did not expose enough operator-specific failure text to responsibly enumerate failure modes. 

EA640/EK80. Evidence strength: thin. RVTEC has presented EK80 best practices, and CSIRO Investigator archives routinely include EK80, but firsthand current pain evidence was not sufficient for a separate ranked finding. 

Knudsen/TOPAS and Doppler systems. Evidence strength: insufficient in reviewed corpus. No strong recent firsthand evidence located.

Seismic systems
Hotshot, GunLink/Seamap, DigiBIRD/DigiCOURSE, GeoEel, Sercel. Evidence strength: insufficient. The public sources reviewed strongly document the mitigation/reporting burden around seismic work, but they do not provide enough recent operator-level troubleshooting material for these named acquisition/control systems. Any product decision specific to gun timing, streamer depth-control telemetry or seismic navigation should therefore wait for direct interviews.

Winches, wire, CTD and deck displays
SBE 911 CTD. Evidence strength: moderate. RVTEC devoted major 2023 and 2025 sessions to CTD/SBE 911 best practices and data quality, implying a sustained training and quality-control burden. The indexed material reviewed did not expose enough presentation detail to quote specific recurring failure rates. 

Winch logging. Evidence strength: moderate. RVTEC has dedicated East Coast/West Coast winch-pool logging and operations sessions, but this review did not locate sufficient detailed operator testimony to rank specific wire-log problems. 

MTNW LCI-90i and outdoor LED scoreboards. Evidence strength: insufficient. These should be treated as explicit research gaps, not assumed easy integrations.

Networking and infrastructure
Serial device servers: Moxa/Digi. Evidence strength: direct but narrow. OpenRVDAS’s November 2026 request for a TCP client reader specifically names Moxa/Digi terminal servers, demonstrating a current integration need. 

Pepperl+Fuchs/Comtrol and Lantronix. Evidence strength: insufficient product-specific evidence. They belong to the same operational class, but no reviewed source justified assigning their specific failure modes.

NTP/PTP. Evidence strength: high for NTP, thin for PTP. UHDAS explicitly flags NTP-server failure and drift when a time server is not used. No comparably strong public evidence was located for PTP-specific research-vessel operational problems. 

VSAT/Starlink and ship-shore synchronization. Evidence strength: high for architecture, moderate for pain quantification. UNOLS now runs SatNAG, HiSeasNet and dedicated ship-to-shore performance sessions; RVTEC 2026 specifically includes Gen3 Starlink transfer architecture. OpenVDM’s prioritized subsets and reduced derived products show why raw-data replication cannot simply assume unlimited connectivity. 

Intermapper/LibreNMS/Zabbix. Evidence strength: insufficient product-specific evidence. Generic network-monitoring need is well supported, but these individual platforms were not sufficiently documented in the reviewed maritime sources.

Ship systems and regulatory interfaces
IEC 61162-450, ECDIS, engine monitoring and DP. Evidence strength: thin for day-to-day operator pain. IMO and IACS establish that bridge, propulsion/machinery, communications and interconnected onboard systems are cyber-relevant, but this review did not locate enough public research-vessel operator testimony to make system-specific failure claims for IEC 61162-450, ECDIS or DP. 

EEZ/foreign-clearance restrictions. Evidence strength: insufficient in this corpus. The existence of restricted-data operations is well known operationally, but the reviewed sources did not provide enough current primary evidence to characterize operator pain without importing unsupported assumptions.

Marine-mammal mitigation. Evidence strength: high for workflow burden. PSOs must associate observations and mitigation decisions with time, position, source activity and environmental context, making authoritative event synchronization a credible product target. 

IMO MSC-FAL.1/Circ.3 and IACS E26/E27. Evidence strength: high for requirements, low for fleet-specific burden measurements. IMO requires cyber-risk management around interconnected operational systems, and revised IACS requirements apply to applicable newbuilds contracted from July 1, 2024. 

Cross-cutting operational themes and workaround catalog
Time integrity
Time is not “just another channel.” It is a dependency shared by nearly every science system. UHDAS treats backward GPS timestamps, bad system time, NTP failure and position/ADCP offset as explicit failure modes. 

Observed workaround: redundant GPS feeds, alternative reliable heading sources and cruise-segment reprocessing. 

Opportunity, INFERENCE: provide a fleet-wide time-health service that compares NTP/system time, source timestamps, arrival time, inter-stream latency and drift. Show “timestamp source” and “timestamp confidence” per stream.

Configuration drift
The strongest direct signal is UHDAS’s explicit warning categories for master-list mismatch, internally inconsistent configuration, wrong ADCP settings, swapped cables and one instrument being logged with another instrument’s settings. 

Observed workaround: manually maintained configuration files, master lists and cruise-specific edits. NOAA SCS historically relies on an SCS manager to keep sensor configuration current. 

Opportunity, INFERENCE: Git-like configuration management for ship systems with semantic diffs: “GPS source changed from port A to port B,” “baud changed,” “calibration coefficient changed,” “units changed,” “stream renamed,” “parser version changed.” Require an operator note for high-risk changes.

Onboarding and tribal knowledge
RVTEC’s wiki, training programs and recurring troubleshooting sessions are direct evidence that operational knowledge is distributed among people and institutions rather than fully encoded in software. 

Observed workaround: wiki pages, SOPs, meeting presentations, peer networks, technician training cruises and troubleshooting seminars. 

Opportunity, INFERENCE: each alarm should link to a vessel-specific runbook containing expected wiring, endpoint, baud/message format, power source, spare location, last known fix and escalation path.

Data delivery and archive readiness
R2R’s repeated findings about package incompleteness, naming, dates, formats and directory structure show that “copy the cruise disk at the end” is not enough. 

Observed workaround: OpenVDM continuously collects, organizes, backs up and prioritizes data transfers rather than building the archive package only at the end. 

Opportunity, INFERENCE: archive-readiness should be a live dashboard: datasets expected, datasets present, last data, temporal coverage, checksum status, metadata completeness, transfer status and repository acceptance.

Cybersecurity
Research vessels must simultaneously support science networks, operational systems, vendor support and shore connectivity. IMO/IACS treat this interconnection as a cyber-risk surface, and UNOLS has established specialized programs to support monitoring, firewalling, incident response and compliance. 

Observed workaround: network segmentation, dedicated firewalls, controlled VPN access, incident-response playbooks and centralized cybersecurity support. 

Opportunity, INFERENCE: the overlay should not require broad administrative access to instrument networks. A collector/observer architecture with narrowly scoped ingest endpoints and one-way or broker-mediated paths is substantially easier to defend.

Bandwidth and offline constraints
OpenVDM explicitly prioritizes ship-to-shore products and recommends derived outputs small enough to transmit economically; NERC DAMP tested mirrored ship/shore operation but retains local acquisition as the primary path. 

Observed workaround: reduced derived products, ranked transfer queues, local authoritative storage and later bulk transport. Schmidt also physically transports a complete cruise-data set ashore for final repository delivery. 

Opportunity, INFERENCE: design as “offline first, opportunistically connected.” All monitoring, configuration, authentication, audit and recovery functions should work with zero shore connectivity.

Unmet needs and OpenRVDAS-overlay opportunity map
Opportunity	Required product behavior	Overlay feasibility	Evidence strength
Universal data-health model	For every stream show packet rate, parse rate, last-good time, value age, valid range, flatline detection, missing-data state, source endpoint and downstream consumers	Very high	Very strong. UHDAS, SAMOS, R2R, OpenRVDAS issues. 
State-transition alerting	Alert on healthy→degraded→failed and recovery, not every individual bad sample	Very high	Direct OpenRVDAS request. 
Configuration provenance and drift detection	Version every parser, endpoint, baud, transform, calibration and mapping; compare with vessel baseline	Very high	Very strong. 
Calibration/units registry	Track coefficients, units, effective dates, certificate/reference, person changing them and dependent outputs	High	Very strong. OpenRVDAS asks for calibration storage; SAMOS documents wrong calibration and units. 
Physical-sensor context	Distinguish “packets arriving” from “sensor healthy”; record intake, orientation, fouling, maintenance and sensor presence	Medium-high	Very strong. SAMOS. 
Dependency-aware fault localization	Trace a bad final variable through source sensor, interface, parser, timebase, transform and datastore	High	Very strong. UHDAS and MAC. 
Authoritative time-health service	Compare host clock, NTP/PTP, source timestamps, arrival time, latency and inter-stream skew	High	Strong for NTP; weaker for PTP. 
Cruise-mode templates	Start a cruise from validated vessel profile; require only cruise-specific deltas	High	Strong. SCS, UHDAS, OpenVDM. 
Continuous archive-readiness	Live manifests, checksums, temporal coverage, expected-vs-present data, metadata checks	High	Very strong. R2R. 
Role-based displays	Technician engineering console, scientist QC console, bridge/deck minimal display, shore dashboard	High	Strong. SIS helmsman display, OpenVDM scientist access, NERC cross-vessel UX problem. 
Integrated operator runbooks	Alarm → likely causes → exact vessel checks → prior incidents → spares/escalation	High	Strong indirect evidence. RVTEC Wiki/training and UHDAS troubleshooting. 
Event annotation timeline	One synchronized timeline for configuration changes, alarms, maintenance, science events and operator notes	Very high	Strong. OpenRVDAS requests one-file state logging; PSO workflows depend on synchronized events. 
Bandwidth-aware replication	Priority queues, resumable transfer, raw-vs-derived policy, transfer observability	High	Very strong. OpenVDM and SOI. 
Offline-first security	Local operation without cloud, RBAC, signed audit records, explicit interfaces, least privilege	High	Strong. IMO/IACS plus UNOLS fleet programs. 
PSO/seismic event integration	Pull source state, UTC and navigation automatically into observer records	Medium	Moderate. Strong reporting requirement, weak integration evidence. 
Generic serial-server inventory and diagnostics	Discover/document endpoint, port, protocol, packet rate, reachability and mappings	Very high	Moderate-to-strong. OpenRVDAS current Moxa/Digi request plus UHDAS feed failures. 

The highest-leverage architectural choice is not to replace specialized systems such as UHDAS, SIS or SCS where they already perform domain-specific acquisition well. The overlay should instead become the vessel’s operational truth layer: health, configuration, provenance, cross-system correlation, event history, cruise state and archive readiness. That is an INFERENCE, but it is strongly supported by the fact that the documented problems occur at interfaces among systems and across the data lifecycle, rather than solely inside individual loggers. 

Contradictions, weak evidence and highest-value field questions
Several findings resist a simple product narrative.

First, more automation is not automatically better. UHDAS succeeds partly because it has deep domain knowledge about ADCP-specific failure signatures; generic range alarms cannot reproduce that. SAMOS likewise combines automated QC with expert review. INFERENCE: the overlay should provide a framework for domain-specific checks rather than promise one generic QC engine. 

Second, modular open systems remove vendor lock-in but can increase systems-engineering burden. NERC explicitly cites “software patchworking” and Kubernetes/networking lessons from DAMP. An OpenRVDAS product that requires marine technicians to become Kubernetes administrators would recreate the burden in a new layer. 

Third, connectivity has improved dramatically, but it does not eliminate offline design requirements. RVTEC’s 2026 agenda includes high-speed Gen3 Starlink transfers, while operational platforms still maintain local acquisition, priority transfers and physical end-of-cruise movement. 

Fourth, vendor software is not uniformly the problem. SIS has built-in input monitoring, fault notification, health tests, sound-speed management and remote-display support, and NOAA SCS continues to receive active releases. The product opportunity is therefore interoperability and cross-system observability, not a blanket “vendors are bad” thesis. 

The weakest evidence domains are MTNW LCI-90i and deck-scoreboard operation; Hotshot/GunLink/DigiCOURSE/GeoEel/Sercel troubleshooting; IEC 61162-450 and DP integration on research vessels; EEZ data restriction workflows; PTP; Lantronix/Comtrol/Pepperl+Fuchs-specific problems; MetAcq; and operator-specific evidence from JAMSTEC, Ifremer, NIOZ, Canadian Coast Guard and NIWA.

The most discriminating interview questions are:

“Tell me about the last three times you lost scientifically useful data even though the acquisition computer still looked healthy. When did you discover it, and what would have exposed it earlier?”
“At cruise start, what files, spreadsheets, scripts, dashboards and handwritten notes do you touch before you trust the ship’s systems?”
“Which configuration changes are dangerous enough that you personally double-check them? How do you know what changed between cruises?”
“Which feeds can be stale or wrong while still displaying believable values?”
“What failure wakes you at 0300 most often?”
“What information do you need in the first 60 seconds of an alarm to decide whether to wake somebody else?”
“Which faults require you to SSH/RDP into multiple machines before you understand the chain of failure?”
“Where do calibration constants and sensor metadata actually live today? Which copy is authoritative?”
“What data do you routinely discover are missing only during end-of-cruise packaging?”
“If a new technician joined tomorrow, what would they be unable to infer from the formal documentation?”
“Which systems require vendor licenses, dongles, remote support or Windows-only tools that cause operational friction?”
“What do you deliberately avoid updating before a cruise because you fear breaking it?”
“Which instrument systems are physically isolated for cybersecurity reasons, and what monitoring visibility do you lose because of that?”
“What happens to your monitoring, authentication and data-transfer workflows when Internet access disappears for six hours?”
“For deck/winch operations, what exact numbers need to be visible outdoors, at what update rate, and what failure or stale-data indication is acceptable?”
“For PSOs, which fields are still copied manually from navigation or seismic-control screens into mitigation records?”
“Which ship-to-shore data do you send immediately, which do you postpone, and who changes those priorities?”
“What would you refuse to let a centralized console control, even if it could technically do so?”
Source register and freshness notes
The central recent sources in this review are the 2026 UNOLS RVTEC program, covering data integrity, multibeam, networking, cyberinfrastructure, MQTT/Grafana, Starlink and operator interfaces; the 2025 RVTEC archive, including OpenRVDAS/Coriolix, K-Sync, SBE 911, R2R, SAMOS, ship-to-shore performance, SOPs and cybersecurity; and the 2024 RVTEC program, which included formal OpenRVDAS/OpenVDM/Sealog training. 

The 2025 NERC/BAS/NOC DAMP report is especially valuable for architecture and operator-maintainability evidence. It explicitly describes the acquisition-system lineage, closed-source limitations, cross-vessel inconsistency and the operational lessons from replacing RVDAS with a Kafka/Kubernetes-based platform. 

The SAMOS 2022 Annual Data Quality Report is the strongest fleet-scale empirical source reviewed for real sensor/configuration problems. It names affected vessels and specific failure classes including plumbing, orientation, calibration, units, missing equipment, phantom sensor channels and transmission issues. 

The R2R quality-assessment documentation and 2022 Frontiers paper provide strong evidence for post-cruise packaging failures, metadata inconsistencies, gaps, corrupt files, wrong dates and downsampled navigation, plus the rationale for exposing QA results to vessel operators. 

The UHDAS 2026 operational documentation is the strongest detailed source for live failure detection, particularly timestamp faults, heading problems, serial-feed failure, missing processes, stale databases, config mismatch, disk faults and recovery procedures. 

The OpenRVDAS issue tracker, current through November 2026, supplies direct unmet-needs evidence around Moxa/Digi TCP connectivity, transition-based QC alerts, stale/null semantics, live-value displays, calibration storage, state auditing, syslog and NetCDF. 

The OpenVDM repository documents the operator-created workaround architecture for cruise packaging, backups, scientist access and bandwidth-aware ship-to-shore synchronization; it lists deployment on Endeavor, Falkor (too), Atlantic Explorer, Helmer Hanssen, OceanXplorer, Nuyina, Roger Revelle and Sally Ride, among others. 

The MAC vessel reports, including Atlantis, provide direct evidence that multibeam artifacts can remain unexplained after common integration causes are ruled out. 

The CSIRO Investigator 2025 voyage archive supplies a particularly useful staffing/data-gap example: a voyage with one GSM technical team member could not maintain 24-hour acquisition. 

The BODC TECHSAS record provides a concrete storage-related acquisition outage in which positional gaps occurred because the TECHSAS system had to be shut down while a virtual-machine storage problem was investigated. 

The IMO maritime cyber-risk guidance and IACS E26/E27 material are authoritative for cyber requirements and the scope of interconnected onboard systems, but they describe regulatory expectations rather than marine-technician workload prevalence. 

The Schmidt Ocean Institute operational pages document Falkor (too) use of OpenVDM/R2R/UHDAS/SIS-class workflows, controlled shipboard networking and data-archive practices. 

Possibly stale, pre-2015 evidence: the older R2R navigation-practices document is useful historical evidence for inconsistent multiplexed file conventions and navigation recording practices but should not be treated as proof that those exact practices remain common today. 
 The 2014 Schmidt/OpenVDM material likewise provides useful design-history evidence but is older than the preferred evidence window. 

The evidence supports a clear product direction: build the layer that answers “Is the science data actually healthy, why do we believe that, what changed, what is affected, and is the cruise package complete?” Do not compete with every specialized acquisition system. Normalize their health and provenance, correlate them on one timeline, detect silent failure, make configuration auditable, and make those capabilities work when the ship is offline. That opportunity is supported independently by the failure patterns found in SAMOS, R2R, UHDAS, OpenRVDAS, NERC/BAS and MAC.
