"""量子位 内容解析器 - 基于真实HTML结构: div.article (h1, p, span.date)"""

from bs4 import BeautifulSoup
from src.core.models import Article
from src.utils.logger import get_logger

logger = get_logger("parser.qbitai")


class QbitAIParser:
    """解析量子位文章页面"""

    def parse(self, crawl_result) -> list[Article]:
        url = crawl_result.url
        raw_html = crawl_result.raw_html

        soup = BeautifulSoup(raw_html, "html.parser")

        # 标题: div.article h1
        title = ""
        h1 = soup.select_one("div.article h1")
        if h1:
            title = h1.get_text(strip=True)
        else:
            h1 = soup.find("h1")
            if h1:
                title = h1.get_text(strip=True)
            else:
                title = url.split("/")[-1]

        # 正文: div.article p (直接子元素)
        content_parts = []
        article_div = soup.select_one("div.article")
        if article_div:
            for p in article_div.find_all("p", recursive=False):
                text = p.get_text(strip=True)
                if text and len(text) > 10:
                    content_parts.append(text)

        # 如果没找到 div.article，尝试更宽泛的选择器
        if not content_parts:
            for p in soup.select("div.content p"):
                text = p.get_text(strip=True)
                if text and len(text) > 15:
                    content_parts.append(text)

        # 日期: div.article span.date
        date = ""
        date_el = soup.select_one("div.article span.date")
        if date_el:
            date = date_el.get_text(strip=True)
        else:
            time_el = soup.select_one("time")
            if time_el:
                date = time_el.get("datetime", "") or time_el.get_text(strip=True)

        url_id = url.split("/")[-1].replace(".html", "") if ".html" in url else url.split("/")[-1]
        article_id = f"qbit_{url_id}"

        abstract = content_parts[0][:300] if content_parts else ""
        full_text = "\n".join(content_parts)

        logger.info(f"[qbitai] parsed: {title[:50]} ({len(content_parts)} paragraphs)")

        return [Article(
            id=article_id,
            source="qbitai",
            title=title,
            abstract=abstract,
            full_text=full_text,
            publish_date=date,
            url=url,
        )]
