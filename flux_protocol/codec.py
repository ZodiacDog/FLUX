"""
Minimal binary codec for JSON-like values (dict, list, str, int, float,
bool, None, bytes) with per-message string deduplication and a CRC-32
trailer.

This is a compact encoding, not a network protocol and not a guarantee
of any particular size reduction versus JSON. Measure with
FluxClient.compare_sizes() on your own payloads.
"""

from __future__ import annotations

import struct
import zlib
from typing import Any, List

from .types import TypeTag

MAGIC = b"FLX1"
MAX_CONTAINER = 1_000_000


class FluxError(ValueError):
    """Codec error."""


def _write_varint(n: int) -> bytes:
    if n < 0:
        raise FluxError("varint must be non-negative")
    out = bytearray()
    while True:
        byte = n & 0x7F
        n >>= 7
        if n:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def _read_varint(data: bytes, i: int) -> tuple[int, int]:
    shift = 0
    n = 0
    while True:
        if i >= len(data):
            raise FluxError("truncated varint")
        byte = data[i]
        i += 1
        n |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            return n, i
        shift += 7
        if shift > 63:
            raise FluxError("varint too long")


class Encoder:
    def __init__(self) -> None:
        self._strings: dict[str, int] = {}
        self._out = bytearray()

    def encode_value(self, value: Any) -> None:
        if value is None:
            self._out.append(TypeTag.NULL)
        elif value is False:
            self._out.append(TypeTag.FALSE)
        elif value is True:
            self._out.append(TypeTag.TRUE)
        elif isinstance(value, bool):  # pragma: no cover - bool is subclass of int
            self._out.append(TypeTag.TRUE if value else TypeTag.FALSE)
        elif isinstance(value, int) and not isinstance(value, bool):
            self._out.append(TypeTag.INT)
            zigzag = (value << 1) if value >= 0 else ((-value) << 1) - 1
            self._out.extend(_write_varint(zigzag))
        elif isinstance(value, float):
            self._out.append(TypeTag.FLOAT)
            self._out.extend(struct.pack("<d", value))
        elif isinstance(value, str):
            self._write_string(value)
        elif isinstance(value, (bytes, bytearray)):
            self._out.append(TypeTag.BYTES)
            raw = bytes(value)
            self._out.extend(_write_varint(len(raw)))
            self._out.extend(raw)
        elif isinstance(value, (list, tuple)):
            if len(value) > MAX_CONTAINER:
                raise FluxError("list too large")
            self._out.append(TypeTag.LIST)
            self._out.extend(_write_varint(len(value)))
            for item in value:
                self.encode_value(item)
        elif isinstance(value, dict):
            if len(value) > MAX_CONTAINER:
                raise FluxError("dict too large")
            self._out.append(TypeTag.DICT)
            self._out.extend(_write_varint(len(value)))
            for key, item in value.items():
                if not isinstance(key, str):
                    raise FluxError("dict keys must be strings")
                self._write_string(key)
                self.encode_value(item)
        else:
            raise FluxError(f"unsupported type: {type(value).__name__}")

    def _write_string(self, s: str) -> None:
        existing = self._strings.get(s)
        if existing is not None:
            self._out.append(TypeTag.STRING_REF)
            self._out.extend(_write_varint(existing))
            return
        idx = len(self._strings)
        self._strings[s] = idx
        raw = s.encode("utf-8")
        self._out.append(TypeTag.STRING)
        self._out.extend(_write_varint(len(raw)))
        self._out.extend(raw)

    def finalize(self, message_type: int = 0) -> bytes:
        if not (0 <= int(message_type) <= 255):
            raise FluxError("message_type must fit in one byte")
        payload = bytes(self._out)
        crc = zlib.crc32(payload) & 0xFFFFFFFF
        return MAGIC + bytes([int(message_type)]) + _write_varint(len(payload)) + payload + struct.pack("<I", crc)


class Decoder:
    def __init__(self, blob: bytes) -> None:
        self.data = blob
        self.i = 0
        self._strings: List[str] = []

    def _need(self, n: int) -> bytes:
        if self.i + n > len(self.data):
            raise FluxError("truncated input")
        sl = self.data[self.i : self.i + n]
        self.i += n
        return sl

    def decode_message(self) -> Any:
        if self.data[:4] != MAGIC:
            raise FluxError("unrecognized FLUX magic")
        self.i = 4
        self.message_type = self._need(1)[0]
        length, self.i = _read_varint(self.data, self.i)
        payload = self._need(length)
        crc_bytes = self._need(4)
        (expected,) = struct.unpack("<I", crc_bytes)
        actual = zlib.crc32(payload) & 0xFFFFFFFF
        if actual != expected:
            raise FluxError("CRC-32 mismatch")
        if self.i != len(self.data):
            raise FluxError("trailing bytes after message")
        inner = Decoder(payload)
        inner.i = 0
        value = inner._decode_value()
        if inner.i != len(payload):
            raise FluxError("unconsumed payload bytes")
        return value

    def _decode_value(self) -> Any:
        tag = self._need(1)[0]
        if tag == TypeTag.NULL:
            return None
        if tag == TypeTag.FALSE:
            return False
        if tag == TypeTag.TRUE:
            return True
        if tag == TypeTag.INT:
            zigzag, self.i = _read_varint(self.data, self.i)
            if zigzag & 1:
                return -(zigzag // 2) - 1
            return zigzag >> 1
        if tag == TypeTag.FLOAT:
            (value,) = struct.unpack("<d", self._need(8))
            return value
        if tag == TypeTag.STRING:
            n, self.i = _read_varint(self.data, self.i)
            raw = self._need(n)
            s = raw.decode("utf-8")
            self._strings.append(s)
            return s
        if tag == TypeTag.STRING_REF:
            idx, self.i = _read_varint(self.data, self.i)
            if idx >= len(self._strings):
                raise FluxError("invalid string reference")
            return self._strings[idx]
        if tag == TypeTag.BYTES:
            n, self.i = _read_varint(self.data, self.i)
            return self._need(n)
        if tag == TypeTag.LIST:
            n, self.i = _read_varint(self.data, self.i)
            if n > MAX_CONTAINER:
                raise FluxError("list too large")
            return [self._decode_value() for _ in range(n)]
        if tag == TypeTag.DICT:
            n, self.i = _read_varint(self.data, self.i)
            if n > MAX_CONTAINER:
                raise FluxError("dict too large")
            out = {}
            for _ in range(n):
                key = self._decode_value()
                if not isinstance(key, str):
                    raise FluxError("dict key is not a string")
                out[key] = self._decode_value()
            return out
        raise FluxError(f"unknown type tag: {tag}")


def encode(value: Any, message_type: int = 0) -> bytes:
    enc = Encoder()
    enc.encode_value(value)
    return enc.finalize(message_type)


def decode(blob: bytes) -> Any:
    return Decoder(blob).decode_message()
