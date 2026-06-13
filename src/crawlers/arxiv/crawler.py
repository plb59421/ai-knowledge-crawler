"""ArXiv AI 论文爬虫 - 通过API接口获取每日新论文元数据"""

import xml.etree.ElementTree as ET
import requests
from src.crawlers.base import BaseCrawler
from src.core.models import CrawlResult
from src.utils.logger import get_logger

logger = get_logger("crawler.arxiv")

ARXIV_API_URL = "https://export.arxiv.org/api/query"
# AI 相关分类
ARXIV_CATEGORIES = ["cs.AI", "cs.CL", "cs.LG", "cs.CV", "cs.NE"]


class ArXivCrawler(BaseCrawler):
    """ArXiv AI 论文爬虫，通过 requests 直接调用 API"""

    source_name = "arxiv"
    fetcher_type = "Fetcher"  # 标记但不实际使用（API用requests）
    proxy_required = False    # ArXiv API 国内可达
    rate_limit_seconds = 3.0
    max_pages = 10

    def crawl(self) -> list[CrawlResult]:
        """通过 ArXiv API 爬取最近 AI 论文元数据"""
        # 构建查询参数
        cat_query = " OR ".join(f"cat:{c}" for c in ARXIV_CATEGORIES)
        params = {
            "search_query": cat_query,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
            "max_results": self.max_pages,
        }

        logger.info(f"[arxiv] start crawling API: cat={cat_query}, max={self.max_pages}")

        # 用 requests 直接调用 API（比 scrapling Fetcher 更可靠）
        try:
            response = requests.get(ARXIV_API_URL, params=params, timeout=30)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"[arxiv] failed to fetch API: {e}")
            return []

        raw_text = response.text

        # 解析 XML 响应
        results = []
        try:
            root = ET.fromstring(raw_text)
            ns = {"atom": "http://www.w3.org/2005/Atom"}

            for entry in root.findall("atom:entry", ns):
                title_el = entry.find("atom:title", ns)
                title = title_el.text.strip().replace("\n", " ") if title_el is not None and title_el.text else ""

                summary_el = entry.find("atom:summary", ns)
                summary = summary_el.text.strip() if summary_el is not None and summary_el.text else ""

                id_el = entry.find("atom:id", ns)
                arxiv_id = id_el.text.strip() if id_el is not None and id_el.text else ""

                pub_el = entry.find("atom:published", ns)
                published = pub_el.text.strip() if pub_el is not None and pub_el.text else ""

                pdf_url = ""
                for link in entry.findall("atom:link", ns):
                    if link.get("title") == "pdf":
                        pdf_url = link.get("href", "")
                        break

                authors = []
                for author in entry.findall("atom:author", ns):
                    name = author.find("atom:name", ns)
                    if name is not None and name.text:
                        authors.append(name.text.strip())

                categories = []
                for cat in entry.findall("atom:category", ns):
                    term = cat.get("term", "")
                    if term:
                        categories.append(term)

                short_id = arxiv_id.split("/")[-1] if "/" in arxiv_id else arxiv_id

                results.append(CrawlResult(
                    url=f"https://arxiv.org/abs/{short_id}",
                    raw_html="",
                    raw_json={
                        "arxiv_id": short_id,
                        "title": title,
                        "summary": summary,
                        "published": published,
                        "pdf_url": pdf_url,
                        "authors": authors,
                        "categories": categories,
                    },
                    metadata={"source": "arxiv", "content_type": "xml_api"},
                ))

        except ET.ParseError as e:
            logger.error(f"[arxiv] XML parse error: {e}")

        logger.info(f"[arxiv] crawl finished, got {len(results)} papers")
        return results
