from datetime import datetime
import json

from src.core.models import Article
from src.ranking.pipeline import enrich_article
from src.ranking.report_data import ReportDataExporter
from src.storage.knowledge_store import KnowledgeStore


def _store_article(root, article: Article):
    stored_at = datetime.fromisoformat(article.publish_date)
    KnowledgeStore(root=root).store(enrich_article(article), stored_at=stored_at)


def test_report_data_exporter_writes_latest_and_dated_json(tmp_path):
    _store_article(
        tmp_path,
        Article(
            id="g1",
            source="qbitai",
            title="新模型发布 GitHub HuggingFace API",
            abstract="一个面向开发者的新模型发布，包含 API、代码和 benchmark 指标。",
            full_text="参数 7B，benchmark 提升 20%，提供 GitHub、HuggingFace、API 和教程。",
            publish_date="2026-06-14",
            url="https://example.com/g1",
        ),
    )
    _store_article(
        tmp_path,
        Article(
            id="a1",
            source="arxiv",
            title="LLM Agent Benchmark with New Method",
            abstract="We propose a method, dataset and benchmark. Accuracy improves by 12.5%.",
            publish_date="2026-06-14",
            url="https://arxiv.org/abs/a1",
        ),
    )

    result = ReportDataExporter(tmp_path).export(date="2026-06-14", pass_score=0)

    latest_path = tmp_path / "exports" / "data" / "report_latest.json"
    dated_path = tmp_path / "exports" / "data" / "report_2026-06-14.json"
    assert result["latest_path"] == str(latest_path)
    assert latest_path.exists()
    assert dated_path.exists()

    payload = json.loads(latest_path.read_text(encoding="utf-8"))
    assert payload["date"] == "2026-06-14"
    assert len(payload["general"]) == 1
    assert len(payload["academic"]) == 1
    assert payload["general"][0]["summary"]["one_sentence"]
    assert payload["academic"][0]["freshness"]["valid_days"] == 90


def test_report_data_filters_expired_by_profile(tmp_path):
    _store_article(
        tmp_path,
        Article(
            id="old-general",
            source="qbitai",
            title="过期技术资讯 GitHub HuggingFace API",
            full_text="参数 7B，benchmark，API，教程，代码。",
            publish_date="2026-05-14",
            url="https://example.com/old-general",
        ),
    )
    _store_article(
        tmp_path,
        Article(
            id="old-academic",
            source="arxiv",
            title="Expired LLM Benchmark Method",
            abstract="We propose a method and benchmark with accuracy 95%.",
            publish_date="2026-03-15",
            url="https://arxiv.org/abs/old-academic",
        ),
    )

    payload = ReportDataExporter(tmp_path).build_payload(pass_score=0)

    assert payload["general"] == []
    assert payload["academic"] == []
    assert payload["stats"]["filtered_expired"] == 2


def test_report_data_can_include_expired_articles(tmp_path):
    _store_article(
        tmp_path,
        Article(
            id="old-general",
            source="qbitai",
            title="过期技术资讯 GitHub HuggingFace API",
            full_text="参数 7B，benchmark，API，教程，代码。",
            publish_date="2026-05-14",
            url="https://example.com/include-old-general",
        ),
    )

    payload = ReportDataExporter(tmp_path).build_payload(pass_score=0, include_expired=True)

    assert len(payload["general"]) == 1
    assert payload["general"][0]["freshness"]["label"] == "已过时效"
    assert payload["general"][0]["freshness"]["is_valid"] is False


def test_report_data_pass_score_filters_low_score(tmp_path):
    _store_article(
        tmp_path,
        Article(
            id="low",
            source="qbitai",
            title="普通消息",
            full_text="简短新闻。",
            publish_date="2026-06-14",
            url="https://example.com/low",
        ),
    )

    payload = ReportDataExporter(tmp_path).build_payload(pass_score=99)

    assert payload["general"] == []
    assert payload["stats"]["filtered_low_score"] == 1
