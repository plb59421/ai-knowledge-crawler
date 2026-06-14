"""Semantic Scholar parser."""

from src.crawlers.generic import GenericJSONAPIParser


class SemanticScholarParser(GenericJSONAPIParser):
    source_name = "semantic_scholar"
    id_prefix = "s2"
