from __future__ import annotations

import typer

from shellclaw.config.paths import DEFAULT_SANDBOX_NAME
from shellclaw.core.gateway import stop_gateway
from shellclaw.core.sandbox import delete_sandbox
from shellclaw.utils.console import log_error, log_success


def stop(
    sandbox_name: str = typer.Option(DEFAULT_SANDBOX_NAME, help="Sandbox name"),
    gateway: bool = typer.Option(False, help="Also stop the gateway"),
) -> None:
    """Stop a sandbox and optionally the gateway."""
    if not delete_sandbox(sandbox_name):
        log_error(f"Failed to stop sandbox '{sandbox_name}'")
        raise typer.Exit(1)
    log_success(f"Sandbox '{sandbox_name}' stopped")

    if gateway:
        if not stop_gateway():
            log_error("Failed to stop gateway")
            raise typer.Exit(1)
        log_success("Gateway stopped")
