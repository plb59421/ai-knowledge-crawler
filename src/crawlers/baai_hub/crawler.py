"""BAAI Hub crawler."""

import json
import re

from src.core.models import CrawlResult
from src.crawlers.generic import GenericHTMLCrawler


class BAAIHubCrawler(GenericHTMLCrawler):
    source_name = "baai_hub"
    fetcher_type = "Fetcher"
    proxy_required = False
    max_pages = 3
    base_url = "https://hub.baai.ac.cn/"

    def crawl(self) -> list[CrawlResult]:
        response = self.fetch_url(self.base_url)
        raw_html = response.html_content if hasattr(response, "html_content") else ""
        records = self._extract_nuxt_records(raw_html)
        if records:
            return [CrawlResult(url=self.base_url, raw_json={"data": records}, metadata={"source": self.source_name})]
        return super().crawl()

    def _extract_nuxt_records(self, html: str) -> list[dict]:
        pattern = re.compile(
            r"story_info:\{.*?title:\"(?P<title>(?:\\.|[^\"\\])*)\".*?"
            r"created_at:\"(?P<created_at>(?:\\.|[^\"\\])*)\".*?"
            r"url:\"(?P<url>(?:\\.|[^\"\\])*)\".*?"
            r"content:\"(?P<content>(?:\\.|[^\"\\])*)\".*?"
            r"summary:\"(?P<summary>(?:\\.|[^\"\\])*)\"",
            re.DOTALL,
        )
        records = []
        for match in pattern.finditer(html):
            item = {key: self._decode(value) for key, value in match.groupdict().items()}
            item["id"] = abs(hash(item["title"]))
            item["source_url"] = item.get("url") or self.base_url
            records.append(item)
            if len(records) >= self.max_pages:
                break
        return records

    def _decode(self, value: str) -> str:
        try:
            return json.loads(f'"{value}"')
        except json.JSONDecodeError:
            return value
