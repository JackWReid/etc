# Audio Modem

Scaffold for an AFSK-based audio modem toolkit. The project targets 48 kHz audio, multiple baud rates, and optional ChaCha20-Poly1305 encryption. Tooling is managed via `uv`.

## Quick start

```bash
uv sync
uv run apps/send_text.py --help
uv run apps/recv_text.py --help
```

Unit tests run with:

```bash
uv run pytest
```

## CLI tools

### Transmit (`apps/send_text.py`)

Send a UTF-8 message as an audio frame:

```bash
uv run apps/send_text.py "Hello, world!"
```

Available options:

- `--baud`: Symbol rate (default `200`). Must be one of `50, 100, 200, 400, 800`.
- `--repeats`: Repeat the frame `N` times (default `1`). Useful for noisy links.
- `--device`: Sounddevice output identifier. Omit to use the system default.
- `--wav-out`: Path to write the generated waveform instead of (or in addition to) playback.

Examples:

```bash
# Send once at 400 baud through the default audio output.
uv run apps/send_text.py "Beacon" --baud 400

# Write a WAV file containing three repeats at 100 baud.
uv run apps/send_text.py "Test frame" --baud 100 --repeats 3 --wav-out out.wav

# Play through a specific audio interface by name.
uv run apps/send_text.py "Diagnostics" --device "USB Audio CODEC"
```

### Receive (`apps/recv_text.py`)

Decode frames from a WAV file or the system microphone:

- `--baud-default`: Initial baud assumption before frame detection (default `200`).
- `--device`: Optional audio input device identifier for live capture.
- `--wav-in`: Optional WAV file to decode instead of live audio.
- `--open-channel`: Continuously decode frames from the input device until interrupted.

Examples:

```bash
# Decode an existing recording.
uv run apps/recv_text.py --wav-in recordings/link-budget.wav

# Listen on the default input until Ctrl+C is pressed, then decode.
uv run apps/recv_text.py

# Keep a rolling listener active and print frames as soon as they are decoded.
uv run apps/recv_text.py --open-channel
```

## Python API examples

The core modem features are exposed as a Python package. Quick interactive snippets:

```python
from modem import config
from modem.framing import Header
from modem.tx import assemble_transmission
from modem.rx import decode_stream

message = "Loopback!"
header = Header(
    version=config.DEFAULT_VERSION,
    rate_code=config.BAUD_TO_RATE_CODE[200],
    flags=config.DEFAULT_FLAGS,
    length=len(message.encode("utf-8")),
)

waveform = assemble_transmission(message, header=header, repeats=1)
decoded_frames = list(decode_stream(waveform))
```

The `decode_stream` helper now scans continuous audio buffers, so you can feed entire recordings or live capture chunks and receive parsed `(metadata, header, payload)` tuples on success.


