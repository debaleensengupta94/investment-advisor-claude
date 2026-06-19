# Investment Advisor POC

> **Educational demo only. Not real financial advice.**

A beginner-friendly investment advisory AI agent for banking customers. Enter your age, income, savings capacity, risk appetite, and investment goal — get back a suggested allocation across Fixed Deposit, Recurring Deposit, Bonds, Mutual Funds, and Equity, visualised as a pie chart with a plain-language explanation.

Built with Python, Streamlit, and Claude AI using the AI-DLC methodology.

---

## Quick Start

```bash
# 1. Clone / navigate to project
cd /home/labuser/investment-advisor-poc

# 2. Install dependencies
bash setup.sh

# 3. Set your API key
echo "ANTHROPIC_API_KEY=sk-ant-your-key-here" > .env

# 4. Run the app
source /home/labuser/venv/bin/activate
streamlit run frontend/app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Architecture

```
Streamlit UI → Orchestrator → [frontend-agent | backend-agent | triage-agent]
                            → [Rules Engine | RAG Engine | MCP Server]
                            → Observability (OTel + Prometheus)
```

See [docs/architecture.md](docs/architecture.md) for the full diagram.

---

## Project Structure

```
investment-advisor-poc/
├── .claude/            ← Agent definitions, rules, skills, hooks
├── config/             ← Allocation rules YAML + settings
├── core/               ← Pydantic models, rules engine, context manager
├── frontend/           ← Streamlit app + components
├── rag/                ← TF-IDF knowledge retrieval
├── mcp/                ← HTTP MCP server (port 8765)
├── observability/      ← JSON logger, Prometheus metrics, OTel traces
├── orchestrator/       ← Delegation hub — routes between all agents
├── tests/              ← Unit + integration tests (no API key needed)
├── load_tests/         ← Locust load test scripts
├── docs/               ← Architecture, AI-DLC tracker, demo script
└── reports/            ← Runtime output (gitignored)
```

---

## Running Tests

No API key required — all LLM calls are mocked.

```bash
cd /home/labuser/investment-advisor-poc
source /home/labuser/venv/bin/activate
python -m unittest discover tests/ -v
```

---

## MCP Server

Auto-starts on port 8765 when the Streamlit app launches.

```bash
# Health check
curl http://localhost:8765/health

# List tools
curl http://localhost:8765/tools

# Get a recommendation directly
curl -X POST http://localhost:8765/tools/get_recommendation \
  -H "Content-Type: application/json" \
  -d '{"age": 32, "monthly_income": 75000, "monthly_savings": 12000, "risk": "MEDIUM", "goal": "LONG"}'
```

---

## Prometheus Metrics

Available at [http://localhost:9090/metrics](http://localhost:9090/metrics) once the app is running.

Key metrics:
- `investment_requests_total` — requests by risk level and goal
- `investment_request_latency_seconds` — P50/P95 latency
- `investment_active_sessions` — concurrent users
- `investment_token_usage_total` — tokens per agent

---

## Skills (Claude Code Slash Commands)

| Command | Description |
|---------|-------------|
| `/review` | Run triage-agent on last session, write quality report to `reports/` |
| `/load-test` | Run 60s Locust load test against MCP server, report P95 latency |
| `/demo` | Guided Step 18 demo walkthrough |

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Yes | — | Your Anthropic API key |
| `MCP_PORT` | No | 8765 | MCP server port |
| `ENABLE_TRIAGE` | No | true | Run triage-agent after each session |
| `OTEL_LOG_FILE` | No | reports/otel_traces.jsonl | OTel trace output file |

---

## AI-DLC Progress

See [docs/aidlc_steps.md](docs/aidlc_steps.md) for the full 18-step tracker.

Steps 12, 17, and 18 are left for the user:
- **Step 12**: Run `/review` after a session to generate the first triage report
- **Step 17**: Tune agent prompts in `.claude/agents/` based on triage feedback
- **Step 18**: Run the demo using [docs/demo_script.md](docs/demo_script.md)
