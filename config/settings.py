import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    anthropic_api_key: str = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))
    orchestrator_model: str = "claude-sonnet-4-6"
    subagent_model: str = "claude-haiku-4-5-20251001"
    triage_model: str = "claude-sonnet-4-6"

    context_max_messages: int = 10
    context_max_tokens: int = 15000

    rag_top_k: int = 3
    rag_similarity_threshold: float = 0.2

    mcp_host: str = "127.0.0.1"
    mcp_port: int = int(os.getenv("MCP_PORT", "8765"))

    otel_enabled: bool = True
    otel_service_name: str = "investment-advisor-poc"
    otel_log_file: str = os.getenv("OTEL_LOG_FILE", "reports/otel_traces.jsonl")
    metrics_port: int = 9090

    enable_triage: bool = os.getenv("ENABLE_TRIAGE", "true").lower() == "true"
    enable_rag: bool = True
    enable_prompt_caching: bool = True

    rules_file: str = "config/investment_rules.yaml"


config = Settings()
