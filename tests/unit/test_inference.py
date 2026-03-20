from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_run_openshell() -> MagicMock:
    with patch("shellclaw.core.inference.run_openshell") as mock:
        mock.return_value = subprocess.CompletedProcess(
            args=["openshell"], returncode=0, stdout="", stderr=""
        )
        yield mock


class TestSetInference:
    def test_calls_inference_set(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.inference import set_inference

        result = set_inference("ollama", "llama3")

        assert result is True
        mock_run_openshell.assert_called_once()
        args = mock_run_openshell.call_args[0][0]
        assert args[0:2] == ["inference", "set"]

    def test_includes_provider_and_model(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.inference import set_inference

        set_inference("anthropic", "claude-sonnet")

        args = mock_run_openshell.call_args[0][0]
        assert "--provider" in args
        assert "anthropic" in args
        assert "--model" in args
        assert "claude-sonnet" in args

    def test_accepts_any_provider_name(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.inference import set_inference

        result = set_inference("my-custom-provider", "model")

        assert result is True
        mock_run_openshell.assert_called_once()

    def test_returns_false_on_failure(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.inference import set_inference

        mock_run_openshell.side_effect = subprocess.CalledProcessError(1, "openshell")

        result = set_inference("ollama", "llama3")
        assert result is False


class TestGetInferenceConfig:
    def test_returns_config_dataclass(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.inference import InferenceConfig, get_inference_config

        mock_run_openshell.return_value = subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout=(
                "Gateway inference:\n"
                "  Provider: litellm\n"
                "  Model: kimi-k2.5-coding\n"
                "  Version: 1\n"
            ),
            stderr=""
        )

        config = get_inference_config()
        assert isinstance(config, InferenceConfig)
        assert config.provider == "litellm"
        assert config.model == "kimi-k2.5-coding"
        assert config.version == "1"

    def test_returns_none_on_failure(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.inference import get_inference_config

        mock_run_openshell.side_effect = subprocess.CalledProcessError(1, "openshell")

        config = get_inference_config()
        assert config is None

    def test_returns_none_when_not_configured(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.inference import get_inference_config

        mock_run_openshell.return_value = subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout="System inference:\n  Not configured\n",
            stderr=""
        )

        config = get_inference_config()
        assert config is None

    def test_handles_ansi_codes(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.inference import get_inference_config

        mock_run_openshell.return_value = subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout=(
                "\x1b[1m\x1b[36mGateway inference:\x1b[39m\x1b[0m\n"
                "  \x1b[2mProvider:\x1b[0m litellm\n"
                "  \x1b[2mModel:\x1b[0m kimi-k2.5-coding\n"
                "  \x1b[2mVersion:\x1b[0m 1\n"
            ),
            stderr=""
        )

        config = get_inference_config()
        assert config is not None
        assert config.provider == "litellm"
        assert config.model == "kimi-k2.5-coding"
