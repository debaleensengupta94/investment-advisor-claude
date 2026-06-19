# Demo Script — Investment Advisor POC

> Use this script for the Step 18 first-user demonstration.
> Pause after each step for questions or reactions.

---

## Step 1 — Show project structure
```bash
find /home/labuser/investment-advisor-poc -type f | sort
```
**Say:** "This is the full project. Every file was generated following the masterplan — no manual coding. Notice the clean separation: core logic, frontend, agents, RAG, MCP, and observability all live in their own folders."

---

## Step 2 — Show CLAUDE.md
```bash
cat /home/labuser/investment-advisor-poc/CLAUDE.md
```
**Say:** "This is the onboarding document Claude reads when it opens the project. It explains the agent map, data flow, and how to run everything. Any new developer — human or AI — starts here."

---

## Step 3 — Show the sub-agent definitions
```bash
ls /home/labuser/investment-advisor-poc/.claude/agents/
cat /home/labuser/investment-advisor-poc/.claude/agents/frontend-agent.md
```
**Say:** "Each agent has a focused role defined in plain markdown with YAML frontmatter. The frontend-agent only validates and formats — it never makes investment decisions. The backend-agent only explains allocations it receives — it never computes them."

---

## Step 4 — Run the app
```bash
cd /home/labuser/investment-advisor-poc
source /home/labuser/venv/bin/activate
streamlit run frontend/app.py
```
**Say:** "Open your browser to localhost:8501. The app starts the MCP server and Prometheus metrics endpoint automatically in the background."

---

## Step 5 — Fill the form
Fill in:
- Age: 32
- Monthly Income: ₹75,000
- Monthly Savings: ₹12,000
- Risk Preference: Medium
- Investment Goal: Long-term (> 7 years)

**Say:** "A 32-year-old with medium risk tolerance and a long-term goal. Let's see what the system recommends."

---

## Step 6 — Click "Get My Investment Plan"
**Say:** "The form data goes to the frontend-agent for validation, then the rules engine computes a deterministic allocation from our YAML config, the RAG engine retrieves relevant education passages, and the backend-agent writes the explanation in plain language. Total round-trip: under 3 seconds."

Point out the pie chart. **Say:** "The allocation is visualised immediately. For this profile: heavy on Mutual Funds and Equity because of the long horizon, with some Fixed Deposit for stability."

---

## Step 7 — Point out the disclaimer
**Say:** "The disclaimer is permanently visible on every screen — this is an educational demo only, not real financial advice. It's also enforced at the agent level — every agent prompt ends with this disclaimer."

---

## Step 8 — Show structured logs
Open a terminal and run:
```bash
tail -f /home/labuser/investment-advisor-poc/reports/otel_traces.jsonl
```
**Say:** "Every request produces structured JSON traces via OpenTelemetry. In production you'd ship these to Grafana or SigNoz."

---

## Step 9 — Show MCP tool registry
```bash
curl http://localhost:8765/tools | python3 -m json.tool
```
**Say:** "The MCP server exposes the rules engine as an HTTP API. Any LLM — including Claude itself — can call `get_recommendation` or `get_knowledge` as a tool. This is how you make your domain logic composable."

---

## Step 10 — Show Prometheus metrics
```bash
curl http://localhost:9090/metrics | grep investment
```
**Say:** "We're tracking request counts by risk/goal, latency histograms, active sessions, and token usage per agent. Wire this to Grafana and you have a live dashboard."

---

## Step 11 — Run the test suite
```bash
cd /home/labuser/investment-advisor-poc
python -m unittest discover tests/ -v
```
**Say:** "All tests pass without an API key — the LLM calls are mocked. The rules engine tests verify all 9 risk×goal combinations, age modifiers, and edge cases."

---

## Step 12 — Show a triage report
```bash
ls /home/labuser/investment-advisor-poc/reports/triage_*.md 2>/dev/null && cat $(ls -t /home/labuser/investment-advisor-poc/reports/triage_*.md | head -1) || echo "Run /review after making a request to generate a triage report."
```
**Say:** "After each advisory session, the triage-agent asynchronously reviews the output for quality: allocation integrity, disclaimer presence, language simplicity, relevance, and hallucination checks. It scores 1–5 per dimension and flags HIGH severity issues."

---

## Step 13 — Explain next steps
**Say:**
- "Replace the YAML rules with a live database for product-specific rates."
- "Add authentication — each user gets their own profile and history."
- "Wire Grafana to the Prometheus endpoint for a real-time operations dashboard."
- "Extend the MCP server to connect to external APIs for live fund data."
- "The agent prompts in `.claude/agents/` are the only place to tune AI behaviour — no code changes needed for most prompt improvements."
