# Brief: p2-kongsberg-tap (Kongsberg multibeam datagram tap, read-only)

- Decision: IDEAS #139, D-SHIP1, from Eugene's 2026-11-18 ask to interface with sonars; build per D-NIGHT1
- Risk tier: medium (binary parsing of untrusted network bytes; no writes anywhere)
- Module: exactly one. Branch `deepsignal/p2-kongsberg-tap` from `3b4b76e`
- Lane: `mac` (`gpt-6.2-sol` high). Needs read-only web access to two public format documents (below)
- Mac scratch path: `/private/tmp/deepsignal/p2-kongsberg-tap/` only (docs/CODEX.md rule 1b)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 5/5/3
- Depends on: none. Core `UDPReader` with `encoding` null delivers raw datagram bytes (65535-byte buffer)

## Goal
A tech sees, live and next to the rest of the ship's data, what the multibeam is actually doing: ping rate,
nadir depth, swath width, how many beams are good, the sound speed it is applying at the transducer, its clock
versus the DAS clock, and when someone changed its runtime settings. Summaries only, not bathymetry.

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

- Formats (read the public documents, cite section and version in code comments; do not guess):
  1. KMALL (SIS 5 / K-Controller; EM124, EM304, EM712, EM2040): Kongsberg document 410224 and the public
     reader at github.com/kjerram/kmall. Common header: `numBytesDgm` uint32, `dgmType` 4 chars (`#MRZ`,
     `#SPO`, `#SKM`, `#SVT`, `#SVP`, `#IOP`, `#IIP`, `#SCL`, `#CPO` and others), `dgmVersion` uint8,
     `systemID` uint8, `echoSounderID` uint16, `time_sec` uint32, `time_nanosec` uint32, little-endian,
     length repeated at the end. Large `#MRZ` arrive in partitions (`numOfDgms`, `dgmNum`); ping info is in
     partition 1.
  2. `.all` (SIS 4; EM122, EM302, EM710): Kongsberg document 160692 (EM datagram formats). Length uint32,
     STX 0x02, type byte (`X` XYZ88 depth, `P` position, `A` and `n` attitude, `C` clock, `G` surface
     sound speed, `R` runtime, `I` and `i` installation), ETX 0x03, checksum uint16.
  Only fetch these two documents, read-only, into the scratch path; never commit them; no other downloads.
  If the fetch is blocked, stop and report (the lead queues it in MORNING.md).

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/kongsberg_tap/`:
- `KongsbergTapTransform(Transform)`: input `bytes` (one UDP datagram, possibly several concatenated
  datagrams). Detects KMALL vs `.all` per datagram; unknown or truncated bytes are counted and dropped,
  never raise. kwargs `prefix` (default `MB`), `types` (allowlist), `max_partitions_wait_s`.
- Output: DAS-record dicts. Field contract (#140, #141, #142, #143 depend on these exact names):
  - per ping (`#MRZ` or `X`): `<prefix>_PingTime` (PU time, UNIX s), `<prefix>_NadirDepth` (m below the
    waterline: depth of the valid sounding with smallest absolute across-track distance, corrected per the
    spec to waterline; state the exact correction in a comment and the docs), `<prefix>_SwathWidth` (m,
    across-track span of valid soundings), `<prefix>_BeamCount`, `<prefix>_ValidBeamFraction`,
    `<prefix>_SVTransducer` (m/s, the value the sonar applied), `<prefix>_PingRate` (Hz from consecutive
    PU ping times), `<prefix>_ClockOffset` (s, PU time minus the record timestamp the reader assigned).
  - `#SKM` or `A`: `<prefix>_AttRoll`, `<prefix>_AttPitch`, `<prefix>_AttHeave`, `<prefix>_AttTime` (latest
    sample in the datagram).
  - `#SPO` or `P`: `<prefix>_PosLat`, `<prefix>_PosLon`, `<prefix>_PosTime`.
  - `#SVT` or `G`: `<prefix>_SVProbe` (the sound speed the sonar received from its probe).
  - `#IOP` or `R`: `<prefix>_RuntimeHash` (sha256 prefix of the runtime parameter bytes) and
    `<prefix>_RuntimeChanged` (1 on the first datagram whose hash differs from the previous one).
  - every 10 s of record time: `<prefix>_DgmRates` (JSON string of datagrams per second by type).
- `KongsbergFileReader(Reader)`: replays a `.kmall` or `.all` file as datagram bytes in order, for
  reanalysis (D-REAN1) and tests. Read-only file access.
- Never open a socket. Never send anything to the sonar or SIS.

## Failing test first
`contrib/deepsignal/test/kongsberg_tap/test_tap.py`: fixtures are bytes built in the test from the spec
structs (a small builder helper in the test folder): `#MRZ` single and partitioned, `#SKM`, `#SPO`,
`#SVT`, `#IOP` change detection, `.all` `X`, `A`, `P`, `G`, `R`; truncated and garbage input counted and
dropped; length mismatch; concatenated datagrams; `None` passes through; file reader replays a file written
by the builder. Each numeric output checked against a hand-computed value written in the test.

## Module contract
Docs `contrib/deepsignal/docs/kongsberg_tap.md`: what to ask the SIS operator to enable (UDP datagram
output to the DAS host or a multicast group, which datagram types), the field contract above, the
read-only guarantee. Sample config `contrib/deepsignal/configs/kongsberg_tap_udp.yaml`: `UDPReader`
(port from config, `encoding: null`) to the tap to a text writer. Depends on no other module.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/kongsberg_tap -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/kongsberg_tap contrib/deepsignal/test/kongsberg_tap
```

## Scope
Create or change only: `contrib/deepsignal/kongsberg_tap/**`, `contrib/deepsignal/test/kongsberg_tap/**`,
`contrib/deepsignal/docs/kongsberg_tap.md`, `contrib/deepsignal/configs/kongsberg_tap_*.yaml`, and empty `__init__.py`
files where missing. Everything else is read-only.

## Trust boundaries and data integrity
Datagram bytes are untrusted: check every length against the buffer before unpacking, cap beam and sample
counts at the spec maximums, bound partition reassembly memory and time, never `eval`. NaN and invalid
detections are excluded and counted, never zero-filled. The record timestamp from the reader is never replaced
by PU time; PU time is reported in its own fields.

## Non-goals and banned
No bathymetry gridding, no water-column data, no beam-level output. No sockets, no writes to any system. No
core changes. No new dependency (`struct` only). No loosened, skipped or deleted tests, no swallowed errors.
No writes, deletes or moves in `/private/tmp` outside `/private/tmp/deepsignal/`.

## Usability (anything a tech sees or edits)
Answer each line of desk `docs/USABILITY.md` in the report, or N/A with a reason. Every config error is one
plain-English line naming the setting, what it saw, what it expected, and a good example. Every alarm text
names the source, the two values, the threshold, and the first thing to check.

## Stop rule
No code change needed: stop and report. Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Acceptance tails:
- Open questions:
