"""机器之心内容解析器"""

from bs4 import BeautifulSoup
from src.core.models import Article
from src.utils.logger import get_logger

logger = get_logger("parser.jiqizhixin")


class JiqiZhixinParser:
    """解析机器之心文章页面"""

    def parse(self, crawl_result) -> list[Article]:
        url = crawl_result.url
        raw_html = crawl_result.raw_html

        soup = BeautifulSoup(raw_html, "html.parser")

        title = ""
        for sel in ["h1", ".article-title"]:
            el = soup.select_one(sel)
            if el:
                title = el.get_text(strip=True)
                break
        if not title:
            title = crawl_result.metadata.get("title") or url.split("/")[-1]

        content_parts = []
        for sel in ["div.article-content p", "div.prose p", ".post-content p", "main p", "p"]:
            for p in soup.select(sel):
                text = p.get_text(strip=True)
                if text and len(text) > 20 and text not in content_parts:
                    content_parts.append(text)
            if content_parts:
                break

        authors = []
        author_el = soup.select_one(".article-author")
        if author_el:
            authors.append(author_el.get_text(strip=True))

        date = ""
        time_el = soup.select_one("time")
        if time_el:
            date = time_el.get("datetime", "") or time_el.get_text(strip=True)
        if not date:
            date_el = soup.select_one(".article-date")
            if date_el:
                date = date_el.get_text(strip=True)

        abstract = content_parts[0][:300] if content_parts else ""
        full_text = "\n".join(content_parts)
        article_id = f"jzx_{url.split('/')[-1]}"

        logger.info(f"[jiqizhixin] parsed: {title[:50]} ({len(content_parts)} paragraphs)")

        return [Article(
            id=article_id,
            source="jiqizhixin",
            title=title,
            abstract=abstract,
            full_text=full_text,
            authors=authors,
            publish_date=date,
            url=url,
        )]
