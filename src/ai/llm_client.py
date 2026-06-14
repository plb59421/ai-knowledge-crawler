"""LLM client protocol."""

from typing import Protocol


class LLMClient(Protocol):
    """Minimal synchronous LLM interface used by the summarizer."""

    def complete(self, prompt: str) -> str:
        """Return model text for a rendered prompt."""
        ...
