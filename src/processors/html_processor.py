"""HTML 内容处理器 - 清洗 HTML 提取纯文本"""

import re


class HTMLProcessor:
    """简单的 HTML 清洗处理器"""

    def process(self, raw_html: str) -> str:
        """去除 HTML 标签，返回纯文本"""
        if not raw_html:
            return ""

        # 去除 script 和 style 标签及内容
        text = re.sub(r"<script[^>]*>.*?</script>", "", raw_html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)

        # 去除所有 HTML 标签
        text = re.sub(r"<[^>]+>", "", text)

        # 去除多余空白
        text = re.sub(r"\s+", " ", text).strip()

        return text