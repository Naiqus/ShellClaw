from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_run_openshell() -> MagicMock:
    with patch("shellclaw.core.sandbox.run_openshell") as mock:
        mock.return_value = subprocess.CompletedProcess(
            args=["openshell"], returncode=0, stdout="", stderr=""
        )
        yield mock


class TestCreateSandbox:
    def test_calls_sandbox_create_with_from_openclaw(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.sandbox import create_sandbox

        result = create_sandbox("my-sandbox")

        assert result is True
        args = mock_run_openshell.call_args[0][0]
        assert "sandbox" in args
        assert "create" in args
        assert "--from" in args
        assert "openclaw" in args

    def test_no_gpu_flag(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.sandbox import create_sandbox

        create_sandbox("test")

        args = mock_run_openshell.call_args[0][0]
        assert "--gpu" not in args

    def test_includes_sandbox_name(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.sandbox import create_sandbox

        create_sandbox("my-sandbox")

        args = mock_run_openshell.call_args[0][0]
        assert "--name" in args
        assert "my-sandbox" in args

    def test_includes_policy_in_create_command(
        self, mock_run_openshell: MagicMock, sample_policy: Path
    ) -> None:
        from shellclaw.core.sandbox import create_sandbox

        create_sandbox("my-sandbox", policy_path=sample_policy)

        # Policy is passed inline with --policy, single call
        mock_run_openshell.assert_called_once()
        args = mock_run_openshell.call_args[0][0]
        assert "--policy" in args
        assert str(sample_policy) in args

    def test_returns_false_on_failure(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.sandbox import create_sandbox

        mock_run_openshell.side_effect = subprocess.CalledProcessError(1, "openshell")

        result = create_sandbox("test")
        assert result is False


class TestDeleteSandbox:
    def test_calls_sandbox_delete(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.sandbox import delete_sandbox

        result = delete_sandbox("my-sandbox")

        assert result is True
        args = mock_run_openshell.call_args[0][0]
        assert args == ["sandbox", "delete", "my-sandbox"]

    def test_returns_false_on_failure(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.sandbox import delete_sandbox

        mock_run_openshell.side_effect = subprocess.CalledProcessError(1, "openshell")
        assert delete_sandbox("test") is False


class TestUploadToSandbox:
    def test_calls_sandbox_upload(self, mock_run_openshell: MagicMock, tmp_path: Path) -> None:
        from shellclaw.core.sandbox import upload_to_sandbox

        local_file = tmp_path / "data.tar.gz"
        local_file.touch()

        result = upload_to_sandbox("my-sandbox", local_file, "/sandbox/.openclaw")

        assert result is True
        args = mock_run_openshell.call_args[0][0]
        assert "upload" in args


class TestExecInSandbox:
    def test_calls_sandbox_connect_with_command(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.sandbox import exec_in_sandbox

        result = exec_in_sandbox("my-sandbox", "openclaw doctor")

        assert result.returncode == 0
        args = mock_run_openshell.call_args[0][0]
        assert "connect" in args
        assert "my-sandbox" in args
        assert "--" in args


class TestListSandboxes:
    def test_returns_list(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.sandbox import list_sandboxes

        mock_run_openshell.return_value = subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout="my-sandbox  running\ntest-box  stopped\n",
            stderr=""
        )

        result = list_sandboxes()
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].name == "my-sandbox"
        assert result[0].state == "running"

    def test_returns_empty_for_no_sandboxes_message(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.sandbox import list_sandboxes

        mock_run_openshell.return_value = subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout="No sandboxes found.\n",
            stderr=""
        )

        result = list_sandboxes()
        assert result == []

    def test_returns_empty_on_failure(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.sandbox import list_sandboxes

        mock_run_openshell.side_effect = subprocess.CalledProcessError(1, "openshell")

        result = list_sandboxes()
        assert result == []

    def test_skips_table_header(self, mock_run_openshell: MagicMock) -> None:
        from shellclaw.core.sandbox import list_sandboxes

        mock_run_openshell.return_value = subprocess.CompletedProcess(
            args=[], returncode=0,
            stdout="NAME    STATE\nmy-sandbox  running\n",
            stderr=""
        )

        result = list_sandboxes()
        assert len(result) == 1
        assert result[0].name == "my-sandbox"
