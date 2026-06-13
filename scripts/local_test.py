"""本地测试入口 - 用本地 HTML 样本验证完整流水线（不依赖网络）"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scrapling import Fetcher
from src.core.models import CrawlResult, Article
from src.storage.knowledge_store import KnowledgeStore
from src.utils.logger import get_logger

logger = get_logger("local_test")


def main():
    logger.info("=== local pipeline test start ===")

    # 1. 从本地文件读取 HTML（模拟爬取结果）
    fixture_path = PROJECT_ROOT / "tests" / "fixtures" / "sample_hf_blog.html"
    logger.info(f"reading fixture: {fixture_path}")

    with open(fixture_path, "r", encoding="utf-8") as f:
        raw_html = f.read()

    crawl_result = CrawlResult(
        url="https://huggingface.co/blog/smolvlm2",
        raw_html=raw_html,
        metadata={"source": "huggingface", "fetcher": "local_test"},
    )
    logger.info(f"loaded fixture HTML ({len(raw_html)} chars)")

    # 2. 用 Scrapling 解析 HTML（模拟 parser）
    logger.info("parsing content with Scrapling CSS selectors...")
    fetcher = Fetcher()
    # Scrapling 可以直接解析 HTML 字符串 - 使用 from_string 方法
    # 如果不支持，则用 BeautifulSoup 作为备选
    try:
        # 尝试 Scrapling 的解析方法
        from scrapling import Adaptor
        response = Adaptor(raw_html)

        title = response.css("h1::text").get() or "Unknown"
        content_parts = []
        for p in response.css("div.prose p"):
            text = p.css("::text").get()
            if text:
                content_parts.append(text.strip())

        abstract = content_parts[0][:300] if content_parts else ""
        full_text = "\n".join(content_parts)

        author = response.css(".author::text").get() or ""
        date = response.css("time::attr(datetime)").get() or ""

    except (ImportError, TypeError, AttributeError):
        # 备选方案：用 BeautifulSoup
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(raw_html, "html.parser")

        title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "Unknown"
        content_parts = [p.get_text(strip=True) for p in soup.select("div.prose p") if p.get_text(strip=True)]
        abstract = content_parts[0][:300] if content_parts else ""
        full_text = "\n".join(content_parts)

        author = soup.select_one(".author").get_text(strip=True) if soup.select_one(".author") else ""
        date_el = soup.select_one("time")
        date = date_el.get("datetime", "") if date_el else ""

    article = Article(
        id="hf_smolvlm2",
        source="huggingface",
        title=title.strip(),
        abstract=abstract,
        full_text=full_text,
        authors=[author] if author else [],
        publish_date=date,
        url="https://huggingface.co/blog/smolvlm2",
    )

    logger.info(f"parsed: title='{article.title}'")
    logger.info(f"  abstract: {article.abstract[:80]}...")
    logger.info(f"  content: {len(article.full_text)} chars, {len(content_parts)} paragraphs")
    logger.info(f"  author: {article.authors}")
    logger.info(f"  date: {article.publish_date}")

    # 3. 存入知识库
    store = KnowledgeStore()
    path = store.store(article)

    if path:
        logger.info(f"stored successfully -> {path}")
    else:
        logger.warning("store failed or duplicate")

    # 4. 验证存储结果
    logger.info("=== verifying stored file ===")
    from pathlib import Path as P
    kb_dir = PROJECT_ROOT / "knowledge_base" / "by_source" / "huggingface"
    json_files = list(kb_dir.rglob("*.json"))
    if json_files:
        import json
        with open(json_files[0], "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"found {len(data)} articles in {json_files[0]}")
        for item in data:
            logger.info(f"  - [{item['source']}] {item['title']} ({len(item['full_text'])} chars)")
    else:
        logger.warning("no JSON files found in knowledge_base")

    logger.info("=== local pipeline test complete ===")


if __name__ == "__main__":
    main()