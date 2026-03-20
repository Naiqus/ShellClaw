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

        result = set_inference("ollama", "llama3", "http://localhost:11434")

        assert result is True
        mock_run_openshell.assert_called_once()
        args = mock_run_openshell.call_args[0][0]
        assert args[0:2] == ["inference", "set"]

    def test_includes_provider_and_model(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.inference import set_inference

        set_inference("anthropic", "claude-sonnet", "https://api.anthropic.com")

        args = mock_run_openshell.call_args[0][0]
        assert "--provider" in args
        assert "anthropic" in args
        assert "--model" in args
        assert "claude-sonnet" in args
        assert "--url" in args

    def test_rejects_unsupported_provider(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.inference import set_inference

        with pytest.raises(ValueError, match="Unsupported provider"):
            set_inference("unsupported-provider", "model", "http://localhost")

        mock_run_openshell.assert_not_called()

    def test_returns_false_on_failure(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.inference import set_inference

        mock_run_openshell.side_effect = subprocess.CalledProcessError(1, "openshell")

        result = set_inference("ollama", "llama3", "http://localhost:11434")
        assert result is False


class TestSupportedProviders:
    def test_contains_expected_providers(self) -> None:
        from shellclaw.core.inference import SUPPORTED_PROVIDERS

        assert "ollama" in SUPPORTED_PROVIDERS
        assert "openai" in SUPPORTED_PROVIDERS
        assert "anthropic" in SUPPORTED_PROVIDERS
        assert "apple-metal" in SUPPORTED_PROVIDERS
        assert "custom" in SUPPORTED_PROVIDERS


class TestGetInferenceConfig:
    def test_returns_config_dataclass(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.inference import InferenceConfig, get_inference_config

        mock_run_openshell.return_value = subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout="provider: ollama\nmodel: llama3\nurl: http://localhost:11434",
            stderr=""
        )

        config = get_inference_config()
        assert isinstance(config, InferenceConfig)

    def test_returns_none_on_failure(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.inference import get_inference_config

        mock_run_openshell.side_effect = subprocess.CalledProcessError(1, "openshell")

        config = get_inference_config()
        assert config is None
