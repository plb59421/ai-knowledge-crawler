"""The Gradient crawler."""

import requests

from src.core.models import CrawlResult
from src.crawlers.base import BaseCrawler
from src.utils.logger import get_logger
from src.utils.proxy_helper import get_proxy_dict

logger = get_logger("crawler.the_gradient")


class TheGradientCrawler(BaseCrawler):
    source_name = "the_gradient"
    fetcher_type = "Fetcher"
    proxy_required = True
    max_pages = 3
    base_url = "https://thegradientpub.substack.com/api/v1/archive"

    def crawl(self) -> list[CrawlResult]:
        logger.info(f"[{self.source_name}] start crawling archive API")
        params = {
            "sort": "new",
            "search": "",
            "offset": 0,
            "limit": self.max_pages,
        }
        proxies = get_proxy_dict(self.proxy_url) if self.proxy_url else None

        try:
            response = requests.get(self.base_url, params=params, proxies=proxies, timeout=30)
            response.raise_for_status()
            records = response.json()
        except Exception as exc:
            logger.error(f"[{self.source_name}] failed to fetch archive API: {exc}")
            return []

        if not isinstance(records, list):
            logger.warning(f"[{self.source_name}] archive API returned unexpected payload")
            return []

        article_records = [
            record for record in records
            if isinstance(record, dict)
            and record.get("title")
            and not record.get("is_geoblocked")
        ][: self.max_pages]

        logger.info(f"[{self.source_name}] archive records: {len(article_records)}")
        return [
            CrawlResult(
                url=self.base_url,
                raw_json={"data": article_records},
                metadata={"source": self.source_name},
            )
        ]
