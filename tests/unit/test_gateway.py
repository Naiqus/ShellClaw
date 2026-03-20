from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_run_openshell() -> MagicMock:
    with patch("shellclaw.core.gateway.run_openshell") as mock:
        mock.return_value = subprocess.CompletedProcess(
            args=["openshell"], returncode=0, stdout="", stderr=""
        )
        yield mock


class TestStartGateway:
    def test_calls_gateway_start(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.gateway import start_gateway

        result = start_gateway()

        mock_run_openshell.assert_called_once_with(["gateway", "start"])
        assert result is True

    def test_no_gpu_flag_in_command(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.gateway import start_gateway

        start_gateway()

        args = mock_run_openshell.call_args[0][0]
        assert "--gpu" not in args

    def test_returns_false_on_failure(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.gateway import start_gateway

        mock_run_openshell.side_effect = subprocess.CalledProcessError(1, "openshell")

        result = start_gateway()
        assert result is False

    def test_accepts_custom_host(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.gateway import start_gateway

        start_gateway(host="192.168.1.100")

        args = mock_run_openshell.call_args[0][0]
        assert "--host" in args
        host_idx = args.index("--host")
        assert args[host_idx + 1] == "192.168.1.100"


class TestStopGateway:
    def test_calls_gateway_stop(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.gateway import stop_gateway

        result = stop_gateway()

        mock_run_openshell.assert_called_once_with(["gateway", "stop"])
        assert result is True

    def test_returns_false_on_failure(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.gateway import stop_gateway

        mock_run_openshell.side_effect = subprocess.CalledProcessError(1, "openshell")

        result = stop_gateway()
        assert result is False


class TestIsGatewayRunning:
    def test_returns_true_when_running(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.gateway import is_gateway_running

        mock_run_openshell.return_value = subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout="  Status: Connected\n  Server: https://127.0.0.1:8080\n",
            stderr=""
        )

        assert is_gateway_running() is True
        mock_run_openshell.assert_called_once_with(["status"], check=True)

    def test_returns_false_when_not_running(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.gateway import is_gateway_running

        mock_run_openshell.side_effect = subprocess.CalledProcessError(1, "openshell")

        assert is_gateway_running() is False

    def test_returns_false_when_disconnected(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.gateway import is_gateway_running

        mock_run_openshell.return_value = subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout="  Status: Disconnected\n",
            stderr=""
        )

        assert is_gateway_running() is False


class TestGetGatewayStatus:
    def test_returns_status_dataclass(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.gateway import GatewayStatus, get_gateway_status

        mock_run_openshell.return_value = subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout=(
                "Server Status\n"
                "  Gateway: nemoclaw\n"
                "  Server: https://127.0.0.1:8080\n"
                "  Status: Connected\n"
                "  Version: 0.0.11\n"
            ),
            stderr=""
        )

        status = get_gateway_status()
        assert isinstance(status, GatewayStatus)
        assert status.running is True
        assert status.host == "https://127.0.0.1:8080"
        assert status.version == "0.0.11"

    def test_returns_stopped_status_on_failure(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.gateway import get_gateway_status

        mock_run_openshell.side_effect = subprocess.CalledProcessError(1, "openshell")

        status = get_gateway_status()
        assert status.running is False


class TestStripAnsi:
    def test_strips_ansi_codes(self) -> None:
        from shellclaw.core.gateway import _strip_ansi

        text = "\x1b[1m\x1b[36mServer Status\x1b[39m\x1b[0m"
        assert _strip_ansi(text) == "Server Status"

    def test_preserves_plain_text(self) -> None:
        from shellclaw.core.gateway import _strip_ansi

        assert _strip_ansi("plain text") == "plain text"


class TestParseKvLines:
    def test_parses_key_value_lines(self) -> None:
        from shellclaw.core.gateway import _parse_kv_lines

        text = "  Provider: litellm\n  Model: kimi-k2.5\n"
        result = _parse_kv_lines(text)
        assert result["provider"] == "litellm"
        assert result["model"] == "kimi-k2.5"

    def test_handles_ansi_codes(self) -> None:
        from shellclaw.core.gateway import _parse_kv_lines

        text = "  \x1b[2mProvider:\x1b[0m litellm\n"
        result = _parse_kv_lines(text)
        assert result["provider"] == "litellm"

    def test_skips_lines_without_colon(self) -> None:
        from shellclaw.core.gateway import _parse_kv_lines

        text = "Header\n  Key: value\n"
        result = _parse_kv_lines(text)
        assert "key" in result
