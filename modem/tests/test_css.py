from __future__ import annotations

import numpy as np

from modem import config, css, css_rx, framing


def _default_params() -> css.ChirpParams:
    return css.ChirpParams(
        sf=config.CSS_DEFAULT_SF,
        bw=config.CSS_DEFAULT_BW,
        fc=config.CSS_DEFAULT_CENTER,
        preamble_up=config.CSS_DEFAULT_PREAMBLE_UP,
        preamble_down=config.CSS_DEFAULT_PREAMBLE_DOWN,
    )


def test_chirp_params_derived_values() -> None:
    params = _default_params()
    assert params.M == (1 << config.CSS_DEFAULT_SF)
    assert params.Ns > 0
    expected_tsym = params.M / params.bw
    assert np.isclose(params.Tsym, expected_tsym)
    assert params.f0 == params.fc - params.bw / 2.0


def test_gray_mapping_roundtrip() -> None:
    params = _default_params()
    for value in range(256):
        shift = css.symbol_to_shift(value, params)
        decoded = css.shift_to_symbol(shift, params)
        assert decoded == value


def test_synthesize_symbols_shape_and_scale() -> None:
    params = _default_params()
    waveform = css.synthesize_symbols(
        [0xAA, 0x55], params, include_preamble=False, include_sync=False, include_tones=False
    )
    assert waveform.dtype == np.float32
    assert waveform.size == 2 * params.Ns
    assert np.max(np.abs(waveform)) <= 0.8 + 1e-6


def test_css_loopback_basic() -> None:
    params = _default_params()
    message = "CSS test"
    payload = message.encode("utf-8")
    header = framing.Header(version=config.DEFAULT_VERSION, rate_code=0, flags=0, length=len(payload))

    waveform = css.assemble_css_transmission(
        message,
        header=header,
        params=params,
        repeats=1,
        fec_enabled=False,
        interleave_depth=1,
        include_tones=False,
    )

    metadata, decoded_header, decoded_payload = css_rx.decode_css_waveform(
        waveform,
        params,
        includes_preamble=True,
        includes_sync=True,
        includes_tones=False,
    )

    assert decoded_header.length == len(payload)
    assert decoded_payload == payload
    assert metadata.detected_sf == params.sf


def test_css_loopback_awgn() -> None:
    rng = np.random.default_rng(1234)
    params = _default_params()
    message = "Robustness"
    payload = message.encode("utf-8")
    header = framing.Header(version=config.DEFAULT_VERSION, rate_code=0, flags=0, length=len(payload))

    clean_waveform = css.assemble_css_transmission(
        message,
        header=header,
        params=params,
        repeats=1,
        fec_enabled=False,
        interleave_depth=1,
        include_tones=False,
    )

    signal_power = np.mean(clean_waveform**2)
    snr_db = 20.0
    noise_power = signal_power / (10 ** (snr_db / 10.0))
    noise = rng.normal(0.0, np.sqrt(noise_power), size=clean_waveform.shape).astype(np.float32)
    noisy_waveform = clean_waveform + noise

    _, _, decoded_payload = css_rx.decode_css_waveform(
        noisy_waveform,
        params,
        includes_preamble=True,
        includes_sync=True,
        includes_tones=False,
    )
    assert decoded_payload == payload


