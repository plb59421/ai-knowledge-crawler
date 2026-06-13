"""机器之心(jiqizhixin.com) 爬虫 - 国内可达的 AI 信息源"""

from scrapling import Selector
from src.crawlers.base import BaseCrawler
from src.core.models import CrawlResult
from src.utils.logger import get_logger

logger = get_logger("crawler.jiqizhixin")

JIQIZHIXIN_URL = "https://www.jiqizhixin.com/"


class JiqiZhixinCrawler(BaseCrawler):
    """机器之心爬虫，使用 Fetcher 爬取静态 HTML"""

    source_name = "jiqizhixin"
    fetcher_type = "Fetcher"
    proxy_required = False
    rate_limit_seconds = 2.0
    max_pages = 5

    def crawl(self) -> list[CrawlResult]:
        """爬取机器之心文章列表页面"""
        logger.info(f"[jiqizhixin] start crawling: {JIQIZHIXIN_URL}")

        fetcher = self.get_fetcher()
        response = fetcher.get(JIQIZHIXIN_URL)

        # 用 Selector 解析提取文章链接
        raw_html = response.html_content if hasattr(response, 'html_content') else ""
        page = Selector(raw_html)

        article_links = []
        for link in page.css("a[href]"):
            href = link.attrib.get("href", "")
            if href and "/articles/" in href:
                full_url = f"https://www.jiqizhixin.com{href}" if href.startswith("/") else href
                if full_url not in article_links:
                    article_links.append(full_url)

        logger.info(f"[jiqizhixin] found {len(article_links)} article links on listing page")

        # 爬取每篇文章详情
        results = []
        limit = min(len(article_links), self.max_pages)
        for i, url in enumerate(article_links[:limit]):
            try:
                logger.info(f"[jiqizhixin] crawling article {i+1}/{limit}: {url}")
                article_response = fetcher.get(url)
                article_html = article_response.html_content if hasattr(article_response, 'html_content') else ""

                results.append(CrawlResult(
                    url=url,
                    raw_html=article_html,
                    metadata={"source": "jiqizhixin", "fetcher": "Fetcher"},
                ))
                self._rate_limit()
            except Exception as e:
                if not self._handle_error(e, url):
                    break

        logger.info(f"[jiqizhixin] crawl finished, got {len(results)} articles")
        return results
