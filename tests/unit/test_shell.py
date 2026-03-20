from __future__ import annotations

import subprocess
from unittest.mock import MagicMock

import pytest


class TestRunOpenshell:
    def test_builds_correct_command(self, mock_subprocess_run: MagicMock) -> None:
        from shellclaw.core.shell import run_openshell

        run_openshell(["gateway", "start"])

        mock_subprocess_run.assert_called_once()
        args = mock_subprocess_run.call_args[0][0]
        assert args == ["openshell", "gateway", "start"]

    def test_returns_completed_process(self, mock_subprocess_run: MagicMock) -> None:
        from shellclaw.core.shell import run_openshell

        result = run_openshell(["sandbox", "list"])

        assert isinstance(result, subprocess.CompletedProcess)
        assert result.returncode == 0

    def test_raises_on_failure_when_check_true(self, mock_subprocess_run: MagicMock) -> None:
        from shellclaw.core.shell import run_openshell

        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            1, "openshell", stderr="error"
        )

        with pytest.raises(subprocess.CalledProcessError):
            run_openshell(["bad", "command"], check=True)

    def test_does_not_raise_when_check_false(self, mock_subprocess_run: MagicMock) -> None:
        from shellclaw.core.shell import run_openshell

        mock_subprocess_run.return_value = subprocess.CompletedProcess(
            args=["openshell"], returncode=1, stdout="", stderr="error"
        )

        result = run_openshell(["bad", "command"], check=False)
        assert result.returncode == 1

    def test_does_not_mutate_input_args(self, mock_subprocess_run: MagicMock) -> None:
        from shellclaw.core.shell import run_openshell

        original_args = ["gateway", "status"]
        args_copy = list(original_args)
        run_openshell(original_args)
        assert original_args == args_copy

    def test_captures_output_by_default(self, mock_subprocess_run: MagicMock) -> None:
        from shellclaw.core.shell import run_openshell

        run_openshell(["sandbox", "list"])

        call_kwargs = mock_subprocess_run.call_args[1]
        assert call_kwargs.get("capture_output") is True

    def test_no_capture_when_disabled(self, mock_subprocess_run: MagicMock) -> None:
        from shellclaw.core.shell import run_openshell

        run_openshell(["sandbox", "connect"], capture=False)

        call_kwargs = mock_subprocess_run.call_args[1]
        assert call_kwargs.get("capture_output") is False


class TestRunDocker:
    def test_builds_docker_command(self, mock_subprocess_run: MagicMock) -> None:
        from shellclaw.core.shell import run_docker

        run_docker(["ps"])

        args = mock_subprocess_run.call_args[0][0]
        assert args == ["docker", "ps"]

    def test_does_not_mutate_input_args(self, mock_subprocess_run: MagicMock) -> None:
        from shellclaw.core.shell import run_docker

        original_args = ["info"]
        args_copy = list(original_args)
        run_docker(original_args)
        assert original_args == args_copy
