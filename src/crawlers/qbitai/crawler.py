"""量子位 爬虫 - WordPress静态站点，不需代理"""

from scrapling import Selector
from src.crawlers.base import BaseCrawler
from src.core.models import CrawlResult
from src.utils.logger import get_logger

logger = get_logger("crawler.qbitai")

class QbitAICrawler(BaseCrawler):
    """量子位爬虫，WordPress 系站点，静态 HTML"""

    source_name = "qbitai"
    fetcher_type = "Fetcher"
    proxy_required = False
    rate_limit_seconds = 2.0
    max_pages = 5
    base_url = "https://www.qbitai.com/"

    def crawl(self) -> list[CrawlResult]:
        """爬取量子位主页，获取最新文章链接"""
        logger.info(f"[qbitai] start crawling: {self.base_url}")

        fetcher = self.get_fetcher()

        try:
            response = fetcher.get(self.base_url)
        except Exception as e:
            logger.error(f"[qbitai] failed to fetch homepage: {e}")
            return []

        # 获取原始 HTML 并用 Selector 解析链接
        raw_html = response.html_content if hasattr(response, 'html_content') else ""
        page = Selector(raw_html)

        # 提取文章链接 (WordPress 文章 URL 格式: qbitai.com/YYYY/MM/{id}.html)
        article_links = []
        for link in page.css("a[href]"):
            href = link.attrib.get("href", "")
            if href and "qbitai.com" in href and ".html" in href:
                if href not in article_links:
                    article_links.append(href)

        logger.info(f"[qbitai] found {len(article_links)} articles")

        # 逐篇爬取详情页
        results = []
        limit = min(len(article_links), self.max_pages)
        for i, url in enumerate(article_links[:limit]):
            try:
                logger.info(f"[qbitai] crawling article {i+1}/{limit}: {url}")
                article_response = fetcher.get(url)
                article_html = article_response.html_content if hasattr(article_response, 'html_content') else ""

                results.append(CrawlResult(
                    url=url,
                    raw_html=article_html,
                    metadata={"source": "qbitai", "fetcher": "Fetcher"},
                ))
                self._rate_limit()
            except Exception as e:
                if not self._handle_error(e, url):
                    break

        logger.info(f"[qbitai] crawl finished, got {len(results)} articles")
        return results
