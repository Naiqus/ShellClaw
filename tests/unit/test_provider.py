from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_run_openshell() -> MagicMock:
    with patch("shellclaw.core.provider.run_openshell") as mock:
        mock.return_value = subprocess.CompletedProcess(
            args=["openshell"], returncode=0, stdout="", stderr=""
        )
        yield mock


class TestCreateProvider:
    def test_calls_provider_create(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.provider import create_provider

        result = create_provider("anthropic", {"ANTHROPIC_API_KEY": "sk-test"})

        assert result is True
        args = mock_run_openshell.call_args[0][0]
        assert "provider" in args
        assert "create" in args

    def test_returns_false_on_failure(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.provider import create_provider

        mock_run_openshell.side_effect = subprocess.CalledProcessError(1, "openshell")

        result = create_provider("test", {"KEY": "val"})
        assert result is False


class TestInjectCredentialsFromEnv:
    def test_injects_existing_env_vars(
        self, mock_run_openshell: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from shellclaw.core.provider import inject_credentials_from_env

        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-123")

        result = inject_credentials_from_env(["ANTHROPIC_API_KEY"])

        assert result is True
        mock_run_openshell.assert_called_once()

    def test_returns_false_when_env_var_missing(
        self, mock_run_openshell: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from shellclaw.core.provider import inject_credentials_from_env

        monkeypatch.delenv("NONEXISTENT_KEY", raising=False)

        result = inject_credentials_from_env(["NONEXISTENT_KEY"])

        assert result is False
        mock_run_openshell.assert_not_called()

    def test_never_logs_credential_values(
        self, mock_run_openshell: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        from shellclaw.core.provider import inject_credentials_from_env

        secret = "sk-super-secret-value-12345"
        monkeypatch.setenv("MY_SECRET", secret)

        inject_credentials_from_env(["MY_SECRET"])

        captured = capsys.readouterr()
        assert secret not in captured.out
        assert secret not in captured.err


class TestListProviders:
    def test_returns_list(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.provider import list_providers

        mock_run_openshell.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="anthropic\nopenai\n", stderr=""
        )

        result = list_providers()
        assert isinstance(result, list)


class TestDeleteProvider:
    def test_calls_provider_delete(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.provider import delete_provider

        result = delete_provider("anthropic")

        assert result is True
        args = mock_run_openshell.call_args[0][0]
        assert "provider" in args
        assert "delete" in args
        assert "anthropic" in args
