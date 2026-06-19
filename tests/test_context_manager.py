import unittest
from unittest.mock import MagicMock, patch
from core.context_manager import ContextManager


class TestContextManager(unittest.TestCase):
    def test_adding_10_messages_stays_within_deque(self):
        cm = ContextManager()
        for i in range(10):
            cm.add_message("user", f"message {i}")
        history = cm.get_trimmed_history()
        self.assertEqual(len(history), 10)

    def test_adding_12_messages_trims_to_10(self):
        cm = ContextManager()
        for i in range(12):
            cm.add_message("user", f"message {i}")
        # deque maxlen=10 keeps only the last 10
        history = cm.get_trimmed_history()
        self.assertLessEqual(len(history), 10)

    def test_token_budget_enforcement(self):
        cm = ContextManager()
        # Each message ~4000 tokens (16000 chars); 4 messages = ~16000 tokens > 15000 limit
        long_content = "x" * 16000
        for _ in range(4):
            cm.add_message("user", long_content)
        history = cm.get_trimmed_history()
        total_tokens = sum(len(m["content"]) // 4 for m in history)
        self.assertLessEqual(total_tokens, ContextManager.MAX_TOKENS)

    def test_reset_clears_history_and_summary(self):
        cm = ContextManager()
        cm.add_message("user", "hello")
        cm._summary = "some summary"
        cm.reset()
        self.assertEqual(len(cm._history), 0)
        self.assertEqual(cm._summary, "")

    def test_summary_prepended_to_history(self):
        cm = ContextManager()
        cm._summary = "Prior context summary."
        cm.add_message("user", "current message")
        history = cm.get_trimmed_history()
        self.assertEqual(history[0]["content"], "Context summary: Prior context summary.")

    @patch("anthropic.Anthropic")
    def test_summarize_overflow_calls_api(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client
        mock_client.messages.create.return_value = MagicMock(
            content=[MagicMock(text="Summary text.")]
        )
        cm = ContextManager()
        messages = [{"role": "user", "content": "hello"}, {"role": "assistant", "content": "hi"}]
        result = cm._summarize_overflow(messages)
        self.assertIsInstance(result, str)
        mock_client.messages.create.assert_called_once()


if __name__ == "__main__":
    unittest.main()
