from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass

from shellclaw.core.gateway import _strip_ansi
from shellclaw.core.shell import run_openshell

_TABLE_HEADER_RE = re.compile(r"^NAME\s+", re.IGNORECASE)


@dataclass(frozen=True)
class ProviderInfo:
    name: str
    provider_type: str = ""


def create_provider(
    name: str,
    provider_type: str,
    credentials: dict[str, str] | None = None,
    config: dict[str, str] | None = None,
    from_existing: bool = False,
) -> bool:
    try:
        args = ["provider", "create", "--name", name, "--type", provider_type]
        if from_existing:
            args.append("--from-existing")
        elif credentials:
            for key, value in credentials.items():
                args.extend(["--credential", f"{key}={value}"])
        if config:
            for key, value in config.items():
                args.extend(["--config", f"{key}={value}"])
        run_openshell(args)
        return True
    except subprocess.CalledProcessError:
        return False


def inject_credentials_from_env(
    key_names: list[str],
    provider_type: str = "generic",
) -> bool:
    credentials: dict[str, str] = {}
    for key in key_names:
        value = os.environ.get(key)
        if value is None:
            return False
        credentials[key] = value

    return create_provider("credentials", provider_type, credentials=credentials)


def list_providers() -> list[ProviderInfo]:
    try:
        result = run_openshell(["provider", "list"], check=True)
        providers: list[ProviderInfo] = []
        for line in result.stdout.strip().splitlines():
            clean = _strip_ansi(line).strip()
            if not clean:
                continue
            # Skip table header row
            if _TABLE_HEADER_RE.match(clean):
                continue
            parts = clean.split()
            if parts:
                providers.append(ProviderInfo(
                    name=parts[0],
                    provider_type=parts[1] if len(parts) > 1 else "",
                ))
        return providers
    except subprocess.CalledProcessError:
        return []


def delete_provider(name: str) -> bool:
    try:
        run_openshell(["provider", "delete", name])
        return True
    except subprocess.CalledProcessError:
        return False
