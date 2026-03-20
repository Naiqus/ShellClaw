from __future__ import annotations

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

runner = CliRunner()


class TestStatusCommand:
    @patch("shellclaw.commands.status.get_gateway_status")
    @patch("shellclaw.commands.status.list_sandboxes", return_value=[])
    @patch("shellclaw.commands.status.get_inference_config", return_value=None)
    @patch("shellclaw.commands.status.list_providers", return_value=[])
    def test_displays_status(
        self,
        mock_providers: MagicMock,
        mock_inference: MagicMock,
        mock_sandboxes: MagicMock,
        mock_gateway: MagicMock,
    ) -> None:
        from shellclaw.core.gateway import GatewayStatus
        from shellclaw.main import app

        mock_gateway.return_value = GatewayStatus(running=True, host="localhost", uptime="120s")

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0

    @patch("shellclaw.commands.status.get_gateway_status")
    @patch("shellclaw.commands.status.list_sandboxes", return_value=[])
    @patch("shellclaw.commands.status.get_inference_config", return_value=None)
    @patch("shellclaw.commands.status.list_providers", return_value=[])
    def test_shows_stopped_gateway(
        self,
        mock_providers: MagicMock,
        mock_inference: MagicMock,
        mock_sandboxes: MagicMock,
        mock_gateway: MagicMock,
    ) -> None:
        from shellclaw.core.gateway import GatewayStatus
        from shellclaw.main import app

        mock_gateway.return_value = GatewayStatus(running=False)

        result = runner.invoke(app, ["status"])

        assert result.exit_code == 0
