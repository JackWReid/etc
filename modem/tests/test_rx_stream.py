"""
Tests for stream decoding of received audio frames.
"""

from __future__ import annotations

import numpy as np

from modem import config
from modem.framing import Header
from modem.rx import (
    IncrementalFrameDecoder,
    decode_stream,
    stream_frames_from_chunks,
)
from modem.tx import assemble_transmission


def _make_header(message: str, *, baud: int) -> Header:
    payload_len = len(message.encode("utf-8"))
    return Header(
        version=config.DEFAULT_VERSION,
        rate_code=config.BAUD_TO_RATE_CODE[baud],
        flags=config.DEFAULT_FLAGS,
        length=payload_len,
    )


def test_decode_stream_handles_repeated_frames() -> None:
    message = "Stream test payload"
    baud = 200
    header = _make_header(message, baud=baud)

    waveform = np.asarray(assemble_transmission(message, header=header, repeats=3), dtype=np.float32)
    decoded = list(decode_stream(waveform))

    assert len(decoded) == 3
    for metadata, parsed_header, payload in decoded:
        assert parsed_header == header
        assert payload == message.encode("utf-8")
        assert metadata.detected_baud == baud


def test_decode_stream_with_leading_noise() -> None:
    message = "Noise guard"
    baud = 100
    header = _make_header(message, baud=baud)

    waveform = np.asarray(assemble_transmission(message, header=header, repeats=1), dtype=np.float32)
    rng = np.random.default_rng(7)
    noise = 0.02 * rng.normal(size=int(0.15 * config.SAMPLE_RATE))
    padded_waveform = np.concatenate((noise.astype(np.float32), waveform))

    decoded = list(decode_stream(padded_waveform))

    assert len(decoded) == 1
    metadata, parsed_header, payload = decoded[0]
    assert parsed_header == header
    assert payload == message.encode("utf-8")
    assert metadata.detected_baud == baud


def test_incremental_decoder_handles_split_frame() -> None:
    message = "Incremental payload"
    baud = 200
    header = _make_header(message, baud=baud)

    waveform = np.asarray(assemble_transmission(message, header=header, repeats=1), dtype=np.float32)
    halfway = waveform.size // 2

    decoder = IncrementalFrameDecoder()
    first_half = waveform[:halfway]
    second_half = waveform[halfway:]

    assert list(decoder.ingest(first_half)) == []

    decoded = list(decoder.ingest(second_half))
    assert len(decoded) == 1
    metadata, parsed_header, payload = decoded[0]
    assert parsed_header == header
    assert payload == message.encode("utf-8")
    assert metadata.detected_baud == baud


def test_stream_frames_from_chunks_handles_multiple_frames() -> None:
    message = "Chunked stream"
    repeats = 2
    baud = 100
    header = _make_header(message, baud=baud)
    waveform = np.asarray(
        assemble_transmission(message, header=header, repeats=repeats),
        dtype=np.float32,
    )

    chunks = np.array_split(waveform, repeats * 4)
    decoded = list(stream_frames_from_chunks(chunks))

    assert len(decoded) == repeats
    for metadata, parsed_header, payload in decoded:
        assert parsed_header == header
        assert payload == message.encode("utf-8")
        assert metadata.detected_baud == baud


def test_stream_frames_from_chunks_handles_low_baud_length() -> None:
    message = "Slow channel payload with a reasonable length"
    baud = min(config.BAUD_RATES)
    header = _make_header(message, baud=baud)
    waveform = np.asarray(
        assemble_transmission(message, header=header, repeats=1),
        dtype=np.float32,
    )

    chunks = np.array_split(waveform, 40)
    decoded = list(stream_frames_from_chunks(chunks))

    assert len(decoded) == 1
    metadata, parsed_header, payload = decoded[0]
    assert parsed_header == header
    assert payload == message.encode("utf-8")
    assert metadata.detected_baud == baud

