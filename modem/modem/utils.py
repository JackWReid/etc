"""
Utility helpers shared across modem modules.
"""

from __future__ import annotations

from typing import Iterable, Iterator, Sequence

import numpy as np


def bits_from_bytes(data: bytes) -> list[int]:
    """Expand a byte string to a list of bits (MSB first)."""
    bits: list[int] = []
    for byte in data:
        bits.extend(((byte >> shift) & 0x01) for shift in reversed(range(8)))
    return bits


def bytes_from_bits(bits: Sequence[int]) -> bytes:
    """Pack a sequence of bits into bytes (MSB first)."""
    if len(bits) % 8 != 0:
        raise ValueError("Number of bits must be a multiple of 8.")
    output = bytearray()
    for i in range(0, len(bits), 8):
        chunk = bits[i : i + 8]
        byte = 0
        for bit in chunk:
            byte = (byte << 1) | (bit & 0x01)
        output.append(byte)
    return bytes(output)


def chunks(iterable: Iterable[int], size: int) -> Iterator[list[int]]:
    """Yield lists of length `size` from `iterable`."""
    if size <= 0:
        raise ValueError("Chunk size must be positive.")
    chunk: list[int] = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) == size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def raised_cosine_window(length: int, *, ramp_fraction: float = 0.1) -> list[float]:
    """
    Generate a simple raised cosine window.
    """
    if length <= 0:
        raise ValueError("Window length must be positive.")
    if not 0.0 <= ramp_fraction < 0.5:
        raise ValueError("ramp_fraction must be in the range [0.0, 0.5).")

    ramp_samples = int(round(length * ramp_fraction))
    ramp_samples = min(ramp_samples, length // 2)

    if ramp_samples <= 0:
        return [1.0] * length

    window = np.ones(length, dtype=np.float64)
    ramp = 0.5 - 0.5 * np.cos(np.linspace(0.0, np.pi, ramp_samples, endpoint=False))
    window[:ramp_samples] = ramp
    window[-ramp_samples:] = ramp[::-1]
    return window.tolist()


