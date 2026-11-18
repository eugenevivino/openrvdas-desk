# Scoreboard output research and design (2026-11-17 to 2026-11-18)

Source thread: T-SCORE ("Design scoreboard output module"). Live design doc:
https://claude.ai/artifact/XYUFNgc4nP67DBBS7RUviN (the doc's early sections predate D-SCORE2; where they
differ, this file and decisions D-SCORE2 and D-SCORE3 win).

Decisions: D-SCORE1 (one ScoreboardWriter fed from CachedDataServer), D-SCORE2 (vendor-agnostic:
transport, codec, profile), D-SCORE3 (stale defaults). Briefs: `briefs/p2/182-187-scoreboard-*.md`
(numbers provisional until the build lead confirms) and `briefs/deepsignal-scoreboard-writer.md` (#5).

## 1. Bottom line

- Target hardware is the **outdoor deck LED scoreboard**: large, sunlight-readable boards that deck crew
  read during operations (Eugene, 2026-11-18). Not winch line-monitoring displays such as the LCI-90i.
- **No public source names the deck scoreboard brand** on Revelle, Sally Ride, Healy, Armstrong,
  Atlantis or Sikuliaq. Ship handbooks list lab monitor walls and serial or UDP repeater feeds only.
  Eugene will gather ship models himself.
- So the output is **vendor-agnostic**: a new board is a YAML profile, not code. Three codecs (templated
  text, Alpha Protocol, Modbus registers) and six transports (serial, RS-485, TCP, UDP, Modbus RTU,
  Modbus TCP) cover every documented large-digit and LED sign family found.
- Stale data: per-field threshold, default 10 s; stale shows dashes (or blanks), never the last value.

## 2. Fleet research: what ships document

Searched: ship handbooks, RVTEC presentations, UNOLS documents, MetAcq manual, ship web pages, photo
archives. Confidence is about the claim in that row only.

| Ship | What is documented | Hardware named | Confidence | Source |
|---|---|---|---|---|
| R/V Roger Revelle | Main display array in the Computer Lab; serial (DB9) or UDP feeds of nav, MET and MRU data in all labs; gyro and doppler log repeaters; MetAcq for MET; VMs shown via multicast KVM | Markey winches; no display model | High for feeds and monitors; none for a deck board model | [Revelle handbook, section 4](https://scripps.ucsd.edu/ships/revelle/handbook/section-4-ships-and-scientific-equipment-description) |
| R/V Sally Ride | "Wall of monitors" in the Main Lab (15-monitor array; 8 in the Wet Lab); point-to-point serial network (SIS); winch shack plus consoles forward and in the Main Lab | Dual Markey CAST6, Markey traction winch; no display model | High for monitors; none for a deck board model | [Sally Ride handbook (2021)](https://scripps.ucsd.edu/system/files/2021-07/Handbook%20Sally%20Ride.2021-07-12.pdf), [Sally Ride deck and lab spaces (2024)](https://scripps.ucsd.edu/system/files/2024-03/DeckLabSpaces_SR_3-2024.pdf) |
| USCGC Healy | Photo captioned "CTD scoreboard" (2013): "The scoreboard says that the CTD ... weighs 686 lbs", so it shows winch tension | Make and model not stated | Medium that it is a winch readout; none for model | [PolarTREC photo](https://media.arcus.org/album/polartrec-2013-andrea-skloss/22243); [Healy cruise planning manual](https://www.unols.org/sites/default/files/healy_2.pdf) has no display content |
| R/V Atlantis | Winch line count, speed and tension "displayed at the control center, in the labs and on the bridge" | Markey DESH-5, DUTW-9-11; display model not stated | Medium (page partly read via summary) | [WHOI Atlantis winches page](https://www.whoi.edu/what-we-do/explore/ships/ships-atlantis/ships-atlantis-scientific-equipment/ships-atlantis-scientific-equipment-winches-wires/) |
| R/V Sikuliaq | PLC winch data via a ZeroMQ data broker to HMIs and a LabVIEW display; NMEA-style `@RCWD` sentence at 20 Hz; "Serial communication could not go below 1.6 sec" | Rapp winch system, HMI, Raspberry Pi; no LED model | High | [RVTEC 2017 Sikuliaq winch monitoring](https://www.unols.org/sites/default/files/201717rvt_breakout6_SikuliaqWinchMonitoring.pdf) |
| UNOLS fleet (winch displays) | MTNW LCI-90i is the standard line monitor: "over 1,100 displays in use" (2009); LCI-90i Bridge Remote; RS-485, RS-232, USB, Ethernet; "Most installations are RS-485 based" | MTNW LCI-90i, LCI-80x; older LCI-90, LCI-90r; also 3PS SD50, Rapp, Hawboldt, Scantrol | High | [RVTEC 2009 MTNW talk](https://www.unols.org/sites/default/files/200911rvtap21.pdf), [RVTEC 2016 line monitoring forum](https://www.unols.org/sites/default/files/201611rvt_BreakOut_LCI90i_LineMonitoringEquipment.pdf) |

MetAcq (Scripps met system, [operator's manual Rev 2.00](http://bcodata.whoi.edu/GATEKEEPERS/MetAcq.pdf)):
on-screen panels and a web server only; generic serial and UDP outputs; no external display hardware
named. Its winch example config names Markey winch readouts at 2400 baud.

Not found anywhere: Daktronics, Trans-Lux, Electro-Mech, Nevco, Colorado Time, Alpha or any LED sign
brand on a UNOLS or USCG research ship. Public text does not answer this; ship photos of nameplates or
technicians do.

## 3. Winch data formats (useful inputs, not the display target)

- LCI-90i output line: `RD,20160621T23:59:59.050,<tension>,<speed>,<payout>,<checksum><CR><LF>`
  ([RVTEC 2023 ECWP winch data talk](https://www.unols.org/sites/default/files/2023-11/202310rvt_apxli.pdf)).
- UNOLS draft winch string `$WIR,<date>,<time>,<tension>,<speed>,<payout>,<warnings byte>,<alarms byte>,<checksum>`
  (same talk) and the longer `$WNC` string with unit codes (tension 0=lbf, 1=kips, 2=kN, 3=kg, 4=ton,
  5=tonne; payout 0=m ... 5=fathoms; speed 0=m/min ... 5=knots) ([RVTEC 2016 display talk](https://www.unols.org/sites/default/files/201611rvt_BreakOut_LCI90i_LineMonitoringDisplay.pdf)).
  Example dates in both sources are invalid (day 31 of June), as printed.
- Hawboldt winch feed: binary, described as "Messy" (2023 talk).
- The 2023 talk lists "Add a bridge display" and "Convert from a TCP/UDP feed to serial feed" as wanted
  uses, which the scoreboard writer covers.

## 4. Outdoor LED and large-digit displays: verified protocols

| Maker and model | Outdoor fit | Interface | Protocol (verified) | Source |
|---|---|---|---|---|
| Red Lion LD2SS6P0 / LD4SS6P0 (2.25 in or 4 in digits, 6 digits) | NEMA 4X/IP65 face; readable to 130 or 180 ft; 0 to 50 C; vendor warns sun ages the overlay | RS-232 or RS-485 (jumper), 300 to 38400 baud, 7 or 8 bits, odd, even or no parity | ASCII `N xx I d6..d1 <CR>`: `N` + two-digit address (0 to 99) for multi-unit loops, identifier char, digits; `<CR>` only terminator; up to 32 units per RS-485 line; no checksum. Identifier meaning for the main display not yet confirmed | [Red Lion LDSS datasheet](https://www.walkerindustrial.com/v/vspfiles/pdf/datasheet/RedLion/redlionldss.pdf) |
| Adaptive Micro Systems Alpha signs (AlphaVision, AlphaEclipse, AlphaPremiere, 4000 and 7000 series) | Outdoor models exist; rating per model | Serial; physical layer not stated in the protocol document | See section 5 | [Alpha Communications Protocol Rev D, 2002](https://mrynet.com/FTP/Hardware/Alpha-Led_sign-97088061.pdf) |
| Precision Digital PD2-6081 Helios (1.8 in, 6 alphanumeric characters) | "SunBright", Type 4X/IP65, -40 to 65 C, readable to 100 ft | RS-485 and USB, 300 to 19200 baud | Modbus RTU master, slave or snooper; addresses 1 to 247; register map in a separate PDF not yet read | [Precision Digital PD2-6081](https://predig.com/family/PD2-6081) |
| Laurel Electronics Laureate serial-input remote display (6 digits) | NEMA 4X/IP65 when panel mounted | RS-232, RS-485, USB or Ethernet (Ethernet is Modbus only), 300 to 19200 baud, 8N1 for Custom ASCII | Custom ASCII `*<addr><cmd><value><CR>[<LF>]` (addresses 0 to F), or Modbus RTU/ASCII | [Laurel remote display manual](https://www.laurels.com/downloadfiles/remote-manual.pdf) |
| Daktronics, Trans-Lux, Electro-Mech, Nevco, Colorado Time Systems | Built for outdoor sports and signage | Typically serial from the vendor's own controller | Proprietary or controller-specific; not verified | Not verified |

Also seen: Rugged Controls (formerly MTNW) line control displays page names the LCI-90i family and
"Offshore Display" products, with no specs or customers on the page
([Rugged Controls](https://rugged-controls.com/products/line-control-displays)).

## 5. Alpha Communications Protocol facts used in the Alpha codec

All verbatim from Rev D (Aug 15 2002), page numbers as printed in the extracted text:

- Sync: "A minimum of five <NUL>s (00H) must be transmitted as frame synchronization characters. Five
  <SOH>s (01H) may be substituted for the five <NUL>s. The sign uses these five characters to establish
  the baud rate." (Table 4, p.9)
- Frame: `<NUL> x5, <SOH>, Type Code, Sign Address, <STX>, Command Code, Data Field, [<ETX>, Checksum], <EOT>`.
- Type code: "Z" 5AH "All signs"; "?" also all signs (wildcard). Address: two ASCII hex digits "00" to
  "FF"; "00" is broadcast.
- Command "A" (41H) = Write TEXT file. Data: File Label (power-up default "A"), optional Mode Field
  (`<ESC>` + display position + mode code), then the message. "On one-line signs, the Display Position
  is irrelevant, but it still must be included" (when a Mode Field is sent).
- Checksum: "Four ASCII digits that represent a 16-bit hexadecimal summation of all transmitted data
  from the previous <STX> through the previous <ETX> inclusive. The most significant digit is first."
  Used only when `<ETX>` precedes `<EOT>`. Hex case not stated (we send uppercase).
- Timing: "Time-out period: 1 second (delays between bytes cannot exceed this)"; nested frames need
  100 ms after `<STX>`.
- Baud: Alpha 2.0 1200 to 38400; Alpha 1.0 up to 9600; ASCII Printable mode at 9600.
- Golden frame computed for the briefs (type Z, address 01, label A, "HELLO", checksum on):
  `00 00 00 00 00 01 5A 30 31 02 41 41 48 45 4C 4C 4F 03 30 31 46 42 04`.
- Not yet read: Appendix A (valid file labels), Standard Modes (p.87), worked checksum example (p.54).

## 6. OpenRVDAS evaluation (what the design builds on)

Code reviewed: OceanDataTools/openrvdas master `3f3d0c37` (v2.7.2); the DeepSignal overlay builds on the
contrib tree `3b4b76e`, which carries an older core.

- Pipeline: a Listener reads (readers in parallel), transforms in series, and writes (writers in parallel
  threads, one lock per writer). Each logger is its own process under the logger manager.
- Records: raw `str`/`bytes`; `DASRecord` (`data_id`, `message_type`, `timestamp`, `fields`,
  `metadata`); record dicts `{timestamp, fields}`; CDS field dicts `{field: [[ts, value], ...]}`.
- Registration: no registry. `listen.py` resolves `class:` from its own imports or a `module:` dotted
  path. Only the kwargs `readers`, `reader`, `transforms`, `writers`, `writer`, `mirror_to` are
  instantiated as nested components.
- Tapping stages: CachedDataServer subscription (any published field, the default); inline writer in an
  instrument logger; `mirror_to` on a reader or transform (taps that exact stage, for example raw NMEA);
  ComposedWriter branch; UDP or MQTT.
- Why a new writer: the zero-code chain `CachedDataReader -> FormatTransform -> SerialWriter` fails on
  multi-instrument boards because the CDS delivers one record per timestamp holding only changed
  fields, so the board shows defaults instead of last good values. A latest-value cache with its own
  render clock is required.
- `SerialWriter` is write only, one record per write, no framing, checksum or pacing, and its
  `exclusive` lock means boards on one RS-485 line need one writer.
- `Listener.quit()` does not close writers; render threads must be daemons.
- Upstream guidance: CONTRIBUTING.md steers new modules to `openrvdas_contrib`; PRs target `dev`. Hard
  rule in this project: nothing goes to OceanDataTools until Eugene approves.

## 7. Current design (D-SCORE2, D-SCORE3)

```
layout (what to show)  ->  codec + profile (how this board wants it)  ->  transport (how bytes leave)
  pages, cells, stale      text | alpha | modbus, driven by profile        serial | rs485 | tcp | udp | modbus_rtu | modbus_tcp
```

- **Package** `contrib/deepsignal/scoreboard/` with a shared `contract.py` (byte-identical on every
  branch; canonical copy `briefs/scoreboard/contract.py`): Profile, Page, Cell, RegisterWrite, Codec and
  Transport bases, errors, registry by convention (`codecs/<name>.py` exports `CODEC`,
  `transports/<name>.py` exports `TRANSPORT`), `unescape()` (no eval), checksums (`none`, `sum8`,
  `xor8`, `lrc`, `sum16`, `crc16_modbus`, `crc16_ccitt`; checked against `0x4B37` and `0x29B1` for
  `123456789`).
- **Profiles**: strict YAML schema, `yaml.safe_load`, unknown keys fail, template fields allowlisted;
  ship profiles in `local/scoreboard_profiles/` shadow packaged ones; each carries `source` and
  `verified` (`unverified`, `datasheet`, `bench`, `ship:<name>`). Starter set: `generic_ascii`,
  `alpha_sign`, and two labelled examples. Vendor profiles (Red Lion, Laurel, Precision Digital) wait
  for bench verification.
- **Transports** are written on pyserial and sockets, not by wrapping OpenRVDAS writers (the contrib
  base's writers differ from current core). Modbus function 16 is framed by hand: no new dependency.
- **Writer (#5)**: latest-value cache, page and cell layout, daemon render loop, per-field stale
  threshold (default 10 s, same as the console MVP source-loss test), stale shown as dashes or blanks,
  never the last value; `#` fill instead of truncating a number; exponential backoff on link loss with
  init frames resent on recovery.
- **Bench tool**: `list`, `check` (prints exact bytes), `send` (dry run unless `--yes`).

## 8. Open items

- Board makes and models per ship (Eugene is collecting).
- Red Lion identifier character, Laurel command letters and the Precision Digital register map, before
  their profiles ship.
- Alpha multi-line separation and display modes, to confirm on a bench.
- Whether an LCI-90i Bridge Remote accepts third-party input (not stated in any source found).
- Upstream home (core or openrvdas_contrib), only when Eugene lifts the upstream hold.

## 9. Sources opened

- https://scripps.ucsd.edu/ships/revelle/handbook/section-4-ships-and-scientific-equipment-description
- https://scripps.ucsd.edu/system/files/2021-07/Handbook%20Sally%20Ride.2021-07-12.pdf
- https://scripps.ucsd.edu/system/files/2024-03/DeckLabSpaces_SR_3-2024.pdf
- https://media.arcus.org/album/polartrec-2013-andrea-skloss/22243
- https://www.unols.org/sites/default/files/healy_2.pdf
- https://www.whoi.edu/what-we-do/explore/ships/ships-atlantis/ships-atlantis-scientific-equipment/ships-atlantis-scientific-equipment-winches-wires/
- http://bcodata.whoi.edu/GATEKEEPERS/MetAcq.pdf
- https://www.unols.org/sites/default/files/201717rvt_breakout6_SikuliaqWinchMonitoring.pdf
- https://www.unols.org/sites/default/files/2023-11/202310rvt_apxli.pdf
- https://www.unols.org/sites/default/files/200911rvtap21.pdf
- https://www.unols.org/sites/default/files/201611rvt_BreakOut_LCI90i_LineMonitoringDisplay.pdf
- https://www.unols.org/sites/default/files/201611rvt_BreakOut_LCI90i_LineMonitoringEquipment.pdf
- https://rugged-controls.com/products/line-control-displays
- https://www.walkerindustrial.com/v/vspfiles/pdf/datasheet/RedLion/redlionldss.pdf
- https://mrynet.com/FTP/Hardware/Alpha-Led_sign-97088061.pdf
- https://predig.com/family/PD2-6081
- https://www.laurels.com/downloadfiles/remote-manual.pdf
- https://github.com/OceanDataTools/openrvdas (master `3f3d0c37`, dev `1a6f1edb`)

Failed or not read: the LCI-90i user manual on manualzz (fetch refused); Precision Digital and Laurel
Modbus register tables (linked PDFs not opened).
