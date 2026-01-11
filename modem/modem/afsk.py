"""
Audio Frequency-Shift Keying primitives.

This module will eventually host waveform synthesis and demodulation routines.
For now, we expose type-annotated stubs so the rest of the code can depend on
stable signatures.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Iterable, Sequence

import numpy as np

from . import config
from . import utils

ArrayLike = np.ndarray


def generate_afsk_waveform(
    bits: Sequence[int],
    *,
    baud: int,
    sample_rate: int | None = None,
    ramp_fraction: float = 0.05,
) -> ArrayLike:
    """
    Convert a sequence of bits into an audio waveform array at the given sample rate.

    Args:
        bits: The bits to transmit (MSB first).
        baud: Symbol rate of the transmission.
        sample_rate: Optional override for the sample rate. Defaults to `config.SAMPLE_RATE`.
        ramp_fraction: Fraction of each symbol period used for raised cosine ramps.
    """
    sample_rate = sample_rate or config.SAMPLE_RATE
    if sample_rate <= 0:
        raise ValueError("sample_rate must be positive.")
    if baud <= 0:
        raise ValueError("baud must be positive.")
    if sample_rate % baud != 0:
        raise ValueError("sample_rate must be an integer multiple of the baud rate.")

    bits = list(bits)
    if not bits:
        return np.zeros(0, dtype=np.float32)

    samples_per_symbol = sample_rate // baud
    window = np.asarray(utils.raised_cosine_window(samples_per_symbol, ramp_fraction=ramp_fraction))

    phase = 0.0
    waveform_segments: list[np.ndarray] = []

    for bit in bits:
        frequency = config.MARK_FREQUENCY if bit else config.SPACE_FREQUENCY
        phase_increments = 2.0 * np.pi * frequency / sample_rate
        t = np.arange(samples_per_symbol, dtype=np.float64)
        segment_phase = phase + phase_increments * t
        segment = np.sin(segment_phase) * window
        phase = (segment_phase[-1] + phase_increments) % (2.0 * np.pi)
        waveform_segments.append(segment)

    waveform = np.concatenate(waveform_segments, dtype=np.float64)
    return waveform.astype(np.float32, copy=False)


def goertzel_power(window: Iterable[float], frequency: float, *, sample_rate: int | None = None) -> float:
    """
    Compute the Goertzel power for a single target frequency window.
    """
    sample_rate = sample_rate or config.SAMPLE_RATE
    if sample_rate <= 0:
        raise ValueError("sample_rate must be positive.")
    if frequency <= 0:
        raise ValueError("frequency must be positive.")

    data = np.asarray(list(window) if not isinstance(window, np.ndarray) else window, dtype=np.float64)
    if data.size == 0:
        raise ValueError("window must contain at least one sample.")

    n = data.size
    k = int(round((n * frequency) / sample_rate))
    if k <= 0:
        k = 1
    w = (2.0 * np.pi * k) / n
    coeff = 2.0 * np.cos(w)
    s0 = 0.0
    s1 = 0.0
    s2 = 0.0
    for sample in data:
        s0 = sample + coeff * s1 - s2
        s2 = s1
        s1 = s0
    power = s1 * s1 + s2 * s2 - coeff * s1 * s2
    return float(max(power, 0.0))


@lru_cache(maxsize=32)
def _reference_waveforms(samples_per_symbol: int, frequency: float) -> tuple[np.ndarray, np.ndarray]:
    """
    Return cached cosine and sine reference tables for the provided frequency.
    """
    t = np.arange(samples_per_symbol, dtype=np.float64) / config.SAMPLE_RATE
    phase = 2.0 * np.pi * frequency * t
    cos_table = np.cos(phase)
    sin_table = np.sin(phase)
    return cos_table, sin_table


def demodulate_afsk(samples: ArrayLike, *, baud: int) -> list[int]:
    """
    Demodulate an AFSK waveform into bits given the nominal baud rate.
    """
    if baud <= 0:
        raise ValueError("baud must be positive.")
    sample_rate = config.SAMPLE_RATE
    if sample_rate % baud != 0:
        raise ValueError("SAMPLE_RATE must be an integer multiple of baud.")

    waveform = np.asarray(samples, dtype=np.float64)
    if waveform.ndim != 1:
        raise ValueError("samples must be a one-dimensional array or sequence.")

    samples_per_symbol = sample_rate // baud
    total_symbols = waveform.size // samples_per_symbol
    if total_symbols == 0:
        return []

    trimmed = waveform[: total_symbols * samples_per_symbol]
    symbols = trimmed.reshape(total_symbols, samples_per_symbol)

    mark_cos, mark_sin = _reference_waveforms(samples_per_symbol, config.MARK_FREQUENCY)
    space_cos, space_sin = _reference_waveforms(samples_per_symbol, config.SPACE_FREQUENCY)

    mark_i = symbols @ mark_cos
    mark_q = symbols @ mark_sin
    mark_power = mark_i * mark_i + mark_q * mark_q

    space_i = symbols @ space_cos
    space_q = symbols @ space_sin
    space_power = space_i * space_i + space_q * space_q

    return [1 if m >= s else 0 for m, s in zip(mark_power, space_power)]


