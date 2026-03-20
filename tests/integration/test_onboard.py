from __future__ import annotations

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

runner = CliRunner()


@patch("shellclaw.commands.onboard.validate_docker_available", return_value=(True, None))
@patch("shellclaw.commands.onboard.validate_openshell_available", return_value=(True, None))
@patch("shellclaw.commands.onboard.start_gateway", return_value=True)
@patch("shellclaw.commands.onboard.set_inference", return_value=True)
@patch("shellclaw.commands.onboard.create_sandbox", return_value=True)
class TestOnboardCommand:
    def test_succeeds_with_defaults(
        self,
        mock_create: MagicMock,
        mock_inference: MagicMock,
        mock_gateway: MagicMock,
        mock_openshell: MagicMock,
        mock_docker: MagicMock,
    ) -> None:
        from shellclaw.main import app

        result = runner.invoke(app, ["onboard"])

        assert result.exit_code == 0

    def test_calls_gateway_start(
        self,
        mock_create: MagicMock,
        mock_inference: MagicMock,
        mock_gateway: MagicMock,
        mock_openshell: MagicMock,
        mock_docker: MagicMock,
    ) -> None:
        from shellclaw.main import app

        runner.invoke(app, ["onboard"])

        mock_gateway.assert_called_once()

    def test_calls_set_inference(
        self,
        mock_create: MagicMock,
        mock_inference: MagicMock,
        mock_gateway: MagicMock,
        mock_openshell: MagicMock,
        mock_docker: MagicMock,
    ) -> None:
        from shellclaw.main import app

        runner.invoke(app, [
            "onboard", "--inference-provider", "anthropic",
            "--inference-model", "claude-sonnet",
        ])

        mock_inference.assert_called_once()
        call_kwargs = mock_inference.call_args
        assert call_kwargs[0][0] == "anthropic"
        assert call_kwargs[0][1] == "claude-sonnet"

    def test_calls_create_sandbox(
        self,
        mock_create: MagicMock,
        mock_inference: MagicMock,
        mock_gateway: MagicMock,
        mock_openshell: MagicMock,
        mock_docker: MagicMock,
    ) -> None:
        from shellclaw.main import app

        runner.invoke(app, ["onboard", "--sandbox-name", "my-box"])

        mock_create.assert_called_once()
        assert mock_create.call_args[0][0] == "my-box"

    def test_no_gpu_flag_in_any_output(
        self,
        mock_create: MagicMock,
        mock_inference: MagicMock,
        mock_gateway: MagicMock,
        mock_openshell: MagicMock,
        mock_docker: MagicMock,
    ) -> None:
        from shellclaw.main import app

        result = runner.invoke(app, ["onboard"])

        assert "--gpu" not in result.output


@patch(
    "shellclaw.commands.onboard.validate_docker_available",
    return_value=(False, "Docker not found"),
)
class TestOnboardFailsWithoutDocker:
    def test_fails_without_docker(self, mock_docker: MagicMock) -> None:
        from shellclaw.main import app

        result = runner.invoke(app, ["onboard"])

        assert result.exit_code != 0


@patch("shellclaw.commands.onboard.validate_docker_available", return_value=(True, None))
@patch("shellclaw.commands.onboard.validate_openshell_available", return_value=(True, None))
@patch("shellclaw.commands.onboard.start_gateway", return_value=False)
class TestOnboardRollbackOnGatewayFailure:
    def test_exits_on_gateway_failure(
        self,
        mock_gateway: MagicMock,
        mock_openshell: MagicMock,
        mock_docker: MagicMock,
    ) -> None:
        from shellclaw.main import app

        result = runner.invoke(app, ["onboard"])

        assert result.exit_code != 0
