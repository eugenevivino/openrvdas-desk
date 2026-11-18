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

Verified 2026-11-18 by reading only the first 4 MB of the RR2205 tarball
(no full download):
- The TSG is in the met archive. The tarball is a BagIt bag
  (`RR2205/151255/data/`), one set per day with extensions ACQ, COR, UCR,
  UNC, MET, LOG, DCC, M00, NOA, SLT, WCH (32 to 33 days each).
- `.ACQ` is the MetAcq configuration and calibration file (Revelle `RR21C.ACQ`,
  2021-11-06). It lists **two SBE45 TSGs** and an SBE38 hull SST:
  - TSG83: SBE45 s/n 0083, bow thruster room UCW intake, Sea-Bird cal 22-Sep-2020
  - TSG72: SBE45 s/n 0572, aft hydro lab, Sea-Bird cal 06-Mar-2021
    (note in file: "changed TSG73 for TSG72 11/06/2021", a swap)
  - SST53: SBE38 s/n 1188, bow thruster UCW intake, SIO/STS cal 05-Jan-2021
  - Also oxygen, fluorometer and flow meters on the hydro lab loop.
  So at RR2205 the TSGs were 15 to 21 months past calibration, which makes
  drift plausible, and the two TSGs plus the SBE38 give a redundant set for
  Tier C consistency.
- `.COR` lines are `$WICOR` sentences carrying both TSGs (TT, TC, SA, SD, SV,
  TG fields) every second, plus met, nav and gyro.
Inferred, check first:
- UCR and UNC look like uncorrected and COR corrected streams (MetAcq applies
  the ACQ slope and offset). If so, COR is a ready-made baseline: our pass
  must at least match it on holdout.
- Calibration certificates are not in R2R or CCHDO; the ACQ gives only cal
  dates. Ask SIO STS for the Sea-Bird certificates (pre and post) for SBE45
  0083 and 0572 and SBE38 1188, and for whatever replaced them by 2023.

Why these: same ship and system (one reader, module 3, covers all three), two
back-to-back legs (RR2204 and RR2205) let a TSG drift be followed across a
port call, and RR2308 is a different ocean for leave-one-cruise-out. GO-SHIP
bottle salinity is analyzed on a salinometer against standard seawater, so
it is a strong Tier A reference. Top bottles at about 5 m match the TSG
intake depth only approximately; the plan treats that as sampling mismatch.

Smallest start: RR2205 met tarball (1.8 GB) plus its 2.4 MB bottle file.
