"""Ranking pipeline helpers."""

from datetime import datetime

from src.core.models import Article, ArticleAnalysis
from src.ranking.scorer import ACADEMIC_SOURCES, score_article
from src.ranking.tagger import ChineseTagger


def article_from_dict(data: dict) -> Article:
    analysis_data = data.get("analysis") or {}
    analysis = ArticleAnalysis(**analysis_data) if analysis_data else None
    return Article(
        id=data.get("id", ""),
        source=data.get("source", ""),
        title=data.get("title", ""),
        abstract=data.get("abstract", ""),
        full_text=data.get("full_text", ""),
        authors=data.get("authors", []),
        publish_date=data.get("publish_date", ""),
        url=data.get("url", ""),
        topics=data.get("topics", []),
        relevance_score=data.get("relevance_score", 0.0),
        analysis=analysis,
        tags=data.get("tags") or {"industries": [], "technologies": [], "content_types": []},
        rank_score=data.get("rank_score", 0.0),
        score_profile=data.get("score_profile", ""),
        score_breakdown=data.get("score_breakdown", {}),
        rank_reason=data.get("rank_reason", ""),
    )


def enrich_article(article: Article, auto_tag: bool = True, rank: bool = True) -> Article:
    if auto_tag:
        article.tags = ChineseTagger().tag(article)
    if rank:
        score_article(article)
    return article


def enrich_articles(articles: list[Article], auto_tag: bool = True, rank: bool = True) -> list[Article]:
    return [enrich_article(article, auto_tag=auto_tag, rank=rank) for article in articles]


def split_profiles(articles: list[Article]) -> tuple[list[Article], list[Article]]:
    academic = []
    general = []
    for article in articles:
        if not article.score_profile:
            score_article(article)
        if article.score_profile == "academic" or article.source in ACADEMIC_SOURCES:
            academic.append(article)
        else:
            general.append(article)
    return sort_ranked(academic), sort_ranked(general)


def sort_ranked(articles: list[Article]) -> list[Article]:
    def date_key(article: Article) -> int:
        raw = article.publish_date[:10] if article.publish_date else ""
        try:
            return datetime.fromisoformat(raw).toordinal()
        except ValueError:
            return 0

    return sorted(
        articles,
        key=lambda article: (-article.rank_score, -date_key(article), article.source, article.title),
        reverse=False,
    )
