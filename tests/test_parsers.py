from pathlib import Path

from src.core.models import CrawlResult
from src.crawlers.anthropic.parser import AnthropicParser
from src.crawlers.arxiv.crawler import ArXivCrawler
from src.crawlers.arxiv.parser import ArXivParser
from src.crawlers.deepmind.parser import DeepMindParser
from src.crawlers.huggingface.parser import HuggingFaceParser
from src.crawlers.jiqizhixin.parser import JiqiZhixinParser
from src.crawlers.openai.parser import OpenAIParser
from src.crawlers.qbitai.parser import QbitAIParser
from src.crawlers.baai_hub.parser import BAAIHubParser
from src.crawlers.google_ai.parser import GoogleAIParser
from src.crawlers.hf_daily_papers.parser import HFDailyPapersParser
from src.crawlers.meta_ai.parser import MetaAIParser
from src.crawlers.openalex.parser import OpenAlexParser
from src.crawlers.semantic_scholar.parser import SemanticScholarParser
from src.crawlers.the_gradient.parser import TheGradientParser


FIXTURES = Path(__file__).parent / "fixtures"


def read_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def parse_one(parser, source: str, fixture_name: str, url: str):
    result = CrawlResult(url=url, raw_html=read_fixture(fixture_name), metadata={"source": source})
    articles = parser.parse(result)
    assert len(articles) == 1
    article = articles[0]
    assert article.source == source
    assert article.title
    assert article.url == url
    assert article.full_text
    return article


def test_html_parsers_parse_minimal_fixtures():
    cases = [
        (HuggingFaceParser(), "huggingface", "sample_hf_blog.html", "https://huggingface.co/blog/smolvlm2"),
        (JiqiZhixinParser(), "jiqizhixin", "sample_jiqizhixin.html", "https://www.jiqizhixin.com/articles/test"),
        (OpenAIParser(), "openai", "sample_openai.html", "https://openai.com/blog/test"),
        (AnthropicParser(), "anthropic", "sample_anthropic.html", "https://www.anthropic.com/research/test"),
        (DeepMindParser(), "deepmind", "sample_deepmind.html", "https://deepmind.google/blog/test"),
        (QbitAIParser(), "qbitai", "sample_qbitai.html", "https://www.qbitai.com/2026/06/1.html"),
    ]

    for parser, source, fixture_name, url in cases:
        parse_one(parser, source, fixture_name, url)


def test_new_generic_html_parsers_parse_fixture():
    cases = [
        (TheGradientParser(), "the_gradient", "https://thegradient.pub/test"),
        (BAAIHubParser(), "baai_hub", "https://hub.baai.ac.cn/articles/test"),
        (GoogleAIParser(), "google_ai", "https://ai.googleblog.com/2026/06/test.html"),
        (MetaAIParser(), "meta_ai", "https://ai.meta.com/blog/test"),
    ]

    for parser, source, url in cases:
        parse_one(parser, source, "sample_generic_article.html", url)


def test_baai_parser_accepts_embedded_records():
    articles = BAAIHubParser().parse(CrawlResult(
        url="https://hub.baai.ac.cn/",
        raw_json={
            "data": [{
                "id": "1",
                "title": "智源文章",
                "summary": "文章摘要",
                "content": "文章正文内容，包含足够的信息用于后续分析。",
                "created_at": "2026-06-14 18:20 分享",
                "source_url": "https://hub.baai.ac.cn/view/1",
            }]
        },
    ))

    assert articles[0].source == "baai_hub"
    assert articles[0].title == "智源文章"
    assert articles[0].publish_date == "2026-06-14"
    assert articles[0].url == "https://hub.baai.ac.cn/view/1"


def test_the_gradient_parser_accepts_archive_records():
    articles = TheGradientParser().parse(CrawlResult(
        url="https://thegradientpub.substack.com/api/v1/archive",
        raw_json={
            "data": [{
                "id": 188438294,
                "title": "After Orthogonality",
                "subtitle": "A short alignment essay.",
                "post_date": "2026-02-19T16:02:41.671Z",
                "canonical_url": "https://thegradientpub.substack.com/p/test",
                "body_html": "<p>Virtue ethics offers another framing for AI alignment.</p>",
                "publishedBylines": [{"name": "The Gradient"}],
                "postTags": [{"name": "AI Alignment"}],
            }]
        },
    ))

    assert articles[0].source == "the_gradient"
    assert articles[0].title == "After Orthogonality"
    assert articles[0].publish_date == "2026-02-19"
    assert articles[0].url == "https://thegradientpub.substack.com/p/test"
    assert "AI alignment" in articles[0].full_text
    assert articles[0].authors == ["The Gradient"]


def test_new_api_parsers_parse_records():
    hf_articles = HFDailyPapersParser().parse(CrawlResult(
        url="https://huggingface.co/api/daily_papers",
        raw_json=[{"paper": {"id": "2606.1", "title": "HF Paper", "summary": "Paper summary", "authors": ["Ada"]}}],
    ))
    semantic_articles = SemanticScholarParser().parse(CrawlResult(
        url="https://api.semanticscholar.org/graph/v1/paper/search",
        raw_json={"data": [{"title": "Semantic Paper", "abstract": "Semantic abstract", "url": "https://example.com/p"}]},
    ))
    openalex_articles = OpenAlexParser().parse(CrawlResult(
        url="https://api.openalex.org/works",
        raw_json={"results": [{
            "id": "https://openalex.org/W1",
            "title": "OpenAlex Paper",
            "abstract_inverted_index": {"OpenAlex": [0], "abstract": [1]},
            "publication_date": "2026-06-14",
            "primary_location": {"landing_page_url": "https://example.com/openalex"},
            "authorships": [{"author": {"display_name": "Ada"}}],
            "topics": [{"display_name": "Artificial intelligence"}],
        }]},
    ))

    assert hf_articles[0].source == "hf_daily_papers"
    assert hf_articles[0].title == "HF Paper"
    assert semantic_articles[0].source == "semantic_scholar"
    assert semantic_articles[0].title == "Semantic Paper"
    assert openalex_articles[0].source == "openalex"
    assert openalex_articles[0].title == "OpenAlex Paper"
    assert openalex_articles[0].full_text == "OpenAlex abstract"


def test_parsers_tolerate_missing_fields():
    empty_html = "<html><body></body></html>"
    cases = [
        (HuggingFaceParser(), "https://huggingface.co/blog/missing"),
        (JiqiZhixinParser(), "https://www.jiqizhixin.com/articles/missing"),
        (OpenAIParser(), "https://openai.com/blog/missing"),
        (AnthropicParser(), "https://www.anthropic.com/research/missing"),
        (DeepMindParser(), "https://deepmind.google/blog/missing"),
        (QbitAIParser(), "https://www.qbitai.com/2026/06/missing.html"),
    ]

    for parser, url in cases:
        articles = parser.parse(CrawlResult(url=url, raw_html=empty_html))
        assert len(articles) == 1
        assert articles[0].title
        assert articles[0].url == url


def test_arxiv_parser_from_raw_json():
    class EmptyPDFExtractor:
        def extract(self, pdf_url, arxiv_id):
            return ""

    result = CrawlResult(
        url="https://arxiv.org/abs/2606.00001v1",
        raw_json={
            "arxiv_id": "2606.00001v1",
            "title": "Test Paper on AI Agents",
            "summary": "This paper studies AI agents.",
            "published": "2026-06-07T00:00:00Z",
            "authors": ["Ada Researcher"],
            "categories": ["cs.AI"],
            "pdf_url": "https://arxiv.org/pdf/2606.00001v1",
        },
    )

    article = ArXivParser(pdf_extractor=EmptyPDFExtractor()).parse(result)[0]

    assert article.id == "arx_2606.00001v1"
    assert article.source == "arxiv"
    assert article.publish_date == "2026-06-07"
    assert "cs.AI" in article.topics
    assert "pdf:https://arxiv.org/pdf/2606.00001v1" in article.topics


def test_arxiv_parser_uses_pdf_text_when_available():
    class PDFExtractor:
        def extract(self, pdf_url, arxiv_id):
            return "Extracted PDF text"

    result = CrawlResult(
        url="https://arxiv.org/abs/2606.00001v1",
        raw_json={
            "arxiv_id": "2606.00001v1",
            "title": "Test Paper",
            "summary": "Summary",
            "pdf_url": "https://arxiv.org/pdf/2606.00001v1",
        },
    )

    article = ArXivParser(pdf_extractor=PDFExtractor()).parse(result)[0]

    assert article.full_text == "Extracted PDF text"


def test_arxiv_crawler_parses_atom_xml(monkeypatch):
    class Response:
        text = read_fixture("sample_arxiv.xml")

        def raise_for_status(self):
            return None

    def fake_get(url, params=None, timeout=None):
        assert "export.arxiv.org" in url
        assert params["max_results"] == 1
        return Response()

    monkeypatch.setattr("src.crawlers.arxiv.crawler.requests.get", fake_get)

    crawler = ArXivCrawler(proxy_required=False)
    crawler.max_pages = 1
    results = crawler.crawl()

    assert len(results) == 1
    assert results[0].raw_json["arxiv_id"] == "2606.00001v1"
