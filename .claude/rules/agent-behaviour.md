# Agent Behaviour Rules

- Every agent response must be valid JSON unless the agent is the triage-agent writing a report
- Agents do not share conversation history — each has its own ContextManager instance
- The orchestrator is the only component that may call sub-agents
- frontend-agent handles ONLY input validation and output formatting — no business logic
- backend-agent handles ONLY explanation generation — allocation numbers come from rules_engine.py
- triage-agent is read-only — it reviews, scores, and reports but never modifies outputs
