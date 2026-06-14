"""Local report summaries for article cards."""

import re
from dataclasses import dataclass

from src.core.models import Article


@dataclass
class ReportSummary:
    one_sentence: str
    why_it_matters: str
    key_points: list[str]


class ReportSummaryBuilder:
    """Build readable summaries without requiring an LLM call."""

    def build(self, article: Article) -> ReportSummary:
        analysis = article.analysis.to_dict() if article.analysis else {}
        one_sentence = analysis.get("core_points") or self._first_sentence(article.abstract or article.full_text or article.title)
        key_points = [
            item for item in [
                analysis.get("technical_details"),
                analysis.get("key_results"),
                analysis.get("applications"),
            ] if item
        ]
        if not key_points:
            key_points = self._key_points(article.abstract or article.full_text)
        return ReportSummary(
            one_sentence=one_sentence or article.title,
            why_it_matters=self._why_it_matters(article),
            key_points=key_points[:3] or [article.abstract or article.title],
        )

    def _first_sentence(self, text: str) -> str:
        sentences = self._sentences(text)
        return sentences[0][:220] if sentences else ""

    def _key_points(self, text: str) -> list[str]:
        sentences = self._sentences(text)
        scored = sorted(sentences, key=self._sentence_signal_score, reverse=True)
        return [sentence[:240] for sentence in scored[:3]]

    def _sentences(self, text: str) -> list[str]:
        if not text:
            return []
        parts = re.split(r"(?<=[。！？.!?])\s+|[\r\n]+", text.strip())
        return [part.strip() for part in parts if len(part.strip()) > 8]

    def _sentence_signal_score(self, sentence: str) -> int:
        keywords = ["模型", "LLM", "智能体", "推理", "Benchmark", "实验", "%", "GitHub", "HuggingFace", "API", "论文", "开源"]
        return sum(1 for keyword in keywords if keyword.lower() in sentence.lower()) + min(5, len(sentence) // 60)

    def _why_it_matters(self, article: Article) -> str:
        tags = article.tags if isinstance(article.tags, dict) else {}
        technologies = "、".join(tags.get("technologies", [])[:3]) or "AI"
        industries = "、".join(tags.get("industries", [])[:2]) or "通用场景"
        if article.score_profile == "academic":
            return f"这篇论文与{technologies}相关，可为{industries}中的方法、评测或后续研究提供参考。"
        return f"这篇资讯涉及{technologies}，对{industries}的产品判断、技术跟踪或落地选型有参考价值。"
