from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass

from shellclaw.core.shell import run_openshell

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


def _parse_kv_lines(text: str) -> dict[str, str]:
    """Parse indented 'Key: Value' lines from openshell output."""
    values: dict[str, str] = {}
    for line in text.splitlines():
        clean = _strip_ansi(line).strip()
        if ":" in clean:
            key, _, value = clean.partition(":")
            values[key.strip().lower()] = value.strip()
    return values


@dataclass(frozen=True)
class GatewayStatus:
    running: bool
    host: str = ""
    version: str = ""


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
        result = run_openshell(["status"], check=True)
        values = _parse_kv_lines(result.stdout)
        return values.get("status", "").lower() == "connected"
    except subprocess.CalledProcessError:
        return False


def get_gateway_status() -> GatewayStatus:
    try:
        result = run_openshell(["status"], check=True)
        values = _parse_kv_lines(result.stdout)
        connected = values.get("status", "").lower() == "connected"
        return GatewayStatus(
            running=connected,
            host=values.get("server", ""),
            version=values.get("version", ""),
        )
    except subprocess.CalledProcessError:
        return GatewayStatus(running=False)
