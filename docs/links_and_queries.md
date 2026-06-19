# Investment Advisor POC — Links & Queries Reference

---

## App Links

| Service | URL | Notes |
|---------|-----|-------|
| 💰 Investment Advisor | http://localhost:8501 | Main Streamlit app |
| 📊 Observability Dashboard | http://localhost:8501/2_%F0%9F%93%8A_Observability | Charts, traces, hook log |

---

## Monitoring Links

| Service | URL | Credentials |
|---------|-----|-------------|
| 📈 Grafana Dashboard | http://localhost:3000/d/efplhh69efj0gc/investment-advisor-poc | admin / admin123 |
| 🏠 Grafana Home | http://localhost:3000 | admin / admin123 |
| 🔥 Prometheus UI | http://localhost:9091 | No login |
| 📋 Prometheus Raw Metrics | http://localhost:9090/metrics | No login |

---

## API Links

| Service | URL | Method |
|---------|-----|--------|
| 🟢 MCP Health | http://localhost:8765/health | GET |
| 🔧 MCP Tools Registry | http://localhost:8765/tools | GET |
| 📦 Get Recommendation | http://localhost:8765/tools/get_recommendation | POST |
| 📚 Get Knowledge | http://localhost:8765/tools/get_knowledge | POST |

### MCP Example Requests

```bash
# Health check
curl http://localhost:8765/health

# List all tools
curl http://localhost:8765/tools

# Get investment recommendation
curl -X POST http://localhost:8765/tools/get_recommendation \
  -H "Content-Type: application/json" \
  -d '{
    "age": 32,
    "monthly_income": 75000,
    "monthly_savings": 12000,
    "risk": "MEDIUM",
    "goal": "LONG"
  }'

# Get knowledge passages
curl -X POST http://localhost:8765/tools/get_knowledge \
  -H "Content-Type: application/json" \
  -d '{"query": "mutual funds risk long term"}'
```

---

## Prometheus Queries

Open **http://localhost:9091**, paste any query into the expression bar, and click **Execute**.

### Request Metrics

| What you want to see | Query |
|---|---|
| Total requests ever | `sum(investment_requests_total)` |
| Requests broken down by risk level | `sum by (risk_level) (investment_requests_total)` |
| Requests broken down by goal | `sum by (goal) (investment_requests_total)` |
| Request rate per minute | `sum(rate(investment_requests_total[1m])) * 60` |
| Active sessions right now | `investment_active_sessions` |

### Latency Metrics

| What you want to see | Query |
|---|---|
| P50 latency (median) | `histogram_quantile(0.50, rate(investment_request_latency_seconds_bucket[5m]))` |
| P95 latency | `histogram_quantile(0.95, rate(investment_request_latency_seconds_bucket[5m]))` |
| P99 latency | `histogram_quantile(0.99, rate(investment_request_latency_seconds_bucket[5m]))` |
| Average latency | `rate(investment_request_latency_seconds_sum[5m]) / rate(investment_request_latency_seconds_count[5m])` |

### Token Usage Metrics

| What you want to see | Query |
|---|---|
| Total tokens used (all agents) | `sum(investment_token_usage_total)` |
| Tokens per agent | `sum by (agent) (investment_token_usage_total)` |
| Input vs output tokens | `sum by (direction) (investment_token_usage_total)` |
| Tokens per agent per direction | `sum by (agent, direction) (investment_token_usage_total)` |
| Token rate per minute | `sum(rate(investment_token_usage_total[1m])) * 60` |

### Triage Quality Metrics

| What you want to see | Query |
|---|---|
| Total triage sessions scored | `investment_triage_score_count` |
| Average triage score | `investment_triage_score_sum / investment_triage_score_count` |
| P50 triage score | `histogram_quantile(0.50, investment_triage_score_bucket)` |

---

## Prometheus UI Tips

1. **Table vs Graph** — after executing a query, switch between the **Table** tab (current values) and **Graph** tab (over time)
2. **Find all app metrics** — in the metrics dropdown, type `investment_` to filter to this app only
3. **Check scrape health** — go to **Status → Targets** to confirm `investment-advisor` shows state **UP**
4. **Scrape interval** — configured to every **5 seconds** in `observability/prometheus.yml`

---

## Grafana Dashboard

The Grafana dashboard at http://localhost:3000/d/efplhh69efj0gc/investment-advisor-poc has 9 pre-built panels:

| Panel | Type | Query |
|-------|------|-------|
| Total Advisory Requests | Stat | `sum(investment_requests_total)` |
| Active Sessions | Stat | `investment_active_sessions` |
| Total Input Tokens | Stat | `sum(investment_token_usage_total{direction="input"})` |
| Total Output Tokens | Stat | `sum(investment_token_usage_total{direction="output"})` |
| Requests by Risk Level | Bar chart | `sum by (risk_level) (investment_requests_total)` |
| Requests by Goal | Bar chart | `sum by (goal) (investment_requests_total)` |
| Request Latency P50/P95 | Time series | `histogram_quantile(0.95/0.50, ...)` |
| Token Usage by Agent | Bar chart | `sum by (agent) (investment_token_usage_total)` |
| Request Rate per Minute | Time series | `sum(rate(investment_requests_total[1m])) * 60` |

Auto-refreshes every **5 seconds**.

---

## GitHub

| | URL |
|---|---|
| 🐙 Repository | https://github.com/debaleensengupta94/investment-advisor-claude |

---

## Load Testing

```bash
# Run 60-second load test (10 users, ramp 2/s)
cd /home/labuser/investment-advisor-poc
source /home/labuser/venv/bin/activate
locust -f load_tests/locustfile.py --host=http://127.0.0.1:8765 --headless -u 10 -r 2 --run-time 60s

# Save results to CSV
locust -f load_tests/locustfile.py --host=http://127.0.0.1:8765 --headless -u 10 -r 2 --run-time 60s --csv=reports/locust_results
```

### Last Run Results (2026-06-19)

| Metric | Value | SLA Target | Status |
|--------|-------|------------|--------|
| Total requests | 288 | — | — |
| Failures | 0 | < 1% | ✅ Pass |
| Throughput | 4.88 req/s | > 5 req/s | ⚠️ Just under (think-time limited) |
| P50 latency | 3 ms | < 500 ms | ✅ Pass |
| P95 latency | 7 ms | < 2,000 ms | ✅ Pass |
| P99 latency | 18 ms | — | ✅ |
| Max latency | 37 ms | — | ✅ |

---

## Running Everything from Scratch

```bash
cd /home/labuser/investment-advisor-poc
source /home/labuser/venv/bin/activate

# 1. Start Prometheus server
nohup prometheus_server \
  --config.file=observability/prometheus.yml \
  --web.listen-address=":9091" \
  --storage.tsdb.path=/tmp/prometheus-data \
  > /tmp/prometheus.log 2>&1 &

# 2. Start Grafana
sudo systemctl start grafana-server

# 3. Start the app (also starts MCP :8765 and metrics :9090 automatically)
streamlit run frontend/app.py
```
