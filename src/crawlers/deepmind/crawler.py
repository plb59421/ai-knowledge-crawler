"""DeepMind Blog 爬虫 - 静态HTML + StealthyFetcher后备"""

from scrapling import Selector
from src.crawlers.base import BaseCrawler
from src.core.models import CrawlResult
from src.core.exceptions import CrawlError
from src.utils.logger import get_logger

logger = get_logger("crawler.deepmind")

DEEPMIND_BLOG_URL = "https://deepmind.google/blog/"


class DeepMindCrawler(BaseCrawler):
    """DeepMind Blog 爬虫，Fetcher主选 + StealthyFetcher后备"""

    source_name = "deepmind"
    fetcher_type = "Fetcher"
    proxy_required = True
    rate_limit_seconds = 2.0
    max_pages = 5

    def crawl(self) -> list[CrawlResult]:
        """爬取 DeepMind Blog 列表页，获取文章链接并逐篇爬取"""
        logger.info(f"[deepmind] start crawling: {DEEPMIND_BLOG_URL}")

        # 1. 尝试 Fetcher，失败则切换 StealthyFetcher
        response = None
        fetcher_used = "Fetcher"
        try:
            fetcher = self.get_fetcher("Fetcher")
            response = fetcher.get(DEEPMIND_BLOG_URL)
        except Exception as e:
            logger.warning(f"[deepmind] Fetcher failed: {e}, switching to StealthyFetcher")
            try:
                stealthy = self.get_fetcher("StealthyFetcher")
                response = stealthy.get(DEEPMIND_BLOG_URL)
                fetcher_used = "StealthyFetcher"
            except Exception as e2:
                logger.error(f"[deepmind] StealthyFetcher also failed: {e2}")
                raise CrawlError("Failed to fetch DeepMind blog", source="deepmind", url=DEEPMIND_BLOG_URL)

        # 2. 用 Selector 解析提取文章链接
        raw_html = response.html_content if hasattr(response, 'html_content') else ""
        page = Selector(raw_html)

        article_links = []
        for link in page.css("a[href]"):
            href = link.attrib.get("href", "")
            if href and "/blog/" in href and href != "/blog/":
                full_url = f"https://deepmind.google{href}" if href.startswith("/") else href
                if full_url != DEEPMIND_BLOG_URL and full_url not in article_links:
                    article_links.append(full_url)

        logger.info(f"[deepmind] found {len(article_links)} blog articles")

        # 3. 逐篇爬取详情页
        detail_fetcher = self.get_fetcher(fetcher_used)
        results = []
        limit = min(len(article_links), self.max_pages)
        for i, url in enumerate(article_links[:limit]):
            try:
                logger.info(f"[deepmind] crawling article {i+1}/{limit}: {url}")
                article_response = detail_fetcher.get(url)
                article_html = article_response.html_content if hasattr(article_response, 'html_content') else ""

                results.append(CrawlResult(
                    url=url,
                    raw_html=article_html,
                    metadata={"source": "deepmind", "fetcher": fetcher_used},
                ))
                self._rate_limit()
            except Exception as e:
                if not self._handle_error(e, url):
                    break

        logger.info(f"[deepmind] crawl finished, got {len(results)} articles")
        return results
