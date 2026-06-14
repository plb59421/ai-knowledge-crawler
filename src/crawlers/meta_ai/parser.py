"""Meta AI Blog parser."""

from src.crawlers.generic import GenericHTMLParser


class MetaAIParser(GenericHTMLParser):
    source_name = "meta_ai"
    id_prefix = "meta"
