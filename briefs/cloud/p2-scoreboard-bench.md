# Shared header, prepend to every cloud prompt (D-UPSTREAM0)

- Work only on the fork eugenevivino/openrvdas, on your deepsignal/* branch. Never push to dev or master.
- gh and git may touch OceanDataTools only for a read-only fetch by URL. No pushes, PRs, issues or comments to any OceanDataTools repo, ever.
- Touch only the files your brief names. No secrets, no .env edits, no new dependencies unless the brief says so.
- No em dashes in any text you write.

You are building ONE module for the DeepSignal overlay on OpenRVDAS, on Eugene's own fork. Work only in this repository (eugenevivino/openrvdas). Do NOT touch, open pull requests against, or push to OceanDataTools or any upstream repository. Nothing here is sent upstream.

Branches: create branch `deepsignal/p2-scoreboard-bench` from `deepsignal/scoreboard-integ` (the build lead's merge of #182 to #186; if it does not exist on origin, stop and report) (if `deepsignal/p2-scoreboard-bench` already exists on origin, check it out instead). Commit your work on that branch only, with one clear commit message, and leave it pushed to origin `deepsignal/p2-scoreboard-bench`. Do not touch any other branch, `dev` or `master`. If you cannot push, leave the commit on the branch in your task and say so.

Environment notes: Python only; Node is not needed. Use `python3.12` if it exists, otherwise `python3` (3.11 or newer). If pytest is missing use `python3 -m unittest`. If flake8 is missing, `pip install flake8` into a throwaway venv and say you did. PyYAML and pyserial are already OpenRVDAS dependencies; add no other dependency. No network beyond 127.0.0.1 test servers.

Write the failing test first and paste its RED output, then make it GREEN. Run every acceptance command at the end and paste the tails. Report under 40 lines: files changed, test names, RED then GREEN tail, acceptance results, any design point you disagree with (do not change a design silently), what you verified versus inferred, and what must run outside the sandbox.

Stop rule: two fix rounds still red means stop and report.

The full brief follows.

----------------------------------------------------------------
# Brief: p2-scoreboard-bench (IDEAS #187: bench tool to check a board profile and send a test frame)

- Decision: D-SCORE2
- Risk tier: medium (`send` drives a real board on the bench; dry run by default)
- Module: exactly one. Branch `deepsignal/p2-scoreboard-bench` from `deepsignal/scoreboard-integ`
- Mac scratch path: `/private/tmp/deepsignal/scoreboard-bench/` only
- Lane: `cloud` (Sol medium, fixed)
- Wave: 2. Base `deepsignal/scoreboard-integ` = the build lead's merge of #182 to #186 (all green). If that
  branch does not exist on origin, stop and report; do not merge them yourself.
- Fresh session, under 40 turns
- Upstream home: fork only for now
- Depends on: #182 profiles, #183 transports, #184 text, #185 Alpha and #186 Modbus codecs (imports them)


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
A technician with a new scoreboard on the bench writes a profile, sees exactly which bytes it would
send, then lights the board with a test number, in under 15 minutes and without writing code.

## What to build
`contrib/deepsignal/scoreboard/bench.py`, run as `python3 -m contrib.deepsignal.scoreboard.bench`, argparse
subcommands:

- `list`: every profile from `profiles.list_profiles()`: name, codec, verified, path, and `(local,
  shadows packaged)` when it applies.
- `check PROFILE [--set KEY=VALUE ...] [--text LINE ...] [--stale] [--address N]`:
  load the profile (`--set` builds the overrides dict: dotted keys, values parsed with `yaml.safe_load`
  so `--set transport_defaults.baudrate=19200` is an int), build a Page from the `--text` lines (default:
  one line of `8` repeated `chars_per_line` times, which lights every segment), one Cell per line with
  `value` = float of the text when it parses, else None; `--stale` marks every cell stale. Encode with
  `contract.codec_class(profile.codec)`. Print `init()` frames and the page frames. Bytes: one line of
  spaced uppercase hex and one line of text with non-printables as `\xNN`. RegisterWrite: unit, address,
  words in hex and decimal. Print the profile's `verified` and `source`. Exit 0, or 1 with the
  ProfileError or ScoreboardError message (no traceback) on stderr.
- `send PROFILE [check options] [--transport TYPE] [--port P] [--host H] [--baud N] [--repeat N]
  [--interval S] [--yes]`: run `check`, then build the transport from `transport_defaults` overridden
  by the command-line options, and print the resolved transport settings. Without `--yes` it stops
  there (dry run) and says how to send. With `--yes` it opens the transport, sends `init()` frames once,
  then the page frames `--repeat` times (default 1) every `--interval` seconds (default 1.0), closes,
  and exits 0; a TransportError prints the message and exits 2.
- `main(argv=None, transport_factory=None)` so tests inject a fake transport. No module-level side
  effects.

## Tests (at least these)
`contrib/deepsignal/test/scoreboard/test_bench.py`:
- `list` shows the four starter profiles
- `check alpha_sign --text HELLO --address 1` prints the #185 golden hex
- `check example_framed --text ' 12.3' --address 1` prints the #184 golden hex
- `check example_modbus --text 12.3 --address 1` prints unit 1, address 0, word 123; with `--stale`
  prints the stale value
- `check` on a profile file with an unknown key exits 1 and names the key
- `send` without `--yes` opens no transport (fake factory never called)
- `send --yes --repeat 2` sends init once and page frames twice through the fake transport
- `--set transport_defaults.baudrate=19200` reaches the transport settings as an int

## Acceptance (exact commands)
```
python3 -m pytest contrib/deepsignal/test/scoreboard -q
```
```
python3 -m flake8 --max-line-length=100 contrib/deepsignal/scoreboard contrib/deepsignal/test/scoreboard
```
```
python3 -m contrib.deepsignal.scoreboard.bench check alpha_sign --text HELLO --address 1
```

## Scope
Create: `bench.py`, the test file, and `contrib/deepsignal/scoreboard/docs/bench.md` (a technician's
walkthrough: copy `generic_ascii.yaml` to `local/scoreboard_profiles/`, edit, `check`, `send --yes`,
then set `verified: bench`). Read-only: everything else, including `contract.py`.

## Usability (a technician runs this)
Answer each line of `docs/USABILITY.md` in the result, or mark N/A with a reason.

## Trust boundaries and data integrity
`--set` values go through `yaml.safe_load` and then full profile validation. Dry run is the default;
nothing reaches a device without `--yes`.

## Non-goals and banned
No writer, no CachedDataServer, no network beyond 127.0.0.1 in tests. No new dependencies.
No writes, deletes or moves in `/private/tmp` outside `/private/tmp/deepsignal/`; never `/private/tmp/kalon`.
No loosened, skipped or deleted tests, no swallowed errors, no sleeps for ordering.

## Report format
Under 40 lines: files, test names, RED then GREEN tails, acceptance tails, design disagreements,
verified versus inferred.

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
`briefs/cloud/p2-scoreboard-bench.md` carries the full text. Create
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
