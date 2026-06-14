"""爬虫自动注册配置 - 将所有信息源爬虫注册到 CrawlerRegistry"""

from src.core.registry import CrawlerRegistry
from src.crawlers.huggingface.crawler import HuggingFaceCrawler
from src.crawlers.huggingface.parser import HuggingFaceParser
from src.crawlers.jiqizhixin.crawler import JiqiZhixinCrawler
from src.crawlers.jiqizhixin.parser import JiqiZhixinParser
from src.crawlers.anthropic.crawler import AnthropicCrawler
from src.crawlers.anthropic.parser import AnthropicParser
from src.crawlers.openai.crawler import OpenAICrawler
from src.crawlers.openai.parser import OpenAIParser
from src.crawlers.deepmind.crawler import DeepMindCrawler
from src.crawlers.deepmind.parser import DeepMindParser
from src.crawlers.arxiv.crawler import ArXivCrawler
from src.crawlers.arxiv.parser import ArXivParser
from src.crawlers.qbitai.crawler import QbitAICrawler
from src.crawlers.qbitai.parser import QbitAIParser
from src.crawlers.hf_daily_papers.crawler import HFDailyPapersCrawler
from src.crawlers.hf_daily_papers.parser import HFDailyPapersParser
from src.crawlers.semantic_scholar.crawler import SemanticScholarCrawler
from src.crawlers.semantic_scholar.parser import SemanticScholarParser
from src.crawlers.openalex.crawler import OpenAlexCrawler
from src.crawlers.openalex.parser import OpenAlexParser
from src.crawlers.the_gradient.crawler import TheGradientCrawler
from src.crawlers.the_gradient.parser import TheGradientParser
from src.crawlers.baai_hub.crawler import BAAIHubCrawler
from src.crawlers.baai_hub.parser import BAAIHubParser
from src.crawlers.google_ai.crawler import GoogleAICrawler
from src.crawlers.google_ai.parser import GoogleAIParser
from src.crawlers.meta_ai.crawler import MetaAICrawler
from src.crawlers.meta_ai.parser import MetaAIParser


def register_all():
    """注册所有信息源爬虫"""
    CrawlerRegistry.register("huggingface", HuggingFaceCrawler, HuggingFaceParser)
    CrawlerRegistry.register("jiqizhixin", JiqiZhixinCrawler, JiqiZhixinParser)
    CrawlerRegistry.register("anthropic", AnthropicCrawler, AnthropicParser)
    CrawlerRegistry.register("openai", OpenAICrawler, OpenAIParser)
    CrawlerRegistry.register("deepmind", DeepMindCrawler, DeepMindParser)
    CrawlerRegistry.register("arxiv", ArXivCrawler, ArXivParser)
    CrawlerRegistry.register("qbitai", QbitAICrawler, QbitAIParser)
    CrawlerRegistry.register("hf_daily_papers", HFDailyPapersCrawler, HFDailyPapersParser)
    CrawlerRegistry.register("semantic_scholar", SemanticScholarCrawler, SemanticScholarParser)
    CrawlerRegistry.register("openalex", OpenAlexCrawler, OpenAlexParser)
    CrawlerRegistry.register("the_gradient", TheGradientCrawler, TheGradientParser)
    CrawlerRegistry.register("baai_hub", BAAIHubCrawler, BAAIHubParser)
    CrawlerRegistry.register("google_ai", GoogleAICrawler, GoogleAIParser)
    CrawlerRegistry.register("meta_ai", MetaAICrawler, MetaAIParser)


# 模块导入时自动注册
register_all()
