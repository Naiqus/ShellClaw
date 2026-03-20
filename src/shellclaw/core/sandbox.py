from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from shellclaw.core.gateway import _strip_ansi
from shellclaw.core.shell import run_openshell

_TABLE_HEADER_RE = re.compile(r"^NAME\s+", re.IGNORECASE)


@dataclass(frozen=True)
class SandboxStatus:
    name: str
    state: str


def create_sandbox(name: str, policy_path: Path | None = None) -> bool:
    existing = {s.name for s in list_sandboxes()}
    if name in existing:
        return True
    try:
        args = [
            "sandbox", "create",
            "--from", "openclaw",
            "--name", name,
        ]
        if policy_path is not None:
            args.extend(["--policy", str(policy_path)])
        # Pass "-- true" to avoid dropping into an interactive shell
        args.extend(["--", "true"])
        run_openshell(args)
        return True
    except subprocess.CalledProcessError:
        return False


def delete_sandbox(name: str) -> bool:
    try:
        run_openshell(["sandbox", "delete", name])
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
        ["sandbox", "connect", name, "--", command],
        check=False,
    )


def list_sandboxes() -> list[SandboxStatus]:
    try:
        result = run_openshell(["sandbox", "list"], check=True)
        sandboxes: list[SandboxStatus] = []
        for line in result.stdout.strip().splitlines():
            clean = _strip_ansi(line).strip()
            if not clean:
                continue
            # Skip "No sandboxes" messages and table headers
            if clean.lower().startswith("no sandbox") or _TABLE_HEADER_RE.match(clean):
                continue
            parts = clean.split()
            if len(parts) >= 2:
                sandboxes.append(SandboxStatus(name=parts[0], state=parts[1]))
        return sandboxes
    except subprocess.CalledProcessError:
        return []
