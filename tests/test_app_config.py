import importlib
from pathlib import Path


def test_user_config_dir_respects_xdg(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    import app_config

    importlib.reload(app_config)
    assert app_config.USER_CONFIG_DIR == tmp_path / "SparkIDE"


def test_user_config_dir_defaults_to_home_config(monkeypatch):
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    import app_config

    importlib.reload(app_config)
    assert app_config.USER_CONFIG_DIR == Path.home() / ".config" / "SparkIDE"
