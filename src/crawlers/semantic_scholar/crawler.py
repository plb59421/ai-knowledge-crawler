"""Semantic Scholar API crawler."""

import requests

from src.core.models import CrawlResult
from src.crawlers.base import BaseCrawler
from src.utils.logger import get_logger

logger = get_logger("crawler.semantic_scholar")


class SemanticScholarCrawler(BaseCrawler):
    source_name = "semantic_scholar"
    fetcher_type = "Fetcher"
    proxy_required = True
    max_pages = 3
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"

    def crawl(self) -> list[CrawlResult]:
        params = {
            "query": "artificial intelligence large language model",
            "limit": self.max_pages,
            "fields": "title,abstract,authors,url,publicationDate",
        }
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f"[semantic_scholar] API fetch failed: {e}")
            return []
        return [CrawlResult(url=self.base_url, raw_json=data, metadata={"source": self.source_name})]
