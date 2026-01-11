"""
Baseline CSS demodulator helpers.

This module currently assumes a single, well-aligned frame synthesized by
`modem.css`. Preamble detection and streaming integration will follow in later
milestones.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

import numpy as np

from . import config
from . import css
from . import framing


@dataclass(slots=True)
class SymbolDecision:
    """Represents a single CSS symbol demodulation decision."""

    shift: int
    magnitude: float
    dominance: float


@dataclass(slots=True)
class CSSFrameMetadata:
    """Placeholder metadata for decoded frames."""

    detected_sf: int
    detected_bw: float
    timestamp: float = 0.0
    rssi: float | None = None


def demod_symbol(
    samples: np.ndarray,
    *,
    templates: np.ndarray,
    template_energy: np.ndarray,
) -> SymbolDecision:
    """
    Demodulate a single symbol worth of samples and return the detected shift.
    """
    if samples.ndim != 1:
        raise ValueError("Symbol samples must be one-dimensional.")
    normalized = samples.astype(np.float32, copy=False)
    correlations = (templates @ normalized) / template_energy
    peak_index = int(np.argmax(correlations))
    peak_value = float(correlations[peak_index])
    if correlations.size > 1:
        second_peak = float(np.partition(correlations, -2)[-2])
    else:
        second_peak = peak_value
    dominance = peak_value / (second_peak + 1e-6)
    return SymbolDecision(shift=peak_index, magnitude=peak_value, dominance=dominance)


def _strip_tones(samples: np.ndarray) -> np.ndarray:
    """
    Remove optional start/end tones (heuristic for now).
    """
    tone_samples = int(round(config.START_END_TONE_DURATION_MS / 1000.0 * config.SAMPLE_RATE))
    if samples.size >= 2 * tone_samples:
        return samples[tone_samples:-tone_samples]
    return samples


def decode_css_waveform(
    samples: Iterable[float],
    params: css.ChirpParams,
    *,
    includes_preamble: bool = True,
    includes_sync: bool = True,
    includes_tones: bool = False,
) -> tuple[CSSFrameMetadata, framing.Header, bytes]:
    """
    Decode a CSS waveform into a frame.

    This assumes a single, complete frame synthesized by `modem.css`. It does
    not yet support repeated frames or streaming decode.
    """
    waveform = np.asarray(list(samples) if not isinstance(samples, np.ndarray) else samples)
    if waveform.ndim != 1:
        raise ValueError("CSS demodulator expects a mono waveform.")
    waveform = waveform.astype(np.float32, copy=False)

    if includes_tones:
        waveform = _strip_tones(waveform)

    symbol_stride = params.Ns
    skip_symbols = 0
    if includes_preamble:
        skip_symbols += params.preamble_up + params.preamble_down
    if includes_sync:
        skip_symbols += len(css.SYNC_PATTERN)
    offset_samples = skip_symbols * symbol_stride
    if waveform.size <= offset_samples:
        raise ValueError("Waveform is too short to contain data symbols.")
    data_region = waveform[offset_samples:]

    complete_symbols = data_region.size // symbol_stride
    if complete_symbols == 0:
        raise ValueError("No complete data symbols found in waveform.")

    reference = css.generate_reference_chirp(params)
    window = np.asarray(css._raised_cosine_window(params), dtype=np.float32)
    reference = css.generate_reference_chirp(params)
    templates = _build_symbol_templates(reference, window, params)
    template_energy = np.linalg.norm(templates, axis=1)
    template_energy[template_energy == 0.0] = 1.0

    decisions: list[SymbolDecision] = []
    bytes_out: list[int] = []

    for idx in range(complete_symbols):
        start = idx * symbol_stride
        segment = data_region[start : start + symbol_stride]
        if segment.size != symbol_stride:
            break
        decision = demod_symbol(segment, templates=templates, template_energy=template_energy)
        symbol = css.shift_to_symbol(decision.shift, params)
        decisions.append(decision)
        bytes_out.append(symbol)

    if len(bytes_out) < framing.Header.HEADER_LENGTH:
        raise ValueError("Insufficient bytes to recover frame header.")

    byte_stream = bytes(bytes_out)
    header = framing.Header.from_bytes(byte_stream[: framing.Header.HEADER_LENGTH])
    total_frame_bytes = framing.Header.HEADER_LENGTH + header.length + 2
    if len(byte_stream) < total_frame_bytes:
        raise ValueError("Decoded byte stream shorter than expected frame size.")

    frame_bytes = byte_stream[:total_frame_bytes]
    header, payload = framing.parse_frame(frame_bytes)

    energy = float(np.mean(data_region**2))
    metadata = CSSFrameMetadata(
        detected_sf=params.sf,
        detected_bw=params.bw,
        timestamp=0.0,
        rssi=10.0 * np.log10(energy + 1e-12),
    )
    return metadata, header, payload


def _build_symbol_templates(
    reference: np.ndarray, window: np.ndarray, params: css.ChirpParams
) -> np.ndarray:
    templates = np.empty((params.M, params.Ns), dtype=np.float32)
    for shift in range(params.M):
        sample_shift = int(round(shift * params.Ns / params.M))
        shifted = np.roll(reference, sample_shift)
        real_symbol = np.real(shifted).astype(np.float32, copy=False)
        templates[shift] = real_symbol * window
    return templates


