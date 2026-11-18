# Brief: p2-scoreboard-modbus-codec (IDEAS #186: Modbus register codec for large-digit displays)

- Decision: D-SCORE2
- Risk tier: low (pure functions: Page in, frames out; no I/O)
- Module: exactly one. Branch `deepsignal/p2-scoreboard-modbus-codec` from `3b4b76e`
- Mac scratch path: `/private/tmp/deepsignal/scoreboard-modbus-codec/` only
- Lane: `cloud` (Sol medium, fixed)
- Wave: 1 (parallel with the other scoreboard briefs)
- Fresh session, under 40 turns
- Upstream home: fork only for now
- Depends on: none to build (contract.py from the appendix; tests build `contract.Profile` objects directly,
  they do not need the #182 loader)


## Shared scoreboard facts (identical in briefs #182 to #187; do not re-derive)

- Design: vendor-agnostic scoreboard output (D-SCORE2). Three layers: **transport** (how bytes or
  register writes leave), **codec** (`text`, `alpha`, `modbus`: how a board wants the data), **profile**
  (one YAML data file per board model). A new board needs a profile, never code. Design doc:
  https://claude.ai/artifact/XYUFNgc4nP67DBBS7RUviN
- Target hardware: outdoor deck LED scoreboards and large-digit displays (Eugene, 2026-11-18), not winch
  readouts. Brands vary by ship and are not known yet, so nothing may be hard-coded per vendor in Python.
- Package `contrib/deepsignal/scoreboard/` on the contrib tree `3b4b76e`. Layout (each brief owns only
  its listed files):
  ```
  contrib/deepsignal/__init__.py                  empty (create only if missing)
  contrib/deepsignal/scoreboard/__init__.py       empty
  contrib/deepsignal/scoreboard/contract.py       VERBATIM from the appendix, every branch
  contrib/deepsignal/scoreboard/profiles.py       #182
  contrib/deepsignal/scoreboard/profiles/*.yaml   #182
  contrib/deepsignal/scoreboard/transports/       #183 (__init__.py empty)
  contrib/deepsignal/scoreboard/codecs/__init__.py  empty
  contrib/deepsignal/scoreboard/codecs/text.py    #184
  contrib/deepsignal/scoreboard/codecs/alpha.py   #185
  contrib/deepsignal/scoreboard/codecs/modbus.py  #186
  contrib/deepsignal/scoreboard/bench.py          #187
  contrib/deepsignal/test/scoreboard/test_*.py    each brief its own test file
  ```
- **contract.py** (appendix) is the shared interface: `Profile`, `Page`, `Cell`, `RegisterWrite`,
  `Codec`, `Transport`, the error classes, `codec_class()`, `transport_class()`, `unescape()`,
  `checksum()`, `format_checksum()`. Copy it byte for byte (sha256 given in the appendix) and check the
  hash. Never edit it. If it blocks you, say so in the report; the build lead issues a new version.
- Registry by convention: `codecs/<name>.py` exports `CODEC = <class>`; `transports/<name>.py` exports
  `TRANSPORT = <class>`. `contract.codec_class('text')` imports it. No shared mutable registry file.
- Every empty `__init__.py` is zero bytes, so parallel branches merge cleanly.
- Records and the ScoreboardWriter (IDEAS #5) are NOT part of this batch. Nothing here subclasses an
  OpenRVDAS Reader, Transform or Writer, so the old-core vs new-core import issue does not apply.
- Dependencies: standard library, PyYAML and pyserial only (both already OpenRVDAS requirements on
  `3b4b76e`). Add no dependency. Modbus is framed by hand (function code 16), not with pymodbus.
- Security: profiles are untrusted data. `yaml.safe_load` only. Templates use `str.format` on known keys
  only; reject any `{` field name that is not in the allowed set, and reject attribute or index access
  (`{a.b}`, `{a[0]}`). Never `eval`, `exec`, or `codecs.decode(..., 'unicode_escape')`; use
  `contract.unescape()`.
- Stale and missing values must never look fresh. A `Cell` with `stale=True` or `value=None` is shown as
  its `text` (the layout already put the stale marker there); the Modbus codec writes the profile's
  `stale_value`.
- Verified protocol facts available to this batch (cite these, do not add unverified ones):
  - Alpha Communications Protocol Rev D (Adaptive Micro Systems, 2002): frame is at least five `<NUL>`
    (00H) sync bytes (five `<SOH>` may substitute), `<SOH>`, type code, two-character sign address
    `00` to `FF` (`00` is broadcast), `<STX>`, command code, data, optionally `<ETX>` plus checksum, then
    `<EOT>`. Type code `Z` = "All signs". Command `A` = Write TEXT file; the data starts with a one-character
    File Label (power-up default `A`), then an optional Mode Field `<ESC>` + display position + mode code,
    then the message. Checksum: "Four ASCII digits that represent a 16-bit hexadecimal summation of all
    transmitted data from the previous <STX> through the previous <ETX> inclusive. The most significant
    digit is first." Checksum is used only when `<ETX>` precedes `<EOT>`. Bytes in a frame may not be more
    than 1 second apart. Baud for Alpha 2.0 signs: 1200 to 38400.
  - Modbus function code 16 (Write Multiple Registers), RTU: unit, `0x10`, start address (2 bytes, big
    endian), quantity (2), byte count (1), data (big-endian words), CRC-16/Modbus low byte first. Normal
    reply echoes unit, `0x10`, address, quantity, plus CRC. Exception reply: function `0x90` and one
    exception-code byte. TCP: 7-byte MBAP header (transaction id, protocol 0, length = bytes that follow,
    unit) then the same PDU without CRC.
  - Golden vectors computed with contract.py: CRC-16/Modbus of `b'123456789'` = `0x4B37`;
    CRC-16/CCITT-FALSE = `0x29B1`.

## Goal
Large-digit displays that only accept Modbus show the right number, and show a recognizable "no data"
value instead of the last good number when data goes stale.

## What to build
`contrib/deepsignal/scoreboard/codecs/modbus.py` exporting `CODEC = ModbusCodec(contract.Codec)`, plus an
empty `codecs/__init__.py`.

- Unit id: argument, else `profile.addressing['default']`; must be 0 to 247, else ScoreboardError.
- At `__init__`, convert every register entry's `stale_value` with the same rules as a live value; if it
  does not fit its type, raise ProfileError now, not on deck.
- `encode(page) -> list[contract.RegisterWrite]`, one per `framing.registers` entry, in profile order:
  1. Cell = `page.lines[line - 1][cell]`. A missing line or cell, `stale=True`, `value=None`, a bool, a
     non-number, NaN or infinity all mean "use `stale_value`".
  2. Otherwise `x = value * scale`. Integer types: round half away from zero
     (`int(math.copysign(math.floor(abs(x) + 0.5), x))`), then range-check (int16 -32768..32767, uint16
     0..65535, int32 and uint32 likewise). Out of range raises ScoreboardError naming the register and
     value. Never clamp and never wrap: a wrapped number on a deck board is a wrong number.
  3. Words: int16 two's complement as one word; uint16 one word; 32-bit types two words, high word first
     for `word_order: big`, low first for `little`; float32 via `struct.pack('>f', x)` split into two
     words (word order applies).
- `init()` returns `[]`.

## Golden vectors (put them in tests)
Unit 1, register 0, `int16`, `scale: 10`, `stale_value: -32768`:
- value 12.3 -> `RegisterWrite(1, 0, [123])`
- value -0.05 -> `[0xFFFF]` (-0.5 rounds away from zero to -1)
- stale -> `[0x8000]`
- `float32`, scale 1, value 12.5 -> `[0x4148, 0x0000]`; with `word_order: little` -> `[0x0000, 0x4148]`
- `int16`, value 4000, scale 10 -> ScoreboardError (40000 does not fit)

## Tests (at least these)
`contrib/deepsignal/test/scoreboard/test_modbus_codec.py`: the golden vectors; uint32 split both word
orders; NaN and a string value use `stale_value`; missing cell uses `stale_value`; a `stale_value` that
does not fit raises ProfileError at construction; unit 248 raises; `contract.codec_class('modbus')` is
`ModbusCodec`.

## Acceptance (exact commands)
```
python3 -m pytest contrib/deepsignal/test/scoreboard/test_modbus_codec.py -q
```
```
python3 -m flake8 --max-line-length=100 contrib/deepsignal/scoreboard/codecs contrib/deepsignal/test/scoreboard/test_modbus_codec.py
```
```
sha256sum contrib/deepsignal/scoreboard/contract.py
```

## Scope
Create: `codecs/__init__.py` (empty), `codecs/modbus.py`, `contract.py` (verbatim), the empty `__init__.py`
files from the shared facts, the test file, and `contrib/deepsignal/scoreboard/docs/modbus-codec.md` (how a technician uses it, under 60 lines; one docs file per
brief so parallel branches never edit the same file).

## Trust boundaries and data integrity
Values are untrusted numbers. Every path to a register goes through the range check.

## Non-goals and banned
No transports, no profile loader, no writer, no other codec. No new dependencies.
No writes, deletes or moves in `/private/tmp` outside `/private/tmp/deepsignal/`; never `/private/tmp/kalon`.
No loosened, skipped or deleted tests, no swallowed errors, no sleeps for ordering.

## Report format
Under 40 lines: files, test names, RED then GREEN tails, acceptance tails, contract sha256, design
disagreements (do not change the design silently), verified versus inferred.

## Stop rule
Two fix rounds still red: stop and report.

## Result (builder fills in)
- Head sha:
- RED receipt:
- Gate receipt sha256 and verdict:
- What changed, in three lines:
- Open questions:

## Appendix: contract.py (verbatim)
Canonical copy: desk `briefs/scoreboard/contract.py`, sha256 `d54e7183e0961744d7aa84ec5bae42e446982701d18f4ac3919a2837a5ea1196`. The cloud prompt
`briefs/cloud/p2-scoreboard-modbus-codec.md` carries the full text. Create
`contrib/deepsignal/scoreboard/contract.py` byte for byte and check the hash.
