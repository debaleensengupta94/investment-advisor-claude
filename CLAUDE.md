# Investment Advisor POC

Beginner-friendly investment advisory AI agent for banking customers.
Educational demo only — no real financial advice.
Built with Python, Streamlit, and Claude AI (AI-DLC methodology).

## Quick Start
1. cp .env.example .env  → add your ANTHROPIC_API_KEY
2. bash setup.sh          → installs dependencies
3. streamlit run frontend/app.py

## Agent Map
| Agent          | File                              | Model                     | Role                                      |
|----------------|-----------------------------------|---------------------------|-------------------------------------------|
| frontend-agent | .claude/agents/frontend-agent.md  | claude-haiku-4-5-20251001 | Validates input, formats display output   |
| backend-agent  | .claude/agents/backend-agent.md   | claude-haiku-4-5-20251001 | Generates plain-language explanation      |
| triage-agent   | .claude/agents/triage-agent.md    | claude-sonnet-4-6         | Reviews output quality, writes report     |
| orchestrator   | orchestrator/orchestrator.py      | Python (SDK)              | Delegates between agents, fan-in results  |

## Data Flow
Streamlit form → frontend-agent (validate) → rules_engine (allocate)
→ rag engine (retrieve) → backend-agent (explain)
→ frontend-agent (format) → Streamlit (render chart + text)

## Rules
All agents must comply with .claude/rules/investment-domain.md

## MCP Server
Auto-starts on port 8765 when Streamlit launches.
Test: curl http://localhost:8765/health

## Skills (Slash Commands)
- /review     → triage agent reviews last session, writes report
- /load-test  → runs Locust against MCP server, prints P95 latency
- /demo       → guided walkthrough for Step 18

## Env Vars
ANTHROPIC_API_KEY  required
MCP_PORT           optional, default 8765
ENABLE_TRIAGE      optional, default true
