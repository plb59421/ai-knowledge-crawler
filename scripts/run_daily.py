"""Daily grouped crawler runner."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.run_crawler import crawl_source
from src.ai.openai_client import OpenAIClient
from src.ai.summarizer import ArticleSummarizer
from src.processors.article_processor import ArticleProcessor
from src.ranking.report_data import ReportDataExporter
from src.storage.knowledge_store import KnowledgeStore
from src.utils.config_loader import get_runtime_config
from src.utils.logger import get_logger

logger = get_logger("run_daily")

DOMESTIC_SOURCES = ["qbitai", "jiqizhixin", "arxiv", "openalex", "baai_hub", "the_gradient"]
PROXY_SOURCES = [
    "huggingface",
    "hf_daily_papers",
    "openai",
    "anthropic",
    "deepmind",
    "google_ai",
    "meta_ai",
]


def run_group(
    sources: list[str],
    no_proxy: bool,
    max_pages: int = None,
    summarize: bool = False,
    dry_run: bool = False,
    auto_tag: bool = True,
    rank: bool = True,
    analysis_limit: int = 10,
    force_analyze: bool = False,
) -> list[dict]:
    if dry_run:
        return [
            {
                "source": source,
                "crawled": 0,
                "parsed": 0,
                "stored": 0,
                "updated": 0,
                "analyzed": 0,
                "analysis_failed": 0,
                "analysis_skipped": 0,
                "error": "",
                "dry_run": True,
            }
            for source in sources
        ]

    summarizer = ArticleSummarizer(OpenAIClient()) if summarize else None
    processor = ArticleProcessor(
        extract_topics=True,
        score_relevance=True,
        summarize=summarize,
        summarizer=summarizer,
        auto_tag=auto_tag,
        rank=rank,
    )

    stats = []
    for source in sources:
        try:
            stats.append(crawl_source(
                source,
                no_proxy=no_proxy,
                max_pages=max_pages,
                processor=processor,
                analysis_limit=analysis_limit,
                force_analyze=force_analyze,
            ))
        except Exception as e:
            logger.error(f"[{source}] daily crawl failed: {e}")
            stats.append({"source": source, "crawled": 0, "parsed": 0, "stored": 0, "error": str(e)})
    return stats


def main():
    runtime_config = get_runtime_config()
    default_analysis_limit = int(runtime_config.get("default_analysis_limit", 10))
    parser = argparse.ArgumentParser(description="Run daily AI knowledge crawler source groups")
    parser.add_argument("--group", choices=["domestic", "proxy", "all"], default="domestic")
    parser.add_argument("--max-pages", type=int, default=None)
    parser.add_argument("--summarize", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-auto-tag", action="store_true")
    parser.add_argument("--no-rank", action="store_true")
    parser.add_argument("--html-report", dest="no_html_report", action="store_false")
    parser.add_argument("--no-html-report", dest="no_html_report", action="store_true")
    parser.add_argument("--report-limit", type=int, default=200)
    parser.add_argument("--pass-score", type=float, default=None)
    parser.add_argument("--general-valid-days", type=int, default=30)
    parser.add_argument("--academic-valid-days", type=int, default=90)
    parser.add_argument("--include-expired", action="store_true")
    parser.add_argument("--analysis-limit", type=int, default=default_analysis_limit)
    parser.add_argument("--force-analyze", action="store_true")
    parser.set_defaults(no_html_report=False)
    args = parser.parse_args()

    auto_tag = not args.no_auto_tag
    rank = not args.no_rank
    if args.group == "domestic":
        stats = run_group(DOMESTIC_SOURCES, no_proxy=True, max_pages=args.max_pages, summarize=args.summarize, dry_run=args.dry_run, auto_tag=auto_tag, rank=rank, analysis_limit=args.analysis_limit, force_analyze=args.force_analyze)
    elif args.group == "proxy":
        stats = run_group(PROXY_SOURCES, no_proxy=False, max_pages=args.max_pages, summarize=args.summarize, dry_run=args.dry_run, auto_tag=auto_tag, rank=rank, analysis_limit=args.analysis_limit, force_analyze=args.force_analyze)
    else:
        stats = []
        stats.extend(run_group(DOMESTIC_SOURCES, no_proxy=True, max_pages=args.max_pages, summarize=args.summarize, dry_run=args.dry_run, auto_tag=auto_tag, rank=rank, analysis_limit=args.analysis_limit, force_analyze=args.force_analyze))
        stats.extend(run_group(PROXY_SOURCES, no_proxy=False, max_pages=args.max_pages, summarize=args.summarize, dry_run=args.dry_run, auto_tag=auto_tag, rank=rank, analysis_limit=args.analysis_limit, force_analyze=args.force_analyze))

    store = KnowledgeStore()
    store.record_crawl_history(stats)
    report_path = store.write_daily_report(stats)
    data_path = ""
    if not args.no_html_report:
        today = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        export_result = ReportDataExporter(store.root).export(
            date=today,
            limit=args.report_limit,
            profile="all",
            pass_score=args.pass_score,
            include_expired=args.include_expired,
            general_valid_days=args.general_valid_days,
            academic_valid_days=args.academic_valid_days,
        )
        data_path = export_result["latest_path"]

    print("=== daily crawl summary ===")
    for item in stats:
        status = "dry-run" if item.get("dry_run") else ("OK" if not item.get("error") else f"ERROR: {item['error']}")
        print(f"{item['source']}: crawled={item['crawled']}, parsed={item['parsed']}, stored={item['stored']} [{status}]")
    print(f"report: {report_path}")
    if data_path:
        print(f"frontend data: {data_path}")


if __name__ == "__main__":
    main()
