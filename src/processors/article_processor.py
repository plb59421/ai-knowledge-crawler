"""Optional article post-processing hooks."""

from src.ai.summarizer import ArticleSummarizer
from src.core.models import Article
from src.processors.html_processor import HTMLProcessor
from src.ranking.pipeline import enrich_article
from src.utils.config_loader import PROJECT_ROOT


class ArticleProcessor:
    """Apply optional local processing without requiring an LLM."""

    def __init__(
        self,
        clean_html: bool = False,
        extract_topics: bool = False,
        score_relevance: bool = False,
        summarize: bool = False,
        summarizer: ArticleSummarizer = None,
        auto_tag: bool = False,
        rank: bool = False,
    ):
        self.clean_html = clean_html
        self.extract_topics = extract_topics
        self.score_relevance = score_relevance
        self.summarize = summarize
        self.summarizer = summarizer
        self.auto_tag = auto_tag
        self.rank = rank
        self.html_processor = HTMLProcessor()
        self.summary_template = self._load_summary_template() if summarize else ""

    def _load_summary_template(self) -> str:
        template_path = PROJECT_ROOT / ".ai" / "prompts" / "summarize.st"
        if not template_path.exists():
            return ""
        return template_path.read_text(encoding="utf-8")

    def process(self, article: Article, allow_summarize: bool = True) -> Article:
        """Return an enriched article. Defaults preserve parser output."""
        if self.clean_html:
            article.full_text = self.html_processor.process(article.full_text)
            article.abstract = self.html_processor.process(article.abstract)

        if self.extract_topics and not article.topics:
            article.topics = self._extract_topics(article)

        if self.score_relevance and not article.relevance_score:
            article.relevance_score = self._score_relevance(article)

        if allow_summarize and self.summarize and self.summarizer:
            article.analysis = self.summarizer.summarize(article)

        if self.auto_tag or self.rank:
            article = enrich_article(article, auto_tag=self.auto_tag, rank=self.rank)

        return article

    def _extract_topics(self, article: Article) -> list[str]:
        text = f"{article.title} {article.abstract} {article.full_text}".lower()
        keyword_map = {
            "llm": ["llm", "large language model", "大模型"],
            "multimodal": ["multimodal", "vision-language", "多模态"],
            "agent": ["agent", "agents", "智能体"],
            "alignment": ["alignment", "safety", "对齐", "安全"],
            "reasoning": ["reasoning", "推理"],
        }
        topics = []
        for topic, keywords in keyword_map.items():
            if any(keyword in text for keyword in keywords):
                topics.append(topic)
        return topics

    def _score_relevance(self, article: Article) -> float:
        score = 0.0
        text = f"{article.title} {article.abstract} {article.full_text}".lower()
        for keyword in ["ai", "model", "llm", "agent", "reasoning", "人工智能", "模型"]:
            if keyword in text:
                score += 1.0
        return min(score, 10.0)
