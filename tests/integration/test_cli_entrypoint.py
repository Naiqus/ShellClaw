from __future__ import annotations

import subprocess
import sys


class TestCliEntrypoint:
    def test_python_m_shows_help(self) -> None:
        """Verify 'python -m shellclaw.main --help' produces output (not silent exit)."""
        result = subprocess.run(
            [sys.executable, "-m", "shellclaw.main", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0
        assert "shellclaw" in result.stdout.lower()
        assert "COMMAND" in result.stdout

    def test_python_m_version(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "shellclaw.main", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        assert result.returncode == 0
        assert "shellclaw" in result.stdout

    def test_python_m_no_args_shows_help(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "shellclaw.main"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        # Typer returns exit code 2 with no_args_is_help=True
        assert result.returncode == 2
        assert "COMMAND" in result.stdout
