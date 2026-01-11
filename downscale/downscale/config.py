# downscale/config.py
import os
import argparse
from pathlib import Path
import logging

# --- Configuration Class ---
class Config:
    """Holds application configuration."""
    # Move constants into the class
    APP_NAME = "downscale"
    DEFAULT_THRESHOLD_GB = 10.0
    DEFAULT_DB_SUBPATH = Path(".cache") / APP_NAME / f"{APP_NAME}.db"
    DEFAULT_LOG_SUBPATH = Path(".cache") / APP_NAME / "logs"
    DEFAULT_SOURCE_DIR = Path("/mnt/Puddle/Media/Movies")
    DEFAULT_OUTPUT_DIR = Path("/mnt/Puddle/Media/Transcodes")
    VIDEO_EXTENSIONS = {".mkv", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm"}
    BYTES_PER_GB = 1024 * 1024 * 1024

    def __init__(self):
        self.threshold_bytes: int = int(self.DEFAULT_THRESHOLD_GB * self.BYTES_PER_GB)
        self.source_dir: Path = self.DEFAULT_SOURCE_DIR
        self.output_dir: Path = self.DEFAULT_OUTPUT_DIR
        self.db_path: Path = Path.home() / self.DEFAULT_DB_SUBPATH
        self.log_dir: Path = Path.home() / self.DEFAULT_LOG_SUBPATH
        self.dry_run: bool = False
        self.skip_confirmation: bool = False
        self.continue_on_failure: bool = False

    def parse_args(self):
        """Parses command line arguments and updates configuration."""
        parser = argparse.ArgumentParser(
            description="Scans a directory for large movie files and transcodes them.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )

        parser.add_argument(
            "-t", "--threshold",
            type=float,
            default=self.DEFAULT_THRESHOLD_GB,
            help="Size threshold in GB. Files larger than this will be queued for transcoding."
        )
        parser.add_argument(
            "-s", "--source",
            type=Path,
            default=self.source_dir,
            help="Source directory containing movie folders."
        )
        parser.add_argument(
            "-o", "--output",
            type=Path,
            default=self.output_dir,
            help="Output directory where transcoded files will be stored."
        )
        parser.add_argument(
            "--db",
            type=Path,
            default=self.db_path,
            help="Path to the SQLite database file."
        )
        parser.add_argument(
            "--log",
            type=Path,
            default=self.log_dir,
            help="Directory to store log files."
        )
        parser.add_argument(
            "-d", "--dry-run",
            action="store_true",
            default=False,
            help="Scan and identify files to transcode, but do not perform transcoding."
        )
        parser.add_argument(
            "-y", "--yes",
            action="store_true",
            default=False,
            help="Skip confirmation prompt before starting transcoding."
        )
        parser.add_argument(
            "-c", "--continue-on-failure",
            action="store_true",
            default=False,
            help="Continue processing tasks even if one fails."
        )

        args = parser.parse_args()

        self.threshold_bytes = int(args.threshold * self.BYTES_PER_GB)
        self.source_dir = args.source.resolve() # Use absolute paths
        self.output_dir = args.output.resolve()
        self.db_path = args.db.resolve()
        self.log_dir = args.log.resolve()
        self.dry_run = args.dry_run
        self.skip_confirmation = args.yes
        self.continue_on_failure = args.continue_on_failure

        # Basic validation
        if not Path.home().exists():
            print(f"ERROR: Home directory '{Path.home()}' not found.")
            exit(1)
        if not self.source_dir.is_dir():
            print(f"ERROR: Source directory '{self.source_dir}' not found or is not a directory.")
            exit(1)

        # Ensure parent directories for db and log exist if using defaults or custom paths
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logging.info("Configuration loaded:")
        logging.info(f"  Threshold: {args.threshold} GB ({self.threshold_bytes} bytes)")
        logging.info(f"  Source Dir: {self.source_dir}")
        logging.info(f"  Output Dir: {self.output_dir}")
        logging.info(f"  Database: {self.db_path}")
        logging.info(f"  Log Dir: {self.log_dir}")
        logging.info(f"  Dry Run: {self.dry_run}")
        logging.info(f"  Skip Confirmation: {self.skip_confirmation}")
        logging.info(f"  Continue on Failure: {self.continue_on_failure}")

# --- Global Config Instance ---
# This instance can be imported by other modules
cfg = Config()

