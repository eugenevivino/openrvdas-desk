# Brief: p2-adcp-health (ADCP health and cross-checks, listen-only)

- Decision: IDEAS #145, D-SHIP1, from Eugene's 2026-11-18 ask: "We should also loop ADCP into this"; build per D-NIGHT1
- Risk tier: medium (binary parsing of untrusted bytes; no writes anywhere)
- Module: exactly one. Branch `deepsignal/p2-adcp-health` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 4/5/2
- Depends on: none to build. In use it reads gyro and GNSS heading fields, TSG and probe sound speed, and
  #139 `MB_NadirDepth` and `MB_PingTime`, by configured names

## Goal
The ADCP is the instrument most often found broken after the cruise (a frozen heading feed, wrong sound
speed, lost bottom track). The watchstander sees it live: ensembles arriving on time, heading agreeing with
the gyro and GNSS, sound speed agreeing with the TSG, bottom track agreeing with the multibeam, and the
instrument's own self-test word.

## Background facts (do not re-derive)
- Base is the contrib `master` tree at `3b4b76e`: it carries a 2024 core tree (old Transform base class,
  no BaseModule). Copy the import-compatibility approach of
  `git show origin/deepsignal/vector-wind:contrib/deepsignal/logger/transforms/vector_wind_average_transform.py`
  so the module also works on current core. If that branch is unreadable, write plain absolute imports
  and say so.
- Create empty `__init__.py` files only where missing, byte-identical to the wind branch (empty), so
  parallel branches merge cleanly.
- OpenRVDAS loads classes from a config with `class:` plus `module:` (for example
  `module: contrib.deepsignal.<module>.<file>`). Records may arrive as a DASRecord, a dict with
  `timestamp` and `fields`, a list of either, or None; handle all, pass None through.
- File ownership is disjoint across phase 2 tasks: you own ONLY the paths under Scope.
- Design and safety context: desk `docs/SHIP-SYSTEMS.md` and decision D-SHIP1. This module is PASSIVE:
  it never opens a socket, never sends a byte to any ship system, and never changes a setting.

- Sources, all passive (never connect to the ADCP's command line, which UHDAS or VmDAS owns):
  1. UHDAS speed log `$PUHAW,UVH,...` (core device type `ADCP_OS75` already parses it).
  2. Raw PD0 ensembles, if the ship offers a copy: a receive-only serial split of the ADCP output, or a
     network re-broadcast set up by the ADCP operator. Core `UDPReader` or `SerialReader` with `encoding`
     null delivers bytes.
- PD0 layout (lead summary of Teledyne RDI's public "Commands and Output Data Format" manuals; put every
  offset and scale in a YAML table `adcp_health/pd0_layout.yaml` so a correction is a data change; the docs
  must say "verify against a real capture on the pilot ship"): little-endian; header ID bytes `7F 7F`;
  bytes 2-3 ensemble length excluding the 2-byte checksum; byte 5 number of data types; then a uint16 offset
  per data type from ensemble start. Checksum: sum of all bytes before it, modulo 65536. Data types by ID:
  fixed leader `0x0000` (byte 8 beams, byte 9 cells), variable leader `0x0080` (bytes 2-3 ensemble number,
  bytes 4-10 RTC year, month, day, hour, minute, second, hundredths, byte 11 ensemble number MSB, bytes
  12-13 BIT result, 14-15 speed of sound m/s, 16-17 transducer depth dm, 18-19 heading 0.01 degree, 20-21
  pitch and 22-23 roll 0.01 degree signed, 24-25 salinity, 26-27 temperature 0.01 C signed), bottom track
  `0x0600` (bytes 16-23 four beam ranges in cm, bytes 40-43 four beam percent good). Ocean Surveyor,
  Workhorse and Pinnacle share this layout for these fields; any data type ID not in the table is skipped.

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/adcp_health/`:
- `PD0SummaryTransform(Transform)`: bytes in (handles split and concatenated ensembles with a bounded
  buffer, resyncs on `7F 7F` plus a valid checksum), emits per ensemble: `ADCP_Ensemble`, `ADCP_Time`
  (from RTC, UNIX s), `ADCP_Interval_s`, `ADCP_Heading`, `ADCP_Pitch`, `ADCP_Roll`, `ADCP_SoundSpeed`,
  `ADCP_XducerDepth`, `ADCP_BIT` (raw word) and `ADCP_BITText` (nonzero bits listed), `ADCP_BTDepth`
  (mean of valid beam ranges times cos of `beam_angle_deg` (kwarg, 30 for Ocean Surveyor, 20 for
  Workhorse, no default: required) plus transducer depth; empty when fewer than 3 beams valid),
  `ADCP_BTGood` (percent of beams valid), `ADCP_ClockOffset_s`, and counters of checksum failures and resyncs.
- `ADCPCrossCheckTransform(Transform)`: roles mapped to field names: `adcp_heading` (ADCP_Heading or the
  UHDAS speed log heading), `gyro_heading`, `gnss_heading`, `adcp_sv`, `tsg_sv`, `probe_sv`, `adcp_bt_depth`,
  `mb_depth`, `adcp_time`, `mb_ping_time`, `ek_ping_time`. Emits:
  - `ADCPX_HeadingDiff_<ref>` (circular difference, wrap at 360), `ADCPX_HeadingFrozen` (ADCP heading
    unchanged for `frozen_s` (default 60) while the gyro moves more than 1 degree: the classic dead heading
    feed);
  - `ADCPX_SVDiff_<ref>` (ADCP speed of sound vs TSG and probe; an ADCP set to a fixed EC value shows a
    steady offset, reported as such);
  - `ADCPX_BTvsMB_pct` (bottom-track depth vs multibeam nadir, both below the waterline);
  - `ADCPX_PingOverlap` (count in the last 5 minutes of ADCP ensemble times within `overlap_window_s` of a
    multibeam or EK80 ping time; a hint for #144 transmit awareness and K-Sync, never a control);
  - `ADCPX_Alarm`, `ADCPX_AlarmText`, `ADCPX_Stale`. Persistence, hysteresis and record-time rules as in
    #140 and #141. Thresholds as kwargs: heading 1.0 degree, SV 2.0 m/s, depth 3 percent.
- Listen-only: no sockets opened by the module, nothing sent to the ADCP, UHDAS or VmDAS.

## Failing test first
`contrib/deepsignal/test/adcp_health/test_adcp.py`: PD0 ensembles built in the test from the layout
table (good checksum, bad checksum, split across reads, two concatenated, garbage between, unknown data
type skipped); every field against a hand-computed value; BIT text; bottom-track depth with 4 and with 2
valid beams; heading wrap (359 vs 1 is 2 degrees); frozen heading; SV offset; BT vs MB; ping overlap; alarm
persistence and clear; stale sources; replay determinism; `None`, list, DASRecord and dict inputs.

## Module contract
Docs `contrib/deepsignal/docs/adcp_health.md`: why each check matters to the ADCP processing (heading
error becomes cross-track velocity error), how to get a passive PD0 copy (ask the ADCP operator; never tap
the command line), the "verify the layout on a real capture" warning. Sample config
`contrib/deepsignal/configs/adcp_health_demo.yaml`. Depends on no other module.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/adcp_health -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/adcp_health contrib/deepsignal/test/adcp_health
```

## Scope
Create or change only: `contrib/deepsignal/adcp_health/**`, `contrib/deepsignal/test/adcp_health/**`,
`contrib/deepsignal/docs/adcp_health.md`, `contrib/deepsignal/configs/adcp_health_*.yaml`, and empty
`__init__.py` files where missing. Everything else is read-only.

## Usability (anything a tech sees or edits)
Answer each line of desk `docs/USABILITY.md` in the report, or N/A with a reason. Alarm text names the
check, both values, the limit and what to try ("ADCP heading stuck at 212.4 for 3 minutes while the gyro
turned 18 degrees. Check the heading feed into UHDAS.").

## Trust boundaries and data integrity
Bytes are untrusted: check every offset and length before reading, cap the buffer at 64 KB, require a
valid checksum before using any field, never `eval`. Never change incoming fields; only add new ones.
Missing or stale values are shown as such, never guessed.

## Non-goals and banned
No velocity profiles or current processing (UHDAS and CODAS do that). No commands to the ADCP. No core
changes, no new dependency (`struct` only), no refactors outside Scope. No loosened, skipped or deleted
tests, no swallowed errors.

## Stop rule
No code change needed: stop and report. Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Acceptance tails:
- Open questions:
