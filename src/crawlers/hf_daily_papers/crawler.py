"""HuggingFace Daily Papers API crawler."""

import requests

from src.core.models import CrawlResult
from src.crawlers.base import BaseCrawler
from src.utils.logger import get_logger

logger = get_logger("crawler.hf_daily_papers")


class HFDailyPapersCrawler(BaseCrawler):
    source_name = "hf_daily_papers"
    fetcher_type = "Fetcher"
    proxy_required = True
    max_pages = 3
    base_url = "https://huggingface.co/api/daily_papers"

    def crawl(self) -> list[CrawlResult]:
        endpoint = self.config.get("api_endpoint", self.base_url)
        try:
            response = requests.get(endpoint, timeout=30)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f"[hf_daily_papers] API fetch failed: {e}")
            return []
        records = data[: self.max_pages] if isinstance(data, list) else data
        return [CrawlResult(url=endpoint, raw_json=records, metadata={"source": self.source_name})]
