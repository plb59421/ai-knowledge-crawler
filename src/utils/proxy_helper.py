"""代理检测与注入工具"""

import os
import socket
from src.utils.logger import get_logger

logger = get_logger("proxy_helper")

DEFAULT_PORTS = [7899, 7897, 7898]


def _check_port_open(host: str, port: int, timeout: int = 2) -> bool:
    """检查端口是否开放"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False


def detect_proxy() -> str | None:
    """检测本地代理，返回代理 URL 或 None

    检测顺序：
    1. HTTPS_PROXY / HTTP_PROXY 环境变量
    2. Clash Verge 本地端口 (7899, 7897, 7898)
    """
    # 优先检查环境变量
    proxy_url = os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY")
    if proxy_url and proxy_url not in ("None", "none", ""):
        logger.info(f"proxy from env: {proxy_url}")
        return proxy_url

    # 检测 Clash 端口
    for port in DEFAULT_PORTS:
        if _check_port_open("127.0.0.1", port):
            proxy_url = f"http://127.0.0.1:{port}"
            logger.info(f"proxy auto-detected: {proxy_url}")
            return proxy_url

    logger.info("no proxy available")
    return None


def get_proxy_dict(proxy_url: str) -> dict:
    """构建 Scrapling Fetcher 代理字典"""
    return {"http": proxy_url, "https": proxy_url}


def setup_proxy_env(proxy_url: str):
    """设置代理环境变量（供非 Scrapling 的 HTTP 请求使用）"""
    os.environ["HTTP_PROXY"] = proxy_url
    os.environ["HTTPS_PROXY"] = proxy_url
    os.environ["http_proxy"] = proxy_url
    os.environ["https_proxy"] = proxy_url
    logger.info(f"proxy env vars set: {proxy_url}")


def clear_proxy_env():
    """清除代理环境变量"""
    for var in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
        if var in os.environ:
            del os.environ[var]
    logger.info("proxy env vars cleared")


def is_proxy_available() -> bool:
    """检查代理是否可用"""
    return detect_proxy() is not None