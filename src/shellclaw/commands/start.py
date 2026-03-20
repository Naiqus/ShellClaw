from __future__ import annotations

import typer

from shellclaw.config.paths import DEFAULT_SANDBOX_NAME
from shellclaw.core.gateway import is_gateway_running, start_gateway
from shellclaw.core.sandbox import start_sandbox
from shellclaw.utils.console import log_error, log_info, log_success


def start(
    sandbox_name: str = typer.Option(DEFAULT_SANDBOX_NAME, help="Sandbox name"),
) -> None:
    """Start a sandbox and its agent."""
    if not is_gateway_running():
        log_info("Gateway not running, starting it...")
        if not start_gateway():
            log_error("Failed to start gateway")
            raise typer.Exit(1)
        log_success("Gateway started")

    if not start_sandbox(sandbox_name):
        log_error(f"Failed to start sandbox '{sandbox_name}'")
        raise typer.Exit(1)

    log_success(f"Sandbox '{sandbox_name}' started")
