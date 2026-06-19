import json
import unittest
from unittest.mock import MagicMock, patch, call


def _make_mock_response(text: str):
    """Build a minimal mock that looks like an anthropic messages response."""
    block = MagicMock()
    block.type = "text"
    block.text = text
    usage = MagicMock()
    usage.input_tokens = 100
    usage.output_tokens = 50
    response = MagicMock()
    response.content = [block]
    response.usage = usage
    return response


class TestOrchestrator(unittest.TestCase):
    @patch("anthropic.Anthropic")
    def _make_orchestrator(self, mock_anthropic_cls, frontend_reply=None, backend_reply=None):
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        default_frontend = json.dumps({
            "valid": True,
            "errors": [],
            "profile": {
                "age": 30,
                "monthly_income": 60000.0,
                "monthly_savings": 12000.0,
                "risk": "MEDIUM",
                "goal": "LONG",
            },
        })
        default_backend = json.dumps({"explanation": "This is your plan."})

        mock_client.messages.create.side_effect = [
            _make_mock_response(frontend_reply or default_frontend),
            _make_mock_response(backend_reply or default_backend),
        ]
        return mock_client

    @patch("anthropic.Anthropic")
    def test_orchestrator_calls_frontend_first_then_backend(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        frontend_reply = json.dumps({
            "valid": True,
            "errors": [],
            "profile": {
                "age": 30,
                "monthly_income": 60000.0,
                "monthly_savings": 12000.0,
                "risk": "MEDIUM",
                "goal": "LONG",
            },
        })
        backend_reply = json.dumps({"explanation": "Here is your investment plan."})

        mock_client.messages.create.side_effect = [
            _make_mock_response(frontend_reply),
            _make_mock_response(backend_reply),
        ]

        # Import here so the Anthropic patch is active during __init__
        from orchestrator.orchestrator import InvestmentOrchestrator
        from config.settings import config as app_config
        orch = InvestmentOrchestrator()

        form_data = {
            "age": 30,
            "monthly_income": 60000,
            "monthly_savings": 12000,
            "risk": "MEDIUM",
            "goal": "LONG",
        }
        # Disable triage so the background thread doesn't make an extra API call
        original_triage = app_config.enable_triage
        app_config.enable_triage = False
        try:
            response = orch.process_advisory_request(form_data)
        finally:
            app_config.enable_triage = original_triage

        # Two calls: frontend-agent (validate), backend-agent (explain)
        self.assertEqual(mock_client.messages.create.call_count, 2)

        # First call should use subagent model (frontend)
        first_call_kwargs = mock_client.messages.create.call_args_list[0][1]
        self.assertEqual(first_call_kwargs["model"], "claude-haiku-4-5-20251001")

    @patch("anthropic.Anthropic")
    def test_advisory_response_has_all_fields(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        frontend_reply = json.dumps({
            "valid": True,
            "errors": [],
            "profile": {
                "age": 45,
                "monthly_income": 80000.0,
                "monthly_savings": 20000.0,
                "risk": "LOW",
                "goal": "SHORT",
            },
        })
        backend_reply = json.dumps({"explanation": "Safety first for short-term goals."})

        mock_client.messages.create.side_effect = [
            _make_mock_response(frontend_reply),
            _make_mock_response(backend_reply),
        ]

        from orchestrator.orchestrator import InvestmentOrchestrator
        orch = InvestmentOrchestrator()

        response = orch.process_advisory_request({
            "age": 45,
            "monthly_income": 80000,
            "monthly_savings": 20000,
            "risk": "LOW",
            "goal": "SHORT",
        })

        self.assertIsNotNone(response.profile)
        self.assertIsNotNone(response.allocation)
        self.assertIsNotNone(response.explanation)
        self.assertIsNotNone(response.disclaimer)
        self.assertIsNotNone(response.chart_data)
        self.assertEqual(sum(response.allocation.model_dump().values()), 100)

    @patch("anthropic.Anthropic")
    def test_invalid_input_raises_value_error(self, mock_anthropic_cls):
        mock_client = MagicMock()
        mock_anthropic_cls.return_value = mock_client

        invalid_reply = json.dumps({
            "valid": False,
            "errors": ["monthly_savings must be less than monthly_income"],
            "profile": None,
        })
        mock_client.messages.create.return_value = _make_mock_response(invalid_reply)

        from orchestrator.orchestrator import InvestmentOrchestrator
        orch = InvestmentOrchestrator()

        with self.assertRaises(ValueError):
            orch.process_advisory_request({
                "age": 30,
                "monthly_income": 5000,
                "monthly_savings": 9000,  # savings > income
                "risk": "MEDIUM",
                "goal": "LONG",
            })


if __name__ == "__main__":
    unittest.main()
