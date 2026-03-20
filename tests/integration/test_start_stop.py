from __future__ import annotations

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

runner = CliRunner()


class TestStartCommand:
    @patch("shellclaw.commands.start.is_gateway_running", return_value=True)
    @patch("shellclaw.commands.start.start_sandbox", return_value=True)
    def test_starts_sandbox(self, mock_start: MagicMock, mock_gw: MagicMock) -> None:
        from shellclaw.main import app

        result = runner.invoke(app, ["start"])

        assert result.exit_code == 0
        mock_start.assert_called_once()

    @patch("shellclaw.commands.start.is_gateway_running", return_value=False)
    @patch("shellclaw.commands.start.start_gateway", return_value=True)
    @patch("shellclaw.commands.start.start_sandbox", return_value=True)
    def test_auto_starts_gateway(
        self, mock_sandbox: MagicMock, mock_gw_start: MagicMock, mock_gw_check: MagicMock
    ) -> None:
        from shellclaw.main import app

        result = runner.invoke(app, ["start"])

        assert result.exit_code == 0
        mock_gw_start.assert_called_once()

    @patch("shellclaw.commands.start.is_gateway_running", return_value=True)
    @patch("shellclaw.commands.start.start_sandbox", return_value=False)
    def test_fails_when_sandbox_fails(self, mock_start: MagicMock, mock_gw: MagicMock) -> None:
        from shellclaw.main import app

        result = runner.invoke(app, ["start"])

        assert result.exit_code != 0


class TestStopCommand:
    @patch("shellclaw.commands.stop.stop_sandbox", return_value=True)
    def test_stops_sandbox(self, mock_stop: MagicMock) -> None:
        from shellclaw.main import app

        result = runner.invoke(app, ["stop"])

        assert result.exit_code == 0
        mock_stop.assert_called_once()

    @patch("shellclaw.commands.stop.stop_sandbox", return_value=True)
    @patch("shellclaw.commands.stop.stop_gateway", return_value=True)
    def test_stops_gateway_when_flag_set(
        self, mock_gw_stop: MagicMock, mock_stop: MagicMock
    ) -> None:
        from shellclaw.main import app

        result = runner.invoke(app, ["stop", "--gateway"])

        assert result.exit_code == 0
        mock_gw_stop.assert_called_once()
