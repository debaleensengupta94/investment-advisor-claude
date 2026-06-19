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
