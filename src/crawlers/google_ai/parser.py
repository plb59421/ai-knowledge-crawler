"""Google AI Blog parser."""

from src.crawlers.generic import GenericHTMLParser


class GoogleAIParser(GenericHTMLParser):
    source_name = "google_ai"
    id_prefix = "gai"
