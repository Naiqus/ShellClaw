from __future__ import annotations

from pathlib import Path

SHELLCLAW_HOME = Path.home() / ".shellclaw"
OPENCLAW_HOME = Path.home() / ".openclaw"
DEFAULT_POLICY_PATH = (
    Path(__file__).resolve().parent.parent.parent.parent / "policies" / "default-policy.yaml"
)
DEFAULT_SANDBOX_NAME = "openclaw-sandbox"
INFERENCE_ENDPOINT = "https://inference.local"
