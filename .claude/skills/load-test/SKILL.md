---
name: load-test
description: Run a 60-second Locust load test against the MCP server and report P50/P95 latency and error rate
---

1. Verify the MCP server is running: curl http://localhost:8765/health
2. If not running, start it: python -m mcp.server &
3. Run: locust -f load_tests/locustfile.py --host=http://127.0.0.1:8765 --headless -u 10 -r 2 --run-time 60s
4. Print: total requests, P50 latency, P95 latency, error rate.
5. Flag if error rate > 1% or P95 > 2000ms.
