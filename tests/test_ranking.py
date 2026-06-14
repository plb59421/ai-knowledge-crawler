import json
from datetime import datetime, timezone

from src.core.models import Article, ArticleAnalysis
from src.ranking.freshness import evaluate_freshness
from src.ranking.html_report import HTMLReportGenerator
from src.ranking.pipeline import enrich_article, enrich_articles, split_profiles
from src.ranking.scorer import AcademicScorer, GeneralContentScorer
from src.ranking.tagger import ChineseTagger
from src.storage.knowledge_store import KnowledgeStore


def test_chinese_tagger_extracts_structured_tags():
    article = Article(
        id="a1",
        source="qbitai",
        title="医疗机器人智能体大模型推理系统",
        full_text="这是一篇关于多模态、RAG、Benchmark 和开源模型的深度解读。",
    )

    tags = ChineseTagger().tag(article)

    assert "医疗" in tags["industries"]
    assert "机器人" in tags["industries"]
    assert "LLM" in tags["technologies"]
    assert "智能体" in tags["technologies"]
    assert "推理" in tags["technologies"]
    assert "行业新闻" in tags["content_types"]


def test_arxiv_defaults_to_academic_type():
    article = Article(id="p1", source="arxiv", title="LLM Agent Benchmark", full_text="benchmark method")

    tags = ChineseTagger().tag(article)

    assert "学术论文" in tags["content_types"]


def test_academic_scorer_profile_and_density():
    rich = enrich_article(Article(
        id="p1",
        source="arxiv",
        title="LLM Agent Benchmark with New Method",
        abstract="We propose a method, dataset, architecture and benchmark. Accuracy improves by 12.5%.",
        publish_date="2026-06-14",
        analysis=ArticleAnalysis(importance_score=8),
    ))
    weak = enrich_article(Article(id="p2", source="arxiv", title="Short note", abstract="A short note."))

    AcademicScorer().score(rich)
    AcademicScorer().score(weak)

    assert rich.score_profile == "academic"
    assert rich.rank_score > weak.rank_score


def test_general_scorer_profile_and_actionability():
    rich = enrich_article(Article(
        id="n1",
        source="qbitai",
        title="新模型发布，GitHub 和 HuggingFace 权重开放",
        full_text="参数 1B，benchmark 提升 20%，提供 API 教程和代码。",
        publish_date="2026-06-14",
    ))
    weak = enrich_article(Article(id="n2", source="qbitai", title="普通消息", full_text="简短新闻。"))

    GeneralContentScorer().score(rich)
    GeneralContentScorer().score(weak)

    assert rich.score_profile == "general"
    assert rich.rank_score > weak.rank_score


def test_split_profiles_keeps_academic_and_general_separate():
    academic = enrich_article(Article(id="p", source="arxiv", title="LLM Benchmark", full_text="benchmark 90%", publish_date="2026-06-14"))
    general = enrich_article(Article(id="g", source="qbitai", title="大模型发布", full_text="github huggingface", publish_date="2026-06-14"))
    articles = enrich_articles([general, academic])

    academic_board, general_board = split_profiles(articles)

    assert academic_board == [academic]
    assert general_board == [general]


def test_html_report_contains_two_boards_and_escaped_content(tmp_path):
    article = enrich_article(Article(
        id="x",
        source="qbitai",
        title="<script>alert(1)</script> 大模型发布",
        abstract="摘要",
        url="https://example.com/a?x=<bad>",
        publish_date="2026-06-14",
    ))
    output = tmp_path / "report.html"

    HTMLReportGenerator().write([article], output, pass_score=0)
    html = output.read_text(encoding="utf-8")

    assert "<h2>学术论文</h2>" in html
    assert "<h2>技术资讯</h2>" in html
    assert "技术资讯" in html
    assert "学术论文" in html
    assert "全部" not in html
    assert "行业标签" not in html
    assert "技术标签" not in html
    assert "文章类型" not in html
    assert "general-board" in html
    assert "academic-board" in html
    assert "&lt;script&gt;" in html
    assert "行业" in html
    assert "技术" in html
    assert "类型" in html
    assert "一句话总结" in html
    assert "为什么值得关注" in html
    assert "关键要点" in html
    assert "时效内" in html
    assert "有效期" in html


def test_generate_report_from_knowledge_base(tmp_path):
    store = KnowledgeStore(root=tmp_path)
    store.store(enrich_article(Article(
        id="r1",
        source="arxiv",
        title="LLM Agent Benchmark",
        abstract="method benchmark 95%",
        url="https://arxiv.org/abs/test",
        publish_date="2026-06-14",
    )))

    from scripts.generate_report import load_articles

    articles = enrich_articles(load_articles(tmp_path))
    output = tmp_path / "exports" / "html" / "report.html"
    HTMLReportGenerator().write(articles, output)

    assert output.exists()
    assert "<h2>学术论文</h2>" in output.read_text(encoding="utf-8")


def test_freshness_windows_by_profile():
    now = datetime(2026, 6, 14, tzinfo=timezone.utc)
    general_valid = enrich_article(Article(id="g1", source="qbitai", title="资讯", publish_date="2026-05-16", full_text="github 模型"))
    general_expired = enrich_article(Article(id="g2", source="qbitai", title="资讯", publish_date="2026-05-14", full_text="github 模型"))
    academic_valid = enrich_article(Article(id="a1", source="arxiv", title="论文", publish_date="2026-03-17", full_text="benchmark method"))
    academic_expired = enrich_article(Article(id="a2", source="arxiv", title="论文", publish_date="2026-03-15", full_text="benchmark method"))

    assert evaluate_freshness(general_valid, now=now).is_valid
    assert not evaluate_freshness(general_expired, now=now).is_valid
    assert evaluate_freshness(academic_valid, now=now).is_valid
    assert not evaluate_freshness(academic_expired, now=now).is_valid
    assert not evaluate_freshness(enrich_article(Article(id="x", source="qbitai", title="无日期")), now=now).is_valid


def test_html_report_filters_low_score_and_expired():
    fresh_good = enrich_article(Article(
        id="good",
        source="qbitai",
        title="新模型发布 GitHub HuggingFace",
        full_text="参数 1B，benchmark 提升 20%，提供 API 教程和代码。",
        publish_date="2026-06-14",
    ))
    expired_good = enrich_article(Article(
        id="old",
        source="qbitai",
        title="旧模型发布 GitHub HuggingFace",
        full_text="参数 1B，benchmark 提升 20%，提供 API 教程和代码。",
        publish_date="2025-01-01",
    ))
    low_score = enrich_article(Article(id="low", source="qbitai", title="普通消息", full_text="简短新闻。", publish_date="2026-06-14"))

    html = HTMLReportGenerator().render([fresh_good, expired_good, low_score], pass_score=60)
    assert "新模型发布" in html
    assert "旧模型发布" not in html
    assert "普通消息" not in html
    assert "过期过滤：1" in html
    assert "低分过滤：1" in html

    html_with_expired = HTMLReportGenerator().render([expired_good], pass_score=0, include_expired=True)
    assert "旧模型发布" in html_with_expired
    assert "已过时效" in html_with_expired


def test_html_report_prefers_ai_analysis_summary():
    article = enrich_article(Article(
        id="analysis",
        source="arxiv",
        title="LLM Agent Benchmark",
        abstract="Fallback summary.",
        full_text="benchmark method 95%",
        publish_date="2026-06-14",
        analysis=ArticleAnalysis(core_points="这是 AI 分析核心观点", technical_details="方法细节", key_results="关键结果"),
    ))

    html = HTMLReportGenerator().render([article], pass_score=0)

    assert "这是 AI 分析核心观点" in html
    assert "方法细节" in html
    assert "关键结果" in html
