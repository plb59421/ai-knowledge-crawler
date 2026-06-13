"""ArXiv PDF 全文提取器 - 从 PDF 下载并提取文本"""

import os
import tempfile
from src.utils.logger import get_logger

logger = get_logger("arxiv.pdf_extractor")


class PDFExtractor:
    """从 ArXiv PDF 提取全文"""

    def extract(self, pdf_url: str, arxiv_id: str) -> str:
        """下载 PDF 并提取全文文本

        Args:
            pdf_url: PDF 下载链接
            arxiv_id: ArXiv 论文 ID

        Returns:
            提取的纯文本内容
        """
        from scrapling import Fetcher
        from src.utils.proxy_helper import detect_proxy, get_proxy_dict

        # 下载 PDF
        logger.info(f"[arxiv] downloading PDF: {pdf_url}")

        proxy_url = detect_proxy() if os.environ.get("HTTPS_PROXY") or os.environ.get("HTTP_PROXY") else None
        fetcher_args = {}
        if proxy_url:
            fetcher_args["proxies"] = get_proxy_dict(proxy_url)

        fetcher = Fetcher(**fetcher_args)

        # 保存到临时文件
        temp_dir = tempfile.mkdtemp()
        pdf_path = os.path.join(temp_dir, f"{arxiv_id}.pdf")

        try:
            response = fetcher.get(pdf_url)
            # 获取 PDF 二进制内容
            content = response.content if hasattr(response, 'content') else b""

            if not content:
                logger.warning(f"[arxiv] empty PDF content for {arxiv_id}")
                return ""

            with open(pdf_path, "wb") as f:
                f.write(content)

            logger.info(f"[arxiv] PDF saved: {pdf_path} ({len(content)} bytes)")

        except Exception as e:
            logger.error(f"[arxiv] PDF download failed: {e}")
            return ""

        # 提取文本
        try:
            import pdfplumber
            text_parts = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)

            full_text = "\n".join(text_parts)
            logger.info(f"[arxiv] PDF text extracted: {len(full_text)} chars from {len(text_parts)} pages")
            return full_text

        except ImportError:
            logger.warning("[arxiv] pdfplumber not installed, cannot extract PDF text")
            return ""
        except Exception as e:
            logger.error(f"[arxiv] PDF extraction failed: {e}")
            return ""

        finally:
            # 清理临时文件
            try:
                os.remove(pdf_path)
                os.rmdir(temp_dir)
            except Exception:
                pass