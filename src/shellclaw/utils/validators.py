from __future__ import annotations

import re
import subprocess
from pathlib import Path


def validate_docker_available() -> tuple[bool, str | None]:
    """Check that Docker daemon is reachable."""
    try:
        subprocess.run(
            ["docker", "info"],
            capture_output=True,
            check=True,
            timeout=10,
        )
        return True, None
    except FileNotFoundError:
        return False, "Docker is not installed. Please install Docker first."
    except subprocess.CalledProcessError:
        return False, "Docker daemon is not running. Please start Docker."
    except subprocess.TimeoutExpired:
        return False, "Docker daemon timed out. Please check Docker status."


def validate_openshell_available() -> tuple[bool, str | None]:
    """Check that openshell CLI is available."""
    try:
        subprocess.run(
            ["openshell", "--version"],
            capture_output=True,
            check=True,
            timeout=10,
        )
        return True, None
    except FileNotFoundError:
        return False, "OpenShell is not installed. Please install OpenShell first."
    except subprocess.CalledProcessError:
        return False, "OpenShell command failed. Please check your installation."
    except subprocess.TimeoutExpired:
        return False, "OpenShell command timed out."


def validate_openclaw_state_exists(path: Path | None = None) -> tuple[bool, str | None]:
    """Check that an OpenClaw state directory exists and has expected structure."""
    from shellclaw.config.paths import OPENCLAW_HOME

    state_dir = path or OPENCLAW_HOME
    if not state_dir.is_dir():
        return False, f"OpenClaw state directory not found: {state_dir}"

    expected = ["credentials", "agents"]
    missing = [d for d in expected if not (state_dir / d).is_dir()]
    if missing:
        return False, f"OpenClaw state directory missing subdirectories: {', '.join(missing)}"

    return True, None


def validate_sandbox_name(name: str) -> tuple[bool, str | None]:
    """Validate sandbox name is alphanumeric with hyphens only."""
    if not name:
        return False, "Sandbox name cannot be empty."
    if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9-]*$", name):
        return False, (
            "Sandbox name must be alphanumeric "
            "(hyphens allowed, cannot start with hyphen)."
        )
    return True, None
