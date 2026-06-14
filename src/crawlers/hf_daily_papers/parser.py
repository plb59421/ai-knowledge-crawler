"""HuggingFace Daily Papers parser."""

from src.core.models import Article


class HFDailyPapersParser:
    def parse(self, crawl_result) -> list[Article]:
        records = crawl_result.raw_json if isinstance(crawl_result.raw_json, list) else []
        articles = []
        for record in records:
            paper = record.get("paper") if isinstance(record, dict) else {}
            if not paper:
                paper = record
            title = paper.get("title") or record.get("title") or "Untitled paper"
            paper_id = paper.get("id") or paper.get("paperId") or record.get("id") or title
            summary = paper.get("summary") or paper.get("abstract") or record.get("summary") or ""
            url = paper.get("url") or f"https://huggingface.co/papers/{paper_id}"
            articles.append(Article(
                id=f"hfpaper_{str(paper_id).replace('/', '_')}",
                source="hf_daily_papers",
                title=title,
                abstract=summary[:300],
                full_text=summary,
                authors=paper.get("authors", []),
                publish_date=paper.get("publishedAt") or record.get("publishedAt", ""),
                url=url,
            ))
        return articles
