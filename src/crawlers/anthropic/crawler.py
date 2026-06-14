"""Anthropic Research 爬虫 - 爬取 AI 对齐与安全研究文章"""

from scrapling import Selector
from src.crawlers.base import BaseCrawler
from src.core.models import CrawlResult
from src.utils.logger import get_logger

logger = get_logger("crawler.anthropic")

class AnthropicCrawler(BaseCrawler):
    """Anthropic Research 爬虫，静态 HTML"""

    source_name = "anthropic"
    fetcher_type = "Fetcher"
    proxy_required = True
    rate_limit_seconds = 2.0
    max_pages = 5
    base_url = "https://www.anthropic.com/research"

    def crawl(self) -> list[CrawlResult]:
        """爬取 Anthropic Research 列表页，获取文章链接并逐篇爬取"""
        logger.info(f"[anthropic] start crawling: {self.base_url}")

        fetcher = self.get_fetcher()

        # 1. 获取列表页
        try:
            response = fetcher.get(self.base_url)
        except Exception as e:
            logger.error(f"[anthropic] failed to fetch listing page: {e}")
            return []

        # 2. 用 Selector 解析提取文章链接
        raw_html = response.html_content if hasattr(response, 'html_content') else ""
        page = Selector(raw_html)

        article_links = []
        for link in page.css("a[href]"):
            href = link.attrib.get("href", "")
            if (
                href
                and "/research/" in href
                and href != "/research"
                and "/research/team/" not in href
            ):
                full_url = f"https://www.anthropic.com{href}" if href.startswith("/") else href
                if full_url not in article_links:
                    article_links.append(full_url)

        logger.info(f"[anthropic] found {len(article_links)} research articles")

        # 3. 逐篇爬取详情页
        results = []
        limit = min(len(article_links), self.max_pages)
        for i, url in enumerate(article_links[:limit]):
            try:
                logger.info(f"[anthropic] crawling article {i+1}/{limit}: {url}")
                article_response = fetcher.get(url)
                article_html = article_response.html_content if hasattr(article_response, 'html_content') else ""

                results.append(CrawlResult(
                    url=url,
                    raw_html=article_html,
                    metadata={"source": "anthropic", "fetcher": "Fetcher"},
                ))
                self._rate_limit()
            except Exception as e:
                if not self._handle_error(e, url):
                    break

        logger.info(f"[anthropic] crawl finished, got {len(results)} articles")
        return results
