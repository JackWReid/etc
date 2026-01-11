"""
Unit tests for the transmit helpers.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from scipy.io import wavfile

from modem import config
from modem.framing import Header
from modem.tx import assemble_transmission, write_wav


def _expected_frame_lengths(baud: int, payload_len: int) -> tuple[int, int, int]:
    """Return (start_len, data_len, end_len) in samples."""
    samples_per_symbol = config.SAMPLE_RATE // baud
    preamble_symbol_count = max(1, int(round(0.2 * baud)))
    frame_bytes = 5 + payload_len + 2  # header + payload + CRC
    total_bits = preamble_symbol_count + 16 + frame_bytes * 8
    data_len = total_bits * samples_per_symbol
    tone_len = int(round(config.START_END_TONE_DURATION_MS / 1000 * config.SAMPLE_RATE))
    return tone_len, data_len, tone_len


def test_assemble_transmission_waveform_layout() -> None:
    message = "Hi"
    baud = 200
    header = Header(
        version=config.DEFAULT_VERSION,
        rate_code=config.BAUD_TO_RATE_CODE[baud],
        flags=config.DEFAULT_FLAGS,
        length=len(message.encode("utf-8")),
    )

    waveform = assemble_transmission(message, header=header, repeats=2)
    assert isinstance(waveform, np.ndarray)
    assert waveform.dtype == np.float32

    start_len, data_len, end_len = _expected_frame_lengths(baud, header.length)
    expected_single_len = start_len + data_len + end_len
    assert waveform.shape == (expected_single_len * 2,)

    start_segment = waveform[:start_len]
    data_segment = waveform[start_len : start_len + data_len]
    end_segment = waveform[start_len + data_len : expected_single_len]

    max_amplitude = float(np.max(np.abs(waveform)))
    assert max_amplitude <= 0.8 + 1e-3
    assert abs(float(np.mean(start_segment[:200]))) <= 0.02
    assert not np.allclose(data_segment, 0.0)
    assert abs(float(np.mean(end_segment[-200:]))) <= 0.02


def test_assemble_transmission_rejects_length_mismatch() -> None:
    baud = 200
    header = Header(
        version=config.DEFAULT_VERSION,
        rate_code=config.BAUD_TO_RATE_CODE[baud],
        flags=config.DEFAULT_FLAGS,
        length=5,  # Incorrect on purpose
    )

    with pytest.raises(ValueError):
        assemble_transmission("abc", header=header)


def test_assemble_transmission_requires_positive_repeats() -> None:
    baud = 200
    header = Header(
        version=config.DEFAULT_VERSION,
        rate_code=config.BAUD_TO_RATE_CODE[baud],
        flags=config.DEFAULT_FLAGS,
        length=0,
    )

    with pytest.raises(ValueError):
        assemble_transmission("", header=header, repeats=0)


def test_write_wav_round_trip(tmp_path: Path) -> None:
    message = "Test"
    baud = 100
    header = Header(
        version=config.DEFAULT_VERSION,
        rate_code=config.BAUD_TO_RATE_CODE[baud],
        flags=config.DEFAULT_FLAGS,
        length=len(message.encode("utf-8")),
    )

    waveform = assemble_transmission(message, header=header)
    destination = tmp_path / "transmission.wav"
    write_wav(waveform, destination)

    assert destination.exists()

    sample_rate, decoded = wavfile.read(destination)

    assert sample_rate == config.SAMPLE_RATE
    assert decoded.ndim == 1
    assert decoded.shape == waveform.shape
    assert decoded.dtype == np.float32
    np.testing.assert_allclose(decoded, waveform, rtol=1e-6, atol=1e-6)

