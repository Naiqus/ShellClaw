from __future__ import annotations

from pathlib import Path
from unittest.mock import patch


class TestValidateDockerAvailable:
    @patch("subprocess.run")
    def test_returns_true_when_available(self, mock_run) -> None:
        from shellclaw.utils.validators import validate_docker_available

        ok, err = validate_docker_available()
        assert ok is True
        assert err is None

    @patch("subprocess.run", side_effect=FileNotFoundError)
    def test_returns_false_when_not_installed(self, mock_run) -> None:
        from shellclaw.utils.validators import validate_docker_available

        ok, err = validate_docker_available()
        assert ok is False
        assert "not installed" in (err or "")

    @patch("subprocess.run", side_effect=__import__("subprocess").CalledProcessError(1, "docker"))
    def test_returns_false_when_daemon_not_running(self, mock_run) -> None:
        from shellclaw.utils.validators import validate_docker_available

        ok, err = validate_docker_available()
        assert ok is False
        assert "not running" in (err or "")

    @patch("subprocess.run", side_effect=__import__("subprocess").TimeoutExpired("docker", 10))
    def test_returns_false_on_timeout(self, mock_run) -> None:
        from shellclaw.utils.validators import validate_docker_available

        ok, err = validate_docker_available()
        assert ok is False
        assert "timed out" in (err or "")


class TestValidateOpenshellAvailable:
    @patch("subprocess.run")
    def test_returns_true_when_available(self, mock_run) -> None:
        from shellclaw.utils.validators import validate_openshell_available

        ok, err = validate_openshell_available()
        assert ok is True

    @patch("subprocess.run", side_effect=FileNotFoundError)
    def test_returns_false_when_not_installed(self, mock_run) -> None:
        from shellclaw.utils.validators import validate_openshell_available

        ok, err = validate_openshell_available()
        assert ok is False

    @patch(
        "subprocess.run",
        side_effect=__import__("subprocess").CalledProcessError(1, "openshell"),
    )
    def test_returns_false_on_error(self, mock_run) -> None:
        from shellclaw.utils.validators import validate_openshell_available

        ok, err = validate_openshell_available()
        assert ok is False

    @patch("subprocess.run", side_effect=__import__("subprocess").TimeoutExpired("openshell", 10))
    def test_returns_false_on_timeout(self, mock_run) -> None:
        from shellclaw.utils.validators import validate_openshell_available

        ok, err = validate_openshell_available()
        assert ok is False


class TestValidateOpenclawStateExists:
    def test_returns_true_for_valid_state(self, tmp_openclaw_home: Path) -> None:
        from shellclaw.utils.validators import validate_openclaw_state_exists

        ok, err = validate_openclaw_state_exists(tmp_openclaw_home)
        assert ok is True

    def test_returns_false_for_nonexistent(self) -> None:
        from shellclaw.utils.validators import validate_openclaw_state_exists

        ok, err = validate_openclaw_state_exists(Path("/nonexistent"))
        assert ok is False

    def test_returns_false_for_missing_subdirs(self, tmp_path: Path) -> None:
        from shellclaw.utils.validators import validate_openclaw_state_exists

        state_dir = tmp_path / ".openclaw"
        state_dir.mkdir()
        # Missing 'credentials' and 'agents' subdirectories

        ok, err = validate_openclaw_state_exists(state_dir)
        assert ok is False


class TestValidateSandboxName:
    def test_valid_name(self) -> None:
        from shellclaw.utils.validators import validate_sandbox_name

        ok, _ = validate_sandbox_name("my-sandbox-1")
        assert ok is True

    def test_empty_name(self) -> None:
        from shellclaw.utils.validators import validate_sandbox_name

        ok, err = validate_sandbox_name("")
        assert ok is False

    def test_invalid_characters(self) -> None:
        from shellclaw.utils.validators import validate_sandbox_name

        ok, err = validate_sandbox_name("my sandbox!")
        assert ok is False

    def test_cannot_start_with_hyphen(self) -> None:
        from shellclaw.utils.validators import validate_sandbox_name

        ok, err = validate_sandbox_name("-invalid")
        assert ok is False
