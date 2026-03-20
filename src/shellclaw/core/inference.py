from __future__ import annotations

import subprocess
from dataclasses import dataclass

from shellclaw.core.shell import run_openshell

SUPPORTED_PROVIDERS: frozenset[str] = frozenset({
    "ollama",
    "openai",
    "anthropic",
    "apple-metal",
    "custom",
})


@dataclass(frozen=True)
class InferenceConfig:
    provider: str = ""
    model: str = ""
    url: str = ""


def set_inference(provider: str, model: str, url: str) -> bool:
    if provider not in SUPPORTED_PROVIDERS:
        raise ValueError(
            f"Unsupported provider: '{provider}'. "
            f"Supported: {', '.join(sorted(SUPPORTED_PROVIDERS))}"
        )
    try:
        run_openshell([
            "inference", "set",
            "--provider", provider,
            "--model", model,
            "--url", url,
        ])
        return True
    except subprocess.CalledProcessError:
        return False


def get_inference_config() -> InferenceConfig | None:
    try:
        result = run_openshell(["inference", "get"], check=True)
        lines = result.stdout.strip().splitlines()
        values: dict[str, str] = {}
        for line in lines:
            if ":" in line:
                key, _, value = line.partition(":")
                values[key.strip()] = value.strip()
        return InferenceConfig(
            provider=values.get("provider", ""),
            model=values.get("model", ""),
            url=values.get("url", ""),
        )
    except subprocess.CalledProcessError:
        return None
