"""
CLI entry point for transmitting text over the audio modem.
"""

from __future__ import annotations

import typer

from pathlib import Path

from modem import config
from modem.framing import Header
from modem.tx import assemble_transmission, play_audio, write_wav

# Rich is an explicit dependency; use it for friendly terminal output.
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.status import Status
from rich import box

_console = Console()

app = typer.Typer(help="Transmit text payloads using the audio modem prototype.")


@app.command()
def main(
    message: str = typer.Argument(..., help="UTF-8 text message to transmit."),
    baud: int = typer.Option(200, "--baud", help="Symbol rate for the transmission."),
    repeats: int = typer.Option(1, "--repeats", min=1, help="Number of times to repeat the frame."),
    device: str | None = typer.Option(None, "--device", help="Audio output device identifier."),
    wav_out: str | None = typer.Option(None, "--wav-out", help="Optional WAV file destination."),
) -> None:
    """
    Play back an encoded frame containing the provided message.
    """
    if baud not in config.BAUD_TO_RATE_CODE:
        raise typer.BadParameter(f"Unsupported baud: {baud}. Choose from {config.BAUD_RATES}.")

    payload = message.encode("utf-8")
    header = Header(
        version=config.DEFAULT_VERSION,
        rate_code=config.BAUD_TO_RATE_CODE[baud],
        flags=config.DEFAULT_FLAGS,
        length=len(payload),
    )

    waveform = assemble_transmission(message, header=header, repeats=repeats)

    info = Table.grid(padding=(0, 1))
    info.add_column(justify="right", style="bold cyan")
    info.add_column()
    info.add_row("Bytes", str(len(payload)))
    info.add_row("Baud", str(baud))
    info.add_row("Repeats", str(repeats))
    if device:
        info.add_row("Device", device)
    if wav_out:
        info.add_row("WAV Out", str(Path(wav_out).expanduser()))

    _console.print(Panel(info, title="Transmit", box=box.ROUNDED, border_style="bright_blue"))

    if wav_out is not None:
        destination = Path(wav_out).expanduser().resolve()
        write_wav(waveform, destination)
        _console.print(f"Wrote WAV to {destination}", style="green")

    with Status("Playing audio...", console=_console, spinner="dots"):
        play_audio(waveform, device=device)

    _console.print(Panel("Transmission complete.", style="green", box=box.ROUNDED))


if __name__ == "__main__":
    app()

