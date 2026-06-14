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
from src.ai.openai_client import OpenAIClient
from src.ai.summarizer import ArticleSummarizer
from src.processors.article_processor import ArticleProcessor
from src.ranking.report_data import ReportDataExporter
from src.utils.config_loader import get_source_config
from src.utils.logger import get_logger

logger = get_logger("run_crawler")


def crawl_source(
    source: str,
    no_proxy: bool = False,
    max_pages: int = None,
    processor: ArticleProcessor = None,
    analysis_limit: int = 10,
    force_analyze: bool = False,
) -> dict:
    """执行单个信息源的爬取-解析-存储流水线，返回统计信息"""
    crawler_cls, parser_cls = CrawlerRegistry.get(source)
    stats = {
        "source": source,
        "crawled": 0,
        "parsed": 0,
        "stored": 0,
        "updated": 0,
        "analyzed": 0,
        "analysis_failed": 0,
        "analysis_skipped": 0,
        "error": "",
    }

    logger.info(f"=== start crawling: {source} ===")

    # 1. 爬取
    crawler = crawler_cls(proxy_required=not no_proxy)
    if max_pages is not None:
        crawler.max_pages = max_pages
    crawl_results = crawler.crawl()
    stats["crawled"] = len(crawl_results)

    if not crawl_results:
        logger.info(f"[{source}] no results, skipping")
        return stats

    # 2. 解析
    parser_instance = parser_cls()
    articles = []
    for result in crawl_results:
        try:
            parsed = parser_instance.parse(result)
            articles.extend(parsed)
        except Exception as e:
            logger.error(f"[{source}] parse failed for {result.url}: {e}")

    stats["parsed"] = len(articles)
    logger.info(f"[{source}] parsed {len(articles)} articles")

    # 3. 存储
    store = KnowledgeStore()
    stored_count = 0
    for article in articles:
        already_exists = store.exists(article)
        if already_exists and not force_analyze:
            if processor and processor.summarize:
                stats["analysis_skipped"] += 1
            logger.info(f"skip existing article before processing: {article.url or article.title}")
            continue

        if processor:
            allow_summarize = bool(processor.summarize)
            if allow_summarize and stats["analyzed"] >= analysis_limit:
                stats["analysis_skipped"] += 1
                allow_summarize = False
            article = processor.process(article, allow_summarize=allow_summarize)
            if allow_summarize:
                if article.analysis and article.analysis.error:
                    stats["analysis_failed"] += 1
                else:
                    stats["analyzed"] += 1

        path = store.update_existing(article) if already_exists and force_analyze else store.store(article)
        if path and already_exists and force_analyze:
            stats["updated"] += 1
            logger.info(f"updated: {article.title} ({article.url})")
        elif path:
            stored_count += 1
            logger.info(f"stored: {article.title} ({article.url})")

    stats["stored"] = stored_count
    logger.info(f"[{source}] finished: crawled={stats['crawled']}, parsed={stats['parsed']}, stored={stats['stored']}")
    return stats


def main():
    parser = argparse.ArgumentParser(description="AI前沿知识爬虫 - 手动爬取")
    parser.add_argument("--source", help="指定信息源名称 (可多个，逗号分隔)")
    parser.add_argument("--all", action="store_true", help="爬取所有已注册的信息源")
    parser.add_argument("--list", action="store_true", help="列出所有可用的信息源")
    parser.add_argument("--no-proxy", action="store_true", help="不使用代理")
    parser.add_argument("--max-pages", type=int, default=None, help="最大爬取页数/条数 (覆盖默认值)")
    parser.add_argument("--clean-html", action="store_true", help="对正文执行基础 HTML 清洗")
    parser.add_argument("--extract-topics", action="store_true", help="启用本地关键词 topic 提取")
    parser.add_argument("--score-relevance", action="store_true", help="启用本地相关性评分")
    parser.add_argument("--summarize", action="store_true", help="调用 LLM 生成结构化摘要")
    parser.add_argument("--no-llm", action="store_true", help="禁用 LLM 调用，仅运行本地规则")
    parser.add_argument("--analysis-language", default="zh-CN", help="AI 分析输出语言")
    parser.add_argument("--auto-tag", action="store_true", help="生成中文结构化标签")
    parser.add_argument("--rank", action="store_true", help="计算分类型排序评分")
    parser.add_argument("--html-report", action="store_true", help="运行结束后生成 HTML 排序报告")
    parser.add_argument("--report-limit", type=int, default=200, help="HTML 报告安全展示上限")
    parser.add_argument("--pass-score", type=float, default=None, help="HTML 报告统一及格线")
    parser.add_argument("--general-valid-days", type=int, default=30, help="技术资讯时效天数")
    parser.add_argument("--academic-valid-days", type=int, default=90, help="学术论文时效天数")
    parser.add_argument("--include-expired", action="store_true", help="HTML 报告包含过期内容")
    parser.add_argument("--analysis-limit", type=int, default=10, help="Max AI analyses per run")
    parser.add_argument("--force-analyze", action="store_true", help="Run AI analysis even when an article already exists")
    args = parser.parse_args()

    # 列出信息源
    if args.list:
        sources = CrawlerRegistry.list_all()
        print(f"已注册的信息源 ({len(sources)} 个):")
        for s in sources:
            crawler_cls, parser_cls = CrawlerRegistry.get(s)
            source_config = get_source_config(s)
            fetcher_type = source_config.get("fetcher_type", crawler_cls.fetcher_type)
            proxy_required = source_config.get("proxy_required", crawler_cls.proxy_required)
            proxy = "需代理" if proxy_required else "无需代理"
            print(f"  - {s}: {crawler_cls.source_name} | fetcher={fetcher_type} | {proxy}")
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
    auto_tag = args.auto_tag or args.html_report
    rank = args.rank or args.html_report
    summarizer = None
    if args.summarize and not args.no_llm:
        summarizer = ArticleSummarizer(OpenAIClient(), language=args.analysis_language)
    processor = ArticleProcessor(
        clean_html=args.clean_html,
        extract_topics=args.extract_topics,
        score_relevance=args.score_relevance,
        summarize=args.summarize and not args.no_llm,
        summarizer=summarizer,
        auto_tag=auto_tag,
        rank=rank,
    )
    for source in sources:
        try:
            stats = crawl_source(
                source,
                no_proxy=args.no_proxy,
                max_pages=args.max_pages,
                processor=processor,
                analysis_limit=args.analysis_limit,
                force_analyze=args.force_analyze,
            )
            all_stats.append(stats)
        except Exception as e:
            logger.error(f"[{source}] crawl failed: {e}")
            all_stats.append({"source": source, "crawled": 0, "parsed": 0, "stored": 0, "error": str(e)})

    store = KnowledgeStore()
    store.record_crawl_history(all_stats)
    store.write_daily_report(all_stats)
    if args.html_report:
        today = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        ReportDataExporter(store.root).export(
            date=today,
            limit=args.report_limit,
            profile="all",
            pass_score=args.pass_score,
            include_expired=args.include_expired,
            general_valid_days=args.general_valid_days,
            academic_valid_days=args.academic_valid_days,
        )

    # 汇总报告
    print("\n=== 爬取汇总 ===")
    total_crawled = total_parsed = total_stored = 0
    for stats in all_stats:
        status = "OK" if not stats.get("error") else f"ERROR: {stats['error']}"
        print(f"  {stats['source']}: crawled={stats['crawled']}, parsed={stats['parsed']}, stored={stats['stored']} [{status}]")
        total_crawled += stats["crawled"]
        total_parsed += stats["parsed"]
        total_stored += stats["stored"]
    print(f"  合计: crawled={total_crawled}, parsed={total_parsed}, stored={total_stored}")


if __name__ == "__main__":
    main()
