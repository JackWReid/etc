"""
Receiving pipeline for the audio modem.

This module will host tone detection, symbol timing, and frame parsing logic.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from logging import getLogger
from time import time

import numpy as np

from . import config
from . import framing
from . import utils
from .afsk import demodulate_afsk, goertzel_power
from .framing import Header

try:  # pragma: no cover - optional dependency for runtime audio capture
    import sounddevice as sd
except ImportError:  # pragma: no cover - handled at call-time
    sd = None

logger = getLogger(__name__)


@dataclass(slots=True)
class FrameMetadata:
    """Metadata associated with a received frame."""

    timestamp: float
    detected_baud: int
    rssi: float | None = None


def _detect_tone(
    samples: np.ndarray,
    *,
    frequency: float,
    comparison_frequencies: tuple[float, ...],
    energy_ratio_threshold: float = 0.1,
    dominance_threshold: float = 8.0,
) -> bool:
    if samples.ndim != 1:
        raise ValueError("samples must be a one-dimensional array.")
    if samples.size == 0:
        return False

    tone_power = goertzel_power(samples, frequency, sample_rate=config.SAMPLE_RATE)
    comparison_powers = [
        goertzel_power(samples, other_freq, sample_rate=config.SAMPLE_RATE)
        for other_freq in comparison_frequencies
    ]
    total_power = float(np.dot(samples, samples))
    if total_power <= 0.0 or tone_power <= 0.0:
        return False
    dominance = tone_power / max(max(comparison_powers, default=0.0), 1e-12)
    energy_ratio = tone_power / total_power
    return dominance > dominance_threshold and energy_ratio > energy_ratio_threshold


def detect_start_tone(samples: np.ndarray) -> bool:
    """
    Detect whether the start tone is present in the provided samples.
    """
    return _detect_tone(
        samples,
        frequency=config.START_TONE_FREQUENCY,
        comparison_frequencies=(
            config.END_TONE_FREQUENCY,
            config.MARK_FREQUENCY,
            config.SPACE_FREQUENCY,
        ),
    )


def detect_end_tone(samples: np.ndarray) -> bool:
    """
    Detect whether the end tone is present in the provided samples.
    """
    return _detect_tone(
        samples,
        frequency=config.END_TONE_FREQUENCY,
        comparison_frequencies=(
            config.START_TONE_FREQUENCY,
            config.MARK_FREQUENCY,
            config.SPACE_FREQUENCY,
        ),
    )


def decode_stream(
    samples: Iterable[float],
) -> Iterator[tuple[FrameMetadata, Header, bytes]]:
    """
    Stream decoder that yields frames as they are detected.
    """
    decoder = IncrementalFrameDecoder()
    yield from decoder.ingest(samples)


def read_from_microphone(*, device: str | None = None) -> Iterator[np.ndarray]:
    """
    Capture audio chunks from an input device.
    """
    if sd is None:
        raise RuntimeError(
            "sounddevice is not installed. Install the 'sounddevice' dependency to enable capture."
        )

    sample_rate = config.SAMPLE_RATE
    blocksize = max(1, int(round(0.1 * sample_rate)))  # 100 ms blocks by default

    stream = sd.InputStream(
        samplerate=sample_rate,
        channels=1,
        dtype="float32",
        device=device,
        blocksize=blocksize,
    )

    try:
        with stream:
            last_status_str: str | None = None
            last_log_time: float = 0.0
            while True:
                data, status = stream.read(blocksize)
                if status:
                    # Throttle and de-duplicate status logs to avoid spam.
                    s = str(status)
                    now = time()
                    if s != last_status_str or (now - last_log_time) > 5.0:
                        logger.warning("Microphone stream status: %s", s)
                        last_status_str = s
                        last_log_time = now
                if data.size == 0:
                    continue
                chunk = np.squeeze(np.asarray(data, dtype=np.float32), axis=-1)
                yield chunk.copy()
    finally:  # pragma: no cover - defensive cleanup
        stream.close()


def _find_sync(bits: list[int], pattern: list[int]) -> int:
    """Return the index of the first occurrence of pattern in bits, or -1."""
    plen = len(pattern)
    limit = len(bits) - plen + 1
    for idx in range(max(0, limit)):
        if bits[idx : idx + plen] == pattern:
            return idx
    return -1


def _find_tone_window(
    waveform: np.ndarray,
    detector: Callable[[np.ndarray], bool],
    *,
    window_size: int,
    start_index: int,
    step_size: int | None = None,
    refine_forward: bool = False,
) -> int:
    """Return the index where the detector finds a tone window, or -1 if absent."""
    if window_size <= 0:
        raise ValueError("window_size must be positive.")
    step = step_size or max(1, window_size // 10)
    start = max(0, start_index)
    limit = waveform.size - window_size
    if limit < start:
        return -1
    for idx in range(start, limit + 1, step):
        segment = waveform[idx : idx + window_size]
        if detector(segment):
            if not refine_forward:
                return idx
            return _refine_tone_window_forward(
                waveform,
                detector,
                initial_index=idx,
                window_size=window_size,
                limit=limit,
                base_step=step,
            )
    return -1


def _refine_tone_window_forward(
    waveform: np.ndarray,
    detector: Callable[[np.ndarray], bool],
    *,
    initial_index: int,
    window_size: int,
    limit: int,
    base_step: int,
) -> int:
    """Refine a detected tone window forward to the last contiguous detection."""
    refine_step = max(1, base_step // 4)
    idx = initial_index
    last_idx = idx
    # Coarse refinement
    while True:
        next_idx = idx + refine_step
        if next_idx > limit:
            break
        segment = waveform[next_idx : next_idx + window_size]
        if not detector(segment):
            break
        last_idx = next_idx
        idx = next_idx
    # Fine refinement (step of 1) to capture trailing edge precisely.
    fine_limit = min(last_idx + refine_step, limit)
    for next_idx in range(last_idx + 1, fine_limit + 1):
        segment = waveform[next_idx : next_idx + window_size]
        if not detector(segment):
            break
        last_idx = next_idx
    return last_idx


def _estimate_rssi(start_segment: np.ndarray, end_segment: np.ndarray) -> float:
    """Crude RSSI estimate based on average magnitude of start tone region."""
    del end_segment  # Placeholder for future refinement.
    rms = float(np.sqrt(np.mean(np.square(start_segment)))) if start_segment.size else 0.0
    return 20.0 * np.log10(max(rms, 1e-12))


class IncrementalFrameDecoder:
    """
    Incremental frame decoder that can accept new audio samples over time.
    """

    def __init__(self, *, sample_rate: int = config.SAMPLE_RATE) -> None:
        self.sample_rate = sample_rate
        self._buffer = np.empty(0, dtype=np.float64)
        self._search_index = 0
        self._tone_samples = int(
            round(self.sample_rate * (config.START_END_TONE_DURATION_MS / 1000.0))
        )
        self._sync_bits = utils.bits_from_bytes(b"\xDD\xAA")
        max_frame_seconds = 0.0
        # Rough upper bound: start tone + end tone + payload at the slowest baud rate.
        if config.BAUD_RATES:
            slowest_baud = min(config.BAUD_RATES)
            # Assume a conservative upper bound of 512 payload bytes + header + CRC.
            payload_bits = (Header.HEADER_LENGTH + 512 + 2) * 8
            max_frame_seconds = (
                2 * (config.START_END_TONE_DURATION_MS / 1000.0)
                + payload_bits / float(slowest_baud)
            )
        # Fall back to 10 seconds if configuration lacks baud rates.
        if max_frame_seconds <= 0.0:
            max_frame_seconds = 10.0
        max_frame_samples = int(round(max_frame_seconds * self.sample_rate))
        # Keep at least the tone window plus the max frame budget to avoid truncation.
        self._tail_keep = max(max_frame_samples, self._tone_samples * 2)

    def ingest(
        self, samples: Iterable[float] | np.ndarray
    ) -> Iterator[tuple[FrameMetadata, Header, bytes]]:
        """
        Append samples into the decoder and yield any frames that can be parsed.
        """
        if isinstance(samples, np.ndarray):
            array = np.asarray(samples, dtype=np.float64)
        else:
            array = np.asarray(list(samples), dtype=np.float64)

        if array.ndim != 1:
            raise ValueError("samples must be a one-dimensional sequence.")
        if array.size == 0:
            return iter(())

        if self._buffer.size == 0:
            self._buffer = array.copy()
        else:
            self._buffer = np.concatenate((self._buffer, array))

        return self._extract_frames()

    def _extract_frames(self) -> Iterator[tuple[FrameMetadata, Header, bytes]]:
        frames: list[tuple[FrameMetadata, Header, bytes]] = []
        if self._buffer.size <= self._tone_samples * 2:
            return iter(frames)

        guard_samples = max(1, self._tone_samples // 8)
        while True:
            if self._buffer.size <= self._tone_samples * 2:
                self._keep_recent_tail()
                break

            start_index = _find_tone_window(
                self._buffer,
                detect_start_tone,
                window_size=self._tone_samples,
                start_index=self._search_index,
            )

            if start_index < 0:
                self._search_index = max(0, self._buffer.size - self._tone_samples)
                self._keep_recent_tail()
                break

            start_end = start_index + self._tone_samples
            if start_end >= self._buffer.size:
                self._trim_prefix_for_partial(start_index)
                break

            end_index = _find_tone_window(
                self._buffer,
                detect_end_tone,
                window_size=self._tone_samples,
                start_index=start_end,
                refine_forward=True,
            )
            if end_index < 0:
                self._trim_prefix_for_partial(start_index)
                break

            end_end = end_index + self._tone_samples
            if end_end > self._buffer.size:
                self._trim_prefix_for_partial(start_index)
                break

            data_end_index = min(
                end_index + guard_samples, end_index + self._tone_samples, self._buffer.size
            )
            data_segment = self._buffer[start_end:data_end_index]
            if data_segment.size <= 0:
                self._consume(end_end)
                continue

            start_segment = self._buffer[start_index:start_end]
            end_segment = self._buffer[end_index:end_end]

            frame = self._parse_frame_from_segment(
                data_segment=data_segment,
                start_segment=start_segment,
                end_segment=end_segment,
            )
            if frame is None:
                # Could not parse; drop this window and continue searching.
                self._consume(end_end)
                continue

            frames.append(frame)
            self._consume(end_end)
            # Continue looking for additional frames in the remaining buffer.

        return iter(frames)

    def _parse_frame_from_segment(
        self,
        *,
        data_segment: np.ndarray,
        start_segment: np.ndarray,
        end_segment: np.ndarray,
    ) -> tuple[FrameMetadata, Header, bytes] | None:
        sync_len = len(self._sync_bits)
        for baud in config.BAUD_RATES:
            try:
                bits = demodulate_afsk(data_segment, baud=baud)
            except ValueError:
                continue

            if len(bits) < sync_len + Header.HEADER_LENGTH * 8:
                continue

            sync_index = _find_sync(bits, self._sync_bits)
            if sync_index < 0:
                continue

            post_sync_bits = bits[sync_index + sync_len :]
            usable_len = len(post_sync_bits) - (len(post_sync_bits) % 8)
            if usable_len < Header.HEADER_LENGTH * 8:
                continue

            frame_bits = post_sync_bits[:usable_len]
            frame_bytes = utils.bytes_from_bits(frame_bits)

            if len(frame_bytes) < Header.HEADER_LENGTH + 2:
                continue

            try:
                header = Header.from_bytes(frame_bytes[: Header.HEADER_LENGTH])
            except ValueError:
                continue

            expected_total = Header.HEADER_LENGTH + header.length + 2
            if len(frame_bytes) < expected_total:
                continue

            frame_payload_bytes = frame_bytes[:expected_total]
            try:
                parsed_header, payload = framing.parse_frame(frame_payload_bytes)
            except ValueError:
                continue

            metadata = FrameMetadata(
                timestamp=time(),
                detected_baud=baud,
                rssi=_estimate_rssi(start_segment, end_segment),
            )
            return metadata, parsed_header, payload

        return None

    def _consume(self, count: int) -> None:
        if count <= 0 or self._buffer.size == 0:
            return
        if count >= self._buffer.size:
            self._buffer = np.empty(0, dtype=np.float64)
            self._search_index = 0
            return
        self._buffer = self._buffer[count:]
        self._search_index = max(0, self._search_index - count)

    def _trim_prefix_for_partial(self, start_index: int) -> None:
        # Keep a guard region before the detected start tone.
        guard = max(self._tone_samples, 1)
        drop = max(0, start_index - guard)
        if drop > 0:
            self._consume(drop)
            start_index -= drop
        max_start = max(0, self._buffer.size - self._tone_samples)
        self._search_index = min(start_index, max_start)

    def _keep_recent_tail(self) -> None:
        if self._buffer.size <= self._tail_keep:
            return
        drop = self._buffer.size - self._tail_keep
        self._consume(drop)


def stream_frames_from_chunks(
    chunks: Iterable[np.ndarray],
) -> Iterator[tuple[FrameMetadata, Header, bytes]]:
    """
    Consume a sequence of sample chunks and yield frames as they are decoded.
    """
    decoder = IncrementalFrameDecoder()
    for chunk in chunks:
        yield from decoder.ingest(chunk)


def stream_frames_from_microphone(
    *, device: str | None = None
) -> Iterator[tuple[FrameMetadata, Header, bytes]]:
    """
    Convenience wrapper that listens to the microphone and yields frames continuously.
    """
    for frame in stream_frames_from_chunks(read_from_microphone(device=device)):
        yield frame

