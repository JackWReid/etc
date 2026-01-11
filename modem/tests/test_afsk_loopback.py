"""
Loopback and spectral tests for the AFSK modem primitives.
"""

from __future__ import annotations

import numpy as np
import pytest

from modem import config
from modem import utils
from modem.afsk import demodulate_afsk, generate_afsk_waveform, goertzel_power


def test_goertzel_power_detects_mark_frequency() -> None:
    sample_rate = config.SAMPLE_RATE
    duration = 0.02  # 20 ms
    num_samples = int(duration * sample_rate)
    t = np.arange(num_samples, dtype=np.float64) / sample_rate
    window = np.sin(2.0 * np.pi * config.MARK_FREQUENCY * t)

    mark_power = goertzel_power(window, config.MARK_FREQUENCY, sample_rate=sample_rate)
    space_power = goertzel_power(window, config.SPACE_FREQUENCY, sample_rate=sample_rate)

    assert mark_power > space_power * 20


@pytest.mark.parametrize("baud", [50, 100, 200])
def test_afsk_round_trip(baud: int) -> None:
    payload = b"Test frame!"
    bits = utils.bits_from_bytes(payload)

    waveform = generate_afsk_waveform(bits, baud=baud, sample_rate=config.SAMPLE_RATE)
    # Ensure we can add small noise without breaking detection.
    noisy_waveform = waveform.astype(np.float64) + 0.01 * np.random.default_rng(42).normal(
        size=waveform.shape
    )

    demod_bits = demodulate_afsk(noisy_waveform, baud=baud)
    assert demod_bits == bits
