from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

runner = CliRunner()


class TestMigrateCommand:
    @patch("shellclaw.commands.migrate.upload_to_sandbox", return_value=True)
    @patch("shellclaw.commands.migrate.exec_in_sandbox")
    def test_migrates_state(
        self,
        mock_exec: MagicMock,
        mock_upload: MagicMock,
        tmp_openclaw_home: Path,
    ) -> None:
        import subprocess

        from shellclaw.main import app

        mock_exec.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="ok", stderr=""
        )

        result = runner.invoke(
            app, ["migrate", "--source", str(tmp_openclaw_home)]
        )

        assert result.exit_code == 0
        mock_upload.assert_called_once()

    def test_fails_with_invalid_source(self) -> None:
        from shellclaw.main import app

        result = runner.invoke(
            app, ["migrate", "--source", "/nonexistent/path"]
        )

        assert result.exit_code != 0

    @patch("shellclaw.commands.migrate.upload_to_sandbox", return_value=True)
    @patch("shellclaw.commands.migrate.exec_in_sandbox")
    def test_dry_run_does_not_upload(
        self,
        mock_exec: MagicMock,
        mock_upload: MagicMock,
        tmp_openclaw_home: Path,
    ) -> None:
        from shellclaw.main import app

        result = runner.invoke(
            app, ["migrate", "--source", str(tmp_openclaw_home), "--dry-run"]
        )

        assert result.exit_code == 0
        mock_upload.assert_not_called()
