"""Generic crawler/parser implementations for configured sources."""

from bs4 import BeautifulSoup
import re
from scrapling import Selector

from src.core.models import Article, CrawlResult
from src.crawlers.base import BaseCrawler
from src.utils.logger import get_logger

logger = get_logger("crawler.generic")


class GenericHTMLCrawler(BaseCrawler):
    """Simple listing-page crawler for HTML sources."""

    article_path_markers: tuple[str, ...] = ("/blog/", "/post/", "/posts/", "/articles/", "/news/")
    excluded_path_markers: tuple[str, ...] = (
        "/about",
        "/tag/",
        "/tags/",
        "/label/",
        "/category/",
        "/author/",
        "/page/",
        "/rss",
    )

    def crawl(self) -> list[CrawlResult]:
        logger.info(f"[{self.source_name}] start crawling: {self.base_url}")
        fetcher = self.get_fetcher()
        try:
            response = fetcher.get(self.base_url)
        except Exception as e:
            logger.error(f"[{self.source_name}] failed to fetch listing page: {e}")
            return []

        raw_html = response.html_content if hasattr(response, "html_content") else ""
        page = Selector(raw_html)
        links = []
        for link in page.css("a[href]"):
            href = link.attrib.get("href", "")
            if not href or href in links:
                continue
            if not any(marker in href for marker in self.article_path_markers):
                continue
            if any(marker in href for marker in self.excluded_path_markers):
                continue
            if href.startswith("/"):
                base = self.base_url.rstrip("/")
                parts = base.split("/")
                href = f"{parts[0]}//{parts[2]}{href}"
            if href.rstrip("/") == self.base_url.rstrip("/"):
                continue
            path = href.split("://", 1)[-1].split("/", 1)[-1]
            if path.rstrip("/").isdigit() or re.search(r"/(?:19|20)\d{2}/?$", href):
                continue
            if href not in links:
                links.append(href)

        results = []
        for url in links[: self.max_pages]:
            try:
                article_response = fetcher.get(url)
                article_html = article_response.html_content if hasattr(article_response, "html_content") else ""
                results.append(CrawlResult(url=url, raw_html=article_html, metadata={"source": self.source_name}))
                self._rate_limit()
            except Exception as e:
                self._handle_error(e, url)
        return results


class GenericHTMLParser:
    """Parse common article HTML into Article."""

    source_name = "generic"
    id_prefix = "gen"

    def parse(self, crawl_result) -> list[Article]:
        soup = BeautifulSoup(crawl_result.raw_html, "html.parser")
        title_el = soup.find("h1") or soup.find("title")
        title = title_el.get_text(strip=True) if title_el else crawl_result.url.rstrip("/").split("/")[-1]

        content_parts = []
        for selector in ["article p", "main p", ".post-content p", ".entry-content p", "div.prose p", "p"]:
            content_parts = [p.get_text(strip=True) for p in soup.select(selector) if len(p.get_text(strip=True)) > 20]
            if content_parts:
                break

        date = ""
        time_el = soup.select_one("time")
        if time_el:
            date = time_el.get("datetime", "") or time_el.get_text(strip=True)

        article_id = f"{self.id_prefix}_{crawl_result.url.rstrip('/').split('/')[-1].replace('.html', '')}"
        return [Article(
            id=article_id,
            source=self.source_name,
            title=title,
            abstract=content_parts[0][:300] if content_parts else "",
            full_text="\n".join(content_parts),
            publish_date=date,
            url=crawl_result.url,
        )]


class GenericJSONAPIParser:
    """Parse common API JSON records into Article."""

    source_name = "generic_api"
    id_prefix = "api"

    def parse(self, crawl_result) -> list[Article]:
        raw = crawl_result.raw_json
        records = raw if isinstance(raw, list) else raw.get("data") or raw.get("papers") or raw.get("items") or []
        articles = []
        for record in records:
            if not isinstance(record, dict):
                continue
            title = record.get("title") or record.get("name") or "Untitled"
            url = record.get("url") or record.get("paperUrl") or record.get("externalIds", {}).get("ArXiv") or crawl_result.url
            article_id = f"{self.id_prefix}_{abs(hash(url or title))}"
            abstract = record.get("abstract") or record.get("summary") or record.get("description") or ""
            articles.append(Article(
                id=article_id,
                source=self.source_name,
                title=title,
                abstract=abstract[:300],
                full_text=abstract,
                authors=record.get("authors", []),
                publish_date=record.get("published") or record.get("publicationDate") or record.get("date", ""),
                url=url,
                topics=record.get("topics", []),
            ))
        return articles
