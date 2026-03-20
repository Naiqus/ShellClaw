from __future__ import annotations

from pathlib import Path

import pytest
import yaml


class TestSettings:
    def test_defaults(self) -> None:
        from shellclaw.config.settings import Settings

        s = Settings()
        assert s.sandbox_name == "openclaw-sandbox"
        assert s.gateway_host == "localhost"
        assert s.inference_provider == "ollama"

    def test_immutable(self) -> None:
        from shellclaw.config.settings import Settings

        s = Settings()
        with pytest.raises(AttributeError):
            s.sandbox_name = "changed"  # type: ignore[misc]


class TestLoadSettings:
    def test_loads_defaults_when_no_config(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    ) -> None:
        from shellclaw.config import settings as settings_mod
        from shellclaw.config.settings import load_settings

        monkeypatch.setattr(settings_mod, "SHELLCLAW_HOME", tmp_path / ".shellclaw")

        s = load_settings()
        assert s.sandbox_name == "openclaw-sandbox"

    def test_loads_from_config_file(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        from shellclaw.config import settings as settings_mod
        from shellclaw.config.settings import load_settings

        home = tmp_path / ".shellclaw"
        home.mkdir()
        config_path = home / "config.yaml"
        config_path.write_text(yaml.dump({
            "sandbox_name": "custom-box",
            "inference_provider": "anthropic",
        }))

        monkeypatch.setattr(settings_mod, "SHELLCLAW_HOME", home)

        s = load_settings()
        assert s.sandbox_name == "custom-box"
        assert s.inference_provider == "anthropic"

    def test_env_vars_override_config(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
    ) -> None:
        from shellclaw.config import settings as settings_mod
        from shellclaw.config.settings import load_settings

        home = tmp_path / ".shellclaw"
        home.mkdir()
        config_path = home / "config.yaml"
        config_path.write_text(yaml.dump({"sandbox_name": "from-file"}))

        monkeypatch.setattr(settings_mod, "SHELLCLAW_HOME", home)
        monkeypatch.setenv("SHELLCLAW_SANDBOX_NAME", "from-env")

        s = load_settings()
        assert s.sandbox_name == "from-env"
