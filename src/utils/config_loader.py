"""Project configuration loader."""

from functools import lru_cache
from pathlib import Path

import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_ROOT = PROJECT_ROOT / "config"


@lru_cache(maxsize=1)
def load_sources_config() -> dict:
    """Load source configuration from config/sources.yaml."""
    path = CONFIG_ROOT / "sources.yaml"
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("sources", {})


@lru_cache(maxsize=1)
def load_settings_config() -> dict:
    """Load global settings from config/settings.yaml."""
    path = CONFIG_ROOT / "settings.yaml"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_source_config(source_name: str) -> dict:
    """Return the config block for one source, or an empty dict."""
    return load_sources_config().get(source_name, {})


def get_llm_config() -> dict:
    """Return the global LLM config block."""
    return load_settings_config().get("llm", {})
