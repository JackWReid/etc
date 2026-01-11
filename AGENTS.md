# Repository Guidelines

## Project Structure & Module Organization
- `modem/`: A Python package for an AFSK audio modem with CLIs in `apps/` and tests in `tests/`.
- `downscale/`: Python package for scanning/transcoding large video files (ffmpeg required).
- `transcribe/`: One-off scripts (e.g., `transcribe_audio.py`) for batch audio transcription.

## Build, Test, and Development Commands
- Modem: `cd modem && uv sync` — install deps with uv.
- Run CLIs: `uv run apps/send_text.py "Hello"` and `uv run apps/recv_text.py --help`.
- Tests: `uv run pytest` — executes `modem/tests` with strict options.
- Lint: `uv run ruff check .` — fast linting (line length 100).
- Types: `uv run mypy modem` — static type checks for modem package.
- Downscale (local run): `cd downscale && python -m downscale.main --help` (or install, then `downscale`).
- Transcribe: `python transcribe/transcribe_audio.py --help`.

## Coding Style & Naming Conventions
- Indentation: 4 spaces; prefer explicit imports; add type hints for public functions.
- Python: follow Ruff rules `E,F,I,B`; target line length 100 (modem).
- Naming: modules `snake_case.py`, classes `PascalCase`, functions/vars `snake_case`.
- Formatting: keep docstrings short and actionable; avoid long scripts in root—place code in packages.

## Testing Guidelines
- Framework: `pytest` with `--strict-markers` (configured in `modem/pyproject.toml`).
- Location: place unit tests under `modem/tests/`, named `test_*.py`.
- Coverage: add tests for new logic and edge cases; include property-style checks where useful.
- Running examples: keep slow or I/O-heavy checks behind markers (e.g., `@pytest.mark.slow`).

## Commit & Pull Request Guidelines
- Commits: concise, imperative subject (<72 chars). Prefix scope when helpful (e.g., `modem:`, `downscale:`).
- PRs: include a clear summary, linked issues, and before/after notes. For CLI/audio changes, attach sample commands, WAV paths, or screenshots.
- Checks: ensure `uv run ruff check .`, `uv run mypy modem`, and `uv run pytest` pass before requesting review.

## Security & Configuration Tips
- Audio I/O: `sounddevice` may require system PortAudio; verify device names via `uv run python -c "import sounddevice as sd; print(sd.query_devices())"`.
- Transcoding: `downscale` expects `ffmpeg` in `PATH`.
