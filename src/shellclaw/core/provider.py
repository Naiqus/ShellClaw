from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass

from shellclaw.core.shell import run_openshell


@dataclass(frozen=True)
class ProviderInfo:
    name: str


def create_provider(name: str, env_vars: dict[str, str]) -> bool:
    try:
        args = ["provider", "create", "--name", name]
        for key, value in env_vars.items():
            args.extend(["--env", f"{key}={value}"])
        run_openshell(args)
        return True
    except subprocess.CalledProcessError:
        return False


def inject_credentials_from_env(key_names: list[str]) -> bool:
    env_vars: dict[str, str] = {}
    for key in key_names:
        value = os.environ.get(key)
        if value is None:
            return False
        env_vars[key] = value

    return create_provider("credentials", env_vars)


def list_providers() -> list[ProviderInfo]:
    try:
        result = run_openshell(["provider", "list"], check=True)
        return [
            ProviderInfo(name=line.strip())
            for line in result.stdout.strip().splitlines()
            if line.strip()
        ]
    except subprocess.CalledProcessError:
        return []


def delete_provider(name: str) -> bool:
    try:
        run_openshell(["provider", "delete", name])
        return True
    except subprocess.CalledProcessError:
        return False
