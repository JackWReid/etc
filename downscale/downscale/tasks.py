# downscale/tasks.py
import logging
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

from rich.progress import Progress # Use rich for progress display

from .config import cfg
from .database import (
    get_large_source_files,
    get_task_by_source_id,
    add_transcode_task,
    update_source_file_duration,
    get_transcoded_path_for_source,
)

def run_ffprobe(file_path: Path) -> Optional[float]:
    """Runs ffprobe to get the duration of a video file."""
    command = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path)
    ]
    logging.debug(f"Running ffprobe command: {' '.join(command)}")
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
        duration_str = result.stdout.strip()
        if duration_str and duration_str != 'N/A':
            return float(duration_str)
        else:
            logging.warning(f"ffprobe could not determine duration for: {file_path}")
            return None
    except FileNotFoundError:
        logging.error("ffprobe command not found. Please ensure ffmpeg (which includes ffprobe) is installed and in your PATH.")
        return None
    except subprocess.CalledProcessError as e:
        logging.error(f"ffprobe failed for {file_path}: {e.stderr}")
        return None
    except ValueError:
        logging.error(f"Could not parse ffprobe duration output '{result.stdout.strip()}' for {file_path}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred running ffprobe for {file_path}: {e}")
        return None


def create_transcode_tasks() -> List[Tuple[int, Path, int]]:
    """
    Identifies source files needing transcoding and creates tasks in the database.

    Returns:
        List[Tuple[int, Path, int]]: A list of tuples, each containing
                                     (task_id, source_path, source_size_bytes)
                                     for newly created or existing pending tasks.
                                     Returns an empty list if no tasks need processing.
    """
    logging.info(f"Identifying files larger than {cfg.threshold_bytes / cfg.BYTES_PER_GB:.2f} GB for transcoding.")
    large_files = get_large_source_files(cfg.threshold_bytes)
    newly_created_tasks = []
    tasks_to_process = [] # Includes new and existing pending/interrupted

    if not large_files:
        logging.info("No source files found exceeding the size threshold.")
        return []

    logging.info(f"Found {len(large_files)} files exceeding threshold. Checking task status...")

    with Progress(transient=True) as progress:
        task_check = progress.add_task("[cyan]Checking files and creating tasks...", total=len(large_files))

        for file_row in large_files:
            source_file_id = file_row['id']
            source_path = Path(file_row['file_path'])
            source_size = file_row['size_bytes']
            duration = file_row['duration_seconds']

            progress.update(task_check, description=f"[cyan]Checking: {source_path.name}")

            # 1. Check if already successfully transcoded
            existing_transcoded_path = get_transcoded_path_for_source(source_file_id)
            if existing_transcoded_path:
                 if Path(existing_transcoded_path).exists():
                     logging.info(f"Skipping '{source_path.name}': Already successfully transcoded to '{existing_transcoded_path}'.")
                     progress.update(task_check, advance=1)
                     continue
                 else:
                     logging.warning(f"Found transcoded record for '{source_path.name}' but file '{existing_transcoded_path}' is missing. Will re-queue.")
                     # Potentially delete the transcoded_files entry here if desired

            # 2. Check if a task already exists (pending, running, failed, interrupted)
            existing_task = get_task_by_source_id(source_file_id)
            if existing_task:
                task_id = existing_task['id']
                status = existing_task['status']
                if status in ('pending', 'interrupted'):
                    logging.info(f"Found existing '{status}' task ID {task_id} for '{source_path.name}'. Adding to process list.")
                    tasks_to_process.append((task_id, source_path, source_size))
                elif status == 'running':
                    logging.warning(f"Skipping '{source_path.name}': Task ID {task_id} is already marked as 'running'. Check for stale process (PID {existing_task.get('ffmpeg_pid', 'N/A')}).")
                elif status == 'completed':
                    # This case should ideally be caught by get_transcoded_path_for_source, but check just in case
                    logging.info(f"Skipping '{source_path.name}': Task ID {task_id} is already marked as 'completed'.")
                elif status == 'failed':
                    logging.warning(f"Skipping '{source_path.name}': Task ID {task_id} previously failed. Re-run manually or clear status if needed.")
                progress.update(task_check, advance=1)
                continue

            # 3. If no existing task or completed file, create a new task
            logging.info(f"File '{source_path.name}' needs transcoding. Creating task...")

            # Get duration if not already known
            if duration is None:
                logging.info(f"Probing duration for '{source_path.name}'...")
                duration = run_ffprobe(source_path)
                if duration:
                    update_source_file_duration(source_file_id, duration)
                else:
                    logging.error(f"Cannot create task for '{source_path.name}': Failed to get duration.")
                    progress.update(task_check, advance=1)
                    continue # Skip this file if we can't get duration

            # Determine target path structure
            target_sub_dir = source_path.parent.name # e.g., "Movie (Year)"
            target_filename = source_path.stem + ".mp4" # Change extension to mp4 (adjust if needed)
            target_full_dir = cfg.output_dir / target_sub_dir

            # Create the task in the DB
            new_task_id = add_transcode_task(source_file_id, cfg.output_dir, target_sub_dir, target_filename)

            if new_task_id:
                tasks_to_process.append((new_task_id, source_path, source_size))
                newly_created_tasks.append((new_task_id, source_path, source_size))
            else:
                logging.error(f"Failed to create database task entry for {source_path.name}")

            progress.update(task_check, advance=1)

        progress.update(task_check, completed=True, description="[green]Task check complete.")

    if newly_created_tasks:
        logging.info(f"Created {len(newly_created_tasks)} new transcode tasks.")
    if tasks_to_process:
        logging.info(f"Total tasks to process (new + pending/interrupted): {len(tasks_to_process)}")
    else:
        logging.info("No tasks require processing at this time.")

    return tasks_to_process

