from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_subprocess_run(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Mock subprocess.run to avoid real process execution."""
    mock = MagicMock(
        return_value=subprocess.CompletedProcess(
            args=["openshell"], returncode=0, stdout="ok\n", stderr=""
        )
    )
    monkeypatch.setattr("subprocess.run", mock)
    return mock


@pytest.fixture
def tmp_shellclaw_home(tmp_path: Path) -> Path:
    """Create a temporary ~/.shellclaw directory."""
    home = tmp_path / ".shellclaw"
    home.mkdir()
    return home


@pytest.fixture
def tmp_openclaw_home(tmp_path: Path) -> Path:
    """Create a temporary ~/.openclaw directory with expected structure."""
    home = tmp_path / ".openclaw"
    home.mkdir()
    (home / "credentials").mkdir()
    (home / "agents").mkdir()
    (home / "MEMORY.md").write_text("# Memory\n")
    (home / "openclaw.json").write_text("{}")
    return home


@pytest.fixture
def sample_policy(tmp_path: Path) -> Path:
    """Create a sample policy YAML file."""
    policy = tmp_path / "policy.yaml"
    policy.write_text(
        "filesystem:\n"
        "  - path: /sandbox\n"
        "    permission: read_write\n"
        "network:\n"
        "  - endpoint: inference.local\n"
        "    action: allow\n"
    )
    return policy
