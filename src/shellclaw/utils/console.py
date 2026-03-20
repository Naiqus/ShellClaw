from __future__ import annotations

from rich.console import Console
from rich.table import Table

console = Console()


def log_info(msg: str) -> None:
    console.print(f"[blue][INFO][/blue] {msg}")


def log_success(msg: str) -> None:
    console.print(f"[green][OK][/green] {msg}")


def log_warning(msg: str) -> None:
    console.print(f"[yellow][WARN][/yellow] {msg}")


def log_error(msg: str) -> None:
    console.print(f"[red][ERROR][/red] {msg}")


def log_step(step: int, total: int, msg: str) -> None:
    console.print(f"[cyan][{step}/{total}][/cyan] {msg}")


def create_status_table(title: str, columns: list[str], rows: list[list[str]]) -> Table:
    table = Table(title=title)
    for col in columns:
        table.add_column(col)
    for row in rows:
        table.add_row(*row)
    return table
