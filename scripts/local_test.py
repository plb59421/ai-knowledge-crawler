"""Local fixture pipeline test without network access."""

import argparse
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.models import CrawlResult
from src.crawlers.huggingface.parser import HuggingFaceParser
from src.storage.knowledge_store import KnowledgeStore
from src.utils.logger import get_logger

logger = get_logger("local_test")


def run_local_pipeline(kb_root: Path = None) -> dict:
    """Parse the HuggingFace fixture and store it in a temporary knowledge base."""
    fixture_path = PROJECT_ROOT / "tests" / "fixtures" / "sample_hf_blog.html"
    with open(fixture_path, "r", encoding="utf-8") as f:
        raw_html = f.read()

    crawl_result = CrawlResult(
        url="https://huggingface.co/blog/smolvlm2",
        raw_html=raw_html,
        metadata={"source": "huggingface", "fetcher": "local_test"},
    )

    articles = HuggingFaceParser().parse(crawl_result)
    store = KnowledgeStore(root=kb_root)
    stored_paths = [store.store(article) for article in articles]

    return {
        "fixture": str(fixture_path),
        "parsed": len(articles),
        "stored": len([path for path in stored_paths if path]),
        "paths": [path for path in stored_paths if path],
    }


def main():
    parser = argparse.ArgumentParser(description="AI knowledge crawler local fixture test")
    parser.add_argument("--kb-root", type=Path, default=None, help="Optional output knowledge base directory")
    args = parser.parse_args()

    logger.info("=== local pipeline test start ===")
    if args.kb_root:
        result = run_local_pipeline(args.kb_root)
    else:
        with tempfile.TemporaryDirectory(prefix="ai_knowledge_crawler_") as tmpdir:
            result = run_local_pipeline(Path(tmpdir))

    logger.info(f"fixture: {result['fixture']}")
    logger.info(f"parsed={result['parsed']}, stored={result['stored']}")
    for path in result["paths"]:
        logger.info(f"stored successfully -> {path}")
    logger.info("=== local pipeline test complete ===")


if __name__ == "__main__":
    main()
