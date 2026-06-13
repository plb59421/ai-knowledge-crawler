"""HuggingFace Blog 内容解析器"""

from bs4 import BeautifulSoup
from src.core.models import Article
from src.utils.logger import get_logger

logger = get_logger("parser.huggingface")


class HuggingFaceParser:
    """解析 HuggingFace Blog 页面，提取标题和内容"""

    def parse(self, crawl_result) -> list[Article]:
        url = crawl_result.url
        raw_html = crawl_result.raw_html

        soup = BeautifulSoup(raw_html, "html.parser")

        title = ""
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)
        else:
            title = url.split("/")[-1]

        content_parts = []
        for p in soup.select("div.prose p"):
            text = p.get_text(strip=True)
            if text:
                content_parts.append(text)

        authors = []
        for a_el in soup.select("a.author-link"):
            name = a_el.get_text(strip=True)
            if name:
                authors.append(name)

        date = ""
        time_el = soup.select_one("time")
        if time_el:
            date = time_el.get("datetime", "") or time_el.get_text(strip=True)

        abstract = content_parts[0][:300] if content_parts else ""
        full_text = "\n".join(content_parts)
        article_id = f"hf_{url.split('/')[-1]}"

        logger.info(f"[huggingface] parsed: {title[:50]} ({len(content_parts)} paragraphs)")

        return [Article(
            id=article_id,
            source="huggingface",
            title=title,
            abstract=abstract,
            full_text=full_text,
            authors=authors,
            publish_date=date,
            url=url,
        )]
