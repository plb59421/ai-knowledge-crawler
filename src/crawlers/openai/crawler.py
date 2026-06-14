"""OpenAI Blog 爬虫 - JS动态列表页 + 静态详情页"""

from scrapling import Selector
from src.crawlers.base import BaseCrawler
from src.core.models import CrawlResult
from src.utils.logger import get_logger

logger = get_logger("crawler.openai")

class OpenAICrawler(BaseCrawler):
    """OpenAI Blog 爬虫，列表页需 DynamicFetcher，详情页用 Fetcher"""

    source_name = "openai"
    fetcher_type = "DynamicFetcher"
    proxy_required = True
    rate_limit_seconds = 2.0
    max_pages = 5
    base_url = "https://openai.com/news/"

    def _status_code(self, response) -> int | None:
        for attr in ("status", "status_code"):
            value = getattr(response, attr, None)
            if isinstance(value, int):
                return value
        return None

    def crawl(self) -> list[CrawlResult]:
        """爬取 OpenAI Blog 列表页，获取文章链接并逐篇爬取"""
        logger.info(f"[openai] start crawling: {self.base_url}")

        # 1. 用 DynamicFetcher 获取列表页（JS动态渲染）
        try:
            response = self.fetch_url(
                self.base_url,
                "DynamicFetcher",
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
        ignored = {
            "/news/",
            "/news/company-announcements/",
            "/news/research/",
            "/news/product-releases/",
            "/news/safety-alignment/",
            "/news/engineering/",
            "/news/security/",
            "/news/global-affairs/",
            "/news/ai-adoption/",
            "/news/applied-ai/",
            "/zh-Hans-CN/news/",
        }
        for link in page.css("a[href]"):
            href = link.attrib.get("href", "")
            if not href or href in ignored or href.endswith("rss.xml"):
                continue
            if href.startswith(("/news/", "/index/")):
                full_url = f"https://openai.com{href}"
                if full_url.rstrip("/") != self.base_url.rstrip("/") and full_url not in article_links:
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
                status_code = self._status_code(article_response)
                if status_code and status_code >= 400:
                    logger.warning(f"[openai] skip HTTP {status_code} article: {url}")
                    continue
                article_html = article_response.html_content if hasattr(article_response, 'html_content') else ""
                if not article_html or "Forbidden" in article_html[:500] or "Access denied" in article_html[:1000]:
                    logger.warning(f"[openai] skip inaccessible article: {url}")
                    continue

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
