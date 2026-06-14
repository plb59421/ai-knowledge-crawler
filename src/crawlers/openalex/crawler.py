"""OpenAlex API crawler."""

import requests
from datetime import datetime, timedelta

from src.core.models import CrawlResult
from src.crawlers.base import BaseCrawler
from src.utils.logger import get_logger

logger = get_logger("crawler.openalex")


class OpenAlexCrawler(BaseCrawler):
    source_name = "openalex"
    fetcher_type = "Fetcher"
    proxy_required = False
    max_pages = 10
    base_url = "https://api.openalex.org/works"
    search_query = "artificial intelligence large language model"

    def crawl(self) -> list[CrawlResult]:
        since = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        params = {
            "search": self.search_query,
            "filter": f"from_publication_date:{since}",
            "sort": "publication_date:desc",
            "per-page": self.max_pages,
        }
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f"[openalex] API fetch failed: {e}")
            return []
        return [CrawlResult(url=self.base_url, raw_json=data, metadata={"source": self.source_name})]
