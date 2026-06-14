"""Freshness windows for HTML report visibility."""

from dataclasses import dataclass
from datetime import datetime, timezone

from src.core.models import Article


GENERAL_VALID_DAYS = 30
ACADEMIC_VALID_DAYS = 90


@dataclass
class FreshnessStatus:
    is_valid: bool
    label: str
    age_days: int | None
    valid_days: int
    reason: str = ""


def profile_valid_days(profile: str, general_valid_days: int = GENERAL_VALID_DAYS, academic_valid_days: int = ACADEMIC_VALID_DAYS) -> int:
    return academic_valid_days if profile == "academic" else general_valid_days


def evaluate_freshness(
    article: Article,
    general_valid_days: int = GENERAL_VALID_DAYS,
    academic_valid_days: int = ACADEMIC_VALID_DAYS,
    now: datetime = None,
) -> FreshnessStatus:
    profile = article.score_profile or ("academic" if article.source in {"arxiv", "semantic_scholar", "openalex"} else "general")
    valid_days = profile_valid_days(profile, general_valid_days, academic_valid_days)

    if not article.publish_date:
        return FreshnessStatus(False, "无日期", None, valid_days, "缺少发表日期")

    raw = article.publish_date[:10]
    try:
        published = datetime.fromisoformat(raw).replace(tzinfo=timezone.utc)
    except ValueError:
        return FreshnessStatus(False, "无日期", None, valid_days, "发表日期无法解析")

    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    age_days = max(0, (current - published).days)
    if age_days <= valid_days:
        return FreshnessStatus(True, "时效内", age_days, valid_days)
    return FreshnessStatus(False, "已过时效", age_days, valid_days, f"超过 {valid_days} 天有效期")
