"""OpenAI Blog 爬虫 - JS动态列表页 + 静态详情页"""

from scrapling import Selector
from src.crawlers.base import BaseCrawler
from src.core.models import CrawlResult
from src.utils.logger import get_logger

logger = get_logger("crawler.openai")

OPENAI_BLOG_URL = "https://openai.com/blog"


class OpenAICrawler(BaseCrawler):
    """OpenAI Blog 爬虫，列表页需 DynamicFetcher，详情页用 Fetcher"""

    source_name = "openai"
    fetcher_type = "DynamicFetcher"
    proxy_required = True
    rate_limit_seconds = 2.0
    max_pages = 5

    def crawl(self) -> list[CrawlResult]:
        """爬取 OpenAI Blog 列表页，获取文章链接并逐篇爬取"""
        logger.info(f"[openai] start crawling: {OPENAI_BLOG_URL}")

        # 1. 用 DynamicFetcher 获取列表页（JS动态渲染）
        dynamic_fetcher = self.get_fetcher("DynamicFetcher")
        try:
            response = dynamic_fetcher.get(
                OPENAI_BLOG_URL,
                wait_for="a[href]",
                wait_timeout=30,
            )
        except Exception as e:
            logger.error(f"[openai] failed to fetch listing page: {e}")
            return []

        # 2. 用 Selector 解析提取文章链接
        raw_html = response.html_content if hasattr(response, 'html_content') else ""
        page = Selector(raw_html)

        article_links = []
        for link in page.css("a[href]"):
            href = link.attrib.get("href", "")
            if href and "/blog/" in href and href != "/blog":
                full_url = f"https://openai.com{href}" if href.startswith("/") else href
                if full_url not in article_links:
                    article_links.append(full_url)

        logger.info(f"[openai] found {len(article_links)} blog articles")

        # 3. 用 Fetcher 逐篇爬取详情页
        static_fetcher = self.get_fetcher("Fetcher")
        results = []
        limit = min(len(article_links), self.max_pages)
        for i, url in enumerate(article_links[:limit]):
            try:
                logger.info(f"[openai] crawling article {i+1}/{limit}: {url}")
                article_response = static_fetcher.get(url)
                article_html = article_response.html_content if hasattr(article_response, 'html_content') else ""

                results.append(CrawlResult(
                    url=url,
                    raw_html=article_html,
                    metadata={"source": "openai", "fetcher": "Fetcher"},
                ))
                self._rate_limit()
            except Exception as e:
                if not self._handle_error(e, url):
                    break

        logger.info(f"[openai] crawl finished, got {len(results)} articles")
        return results
