# downscale/ui.py
import time
from typing import List, Dict, Any, Optional
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    SpinnerColumn,
    TaskProgressColumn,
)
from rich.text import Text

from .config import cfg

console = Console()

def display_tasks_confirmation(tasks_to_process: List[Dict[str, Any]]):
    """
    Displays a table of tasks that will be processed and asks for confirmation.

    Args:
        tasks_to_process: A list of dictionaries, each representing a task.
                          Expected keys: 'task_id', 'source_path', 'source_size_bytes', 'status'.

    Returns:
        bool: True if the user confirms, False otherwise.
    """
    if not tasks_to_process:
        console.print("[yellow]No tasks identified for processing.[/yellow]")
        return False

    table = Table(title="Tasks to Process", show_header=True, header_style="bold magenta")
    table.add_column("Source File", style="dim", width=50)
    table.add_column("Size (GB)", justify="right")
    table.add_column("Status", justify="center")
    table.add_column("Task ID", justify="right")

    total_size_gb = 0
    for task in tasks_to_process:
        source_path = Path(task['source_path'])
        size_gb = task['source_size_bytes'] / cfg.BYTES_PER_GB
        total_size_gb += size_gb
        status = task['status']
        color = "yellow" if status == "pending" else "cyan" if status == "interrupted" else "white"
        table.add_row(
            source_path.name,
            f"{size_gb:.2f}",
            Text(status.capitalize(), style=color),
            str(task['task_id'])
        )

    console.print(table)
    console.print(f"\n[bold]Total files:[/bold] {len(tasks_to_process)}")
    console.print(f"[bold]Total size:[/bold] {total_size_gb:.2f} GB")

    if cfg.dry_run:
        console.print("\n[cyan][Dry Run][/cyan] No changes will be made.")
        return False # Don't proceed in dry run

    if cfg.skip_confirmation:
        console.print("\n[yellow]Skipping confirmation due to -y flag.[/yellow]")
        return True

    try:
        confirm = console.input("\n[bold yellow]Proceed with transcoding? (y/N): [/bold yellow]").lower()
        return confirm == 'y'
    except (KeyboardInterrupt, EOFError):
        console.print("\n[red]Operation cancelled by user.[/red]")
        return False


def setup_progress_bars() -> Progress:
    """Creates and returns a Rich Progress instance with standard columns."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(), # Percentage e.g. "[progress.percentage]{task.percentage:>3.0f}%"
        TimeRemainingColumn(),
        TimeElapsedColumn(),
        # TextColumn("[progress.filesize]{task.fields[size_str]}"), # Custom field for size
        TextColumn("[cyan]{task.fields[speed_str]}"), # Custom field for speed
        console=console,
        transient=False # Keep progress bars visible after completion
    )

def format_size(size_bytes: Optional[int]) -> str:
    """Formats bytes into a human-readable string (KB, MB, GB)."""
    if size_bytes is None:
        return "N/A"
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/1024**2:.1f} MB"
    else:
        return f"{size_bytes/1024**3:.2f} GB"

