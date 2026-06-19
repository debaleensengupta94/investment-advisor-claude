from prometheus_client import Counter, Gauge, Histogram, start_http_server

REQUEST_COUNT = Counter(
    "investment_requests_total",
    "Total advisory requests",
    ["risk_level", "goal"],
)

REQUEST_LATENCY = Histogram(
    "investment_request_latency_seconds",
    "Request latency in seconds",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0],
)

ACTIVE_SESSIONS = Gauge(
    "investment_active_sessions",
    "Currently active advisory sessions",
)

TOKEN_USAGE = Counter(
    "investment_token_usage_total",
    "Token usage by agent and direction",
    ["agent", "direction"],
)

TRIAGE_SCORE = Histogram(
    "investment_triage_score",
    "Triage quality scores",
    buckets=[1, 2, 3, 4, 5],
)


def start_metrics_server(port: int = 9090) -> None:
    start_http_server(port)
