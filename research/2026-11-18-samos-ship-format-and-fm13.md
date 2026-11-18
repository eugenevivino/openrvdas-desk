# SAMOS ship submission format and FM-13 SHIP code (for #111)

Written 2026-11-18 by the parity thread, after Eugene asked us to find public samples ("I don't have
them"). Builds on `research/2026-11-18-samos-sample-files.md`. Verified means a fetch agent read the text
on the page; anything summary-only is marked.

## Bottom line

- **What a ship sends to SAMOS is a plain-text daily file of one-minute key:value records, zipped and
  emailed once a day.** SAMOS turns it into netCDF on its side. So the #111 SAMOS writer should produce the
  text file, not netCDF. This is the format MetAcq's "SAMOS daily zip" email replaces.
- The **"NOAA hourly ship weather report" is the WMO FM-13 SHIP code (BBXX)**, laid out in NWS Observing
  Handbook No. 1. The group layout is verified below; no complete worked observation was found, so
  byte-level checks still need a real message.
- One real ship-to-SAMOS record line is saved in `research/samples/samos_ship_line_SCS_2013.txt`.

## 1. Ship-to-SAMOS daily file (verified)

Source: NOAA "SCS SAMOS Operational Procedure", May 3, 2013,
https://www.nodc.noaa.gov/archive/arc0216/0112745/1.1/data/1-data/SCS_SAMOS_Operational_Procedure.pdf

- Values are computed once per minute all day (1440 records per day). Each value is a 60-second average
  of at least 12 samples.
- One file per UTC day, zipped, mailed by SMTP once per day at 0001 GMT. The subject line must contain the
  ship name and call sign. (The procedure gives the NOAA-ship address; a UNOLS ship would get its own
  address from SAMOS. That last part is our inference.)
- Record layout, as printed on page 9 (saved verbatim in the sample file):
  `$SAMOS:001, CS:WTDM, YMD:20070301, HMS:143450, LAT:55.47518, LON:-160.41834, GYRO:64.1, COG:, SOG:, RWDIR:225.25, RWSPD:5.95, TWDIR:, TWSPD:, RELHUM:59.3, TSGTEMP:, TSGSAL:30.48, ATEMP:12.05`
  An empty value after the colon means missing.
- Designator table (page 2): CS (call sign), LAT, LON, GYRO, SOG (knots), COG, ATEMP (degC), BARO (hPa,
  not reduced to sea level), RELH (%), RWSPD (knots), RWDIR, TWSPD (knots), TWDIR, TSGWT (degC), TSGS (psu),
  TSGC (S/m), TSGSV (m/s).
- **Inconsistency in the source:** the sample line uses RELHUM, TSGTEMP and TSGSAL, while the table says
  RELH, TSGWT and TSGS. The writer must take designators from config, and the first real file from a UNOLS
  ship decides which spelling SAMOS accepts today. Ask the SAMOS team before going live.

## 2. SAMOS naming and netCDF (verified unless marked)

- File name: `CALLSIGN_YYYYMMDDvVVVOO.nc` (`.asc` for ASCII). VVV is the SAMOS version (100 or more, "v1.0.0");
  OO is the receipt order, from 01, incremented when more data arrives for the same day.
  https://samos.coaps.fsu.edu/html/naming_convention.php
- Requested parameters, nominal one-minute interval: time, lat, lon, COG, SOG, heading, speed through
  water, relative and true wind, pressure, air temperature, humidity, precipitation, shortwave and longwave
  radiation, sea temperature, salinity, conductivity; secondary ones include PAR, fluorescence and oxygen.
  https://samos.coaps.fsu.edu/html/parameters.php
- SAMOS netCDF manual v2.0 (24 March 2026), https://samos.coaps.fsu.edu/html/docs/samos_netcdf_manual_v2.pdf:
  time is "minutes since 1-1-1980 00:00 UTC"; lon is 0 to 359.9999 east; missing value -9999 (not for
  time, lat, lon); special value -8888. Variable names include PL_HD, PL_CRS, PL_SPD, PL_SOW, PL_WDIR,
  PL_WSPD, DIR, SPD, P (hPa), T, TW, TD, RH, Q, TS, PRECIP, RRATE, RAD_SW, RAD_LW. SSPS and CNDC and the QC
  flag letters were in the summary only (not verified). We only need this to read SAMOS files back for
  validation (#95), not to write them.
- Revelle is call sign **KAOU** (Knorr was KCEJ, Sally Ride is WSAF).

## 3. FM-13 SHIP (BBXX) layout (verified)

Source: NWS Observing Handbook No. 1, May 2010,
https://www.weather.gov/media/marine/ObservingHandbook1_2010_508_compliant.pdf, chapter 2, pages 2-1 and 2-2:

`BBXX D.....D YYGGiw 99LaLaLa QcLoLoLoLo iRixhVV Nddff 00fff 1snTTT 2snTdTdTd 4PPPP 5appp 7wwW1W2 8NhCLCMCH 222Dsvs 0ssTwTwTw 2PwPwHwHw 3dw1dw1dw2dw2 4Pw1Pw1Hw1Hw1 5Pw2Pw2Hw2Hw2 6IsEsEsRs 8swTbTbTb ICE ciSibiDizi`

- Section 0 is groups 1 to 5 (BBXX to QcLoLoLoLo), section 1 is groups 6 to 14 (iRixhVV to 8NhCLCMCH),
  section 2 is groups 15 to 23 (222Dsvs to ICE).
- Group definitions start on page 2-3 (BBXX), 2-4 (call sign), 2-5 to 2-7 (day, hour, wind indicator),
  2-8 to 2-10 (position), 2-11 to 2-13 (indicators, cloud height). Later page numbers came from a summary
  and are unverified.
- Automated systems can fill section 0, wind (Nddff with N as "/" if not observed), 1snTTT, 2snTdTdTd,
  4PPPP, 5appp, 222Dsvs and 0ssTwTwTw. Visual groups (VV, N, ww, clouds, waves, ice) are "/" or omitted:
  the writer must never invent them.
- No complete worked BBXX message was verified in the handbook. A real one, or an online decoder test, is
  still needed before the template is marked VERIFIED.

## 4. What this changes in #111

1. SAMOS template = the text format in section 1, one `$SAMOS:` line per minute, designators from config,
   empty value for missing, daily zip. Status: VERIFIED for structure against the sample line; field
   spelling to confirm with SAMOS.
2. NOAA hourly = FM-13 template per section 3, automated groups only. Status: UNVERIFIED until checked
   against a real message.
3. SHIPTRACK, OPSUM, PCO2: still no public spec. Keep them out of v1 unless SIO supplies samples.
