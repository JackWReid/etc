# downscale/database.py
import sqlite3
import logging
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, List, Tuple, Dict, Any

from .config import cfg

# --- Database Schema ---
# (Copied from the SQL immersive for reference within the code)
DB_SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS source_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE NOT NULL,
    file_name TEXT NOT NULL,
    directory_name TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    duration_seconds REAL,
    scanned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_source_files_file_path ON source_files (file_path);
CREATE INDEX IF NOT EXISTS idx_source_files_directory_name ON source_files (directory_name);

CREATE TABLE IF NOT EXISTS transcode_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file_id INTEGER NOT NULL,
    target_directory TEXT NOT NULL,
    target_sub_directory TEXT NOT NULL,
    target_filename TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('pending', 'running', 'completed', 'failed', 'interrupted')) DEFAULT 'pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    ffmpeg_pid INTEGER,
    progress_percentage REAL DEFAULT 0.0,
    current_timestamp_seconds REAL,
    transcoded_size_bytes INTEGER,
    error_message TEXT,
    FOREIGN KEY (source_file_id) REFERENCES source_files (id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_transcode_tasks_status ON transcode_tasks (status);
CREATE INDEX IF NOT EXISTS idx_transcode_tasks_source_file_id ON transcode_tasks (source_file_id);

CREATE TABLE IF NOT EXISTS transcoded_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL UNIQUE,
    file_path TEXT UNIQUE NOT NULL,
    size_bytes INTEGER NOT NULL,
    transcoded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES transcode_tasks (id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_transcoded_files_file_path ON transcoded_files (file_path);
CREATE INDEX IF NOT EXISTS idx_transcoded_files_task_id ON transcoded_files (task_id);
"""

# --- Database Connection Context Manager ---
@contextmanager
def db_connect(db_path: Path = cfg.db_path):
    """Provides a transactional scope around a series of operations."""
    conn = None
    try:
        logging.debug(f"Connecting to database: {db_path}")
        conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        conn.row_factory = sqlite3.Row # Access columns by name
        conn.execute("PRAGMA foreign_keys = ON;") # Ensure FKs are enforced
        yield conn.cursor()
        conn.commit()
        logging.debug("Database transaction committed.")
    except sqlite3.Error as e:
        logging.error(f"Database error: {e}")
        if conn:
            conn.rollback()
            logging.warning("Database transaction rolled back.")
        raise # Re-raise the exception
    finally:
        if conn:
            conn.close()
            logging.debug("Database connection closed.")

# --- Initialization ---
def init_db():
    """Initializes the database by creating tables if they don't exist."""
    try:
        with db_connect() as cur:
            logging.info(f"Initializing database schema in {cfg.db_path}...")
            cur.executescript(DB_SCHEMA)
            logging.info("Database schema initialized successfully.")
    except sqlite3.Error as e:
        logging.error(f"Failed to initialize database schema: {e}")
        raise

# --- Source File Operations ---
def add_or_update_source_file(file_path: Path, size_bytes: int, last_modified: float):
    """Adds a new source file or updates its size/timestamp if changed."""
    sql = """
    INSERT INTO source_files (file_path, file_name, directory_name, size_bytes, last_modified)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(file_path) DO UPDATE SET
        size_bytes = excluded.size_bytes,
        last_modified = excluded.last_modified,
        scanned_at = CURRENT_TIMESTAMP
    WHERE size_bytes != excluded.size_bytes OR last_modified != excluded.last_modified;
    """
    try:
        with db_connect() as cur:
            cur.execute(sql, (
                str(file_path),
                file_path.name,
                file_path.parent.name, # Assumes structure Movie (Year)/file.mkv
                size_bytes,
                last_modified # Store as timestamp
            ))
            if cur.rowcount > 0:
                 logging.debug(f"Added/Updated source file: {file_path}")
            else:
                 logging.debug(f"Source file unchanged: {file_path}")

    except sqlite3.Error as e:
        logging.error(f"Error adding/updating source file {file_path}: {e}")

def get_source_file_id(file_path: Path) -> Optional[int]:
    """Gets the ID of a source file by its path."""
    sql = "SELECT id FROM source_files WHERE file_path = ?;"
    try:
        with db_connect() as cur:
            cur.execute(sql, (str(file_path),))
            row = cur.fetchone()
            return row['id'] if row else None
    except sqlite3.Error as e:
        logging.error(f"Error getting source file ID for {file_path}: {e}")
        return None

def get_large_source_files(threshold_bytes: int) -> List[sqlite3.Row]:
    """Gets source files larger than the specified threshold."""
    sql = """
    SELECT id, file_path, size_bytes, duration_seconds
    FROM source_files
    WHERE size_bytes > ?;
    """
    try:
        with db_connect() as cur:
            cur.execute(sql, (threshold_bytes,))
            return cur.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error fetching large source files: {e}")
        return []

def update_source_file_duration(file_id: int, duration: float):
    """Updates the duration for a specific source file."""
    sql = "UPDATE source_files SET duration_seconds = ? WHERE id = ?;"
    try:
        with db_connect() as cur:
            cur.execute(sql, (duration, file_id))
            logging.info(f"Updated duration for source file ID {file_id} to {duration:.2f}s")
    except sqlite3.Error as e:
        logging.error(f"Error updating duration for source file ID {file_id}: {e}")


# --- Transcode Task Operations ---
def add_transcode_task(source_file_id: int, target_dir: Path, target_sub_dir: str, target_filename: str) -> Optional[int]:
    """Adds a new transcode task in 'pending' state."""
    sql = """
    INSERT INTO transcode_tasks (source_file_id, target_directory, target_sub_directory, target_filename, status)
    VALUES (?, ?, ?, ?, 'pending');
    """
    try:
        with db_connect() as cur:
            cur.execute(sql, (source_file_id, str(target_dir), target_sub_dir, target_filename))
            task_id = cur.lastrowid
            logging.info(f"Added transcode task ID {task_id} for source file ID {source_file_id}")
            return task_id
    except sqlite3.IntegrityError:
         logging.warning(f"Task for source file ID {source_file_id} might already exist or FK constraint failed.")
         return None # Or handle differently if needed
    except sqlite3.Error as e:
        logging.error(f"Error adding transcode task for source file ID {source_file_id}: {e}")
        return None

def get_task_by_source_id(source_file_id: int) -> Optional[sqlite3.Row]:
    """Checks if a task (any status) exists for a given source file ID."""
    sql = "SELECT id, status FROM transcode_tasks WHERE source_file_id = ?;"
    try:
        with db_connect() as cur:
            cur.execute(sql, (source_file_id,))
            return cur.fetchone()
    except sqlite3.Error as e:
        logging.error(f"Error checking task for source file ID {source_file_id}: {e}")
        return None

def get_pending_or_interrupted_tasks() -> List[sqlite3.Row]:
    """Gets tasks that are ready to be processed."""
    sql = """
    SELECT t.id, t.status, t.target_directory, t.target_sub_directory, t.target_filename,
           s.file_path AS source_path, s.size_bytes AS source_size_bytes, s.duration_seconds
    FROM transcode_tasks t
    JOIN source_files s ON t.source_file_id = s.id
    WHERE t.status IN ('pending', 'interrupted');
    """
    try:
        with db_connect() as cur:
            cur.execute(sql)
            return cur.fetchall()
    except sqlite3.Error as e:
        logging.error(f"Error fetching pending/interrupted tasks: {e}")
        return []

def update_task_status(task_id: int, status: str, error_message: Optional[str] = None):
    """Updates the status of a task."""
    sql = "UPDATE transcode_tasks SET status = ?, error_message = ?, completed_at = CASE WHEN ? IN ('completed', 'failed') THEN CURRENT_TIMESTAMP ELSE completed_at END WHERE id = ?;"
    try:
        with db_connect() as cur:
            cur.execute(sql, (status, error_message, status, task_id))
            logging.info(f"Updated task ID {task_id} status to {status}")
    except sqlite3.Error as e:
        logging.error(f"Error updating status for task ID {task_id}: {e}")

def update_task_start(task_id: int, pid: int):
    """Marks a task as started and stores the PID."""
    sql = "UPDATE transcode_tasks SET status = 'running', started_at = CURRENT_TIMESTAMP, ffmpeg_pid = ? WHERE id = ?;"
    try:
        with db_connect() as cur:
            cur.execute(sql, (pid, task_id))
            logging.info(f"Started task ID {task_id} with PID {pid}")
    except sqlite3.Error as e:
        logging.error(f"Error marking task ID {task_id} as started: {e}")

def update_task_progress(task_id: int, percentage: float, current_time: float, output_size: Optional[int]):
    """Updates the progress details of a running task."""
    sql = """
    UPDATE transcode_tasks
    SET progress_percentage = ?, current_timestamp_seconds = ?, transcoded_size_bytes = ?
    WHERE id = ? AND status = 'running';
    """
    try:
        with db_connect() as cur:
            # Use a separate connection for progress updates to avoid blocking main transaction
            conn_progress = sqlite3.connect(cfg.db_path, timeout=10) # Increase timeout for progress updates
            cur_progress = conn_progress.cursor()
            cur_progress.execute(sql, (percentage, current_time, output_size, task_id))
            conn_progress.commit()
            conn_progress.close()
            # Minimal logging for progress to avoid flooding logs
            # logging.debug(f"Updated progress for task ID {task_id}: {percentage:.1f}%")
    except sqlite3.Error as e:
        # Log progress errors less verbosely
        logging.warning(f"Error updating progress for task ID {task_id}: {e}")


# --- Transcoded File Operations ---
def add_transcoded_file(task_id: int, file_path: Path, size_bytes: int):
    """Adds a record for a successfully transcoded file."""
    sql = """
    INSERT INTO transcoded_files (task_id, file_path, size_bytes)
    VALUES (?, ?, ?);
    """
    try:
        with db_connect() as cur:
            cur.execute(sql, (task_id, str(file_path), size_bytes))
            logging.info(f"Added transcoded file record for task ID {task_id}: {file_path}")
    except sqlite3.IntegrityError:
         logging.warning(f"Transcoded file record for task {task_id} or path {file_path} already exists.")
    except sqlite3.Error as e:
        logging.error(f"Error adding transcoded file for task ID {task_id}: {e}")

def get_transcoded_path_for_source(source_file_id: int) -> Optional[str]:
    """Checks if a completed transcoded file exists for a source file."""
    sql = """
    SELECT tf.file_path
    FROM transcoded_files tf
    JOIN transcode_tasks tt ON tf.task_id = tt.id
    WHERE tt.source_file_id = ?;
    """
    # Alternative: Check task status = 'completed' directly
    # sql_alt = "SELECT target_directory, target_sub_directory, target_filename FROM transcode_tasks WHERE source_file_id = ? AND status = 'completed';"
    try:
        with db_connect() as cur:
            cur.execute(sql, (source_file_id,))
            row = cur.fetchone()
            return row['file_path'] if row else None
    except sqlite3.Error as e:
        logging.error(f"Error checking transcoded file for source ID {source_file_id}: {e}")
        return None

