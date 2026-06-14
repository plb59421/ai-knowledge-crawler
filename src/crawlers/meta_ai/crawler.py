"""Meta AI Blog crawler."""

from src.crawlers.generic import GenericHTMLCrawler


class MetaAICrawler(GenericHTMLCrawler):
    source_name = "meta_ai"
    fetcher_type = "Fetcher"
    proxy_required = True
    max_pages = 3
    base_url = "https://ai.meta.com/blog/"
