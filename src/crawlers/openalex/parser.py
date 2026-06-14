"""OpenAlex parser."""

from src.core.models import Article


class OpenAlexParser:
    source_name = "openalex"
    id_prefix = "oa"

    def parse(self, crawl_result) -> list[Article]:
        records = crawl_result.raw_json.get("results", []) if isinstance(crawl_result.raw_json, dict) else []
        articles = []
        for record in records:
            if not isinstance(record, dict):
                continue
            title = record.get("title") or record.get("display_name") or "Untitled"
            url = self._url(record) or crawl_result.url
            abstract = self._abstract(record.get("abstract_inverted_index") or {})
            authors = [
                item.get("author", {}).get("display_name", "")
                for item in record.get("authorships", [])
                if item.get("author", {}).get("display_name")
            ]
            topics = [
                topic.get("display_name", "")
                for topic in record.get("topics", [])
                if topic.get("display_name")
            ]
            article_id = self._article_id(record, url)
            articles.append(Article(
                id=article_id,
                source=self.source_name,
                title=title,
                abstract=abstract[:300],
                full_text=abstract,
                authors=authors,
                publish_date=record.get("publication_date") or "",
                url=url,
                topics=topics,
            ))
        return articles

    def _url(self, record: dict) -> str:
        location = record.get("primary_location") or {}
        source_url = location.get("landing_page_url") or location.get("pdf_url")
        ids = record.get("ids") or {}
        return source_url or ids.get("doi") or ids.get("openalex") or record.get("id", "")

    def _article_id(self, record: dict, url: str) -> str:
        raw_id = record.get("id") or url or record.get("title", "")
        return f"{self.id_prefix}_{raw_id.rstrip('/').split('/')[-1].replace(':', '_')}"

    def _abstract(self, inverted_index: dict) -> str:
        if not isinstance(inverted_index, dict) or not inverted_index:
            return ""
        positioned = []
        for word, positions in inverted_index.items():
            for position in positions:
                positioned.append((position, word))
        return " ".join(word for _, word in sorted(positioned))
