# SAMPLE-DATA: public test data for DeepSignal decoders

Status: 2026-11-18. Owner: decoders and sonar math lanes.
Rule: public sources only. Nobody was contacted. Nothing here came from SIO internal stores.

## TL;DR

- **Got (254 MB, 28 files, cloud only):** real UNOLS raw for Kongsberg `.kmall`, `.all`, `.kmwcd`, `.wcd`, Simrad EK80 `.raw`, Sea-Bird SBE 911 `.hex`, Sippican XBT `.edf`, RDI VmDAS Ocean Surveyor `.ENR`, Moxa SNMP walks and MIBs, small SEG-Y.
- **Two matched pairs** for water-column work: Revelle RR2214 EM124 `.kmall` + `.kmwcd` (same ping file 0578), Sikuliaq SKQ202217T EM302 `.all` + `.wcd` (same file 0027).
- **Gaps:** sub-bottom (Knudsen `.keb`/SEG-Y, EM SBP29), real ship seismic SEG-D, SAMOS, UHDAS raw tree, Moxa NPort MIB. Sources listed below, all blocked from the cloud proxy; fetch on demand.
- **Where:** `/mnt/project-files/sample-data/<category>/`, checksums in `MANIFEST.tsv`. Nothing was written to the MacBook.

## How access works (why some sources are missing)

The cloud container's proxy allows AWS S3 and GitHub. It blocks rvdata.us (R2R), marine-geo.org (MGDS), ncei.noaa.gov web pages, samos.coaps.fsu.edu, zenodo, pangaea, figshare, moxa.com.

The good news: NOAA publishes the two archives that matter most for sonar as open S3 buckets, no account needed:

| Bucket | What | Browse |
|---|---|---|
| `noaa-dcdb-bathymetry-pds` | NCEI multibeam raw (`.kmall`, `.all`) by ship/cruise, R2R-submitted, plus MB-System `.inf/.fbt/.fnv` | https://noaa-dcdb-bathymetry-pds.s3.amazonaws.com/index.html#mb/ships/ |
| `noaa-wcsd-pds` | NCEI water column sonar: EK60/EK80 `.raw`, EM `.wcd`/`.kmwcd`, some ancillary CTD/XBT | https://noaa-wcsd-pds.s3.amazonaws.com/index.html#data/raw/ |

Path patterns: `mb/ships/<ship_snake>/<CRUISE>/multibeam/level_00/<CRUISE>_RAW_<EM>/` and `data/raw/<Ship_Camel>/<CRUISE>/<INSTRUMENT>/`.
Fetch any key with `curl -O https://<bucket>.s3.amazonaws.com/<key>` or `aws s3 cp s3://<bucket>/<key> . --no-sign-request`.

License for both buckets: US Government work, no restrictions. Cite as "Rolling Deck to Repository. <year>. <Instrument> data collected during <CRUISE>. NOAA NCEI."

## Downloaded subset

All headers checked: `.kmall`/`.kmwcd` start with `#IIP`, `.all`/`.wcd` with STX `0x02` + `I` (installation datagram), EK80 with `XML0`, VmDAS with `0x7F7F`.

| Format | File | Ship / cruise | Sonar | Size | Source |
|---|---|---|---|---|---|
| kmall | `multibeam_kmall/0578_20221227_102925_ROGERREVELLE_EM124.kmall` | Revelle RR2214 (GEOTRACES GP17-OCE, Papeete to Punta Arenas) | EM124 | 88.2 MB | DCDB S3 |
| kmwcd | `water_column_kmwcd/0578_20221227_102925_ROGERREVELLE_EM124.kmwcd` | Revelle RR2214, **same file as above** | EM124 | 26.7 MB | WCSD S3 |
| kmall | `multibeam_kmall/0018_20220501_043609.kmall` | Revelle RR2204 | EM124 | 20.9 MB | DCDB S3 |
| kmall | `multibeam_kmall/0204_20241027_203259.kmall` | Sikuliaq SKQ202416T | EM304 | 5.5 MB | DCDB S3 |
| kmwcd | `water_column_kmwcd/0057_20220808_111429.kmwcd` | Atlantis AT50-02 | EM124 | 2.8 MB | WCSD S3 |
| all | `multibeam_all/0027_20221208_223050_Sikuliaq.all` | Sikuliaq SKQ202217T | EM302 | 2.9 MB | DCDB S3 |
| wcd | `water_column_wcd/0027_20221208_223050_Sikuliaq.wcd` | Sikuliaq SKQ202217T, **same file as above** | EM302 | 3.2 MB | WCSD S3 |
| all | `multibeam_all/0011_20230612_125943_Armstrong.all` | Armstrong AR74 | EM122 | 3.1 MB | DCDB S3 |
| all | `multibeam_all/0099_20230918_165036_Healy.all` | Healy HLY2302 | EM122 | 26.1 MB | DCDB S3 |
| EK80 raw | `ek80_raw/SR-D20221207-T220045.raw` + `.idx` | Sally Ride SR2213 | EK80 | 72.7 MB | WCSD S3 |
| EK80 raw | `ek80_raw/ar66b-D20220420-T233358.raw` | Armstrong AR66-B | EK80 | 0.26 MB | WCSD S3 |
| CTD | `ctd_sbe911/EX2505_CTD001_20250722T0536Z.hex/.hdr/.bl` | Okeanos Explorer EX2505 (NOAA, not UNOLS) | SBE 911plus | 0.56 MB | WCSD S3 ancillary |
| XBT | `xbt/EX2505_XBT052_20250807T061100Z.edf` | Okeanos Explorer EX2505 | Sippican MK21 | 47 KB | WCSD S3 ancillary |
| ADCP | `adcp_vmdas/vmdas02_os.ENR` | unknown vessel (dolfyn test file) | RDI Ocean Surveyor, VmDAS PD0 | 1.3 MB | github.com/lkilcher/dolfyn, BSD-3-Clause |
| SNMP | `moxa_snmp/moxa-nport.snmprec`, `moxa-nport_np6150.snmprec` | n/a | NPort 5610-16, NPort 6150 (sysDescr/sysObjectID only) | tiny | github.com/librenms/librenms, GPL-3.0 |
| SNMP | `moxa_snmp/moxa-etherdevice_eds510e.snmprec` | n/a | Moxa EDS-510E full walk (879 OIDs) | 50 KB | LibreNMS |
| MIB | `moxa_snmp/MOXA-GENERAL-MIB`, `MOXA-PORT-MIB` | n/a | Moxa enterprise 8691 | small | LibreNMS (Moxa-authored) |
| SEG-Y | `seismic_segy/small.sgy`, `small-ps.sgy` | synthetic | SEG-Y rev1 | 25 KB | github.com/equinor/segyio, LGPL-3.0 |

Also in the fork already, no download needed: `test/NBP1406/data/` (Palmer NBP1406, real NMEA and vendor strings for gyro, s330, seapath, knud Knudsen depth, adcp, mwx1 met, tsg1/tsg2, svp1, pco2, grv1, 20 streams, 6.8 MB). This is the underway NMEA and OpenRVDAS log sample.

## Fetch on demand (bigger, URL only)

| Want | Where | Size note |
|---|---|---|
| Full EM124 + water column line set | `s3://noaa-wcsd-pds/data/raw/Roger_Revelle/RR2214/EM124/` and DCDB `roger_revelle/RR2214` | DCDB lines 30 to 90 MB each |
| EM124 + EM712 dual-sonar cruise | DCDB `sally_ride/SR2411/multibeam/level_00/` (`SR2411_RAW_EM124`, `SR2411_RAW_EM712`) | 400 files, 51 GB total, many 0.3 to 135 MB |
| EM712 shallow sonar on Revelle | DCDB `roger_revelle/RR2410/multibeam/data/version1/MB/em712/` | smallest 87 MB |
| Big EM302 water column | `s3://noaa-wcsd-pds/data/raw/Sikuliaq/SKQ202217T/EM302/` | 86 files, 43.5 GB |
| EM304 `.kmwcd` with paired CTD/XBT ancillary | `s3://noaa-wcsd-pds/data/raw/Okeanos_Explorer/EX2505/` | 706 kmwcd, 191 GB; ancillary is small |
| EK80 on Armstrong (long run) | `s3://noaa-wcsd-pds/data/raw/Neil_Armstrong/AR66-B/EK80/` | 1,795 files, 373 GB |
| Other UNOLS ships in both buckets | Revelle, Sally Ride, Armstrong, Atlantis, Healy, Sikuliaq, Thompson, Kilo Moana, Langseth, Palmer | list with `?list-type=2&delimiter=/&prefix=...` |

Tip: DCDB `generated/*.inf` (MB-System info) sits next to every raw file. Use it as the ground truth for ping counts, time span and depth range when testing a decoder.

## Gaps and where they live (not reachable from cloud, not verified this pass)

Per Eugene, sonar extras were a short try, not a deep chase. These sources are public but blocked by the cloud proxy. Fetch them through the MacBook browser only when a lane needs them, then move the file to the project folder and delete the Mac copy.

| Format | Best public source | Note |
|---|---|---|
| Knudsen 3260 `.keb`/`.kea`/SEG-Y sub-bottom | R2R cruise file sets, https://www.rvdata.us/search/cruise/RR2214 (and other cruises), and NCEI trackline geophysics | R2R distributes SBP raw per cruise for UNOLS ships that ran Knudsen |
| Kongsberg SBP29 / SBP120 raw | R2R file sets for EM124 ships (Revelle, Atlantis, Sally Ride) | not in DCDB or WCSD buckets |
| Seismic SEG-D / SEG-Y + shot logs | MGDS Academic Seismic Portal, https://www.marine-geo.org (Langseth MCS) | large; ask for a single shot gather only |
| SAMOS (Revelle KAOU) | https://samos.coaps.fsu.edu and NCEI SAMOS accessions | memory note: real KAOU file only via manual NCEI download |
| UHDAS raw tree / CODAS output | R2R ADCP file sets per cruise; JASADCP archive at Univ. of Hawaii (URL not verified) and UHDAS docs at https://currents.soest.hawaii.edu | dolfyn VmDAS file covers PD0 parsing now; UHDAS `.raw` + `.rbin` still missing |
| Moxa NPort MIB (`MOXA-NP*`) | moxa.com download center, NPort product pages | LibreNMS walk only has sysDescr for NPort; full walk would need a real device |
| SVP `.asvp` / Valeport casts | R2R file sets | XBT `.edf` covers casts for now |

## Manifest

`/mnt/project-files/sample-data/MANIFEST.tsv`: path, bytes, sha256, source URL for every file. Re-fetch any file with its URL and check the hash.
