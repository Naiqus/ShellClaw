from __future__ import annotations

import subprocess
from dataclasses import dataclass

from shellclaw.core.shell import run_openshell


@dataclass(frozen=True)
class GatewayStatus:
    running: bool
    host: str = ""
    uptime: str = ""


def start_gateway(host: str = "localhost") -> bool:
    try:
        args = ["gateway", "start"]
        if host != "localhost":
            args.extend(["--host", host])
        run_openshell(args)
        return True
    except subprocess.CalledProcessError:
        return False


def stop_gateway() -> bool:
    try:
        run_openshell(["gateway", "stop"])
        return True
    except subprocess.CalledProcessError:
        return False


def is_gateway_running() -> bool:
    try:
        run_openshell(["gateway", "status"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def get_gateway_status() -> GatewayStatus:
    try:
        result = run_openshell(["gateway", "status"], check=True)
        lines = result.stdout.strip().splitlines()
        return GatewayStatus(
            running=True,
            host=lines[1] if len(lines) > 1 else "",
            uptime=lines[2] if len(lines) > 2 else "",
        )
    except subprocess.CalledProcessError:
        return GatewayStatus(running=False)
