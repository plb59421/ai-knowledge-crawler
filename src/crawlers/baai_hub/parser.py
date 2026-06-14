"""BAAI Hub parser."""

from src.core.models import Article
from src.crawlers.generic import GenericHTMLParser


class BAAIHubParser(GenericHTMLParser):
    source_name = "baai_hub"
    id_prefix = "baai"

    def parse(self, crawl_result) -> list[Article]:
        records = crawl_result.raw_json.get("data", []) if isinstance(crawl_result.raw_json, dict) else []
        if not records:
            return super().parse(crawl_result)

        articles = []
        for record in records:
            title = record.get("title") or "Untitled"
            summary = record.get("summary") or ""
            content = record.get("content") or summary
            articles.append(Article(
                id=f"{self.id_prefix}_{record.get('id', abs(hash(title)))}",
                source=self.source_name,
                title=title,
                abstract=summary[:300],
                full_text=content,
                publish_date=(record.get("created_at") or "")[:10],
                url=record.get("source_url") or record.get("url") or crawl_result.url,
            ))
        return articles
