from __future__ import annotations

from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from shellclaw.core.provider import ProviderInfo

runner = CliRunner()


@patch("shellclaw.commands.onboard.validate_docker_available", return_value=(True, None))
@patch("shellclaw.commands.onboard.validate_openshell_available", return_value=(True, None))
@patch("shellclaw.commands.onboard.start_gateway", return_value=True)
@patch("shellclaw.commands.onboard.list_providers", return_value=[ProviderInfo(name="ollama")])
@patch("shellclaw.commands.onboard.set_inference", return_value=True)
@patch("shellclaw.commands.onboard.create_sandbox", return_value=True)
class TestOnboardCommand:
    def test_succeeds_with_existing_provider(
        self,
        mock_create: MagicMock,
        mock_inference: MagicMock,
        mock_list_prov: MagicMock,
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
        mock_list_prov: MagicMock,
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
        mock_list_prov: MagicMock,
        mock_gateway: MagicMock,
        mock_openshell: MagicMock,
        mock_docker: MagicMock,
    ) -> None:
        from shellclaw.main import app

        runner.invoke(app, [
            "onboard", "--inference-provider", "ollama",
            "--inference-model", "claude-sonnet",
        ])

        mock_inference.assert_called_once()
        call_kwargs = mock_inference.call_args
        assert call_kwargs[0][0] == "ollama"
        assert call_kwargs[0][1] == "claude-sonnet"

    def test_calls_create_sandbox(
        self,
        mock_create: MagicMock,
        mock_inference: MagicMock,
        mock_list_prov: MagicMock,
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
        mock_list_prov: MagicMock,
        mock_gateway: MagicMock,
        mock_openshell: MagicMock,
        mock_docker: MagicMock,
    ) -> None:
        from shellclaw.main import app

        result = runner.invoke(app, ["onboard"])

        assert "--gpu" not in result.output

    def test_skips_provider_creation_when_exists(
        self,
        mock_create: MagicMock,
        mock_inference: MagicMock,
        mock_list_prov: MagicMock,
        mock_gateway: MagicMock,
        mock_openshell: MagicMock,
        mock_docker: MagicMock,
    ) -> None:
        from shellclaw.main import app

        result = runner.invoke(app, ["onboard"])

        assert result.exit_code == 0
        assert "already exists" in result.output


@patch("shellclaw.commands.onboard.validate_docker_available", return_value=(True, None))
@patch("shellclaw.commands.onboard.validate_openshell_available", return_value=(True, None))
@patch("shellclaw.commands.onboard.start_gateway", return_value=True)
@patch("shellclaw.commands.onboard.list_providers", return_value=[])
@patch("shellclaw.commands.onboard.create_provider", return_value=True)
@patch("shellclaw.commands.onboard.set_inference", return_value=True)
@patch("shellclaw.commands.onboard.create_sandbox", return_value=True)
class TestOnboardCreatesProvider:
    def test_creates_provider_with_url_and_key(
        self,
        mock_create_sb: MagicMock,
        mock_inference: MagicMock,
        mock_create_prov: MagicMock,
        mock_list_prov: MagicMock,
        mock_gateway: MagicMock,
        mock_openshell: MagicMock,
        mock_docker: MagicMock,
    ) -> None:
        from shellclaw.main import app

        result = runner.invoke(app, [
            "onboard",
            "--inference-provider", "litellm",
            "--inference-model", "kimi-k2.5-coding",
            "--inference-url", "http://192.168.50.101:4000/v1",
            "--inference-api-key", "sk-test",
        ])

        assert result.exit_code == 0
        mock_create_prov.assert_called_once_with(
            "litellm", "openai",
            credentials={"OPENAI_API_KEY": "sk-test"},
            config={"OPENAI_BASE_URL": "http://192.168.50.101:4000/v1"},
        )

    def test_fails_when_provider_missing_and_no_url(
        self,
        mock_create_sb: MagicMock,
        mock_inference: MagicMock,
        mock_create_prov: MagicMock,
        mock_list_prov: MagicMock,
        mock_gateway: MagicMock,
        mock_openshell: MagicMock,
        mock_docker: MagicMock,
    ) -> None:
        from shellclaw.main import app

        result = runner.invoke(app, ["onboard"])

        assert result.exit_code != 0
        assert "not found" in result.output


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
