"""
CLI entry point for receiving text over the audio modem.
"""

# pyright: reportMissingImports=false

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Iterator

import numpy as np
import typer

from modem import config
from modem import rx
from time import monotonic

# Optional rich-based formatting. Falls back to plain output if unavailable.
try:  # pragma: no cover - presentation only
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich import box

    _RICH_AVAILABLE = True
    _console = Console()
except Exception:  # pragma: no cover - graceful fallback
    _RICH_AVAILABLE = False
    _console = None  # type: ignore[assignment]

try:  # pragma: no cover - dependency is expected to be available
    from scipy.io import wavfile
except ImportError as exc:  # pragma: no cover - fail with actionable guidance
    raise RuntimeError(
        "scipy is required for WAV decoding. Install the 'scipy' dependency."
    ) from exc

app = typer.Typer(help="Receive text payloads using the audio modem prototype.")


def _load_waveform_from_wav(path: Path) -> np.ndarray:
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


def _decode_and_report(samples: Iterable[float]) -> None:
    frames = list(rx.decode_stream(samples))
    if not frames:
        if _RICH_AVAILABLE:
            _console.print(Panel(Text("No frames decoded.", style="bold red"), box=box.ROUNDED))
        else:
            typer.echo("No frames decoded.")
        return

    for frame in frames:
        _report_frame(frame)


def _report_frame(frame: tuple[rx.FrameMetadata, rx.Header, bytes]) -> None:
    metadata, header, payload = frame
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError:
        text = payload.hex()

    if _RICH_AVAILABLE:
        stats = Table.grid(padding=(0, 1))
        stats.add_column(justify="right", style="bold cyan")
        stats.add_column()
        stats.add_row("Baud", str(metadata.detected_baud))
        stats.add_row("Version", str(header.version))
        stats.add_row("Flags", f"0x{header.flags:02X}")
        stats.add_row("Length", str(header.length))
        if getattr(metadata, "rssi", None) is not None:
            stats.add_row("RSSI", f"{metadata.rssi:.1f} dB")
        stats.add_row("Timestamp", f"{metadata.timestamp:.3f}s")

        # Render payload with subtle styling; hex payloads in dim cyan.
        is_hex = payload != payload.decode("utf-8", errors="ignore").encode("utf-8")
        payload_label = Text("Payload", style="bold green")
        payload_text = Text(text, style="cyan dim" if is_hex else "green")

        body = Table.grid(expand=True)
        body.add_row(stats)
        body.add_row("")
        body.add_row(payload_label)
        body.add_row(payload_text)

        _console.print(
            Panel(
                body,
                title="Frame Decoded",
                title_align="left",
                box=box.ROUNDED,
                border_style="bright_blue",
            )
        )
    else:
        typer.echo(
            "Frame detected: baud=%d version=%d flags=0x%02X length=%d"
            % (metadata.detected_baud, header.version, header.flags, header.length)
        )
        typer.echo(f"Payload: {text}")


@app.command()
def main(
    baud_default: int = typer.Option(
        200, "--baud-default", help="Initial symbol rate assumption before sync."
    ),
    device: str | None = typer.Option(None, "--device", help="Audio input device identifier."),
    wav_in: str | None = typer.Option(None, "--wav-in", help="Optional WAV file source."),
    open_channel: bool = typer.Option(
        False,
        "--open-channel",
        help="Continuously decode frames from the input device without stopping.",
    ),
) -> None:
    """
    Decode frames from a WAV file or live audio capture.
    """
    if baud_default not in config.BAUD_TO_RATE_CODE:
        raise typer.BadParameter(
            f"Unsupported baud: {baud_default}. Choose from {config.BAUD_RATES}."
        )

    if wav_in and open_channel:
        raise typer.BadParameter("--open-channel cannot be used with --wav-in.")

    if wav_in:
        waveform = _load_waveform_from_wav(Path(wav_in))
        _decode_and_report(waveform)
        return

    if open_channel:
        _run_open_channel_listener(device=device)
        return

    if _RICH_AVAILABLE:
        _console.rule("Listening for frames", style="bright_blue")
        _console.print("Press Ctrl+C to stop.", style="dim")
    else:
        typer.echo("Listening for frames... Press Ctrl+C to stop.")
    captured_chunks: list[np.ndarray] = []
    try:
        for chunk in rx.read_from_microphone(device=device):
            captured_chunks.append(chunk)
    except KeyboardInterrupt:
        if _RICH_AVAILABLE:
            _console.print("Capture stopped, decoding collected audio.", style="yellow")
        else:
            typer.echo("Capture stopped, decoding collected audio.")

    if not captured_chunks:
        if _RICH_AVAILABLE:
            _console.print(Panel("No audio captured.", style="red"))
        else:
            typer.echo("No audio captured.")
        return

    waveform = np.concatenate(captured_chunks).astype(np.float32, copy=False)
    _decode_and_report(waveform)


def _run_open_channel_listener(*, device: str | None) -> None:
    if _RICH_AVAILABLE:
        from rich.live import Live
        from rich.spinner import Spinner

        _console.rule("Open-channel listener", style="bright_blue")
        decoded_any = False
        frame_count = 0
        last_activity = "Listening for frames..."
        started = monotonic()
        last_baud: int | None = None
        last_rssi: float | None = None

        def _render_live() -> Panel:
            table = Table.grid(padding=(0, 1))
            table.add_column(justify="left")
            table.add_column(justify="right")
            spinner = Spinner("dots", text=last_activity, style="bright_blue")
            table.add_row(spinner, f"[dim]{monotonic() - started:0.1f}s[/dim]")
            table.add_row("[bold cyan]Frames[/bold cyan]", str(frame_count))
            table.add_row("[bold cyan]Last baud[/bold cyan]", str(last_baud) if last_baud is not None else "—")
            table.add_row(
                "[bold cyan]Last RSSI[/bold cyan]",
                f"{last_rssi:.1f} dB" if last_rssi is not None else "—",
            )
            return Panel(table, title="Live", border_style="bright_blue", box=box.ROUNDED)

        # Use an incremental decoder so we can inspect chunks and update live view.
        decoder = rx.IncrementalFrameDecoder()
        try:
            with Live(_render_live(), console=_console, refresh_per_second=10, transient=False) as live:
                for chunk in rx.read_from_microphone(device=device):
                    # Hint when a possible start tone is present.
                    try:
                        if rx.detect_start_tone(chunk):
                            last_activity = "Possible frame detected — syncing..."
                            live.update(_render_live())
                    except Exception:
                        pass
                    for frame in decoder.ingest(chunk):
                        decoded_any = True
                        frame_count += 1
                        last_activity = "Frame decoded!"
                        # Update last-baud/RSSI for live panel
                        try:
                            meta = frame[0]
                            last_baud = getattr(meta, "detected_baud", None)
                            last_rssi = getattr(meta, "rssi", None)
                        except Exception:
                            pass
                        live.update(_render_live())
                        _report_frame(frame)
                        last_activity = "Listening for frames..."
                        live.update(_render_live())
        except KeyboardInterrupt:
            _console.print("Stopping open-channel listener.", style="yellow")
        finally:
            if not decoded_any:
                _console.print(Panel(Text("No frames decoded before exit.", style="red")))
    else:
        typer.echo("Open-channel listening... Press Ctrl+C to stop.")
        decoded_any = False
        try:
            for frame in _iterate_stream_frames(device=device):
                decoded_any = True
                _report_frame(frame)
        except KeyboardInterrupt:
            typer.echo("Stopping open-channel listener.")
        finally:
            if not decoded_any:
                typer.echo("No frames decoded before exit.")


def _iterate_stream_frames(
    *, device: str | None
) -> Iterator[tuple[rx.FrameMetadata, rx.Header, bytes]]:
    yield from rx.stream_frames_from_microphone(device=device)


if __name__ == "__main__":
    app()
