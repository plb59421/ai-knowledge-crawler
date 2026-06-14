from datetime import datetime
import json
from pathlib import Path

from src.core.models import Article, ArticleAnalysis
from src.core.registry import CrawlerRegistry
from src.storage.knowledge_store import KnowledgeStore


class DummyCrawler:
    source_name = "dummy"
    fetcher_type = "Fetcher"
    proxy_required = False


class DummyParser:
    pass


def test_article_to_dict():
    article = Article(
        id="a1",
        source="unit",
        title="Unit Test",
        abstract="Short",
        full_text="Long text",
        authors=["Ada"],
        publish_date="2026-06-01",
        url="https://example.com/a1",
        topics=["ai"],
        relevance_score=7.5,
        analysis=ArticleAnalysis(core_points="Core", importance_score=8.0),
    )

    data = article.to_dict()

    assert data["id"] == "a1"
    assert data["source"] == "unit"
    assert data["title"] == "Unit Test"
    assert data["authors"] == ["Ada"]
    assert data["topics"] == ["ai"]
    assert data["relevance_score"] == 7.5
    assert data["analysis"]["core_points"] == "Core"
    assert data["tags"] == {"industries": [], "technologies": [], "content_types": []}
    assert data["rank_score"] == 0.0


def test_registry_register_get_list_has():
    CrawlerRegistry.register("unit_dummy", DummyCrawler, DummyParser)

    assert CrawlerRegistry.has("unit_dummy")
    assert "unit_dummy" in CrawlerRegistry.list_all()
    assert CrawlerRegistry.get("unit_dummy") == (DummyCrawler, DummyParser)


def test_knowledge_store_writes_and_deduplicates(tmp_path):
    store = KnowledgeStore(root=tmp_path)
    article = Article(
        id="a1",
        source="unit",
        title="Same Title",
        full_text="Body",
        url="https://example.com/a1",
    )
    stored_at = datetime(2026, 6, 14, 8, 0, 0)

    first_path = store.store(article, stored_at=stored_at)
    second_path = store.store(article, stored_at=stored_at)
    same_title_path = store.store(
        Article(
            id="a2",
            source="unit",
            title="Same Title",
            full_text="Different body",
            url="https://example.com/a2",
        ),
        stored_at=stored_at,
    )

    assert first_path
    assert second_path == ""
    assert same_title_path == ""
    assert (tmp_path / "by_source" / "unit" / "2026" / "06" / "2026-06-14.json").exists()
    assert (tmp_path / "by_time" / "2026" / "06" / "2026-06-14.json").exists()
    assert (tmp_path / "by_topic" / "uncategorized" / "2026" / "06" / "2026-06-14.json").exists()
    assert (tmp_path / "index" / "url_index.json").exists()
    assert (tmp_path / "index" / "full_text_index.json").exists()
    assert (tmp_path / "metadata" / "dedup_records.json").exists()
    assert list((tmp_path / "exports" / "markdown" / "unit").glob("*.md"))


def test_knowledge_store_updates_existing_article(tmp_path):
    store = KnowledgeStore(root=tmp_path)
    article = Article(id="a1", source="unit", title="Title", full_text="old", url="https://example.com/a1")
    path = store.store(article, stored_at=datetime(2026, 6, 14, 8, 0, 0))

    updated = Article(id="a1", source="unit", title="Title", full_text="new", url="https://example.com/a1")
    update_path = store.update_existing(updated, stored_at=datetime(2026, 6, 14, 9, 0, 0))

    assert update_path == path
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    assert data[0]["full_text"] == "new"


def test_knowledge_store_records_history(tmp_path):
    store = KnowledgeStore(root=tmp_path)

    store.record_crawl_history([
        {"source": "unit", "crawled": 1, "parsed": 1, "stored": 1, "error": ""}
    ])

    assert (tmp_path / "metadata" / "crawl_history.json").exists()
    report_path = store.write_daily_report([
        {"source": "unit", "crawled": 1, "parsed": 1, "stored": 1, "error": ""}
    ], report_date=datetime(2026, 6, 14, 8, 0, 0))
    assert report_path.endswith("daily_report_2026-06-14.json")


def test_knowledge_store_deduplicates_across_dates(tmp_path):
    store = KnowledgeStore(root=tmp_path)
    article = Article(
        id="a1",
        source="unit",
        title="Cross Date Title",
        full_text="Body",
        url="https://example.com/cross-date",
    )

    first_path = store.store(article, stored_at=datetime(2026, 6, 14, 8, 0, 0))
    second_path = store.store(article, stored_at=datetime(2026, 6, 15, 8, 0, 0))

    assert first_path
    assert second_path == ""
