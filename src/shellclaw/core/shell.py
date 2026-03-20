from __future__ import annotations

import subprocess


def run_openshell(
    args: list[str],
    capture: bool = True,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Execute an openshell CLI command.

    Args:
        args: Command arguments (without the 'openshell' prefix).
        capture: Whether to capture stdout/stderr.
        check: Whether to raise CalledProcessError on non-zero exit.

    Returns:
        CompletedProcess with command results.
    """
    cmd = ["openshell", *args]
    return subprocess.run(
        cmd,
        capture_output=capture,
        check=check,
        text=True,
    )


def run_docker(
    args: list[str],
    capture: bool = True,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Execute a docker CLI command."""
    cmd = ["docker", *args]
    return subprocess.run(
        cmd,
        capture_output=capture,
        check=check,
        text=True,
    )
