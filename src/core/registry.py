"""爬虫注册中心 - 管理所有信息源的爬虫和解析器映射"""

from src.utils.logger import get_logger

logger = get_logger("registry")


class CrawlerRegistry:
    """爬虫注册中心，管理 source_name → (CrawlerClass, ParserClass) 映射"""

    _registry: dict = {}

    @classmethod
    def register(cls, name: str, crawler_cls, parser_cls):
        """注册一个信息源的爬虫和解析器"""
        cls._registry[name] = (crawler_cls, parser_cls)
        logger.info(f"registered crawler: {name}")

    @classmethod
    def get(cls, name: str):
        """获取指定信息源的爬虫和解析器类"""
        if name not in cls._registry:
            raise KeyError(f"Unknown source: {name}. Available: {cls.list_all()}")
        return cls._registry[name]

    @classmethod
    def list_all(cls) -> list[str]:
        """列出所有已注册的信息源名称"""
        return list(cls._registry.keys())

    @classmethod
    def has(cls, name: str) -> bool:
        """检查信息源是否已注册"""
        return name in cls._registry