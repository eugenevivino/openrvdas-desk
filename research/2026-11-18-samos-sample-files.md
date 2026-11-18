# SAMOS and NOAA sample files for #111 (met-reports)

Result: no real SAMOS daily file, NOAA hourly ship weather, SHIPTRACK, OPSUM or PCO2 sample was found and
verified. Everything below was read on a page (verified) or only named (not opened). Eugene does not have sample files.

## Verified (page opened 2026-11-18)
- SAMOS file naming: `CALLSIGN_YYYYMMDDvVVVOO.nc` (`.asc` for ASCII): call sign, year, month, day of the first
  record, version `vVVV`, two-digit order `OO`. Source: samos.coaps.fsu.edu/html/naming_convention.php
- Distribution format per the NCEI record: netCDF-3, "SAMOS netCDF Version 1.0". Free and open. Citation: Smith et al., DOI 10.7289/v5qj7f8r.
- Call signs (NCEI ICES list): ROGER REVELLE = **KAOU** (ICES 33RR); KNORR = KCEJ (ICES 316N); Sally Ride = WSAF.
  **Our earlier assumption that Revelle is KCEJ is probably wrong: check before using it anywhere.**
- Real data directory (per its README, not opened): data.coaps.fsu.edu/pub/samos/data/IMMA_source_data/S02_v08/ holds
  per-ship, per-month gzipped tar archives of SAMOS netCDF files, 2005 to 2014, partial coverage.

## Named, not opened (next to read)
- Format manuals: samos.coaps.fsu.edu/html/docs/samos_netcdf_manual.pdf, samos_naming.pdf, samos_quality_flag.pdf;
  parameters: samos.coaps.fsu.edu/html/parameters.php; availability: data_availability.php, cruise_data_availability.php;
  THREDDS: coaps.fsu.edu/thredds-listing; FTP ftp.coaps.fsu.edu/samos_pub/data.
- R2R cruise search: rvdata.us/search (no Revelle or Sally Ride cruise page was found yet).

## Not found
NOAA hourly ship weather, SHIPTRACK, OPSUM, PCO2: no public spec or sample found. The #111 templates stay UNVERIFIED for those.
Next step (agent task, read-only): open the three manuals and one real 2013 archive from the S02_v08 directory on the Mini or in cloud.
