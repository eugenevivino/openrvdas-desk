# Brief: p2-iec450-bridge (IEC 61162-450 bridge reader)

- Decision: IDEAS #138, D-SHIP1, from Eugene's 2026-11-18 ask to interface with sonars and ship systems; build per D-NIGHT1
- Risk tier: low (receive only, pure parsing)
- Module: exactly one. Branch `deepsignal/p2-iec450-bridge` from `3b4b76e`
- Lane: `cloud` (Sol medium, fixed)
- Fresh session, under 40 turns
- Upstream home: openrvdas_contrib tree, fork only for now
- Value (techs/science/shore): 4/3/2
- Depends on: none. Core `UDPReader` already joins multicast (`mc_group`) and returns raw bytes when `encoding` is null

## Goal
On a ship whose bridge publishes NMEA on an IEC 61162-450 multicast network, a tech points a normal
`UDPReader` at the group and gets clean NMEA sentences that the existing parse transforms and device files
already understand, plus which bridge device sent each one.

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
- 61162-450 datagram layout (lead summary of the published standard; the full text is paid, so tolerate
  variants): a 6-byte header, `UdPbC` plus a NUL byte, for sentence datagrams. Other headers (`RaUdP`,
  `RrUdP` binary file transfer, anything else) are not sentences: drop them and count them.
  After the header: one or more lines, each `\<tag block>\<NMEA sentence>\r\n`. The tag block is
  comma-separated `key:value` pairs then `*hh`, where hh is the XOR of every character between the opening
  backslash and the `*`. Keys seen: `s` source id (for example `GP0001`), `d` destination, `n` line
  counter, `c` UNIX time in seconds, `g` grouping, `t` text. A line may have no tag block.
- Typical groups (configure, never hard-code): 239.192.0.1 to 239.192.0.8, ports 60001 to 60008, for
  MISC, TGTD, SATD, NAVD, VDRD, RCOM, TIME, PROP; user groups above. Verify on the pilot ship.

## Design (lead decisions; flag disagreement in the report)
Package `contrib/deepsignal/iec450/`, class `Iec450Transform(Transform)`:
- Input `bytes` or `str` (decode bytes as ASCII with `errors='replace'` only after header check).
- kwargs: `output='sentence'` (default, emits the bare NMEA sentence, or a list when a datagram holds
  several) or `'record'` (emits dicts `{timestamp, fields: {iec450_source, iec450_line, iec450_time,
  iec450_sentence}}` using the record timestamp, never the bridge time, as `timestamp`); `sources`
  (optional allowlist of `s` values); `check_tag_checksum=True`; `check_nmea_checksum=False` (core
  `NMEAChecksumTransform` exists for that).
- A bad tag-block checksum drops that line and logs one warning per source per minute (rate-limited).
- `stats()` returns a JSON-safe dict: datagrams seen, non-sentence datagrams dropped by header, bad
  checksums, and per-source line-counter gaps (missing `n` values), which #142 and #143 use as freshness.
- Never change sentence bytes. Never invent a field.
- `contrib/deepsignal/iec450/sim.py`: a loopback-only sender for demos and tests that emits 450 datagrams
  from a text file of sentences to 127.0.0.1; it refuses any non-loopback address with an error.

## Failing test first
`contrib/deepsignal/test/iec450/test_iec450.py`: header accept and reject; tag block parse; checksum
pass and fail; several lines per datagram; no tag block; source allowlist; record mode fields; line-counter
gap counting; `None` passes through; bytes and str inputs; a test that the transform module imports no
`socket` (receive-only by construction); simulator refuses a non-loopback address. One end-to-end test:
simulator to a core `UDPReader` on 127.0.0.1 (unicast loopback, encoding null) into the transform, then
core `ParseNMEATransform` or `ParseTransform` with an existing device file parses a `GGA`.

## Module contract
Docs `contrib/deepsignal/docs/iec450.md`: what 61162-450 is in two sentences, the network placement rule
(read through a 61162-460 gateway, diode or mirror port; never transmit on a bridge network), a sample config.
Sample config `contrib/deepsignal/configs/iec450_navd.yaml`: `UDPReader` (mc_group 239.192.0.4, port
60004, encoding null) to `Iec450Transform` to a text writer. Depends on no other module.

## Acceptance (exact commands, from repo root, Linux, no browser)
```
python3.12 -m unittest discover -s contrib/deepsignal/test/iec450 -t . -v
```
```
python3.12 -m flake8 --config .flake8 contrib/deepsignal/iec450 contrib/deepsignal/test/iec450
```

## Scope
Create or change only: `contrib/deepsignal/iec450/**`, `contrib/deepsignal/test/iec450/**`,
`contrib/deepsignal/docs/iec450.md`, `contrib/deepsignal/configs/iec450_*.yaml`, and empty `__init__.py`
files where missing. Everything else is read-only.

## Usability (anything a tech sees or edits)
Answer each line of desk `docs/USABILITY.md` in the report, or N/A with a reason. Every config error is one
plain-English line naming the setting, what it saw, what it expected, and a good example.

## Trust boundaries and data integrity
Network bytes are untrusted: bound every loop, cap lines per datagram at 64, never `eval`. Never change or
drop a valid sentence. Bridge time (`c:`) is reported as a separate field, never substituted for the
record timestamp.

## Non-goals and banned
No sending to any network except the loopback simulator. No core changes. No new dependency. No
refactors outside Scope. No loosened, skipped or deleted tests, no swallowed errors, no sleeps for
ordering (the end-to-end test may poll with a timeout).

## Stop rule
No code change needed: stop and report. Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Acceptance tails:
- Open questions:
