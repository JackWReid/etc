# downscale/main.py
import sys
import logging
import signal
import time
from pathlib import Path
from typing import Optional, Dict, Any, List # Added Optional

# Import necessary components from the package
from . import config, log_setup, database, scanner, tasks, transcoder, ui

# Flag to indicate if shutdown is requested
shutdown_requested = False

def handle_shutdown_signal(sig, frame):
    """Sets the shutdown flag when SIGINT or SIGTERM is received."""
    global shutdown_requested
    logging.warning(f"Received signal {sig}. Requesting graceful shutdown...")
    ui.console.print("\n[bold yellow]Shutdown requested. Finishing current task and exiting...[/bold yellow]")
    shutdown_requested = True
    # Also signal the transcoder process if it's running
    transcoder.request_shutdown()

def main():
    """Main execution function for the downscale application."""
    global shutdown_requested
    # 1. Parse Arguments & Load Configuration
    # The cfg object is loaded when config.py is imported and parsed here
    try:
        config.cfg.parse_args()
    except Exception as e:
        print(f"Error parsing arguments: {e}", file=sys.stderr)
        sys.exit(1)

    # 2. Setup Logging
    try:
        log_setup.setup_logging()
    except Exception as e:
        print(f"Error setting up logging: {e}", file=sys.stderr)
        # Continue without logging if setup fails, but warn user
        logging.basicConfig(level=logging.WARNING) # Basic fallback
        logging.warning("Logging setup failed, using basic console logging.")

    logging.info(f"--- {config.cfg.APP_NAME} execution started ---")
    logging.info(f"Arguments: {sys.argv}")
    logging.info(f"Effective Configuration: {config.cfg}") # Log effective config

    # 3. Initialize Database
    try:
        database.init_db()
    except Exception as e:
        logging.critical(f"Failed to initialize database at {config.cfg.db_path}. Cannot continue. Error: {e}")
        sys.exit(1)

    # 4. Scan Source Directory
    try:
        scanner.scan_source_directory()
    except Exception as e:
        logging.error(f"Failed during source directory scan: {e}")
        # Decide if this is critical - perhaps continue if DB has old data?
        # For now, let's exit if scan fails badly.
        sys.exit(1)

    # 5. Identify and Create Tasks
    tasks_to_process_details: List[Dict[str, Any]] = []
    try:
        # Get tasks that are pending or were interrupted
        tasks_to_process_details = database.get_pending_or_interrupted_tasks()

        # If no tasks are pending/interrupted, check if new ones should be created
        if not tasks_to_process_details:
            logging.info("No pending or interrupted tasks found. Checking for new files exceeding threshold...")
            # This call finds large files, checks existing tasks/completions, and creates NEW tasks if needed.
            tasks.create_transcode_tasks()
            # Re-fetch the tasks that are now ready
            tasks_to_process_details = database.get_pending_or_interrupted_tasks()

        # Prepare data for UI confirmation table
        tasks_for_ui = []
        if tasks_to_process_details:
            logging.info(f"Found {len(tasks_to_process_details)} tasks to process.")
            for task_row in tasks_to_process_details:
                tasks_for_ui.append({
                    'task_id': task_row['id'],
                    'source_path': Path(task_row['source_path']),
                    'source_size_bytes': task_row['source_size_bytes'],
                    'status': task_row['status'] # Include status for display
                })
        else:
            logging.info("No tasks require processing after check.")
            ui.console.print("[green]All files are within threshold or already transcoded/processed.[/green]")
            logging.info(f"--- {config.cfg.APP_NAME} execution finished ---")
            sys.exit(0)

    except Exception as e:
        logging.exception("Failed during task identification or creation.")
        sys.exit(1)

    # 6. Display Confirmation & Handle Dry Run
    if not ui.display_tasks_confirmation(tasks_for_ui):
        # This handles dry run exit or user cancellation
        logging.info("Exiting based on user confirmation or dry run setting.")
        logging.info(f"--- {config.cfg.APP_NAME} execution finished ---")
        sys.exit(0)

    # --- Proceed with Transcoding ---
    logging.info("User confirmed. Starting transcoding process...")

    # 7. Setup Signal Handling for graceful shutdown
    signal.signal(signal.SIGINT, handle_shutdown_signal)
    signal.signal(signal.SIGTERM, handle_shutdown_signal)

    # 8. Setup Progress Bars
    progress = ui.setup_progress_bars()
    overall_task = progress.add_task("[bold green]Overall Progress", total=len(tasks_to_process_details), speed_str="", size_str="")
    current_task_progress = None # To hold the TaskID for the current file

    # 9. Execute Transcode Tasks
    errors_occurred = False
    tasks_completed_count = 0
    tasks_failed_count = 0
    tasks_interrupted_count = 0
    start_time_overall = time.time()

    with progress: # Start rendering the progress bars
        for i, task_row in enumerate(tasks_to_process_details):
            if shutdown_requested:
                logging.warning("Shutdown requested, stopping task processing loop.")
                tasks_interrupted_count += (len(tasks_to_process_details) - i) # Count remaining as interrupted
                break # Exit the loop

            task_id = task_row['id']
            source_path = Path(task_row['source_path'])
            total_duration = task_row['duration_seconds']
            target_dir = Path(task_row['target_directory'])
            target_sub_dir = task_row['target_sub_directory']
            target_filename = task_row['target_filename']
            target_path = target_dir / target_sub_dir / target_filename

            # Ensure duration is available (should have been fetched during task creation)
            if not total_duration:
                 # Attempt to fetch duration again if missing (shouldn't happen ideally)
                 logging.warning(f"Duration missing for task {task_id}, attempting ffprobe again.")
                 total_duration = tasks.run_ffprobe(source_path)
                 if total_duration:
                     # Need source_file_id to update duration
                     source_file_id = database.get_source_file_id(str(source_path))
                     if source_file_id:
                         database.update_source_file_duration(source_file_id, total_duration)
                     else:
                         logging.error(f"Could not find source_file_id for {source_path} to update duration.")
                         # Continue without duration, ffmpeg might still work but progress % will be wrong
                 else:
                     logging.error(f"Cannot process task {task_id} ('{source_path.name}'): Failed to get duration.")
                     database.update_task_status(task_id, 'failed', 'Failed to get duration')
                     errors_occurred = True
                     tasks_failed_count += 1
                     progress.update(overall_task, advance=1, speed_str="Failed") # Advance overall progress even on failure
                     continue # Skip to next task

            ui.console.print(f"\n[bold blue]Processing Task {i+1}/{len(tasks_to_process_details)}: {source_path.name} (ID: {task_id})[/bold blue]")

            # Add specific progress bar for this task
            if current_task_progress is not None:
                 progress.remove_task(current_task_progress) # Remove previous file's bar

            current_task_progress = progress.add_task(
                 f"[cyan]{source_path.name}",
                 total=100.0, # Progress is percentage based
                 start=False, # Start manually after setup
                 speed_str="0 FPS @ 0.0x",
                 size_str="0 B"
            )
            progress.start_task(current_task_progress)

            # --- Callback function for the transcoder to update Rich progress ---
            def progress_updater(current_time_secs: float, percentage: float, fps: str, speed: str, output_size: Optional[int]):
                """Updates the Rich progress bar for the current transcode task."""
                if current_task_progress is not None:
                    # Ensure percentage doesn't exceed 100 visually
                    display_percentage = min(percentage, 100.0)
                    speed_str_val = f"{float(fps):>5.1f} FPS @ {float(speed):>4.2f}x" if fps != 'N/A' and speed != 'N/A' else "Starting..."
                    size_str_val = ui.format_size(output_size) if output_size is not None else "N/A"
                    progress.update(current_task_progress,
                                    completed=display_percentage,
                                    speed_str=speed_str_val,
                                    size_str=size_str_val)
            # --- End of callback function ---

            try:
                logging.info(f"Starting transcode for task {task_id}: {source_path} -> {target_path}")
                database.update_task_status(task_id, 'processing')

                # Execute the transcode
                success, final_size, error_message = transcoder.run_ffmpeg_transcode(
                    task_id=task_id,
                    source_path=source_path,
                    target_path=target_path,
                    total_duration=total_duration, # Pass duration for percentage calc
                    progress_callback=progress_updater
                )

                if shutdown_requested:
                    logging.warning(f"Task {task_id} interrupted by shutdown signal.")
                    database.update_task_status(task_id, 'interrupted', 'Shutdown requested')
                    tasks_interrupted_count += 1
                elif success:
                    logging.info(f"Task {task_id} completed successfully. Output size: {ui.format_size(final_size)}")
                    database.update_task_status(task_id, 'completed', final_size=final_size)
                    tasks_completed_count += 1
                    progress.update(current_task_progress, completed=100.0, description=f"[green]{source_path.name} (Done)", speed_str="", size_str=ui.format_size(final_size))
                else:
                    logging.error(f"Task {task_id} failed: {error_message}")
                    database.update_task_status(task_id, 'failed', error_message)
                    errors_occurred = True
                    tasks_failed_count += 1
                    progress.update(current_task_progress, description=f"[red]{source_path.name} (Failed)", speed_str="", size_str="")
                    if not config.cfg.continue_on_failure:
                        logging.error("Exiting due to task failure (continue-on-failure flag not set).")
                        break # Exit the loop if continue-on-failure is not enabled

            except Exception as e:
                logging.exception(f"Unexpected error during transcoding task {task_id} for {source_path.name}")
                database.update_task_status(task_id, 'failed', f"Unexpected error: {e}")
                errors_occurred = True
                tasks_failed_count += 1
                progress.update(current_task_progress, description=f"[red]{source_path.name} (Error)", speed_str="", size_str="")
                if not config.cfg.continue_on_failure:
                    logging.error("Exiting due to unexpected error (continue-on-failure flag not set).")
                    break # Exit the loop if continue-on-failure is not enabled
            finally:
                # Advance overall progress regardless of outcome for this task
                progress.update(overall_task, advance=1)
                # Ensure the specific task bar is marked as finished or removed if needed
                if current_task_progress is not None and not progress.tasks[current_task_progress].finished:
                     progress.update(current_task_progress, completed=100.0) # Mark as visually complete
                     # Optionally remove the task bar after a short delay or keep it static
                     # progress.remove_task(current_task_progress)
                     # current_task_progress = None


    # 10. Final Summary
    end_time_overall = time.time()
    total_duration_secs = end_time_overall - start_time_overall
    total_duration_str = time.strftime("%H:%M:%S", time.gmtime(total_duration_secs))

    ui.console.print("\n" + "="*30 + " Transcoding Summary " + "="*30)
    ui.console.print(f"Total execution time: {total_duration_str}")
    ui.console.print(f"Tasks processed: {tasks_completed_count + tasks_failed_count + tasks_interrupted_count}/{len(tasks_to_process_details)}")
    ui.console.print(f"[green]  Completed: {tasks_completed_count}[/green]")
    ui.console.print(f"[red]  Failed: {tasks_failed_count}[/red]")
    if tasks_interrupted_count > 0:
         ui.console.print(f"[yellow]  Interrupted/Remaining: {tasks_interrupted_count}[/yellow]")
    ui.console.print("="*79)

    logging.info(f"--- {config.cfg.APP_NAME} execution finished ---")
    logging.info(f"Summary: Completed={tasks_completed_count}, Failed={tasks_failed_count}, Interrupted={tasks_interrupted_count}, TotalTime={total_duration_str}")

    # Exit with error code if any tasks failed or if shutdown was requested mid-process
    if errors_occurred or shutdown_requested:
        sys.exit(1)
    else:
        sys.exit(0)


# Entry point for the application
if __name__ == "__main__":
    main()
