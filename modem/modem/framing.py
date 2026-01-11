"""
Frame construction, parsing, and CRC helpers.

The concrete implementations will follow the specification in `PLAN.md`,
but for now we provide type-safe stubs to guide future development.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

FramePayload = bytes

CRC_POLY = 0x1021
CRC_INIT = 0xFFFF


@dataclass(slots=True)
class Header:
    """Represents the five-byte modem header."""

    version: int
    rate_code: int
    flags: int
    length: int

    HEADER_LENGTH: ClassVar[int] = 5

    def to_bytes(self) -> bytes:
        """Serialize the header to bytes."""
        return bytes(
            (
                self.version & 0xFF,
                self.rate_code & 0xFF,
                self.flags & 0xFF,
                (self.length >> 8) & 0xFF,
                self.length & 0xFF,
            )
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "Header":
        """Parse header bytes into an instance."""
        if len(data) != cls.HEADER_LENGTH:
            raise ValueError(f"Header must be {cls.HEADER_LENGTH} bytes, got {len(data)}")
        version, rate_code, flags, high_len, low_len = data
        length = (high_len << 8) | low_len
        return cls(version=version, rate_code=rate_code, flags=flags, length=length)


def crc16_ccitt(data: bytes, initial: int = 0xFFFF) -> int:
    """
    Calculate the CRC-16-CCITT checksum for the provided payload.

    Implements the polynomial 0x1021 with refin/refout disabled.
    """
    crc = initial & 0xFFFF
    for byte in data:
        crc ^= (byte & 0xFF) << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) & 0xFFFF) ^ CRC_POLY
            else:
                crc = (crc << 1) & 0xFFFF
    return crc & 0xFFFF


def build_frame(header: Header, payload: FramePayload) -> bytes:
    """
    Construct a full frame `[header || payload || crc]`.

    The audio waveform wrapping (start tone, preamble, etc.) is handled
    elsewhere. This function will provide the raw binary structure.
    """
    if header.length != len(payload):
        raise ValueError(
            f"Header length ({header.length}) does not match payload ({len(payload)})"
        )
    frame_core = header.to_bytes() + payload
    crc = crc16_ccitt(frame_core)
    crc_bytes = bytes(((crc >> 8) & 0xFF, crc & 0xFF))
    return frame_core + crc_bytes


def parse_frame(frame_bytes: bytes) -> tuple[Header, FramePayload]:
    """
    Parse a frame into its header and payload components.
    """
    if len(frame_bytes) < Header.HEADER_LENGTH + 2:
        raise ValueError("Frame is too short to contain header and CRC.")

    header = Header.from_bytes(frame_bytes[: Header.HEADER_LENGTH])
    payload = frame_bytes[Header.HEADER_LENGTH : -2]
    crc_rx = (frame_bytes[-2] << 8) | frame_bytes[-1]

    if header.length != len(payload):
        raise ValueError(
            f"Header declared payload length {header.length} but frame contains {len(payload)} bytes."
        )

    crc_computed = crc16_ccitt(frame_bytes[: -2])
    if crc_computed != crc_rx:
        raise ValueError(
            f"CRC mismatch: calculated 0x{crc_computed:04X} but frame carried 0x{crc_rx:04X}."
        )

    return header, payload



