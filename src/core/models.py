"""AI前沿知识爬虫 - 数据模型定义"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CrawlResult:
    """爬虫原始结果"""
    url: str
    raw_html: str = ""
    raw_json: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    crawl_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ArticleAnalysis:
    """AI 分析结果"""
    core_points: str = ""
    technical_details: str = ""
    key_results: str = ""
    applications: str = ""
    risk_level: str = ""
    importance_score: float = 0.0
    error: str = ""

    def to_dict(self) -> dict:
        return {
            "core_points": self.core_points,
            "technical_details": self.technical_details,
            "key_results": self.key_results,
            "applications": self.applications,
            "risk_level": self.risk_level,
            "importance_score": self.importance_score,
            "error": self.error,
        }


@dataclass
class Article:
    """解析后的文章数据"""
    id: str
    source: str
    title: str
    abstract: str = ""
    full_text: str = ""
    authors: list = field(default_factory=list)
    publish_date: str = ""
    url: str = ""
    topics: list = field(default_factory=list)
    relevance_score: float = 0.0
    analysis: ArticleAnalysis | None = None
    tags: dict = field(default_factory=lambda: {
        "industries": [],
        "technologies": [],
        "content_types": [],
    })
    rank_score: float = 0.0
    score_profile: str = ""
    score_breakdown: dict = field(default_factory=dict)
    rank_reason: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source": self.source,
            "title": self.title,
            "abstract": self.abstract,
            "full_text": self.full_text,
            "authors": self.authors,
            "publish_date": self.publish_date,
            "url": self.url,
            "topics": self.topics,
            "relevance_score": self.relevance_score,
            "analysis": self.analysis.to_dict() if self.analysis else {},
            "tags": self.tags,
            "rank_score": self.rank_score,
            "score_profile": self.score_profile,
            "score_breakdown": self.score_breakdown,
            "rank_reason": self.rank_reason,
        }
