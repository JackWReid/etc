"""
CLI to transmit text using the CSS modem waveform.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.status import Status
from rich.table import Table

from modem import config
from modem.css import ChirpParams, assemble_css_transmission
from modem.framing import Header
from modem.tx import play_audio, write_wav

_console = Console()

app = typer.Typer(help="Transmit text payloads using the CSS acoustic modem.")


@app.command()
def main(
    message: str = typer.Argument(..., help="UTF-8 text message to transmit."),
    sf: int = typer.Option(config.CSS_DEFAULT_SF, "--sf", min=1, help="Spreading factor."),
    bw: float = typer.Option(config.CSS_DEFAULT_BW, "--bw", help="Chirp bandwidth (Hz)."),
    center: float = typer.Option(
        config.CSS_DEFAULT_CENTER, "--center", help="Chirp center frequency (Hz)."
    ),
    repeats: int = typer.Option(1, "--repeats", min=1, help="Number of frame repeats."),
    fec: bool = typer.Option(False, "--fec/--no-fec", help="Enable convolutional FEC."),
    interleave: int = typer.Option(
        1, "--interleave", min=1, help="Bit interleave depth (FEC modes)."
    ),
    tones: bool = typer.Option(False, "--tones/--no-tones", help="Include start/end tones."),
    device: str | None = typer.Option(None, "--device", help="Audio output device identifier."),
    wav_out: str | None = typer.Option(None, "--wav-out", help="Optional WAV file destination."),
) -> None:
    """
    Encode and play a CSS waveform for the provided message.
    """
    payload = message.encode("utf-8")
    header = Header(
        version=config.DEFAULT_VERSION,
        rate_code=0,
        flags=config.DEFAULT_FLAGS,
        length=len(payload),
    )

    params = ChirpParams(
        sf=sf,
        bw=bw,
        fc=center,
        preamble_up=config.CSS_DEFAULT_PREAMBLE_UP,
        preamble_down=config.CSS_DEFAULT_PREAMBLE_DOWN,
    )

    waveform = assemble_css_transmission(
        message,
        header=header,
        params=params,
        repeats=repeats,
        fec_enabled=fec,
        interleave_depth=interleave,
        include_tones=tones,
    )

    info = Table.grid(padding=(0, 1))
    info.add_column(justify="right", style="bold cyan")
    info.add_column()
    info.add_row("Bytes", str(len(payload)))
    info.add_row("SF", str(sf))
    info.add_row("Bandwidth", f"{bw:.1f} Hz")
    info.add_row("Center", f"{center:.1f} Hz")
    info.add_row("Repeats", str(repeats))
    info.add_row("FEC", "on" if fec else "off")
    if wav_out:
        info.add_row("WAV Out", str(Path(wav_out).expanduser()))
    if device:
        info.add_row("Device", device)

    _console.print(Panel(info, title="CSS Transmit", box=box.ROUNDED, border_style="bright_blue"))

    if wav_out is not None:
        destination = Path(wav_out).expanduser().resolve()
        write_wav(waveform, destination)
        _console.print(f"Wrote WAV to {destination}", style="green")

    with Status("Playing audio...", console=_console, spinner="dots"):
        play_audio(waveform, device=device)

    _console.print(Panel("Transmission complete.", style="green", box=box.ROUNDED))


if __name__ == "__main__":
    app()


