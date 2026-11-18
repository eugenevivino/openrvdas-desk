# Format samples and specs (2026-11-18)

Public samples and specs for #111 (met-reports). Each file says where it came from. Read with
`research/2026-11-18-samos-ship-format-and-fm13.md`.

| File | What | Source | Verified |
|---|---|---|---|
| `samos_ship_line_SCS_2013.txt` | One real ship-to-SAMOS record line (NOAA ship call sign WTDM, 2007-03-01) as printed in NOAA's SCS SAMOS procedure, page 9 | https://www.nodc.noaa.gov/archive/arc0216/0112745/1.1/data/1-data/SCS_SAMOS_Operational_Procedure.pdf | Text read from the PDF by a fetch agent; spacing as printed |

Not obtained: a full SAMOS daily file, a SAMOS netCDF file for Revelle (KAOU), and any NOAA hourly ship
weather, SHIPTRACK, OPSUM or PCO2 message. The Revelle SAMOS archive at
https://data.nodc.noaa.gov/coaps/samos/KAOU/ refuses automated fetches (robots.txt), and the cloud and
Mac VM networks block samos.coaps.fsu.edu and rvdata.us. A person can download one day by hand in a
browser from that KAOU folder (for example `2018/06/`) and drop it here.
