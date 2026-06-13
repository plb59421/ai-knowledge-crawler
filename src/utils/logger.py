"""结构化日志配置"""

import logging
import structlog


def get_logger(name: str) -> structlog.BoundLogger:
    """获取指定名称的结构化日志器"""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(),
    )
    return structlog.get_logger(name)