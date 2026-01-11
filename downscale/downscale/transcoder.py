# downscale/transcoder.py
import subprocess
import logging
import re
import signal
import sys
import time
from pathlib import Path
from typing import Optional, Tuple

from .config import cfg
from .database import update_task_status, update_task_start, update_task_progress, add_transcoded_file

# --- Globals for signal handling ---
current_process: Optional[subprocess.Popen] = None
current_task_id: Optional[int] = None

# --- Signal Handler ---
def handle_signal(signum, frame):
    """Gracefully handle termination signals (SIGINT, SIGTERM)."""
    global current_process, current_task_id
    if current_process and current_process.poll() is None: # Check if process is running
        logging.warning(f"Received signal {signum}. Terminating ffmpeg process PID {current_process.pid} for task {current_task_id}...")
        try:
            # Send SIGTERM first for graceful shutdown if ffmpeg handles it
            current_process.terminate()
            try:
                # Wait a bit for ffmpeg to exit
                current_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logging.warning("ffmpeg did not terminate gracefully, sending SIGKILL.")
                current_process.kill() # Force kill if necessary
        except Exception as e:
            logging.error(f"Error terminating ffmpeg process: {e}")
            current_process.kill() # Ensure it's killed

        if current_task_id:
            logging.warning(f"Marking task {current_task_id} as 'interrupted'.")
            update_task_status(current_task_id, 'interrupted', error_message=f"Process interrupted by signal {signum}")
    else:
        logging.warning(f"Received signal {signum}, but no active ffmpeg process found or process already finished.")

    # Exit the main script
    print("\nExiting due to signal.", file=sys.stderr)
    sys.exit(1) # Indicate abnormal termination

# --- FFmpeg Execution ---
def run_ffmpeg_transcode(
    task_id: int,
    source_path: Path,
    target_path: Path,
    total_duration: Optional[float],
    progress_callback # Function to update Rich progress bar
) -> Tuple[bool, Optional[Path], Optional[str]]:
    """
    Runs the ffmpeg transcoding process for a single task.

    Args:
        task_id: The database ID of the task.
        source_path: Path to the input video file.
        target_path: Path for the output video file.
        total_duration: Total duration of the source video in seconds (for progress %).
        progress_callback: Function to call with progress updates (current_time, percentage, fps, speed, output_size).

    Returns:
        Tuple containing:
        - True if transcoding was successful, False otherwise.
        - Path to the output file if successful, None otherwise.
        - Error message if failed, None otherwise.
    """
    global current_process, current_task_id

    if not total_duration or total_duration <= 0:
        logging.error(f"Task {task_id}: Invalid total duration ({total_duration}). Cannot calculate progress.")
        update_task_status(task_id, 'failed', 'Invalid source duration')
        return False, None, "Invalid source duration"

    # Ensure target directory exists
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # --- Build FFmpeg Command ---
    # Adjust these parameters as needed for desired quality/compatibility
    # -map 0 copies all streams (video, audio, subtitles)
    # -c:v libx264: Good balance of quality/compatibility/speed
    # -crf 22: Constant Rate Factor (lower means better quality, larger file). 18-28 is common.
    # -preset medium: Encoding speed vs compression efficiency. Slower presets = better compression.
    # -vf "scale=-2:1080": Scale to 1080p height, maintaining aspect ratio (-2 ensures width is even).
    # -c:a aac: Common audio codec. Use 'copy' if you don't want to re-encode audio.
    # -b:a 192k: Audio bitrate (if re-encoding).
    # -c:s copy: Copy subtitle streams without re-encoding.
    # -progress pipe:1: Send progress information to stdout.
    # -y: Overwrite output file without asking.
    command = [
        "ffmpeg",
        "-hide_banner", # Suppress version info
        "-analyzeduration", "100M",  # Increase analyzeduration to 100MB
        "-probesize", "50M",         # Increase probesize to 50MB
        "-i", str(source_path),
        "-map", "0",             # Include all streams from input 0
        "-c:v", "libx264",       # Video codec
        "-crf", "22",            # Video quality
        "-preset", "medium",     # Encoding speed/compression trade-off
        "-vf", "scale=-2:1080",  # Scale to 1080p height, keep aspect ratio
        "-c:a", "aac",           # Audio codec (use 'copy' to avoid re-encoding)
        "-b:a", "192k",          # Audio bitrate (if using aac)
        "-c:s", "copy",          # Copy subtitles
        "-progress", "pipe:1",   # Output progress to stdout
        "-y",                    # Overwrite output without asking
        str(target_path)
    ]

    logging.info(f"Task {task_id}: Starting transcode for '{source_path.name}'")
    logging.info(f"Task {task_id}: Output path: '{target_path}'")
    logging.debug(f"Task {task_id}: FFmpeg command: {' '.join(command)}")

    process = None
    start_time = time.time()
    try:
        # Start the ffmpeg process
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, # Capture stderr for errors
            text=True, # Decode stdout/stderr as text
            encoding='utf-8',
            errors='replace' # Handle potential decoding errors
        )

        # Update DB: Mark as running and store PID
        update_task_start(task_id, process.pid)
        current_process = process
        current_task_id = task_id

        # --- Process FFmpeg Output ---
        progress_data = {}
        while True:
            if process.stdout:
                line = process.stdout.readline()
                if not line and process.poll() is not None: # Process finished
                    break
                if line:
                    # Parse progress line (key=value)
                    parts = line.strip().split('=', 1)
                    if len(parts) == 2:
                        key, value = parts
                        progress_data[key.strip()] = value.strip()

                        # Check if we have a 'time=' key to update progress
                        if key.strip() == 'time':
                            time_str = value.strip()
                            try:
                                # FFmpeg time format can be HH:MM:SS.ms or just seconds
                                if ':' in time_str:
                                    h, m, s_ms = time_str.split(':')
                                    s, ms = map(float, s_ms.split('.'))
                                    current_time = int(h) * 3600 + int(m) * 60 + s + ms / 1000.0
                                else:
                                     # Handle cases where time might just be seconds (less common for progress)
                                     current_time = float(time_str)

                                percentage = min(100.0, (current_time / total_duration) * 100.0) if total_duration > 0 else 0.0
                                fps = progress_data.get('fps', '0')
                                speed = progress_data.get('speed', '0x').replace('x', '')

                                # Get current output file size (can be None if file not accessible)
                                current_output_size = None
                                try:
                                    if target_path.exists():
                                        current_output_size = target_path.stat().st_size
                                except OSError:
                                    pass # Ignore if we can't stat the file during processing

                                # Update DB (non-blocking if possible)
                                update_task_progress(task_id, percentage, current_time, current_output_size)
                                # Update Rich progress bar
                                progress_callback(current_time, percentage, fps, speed, current_output_size)

                            except ValueError as e:
                                logging.warning(f"Task {task_id}: Could not parse time value '{time_str}': {e}")
                            except Exception as e:
                                logging.warning(f"Task {task_id}: Error processing progress line: {e}")


            # Check if process terminated unexpectedly
            if process.poll() is not None:
                break
            # Small sleep to avoid busy-waiting
            # time.sleep(0.1)


        # --- Check Final Status ---
        process.wait() # Ensure process is finished and get return code
        elapsed_time = time.time() - start_time

        if process.returncode == 0:
            logging.info(f"Task {task_id}: Transcode completed successfully in {elapsed_time:.2f} seconds.")
            final_size = target_path.stat().st_size
            update_task_status(task_id, 'completed')
            add_transcoded_file(task_id, target_path, final_size)
            # Final progress update to 100%
            progress_callback(total_duration, 100.0, 'N/A', 'N/A', final_size)
            return True, target_path, None
        else:
            logging.error(f"Task {task_id}: FFmpeg process failed with return code {process.returncode}.")
            # Read stderr for error details
            error_output = "Unknown error"
            if process.stderr:
                try:
                    # Read the rest of stderr
                    error_output = process.stderr.read()
                    if not error_output: # Sometimes error is on stdout on failure
                        process.stdout.seek(0)
                        error_output = process.stdout.read()
                except Exception as e:
                    error_output = f"Could not read stderr: {e}"

            logging.error(f"Task {task_id}: Error output:\n{error_output[:1000]}...") # Log first 1KB
            update_task_status(task_id, 'failed', f"FFmpeg exited with code {process.returncode}. Error: {error_output[:500]}") # Truncate error for DB
            # Clean up potentially partial output file
            try:
                target_path.unlink(missing_ok=True)
                logging.info(f"Task {task_id}: Removed potentially incomplete output file: {target_path}")
            except OSError as e:
                logging.warning(f"Task {task_id}: Could not remove incomplete output file {target_path}: {e}")
            return False, None, f"FFmpeg exited with code {process.returncode}. Error: {error_output[:500]}" # Return error message

    except FileNotFoundError:
        logging.error("ffmpeg command not found. Please ensure ffmpeg is installed and in your PATH.")
        update_task_status(task_id, 'failed', 'ffmpeg not found')
        return False, None, "ffmpeg not found"
    except Exception as e:
        logging.exception(f"Task {task_id}: An unexpected error occurred during transcoding: {e}")
        if process and process.poll() is None:
            process.kill() # Ensure ffmpeg is killed on unexpected error
        update_task_status(task_id, 'failed', f"Unexpected error: {e}")
        return False, None, f"Unexpected error: {e}"
    finally:
        # Clear global state when done with this task
        current_process = None
        current_task_id = None

