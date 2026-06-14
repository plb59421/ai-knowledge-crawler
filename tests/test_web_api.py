from datetime import datetime

from fastapi.testclient import TestClient

from src.core.models import Article
from src.ranking.pipeline import enrich_article
from src.storage.knowledge_store import KnowledgeStore
from src.web_api import app as app_module


def _store_article(root, article: Article):
    KnowledgeStore(root=root).store(enrich_article(article), stored_at=datetime.fromisoformat(article.publish_date))


def test_report_api_reads_knowledge_base_and_filters_tag(tmp_path, monkeypatch):
    _store_article(
        tmp_path,
        Article(
            id="g1",
            source="qbitai",
            title="LLM Agent Product GitHub API",
            full_text="LLM agent product with GitHub API benchmark for developers.",
            publish_date="2026-06-14",
            url="https://example.com/g1",
            tags={"industries": ["企业服务"], "technologies": ["LLM"], "content_types": ["产品发布"]},
        ),
    )
    _store_article(
        tmp_path,
        Article(
            id="a1",
            source="arxiv",
            title="LLM Agent Benchmark Method",
            abstract="We propose a benchmark method with accuracy 95%.",
            publish_date="2026-06-14",
            url="https://arxiv.org/abs/a1",
            tags={"industries": ["科研"], "technologies": ["LLM"], "content_types": ["学术论文"]},
        ),
    )
    monkeypatch.setattr(app_module, "KB_ROOT", tmp_path)

    client = TestClient(app_module.app)
    response = client.get("/api/report", params={"pass_score": 0, "tag": "LLM"})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["general"]) == 1
    assert len(payload["academic"]) == 1
    assert payload["filters"]["tag"] == "LLM"


def test_report_api_profile_academic_only(tmp_path, monkeypatch):
    _store_article(
        tmp_path,
        Article(
            id="a1",
            source="arxiv",
            title="LLM Agent Benchmark Method",
            abstract="We propose a benchmark method with accuracy 95%.",
            publish_date="2026-06-14",
            url="https://arxiv.org/abs/a1-only",
        ),
    )
    monkeypatch.setattr(app_module, "KB_ROOT", tmp_path)

    client = TestClient(app_module.app)
    payload = client.get("/api/report", params={"profile": "academic", "pass_score": 0}).json()

    assert payload["general"] == []
    assert len(payload["academic"]) == 1
