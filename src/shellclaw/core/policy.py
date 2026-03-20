from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

from shellclaw.core.shell import run_openshell

REQUIRED_SECTIONS = ("filesystem", "network")


def load_policy(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Policy file not found: {path}")

    with open(path) as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in policy file: {e}") from e

    if not isinstance(data, dict):
        raise ValueError("Invalid YAML: policy must be a mapping")

    return data


def validate_policy(policy: dict) -> list[str]:
    errors: list[str] = []
    for section in REQUIRED_SECTIONS:
        if section not in policy:
            errors.append(f"Missing required section: '{section}'")
    return errors


def apply_policy(sandbox_name: str, policy_path: Path) -> bool:
    try:
        run_openshell(["policy", "set", str(policy_path), "--sandbox", sandbox_name])
        return True
    except subprocess.CalledProcessError:
        return False
