"""Static HTML report generation."""

from dataclasses import dataclass
from datetime import datetime
from html import escape
from pathlib import Path

from src.core.models import Article
from src.ranking.freshness import ACADEMIC_VALID_DAYS, GENERAL_VALID_DAYS, FreshnessStatus, evaluate_freshness
from src.ranking.pipeline import split_profiles
from src.ranking.summary import ReportSummaryBuilder


@dataclass
class ReportFilterResult:
    academic: list[tuple[Article, FreshnessStatus]]
    general: list[tuple[Article, FreshnessStatus]]
    total_loaded: int
    filtered_expired: int
    filtered_low_score: int


class HTMLReportGenerator:
    """Generate a static two-tab HTML report."""

    def render(
        self,
        articles: list[Article],
        title: str = "AI 前沿知识日报",
        limit: int = 200,
        profile: str = "all",
        pass_score: float | None = None,
        include_expired: bool = False,
        general_valid_days: int = GENERAL_VALID_DAYS,
        academic_valid_days: int = ACADEMIC_VALID_DAYS,
    ) -> str:
        result = self._filter_articles(
            articles,
            limit=limit,
            profile=profile,
            pass_score=pass_score,
            include_expired=include_expired,
            general_valid_days=general_valid_days,
            academic_valid_days=academic_valid_days,
        )
        total_selected = len(result.academic) + len(result.general)

        return "\n".join([
            "<!doctype html>",
            '<html lang="zh-CN">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>{escape(title)}</title>",
            self._style(),
            "</head>",
            "<body>",
            "<main>",
            f"<h1>{escape(title)}</h1>",
            self._stats(result, total_selected, general_valid_days, academic_valid_days),
            self._nav(profile),
            self._board("技术资讯", "general-board", result.general, default_visible=True),
            self._board("学术论文", "academic-board", result.academic, default_visible=(profile == "academic")),
            "</main>",
            self._script(),
            "</body>",
            "</html>",
        ])

    def write(
        self,
        articles: list[Article],
        output_path: str | Path,
        title: str = "AI 前沿知识日报",
        limit: int = 200,
        profile: str = "all",
        pass_score: float | None = None,
        include_expired: bool = False,
        general_valid_days: int = GENERAL_VALID_DAYS,
        academic_valid_days: int = ACADEMIC_VALID_DAYS,
    ) -> str:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            self.render(
                articles,
                title=title,
                limit=limit,
                profile=profile,
                pass_score=pass_score,
                include_expired=include_expired,
                general_valid_days=general_valid_days,
                academic_valid_days=academic_valid_days,
            ),
            encoding="utf-8",
        )
        return str(path)

    def _filter_articles(
        self,
        articles: list[Article],
        limit: int,
        profile: str,
        pass_score: float | None,
        include_expired: bool,
        general_valid_days: int,
        academic_valid_days: int,
    ) -> ReportFilterResult:
        academic, general = split_profiles(articles)
        if profile == "academic":
            general = []
        elif profile == "general":
            academic = []

        filtered_expired = 0
        filtered_low_score = 0

        def keep(items: list[Article], profile_name: str) -> list[tuple[Article, FreshnessStatus]]:
            nonlocal filtered_expired, filtered_low_score
            threshold = pass_score if pass_score is not None else (50.0 if profile_name == "academic" else 60.0)
            kept = []
            for article in items:
                freshness = evaluate_freshness(article, general_valid_days, academic_valid_days)
                if not freshness.is_valid and not include_expired:
                    filtered_expired += 1
                    continue
                if article.rank_score < threshold:
                    filtered_low_score += 1
                    continue
                kept.append((article, freshness))
            return kept[:limit]

        return ReportFilterResult(
            academic=keep(academic, "academic"),
            general=keep(general, "general"),
            total_loaded=len(articles),
            filtered_expired=filtered_expired,
            filtered_low_score=filtered_low_score,
        )

    def _stats(self, result: ReportFilterResult, total_selected: int, general_valid_days: int, academic_valid_days: int) -> str:
        return (
            '<div class="stats">'
            f'<span>总加载：{result.total_loaded}</span>'
            f'<span>入选：{total_selected}</span>'
            f'<span>技术资讯：{len(result.general)}</span>'
            f'<span>学术论文：{len(result.academic)}</span>'
            f'<span>过期过滤：{result.filtered_expired}</span>'
            f'<span>低分过滤：{result.filtered_low_score}</span>'
            f'<span>资讯有效期：{general_valid_days}天</span>'
            f'<span>论文有效期：{academic_valid_days}天</span>'
            '</div>'
        )

    def _nav(self, profile: str) -> str:
        if profile == "general":
            active_general, active_academic = "active", ""
        elif profile == "academic":
            active_general, active_academic = "", "active"
        else:
            active_general, active_academic = "active", ""
        return (
            '<nav class="tabs">'
            f'<button class="{active_general}" data-target="general-board">技术资讯</button>'
            f'<button class="{active_academic}" data-target="academic-board">学术论文</button>'
            '</nav>'
        )

    def _board(self, heading: str, board_id: str, items: list[tuple[Article, FreshnessStatus]], default_visible: bool) -> str:
        visible = "" if default_visible else " hidden"
        if not items:
            return f'<section id="{board_id}" class="board{visible}"><h2>{escape(heading)}</h2><p class="empty">暂无入选文章</p></section>'
        cards = "\n".join(self._card(article, freshness, index + 1) for index, (article, freshness) in enumerate(items))
        return f'<section id="{board_id}" class="board{visible}"><h2>{escape(heading)}</h2>{cards}</section>'

    def _card(self, article: Article, freshness: FreshnessStatus, rank: int) -> str:
        tags = article.tags if isinstance(article.tags, dict) else {}
        analysis = article.analysis.to_dict() if article.analysis else {}
        summary = ReportSummaryBuilder().build(article)
        age = "未知" if freshness.age_days is None else f"发表 {freshness.age_days} 天"
        return "\n".join([
            f'<article class="card" data-profile="{escape(article.score_profile)}">',
            '<div class="card-head">',
            f'<span class="rank">#{rank}</span><span class="score">{article.rank_score:.1f}</span>',
            f'<span class="freshness">{escape(freshness.label)}</span>',
            "</div>",
            f'<h3><a href="{escape(article.url)}">{escape(article.title)}</a></h3>',
            f'<p class="meta">{escape(article.source)} ｜ {escape(article.publish_date or "未知日期")} ｜ {escape(age)} ｜ 有效期 {freshness.valid_days} 天</p>',
            self._tag_group("行业", tags.get("industries", [])),
            self._tag_group("技术", tags.get("technologies", [])),
            self._tag_group("类型", tags.get("content_types", [])),
            self._summary_block(summary),
            f'<p class="abstract"><strong>原始摘要：</strong>{escape(article.abstract or article.full_text[:360])}</p>',
            self._analysis_block(analysis),
            f'<p class="reason">{escape(article.rank_reason)}</p>' if article.rank_reason else "",
            self._breakdown(article.score_breakdown),
            f'<p><a class="source-link" href="{escape(article.url)}">原文链接</a></p>' if article.url else "",
            "</article>",
        ])

    def _summary_block(self, summary) -> str:
        points = "".join(f"<li>{escape(point)}</li>" for point in summary.key_points)
        return (
            '<div class="summary">'
            f'<p><strong>一句话总结：</strong>{escape(summary.one_sentence)}</p>'
            f'<p><strong>为什么值得关注：</strong>{escape(summary.why_it_matters)}</p>'
            f'<div><strong>关键要点：</strong><ul>{points}</ul></div>'
            '</div>'
        )

    def _analysis_block(self, analysis: dict) -> str:
        rows = []
        for label, key in [("核心观点", "core_points"), ("技术细节", "technical_details"), ("关键结果", "key_results"), ("应用场景", "applications")]:
            value = analysis.get(key)
            if value:
                rows.append(f"<li><strong>{escape(label)}：</strong>{escape(str(value))}</li>")
        if not rows:
            return ""
        return f'<details open><summary>AI 分析</summary><ul>{"".join(rows)}</ul></details>'

    def _tag_group(self, label: str, values: list[str]) -> str:
        if not values:
            return ""
        tags = "".join(f'<span class="tag">{escape(value)}</span>' for value in values)
        return f'<div class="tags"><span class="tag-label">{escape(label)}</span>{tags}</div>'

    def _breakdown(self, breakdown: dict) -> str:
        if not breakdown:
            return ""
        rows = "".join(f"<li>{escape(str(key))}: {escape(str(value))}</li>" for key, value in breakdown.items())
        return f"<details><summary>分项评分</summary><ul>{rows}</ul></details>"

    def _script(self) -> str:
        return """
<script>
document.querySelectorAll('.tabs button').forEach(function(button){
  button.addEventListener('click', function(){
    document.querySelectorAll('.tabs button').forEach(function(item){ item.classList.remove('active'); });
    button.classList.add('active');
    document.querySelectorAll('.board').forEach(function(board){ board.classList.add('hidden'); });
    document.getElementById(button.dataset.target).classList.remove('hidden');
  });
});
</script>
"""

    def _style(self) -> str:
        return """
<style>
body{margin:0;background:#f7f8fa;color:#1f2933;font-family:Arial,"Microsoft YaHei",sans-serif;line-height:1.6}
main{max-width:1160px;margin:0 auto;padding:32px 20px}
h1{font-size:28px;margin:0 0 10px}h2{font-size:22px;margin:28px 0 16px}
.stats{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 18px}.stats span{background:#fff;border:1px solid #d9dee7;border-radius:4px;padding:4px 8px;color:#475467}
.tabs{display:flex;gap:8px;position:sticky;top:0;background:#f7f8fa;padding:10px 0;z-index:2}.tabs button{border:1px solid #b8c4d6;background:#fff;border-radius:4px;padding:8px 14px;cursor:pointer;font-weight:700}.tabs button.active{background:#102a43;color:#fff}
.meta{color:#667085;font-size:14px}.empty{color:#667085}.hidden{display:none}
.card{background:white;border:1px solid #d9dee7;border-radius:8px;padding:18px;margin:14px 0}
.card-head{display:flex;gap:10px;align-items:center}.rank{font-weight:700;color:#475467}.score{background:#102a43;color:white;border-radius:4px;padding:2px 8px;font-weight:700}.freshness{background:#ecfdf3;color:#027a48;border-radius:4px;padding:2px 8px;font-size:13px}
h3{font-size:19px;margin:10px 0 4px}a{color:#0b5cad;text-decoration:none}a:hover{text-decoration:underline}
.tags{margin:8px 0}.tag-label{font-weight:700;margin-right:8px;color:#344054}.tag{display:inline-block;background:#eef4ff;color:#1849a9;border-radius:4px;padding:2px 7px;margin:2px 4px 2px 0;font-size:13px}
.summary{background:#f8fbff;border-left:3px solid #2e90fa;padding:10px 12px;margin:12px 0}.summary p{margin:4px 0}.summary ul{margin:6px 0 0 18px;padding:0}
.abstract{margin-top:10px}.reason{color:#475467}.source-link{font-weight:700}
details{margin-top:10px}summary{cursor:pointer;color:#1849a9}li{font-size:14px}
</style>
"""
