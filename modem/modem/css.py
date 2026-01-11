"""
Chirp Spread Spectrum transmitter helpers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Sequence

import numpy as np

from . import config
from . import framing
from . import utils
from .framing import Header

SYNC_PATTERN = (0x2D, 0xD4)


@dataclass(frozen=True, slots=True)
class ChirpParams:
    """CSS configuration parameters with derived fields."""

    sf: int
    bw: float
    fc: float
    fs: int = config.SAMPLE_RATE
    preamble_up: int = 10
    preamble_down: int = 2
    window_fraction: float = 0.025
    M: int = field(init=False)
    Tsym: float = field(init=False)
    Ns: int = field(init=False)
    f0: float = field(init=False)
    k: float = field(init=False)

    def __post_init__(self) -> None:
        if self.sf <= 0:
            raise ValueError("Spreading factor must be positive.")
        if self.bw <= 0.0:
            raise ValueError("Bandwidth must be positive.")
        if self.fs <= 0:
            raise ValueError("Sample rate must be positive.")
        if not 0.0 < self.window_fraction < 0.5:
            raise ValueError("window_fraction should be between 0 and 0.5.")
        object.__setattr__(self, "M", 1 << self.sf)
        tsym = (self.M) / self.bw
        object.__setattr__(self, "Tsym", tsym)
        samples = int(round(self.fs * tsym))
        object.__setattr__(self, "Ns", samples)
        f0 = self.fc - self.bw / 2.0
        object.__setattr__(self, "f0", f0)
        k = self.bw / tsym
        object.__setattr__(self, "k", k)


def generate_reference_chirp(params: ChirpParams) -> np.ndarray:
    """
    Return the complex baseband up-chirp for the provided parameters.
    """
    t = np.arange(params.Ns, dtype=np.float64) / params.fs
    phase = 2.0 * np.pi * (params.f0 * t + 0.5 * params.k * t * t)
    chirp = np.exp(1j * phase)
    return chirp.astype(np.complex64, copy=False)


def _raised_cosine_window(params: ChirpParams) -> np.ndarray:
    window = utils.raised_cosine_window(params.Ns, ramp_fraction=params.window_fraction)
    return np.asarray(window, dtype=np.float32)


def _gray_encode(value: int) -> int:
    return value ^ (value >> 1)


def _gray_decode(gray: int) -> int:
    result = 0
    while gray:
        result ^= gray
        gray >>= 1
    return result


def symbol_to_shift(symbol: int, params: ChirpParams) -> int:
    """
    Map an 8-bit symbol to a chirp cyclic shift.
    """
    if not 0 <= symbol < 256:
        raise ValueError("symbol must be an 8-bit value.")
    index = _gray_encode(symbol)
    if index >= params.M:
        raise ValueError(f"Symbol mapping exceeds available shifts (M={params.M}).")
    return index


def shift_to_symbol(index: int, params: ChirpParams) -> int:
    """
    Inverse of `symbol_to_shift`.
    """
    if not 0 <= index < params.M:
        raise ValueError("shift index out of range.")
    return _gray_decode(index)


def _synthesize_symbol_waveform(
    shift_index: int, reference: np.ndarray, window: np.ndarray, params: ChirpParams
) -> np.ndarray:
    samples_shift = int(round(shift_index * params.Ns / params.M))
    shifted = np.roll(reference, samples_shift) * window
    return np.real(shifted).astype(np.float32, copy=False)


def _generate_down_chirp(reference: np.ndarray, window: np.ndarray) -> np.ndarray:
    down = np.conj(reference) * window
    return np.real(down).astype(np.float32, copy=False)


def synthesize_symbols(
    symbols: Sequence[int],
    params: ChirpParams,
    *,
    include_preamble: bool = True,
    include_sync: bool = True,
    include_tones: bool = False,
) -> np.ndarray:
    """
    Convert a sequence of byte values into a CSS waveform.
    """
    reference = generate_reference_chirp(params)
    window = _raised_cosine_window(params)

    waveform_parts: list[np.ndarray] = []

    if include_tones:
        waveform_parts.append(
            _sine_tone(config.START_TONE_FREQUENCY, config.START_END_TONE_DURATION_MS / 1000.0)
        )

    if include_preamble:
        up_symbol = _synthesize_symbol_waveform(0, reference, window, params)
        down_symbol = _generate_down_chirp(reference, window)
        for _ in range(params.preamble_up):
            waveform_parts.append(up_symbol)
        for _ in range(params.preamble_down):
            waveform_parts.append(down_symbol)

    if include_sync:
        for pattern in SYNC_PATTERN:
            shift = symbol_to_shift(pattern, params)
            waveform_parts.append(_synthesize_symbol_waveform(shift, reference, window, params))

    for symbol in symbols:
        shift = symbol_to_shift(symbol, params)
        waveform_parts.append(_synthesize_symbol_waveform(shift, reference, window, params))

    if include_tones:
        waveform_parts.append(
            _sine_tone(config.END_TONE_FREQUENCY, config.START_END_TONE_DURATION_MS / 1000.0)
        )

    if not waveform_parts:
        return np.asarray([], dtype=np.float32)

    waveform = np.concatenate(waveform_parts).astype(np.float32, copy=False)
    peak = np.max(np.abs(waveform)) or 1.0
    return 0.8 * waveform / peak


def _sine_tone(frequency: float, duration_seconds: float) -> np.ndarray:
    if duration_seconds <= 0.0:
        raise ValueError("duration_seconds must be positive.")
    num_samples = int(round(duration_seconds * config.SAMPLE_RATE))
    t = np.arange(num_samples, dtype=np.float64) / config.SAMPLE_RATE
    tone = np.sin(2.0 * np.pi * frequency * t)
    window = np.asarray(utils.raised_cosine_window(num_samples, ramp_fraction=0.02), dtype=np.float64)
    return (tone * window).astype(np.float32, copy=False)


def assemble_css_transmission(
    text: str,
    *,
    header: Header,
    params: ChirpParams,
    repeats: int = 1,
    fec_enabled: bool = False,
    interleave_depth: int = 1,
    include_tones: bool = False,
) -> Iterable[float]:
    """
    High-level assembly for CSS transmission audio samples.
    """
    if repeats <= 0:
        raise ValueError("repeats must be a positive integer.")
    if interleave_depth < 1:
        raise ValueError("interleave_depth must be >= 1.")

    payload = text.encode("utf-8")
    base_header = framing.Header(
        version=header.version,
        rate_code=header.rate_code,
        flags=_update_flags(header.flags, fec_enabled),
        length=header.length,
    )

    if base_header.length != len(payload):
        raise ValueError(
            f"Header length ({base_header.length}) does not match payload ({len(payload)})."
        )

    frame_bytes = framing.build_frame(base_header, payload)
    frame_bits = utils.bits_from_bytes(frame_bytes)

    if fec_enabled:
        raise NotImplementedError("FEC support will arrive in a later milestone.")

    symbols = list(frame_bytes)
    waveform = synthesize_symbols(
        symbols,
        params,
        include_preamble=True,
        include_sync=True,
        include_tones=include_tones,
    )

    if repeats > 1:
        waveform = np.tile(waveform, repeats)

    return waveform.astype(np.float32, copy=False)


def _update_flags(original_flags: int, fec_enabled: bool) -> int:
    if fec_enabled:
        return original_flags | config.CSS_FLAG_FEC
    return original_flags & ~config.CSS_FLAG_FEC


