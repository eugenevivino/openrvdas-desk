# Brief: p2-scoreboard-profiles (IDEAS #182: board profile schema, loader and starter profiles)

- Decision: D-SCORE2 (vendor-agnostic scoreboard output), refines D-SCORE1
- Risk tier: low (reads local YAML files only; no device I/O)
- Module: exactly one. Branch `deepsignal/p2-scoreboard-profiles` from `3b4b76e`
- Mac scratch path: `/private/tmp/deepsignal/scoreboard-profiles/` only
- Lane: `cloud` (Sol medium, fixed)
- Wave: 1 (parallel with #183 to #186)
- Fresh session, under 40 turns
- Upstream home: fork only for now (openrvdas_contrib later, Eugene decides)
- Depends on: none (contract.py from the appendix)


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
A technician describes a new deck scoreboard in one small YAML file, and the system rejects a wrong file
at startup with a message naming the bad key, before anything is sent to the board.

## Failing test first
`contrib/deepsignal/test/scoreboard/test_profiles.py`. Write the tests below first, paste the RED run.

## What to build
`contrib/deepsignal/scoreboard/profiles.py`:

- `load_profile(name_or_path, overrides=None, search_path=None) -> contract.Profile`
  - A value ending in `.yaml` or containing a path separator is a file path. Otherwise it is a profile
    name looked up as `<dir>/<name>.yaml` in `search_path` order, first match wins.
  - Default search path: `<repo>/local/scoreboard_profiles/` first, then the package's `profiles/`
    directory. `<repo>` is `os.path.dirname` applied four times to `os.path.realpath(__file__)`; no environment variables,
    no working-directory assumptions. A ship's own profile with the same name wins.
  - `overrides` (a dict from the logger config) is deep-merged over the file (dicts merge key by key,
    anything else replaces), then the merged result is validated.
  - Sets `Profile.path` to the resolved file.
- `validate_profile(data: dict, source: str) -> contract.Profile`, raising `contract.ProfileError` whose
  message names `source` and the dotted key path (for example `red.yaml: framing.checksum: unknown
  checksum "crc32"`).
- `list_profiles(search_path=None) -> list[dict]` with `name`, `path`, `codec`, `verified`, `shadowed`
  (True when a local file hides a packaged one).

Schema (unknown top-level or section keys are an error, so typos fail loudly):

| Key | Type and rule |
|---|---|
| `name` | required str, must equal the file stem |
| `description`, `source` | optional str |
| `verified` | optional, default `unverified`; one of `unverified`, `datasheet`, `bench`, `ship:<name>` (`<name>` = letters, digits, space, `_`, `-`) |
| `codec` | required, one of `contract.CODEC_NAMES` |
| `limits.lines` | required int >= 1 |
| `limits.chars_per_line` | required int >= 1 |
| `limits.charset` | optional, default `ascii`; one of `ascii`, `upper`, `digits_sign_point` (digits, space, `-`, `.`, `+`) |
| `limits.replace_char` | optional single char, default `?`; must itself be valid in the charset |
| `framing` | codec-specific, below |
| `addressing.default` | optional int |
| `addressing.range` | optional `[low, high]` ints, low <= high; `default` must be inside |
| `addressing.multidrop` | optional bool, default false |
| `pacing.inter_frame_delay` | optional float seconds >= 0, default 0 |
| `pacing.max_rate_hz` | optional float > 0 |
| `transport_defaults.type` | optional, one of `contract.TRANSPORT_NAMES` |
| `transport_defaults.*` | other keys passed through to the transport untouched (the transport validates them) |
| `init_frames` | optional list of str (text codec only; each passed through `contract.unescape` to prove it decodes) |

Codec and transport pairing: `codec: modbus` requires a `transport_defaults.type` that is absent or in
`contract.REGISTER_TRANSPORTS`; `text` and `alpha` require absent or `contract.BYTE_TRANSPORTS`.

`framing` by codec:

- `text`: `template` (required str), `frame_per` (`line` default, or `page`), `line_separator` (str,
  default empty, used for `{page}`), `checksum` (one of `contract.CHECKSUM_NAMES`, default `none`),
  `checksum_format` (one of `contract.CHECKSUM_FORMATS`, default `hex2`), `checksum_from` (escaped str,
  default empty = start of frame). Allowed template fields: `address`, `line`, `line_number`, `page`,
  `line1` to `line9`, `checksum`. Validate the template with `string.Formatter().parse`: unknown field,
  attribute or index access, or `{checksum}` appearing more than once is a ProfileError. `{checksum}` is
  only allowed when `checksum` is not `none`, and vice versa. `{line}`/`{line_number}` only with
  `frame_per: line`; `{lineN}` and `{page}` only with `frame_per: page`, and N <= `limits.lines`.
- `alpha`: `type_code` (one char, default `Z`), `file_label` (one char, default `A`), `sync` (`nul`
  default, or `soh`), `checksum` (bool, default true), `mode` (optional: `position` one char and `code`
  one char, both required if `mode` is present), `line_separator` (escaped str, default a single space;
  mark in the profile comment that multi-line separation must be confirmed on a bench).
- `modbus`: `registers` (required non-empty list). Each entry: `line` (int, 1 to `limits.lines`), `cell`
  (int >= 0, default 0), `register` (int 0 to 65535), `type` (`int16`, `uint16`, `int32`, `uint32`,
  `float32`), `scale` (number, default 1), `word_order` (`big` default or `little`; only for 32-bit types),
  `stale_value` (required number; written when the cell is stale or missing). No two entries may write
  overlapping registers.

Starter profiles in `contrib/deepsignal/scoreboard/profiles/` (only these; each must load cleanly):

- `generic_ascii.yaml`: `codec: text`, 1 line x 16 chars, charset `ascii`, `template: '{line}\r\n'`, `verified: unverified`,
  transport_defaults serial 9600 8N1. Purpose: any board that takes a plain line, and a terminal.
- `alpha_sign.yaml`: `codec: alpha`, 1 line x 16 chars, `type_code: Z`, `file_label: A`, `checksum: true`,
  `verified: datasheet`, `source:` the Alpha Rev D document title, transport_defaults serial 9600 8N1
  (comment: 7E1 and other rates exist; set per sign).
- `example_framed.yaml`: `codec: text`, 1 line x 8 chars, `addressing: {default: 1, range: [0, 99]}`, `template: '\x02{address:02d}{line}\x03{checksum}'`,
  `checksum: xor8`, `checksum_format: hex2`, `checksum_from: '\x02'`, `verified: unverified`, header comment
  "Example only. Not a real product."
- `example_modbus.yaml`: `codec: modbus`, 1 line x 6 chars, charset `digits_sign_point`, `addressing: {default: 1, range: [1, 247]}`, one `int16` register at 0 with `scale: 10` and
  `stale_value: -32768`, `verified: unverified`, header comment "Example only. Not a real product."

Do NOT add Red Lion, Laurel, Precision Digital or other vendor profiles: their exact frames are not yet
bench-verified. Eugene and the bench tool (#187) add them later.

## Tests (at least these)
- each starter profile loads; `list_profiles` returns all four
- a local profile with the same name shadows the packaged one (temp dir search path)
- overrides deep-merge (`{'transport_defaults': {'baudrate': 19200}}` keeps `type`)
- each of: unknown top-level key, unknown `framing` key, `name` not equal to stem, bad `verified`,
  `codec: modbus` with `type: serial`, template field `{foo}`, `{line.__class__}`, `{line[0]}`,
  `{checksum}` with `checksum: none`, `{line2}` with `limits.lines: 1`, overlapping Modbus registers,
  bad escape `\q` in `init_frames` -> ProfileError naming the key
- `yaml.safe_load` is used (a `!!python/object` tag is rejected)

## Acceptance (exact commands)
```
python3 -m pytest contrib/deepsignal/test/scoreboard/test_profiles.py -q
```
```
python3 -m flake8 --max-line-length=100 contrib/deepsignal/scoreboard/profiles.py contrib/deepsignal/test/scoreboard/test_profiles.py
```
```
sha256sum contrib/deepsignal/scoreboard/contract.py
```

## Scope
Create: `profiles.py`, `profiles/*.yaml` (the four above), `contract.py` (verbatim), the empty
`__init__.py` files listed in the shared facts, the test file, and `contrib/deepsignal/scoreboard/docs/profiles.md` (how a technician uses it, under 60 lines; one docs file per
brief so parallel branches never edit the same file). Nothing else.

## Trust boundaries and data integrity
Profile files are untrusted. Fail closed: any doubt is a ProfileError at load time, never a guess.

## Non-goals and banned
No codecs, no transports, no writer. No vendor profiles beyond the four. No new dependencies.
No writes, deletes or moves in `/private/tmp` outside `/private/tmp/deepsignal/`; never `/private/tmp/kalon`.
No loosened, skipped or deleted tests, no swallowed errors, no sleeps for ordering.

## Report format
Under 40 lines: files, test names, RED then GREEN tails, acceptance tails, contract sha256, any schema
point you disagree with (do not change the design silently), verified versus inferred.

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
`briefs/cloud/p2-scoreboard-profiles.md` carries the full text. Create
`contrib/deepsignal/scoreboard/contract.py` byte for byte and check the hash.
