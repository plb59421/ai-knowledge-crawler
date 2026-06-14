"""Mock LLM client for tests and dry runs."""


class MockLLMClient:
    """Return a configurable response without network access."""

    def __init__(self, response: str = None):
        self.response = response or (
            '{"core_points":"Mock summary","technical_details":"Mock technical details",'
            '"key_results":"Mock results","applications":"Mock applications",'
            '"risk_level":"low","importance_score":5.0}'
        )
        self.calls: list[str] = []

    def complete(self, prompt: str) -> str:
        self.calls.append(prompt)
        return self.response
