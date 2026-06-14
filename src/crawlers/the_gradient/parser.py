"""The Gradient parser."""

from bs4 import BeautifulSoup

from src.core.models import Article
from src.crawlers.generic import GenericHTMLParser


class TheGradientParser(GenericHTMLParser):
    source_name = "the_gradient"
    id_prefix = "grad"

    def parse(self, crawl_result) -> list[Article]:
        records = []
        if isinstance(crawl_result.raw_json, dict):
            records = crawl_result.raw_json.get("data") or []
        elif isinstance(crawl_result.raw_json, list):
            records = crawl_result.raw_json

        if not records:
            return super().parse(crawl_result)

        articles = []
        for record in records:
            if not isinstance(record, dict):
                continue

            title = record.get("title") or record.get("social_title") or "Untitled"
            url = (
                record.get("canonical_url")
                or record.get("web_url")
                or record.get("url")
                or crawl_result.url
            )
            body_html = record.get("body_html") or record.get("description") or ""
            full_text = self._html_to_text(body_html)
            abstract = (
                record.get("subtitle")
                or record.get("description")
                or record.get("search_engine_description")
                or full_text[:300]
            )
            publish_date = (record.get("post_date") or "")[:10]
            authors = self._authors(record)
            article_id = f"{self.id_prefix}_{record.get('id') or record.get('slug') or abs(hash(url or title))}"

            articles.append(Article(
                id=article_id,
                source=self.source_name,
                title=title,
                abstract=self._html_to_text(abstract)[:500],
                full_text=full_text or self._html_to_text(abstract),
                authors=authors,
                publish_date=publish_date,
                url=url,
                topics=[tag.get("name") for tag in record.get("postTags", []) if isinstance(tag, dict) and tag.get("name")],
            ))

        return articles

    def _html_to_text(self, value: str) -> str:
        if not value:
            return ""
        soup = BeautifulSoup(value, "html.parser")
        return "\n".join(
            part.strip()
            for part in soup.get_text("\n", strip=True).splitlines()
            if part.strip()
        )

    def _authors(self, record: dict) -> list[str]:
        authors = []
        for byline in record.get("publishedBylines") or []:
            if not isinstance(byline, dict):
                continue
            name = byline.get("name") or byline.get("handle")
            if name and name not in authors:
                authors.append(name)
        return authors
