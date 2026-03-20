from __future__ import annotations

import typer

from shellclaw.config.paths import DEFAULT_SANDBOX_NAME
from shellclaw.core.sandbox import connect_sandbox


def connect(
    sandbox_name: str = typer.Option(DEFAULT_SANDBOX_NAME, help="Sandbox name"),
) -> None:
    """Connect to a running sandbox shell."""
    exit_code = connect_sandbox(sandbox_name)
    raise typer.Exit(exit_code)
