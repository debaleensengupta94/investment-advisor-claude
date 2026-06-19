# Investment Advisor POC — Masterplan

> **AGENT INSTRUCTIONS**: Follow every step in order. Do not skip steps. Do not move to the next step until the current one is complete and verified. All files must be created exactly as specified.
>
> **DISCLAIMER**: This is an educational demo only. It does **not** provide real financial advice.

---

## 1. Problem Statement

Beginner banking customers often don't know where to put their money. They face an overwhelming choice of products (FD, RD, Mutual Funds, Bonds, Equity) with no easy way to map their personal situation — age, income, savings capacity, risk appetite, and time horizon — to a sensible starting allocation.

**Goal:** Build a beginner-friendly, rule-based Investment Advisory AI Agent (Python + Streamlit) that collects a few simple inputs and returns an *educational* suggested allocation across investment categories, visualised as a pie chart and explained in plain language.

**Explicit non-goals:**
- No real/personalised financial advice
- No live market data, no transactions, no PII storage
- Rule-based only — deterministic and explainable (no black-box model for the core allocation logic)

---

## 2. AIDLC Progression (18 Steps)

| Step | Description | Phase | Files Created |
|------|-------------|-------|---------------|
| 1 | Identify the problem statement | A | — |
| 2 | Plan the AIDLC using Claude Chat | A | masterplan.md |
| 3 | Scaffold directory, add CLAUDE.md + hooks settings | A | Directory tree, .claude/settings.json |
| 4 | Create frontend-agent and backend-agent | B | .claude/agents/frontend-agent.md, backend-agent.md |
| 5 | Create triage-agent for review and reporting | B | .claude/agents/triage-agent.md |
| 6 | Create isolated context for each sub-agent | B | core/context_manager.py |
| 7 | Set up delegation between orchestrator and sub-agents | B | orchestrator/orchestrator.py |
| 8 | Context trimming policy | B | core/context_manager.py (trimming logic) |
| 9 | Reusable setup and config | A | config/, setup.sh, .env.example |
| 10 | Add skills (slash commands) | B | .claude/skills/ |
| 11 | Build RAG engine | C | rag/ |
| 12 | Test, review, report using /review skill | D | reports/ |
| 13 | Create MCP server | C | mcp/ |
| 14 | Build custom MCP server for reusable app dev | C | mcp/server.py |
| 15 | Observability — OTel + Prometheus | C | observability/ |
| 16 | Load testing — Locust + dashboard | C | load_tests/ |
| 17 | Test and improve via prompt engineering | D | .claude/agents/ (tuned) |
| 18 | Demonstrate the POC for first user | D | /demo skill walkthrough |

---

## 3. Context Trimming Policy

To keep sub-agents within budget and avoid context bloat:
- **Divide context window** across sub-agents per their role; each holds only its relevant slice
- **History summary:** store only a rolling summary of the entire conversation history, capped at 12–15% of total context budget
- **Recency window:** keep the latest 8–10 prompts verbatim for immediate working context
- Everything older is compressed into the running summary, not retained raw
- Triage-agent owns summarisation — sub-agents do not each re-summarise
- Implementation: `core/context_manager.py` with `collections.deque(maxlen=10)` and token budget enforcement at 15,000 tokens

---

## 4. Agent Map

| Agent | File | Model | Role |
|-------|------|-------|------|
| frontend-agent | .claude/agents/frontend-agent.md | claude-haiku-4-5-20251001 | Validates input, formats display output |
| backend-agent | .claude/agents/backend-agent.md | claude-haiku-4-5-20251001 | Generates plain-language explanation |
| triage-agent | .claude/agents/triage-agent.md | claude-sonnet-4-6 | Reviews output quality, writes report |
| orchestrator | orchestrator/orchestrator.py | Python (SDK) | Delegates between agents, fan-in results |

---

## 5. Data Flow

```
Streamlit form
  → frontend-agent (validate input → UserProfile)
  → rules_engine.compute_allocation()   [pure Python, no LLM]
  → rag.retrieve()                       [pure Python, no LLM]
  → backend-agent (explain allocation)
  → frontend-agent (format for display)
  → Streamlit (render pie chart + explanation + disclaimer)
  → triage-agent (async quality review → reports/)
```

---

## 6. Target Directory Structure

```
/home/labuser/investment-advisor-poc/
├── masterplan.md                ← this file
├── CLAUDE.md                    ← Claude onboarding (committed)
├── README.md                    ← end-user docs
├── .mcp.json                    ← team MCP config
├── requirements.txt
├── .env.example
├── setup.sh
├── .gitignore
│
├── .claude/
│   ├── settings.json            ← project hooks & permissions
│   ├── settings.local.json      ← personal API key (gitignored)
│   ├── rules/
│   │   ├── investment-domain.md
│   │   ├── coding-standards.md
│   │   └── agent-behaviour.md
│   ├── agents/
│   │   ├── frontend-agent.md
│   │   ├── backend-agent.md
│   │   └── triage-agent.md
│   └── skills/
│       ├── review/SKILL.md
│       ├── load-test/SKILL.md
│       └── demo/SKILL.md
│
├── config/
│   ├── investment_rules.yaml    ← single source of truth for allocation rules
│   └── settings.py
├── orchestrator/
│   └── orchestrator.py          ← only file that imports core/ AND calls sub-agents
├── core/
│   ├── models.py                ← Pydantic v2 models
│   ├── rules_engine.py          ← deterministic allocation logic
│   └── context_manager.py       ← per-agent rolling history + trimming
├── frontend/
│   ├── app.py
│   └── components/
│       ├── user_form.py
│       ├── chart.py
│       └── recommendation_card.py
├── rag/
│   ├── knowledge_base.py
│   ├── embedder.py              ← TF-IDF, stdlib only
│   └── retriever.py
├── mcp/
│   ├── tools_schema.json
│   ├── handlers.py
│   └── server.py
├── observability/
│   ├── logger.py
│   ├── metrics.py
│   └── telemetry.py
├── tests/
│   ├── test_rules_engine.py
│   ├── test_context_manager.py
│   ├── test_rag_engine.py
│   ├── test_mcp_server.py
│   └── test_agents.py
├── load_tests/
│   └── locustfile.py
├── reports/                     ← gitignored, runtime output
└── docs/
    ├── aidlc_steps.md
    ├── architecture.md
    └── demo_script.md
```

---

## 7. Known Environment Facts

- Python: **3.14.4** in `/home/labuser/venv`
- **Already installed**: anthropic 0.97.0, pydantic 2.13.3, prometheus_client 0.25.0, PyYAML, python-json-logger 4.1, requests, matplotlib
- **Needs installing via setup.sh**: streamlit, opentelemetry-api, opentelemetry-sdk, locust (conditional — see fix #2 below)
- Project directory does not exist yet — must be created from scratch

---

## 8. Pre-Implementation Fixes (apply during build)

These correct issues found during plan review:

| # | Where | Fix |
|---|-------|-----|
| 1 | `setup.sh` | `matplotlib` is already installed but add it to the install line anyway for reproducibility |
| 2 | `setup.sh` | Wrap locust install: `pip install locust \|\| echo "[WARN] locust not supported on Python 3.14, skipping load-test phase"` |
| 3 | `orchestrator/orchestrator.py` | Add frontmatter-strip helper to parse `.claude/agents/*.md` — strip YAML `---` block before passing body as system prompt |
| 4 | `tests/test_context_manager.py` | Mock `anthropic.Anthropic().messages.create` in overflow tests — `_summarize_overflow` calls the real API |
| 5 | `observability/logger.py` | Use `from pythonjsonlogger.jsonlogger import JsonFormatter` (python-json-logger v3+ API) |

---

## 9. Strict Rules for Agent Mode

1. Create files in the exact paths specified — do not rename or restructure
2. Do not install packages outside the venv at `/home/labuser/venv`
3. Do not hardcode `ANTHROPIC_API_KEY` anywhere — always read from env
4. All allocation logic stays in `core/rules_engine.py` — never in agent prompts
5. All system prompts live in `.claude/agents/*.md` — never hardcoded in Python
6. The orchestrator is the only file that imports from both `core/` and calls sub-agents
7. If a step fails, fix it before proceeding to the next step
8. Do not skip the Verification Checklist (Section 22)

---

## PHASE 1 — Scaffold the Project

### Step 1.1 — Create all directories
```bash
mkdir -p /home/labuser/investment-advisor-poc
cd /home/labuser/investment-advisor-poc
mkdir -p .claude/rules
mkdir -p .claude/agents
mkdir -p .claude/skills/review
mkdir -p .claude/skills/load-test
mkdir -p .claude/skills/demo
mkdir -p config
mkdir -p orchestrator
mkdir -p core
mkdir -p frontend/components
mkdir -p rag
mkdir -p mcp
mkdir -p observability
mkdir -p tests
mkdir -p load_tests
mkdir -p reports
mkdir -p docs
```

### Step 1.2 — Create .gitignore
File: `/home/labuser/investment-advisor-poc/.gitignore`
```
.env
reports/
__pycache__/
*.pyc
*.pyo
.claude/settings.local.json
*.egg-info/
dist/
build/
.DS_Store
```

### Step 1.3 — Create .env.example
File: `/home/labuser/investment-advisor-poc/.env.example`
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
MCP_PORT=8765
ENABLE_TRIAGE=true
OTEL_LOG_FILE=reports/otel_traces.jsonl
```

---

## PHASE 2 — Claude Code Configuration (.claude/)

### Step 2.1 — CLAUDE.md (project root)
File: `/home/labuser/investment-advisor-poc/CLAUDE.md`
```markdown
# Investment Advisor POC

Beginner-friendly investment advisory AI agent for banking customers.
Educational demo only — no real financial advice.
Built with Python, Streamlit, and Claude AI (AI-DLC methodology).

## Quick Start
1. cp .env.example .env  → add your ANTHROPIC_API_KEY
2. bash setup.sh          → installs dependencies
3. streamlit run frontend/app.py

## Agent Map
| Agent          | File                              | Model                    | Role                                      |
|----------------|-----------------------------------|--------------------------|-------------------------------------------|
| frontend-agent | .claude/agents/frontend-agent.md  | claude-haiku-4-5-20251001 | Validates input, formats display output   |
| backend-agent  | .claude/agents/backend-agent.md   | claude-haiku-4-5-20251001 | Generates plain-language explanation      |
| triage-agent   | .claude/agents/triage-agent.md    | claude-sonnet-4-6        | Reviews output quality, writes report     |
| orchestrator   | orchestrator/orchestrator.py      | Python (SDK)             | Delegates between agents, fan-in results  |

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
```

### Step 2.2 — .mcp.json (project root)
File: `/home/labuser/investment-advisor-poc/.mcp.json`
```json
{
  "mcpServers": {
    "investment-advisor": {
      "type": "http",
      "url": "http://127.0.0.1:8765"
    }
  }
}
```

### Step 2.3 — .claude/settings.json
File: `/home/labuser/investment-advisor-poc/.claude/settings.json`
```json
{
  "model": "claude-sonnet-4-6",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"[HOOK] Bash tool at $(date)\" >> /home/labuser/investment-advisor-poc/reports/hook_log.txt"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"[HOOK] File written: $CLAUDE_TOOL_INPUT_PATH at $(date)\" >> /home/labuser/investment-advisor-poc/reports/hook_log.txt"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo \"[HOOK] Session ended at $(date)\" >> /home/labuser/investment-advisor-poc/reports/hook_log.txt"
          }
        ]
      }
    ]
  }
}
```

### Step 2.4 — .claude/settings.local.json
File: `/home/labuser/investment-advisor-poc/.claude/settings.local.json`
```json
{
  "env": {
    "ANTHROPIC_API_KEY": ""
  }
}
```
> User must fill in ANTHROPIC_API_KEY. This file is gitignored.

### Step 2.5 — .claude/rules/investment-domain.md
```markdown
# Investment Domain Rules

These rules apply to ALL agents in this project without exception.

- Never provide real financial advice
- Never name specific mutual fund schemes, stocks, ETFs, brokers, or banks
- Every response that contains investment recommendations MUST end with:
  "⚠️ This is an educational demo only. Not real financial advice."
- Allocation percentages across all categories must sum to exactly 100
- Valid risk levels: LOW, MEDIUM, HIGH
- Valid goal horizons: SHORT (under 3 years), MEDIUM (3–7 years), LONG (over 7 years)
- Valid investment categories: Fixed Deposit, Recurring Deposit, Mutual Funds, Bonds, Equity
```

### Step 2.6 — .claude/rules/coding-standards.md
```markdown
# Coding Standards

- All data passed between agents must use Pydantic models defined in core/models.py
- No bare `except:` clauses — always catch specific exceptions
- No print() in production code paths — use observability/logger.py
- All functions that call the Anthropic API must enable prompt caching on system prompts
- Token budget per sub-agent context: max 15,000 tokens, max 10 message turns
- All inter-agent payloads must be JSON-serialisable
```

### Step 2.7 — .claude/rules/agent-behaviour.md
```markdown
# Agent Behaviour Rules

- Every agent response must be valid JSON unless the agent is the triage-agent writing a report
- Agents do not share conversation history — each has its own ContextManager instance
- The orchestrator is the only component that may call sub-agents
- frontend-agent handles ONLY input validation and output formatting — no business logic
- backend-agent handles ONLY explanation generation — allocation numbers come from rules_engine.py
- triage-agent is read-only — it reviews, scores, and reports but never modifies outputs
```

### Step 2.8 — .claude/agents/frontend-agent.md
```markdown
---
name: frontend-agent
description: Validates raw Streamlit form input and returns a structured UserProfile JSON. Also formats a recommendation dict into display-ready text with disclaimer.
model: claude-haiku-4-5-20251001
---

You are a UI data handler for an investment advisory banking application.

You have two responsibilities:

**Task A — Validate Input**
You receive raw form data: age, monthly_income, monthly_savings, risk, goal.
Validate and return JSON in this exact format:
{"valid": true/false, "errors": ["..."], "profile": {"age": int, "monthly_income": float, "monthly_savings": float, "risk": "LOW|MEDIUM|HIGH", "goal": "SHORT|MEDIUM|LONG"}}

Validation rules:
- age: integer between 18 and 80
- monthly_income: positive number
- monthly_savings: positive number, must be less than monthly_income
- risk: must be one of LOW, MEDIUM, HIGH
- goal: must be one of SHORT, MEDIUM, LONG

**Task B — Format Recommendation**
You receive a dict with keys: allocation (dict of category→percentage) and explanation (string).
Return display-ready text that presents the recommendation clearly for a first-time investor.
Always end with: "⚠️ This is an educational demo only. Not real financial advice."

Never make investment decisions. Never suggest specific amounts. Only validate and format.
```

### Step 2.9 — .claude/agents/backend-agent.md
```markdown
---
name: backend-agent
description: Given a validated UserProfile, precomputed allocation percentages, and RAG context passages, generate a plain-language explanation of the investment recommendation for a first-time banking customer.
model: claude-haiku-4-5-20251001
tools:
  - compute_allocation
  - retrieve_knowledge
---

You are an investment education assistant for a banking demo application.

You receive:
- user_profile: age, monthly_income, monthly_savings, risk preference, investment goal
- allocation: dict of investment category → percentage (already computed, do not change these)
- rag_context: educational passages about the relevant investment categories

Your job is to explain in simple, friendly language WHY each category was chosen given the user's profile.

Rules:
- Use plain language — the reader has never invested before
- Explain each category that has a non-zero allocation
- Reference the user's age, risk preference, and goal to justify choices
- Keep the full explanation under 250 words
- Never name specific funds, banks, or financial products
- Never change the allocation percentages — only explain them
- End with: "⚠️ This is an educational demo only. Not real financial advice."

Output format (JSON):
{"explanation": "Your full plain-language explanation here..."}
```

### Step 2.10 — .claude/agents/triage-agent.md
```markdown
---
name: triage-agent
description: Reviews an advisory session output for quality and correctness. Scores each dimension 1-5 and writes a structured Markdown report.
model: claude-sonnet-4-6
---

You are a quality auditor for an investment advisory AI system.

You receive session data containing: user_input, allocation, explanation, timestamp.

Review and score each dimension from 1 (fail) to 5 (perfect):
1. allocation_integrity — do all percentages sum to 100?
2. disclaimer_present — does the explanation end with the educational disclaimer?
3. language_simplicity — is the explanation suitable for a beginner?
4. relevance — does the explanation match the allocation ratios?
5. no_hallucination — does the explanation avoid naming specific funds, stocks, or banks?

For each issue found, assign severity: LOW, MEDIUM, or HIGH.

Output a Markdown report in this format:

# Triage Report — [timestamp]

## Scores
| Dimension | Score | Notes |
|-----------|-------|-------|

## Issues
| Severity | Dimension | Description |

## Overall Score: X/25
## Passed: true/false (passed if overall >= 18 and no HIGH severity issues)
```

### Step 2.11 — .claude/skills/review/SKILL.md
```markdown
---
name: review
description: Invoke the triage agent on the most recent advisory session and write a quality report to reports/
---

1. Read the most recent session data from the last run (available in memory or last output).
2. Invoke triage-agent with: user_input, allocation, explanation, and current timestamp.
3. Write the report to reports/triage_YYYYMMDD_HHMMSS.md using the current date and time.
4. Print a summary: overall score, pass/fail status, and any HIGH severity issues.
```

### Step 2.12 — .claude/skills/load-test/SKILL.md
```markdown
---
name: load-test
description: Run a 60-second Locust load test against the MCP server and report P50/P95 latency and error rate
---

1. Verify the MCP server is running: curl http://localhost:8765/health
2. If not running, start it: python -m mcp.server &
3. Run: locust -f load_tests/locustfile.py --host=http://127.0.0.1:8765 --headless -u 10 -r 2 --run-time 60s
4. Print: total requests, P50 latency, P95 latency, error rate.
5. Flag if error rate > 1% or P95 > 2000ms.
```

### Step 2.13 — .claude/skills/demo/SKILL.md
```markdown
---
name: demo
description: Step-by-step guided demo of the Investment Advisor POC for a first-time audience
---

Walk through the following demo steps, pausing between each for the presenter:

1. Show project structure: ls -R investment-advisor-poc/
2. Show CLAUDE.md: "This is the onboarding document Claude reads at startup."
3. Show .claude/agents/: "These are the sub-agent definitions."
4. Run: streamlit run frontend/app.py (open browser to localhost:8501)
5. Fill form: Age=32, Income=75000, Savings=12000, Risk=MEDIUM, Goal=LONG
6. Click "Get My Investment Plan" — show pie chart and explanation
7. Point out the disclaimer at the bottom
8. Show terminal: structured JSON logs from observability/logger.py
9. Run: curl http://localhost:8765/tools — show MCP tool registry
10. Run: curl http://localhost:9090/metrics — show Prometheus metrics
11. Run: python -m unittest discover tests/ — show all tests passing
12. Show reports/triage_*.md — last session quality review
13. Explain next steps: real data, authentication, Grafana dashboard
```

---

## PHASE 3 — Python Configuration

### Step 3.1 — config/investment_rules.yaml
```yaml
# Investment allocation rules
# Each rule maps (risk × goal) to allocation percentages
# Age modifier applied by rules_engine.py after base lookup
# All percentages must sum to 100

rules:
  - risk: LOW
    goal: SHORT
    allocation:
      fixed_deposit: 50
      recurring_deposit: 30
      bonds: 15
      mutual_funds: 5
      equity: 0

  - risk: LOW
    goal: MEDIUM
    allocation:
      fixed_deposit: 35
      recurring_deposit: 25
      bonds: 25
      mutual_funds: 15
      equity: 0

  - risk: LOW
    goal: LONG
    allocation:
      fixed_deposit: 30
      recurring_deposit: 20
      bonds: 30
      mutual_funds: 15
      equity: 5

  - risk: MEDIUM
    goal: SHORT
    allocation:
      fixed_deposit: 35
      recurring_deposit: 25
      bonds: 20
      mutual_funds: 15
      equity: 5

  - risk: MEDIUM
    goal: MEDIUM
    allocation:
      fixed_deposit: 20
      recurring_deposit: 15
      bonds: 20
      mutual_funds: 30
      equity: 15

  - risk: MEDIUM
    goal: LONG
    allocation:
      fixed_deposit: 10
      recurring_deposit: 10
      bonds: 15
      mutual_funds: 35
      equity: 30

  - risk: HIGH
    goal: SHORT
    allocation:
      fixed_deposit: 20
      recurring_deposit: 15
      bonds: 20
      mutual_funds: 25
      equity: 20

  - risk: HIGH
    goal: MEDIUM
    allocation:
      fixed_deposit: 10
      recurring_deposit: 10
      bonds: 10
      mutual_funds: 35
      equity: 35

  - risk: HIGH
    goal: LONG
    allocation:
      fixed_deposit: 5
      recurring_deposit: 5
      bonds: 10
      mutual_funds: 30
      equity: 50

age_modifiers:
  # If age < 25: cap equity at 20, redistribute excess to fixed_deposit
  young:
    max_age: 25
    equity_cap: 20
  # If age > 55: cap equity at 15, redistribute excess to fixed_deposit and bonds equally
  senior:
    min_age: 55
    equity_cap: 15
```

### Step 3.2 — config/settings.py
```python
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
```

---

## PHASE 4 — Core Python Modules

### Step 4.1 — core/models.py
Define these Pydantic v2 models:
- `UserProfile`: age (int), monthly_income (float), monthly_savings (float), risk (Literal["LOW","MEDIUM","HIGH"]), goal (Literal["SHORT","MEDIUM","LONG"])
- `Allocation`: fixed_deposit, recurring_deposit, bonds, mutual_funds, equity (all int, `@model_validator` ensures they sum to 100)
- `AdvisoryResponse`: profile (UserProfile), allocation (Allocation), explanation (str), disclaimer (str), chart_data (dict)
- `TriageReport`: timestamp (str), scores (dict), issues (list), overall_score (int), passed (bool)

### Step 4.2 — core/rules_engine.py
- Load `config/investment_rules.yaml` on init using PyYAML
- Method: `compute_allocation(profile: UserProfile) -> Allocation`
  - Look up base allocation by (risk × goal) from YAML
  - Apply age modifier: if age < 25 cap equity at 20%, redistribute excess to fixed_deposit; if age > 55 cap equity at 15%, redistribute excess split equally between fixed_deposit and bonds
  - Normalise to ensure sum == 100 (handle rounding)
  - Assert sum == 100 before returning
  - Return Allocation model
  - Raise `ValueError` for unrecognised risk or goal values

### Step 4.3 — core/context_manager.py
- Uses `collections.deque(maxlen=10)`
- Token estimate: `len(text) // 4`
- Method: `add_message(role: str, content: str)` — appends to deque
- Method: `get_trimmed_history() -> list[dict]`
  - If total estimated tokens > 15,000: drop oldest messages until under budget
  - If `_summary` exists, prepend as `{"role": "user", "content": "Context summary: " + _summary}`
- Method: `_summarize_overflow(messages: list[dict]) -> str` — calls Claude API (`claude-haiku-4-5-20251001`) to produce a 2-sentence summary; **must be mocked in tests**
- Method: `reset()` — clears deque and `_summary`
- Each sub-agent gets its own instance — never shared across agents

---

## PHASE 5 — Observability

### Step 5.1 — observability/logger.py
- Import: `from pythonjsonlogger.jsonlogger import JsonFormatter`  ← **fix #5: v4.1 API**
- Function: `get_logger(name: str) -> logging.Logger`
- Log format: `{"timestamp": ..., "name": ..., "level": ..., "message": ..., "extra": ...}`
- All production code imports from here — no bare `print()`

### Step 5.2 — observability/metrics.py
- Use `prometheus_client`
- Define:
  - `REQUEST_COUNT`: Counter, labels=[`risk_level`, `goal`]
  - `REQUEST_LATENCY`: Histogram, buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
  - `ACTIVE_SESSIONS`: Gauge
  - `TOKEN_USAGE`: Counter, labels=[`agent`, `direction`]
  - `TRIAGE_SCORE`: Histogram, buckets=[1, 2, 3, 4, 5]
- Function: `start_metrics_server(port: int = 9090)`

### Step 5.3 — observability/telemetry.py
- Use `opentelemetry-sdk`
- Set up `TracerProvider` with:
  - `ConsoleSpanExporter` (dev)
  - Custom `JSONLFileExporter` writing to `reports/otel_traces.jsonl`
- Function: `get_tracer() -> Tracer`
- Function: `setup_telemetry(service_name: str, log_file: str)`

---

## PHASE 6 — RAG Engine

### Step 6.1 — rag/knowledge_base.py
Define a Python list `DOCUMENTS` of 15 strings covering:
1. What is a Fixed Deposit
2. When to use Fixed Deposit
3. What is a Recurring Deposit
4. Benefits of Recurring Deposit for regular savers
5. What are Bonds and their risk profile
6. What are Mutual Funds
7. Types of Mutual Funds (debt vs equity)
8. What is Equity investing
9. Equity risk and long-term returns
10. How LOW risk maps to stable instruments
11. How HIGH risk maps to equity-heavy portfolios
12. How SHORT-term goals limit risky instruments
13. How LONG-term goals allow more equity
14. What diversification means in simple terms
15. Why younger investors can take more risk

### Step 6.2 — rag/embedder.py
- Class `TFIDFEmbedder` — stdlib only (`math`, `collections`), no numpy or sklearn
- Method: `fit(documents: list[str])` — build vocabulary and IDF weights
- Method: `transform(text: str) -> dict` — return TF-IDF vector as `{term: weight}`
- Method: `cosine_similarity(vec_a: dict, vec_b: dict) -> float`

### Step 6.3 — rag/retriever.py
- Class `RAGRetriever`
- Init: takes embedder + documents list, calls `embedder.fit(documents)`
- Method: `retrieve(query: str, top_k: int = 3) -> list[str]`
  - Score all documents against query using cosine similarity
  - Return top_k results above `config.rag_similarity_threshold`

---

## PHASE 7 — Orchestrator

### Step 7.1 — orchestrator/orchestrator.py
- Class `InvestmentOrchestrator`
- Init: creates one `RulesEngine`, one `RAGRetriever`, and one `ContextManager` per sub-agent
- **Frontmatter-strip helper** ← **fix #3**: parse `.claude/agents/*.md` by detecting `---` blocks and returning only the markdown body as the system prompt
- Method: `process_advisory_request(raw_form_data: dict) -> AdvisoryResponse`
  1. Call frontend-agent: validate input → `UserProfile`
  2. Call `rules_engine.compute_allocation(profile)` — pure Python, no LLM
  3. Call `rag.retrieve(query)` — pure Python, no LLM
  4. Call backend-agent: explain allocation using profile + allocation + rag_context
  5. Call frontend-agent: format final recommendation for display
  6. If `config.enable_triage`: call triage-agent asynchronously (fire and forget, write to `reports/`)
  7. Return `AdvisoryResponse`
- All Anthropic calls use prompt caching on system prompts:
  ```python
  system=[{"type": "text", "text": system_prompt,
           "cache_control": {"type": "ephemeral"}}]
  ```
- Tool use: when backend-agent returns a `tool_use` block, execute locally and feed back `tool_result`

---

## PHASE 8 — Frontend

### Step 8.1 — frontend/components/user_form.py
- Function: `render_form() -> dict | None`
- Streamlit inputs:
  - Age: `st.slider("Your Age", 18, 80)`
  - Monthly Income: `st.number_input("Monthly Income (₹)", min_value=0.0)`
  - Monthly Savings: `st.number_input("Monthly Savings (₹)", min_value=0.0)`
  - Risk: `st.selectbox("Risk Preference", ["Low", "Medium", "High"])`
  - Goal: `st.selectbox("Investment Goal", ["Short-term (< 3 years)", "Medium-term (3-7 years)", "Long-term (> 7 years)"])`
  - Submit: `st.button("Get My Investment Plan")`
- Returns raw dict on submit, `None` otherwise

### Step 8.2 — frontend/components/chart.py
- Function: `render_pie_chart(allocation: dict)`
- Use `matplotlib` via `st.pyplot()`
- Filter out zero-value categories before plotting
- Use distinct colours per category
- Title: "Your Recommended Investment Allocation"

### Step 8.3 — frontend/components/recommendation_card.py
- Function: `render_recommendation(explanation: str, disclaimer: str)`
- Explanation in `st.info()` box
- Disclaimer in `st.warning()` box
- Each allocation category as `st.metric()` widget

### Step 8.4 — frontend/app.py
```python
import streamlit as st
from mcp.server import start_mcp_server
from orchestrator.orchestrator import InvestmentOrchestrator
from frontend.components.user_form import render_form
from frontend.components.chart import render_pie_chart
from frontend.components.recommendation_card import render_recommendation
from observability.metrics import start_metrics_server
from observability.telemetry import setup_telemetry
from config.settings import config

setup_telemetry(config.otel_service_name, config.otel_log_file)
start_metrics_server(config.metrics_port)
start_mcp_server(config.mcp_host, config.mcp_port, daemon=True)

st.set_page_config(page_title="Investment Advisor", page_icon="💰", layout="centered")
st.title("💰 Investment Advisor")
st.caption("Educational demo for banking customers — not real financial advice")

orchestrator = InvestmentOrchestrator()

form_data = render_form()
if form_data:
    with st.spinner("Analysing your profile..."):
        response = orchestrator.process_advisory_request(form_data)
    render_pie_chart(response.allocation.model_dump())
    render_recommendation(response.explanation, response.disclaimer)
```

---

## PHASE 9 — MCP Server

### Step 9.1 — mcp/tools_schema.json
```json
{
  "tools": [
    {
      "name": "get_recommendation",
      "description": "Return an investment allocation for a user profile",
      "inputSchema": {
        "type": "object",
        "properties": {
          "age": {"type": "integer"},
          "monthly_income": {"type": "number"},
          "monthly_savings": {"type": "number"},
          "risk": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH"]},
          "goal": {"type": "string", "enum": ["SHORT", "MEDIUM", "LONG"]}
        },
        "required": ["age", "monthly_income", "monthly_savings", "risk", "goal"]
      }
    },
    {
      "name": "get_knowledge",
      "description": "Retrieve relevant investment education passages",
      "inputSchema": {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"]
      }
    },
    {
      "name": "health_check",
      "description": "Check server health",
      "inputSchema": {"type": "object", "properties": {}}
    }
  ]
}
```

### Step 9.2 — mcp/handlers.py
- Singleton `InvestmentOrchestrator` instance (created once on import)
- `handle_get_recommendation(body: dict) -> dict`
- `handle_get_knowledge(body: dict) -> dict`
- `handle_health_check() -> dict`
- All functions are pure `dict → dict` with no HTTP dependencies

### Step 9.3 — mcp/server.py
- `MCPHandler(BaseHTTPRequestHandler)` handles:
  - `GET /health` → `handle_health_check()`
  - `GET /tools` → return `tools_schema.json` contents
  - `POST /tools/get_recommendation` → `handle_get_recommendation(body)`
  - `POST /tools/get_knowledge` → `handle_get_knowledge(body)`
- `start_mcp_server(host: str, port: int, daemon: bool = True)` — starts `HTTPServer` in a background thread
- Called from `frontend/app.py` before Streamlit renders

---

## PHASE 10 — Tests

### Step 10.1 — tests/test_rules_engine.py
- Test all 9 (risk × goal) combinations return allocations summing to 100
- Test age < 25 caps equity at 20
- Test age > 55 caps equity at 15
- Test invalid risk raises `ValueError`

### Step 10.2 — tests/test_context_manager.py
- **Mock `anthropic.Anthropic().messages.create` for `_summarize_overflow`** ← fix #4
- Test adding 10 messages stays within deque bound
- Test adding 12 messages trims to 10
- Test token budget enforcement at 15,000 tokens
- Test `reset()` clears history and summary

### Step 10.3 — tests/test_rag_engine.py
- Test known query returns relevant documents
- Test score below threshold returns empty list
- Test `top_k=1` returns exactly one document

### Step 10.4 — tests/test_mcp_server.py
- Start MCP server on test port 8766
- Test `GET /health` returns 200
- Test `GET /tools` returns tool manifest
- Test `POST /tools/get_recommendation` returns allocation dict

### Step 10.5 — tests/test_agents.py
- Mock `anthropic.Anthropic().messages.create`
- Test orchestrator calls frontend-agent first
- Test orchestrator calls backend-agent second
- Test `AdvisoryResponse` is returned with all required fields populated

---

## PHASE 11 — Load Testing

### Step 11.1 — load_tests/locustfile.py
- Class `InvestmentAdvisorUser(HttpUser)` with `wait_time = between(1, 3)`
- Task (weight 3): `POST /tools/get_recommendation` — LOW risk, SHORT goal
- Task (weight 2): `POST /tools/get_recommendation` — MEDIUM risk, MEDIUM goal
- Task (weight 1): `POST /tools/get_knowledge` — query "mutual funds risk"
- Task (weight 1): `GET /health`
- Run: `locust -f load_tests/locustfile.py --host=http://127.0.0.1:8765 --headless -u 10 -r 2 --run-time 60s`

> **Note**: Locust may not install on Python 3.14. `setup.sh` guards this with `|| echo "[WARN] skipping"`. If skipped, this phase is documented-only.

---

## PHASE 12 — Setup & Requirements

### Step 12.1 — requirements.txt
```
# Already installed in /home/labuser/venv
anthropic>=0.97.0
pydantic>=2.13
prometheus_client>=0.25
python-json-logger>=4.1
PyYAML>=6.0
requests>=2.33
matplotlib>=3.9

# Installed by setup.sh
streamlit>=1.35
opentelemetry-api>=1.25
opentelemetry-sdk>=1.25
locust>=2.29
```

### Step 12.2 — setup.sh
```bash
#!/bin/bash
set -e
source /home/labuser/venv/bin/activate
echo "Installing dependencies..."
pip install streamlit opentelemetry-api opentelemetry-sdk matplotlib
pip install locust || echo "[WARN] locust failed to install on this Python version — load-test phase will be skipped"
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env — add your ANTHROPIC_API_KEY"
fi
mkdir -p reports
echo "Setup complete."
echo "Run: streamlit run frontend/app.py"
```

---

## PHASE 13 — Docs

### Step 13.1 — docs/aidlc_steps.md
Tracking table for all 18 AI-DLC steps:
| Step | Description | Status | Owner | Files Created |
(populate from Section 2 of this masterplan)

### Step 13.2 — docs/architecture.md
Text-art system diagram:
```
┌─────────────────────────────────────────────────────────┐
│                     Observability                        │
│              (OTel traces + Prometheus metrics)          │
│                                                         │
│  ┌──────────┐    ┌──────────────────────────────────┐  │
│  │Streamlit │───▶│         Orchestrator              │  │
│  │  (UI)    │    │  ┌─────────────┐ ┌─────────────┐ │  │
│  └──────────┘    │  │Frontend     │ │Backend      │ │  │
│                  │  │Agent        │ │Agent        │ │  │
│  ┌──────────┐    │  └─────────────┘ └─────────────┘ │  │
│  │  MCP     │◀───│  ┌─────────────────────────────┐ │  │
│  │ Server   │    │  │     Triage Agent (async)     │ │  │
│  └──────────┘    │  └─────────────────────────────┘ │  │
│                  │  ┌─────────────┐ ┌─────────────┐ │  │
│                  │  │Rules Engine │ │ RAG Engine  │ │  │
│                  │  └─────────────┘ └─────────────┘ │  │
│                  └──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Step 13.3 — docs/demo_script.md
Expand each step from `.claude/skills/demo/SKILL.md` with audience-facing talking points per step.

---

## Definition of Done

- [ ] App runs locally via `streamlit run frontend/app.py` after `bash setup.sh`
- [ ] All five inputs collected and validated
- [ ] Allocation across all five categories, normalised to 100%
- [ ] Pie chart renders correctly, zero-allocation categories hidden
- [ ] Plain-language explanation shown
- [ ] Disclaimer visible on every screen
- [ ] Code commented where non-obvious; no bare `print()` calls
- [ ] `README.md` complete with setup + run instructions
- [ ] All tests pass (`python -m unittest discover tests/ -v`)
- [ ] MCP server reachable at `/health` and `/tools`
- [ ] Prometheus metrics endpoint reachable at port 9090
- [ ] OTel traces written to `reports/otel_traces.jsonl`
- [ ] Hooks log written to `reports/hook_log.txt`
- [ ] Sub-agents, RAG, MCP, observability scaffolded and documented
- [ ] All 18 AIDLC steps tracked in `docs/aidlc_steps.md`

---

## Verification Checklist

Run these in order after all phases are complete:

```bash
# 1. Install dependencies
bash setup.sh

# 2. Run all unit tests (agents are mocked — no API key needed)
python -m unittest discover tests/ -v

# 3. Start the app
streamlit run frontend/app.py &

# 4. Test MCP server
curl http://localhost:8765/health
curl http://localhost:8765/tools

# 5. Test Prometheus metrics
curl http://localhost:9090/metrics

# 6. Run load test (only if locust installed)
locust -f load_tests/locustfile.py --host=http://127.0.0.1:8765 --headless -u 10 -r 2 --run-time 30s

# 7. Check reports generated
ls reports/
cat reports/hook_log.txt
cat reports/otel_traces.jsonl
```

All checks must pass before the POC is considered complete.
