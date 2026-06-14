"""Proxy detection and environment helpers."""

import os
import socket

from src.utils.config_loader import get_proxy_config
from src.utils.logger import get_logger

logger = get_logger("proxy_helper")

DEFAULT_PORTS = [7899, 7897, 7898]


def _check_port_open(host: str, port: int, timeout: int = 2) -> bool:
    """Return True when a TCP port accepts connections."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def detect_proxy() -> str | None:
    """Detect a proxy from user config, environment, or local ports."""
    config = get_proxy_config()
    if config.get("enabled") is False:
        logger.info("proxy disabled by config")
        return None

    configured_url = config.get("url")
    if configured_url:
        logger.info(f"proxy from config: {configured_url}")
        return configured_url

    proxy_url = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")
    if proxy_url and proxy_url not in ("None", "none", ""):
        logger.info(f"proxy from env: {proxy_url}")
        return proxy_url

    if config.get("auto_detect", True) is False:
        logger.info("proxy auto-detect disabled")
        return None

    host = config.get("host", "127.0.0.1")
    ports = config.get("ports", DEFAULT_PORTS) or DEFAULT_PORTS
    for port in ports:
        if _check_port_open(host, int(port)):
            proxy_url = f"http://{host}:{port}"
            logger.info(f"proxy auto-detected: {proxy_url}")
            return proxy_url

    logger.info("no proxy available")
    return None


def get_proxy_dict(proxy_url: str) -> dict:
    """Build a requests-compatible proxy dictionary."""
    return {"http": proxy_url, "https": proxy_url}


def setup_proxy_env(proxy_url: str):
    """Set proxy environment variables for non-Scrapling HTTP requests."""
    os.environ["HTTP_PROXY"] = proxy_url
    os.environ["HTTPS_PROXY"] = proxy_url
    os.environ["http_proxy"] = proxy_url
    os.environ["https_proxy"] = proxy_url
    logger.info(f"proxy env vars set: {proxy_url}")


def clear_proxy_env():
    """Clear proxy environment variables."""
    for var in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
        if var in os.environ:
            del os.environ[var]
    logger.info("proxy env vars cleared")


def is_proxy_available() -> bool:
    """Return True when proxy detection finds a usable proxy."""
    return detect_proxy() is not None
