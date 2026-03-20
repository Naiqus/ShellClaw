from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from shellclaw.core.shell import run_openshell


@dataclass(frozen=True)
class SandboxStatus:
    name: str
    state: str


def create_sandbox(name: str, policy_path: Path | None = None) -> bool:
    try:
        run_openshell([
            "sandbox", "create",
            "--from", "openclaw",
            "--name", name,
        ])
        if policy_path is not None:
            run_openshell(["policy", "set", str(policy_path), "--sandbox", name])
        return True
    except subprocess.CalledProcessError:
        return False


def start_sandbox(name: str) -> bool:
    try:
        run_openshell(["sandbox", "start", name])
        return True
    except subprocess.CalledProcessError:
        return False


def stop_sandbox(name: str) -> bool:
    try:
        run_openshell(["sandbox", "stop", name])
        return True
    except subprocess.CalledProcessError:
        return False


def connect_sandbox(name: str) -> int:
    result = run_openshell(["sandbox", "connect", name], capture=False, check=False)
    return result.returncode


def upload_to_sandbox(name: str, local_path: Path, remote_path: str) -> bool:
    try:
        run_openshell([
            "sandbox", "upload",
            "--sandbox", name,
            str(local_path),
            remote_path,
        ])
        return True
    except subprocess.CalledProcessError:
        return False


def exec_in_sandbox(name: str, command: str) -> subprocess.CompletedProcess[str]:
    return run_openshell(
        ["sandbox", "exec", name, "--", command],
        check=False,
    )


def list_sandboxes() -> list[SandboxStatus]:
    try:
        result = run_openshell(["sandbox", "list"], check=True)
        sandboxes: list[SandboxStatus] = []
        for line in result.stdout.strip().splitlines():
            parts = line.split()
            if len(parts) >= 2:
                sandboxes.append(SandboxStatus(name=parts[0], state=parts[1]))
        return sandboxes
    except subprocess.CalledProcessError:
        return []
