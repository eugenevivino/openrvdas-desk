# Shared header, prepend to every cloud prompt (D-UPSTREAM0)

- Work only on the fork eugenevivino/openrvdas, on your deepsignal/* branch. Never push to dev or master.
- gh and git may touch OceanDataTools only for a read-only fetch by URL. No pushes, PRs, issues or comments to any OceanDataTools repo, ever.
- Touch only the files your brief names. No secrets, no .env edits, no new dependencies unless the brief says so.
- No em dashes in any text you write.

You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-scoreboard-transports` from commit `3b4b76e` (the contrib master tree; it is in this fork's history) (if `deepsignal/p2-scoreboard-transports` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-scoreboard-transports`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML and pyserial are already OpenRVDAS dependencies; add no other dependency. No network beyond 127.0.0.1 test servers.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-scoreboard-transports (IDEAS #183: scoreboard transports: serial, RS-485, TCP, UDP, Modbus RTU and TCP)

- Decision: D-SCORE2
- Risk tier: medium (opens serial ports and sockets; tests use only ptys and 127.0.0.1)
- Module: exactly one. Branch `deepsignal/p2-scoreboard-transports` from `3b4b76e`
- Mac scratch path: `/private/tmp/deepsignal/scoreboard-transports/` only
- Lane: `cloud` (Sol medium, fixed)
- Wave: 1
- Fresh session, under 40 turns
- Upstream home: fork only for now
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
The same rendered board data reaches a scoreboard over RS-232, RS-485, TCP, UDP or Modbus, chosen by
one `type:` value in config, with a clear error when the link is down.

## Lead decision (flag disagreement in the report)
Transports are written directly on pyserial and `socket`, not by wrapping OpenRVDAS writers. Reason: the
base `3b4b76e` carries an older core whose writer classes differ from current core, and Modbus needs
request and reply handling the writers do not have. The design doc's "wrap existing writers" idea is
replaced by this.

## What to build
`contrib/deepsignal/scoreboard/transports/` with an empty `__init__.py` and one module per name in
`contract.TRANSPORT_NAMES`, each exporting `TRANSPORT = <class>` subclassing `contract.Transport`.

Common rules:
- Constructor takes keyword settings only and validates them immediately: unknown key, wrong type or
  out-of-range value raises `contract.TransportError` naming the key. No I/O in the constructor.
- `open()` connects; `close()` is safe to call twice; `send(frames)` opens lazily if needed.
- `inter_frame_delay` (float seconds, default 0, accepted by every transport): `self.sleep(delay)` between
  frames, never after the last one, never before the first. Tests replace `sleep` with a recorder.
- On any I/O error in `send`: close, then raise `TransportError` with the cause. No retry loops and no
  backoff here (the writer, IDEAS #5, owns reconnect policy).
- Byte transports raise `TransportError` if given a `RegisterWrite`; Modbus transports raise it if given
  `bytes`.
- Never log frame contents above DEBUG.

Per transport:
- `serial`: keys `port` (required), `baudrate` (default 9600), `bytesize` (5 to 8, default 8), `parity`
  (`N`, `E`, `O`, `M`, `S`; default `N`), `stopbits` (1, 1.5, 2; default 1), `xonxoff`, `rtscts` (bools,
  default false), `write_timeout` (float, default 2.0), `exclusive` (bool, default true; passed to
  pyserial so a second process cannot interleave output on the same port).
- `rs485`: all `serial` keys plus `rts_level_for_tx` (default true), `rts_level_for_rx` (default false),
  `delay_before_tx`, `delay_before_rx` (float or None). Sets `serial.rs485.RS485Settings` on the port after
  opening. If the driver refuses (pty, unsupported adapter) raise `TransportError` that says to use
  `type: serial` with an auto-direction adapter. Build the settings through one small method so a test
  can check them with a fake serial class.
- `tcp`: `host`, `port` (required), `connect_timeout` (default 5.0), `send_timeout` (default 5.0). Uses
  `socket.create_connection` and `sendall`.
- `udp`: `host`, `port` (required), `broadcast` (bool, default false; sets `SO_BROADCAST`). One datagram
  per frame.
- `modbus_rtu`: serial keys plus `response_timeout` (default 1.0). For each `RegisterWrite`: build function
  16 exactly as in the shared facts, append CRC with `contract.checksum(..., 'crc16_modbus')` low byte
  first, write it, read the 8-byte reply within `response_timeout`, check unit, function, address,
  quantity and CRC. Exception reply (function `0x90`) raises `TransportError` with the exception code.
  Unit 0 (broadcast) sends and reads no reply. Values must be 0 to 65535 and 1 to 123 words, else
  `TransportError` before anything is written.
- `modbus_tcp`: `host`, `port` (default 502), `connect_timeout`, `response_timeout`. MBAP header with a
  transaction id that increments per request and wraps at 65535; check the reply's transaction id, unit,
  function, address and quantity; exception replies as above.

## Golden vectors (from contract.py, put them in tests)
- RTU request, unit 1, address 0, values `[123]`: `01 10 00 00 00 01 02 00 7B E6 73`
- RTU normal reply for it: `01 10 00 00 00 01 01 C9`
- TCP request, transaction 1, same write: `00 01 00 00 00 09 01 10 00 00 00 01 02 00 7B`

## Tests (at least these)
`contrib/deepsignal/test/scoreboard/test_transports.py`:
- serial: a pty pair (`os.openpty()`, open the slave with `os.ttyname`) receives the exact bytes of two
  frames, with one recorded sleep of `inter_frame_delay` between them
- serial: bad `parity`, unknown key -> TransportError without opening anything
- rs485: the settings method builds RS485Settings with the configured values (fake serial class)
- tcp: a 127.0.0.1 server thread receives the frames in order; connection refused -> TransportError
- udp: a bound 127.0.0.1 socket receives one datagram per frame
- modbus_rtu: over a pty, a fake slave thread checks the golden request and returns the golden reply;
  a bad CRC reply, an exception reply (`01 90 02` + CRC) and a timeout each raise TransportError
- modbus_tcp: a 127.0.0.1 fake server checks the golden request and replies; transaction ids increment
- every transport: type mismatch (`bytes` vs `RegisterWrite`) raises TransportError
- `contract.transport_class(name)` returns each class

## Acceptance (exact commands)
```
python3 -m pytest contrib/deepsignal/test/scoreboard/test_transports.py -q
```
```
python3 -m flake8 --max-line-length=100 contrib/deepsignal/scoreboard/transports contrib/deepsignal/test/scoreboard/test_transports.py
```
```
sha256sum contrib/deepsignal/scoreboard/contract.py
```

## Scope
Create: `transports/` (`__init__.py` empty plus six modules), `contract.py` (verbatim), the empty
`__init__.py` files from the shared facts, the test file, and `contrib/deepsignal/scoreboard/docs/transports.md` (how a technician uses it, under 60 lines; one docs file per
brief so parallel branches never edit the same file).

## Trust boundaries and data integrity
Device replies are untrusted: length-check before indexing, never trust a reply length field. A
transport never alters frame bytes. A failed send is always an exception, never a silent drop.

## Non-goals and banned
No codecs, profiles or writer. No retry or backoff loops. No real hardware, no network beyond
127.0.0.1. No new dependencies (no pymodbus, no pyModbusTCP).
No writes, deletes or moves in `/private/tmp` outside `/private/tmp/deepsignal/`; never `/private/tmp/kalon`.
No loosened, skipped or deleted tests, no swallowed errors, no sleeps for ordering (use events and the
injected `sleep`).

## Report format
Under 40 lines: files, test names, RED then GREEN tails, acceptance tails, contract sha256, design
disagreements, verified versus inferred, and anything that must be checked on real RS-485 hardware.

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
`briefs/cloud/p2-scoreboard-transports.md` carries the full text. Create
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
