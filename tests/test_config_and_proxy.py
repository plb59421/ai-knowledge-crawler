from src.utils import config_loader
from src.utils.proxy_helper import detect_proxy


def _write_user_config(tmp_path, text: str, monkeypatch):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "settings.yaml").write_text("{}", encoding="utf-8")
    (config_dir / "user.yaml").write_text(text, encoding="utf-8")
    monkeypatch.setattr(config_loader, "CONFIG_ROOT", config_dir)
    config_loader.load_settings_config.cache_clear()
    config_loader.load_user_config.cache_clear()


def test_detect_proxy_reads_user_config_url(tmp_path, monkeypatch):
    _write_user_config(
        tmp_path,
        "proxy:\n  enabled: true\n  url: http://127.0.0.1:7899\n",
        monkeypatch,
    )
    monkeypatch.delenv("HTTP_PROXY", raising=False)
    monkeypatch.delenv("HTTPS_PROXY", raising=False)

    assert detect_proxy() == "http://127.0.0.1:7899"


def test_detect_proxy_can_be_disabled_by_user_config(tmp_path, monkeypatch):
    _write_user_config(tmp_path, "proxy:\n  enabled: false\n", monkeypatch)
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:7899")
    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:7899")

    assert detect_proxy() is None
