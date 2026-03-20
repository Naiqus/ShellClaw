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
            args=[], returncode=0, stdout="running", stderr=""
        )

        assert is_gateway_running() is True

    def test_returns_false_when_not_running(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.gateway import is_gateway_running

        mock_run_openshell.side_effect = subprocess.CalledProcessError(1, "openshell")

        assert is_gateway_running() is False


class TestGetGatewayStatus:
    def test_returns_status_dataclass(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.gateway import GatewayStatus, get_gateway_status

        mock_run_openshell.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="running\nlocalhost\n120s", stderr=""
        )

        status = get_gateway_status()
        assert isinstance(status, GatewayStatus)
        assert status.running is True

    def test_returns_stopped_status_on_failure(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.gateway import get_gateway_status

        mock_run_openshell.side_effect = subprocess.CalledProcessError(1, "openshell")

        status = get_gateway_status()
        assert status.running is False
