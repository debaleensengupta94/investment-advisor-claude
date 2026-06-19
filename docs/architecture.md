# System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Observability                          │
│               OTel traces + Prometheus metrics               │
│                                                             │
│  ┌───────────┐    ┌────────────────────────────────────┐   │
│  │ Streamlit │───▶│           Orchestrator              │   │
│  │   (UI)    │    │                                     │   │
│  └───────────┘    │  ┌──────────────┐ ┌─────────────┐  │   │
│                   │  │ Frontend     │ │ Backend     │  │   │
│                   │  │ Agent        │ │ Agent       │  │   │
│  ┌───────────┐    │  │ (validate +  │ │ (explain)   │  │   │
│  │    MCP    │◀───│  │  format)     │ │             │  │   │
│  │  Server   │    │  └──────────────┘ └─────────────┘  │   │
│  │ :8765     │    │  ┌────────────────────────────────┐ │   │
│  └───────────┘    │  │    Triage Agent (async)         │ │   │
│                   │  │    writes to reports/           │ │   │
│  ┌───────────┐    │  └────────────────────────────────┘ │   │
│  │Prometheus │    │  ┌──────────────┐ ┌─────────────┐  │   │
│  │  :9090    │    │  │ Rules Engine │ │ RAG Engine  │  │   │
│  └───────────┘    │  │ (pure Python)│ │ (TF-IDF)    │  │   │
│                   │  └──────────────┘ └─────────────┘  │   │
│                   └────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

```
User fills form
    │
    ▼
frontend-agent  ──  validates input  ──▶  UserProfile (Pydantic)
    │
    ▼
rules_engine.compute_allocation()  [no LLM]  ──▶  Allocation
    │
    ▼
rag.retrieve()  [no LLM]  ──▶  list[str] (relevant passages)
    │
    ▼
backend-agent  ──  generates explanation  ──▶  {"explanation": "..."}
    │
    ▼
AdvisoryResponse  ──▶  Streamlit renders pie chart + text + disclaimer
    │
    ▼ (async)
triage-agent  ──  scores + writes  ──▶  reports/triage_YYYYMMDD_HHMMSS.md
```

## Component Responsibilities

| Component | Location | LLM? | Role |
|-----------|----------|------|------|
| frontend-agent | .claude/agents/frontend-agent.md | Yes (Haiku) | Validate input, format output |
| backend-agent | .claude/agents/backend-agent.md | Yes (Haiku) | Generate plain-language explanation |
| triage-agent | .claude/agents/triage-agent.md | Yes (Sonnet) | Quality audit, write report |
| orchestrator | orchestrator/orchestrator.py | No (SDK only) | Route between all components |
| rules_engine | core/rules_engine.py | No | Deterministic allocation from YAML |
| rag | rag/ | No | TF-IDF retrieval from knowledge base |
| mcp/server | mcp/server.py | No | HTTP API wrapping the rules engine |
| observability | observability/ | No | Traces, metrics, JSON logs |
