import json
from collections import deque


class ContextManager:
    """Per-agent rolling conversation history with token budget enforcement.

    Each sub-agent gets its own instance — never share across agents.
    Token budget: 15,000 estimated tokens, 10 message turns max.
    """

    MAX_MESSAGES = 10
    MAX_TOKENS = 15000

    def __init__(self):
        self._history: deque[dict] = deque(maxlen=self.MAX_MESSAGES)
        self._summary: str = ""

    def add_message(self, role: str, content: str) -> None:
        self._history.append({"role": role, "content": content})

    def get_trimmed_history(self) -> list[dict]:
        messages = list(self._history)

        # Drop oldest messages until under token budget
        while self._estimate_tokens(messages) > self.MAX_TOKENS and len(messages) > 1:
            messages.pop(0)

        # Prepend rolling summary if one exists
        if self._summary:
            summary_msg = {
                "role": "user",
                "content": f"Context summary: {self._summary}",
            }
            messages = [summary_msg] + messages

        return messages

    def reset(self) -> None:
        self._history.clear()
        self._summary = ""

    def _estimate_tokens(self, messages: list[dict]) -> int:
        total_text = " ".join(m.get("content", "") for m in messages)
        return len(total_text) // 4

    def _summarize_overflow(self, messages: list[dict]) -> str:
        """Summarise overflowed messages via Claude API.

        WARNING: calls the Anthropic API — must be mocked in tests.
        """
        import anthropic

        client = anthropic.Anthropic()
        text = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in messages
        )
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=150,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Summarise the following conversation in 2 sentences:\n\n{text}"
                    ),
                }
            ],
        )
        return response.content[0].text
