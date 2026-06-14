"""Export frontend report data from the local knowledge base."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.ranking.report_data import ReportDataExporter
from src.storage.knowledge_store import KB_ROOT


def load_articles(kb_root: Path = KB_ROOT, date: str = None, days: int = None, sources: list[str] = None):
    """Backward-compatible helper for callers that only need loaded articles."""
    return ReportDataExporter(kb_root).load_articles(date=date, days=days, sources=sources)


def main():
    parser = argparse.ArgumentParser(description="Export ranked AI knowledge report data")
    parser.add_argument("--date", default=None, help="Report date, e.g. 2026-06-14")
    parser.add_argument("--days", type=int, default=None, help="Include recent N days")
    parser.add_argument("--source", default=None, help="Comma-separated source filter")
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--profile", choices=["all", "academic", "general"], default="all")
    parser.add_argument("--kb-root", type=Path, default=KB_ROOT)
    parser.add_argument("--pass-score", type=float, default=None, help="Override pass score threshold for both profiles")
    parser.add_argument("--general-valid-days", type=int, default=30)
    parser.add_argument("--academic-valid-days", type=int, default=90)
    parser.add_argument("--include-expired", action="store_true")
    args = parser.parse_args()

    sources = [item.strip() for item in args.source.split(",")] if args.source else None
    result = ReportDataExporter(args.kb_root).export(
        date=args.date,
        days=args.days,
        sources=sources,
        limit=args.limit,
        profile=args.profile,
        pass_score=args.pass_score,
        include_expired=args.include_expired,
        general_valid_days=args.general_valid_days,
        academic_valid_days=args.academic_valid_days,
    )
    payload = result["payload"]
    print(f"generated: {result['dated_path']}")
    print(f"latest: {result['latest_path']}")
    print(f"articles: {payload['stats']['selected']} selected / {payload['stats']['total_loaded']} loaded")


if __name__ == "__main__":
    main()
