"""结构化日志配置"""

import logging
from datetime import datetime
from pathlib import Path
import structlog


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LOG_ROOT = PROJECT_ROOT / "logs"
_CONFIGURED = False


def get_logger(name: str) -> structlog.BoundLogger:
    """获取指定名称的结构化日志器"""
    global _CONFIGURED
    LOG_ROOT.mkdir(parents=True, exist_ok=True)
    log_file = LOG_ROOT / f"{datetime.now().strftime('%Y-%m-%d')}.log"
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding="utf-8"),
        ],
        format="%(message)s",
        force=not _CONFIGURED,
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
    _CONFIGURED = True
    return structlog.get_logger(name)
