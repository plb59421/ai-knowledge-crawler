"""ArXiv 论文内容解析器 - 从 API XML 数据解析为 Article"""

from src.core.models import Article
from src.crawlers.arxiv.pdf_extractor import PDFExtractor
from src.utils.config_loader import get_source_config
from src.utils.logger import get_logger

logger = get_logger("parser.arxiv")


class ArXivParser:
    """解析 ArXiv API 返回的论文元数据"""

    def __init__(self, pdf_extractor: PDFExtractor = None):
        self.config = get_source_config("arxiv")
        self.pdf_extractor = pdf_extractor or PDFExtractor()

    def parse(self, crawl_result) -> list[Article]:
        url = crawl_result.url
        raw_json = crawl_result.raw_json

        # 如果有 JSON 数据（来自 API），直接提取
        if raw_json and "arxiv_id" in raw_json:
            arxiv_id = raw_json["arxiv_id"]
            title = raw_json.get("title", "")
            summary = raw_json.get("summary", "")
            published = raw_json.get("published", "")
            authors = raw_json.get("authors", [])
            categories = raw_json.get("categories", [])
            pdf_url = raw_json.get("pdf_url", "")
            full_text = summary

            if self.config.get("pdf_download") and pdf_url:
                extracted = self.pdf_extractor.extract(pdf_url, arxiv_id)
                if extracted:
                    full_text = extracted

            article_id = f"arx_{arxiv_id}"

            logger.info(f"[arxiv] parsed paper: {title[:60]} ({len(categories)} categories)")

            article = Article(
                id=article_id,
                source="arxiv",
                title=title,
                abstract=summary[:300],
                full_text=full_text,
                authors=authors,
                publish_date=published[:10] if published else "",  # 截取日期部分
                url=f"https://arxiv.org/abs/{arxiv_id}",
                topics=categories,
            )

            # 如有 PDF URL，存入 metadata 方便后续下载
            if pdf_url:
                article.topics = categories + [f"pdf:{pdf_url}"]

            return [article]

        # 如果只有 HTML（来自解析失败的回退）
        logger.warning(f"[arxiv] no JSON data in crawl_result, skipping: {url}")
        return []
