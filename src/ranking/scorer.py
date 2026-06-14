"""Split ranking scorers for academic and general AI content."""

import re
from datetime import datetime, timezone

from src.core.models import Article


ACADEMIC_SOURCES = {"arxiv", "semantic_scholar", "openalex"}


SOURCE_TRUST = {
    "openai": 15,
    "deepmind": 15,
    "anthropic": 15,
    "arxiv": 15,
    "semantic_scholar": 14,
    "openalex": 14,
    "huggingface": 13,
    "hf_daily_papers": 12,
    "google_ai": 12,
    "meta_ai": 12,
    "the_gradient": 10,
    "qbitai": 8,
    "jiqizhixin": 8,
    "baai_hub": 8,
}


class BaseScorer:
    profile = "base"

    def score(self, article: Article) -> Article:
        raise NotImplementedError

    def _text(self, article: Article) -> str:
        analysis = article.analysis.to_dict() if article.analysis else {}
        return " ".join([
            article.title,
            article.abstract,
            article.full_text,
            " ".join(article.topics),
            " ".join(article.tags.get("industries", [])) if isinstance(article.tags, dict) else "",
            " ".join(article.tags.get("technologies", [])) if isinstance(article.tags, dict) else "",
            " ".join(str(v) for v in analysis.values()),
        ]).lower()

    def _keyword_score(self, text: str, keywords: list[str], max_score: float) -> float:
        hits = sum(1 for keyword in keywords if keyword.lower() in text)
        return min(max_score, hits * (max_score / max(1, min(len(keywords), 5))))

    def _freshness_score(self, publish_date: str, max_score: float) -> float:
        if not publish_date:
            return max_score * 0.5
        raw = publish_date[:10]
        try:
            dt = datetime.fromisoformat(raw).replace(tzinfo=timezone.utc)
        except ValueError:
            return max_score * 0.5
        days = max(0, (datetime.now(timezone.utc) - dt).days)
        if days <= 7:
            return max_score
        if days <= 30:
            return max_score * (1 - (days - 7) / 46)
        return max_score * 0.25

    def _analysis_score(self, article: Article, max_score: float) -> float:
        if not article.analysis:
            return 0.0
        return min(max_score, max(0.0, article.analysis.importance_score) / 10 * max_score)

    def _numbers_and_links(self, text: str) -> int:
        patterns = [
            r"\d+(\.\d+)?%",
            r"\b\d+(\.\d+)?[bmk]\b",
            r"github",
            r"huggingface",
            r"arxiv",
            r"benchmark",
            r"dataset",
        ]
        return sum(1 for pattern in patterns if re.search(pattern, text))


class AcademicScorer(BaseScorer):
    profile = "academic"

    def score(self, article: Article) -> Article:
        text = self._text(article)
        breakdown = {
            "研究相关性": self._keyword_score(text, ["llm", "agent", "多模态", "reasoning", "alignment", "benchmark", "memory", "评测", "推理"], 25),
            "技术创新密度": self._keyword_score(text, ["method", "framework", "architecture", "dataset", "ablation", "sota", "algorithm", "benchmark", "模型"], 25),
            "实验可信度": min(20, self._numbers_and_links(text) * 4),
            "应用潜力": self._keyword_score(text, ["医疗", "机器人", "企业", "科研", "开发者", "deployment", "application"], 15),
            "新鲜度": self._freshness_score(article.publish_date, 10),
            "AI分析重要性": self._analysis_score(article, 5),
        }
        self._apply(article, breakdown, "academic")
        article.rank_reason = f"学术评分基于研究相关性、技术创新密度和实验可信度；当前得分 {article.rank_score:.1f}。"
        return article

    def _apply(self, article: Article, breakdown: dict, profile: str):
        article.score_profile = profile
        article.score_breakdown = {k: round(v, 2) for k, v in breakdown.items()}
        article.rank_score = round(min(100.0, sum(breakdown.values())), 2)


class GeneralContentScorer(BaseScorer):
    profile = "general"

    def score(self, article: Article) -> Article:
        text = self._text(article)
        breakdown = {
            "信息价值": self._keyword_score(text, ["新模型", "发布", "论文", "框架", "趋势", "模型", "release", "introducing"], 25),
            "技术密度": min(20, self._numbers_and_links(text) * 3.5 + self._keyword_score(text, ["参数", "benchmark", "github", "huggingface", "api"], 8)),
            "行业影响": self._keyword_score(text, ["企业", "产业", "开发者", "生态", "应用", "客户", "公司", "business"], 20),
            "来源可信度": SOURCE_TRUST.get(article.source, 8),
            "新鲜度": self._freshness_score(article.publish_date, 10),
            "可行动性": self._keyword_score(text, ["github", "huggingface", "api", "教程", "course", "代码", "开源", "实践"], 10),
        }
        article.score_profile = "general"
        article.score_breakdown = {k: round(v, 2) for k, v in breakdown.items()}
        article.rank_score = round(min(100.0, sum(breakdown.values())), 2)
        article.rank_reason = f"资讯评分基于信息价值、技术密度、行业影响和可行动性；当前得分 {article.rank_score:.1f}。"
        return article


def get_scorer(article: Article) -> BaseScorer:
    if article.source in ACADEMIC_SOURCES:
        return AcademicScorer()
    return GeneralContentScorer()


def score_article(article: Article) -> Article:
    return get_scorer(article).score(article)


def sort_articles(articles: list[Article]) -> list[Article]:
    return sorted(
        articles,
        key=lambda item: (
            -item.rank_score,
            item.publish_date or "",
            item.source,
            item.title,
        ),
        reverse=False,
    )
