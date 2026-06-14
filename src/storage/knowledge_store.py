"""知识库存储 - 将 Article 保存为 JSON 文件"""

import json
from datetime import datetime
from pathlib import Path
from src.core.models import Article
from src.utils.logger import get_logger

logger = get_logger("storage")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
KB_ROOT = PROJECT_ROOT / "knowledge_base"


class KnowledgeStore:
    """文件系统知识库存储"""

    def __init__(self, root: str | Path = None):
        self.root = Path(root) if root else KB_ROOT
        self.by_source_root = self.root / "by_source"
        self.by_time_root = self.root / "by_time"
        self.by_topic_root = self.root / "by_topic"
        self.index_root = self.root / "index"
        self.metadata_root = self.root / "metadata"
        self.index_root.mkdir(parents=True, exist_ok=True)
        self.metadata_root.mkdir(parents=True, exist_ok=True)

    def _load_json(self, path: Path, default):
        """Load JSON with a safe fallback for missing, empty, or broken files."""
        if not path.exists() or path.stat().st_size == 0:
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.error(f"invalid JSON at {path}: {e}")
            return default
        except OSError as e:
            logger.error(f"failed to read {path}: {e}")
            return default

    def _write_json(self, path: Path, data) -> bool:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except OSError as e:
            logger.error(f"failed to write {path}: {e}")
            return False

    def _load_mapping(self, path: Path) -> dict:
        data = self._load_json(path, {})
        if isinstance(data, dict):
            return data
        logger.error(f"index file is not an object, rebuilding as empty mapping: {path}")
        return {}

    def _source_title_key(self, article: Article) -> str:
        return f"{article.source}:{article.title.strip().lower()}"

    def _is_duplicate(self, article: Article, existing: list[dict]) -> bool:
        url_index = self._load_mapping(self.index_root / "url_index.json")
        dedup_records = self._load_mapping(self.metadata_root / "dedup_records.json")
        title_key = self._source_title_key(article)

        if article.url and (article.url in url_index or any(item.get("url") == article.url for item in existing)):
            logger.info(f"skip duplicate URL: {article.url}")
            return True
        if article.title and (
            title_key in dedup_records
            or any(title_key == f"{item.get('source', '')}:{item.get('title', '').strip().lower()}" for item in existing)
        ):
            logger.info(f"skip duplicate source/title: {article.source} | {article.title}")
            return True
        return False

    def exists(self, article: Article) -> bool:
        """Return whether an article already exists by URL or source/title."""
        return self._find_existing_record(article) is not None

    def _find_existing_record(self, article: Article) -> dict | None:
        url_index = self._load_mapping(self.index_root / "url_index.json")
        dedup_records = self._load_mapping(self.metadata_root / "dedup_records.json")
        title_key = self._source_title_key(article)
        if article.url and article.url in url_index:
            return url_index[article.url]
        if article.title and title_key in dedup_records:
            return dedup_records[title_key]

        source_root = self.by_source_root / article.source
        if not source_root.exists():
            return None
        for path in source_root.rglob("*.json"):
            data = self._load_json(path, [])
            if not isinstance(data, list):
                continue
            for item in data:
                item_key = f"{item.get('source', '')}:{item.get('title', '').strip().lower()}"
                if (article.url and item.get("url") == article.url) or (article.title and item_key == title_key):
                    return {"path": str(path), "url": item.get("url", ""), "title": item.get("title", "")}
        return None

    def update_existing(self, article: Article, stored_at: datetime = None) -> str:
        """Update an existing article record by URL or source/title."""
        title_key = self._source_title_key(article)
        record = self._find_existing_record(article)
        if not record or not record.get("path"):
            return ""

        file_path = Path(record["path"])
        data = self._load_json(file_path, [])
        if not isinstance(data, list):
            logger.error(f"storage file is not a list: {file_path}")
            return ""

        updated = False
        for index, item in enumerate(data):
            item_key = f"{item.get('source', '')}:{item.get('title', '').strip().lower()}"
            if (article.url and item.get("url") == article.url) or item_key == title_key:
                data[index] = article.to_dict()
                updated = True
                break

        if not updated or not self._write_json(file_path, data):
            return ""

        now = stored_at or datetime.now()
        self._update_metadata(article, file_path)
        self._write_views(article, now)
        self._write_markdown_export(article, now)
        logger.info(f"updated article: {article.id} -> {file_path}")
        return str(file_path)

    def _update_metadata(self, article: Article, file_path: Path):
        url_index_path = self.index_root / "url_index.json"
        dedup_path = self.metadata_root / "dedup_records.json"
        search_index_path = self.index_root / "full_text_index.json"

        url_index = self._load_mapping(url_index_path)
        if article.url:
            url_index[article.url] = {
                "source": article.source,
                "title": article.title,
                "publish_date": article.publish_date,
                "topics": article.topics,
                "tags": article.tags,
                "relevance_score": article.relevance_score,
                "rank_score": article.rank_score,
                "score_profile": article.score_profile,
                "path": str(file_path),
            }
            self._write_json(url_index_path, url_index)

        dedup_records = self._load_mapping(dedup_path)
        dedup_records[self._source_title_key(article)] = {
            "url": article.url,
            "source": article.source,
            "title": article.title,
            "path": str(file_path),
        }
        self._write_json(dedup_path, dedup_records)

        search_index = self._load_mapping(search_index_path)
        search_index[article.id] = {
            "source": article.source,
            "title": article.title,
            "url": article.url,
            "topics": article.topics,
            "tags": article.tags,
            "rank_score": article.rank_score,
            "text": f"{article.title}\n{article.abstract}\n{article.full_text}"[:5000],
        }
        self._write_json(search_index_path, search_index)

    def _append_view_record(self, path: Path, article: Article):
        data = self._load_json(path, [])
        if not isinstance(data, list):
            logger.error(f"view file is not a list: {path}")
            data = []
        if not any(item.get("url") == article.url for item in data):
            data.append(article.to_dict())
            self._write_json(path, data)

    def _write_views(self, article: Article, now: datetime):
        date_key = now.strftime("%Y-%m-%d")
        year = now.strftime("%Y")
        month = now.strftime("%m")

        self._append_view_record(self.by_time_root / year / month / f"{date_key}.json", article)

        topics = article.topics or ["uncategorized"]
        for topic in topics:
            safe_topic = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in topic)[:80]
            self._append_view_record(self.by_topic_root / safe_topic / year / month / f"{date_key}.json", article)

    def _write_markdown_export(self, article: Article, now: datetime):
        date_key = now.strftime("%Y-%m-%d")
        export_dir = self.root / "exports" / "markdown" / article.source
        export_dir.mkdir(parents=True, exist_ok=True)
        safe_id = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in article.id)
        path = export_dir / f"{date_key}_{safe_id}.md"
        analysis = article.analysis.to_dict() if article.analysis else {}
        lines = [
            f"# {article.title}",
            "",
            f"- Source: {article.source}",
            f"- URL: {article.url}",
            f"- Publish Date: {article.publish_date}",
            f"- Topics: {', '.join(article.topics)}",
            f"- Relevance Score: {article.relevance_score}",
            "",
            "## Abstract",
            article.abstract,
            "",
        ]
        if analysis:
            lines.extend([
                "## AI Analysis",
                f"- Core Points: {analysis.get('core_points', '')}",
                f"- Technical Details: {analysis.get('technical_details', '')}",
                f"- Key Results: {analysis.get('key_results', '')}",
                f"- Applications: {analysis.get('applications', '')}",
                "",
            ])
        lines.extend(["## Full Text", article.full_text])
        try:
            path.write_text("\n".join(lines), encoding="utf-8")
        except OSError as e:
            logger.error(f"failed to write markdown export {path}: {e}")

    def store(self, article: Article, stored_at: datetime = None) -> str:
        """将 Article 存入 by_source/{source}/{year}/{month}/{date}.json"""
        now = stored_at or datetime.now()
        today = now.strftime("%Y-%m-%d")
        year = now.strftime("%Y")
        month = now.strftime("%m")

        dir_path = self.by_source_root / article.source / year / month
        dir_path.mkdir(parents=True, exist_ok=True)

        file_path = dir_path / f"{today}.json"

        # 读取已有数据或创建新文件
        existing = self._load_json(file_path, [])
        if not isinstance(existing, list):
            logger.error(f"storage file is not a list: {file_path}")
            existing = []

        # 检查是否已存在（URL、source+title 去重）
        if self._is_duplicate(article, existing):
            return ""

        existing.append(article.to_dict())

        if not self._write_json(file_path, existing):
            return ""

        self._update_metadata(article, file_path)
        self._write_views(article, now)
        self._write_markdown_export(article, now)
        logger.info(f"stored article: {article.id} -> {file_path}")
        return str(file_path)

    def record_crawl_history(self, stats: list[dict]):
        """Append one CLI run summary to metadata/crawl_history.json."""
        history_path = self.metadata_root / "crawl_history.json"
        history = self._load_json(history_path, [])
        if not isinstance(history, list):
            logger.error(f"crawl history is not a list: {history_path}")
            history = []

        history.append({
            "run_time": datetime.now().isoformat(),
            "sources": stats,
        })
        self._write_json(history_path, history)

    def write_daily_report(self, stats: list[dict], report_date: datetime = None) -> str:
        """Write one daily run report into metadata."""
        now = report_date or datetime.now()
        report_path = self.metadata_root / f"daily_report_{now.strftime('%Y-%m-%d')}.json"
        report = {
            "date": now.strftime("%Y-%m-%d"),
            "sources": stats,
            "totals": {
                "crawled": sum(item.get("crawled", 0) for item in stats),
                "parsed": sum(item.get("parsed", 0) for item in stats),
                "stored": sum(item.get("stored", 0) for item in stats),
                "updated": sum(item.get("updated", 0) for item in stats),
                "analyzed": sum(item.get("analyzed", 0) for item in stats),
                "analysis_failed": sum(item.get("analysis_failed", 0) for item in stats),
                "analysis_skipped": sum(item.get("analysis_skipped", 0) for item in stats),
                "errors": len([item for item in stats if item.get("error")]),
            },
        }
        self._write_json(report_path, report)
        return str(report_path)
