"""
Tests for the receive-side helpers.
"""

from __future__ import annotations

import numpy as np

from modem import config
from modem.framing import Header
from modem.rx import decode_stream, detect_start_tone
from modem.tx import assemble_transmission


def _make_tone(frequency: float, duration_ms: float) -> np.ndarray:
    sample_rate = config.SAMPLE_RATE
    samples = int(round(duration_ms / 1000.0 * sample_rate))
    t = np.arange(samples, dtype=np.float64) / sample_rate
    window = np.sin(2.0 * np.pi * frequency * t) * 0.8
    return window.astype(np.float32)


def test_detect_start_tone_positive() -> None:
    tone = _make_tone(config.START_TONE_FREQUENCY, config.START_END_TONE_DURATION_MS)
    assert detect_start_tone(tone)


def test_detect_start_tone_negative() -> None:
    noise = np.random.default_rng(123).normal(0.0, 0.01, size=4800).astype(np.float32)
    assert not detect_start_tone(noise)


def test_decode_stream_single_frame() -> None:
    message = "Loopback!"
    baud = 200
    payload = message.encode("utf-8")
    header = Header(
        version=config.DEFAULT_VERSION,
        rate_code=config.BAUD_TO_RATE_CODE[baud],
        flags=config.DEFAULT_FLAGS,
        length=len(payload),
    )

    waveform = assemble_transmission(message, header=header, repeats=1)
    results = list(decode_stream(waveform))
    assert len(results) == 1

    metadata, parsed_header, received_payload = results[0]
    assert metadata.detected_baud == baud
    assert parsed_header == header
    assert received_payload == payload


def test_decode_stream_requires_start_tone() -> None:
    baud = 200
    payload = b"no start tone"
    header = Header(
        version=config.DEFAULT_VERSION,
        rate_code=config.BAUD_TO_RATE_CODE[baud],
        flags=config.DEFAULT_FLAGS,
        length=len(payload),
    )
    waveform = assemble_transmission(payload.decode("utf-8"), header=header, repeats=1)
    # Strip the start tone portion to simulate truncated capture.
    tone_samples = int(round(config.START_END_TONE_DURATION_MS / 1000.0 * config.SAMPLE_RATE))
    truncated = waveform[tone_samples:]

    assert list(decode_stream(truncated)) == []

