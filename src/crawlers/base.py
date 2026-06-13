"""AI前沿知识爬虫 - 爬虫基类"""

import time
from abc import ABC, abstractmethod
from scrapling import Fetcher, DynamicFetcher, StealthyFetcher, AsyncFetcher
from src.core.models import CrawlResult
from src.core.exceptions import CrawlError
from src.utils.proxy_helper import detect_proxy, get_proxy_dict, clear_proxy_env
from src.utils.logger import get_logger

logger = get_logger("crawler.base")

# Fetcher 类型映射
FETCHER_MAP = {
    "Fetcher": Fetcher,
    "DynamicFetcher": DynamicFetcher,
    "StealthyFetcher": StealthyFetcher,
    "AsyncFetcher": AsyncFetcher,
}


class BaseCrawler(ABC):
    """所有爬虫的抽象基类"""

    source_name: str = ""
    fetcher_type: str = "Fetcher"
    proxy_required: bool = True
    rate_limit_seconds: float = 1.0
    max_pages: int = 5

    def __init__(self, proxy_required: bool = True):
        self.proxy_required = proxy_required
        self.proxy_url = None
        self._setup_proxy()

    def _setup_proxy(self):
        """配置代理"""
        if self.proxy_required:
            self.proxy_url = detect_proxy()
            if self.proxy_url:
                logger.info(f"[{self.source_name}] proxy: {self.proxy_url}")
            else:
                logger.warning(f"[{self.source_name}] proxy required but not available")
        else:
            clear_proxy_env()
            logger.info(f"[{self.source_name}] no proxy needed")

    def get_fetcher(self, fetcher_type: str = None) -> Fetcher | DynamicFetcher | StealthyFetcher:
        """获取指定类型的 Fetcher，自动注入代理配置"""
        ft = fetcher_type or self.fetcher_type
        fetcher_cls = FETCHER_MAP.get(ft, Fetcher)

        fetcher_args = {}
        if self.proxy_url:
            fetcher_args["proxies"] = get_proxy_dict(self.proxy_url)

        return fetcher_cls(**fetcher_args)

    def _rate_limit(self):
        """请求间速率控制"""
        time.sleep(self.rate_limit_seconds)

    def _handle_error(self, exception: Exception, url: str) -> bool:
        """错误处理，返回 True 表示应该继续，False 表示应该中止"""
        logger.error(f"[{self.source_name}] error crawling {url}: {exception}")

        # 连接超时或网络错误：继续尝试下一个 URL
        if isinstance(exception, (ConnectionError, TimeoutError)):
            return True

        # HTTP 429 速率限制：等待更长时间后继续
        if hasattr(exception, 'response') and hasattr(exception.response, 'status_code'):
            if exception.response.status_code == 429:
                logger.warning(f"[{self.source_name}] rate limited, backing off")
                time.sleep(5)
                return True

        # 其他错误：继续但不重试
        return True

    @abstractmethod
    def crawl(self) -> list[CrawlResult]:
        """执行爬取，返回原始结果列表"""
        pass