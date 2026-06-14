import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(autouse=True)
def clear_config_cache():
    from src.utils import config_loader

    config_loader.load_settings_config.cache_clear()
    config_loader.load_sources_config.cache_clear()
    config_loader.load_user_config.cache_clear()
    yield
    config_loader.load_settings_config.cache_clear()
    config_loader.load_sources_config.cache_clear()
    config_loader.load_user_config.cache_clear()
