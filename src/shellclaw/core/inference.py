from __future__ import annotations

import subprocess
from dataclasses import dataclass

from shellclaw.core.gateway import _parse_kv_lines
from shellclaw.core.shell import run_openshell


@dataclass(frozen=True)
class InferenceConfig:
    provider: str = ""
    model: str = ""
    version: str = ""


def set_inference(provider: str, model: str) -> bool:
    try:
        run_openshell([
            "inference", "set",
            "--provider", provider,
            "--model", model,
        ])
        return True
    except subprocess.CalledProcessError:
        return False


def get_inference_config() -> InferenceConfig | None:
    try:
        result = run_openshell(["inference", "get"], check=True)
        values = _parse_kv_lines(result.stdout)
        provider = values.get("provider", "")
        model = values.get("model", "")
        if not provider and not model:
            return None
        return InferenceConfig(
            provider=provider,
            model=model,
            version=values.get("version", ""),
        )
    except subprocess.CalledProcessError:
        return None
