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
        }