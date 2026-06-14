"""OpenAI-compatible HTTP client."""

import os

import requests

from src.utils.config_loader import get_llm_config


class OpenAIClient:
    """Small OpenAI-compatible Chat Completions client."""

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        base_url: str = None,
        timeout: int = 60,
    ):
        config = get_llm_config()
        api_key_env = config.get("api_key_env", "DASHSCOPE_API_KEY")
        self.api_key = (
            api_key
            or os.environ.get("DASHSCOPE_API_KEY")
            or os.environ.get(api_key_env, "")
            or os.environ.get("LLM_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
        )
        self.model = model or os.environ.get("LLM_MODEL") or config.get("model") or "qwen-plus"
        self.base_url = (
            base_url
            or os.environ.get("OPENAI_BASE_URL")
            or os.environ.get("LLM_BASE_URL")
            or config.get("base_url")
            or "https://dashscope.aliyuncs.com/compatible-mode/v1"
        ).rstrip("/")
        self.timeout = int(os.environ.get("LLM_TIMEOUT") or config.get("timeout") or timeout)

    def complete(self, prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("missing DASHSCOPE_API_KEY, LLM_API_KEY, or OPENAI_API_KEY")

        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
