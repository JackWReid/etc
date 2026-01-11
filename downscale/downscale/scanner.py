# downscale/scanner.py
import os
import logging
from pathlib import Path
from typing import Generator

from rich.progress import Progress # Use rich for progress display

from .config import cfg
from .database import add_or_update_source_file

def scan_source_directory() -> int:
    """
    Recursively scans the source directory for video files.

    Updates the database with found files and their metadata.

    Returns:
        int: The number of potential video files found.
    """
    logging.info(f"Starting scan of source directory: {cfg.source_dir}")
    found_files_count = 0
    skipped_count = 0

    # Use scandir for potentially better performance on large directories
    # We expect structure like: source_dir / Movie (Year) / movie_file.ext
    # So we iterate one level deep first.
    movie_dirs: Generator[Path, None, None] = (Path(entry.path) for entry in os.scandir(cfg.source_dir) if entry.is_dir())

    with Progress(transient=True) as progress:
        scan_task = progress.add_task("[cyan]Scanning source directory...", total=None) # Indeterminate

        for movie_dir in movie_dirs:
            progress.update(scan_task, description=f"[cyan]Scanning: {movie_dir.name}")
            logging.debug(f"Scanning directory: {movie_dir}")
            try:
                for item in movie_dir.iterdir():
                    if item.is_file() and item.suffix.lower() in cfg.VIDEO_EXTENSIONS:
                        found_files_count += 1
                        try:
                            stats = item.stat()
                            size_bytes = stats.st_size
                            last_modified = stats.st_mtime # Timestamp
                            # Update DB - this handles inserts and updates
                            add_or_update_source_file(item, size_bytes, last_modified)
                        except OSError as e:
                            logging.warning(f"Could not stat file {item}: {e}")
                            skipped_count += 1
                        except Exception as e:
                            logging.error(f"Unexpected error processing file {item}: {e}")
                            skipped_count += 1
                    elif item.is_file():
                         logging.debug(f"Skipping non-video file: {item}")
            except OSError as e:
                logging.warning(f"Could not scan directory {movie_dir}: {e}")
                skipped_count += 1
            except Exception as e:
                logging.error(f"Unexpected error scanning directory {movie_dir}: {e}")
                skipped_count += 1

        progress.update(scan_task, completed=True, description="[green]Scan complete.")

    logging.info(f"Scan complete. Found {found_files_count} potential video files.")
    if skipped_count > 0:
        logging.warning(f"Skipped {skipped_count} files/directories due to errors.")

    return found_files_count

