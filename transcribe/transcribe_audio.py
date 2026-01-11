#!/usr/bin/env python3
import argparse
import os
from pathlib import Path

from faster_whisper import WhisperModel


def parse_args():
    p = argparse.ArgumentParser(
        description="Batch transcribe MP3s to .txt using faster-whisper (medium)."
    )
    p.add_argument("--input-dir", required=True, help="Folder with .mp3 files")
    p.add_argument("--output-dir", default="transcripts", help="Output folder for .txt")
    p.add_argument(
        "--language",
        default=None,
        help="Force language code (e.g. 'en'); default: auto-detect",
    )
    p.add_argument(
        "--cpu-threads",
        type=int,
        default=max(1, (os.cpu_count() or 4) // 2),
        help="CPU threads for faster-whisper (default: half your cores).",
    )
    return p.parse_args()


def load_model(cpu_threads: int):
    # On M1: device='cpu', compute_type='int8' is usually the sweet spot
    print(f"Loading faster-whisper model 'medium' on CPU (int8), threads={cpu_threads}...")
    model = WhisperModel(
        "medium",
        device="cpu",
        compute_type="int8",
        cpu_threads=cpu_threads,
        num_workers=1,
    )
    return model


def transcribe_file(model, src: Path, dest_txt: Path, language: str | None):
    partial = dest_txt.with_suffix(dest_txt.suffix + ".partial")

    # If a stale partial exists, just overwrite it
    if partial.exists():
        partial.unlink()

    print(f"[TRANSCRIBE] {src.name} -> {dest_txt.name}")

    segments, info = model.transcribe(
        str(src),
        language=language,
        beam_size=5,
        best_of=5,
        vad_filter=True,
    )

    with partial.open("w", encoding="utf-8") as f:
        f.write(f"# language: {info.language}\n")
        f.write(f"# duration: {info.duration:.2f}s\n\n")
        for seg in segments:
            text = seg.text.strip()
            if text:
                f.write(text + " ")

    os.replace(partial, dest_txt)
    print(f"[DONE] {src.name}")


def main():
    args = parse_args()
    in_dir = Path(args.input_dir).expanduser().resolve()
    out_dir = Path(args.output_dir).expanduser().resolve()

    if not in_dir.is_dir():
        raise SystemExit(f"Input dir does not exist or is not a directory: {in_dir}")

    out_dir.mkdir(parents=True, exist_ok=True)

    mp3_files = sorted(in_dir.glob("*.mp3"))
    if not mp3_files:
        print(f"No .mp3 files found in {in_dir}")
        return

    model = load_model(args.cpu_threads)

    for mp3 in mp3_files:
        dest_txt = out_dir / (mp3.stem + ".txt")

        if dest_txt.exists():
            print(f"[SKIP] {mp3.name} (already has transcript)")
            continue

        try:
            transcribe_file(model, mp3, dest_txt, args.language)
        except KeyboardInterrupt:
            print("\nInterrupted by user. Partial file kept if any.")
            break
        except Exception as e:
            print(f"[ERROR] {mp3.name}: {e}")

    print("Done.")


if __name__ == "__main__":
    main()
