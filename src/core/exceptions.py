"""AI前沿知识爬虫 - 自定义异常体系"""


class CrawlError(Exception):
    """爬取过程中的错误"""
    def __init__(self, message: str, source: str = "", url: str = ""):
        super().__init__(message)
        self.source = source
        self.url = url


class ProcessError(Exception):
    """内容处理过程中的错误"""
    pass


class AnalysisError(Exception):
    """AI 分析过程中的错误"""
    pass


class StorageError(Exception):
    """知识库存储过程中的错误"""
    pass