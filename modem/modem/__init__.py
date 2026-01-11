"""
Core package for the audio modem toolkit.

The modules inside provide the following responsibilities:

- `config`: Shared constants such as tones, baud rates, and timing defaults.
- `framing`: Frame header packing, CRC helpers, and frame construction.
- `afsk`: Audio Frequency-Shift Keying primitives for synthesis and demodulation.
- `tx`: High-level transmission helpers (playback, WAV emission).
- `rx`: Receive pipeline with tone detection and frame parsing.
- `crypto`: Optional ChaCha20-Poly1305 helpers and key handling.
- `utils`: Utility helpers for bit/byte conversion and window shaping.
"""

from __future__ import annotations

__all__ = [
    "config",
    "framing",
    "afsk",
    "css",
    "tx",
    "rx",
    "crypto",
    "utils",
    "fec_conv",
]


