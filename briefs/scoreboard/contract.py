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
