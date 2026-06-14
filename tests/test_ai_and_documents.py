from pathlib import Path

from src.ai.mock_client import MockLLMClient
from src.ai.openai_client import OpenAIClient
from src.ai.summarizer import ArticleSummarizer
from src.core.models import Article
from src.processors.article_processor import ArticleProcessor
from src.processors.document_processor import DocumentProcessor


def test_summarizer_parses_valid_json():
    client = MockLLMClient()
    summarizer = ArticleSummarizer(client, language="zh-CN")
    article = Article(id="a1", source="unit", title="Title", full_text="AI model content")

    analysis = summarizer.summarize(article)

    assert analysis.core_points == "Mock summary"
    assert analysis.importance_score == 5.0
    assert client.calls


def test_summarizer_handles_invalid_json():
    client = MockLLMClient(response="not json")
    summarizer = ArticleSummarizer(client)
    article = Article(id="a1", source="unit", title="Title", full_text="Body")

    analysis = summarizer.summarize(article)

    assert analysis.error


def test_summarizer_parses_fenced_json_and_clamps_score():
    client = MockLLMClient(response='```json\n{"core_points":"ok","importance_score":99}\n```')
    summarizer = ArticleSummarizer(client)
    article = Article(id="a1", source="unit", title="Title", full_text="Body")

    analysis = summarizer.summarize(article)

    assert analysis.core_points == "ok"
    assert analysis.importance_score == 10.0


def test_summarizer_truncates_long_content():
    client = MockLLMClient()
    summarizer = ArticleSummarizer(client, max_input_chars=20)
    article = Article(id="a1", source="unit", title="Title", full_text="x" * 100)

    summarizer.summarize(article)

    assert "x" * 21 not in client.calls[0]


def test_article_processor_only_summarizes_when_summarizer_present():
    client = MockLLMClient()
    summarizer = ArticleSummarizer(client)
    processor = ArticleProcessor(summarize=True, summarizer=summarizer)
    article = Article(id="a1", source="unit", title="Title", full_text="AI agent reasoning")

    processed = processor.process(article)

    assert processed.analysis.core_points == "Mock summary"


def test_openai_client_prefers_dashscope_env(monkeypatch):
    monkeypatch.setenv("DASHSCOPE_API_KEY", "dashscope-key")
    monkeypatch.setenv("LLM_MODEL", "qwen-plus")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

    client = OpenAIClient()

    assert client.api_key == "dashscope-key"
    assert client.model == "qwen-plus"
    assert client.base_url == "https://dashscope.aliyuncs.com/compatible-mode/v1"


def test_document_processor_html_and_text(tmp_path):
    html_path = tmp_path / "sample.html"
    html_path.write_text("<html><body><h1>Title</h1><p>Body text</p></body></html>", encoding="utf-8")
    txt_path = tmp_path / "sample.txt"
    txt_path.write_text("Plain text", encoding="utf-8")

    processor = DocumentProcessor()

    assert "Body text" in processor.process_path(html_path).clean_text
    assert processor.process_path(txt_path).clean_text == "Plain text"


def test_document_processor_docx_missing_dependency_path(tmp_path):
    path = tmp_path / "sample.docx"
    path.write_bytes(b"not a real docx")
    processor = DocumentProcessor()

    result = processor.process_path(path)

    assert result.metadata["format"] == "docx"
    assert "error" in result.metadata or result.clean_text == ""
