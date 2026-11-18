# Pilot cruises for the reanalysis program (D-REAN1)

Answer: three R/V Roger Revelle GO-SHIP cruises. Each has the raw SIO
MET-System (MetAcq) archive on R2R and final bottle salinity plus CTD on
CCHDO. One ship, one acquisition system, a few years apart. Checked
2026-11-18 through the R2R and CCHDO APIs. Nothing downloaded except three
small bottle files read for counts.

| Cruise | Line | Dates | Route | R2R met fileset (raw MetAcq) | R2R CTD fileset | CCHDO bottle file (latest) |
|---|---|---|---|---|---|---|
| RR2204 | P02W | 2022-04-30 to 06-10 | Guam to Honolulu | 151238: 460 files, 18.4 GB raw, 2.35 GB tar.gz | 151240: 897 files, 4.7 GB | 33RR20220430_hy1.csv: 116 stations, 3953 bottle salinities |
| RR2205 | P02E | 2022-06-13 to 07-16 | from Honolulu, eastward (port not checked) | 151255: 361 files, 14.3 GB raw, 1.81 GB tar.gz | 164492: 574 files, 2.7 GB | 33RR20220613_hy1.csv: 88 stations, 3261 bottle salinities |
| RR2308 | I05 | 2023-07-22 to 09-14 | Fremantle to Cape Town | 159533: 535 files, 24.0 GB raw, 3.00 GB tar.gz | 159521: 984 files, 4.7 GB | 33RR20230722_hy1.csv: 195 stations, 6322 bottle salinities |

Download links (verified HTTP 200 for the met tarballs; CTD links not probed):
- R2R fileset: `https://service.rvdata.us/data/cruise/<cruise>/fileset/<id>`
  (redirects to a Globus-hosted `<cruise>_<id>_metstation.tar.gz`)
- CCHDO cruise page: `https://cchdo.ucsd.edu/cruise/<expocode>`, expocodes
  33RR20220430, 33RR20220613, 33RR20230722. Bottle files:
  `https://cchdo.ucsd.edu/data/44578/33RR20220430_hy1.csv`,
  `https://cchdo.ucsd.edu/data/44597/33RR20220613_hy1.csv`,
  `https://cchdo.ucsd.edu/data/42022/33RR20230722_hy1.csv`.
  Processed CTD (ct1 exchange, netCDF) is on the same pages, a few MB each.

Verified:
- R2R format for all three met filesets: "SIO MET-Station ACQ,LOG,UCR,COR,MET".
- Each hy1 file has SALNTY (bottle) and CTDSAL columns with counts above.

Inferred, check first:
- That the MetAcq archive contains the TSG channels. No separate TSG fileset
  exists for these cruises, and MetAcq on Revelle logs the TSG, so it should
  be inside; confirm by listing one tarball before planning around it.
- The archive has both raw (ACQ) and MetAcq-corrected (COR) files. If so,
  COR is a ready-made baseline: our pass must at least match it on holdout.
- Calibration certificates are not in R2R or CCHDO. Ask SIO shipboard tech
  group (STS) for the TSG and met sensor cal sheets for 2022 and 2023.

Why these: same ship and system (one reader, module 3, covers all three), two
back-to-back legs (RR2204 and RR2205) let a TSG drift be followed across a
port call, and RR2308 is a different ocean for leave-one-cruise-out. GO-SHIP
bottle salinity is analyzed on a salinometer against standard seawater, so
it is a strong Tier A reference. Top bottles at about 5 m match the TSG
intake depth only approximately; the plan treats that as sampling mismatch.

Smallest start: RR2205 met tarball (1.8 GB) plus its 2.4 MB bottle file.
