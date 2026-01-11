# downscale/log_setup.py
import logging
import logging.handlers
import sys
from pathlib import Path

from .config import cfg # Import the global config instance

def setup_logging():
    """Configures logging to file and console."""
    log_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(module)s:%(lineno)d] - %(message)s'
    )
    log_file = cfg.log_dir / f"{cfg.APP_NAME}.log"

    # --- File Handler (Rotating) ---
    try:
        # Rotate logs, keep 5 backups, max 10MB each
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8'
        )
        file_handler.setFormatter(log_formatter)
        file_handler.setLevel(logging.INFO) # Log INFO level and above to file
    except Exception as e:
        print(f"Error setting up file logger at {log_file}: {e}", file=sys.stderr)
        # Continue without file logging if setup fails
        file_handler = None

    # --- Console Handler ---
    # We will use Rich for most console output, but basic logging is good too
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.WARNING) # Log WARNING level and above to console by default

    # --- Root Logger Configuration ---
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO) # Set root logger level to lowest level needed
    root_logger.handlers.clear() # Remove default handlers if any
    if file_handler:
        root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    logging.info("Logging initialized.")
    if file_handler:
        logging.info(f"Logging to file: {log_file}")
    else:
        logging.warning("File logging disabled due to setup error.")

