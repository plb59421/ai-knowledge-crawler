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


def register_all():
    """注册所有信息源爬虫"""
    CrawlerRegistry.register("huggingface", HuggingFaceCrawler, HuggingFaceParser)
    CrawlerRegistry.register("jiqizhixin", JiqiZhixinCrawler, JiqiZhixinParser)
    CrawlerRegistry.register("anthropic", AnthropicCrawler, AnthropicParser)
    CrawlerRegistry.register("openai", OpenAICrawler, OpenAIParser)
    CrawlerRegistry.register("deepmind", DeepMindCrawler, DeepMindParser)
    CrawlerRegistry.register("arxiv", ArXivCrawler, ArXivParser)
    CrawlerRegistry.register("qbitai", QbitAICrawler, QbitAIParser)


# 模块导入时自动注册
register_all()