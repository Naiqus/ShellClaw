from __future__ import annotations

import os
from dataclasses import dataclass

import yaml

from shellclaw.config.paths import DEFAULT_SANDBOX_NAME, SHELLCLAW_HOME


@dataclass(frozen=True)
class Settings:
    sandbox_name: str = DEFAULT_SANDBOX_NAME
    gateway_host: str = "localhost"
    inference_provider: str = "ollama"
    inference_model: str = "llama3"
    inference_url: str = "http://localhost:11434"


def load_settings() -> Settings:
    """Load settings from config file, then override with env vars."""
    config_path = SHELLCLAW_HOME / "config.yaml"
    values: dict[str, str] = {}

    if config_path.exists():
        with open(config_path) as f:
            data = yaml.safe_load(f)
            if isinstance(data, dict):
                values.update(data)

    # Environment variable overrides (SHELLCLAW_ prefix)
    field_names = Settings.__dataclass_fields__.keys()
    for field in field_names:
        env_key = f"SHELLCLAW_{field.upper()}"
        env_val = os.environ.get(env_key)
        if env_val is not None:
            values[field] = env_val

    return Settings(**{k: v for k, v in values.items() if k in field_names})
