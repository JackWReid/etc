"""
Transmission helpers for the audio modem.

This module will eventually integrate with sounddevice for live playback and
wave file emission. The stubs below provide the intended surface area.
"""

from __future__ import annotations

from pathlib import Path
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

from . import afsk
from . import config
from . import framing
from . import utils
from .framing import Header

try:  # pragma: no cover - import guard for optional runtime dependency
    import sounddevice as sd
except ImportError:  # pragma: no cover - handled at call-time
    sd = None

ArrayLike = np.ndarray


def _sine_tone(
    frequency: float,
    duration_seconds: float,
    *,
    sample_rate: int,
    ramp_fraction: float = 0.02,
) -> ArrayLike:
    """Generate a single-frequency tone with optional raised-cosine ramps."""
    if duration_seconds <= 0:
        raise ValueError("duration_seconds must be positive.")
    num_samples = max(1, int(round(duration_seconds * sample_rate)))
    t = np.arange(num_samples, dtype=np.float64) / sample_rate
    tone = np.sin(2.0 * np.pi * frequency * t)
    if ramp_fraction > 0.0:
        window = np.asarray(
            utils.raised_cosine_window(num_samples, ramp_fraction=ramp_fraction),
            dtype=np.float64,
        )
        tone *= window
    return tone.astype(np.float32, copy=False)


def assemble_transmission(
    text: str,
    *,
    header: Header,
    repeats: int = 1,
) -> Iterable[float]:
    """
    Yield audio samples for the provided text payload.
    """
    if repeats <= 0:
        raise ValueError("repeats must be a positive integer.")

    payload = text.encode("utf-8")
    if header.length != len(payload):
        raise ValueError(
            f"Header length ({header.length}) does not match payload ({len(payload)})."
        )

    baud = config.baud_from_rate_code(header.rate_code)
    sample_rate = config.SAMPLE_RATE

    frame_bytes = framing.build_frame(header, payload)
    frame_bits: Sequence[int] = utils.bits_from_bytes(frame_bytes)

    preamble_symbol_count = max(1, int(round(0.2 * baud)))
    preamble_bits = [0, 1] * ((preamble_symbol_count + 1) // 2)
    preamble_bits = preamble_bits[:preamble_symbol_count]

    sync_bits = utils.bits_from_bytes(b"\xDD\xAA")
    bitstream = list(preamble_bits) + list(sync_bits) + list(frame_bits)

    data_waveform = afsk.generate_afsk_waveform(
        bitstream,
        baud=baud,
        sample_rate=sample_rate,
    )

    start_tone = _sine_tone(
        config.START_TONE_FREQUENCY,
        config.START_END_TONE_DURATION_MS / 1000.0,
        sample_rate=sample_rate,
    )
    end_tone = _sine_tone(
        config.END_TONE_FREQUENCY,
        config.START_END_TONE_DURATION_MS / 1000.0,
        sample_rate=sample_rate,
    )

    frame_waveform = np.concatenate((start_tone, data_waveform, end_tone), dtype=np.float32)

    if repeats > 1:
        frame_waveform = np.tile(frame_waveform, repeats)

    # Scale to a conservative output level to avoid clipping.
    return (0.8 * frame_waveform).astype(np.float32, copy=False)


def play_audio(samples: Iterable[float], *, device: str | None = None) -> None:
    """
    Play an iterable of audio samples using the default or provided audio device.
    """
    if sd is None:
        raise RuntimeError(
            "sounddevice is not installed. Install the 'sounddevice' dependency to enable playback."
        )

    waveform = np.asarray(list(samples) if not isinstance(samples, np.ndarray) else samples)
    if waveform.ndim != 1:
        raise ValueError("Audio samples must be a one-dimensional sequence.")

    sd.play(
        waveform.astype(np.float32, copy=False),
        samplerate=config.SAMPLE_RATE,
        device=device,
    )
    sd.wait()


def write_wav(samples: Iterable[float], destination: Path) -> None:
    """
    Write the given audio samples to a WAV file using the configured sample rate.
    """
    waveform = np.asarray(list(samples) if not isinstance(samples, np.ndarray) else samples)
    if waveform.ndim != 1:
        raise ValueError("Audio samples must be a one-dimensional sequence.")

    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    try:
        from scipy.io import wavfile
    except ImportError as exc:  # pragma: no cover - dependency should be available
        raise RuntimeError(
            "scipy is required to write WAV files. Install the 'scipy' dependency."
        ) from exc

    wavfile.write(destination, config.SAMPLE_RATE, waveform.astype(np.float32, copy=False))


