"""Frontend report data export."""

import json
from datetime import datetime, timedelta
from pathlib import Path

from src.core.models import Article
from src.ranking.freshness import ACADEMIC_VALID_DAYS, GENERAL_VALID_DAYS, evaluate_freshness
from src.ranking.pipeline import article_from_dict, enrich_articles, split_profiles
from src.ranking.summary import ReportSummaryBuilder
from src.storage.knowledge_store import KB_ROOT, KnowledgeStore


class ReportDataExporter:
    """Export ranked report data as JSON for a decoupled frontend."""

    def __init__(self, kb_root: str | Path = KB_ROOT):
        self.kb_root = Path(kb_root)
        self.store = KnowledgeStore(root=self.kb_root)

    def load_articles(self, date: str = None, days: int = None, sources: list[str] = None) -> list[Article]:
        by_source = self.kb_root / "by_source"
        articles = []
        allowed_dates = None
        if date:
            allowed_dates = {date}
        elif days:
            today = datetime.now()
            allowed_dates = {
                (today - timedelta(days=offset)).strftime("%Y-%m-%d")
                for offset in range(days)
            }

        for path in by_source.rglob("*.json"):
            if allowed_dates and path.stem not in allowed_dates:
                continue
            source = path.parts[-4] if len(path.parts) >= 4 else ""
            if sources and source not in sources:
                continue
            data = self.store._load_json(path, [])
            if isinstance(data, list):
                articles.extend(article_from_dict(item) for item in data)
        return articles

    def build_payload(
        self,
        date: str = None,
        days: int = None,
        sources: list[str] = None,
        limit: int = 200,
        profile: str = "all",
        pass_score: float | None = None,
        include_expired: bool = False,
        general_valid_days: int = GENERAL_VALID_DAYS,
        academic_valid_days: int = ACADEMIC_VALID_DAYS,
        tag: str = None,
    ) -> dict:
        report_date = date or datetime.now().strftime("%Y-%m-%d")
        articles = enrich_articles(self.load_articles(date=date, days=days, sources=sources), auto_tag=True, rank=True)
        academic, general = split_profiles(articles)
        if profile == "academic":
            general = []
        elif profile == "general":
            academic = []

        filtered_expired = 0
        filtered_low_score = 0

        def keep(items: list[Article], profile_name: str) -> list[dict]:
            nonlocal filtered_expired, filtered_low_score
            threshold = pass_score if pass_score is not None else (50.0 if profile_name == "academic" else 60.0)
            rows = []
            for article in items:
                if tag and not self._has_tag(article, tag):
                    continue
                freshness = evaluate_freshness(article, general_valid_days, academic_valid_days)
                if not freshness.is_valid and not include_expired:
                    filtered_expired += 1
                    continue
                if article.rank_score < threshold:
                    filtered_low_score += 1
                    continue
                rows.append(self._article_payload(article, freshness))
            return rows[:limit]

        academic_rows = keep(academic, "academic")
        general_rows = keep(general, "general")
        selected_count = len(academic_rows) + len(general_rows)

        return {
            "generated_at": datetime.now().isoformat(),
            "date": report_date,
            "stats": {
                "total_loaded": len(articles),
                "selected": selected_count,
                "academic": len(academic_rows),
                "general": len(general_rows),
                "filtered_expired": filtered_expired,
                "filtered_low_score": filtered_low_score,
            },
            "filters": {
                "profile": profile,
                "limit": limit,
                "pass_score": pass_score,
                "include_expired": include_expired,
                "general_valid_days": general_valid_days,
                "academic_valid_days": academic_valid_days,
                "sources": sources or [],
                "tag": tag or "",
            },
            "academic": academic_rows,
            "general": general_rows,
        }

    def export(
        self,
        date: str = None,
        days: int = None,
        sources: list[str] = None,
        limit: int = 200,
        profile: str = "all",
        pass_score: float | None = None,
        include_expired: bool = False,
        general_valid_days: int = GENERAL_VALID_DAYS,
        academic_valid_days: int = ACADEMIC_VALID_DAYS,
        tag: str = None,
    ) -> dict:
        payload = self.build_payload(
            date=date,
            days=days,
            sources=sources,
            limit=limit,
            profile=profile,
            pass_score=pass_score,
            include_expired=include_expired,
            general_valid_days=general_valid_days,
            academic_valid_days=academic_valid_days,
            tag=tag,
        )
        data_dir = self.kb_root / "exports" / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        report_date = payload["date"]
        dated_path = data_dir / f"report_{report_date}.json"
        latest_path = data_dir / "report_latest.json"
        for path in [dated_path, latest_path]:
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {
            "payload": payload,
            "dated_path": str(dated_path),
            "latest_path": str(latest_path),
        }

    def _article_payload(self, article: Article, freshness) -> dict:
        summary = ReportSummaryBuilder().build(article)
        return {
            "id": article.id,
            "source": article.source,
            "title": article.title,
            "url": article.url,
            "publish_date": article.publish_date,
            "abstract": article.abstract,
            "summary": {
                "one_sentence": summary.one_sentence,
                "why_it_matters": summary.why_it_matters,
                "key_points": summary.key_points,
            },
            "tags": article.tags,
            "rank_score": article.rank_score,
            "score_profile": article.score_profile,
            "score_breakdown": article.score_breakdown,
            "rank_reason": article.rank_reason,
            "freshness": {
                "label": freshness.label,
                "age_days": freshness.age_days,
                "valid_days": freshness.valid_days,
                "is_valid": freshness.is_valid,
            },
        }

    def _has_tag(self, article: Article, tag: str) -> bool:
        normalized = tag.strip().lower()
        for values in (article.tags or {}).values():
            if any(str(value).strip().lower() == normalized for value in values):
                return True
        return False
