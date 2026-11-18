# Shared header, prepend to every cloud prompt (D-UPSTREAM0)

- Work only on the fork eugenevivino/openrvdas, on your deepsignal/* branch. Never push to dev or master.
- gh and git may touch OceanDataTools only for a read-only fetch by URL. No pushes, PRs, issues or comments to any OceanDataTools repo, ever.
- Touch only the files your brief names. No secrets, no .env edits, no new dependencies unless the brief says so.
- No em dashes in any text you write.

You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-scoreboard-alpha-codec` from commit `3b4b76e` (the contrib master tree; it is in this fork's history) (if `deepsignal/p2-scoreboard-alpha-codec` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-scoreboard-alpha-codec`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML and pyserial are already OpenRVDAS dependencies; add no other dependency. No network beyond 127.0.0.1 test servers.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-scoreboard-alpha-codec (IDEAS #185: Alpha Protocol codec for LED signs)

- Decision: D-SCORE2
- Risk tier: low (pure functions: Page in, frames out; no I/O)
- Module: exactly one. Branch `deepsignal/p2-scoreboard-alpha-codec` from `3b4b76e`
- Mac scratch path: `/private/tmp/deepsignal/scoreboard-alpha-codec/` only
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
Any sign that speaks the Alpha Communications Protocol shows the board data from one profile, with the
protocol checksum so a corrupted frame is ignored by the sign instead of displayed.

## What to build
`contrib/deepsignal/scoreboard/codecs/alpha.py` exporting `CODEC = AlphaCodec(contract.Codec)`, plus an
empty `codecs/__init__.py`.

- Address: argument, else `profile.addressing['default']`, else 0. Int 0 to 255 or a two-character hex
  string; rendered as two uppercase hex digits. `0` is the broadcast address `00`. Out of range raises
  ScoreboardError.
- Framing keys (defaults as in #182): `type_code` `Z`, `file_label` `A`, `sync` `nul`, `checksum` true,
  optional `mode` (`position`, `code`), `line_separator` default `' '`.
- `encode(page)` returns ONE frame per page:
  `sync` (five `00`, or five `01` if `sync: soh`) + `01` (SOH) + type_code + address + `02` (STX) + `A`
  (Write TEXT) + file_label + [`1B` (ESC) + position + code, only when `mode` is set] + message +
  (if `checksum`: `03` (ETX) + four uppercase hex digits of `contract.checksum(STX..ETX inclusive,
  'sum16')`) + `04` (EOT).
- Message: lines joined with the unescaped `line_separator` decoded latin-1; characters outside 0x20 to
  0x7E become `limits.replace_char`; `upper` charset uppercases first; `digits_sign_point` as in #184.
  (Copy the 10-line charset helper; do not import the text codec, so this branch stands alone.) A line
  longer than `chars_per_line` raises ScoreboardError.
- `init()` returns `[]` in v1 (memory configuration commands are out of scope).
- Docstring states the facts used (from the shared facts) and that multi-line separation and display
  modes must be confirmed on a bench before a profile is marked `verified: bench`.

## Golden vector (put it in tests)
Type `Z`, address 1, file label `A`, checksum on, no mode, message `HELLO`:
`00 00 00 00 00 01 5A 30 31 02 41 41 48 45 4C 4C 4F 03 30 31 46 42 04`
(checksum `01FB` = 16-bit sum of `02 41 41 48 45 4C 4C 4F 03`).

## Tests (at least these)
`contrib/deepsignal/test/scoreboard/test_alpha_codec.py`: the golden vector; `checksum: false` ends
`...4F 04` with no ETX; `sync: soh`; `mode` inserts `1B` + position + code before the message; address
`'0A'` and `10` give the same bytes; address 256 raises; control characters in a cell are replaced;
two-line page joined by the separator; too-long line raises; `contract.codec_class('alpha')` is
`AlphaCodec`.

## Acceptance (exact commands)
```
python3 -m pytest contrib/deepsignal/test/scoreboard/test_alpha_codec.py -q
```
```
python3 -m flake8 --max-line-length=100 contrib/deepsignal/scoreboard/codecs contrib/deepsignal/test/scoreboard/test_alpha_codec.py
```
```
sha256sum contrib/deepsignal/scoreboard/contract.py
```

## Scope
Create: `codecs/__init__.py` (empty), `codecs/alpha.py`, `contract.py` (verbatim), the empty `__init__.py`
files from the shared facts, the test file, and `contrib/deepsignal/scoreboard/docs/alpha-codec.md` (how a technician uses it, under 60 lines; one docs file per
brief so parallel branches never edit the same file).

## Trust boundaries and data integrity
Cell text is untrusted and must never inject protocol control bytes: only 0x20 to 0x7E reach the
message, so no cell can forge an ETX, EOT or ESC.

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
`briefs/cloud/p2-scoreboard-alpha-codec.md` carries the full text. Create
`contrib/deepsignal/scoreboard/contract.py` byte for byte and check the hash.

```python
"""Shared contract for the DeepSignal scoreboard modules.

This file must be byte-identical on every scoreboard branch so the branches
merge cleanly. Do not edit it on a feature branch. Changes go through the
build lead as a new version of this file in every brief.
"""
import importlib
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

CONTRACT_VERSION = 1
PACKAGE = 'contrib.deepsignal.scoreboard'
CODEC_NAMES = ('text', 'alpha', 'modbus')
TRANSPORT_NAMES = ('serial', 'rs485', 'tcp', 'udp', 'modbus_rtu', 'modbus_tcp')
BYTE_TRANSPORTS = ('serial', 'rs485', 'tcp', 'udp')
REGISTER_TRANSPORTS = ('modbus_rtu', 'modbus_tcp')
CHECKSUM_NAMES = ('none', 'sum8', 'xor8', 'lrc', 'sum16', 'crc16_modbus',
                  'crc16_ccitt')
CHECKSUM_FORMATS = ('hex2', 'hex4', 'raw1', 'raw2_le', 'raw2_be')


class ScoreboardError(Exception):
    """Base error. Messages name the profile, key and value at fault."""


class ProfileError(ScoreboardError):
    """A profile file or an override is invalid."""


class TransportError(ScoreboardError):
    """A transport could not open, send or close."""


@dataclass(frozen=True)
class Cell:
    field: Optional[str]
    text: str
    value: Any = None
    stale: bool = False


@dataclass(frozen=True)
class Page:
    lines: List[List[Cell]]

    def line_text(self, index: int) -> str:
        return ''.join(cell.text for cell in self.lines[index])


@dataclass(frozen=True)
class RegisterWrite:
    unit: int
    address: int
    values: List[int]


Frame = Union[bytes, RegisterWrite]


@dataclass
class Profile:
    name: str
    codec: str
    limits: Dict[str, Any]
    framing: Dict[str, Any] = field(default_factory=dict)
    addressing: Dict[str, Any] = field(default_factory=dict)
    pacing: Dict[str, Any] = field(default_factory=dict)
    transport_defaults: Dict[str, Any] = field(default_factory=dict)
    init_frames: List[str] = field(default_factory=list)
    description: str = ''
    source: str = ''
    verified: str = 'unverified'
    path: str = ''


class Codec:
    """Turns a rendered Page into frames for one board."""

    def __init__(self, profile: Profile, address: Any = None):
        self.profile = profile
        self.address = address

    def init(self) -> List[Frame]:
        return []

    def encode(self, page: Page) -> List[Frame]:
        raise NotImplementedError


class Transport:
    """Moves frames to a board: bytes for byte transports, RegisterWrite
    for Modbus transports. Tests replace sleep with a fake."""

    sleep = staticmethod(time.sleep)

    def __init__(self, **settings):
        self.settings = settings

    def open(self) -> None:
        raise NotImplementedError

    def send(self, frames: List[Frame]) -> None:
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError


def _load(kind: str, name: str, names: tuple):
    if name not in names:
        raise ScoreboardError('unknown %s "%s"; expected one of: %s'
                              % (kind, name, ', '.join(names)))
    module = importlib.import_module('%s.%ss.%s' % (PACKAGE, kind, name))
    return getattr(module, kind.upper())


def codec_class(name: str):
    """Return the Codec subclass exported as CODEC by codecs/<name>.py."""
    return _load('codec', name, CODEC_NAMES)


def transport_class(name: str):
    """Return the Transport subclass exported as TRANSPORT by
    transports/<name>.py."""
    return _load('transport', name, TRANSPORT_NAMES)


_SIMPLE_ESCAPES = {'r': '\r', 'n': '\n', 't': '\t', '\\': '\\'}


def unescape(text: str) -> bytes:
    r"""Decode \xNN, \r, \n, \t and \\ in profile text to bytes (latin-1).
    Any other backslash sequence is a ProfileError. Never uses eval."""
    out = []
    i = 0
    while i < len(text):
        char = text[i]
        if char != '\\':
            out.append(char)
            i += 1
            continue
        nxt = text[i + 1:i + 2]
        if nxt in _SIMPLE_ESCAPES:
            out.append(_SIMPLE_ESCAPES[nxt])
            i += 2
        elif nxt == 'x' and len(text) >= i + 4:
            digits = text[i + 2:i + 4]
            try:
                out.append(chr(int(digits, 16)))
            except ValueError:
                raise ProfileError('bad escape "\\x%s" in "%s"' % (digits, text))
            i += 4
        else:
            raise ProfileError('bad escape at position %d in "%s"' % (i, text))
    try:
        return ''.join(out).encode('latin-1')
    except UnicodeEncodeError as err:
        raise ProfileError('non latin-1 character in "%s": %s' % (text, err))


def checksum(data: bytes, name: str) -> int:
    """Checksum of data by name. sum16 is the Alpha Protocol summation."""
    if name == 'none':
        return 0
    if name == 'sum8':
        return sum(data) & 0xFF
    if name == 'xor8':
        value = 0
        for byte in data:
            value ^= byte
        return value
    if name == 'lrc':
        return (-sum(data)) & 0xFF
    if name == 'sum16':
        return sum(data) & 0xFFFF
    if name == 'crc16_modbus':
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
        return crc
    if name == 'crc16_ccitt':
        crc = 0xFFFF
        for byte in data:
            crc ^= byte << 8
            for _ in range(8):
                crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else crc << 1
                crc &= 0xFFFF
        return crc
    raise ProfileError('unknown checksum "%s"; expected one of: %s'
                       % (name, ', '.join(CHECKSUM_NAMES)))


def format_checksum(value: int, fmt: str) -> bytes:
    """Render a checksum value as bytes. Hex digits are uppercase."""
    if fmt == 'hex2':
        return ('%02X' % (value & 0xFF)).encode('ascii')
    if fmt == 'hex4':
        return ('%04X' % (value & 0xFFFF)).encode('ascii')
    if fmt == 'raw1':
        return bytes([value & 0xFF])
    if fmt == 'raw2_le':
        return (value & 0xFFFF).to_bytes(2, 'little')
    if fmt == 'raw2_be':
        return (value & 0xFFFF).to_bytes(2, 'big')
    raise ProfileError('unknown checksum format "%s"; expected one of: %s'
                       % (fmt, ', '.join(CHECKSUM_FORMATS)))
```

Expected: `sha256sum contrib/deepsignal/scoreboard/contract.py` prints `d54e7183e0961744d7aa84ec5bae42e446982701d18f4ac3919a2837a5ea1196`.
