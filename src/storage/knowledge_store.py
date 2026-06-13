"""知识库存储 - 将 Article 保存为 JSON 文件"""

import json
import os
from datetime import datetime
from pathlib import Path
from src.core.models import Article
from src.utils.logger import get_logger

logger = get_logger("storage")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
KB_ROOT = PROJECT_ROOT / "knowledge_base"


class KnowledgeStore:
    """文件系统知识库存储"""

    def store(self, article: Article) -> str:
        """将 Article 存入 by_source/{source}/{year}/{month}/{date}.json"""
        today = datetime.now().strftime("%Y-%m-%d")
        year = datetime.now().strftime("%Y")
        month = datetime.now().strftime("%m")

        dir_path = KB_ROOT / "by_source" / article.source / year / month
        dir_path.mkdir(parents=True, exist_ok=True)

        file_path = dir_path / f"{today}.json"

        # 读取已有数据或创建新文件
        existing = []
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                existing = json.load(f)

        # 检查是否已存在（URL 去重）
        if any(item.get("url") == article.url for item in existing):
            logger.info(f"skip duplicate: {article.url}")
            return ""

        existing.append(article.to_dict())

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

        logger.info(f"stored article: {article.id} -> {file_path}")
        return str(file_path)