"""手动爬取 CLI - 执行指定信息源的爬取、解析、存储"""

import sys
import argparse
from pathlib import Path

# 将项目根目录加入 Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 导入注册中心 + 自动注册所有爬虫
from src.core.registry import CrawlerRegistry
import src.crawlers.registry_config  # noqa: F401 — 触发自动注册

from src.storage.knowledge_store import KnowledgeStore
from src.utils.logger import get_logger

logger = get_logger("run_crawler")


def crawl_source(source: str, no_proxy: bool = False, max_pages: int = None) -> dict:
    """执行单个信息源的爬取-解析-存储流水线，返回统计信息"""
    crawler_cls, parser_cls = CrawlerRegistry.get(source)

    logger.info(f"=== start crawling: {source} ===")

    # 1. 爬取
    crawler = crawler_cls(proxy_required=not no_proxy)
    if max_pages is not None:
        crawler.max_pages = max_pages
    crawl_results = crawler.crawl()

    if not crawl_results:
        logger.info(f"[{source}] no results, skipping")
        return {"source": source, "crawled": 0, "parsed": 0, "stored": 0}

    # 2. 解析
    parser_instance = parser_cls()
    articles = []
    for result in crawl_results:
        parsed = parser_instance.parse(result)
        articles.extend(parsed)

    logger.info(f"[{source}] parsed {len(articles)} articles")

    # 3. 存储
    store = KnowledgeStore()
    stored_count = 0
    for article in articles:
        path = store.store(article)
        if path:
            stored_count += 1
            logger.info(f"stored: {article.title} ({article.url})")

    stats = {"source": source, "crawled": len(crawl_results), "parsed": len(articles), "stored": stored_count}
    logger.info(f"[{source}] finished: crawled={stats['crawled']}, parsed={stats['parsed']}, stored={stats['stored']}")
    return stats


def main():
    parser = argparse.ArgumentParser(description="AI前沿知识爬虫 - 手动爬取")
    parser.add_argument("--source", help="指定信息源名称 (可多个，逗号分隔)")
    parser.add_argument("--all", action="store_true", help="爬取所有已注册的信息源")
    parser.add_argument("--list", action="store_true", help="列出所有可用的信息源")
    parser.add_argument("--no-proxy", action="store_true", help="不使用代理")
    parser.add_argument("--max-pages", type=int, default=None, help="最大爬取页数/条数 (覆盖默认值)")
    args = parser.parse_args()

    # 列出信息源
    if args.list:
        sources = CrawlerRegistry.list_all()
        print(f"已注册的信息源 ({len(sources)} 个):")
        for s in sources:
            crawler_cls, parser_cls = CrawlerRegistry.get(s)
            proxy = "需代理" if crawler_cls.proxy_required else "无需代理"
            print(f"  - {s}: {crawler_cls.source_name} | fetcher={crawler_cls.fetcher_type} | {proxy}")
        return

    # 确定要爬取的信息源
    if args.all:
        sources = CrawlerRegistry.list_all()
    elif args.source:
        sources = [s.strip() for s in args.source.split(",")]
        # 验证所有源是否已注册
        for s in sources:
            if not CrawlerRegistry.has(s):
                print(f"错误: 未知信息源 '{s}'")
                print(f"可用信息源: {CrawlerRegistry.list_all()}")
                sys.exit(1)
    else:
        print("错误: 请指定 --source <name> 或 --all")
        print(f"可用信息源: {CrawlerRegistry.list_all()}")
        sys.exit(1)

    # 执行爬取
    all_stats = []
    for source in sources:
        try:
            stats = crawl_source(source, no_proxy=args.no_proxy, max_pages=args.max_pages)
            all_stats.append(stats)
        except Exception as e:
            logger.error(f"[{source}] crawl failed: {e}")
            all_stats.append({"source": source, "crawled": 0, "parsed": 0, "stored": 0, "error": str(e)})

    # 汇总报告
    print("\n=== 爬取汇总 ===")
    total_crawled = total_parsed = total_stored = 0
    for stats in all_stats:
        status = "OK" if "error" not in stats else f"ERROR: {stats['error']}"
        print(f"  {stats['source']}: crawled={stats['crawled']}, parsed={stats['parsed']}, stored={stats['stored']} [{status}]")
        total_crawled += stats["crawled"]
        total_parsed += stats["parsed"]
        total_stored += stats["stored"]
    print(f"  合计: crawled={total_crawled}, parsed={total_parsed}, stored={total_stored}")


if __name__ == "__main__":
    main()
