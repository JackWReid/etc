"""
CLI to decode CSS modem waveforms from WAV files.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from modem import config
from modem import css
from modem import css_rx

try:  # pragma: no cover - dependency should be available
    from scipy.io import wavfile
except ImportError as exc:  # pragma: no cover - fail with actionable guidance
    raise RuntimeError("scipy is required for WAV decoding. Install the 'scipy' extra.") from exc

_console = Console()

app = typer.Typer(help="Decode CSS acoustic modem frames from WAV files.")


def _load_waveform(path: Path) -> np.ndarray:
    if not path.exists():
        raise typer.BadParameter(f"WAV file {path} does not exist.")

    sample_rate, data = wavfile.read(path)
    if sample_rate != config.SAMPLE_RATE:
        raise typer.BadParameter(
            f"WAV sample rate {sample_rate} Hz does not match expected {config.SAMPLE_RATE} Hz."
        )

    array = np.asarray(data)
    if array.ndim == 2:
        array = array[:, 0]

    if np.issubdtype(array.dtype, np.integer):
        info = np.iinfo(array.dtype)
        scale = max(abs(info.min), abs(info.max))
        if scale == 0:
            raise typer.BadParameter("WAV file contains invalid integer amplitude values.")
        array = array.astype(np.float32) / float(scale)
    else:
        array = array.astype(np.float32)
    return np.asarray(array, dtype=np.float32)


@app.command()
def main(
    wav_in: str = typer.Argument(..., help="Path to a WAV file containing a CSS frame."),
    sf: int = typer.Option(config.CSS_DEFAULT_SF, "--sf", min=1, help="Spreading factor."),
    bw: float = typer.Option(config.CSS_DEFAULT_BW, "--bw", help="Chirp bandwidth (Hz)."),
    center: float = typer.Option(
        config.CSS_DEFAULT_CENTER, "--center", help="Chirp center frequency (Hz)."
    ),
    tones: bool = typer.Option(False, "--tones/--no-tones", help="Waveform includes start/end tones."),
) -> None:
    """
    Decode a single CSS frame from the provided WAV file.
    """
    waveform = _load_waveform(Path(wav_in).expanduser().resolve())
    params = css.ChirpParams(
        sf=sf,
        bw=bw,
        fc=center,
        preamble_up=config.CSS_DEFAULT_PREAMBLE_UP,
        preamble_down=config.CSS_DEFAULT_PREAMBLE_DOWN,
    )

    metadata, header, payload = css_rx.decode_css_waveform(
        waveform,
        params,
        includes_preamble=True,
        includes_sync=True,
        includes_tones=tones,
    )

    try:
        text = payload.decode("utf-8")
        payload_repr = text
        payload_style = "green"
    except UnicodeDecodeError:
        payload_repr = payload.hex()
        payload_style = "cyan dim"

    info = Table.grid(padding=(0, 1))
    info.add_column(justify="right", style="bold cyan")
    info.add_column()
    info.add_row("Version", str(header.version))
    info.add_row("Flags", f"0x{header.flags:02X}")
    info.add_row("Length", str(header.length))
    info.add_row("Detected SF", str(metadata.detected_sf))
    info.add_row("Detected BW", f"{metadata.detected_bw:.1f} Hz")
    if metadata.rssi is not None:
        info.add_row("RSSI", f"{metadata.rssi:.1f} dB")

    _console.print(Panel(info, title="CSS Frame", border_style="bright_blue", box=box.ROUNDED))
    _console.print(Panel(payload_repr, title="Payload", border_style="green", style=payload_style))


if __name__ == "__main__":
    app()


