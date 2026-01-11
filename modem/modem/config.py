"""
Shared configuration constants for the audio modem toolkit.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

SAMPLE_RATE: Final[int] = 48_000
MARK_FREQUENCY: Final[float] = 1_200.0
SPACE_FREQUENCY: Final[float] = 2_200.0
START_TONE_FREQUENCY: Final[float] = 1_000.0
END_TONE_FREQUENCY: Final[float] = 1_500.0
START_END_TONE_DURATION_MS: Final[int] = 250

CSS_DEFAULT_SF: Final[int] = 8
CSS_DEFAULT_BW: Final[float] = 1_000.0
CSS_DEFAULT_CENTER: Final[float] = 2_000.0
CSS_DEFAULT_PREAMBLE_UP: Final[int] = 10
CSS_DEFAULT_PREAMBLE_DOWN: Final[int] = 2
CSS_FLAG_FEC: Final[int] = 0x01

BAUD_RATES: Final[tuple[int, ...]] = (50, 100, 200)
RATE_CODE_TO_BAUD: Final[dict[int, int]] = {idx: baud for idx, baud in enumerate(BAUD_RATES)}
BAUD_TO_RATE_CODE: Final[dict[int, int]] = {baud: idx for idx, baud in enumerate(BAUD_RATES)}

DEFAULT_VERSION: Final[int] = 0x01
DEFAULT_FLAGS: Final[int] = 0x00


@dataclass(frozen=True, slots=True)
class TransmissionProfile:
    """Describes the parameters for a single transmission."""

    baud: int
    repeats: int = 1
    volume: float = 0.8

    def rate_code(self) -> int:
        """Return the configured baud rate encoded as a rate code."""
        if self.baud not in BAUD_TO_RATE_CODE:
            raise ValueError(f"Unsupported baud: {self.baud}")
        return BAUD_TO_RATE_CODE[self.baud]


def baud_from_rate_code(code: int) -> int:
    """Return the baud value for a given rate code."""
    try:
        return RATE_CODE_TO_BAUD[code]
    except KeyError as exc:  # pragma: no cover - defensive guard
        raise ValueError(f"Invalid rate code: {code}") from exc


