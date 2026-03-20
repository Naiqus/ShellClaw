from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_run_openshell() -> MagicMock:
    with patch("shellclaw.core.policy.run_openshell") as mock:
        mock.return_value = subprocess.CompletedProcess(
            args=["openshell"], returncode=0, stdout="", stderr=""
        )
        yield mock


class TestLoadPolicy:
    def test_loads_valid_yaml(self, sample_policy: Path) -> None:
        from shellclaw.core.policy import load_policy

        policy = load_policy(sample_policy)
        assert isinstance(policy, dict)
        assert "filesystem" in policy
        assert "network" in policy

    def test_raises_on_nonexistent_file(self) -> None:
        from shellclaw.core.policy import load_policy

        with pytest.raises(FileNotFoundError):
            load_policy(Path("/nonexistent/policy.yaml"))

    def test_raises_on_invalid_yaml(self, tmp_path: Path) -> None:
        from shellclaw.core.policy import load_policy

        bad_file = tmp_path / "bad.yaml"
        bad_file.write_text("{{invalid yaml::")

        with pytest.raises(ValueError, match="Invalid YAML"):
            load_policy(bad_file)


class TestValidatePolicy:
    def test_valid_policy_returns_no_errors(self) -> None:
        from shellclaw.core.policy import validate_policy

        policy = {
            "filesystem": [{"path": "/sandbox", "permission": "read_write"}],
            "network": [{"endpoint": "inference.local", "action": "allow"}],
        }

        errors = validate_policy(policy)
        assert errors == []

    def test_missing_filesystem_section(self) -> None:
        from shellclaw.core.policy import validate_policy

        errors = validate_policy({"network": []})
        assert any("filesystem" in e for e in errors)

    def test_missing_network_section(self) -> None:
        from shellclaw.core.policy import validate_policy

        errors = validate_policy({"filesystem": []})
        assert any("network" in e for e in errors)

    def test_empty_dict_returns_errors(self) -> None:
        from shellclaw.core.policy import validate_policy

        errors = validate_policy({})
        assert len(errors) >= 2


class TestApplyPolicy:
    def test_calls_policy_set(
        self, mock_run_openshell: MagicMock, sample_policy: Path
    ) -> None:
        from shellclaw.core.policy import apply_policy

        result = apply_policy("my-sandbox", sample_policy)

        assert result is True
        args = mock_run_openshell.call_args[0][0]
        assert "policy" in args
        assert "set" in args

    def test_returns_false_on_failure(
        self, mock_run_openshell: MagicMock, sample_policy: Path
    ) -> None:
        from shellclaw.core.policy import apply_policy

        mock_run_openshell.side_effect = subprocess.CalledProcessError(1, "openshell")

        result = apply_policy("my-sandbox", sample_policy)
        assert result is False
