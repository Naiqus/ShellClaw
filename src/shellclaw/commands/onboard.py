from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from shellclaw.config.paths import DEFAULT_POLICY_PATH, DEFAULT_SANDBOX_NAME
from shellclaw.core.gateway import start_gateway
from shellclaw.core.inference import set_inference
from shellclaw.core.sandbox import create_sandbox
from shellclaw.utils.console import log_error, log_step, log_success
from shellclaw.utils.validators import validate_docker_available, validate_openshell_available


def onboard(
    inference_provider: str = typer.Option("ollama", help="Inference provider"),
    inference_model: str = typer.Option("llama3", help="Model name"),
    inference_url: str = typer.Option("http://localhost:11434", help="Inference endpoint URL"),
    sandbox_name: str = typer.Option(DEFAULT_SANDBOX_NAME, help="Sandbox name"),
    policy: Optional[Path] = typer.Option(None, help="Custom policy YAML path"),
) -> None:
    """One-click initialization: start gateway, configure inference, create sandbox."""
    total = 4

    # Step 1: Validate prerequisites
    log_step(1, total, "Validating prerequisites...")
    ok, err = validate_docker_available()
    if not ok:
        log_error(err or "Docker validation failed")
        raise typer.Exit(1)

    ok, err = validate_openshell_available()
    if not ok:
        log_error(err or "OpenShell validation failed")
        raise typer.Exit(1)
    log_success("Prerequisites validated")

    # Step 2: Start gateway
    log_step(2, total, "Starting gateway...")
    if not start_gateway():
        log_error("Failed to start gateway")
        raise typer.Exit(1)
    log_success("Gateway started")

    # Step 3: Configure inference routing
    log_step(3, total, "Configuring inference routing...")
    if not set_inference(inference_provider, inference_model, inference_url):
        log_error("Failed to configure inference routing")
        raise typer.Exit(1)
    log_success(f"Inference routed to {inference_provider}/{inference_model}")

    # Step 4: Create sandbox
    log_step(4, total, "Creating sandbox...")
    policy_path = policy or DEFAULT_POLICY_PATH
    if not create_sandbox(sandbox_name, policy_path=policy_path):
        log_error("Failed to create sandbox")
        raise typer.Exit(1)
    log_success(f"Sandbox '{sandbox_name}' created")

    log_success("Onboarding complete! Use 'shellclaw connect' to enter the sandbox.")
