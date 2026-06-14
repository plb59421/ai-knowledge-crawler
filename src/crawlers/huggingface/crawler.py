"""HuggingFace Blog 爬虫"""

from scrapling import Selector
from src.crawlers.base import BaseCrawler
from src.core.models import CrawlResult
from src.utils.logger import get_logger

logger = get_logger("crawler.huggingface")

class HuggingFaceCrawler(BaseCrawler):
    """HuggingFace Blog 爬虫，使用 Fetcher 爬取静态 HTML"""

    source_name = "huggingface"
    fetcher_type = "Fetcher"
    proxy_required = True
    rate_limit_seconds = 1.0
    max_pages = 5
    base_url = "https://huggingface.co/blog"

    def crawl(self) -> list[CrawlResult]:
        """爬取 HuggingFace Blog 页面"""
        logger.info(f"[huggingface] start crawling: {self.base_url}")

        fetcher = self.get_fetcher()
        response = fetcher.get(self.base_url)

        # 用 Selector 解析提取文章链接
        raw_html = response.html_content if hasattr(response, 'html_content') else ""
        page = Selector(raw_html)

        blog_links = []
        ignored_paths = {
            "/blog/community",
        }
        for link in page.css("a[href]"):
            href = link.attrib.get("href", "")
            path = href.split("?", 1)[0].rstrip("/")
            if href and "/blog/" in href and href != "/blog" and path not in ignored_paths:
                full_url = f"https://huggingface.co{href}" if href.startswith("/") else href
                if full_url not in blog_links:
                    blog_links.append(full_url)

        logger.info(f"[huggingface] found {len(blog_links)} blog links on listing page")

        # 爬取每篇文章详情
        results = []
        limit = min(len(blog_links), self.max_pages)
        for i, url in enumerate(blog_links[:limit]):
            try:
                logger.info(f"[huggingface] crawling article {i+1}/{limit}: {url}")
                article_response = fetcher.get(url)
                article_html = article_response.html_content if hasattr(article_response, 'html_content') else ""

                results.append(CrawlResult(
                    url=url,
                    raw_html=article_html,
                    metadata={"source": "huggingface", "fetcher": "Fetcher"},
                ))
                self._rate_limit()
            except Exception as e:
                if not self._handle_error(e, url):
                    break

        logger.info(f"[huggingface] crawl finished, got {len(results)} articles")
        return results
