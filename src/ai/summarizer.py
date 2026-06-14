"""Structured article summarization."""

import json
import re

from src.ai.llm_client import LLMClient
from src.core.models import Article, ArticleAnalysis
from src.utils.config_loader import PROJECT_ROOT
from src.utils.logger import get_logger

logger = get_logger("ai.summarizer")


class ArticleSummarizer:
    """Render the summary prompt and parse structured LLM output."""

    def __init__(
        self,
        client: LLMClient,
        template_path=None,
        max_length: int = 600,
        language: str = "zh-CN",
        max_input_chars: int = 12000,
    ):
        self.client = client
        self.template_path = template_path or PROJECT_ROOT / ".qoder" / "prompts" / "summarize.st"
        self.max_length = max_length
        self.language = language
        self.max_input_chars = max_input_chars
        self.template = self._load_template()

    def _load_template(self) -> str:
        with open(self.template_path, "r", encoding="utf-8") as f:
            return f.read()

    def summarize(self, article: Article, content_type: str = "article") -> ArticleAnalysis:
        prompt = self._render_prompt(article, content_type)
        try:
            response = self.client.complete(prompt)
            data = self._parse_json(response)
            return ArticleAnalysis(
                core_points=str(data.get("core_points", "")),
                technical_details=str(data.get("technical_details", "")),
                key_results=str(data.get("key_results", "")),
                applications=str(data.get("applications", "")),
                risk_level=str(data.get("risk_level", "")),
                importance_score=self._clamp_score(data.get("importance_score", 0.0)),
            )
        except Exception as e:
            logger.error(f"summarization failed for {article.url}: {e}")
            return ArticleAnalysis(error=str(e))

    def _render_prompt(self, article: Article, content_type: str) -> str:
        raw_content = article.full_text or article.abstract or article.title
        raw_content = raw_content[: self.max_input_chars]
        values = {
            "{raw_content}": raw_content,
            "{source_name}": article.source,
            "{content_type}": content_type,
            "{max_length}": str(self.max_length),
            "{language}": self.language,
        }
        prompt = self.template
        for key, value in values.items():
            prompt = prompt.replace(key, value)
        return prompt

    def _parse_json(self, text: str) -> dict:
        fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
        if fenced:
            return json.loads(fenced.group(1))
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, flags=re.DOTALL)
            if not match:
                raise
            return json.loads(match.group(0))

    def _clamp_score(self, value) -> float:
        try:
            score = float(value or 0.0)
        except (TypeError, ValueError):
            return 0.0
        return min(10.0, max(0.0, score))
