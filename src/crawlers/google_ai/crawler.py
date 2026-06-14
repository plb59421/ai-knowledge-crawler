"""Google AI Blog crawler."""

from src.crawlers.generic import GenericHTMLCrawler


class GoogleAICrawler(GenericHTMLCrawler):
    source_name = "google_ai"
    fetcher_type = "Fetcher"
    proxy_required = True
    max_pages = 3
    base_url = "https://research.google/blog/"
    article_path_markers = ("/blog/",)
    excluded_path_markers = (
        "/blog/label/",
        "/blog/rss",
        "/category/",
        "/tag/",
    )
