import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
import time
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import streamlit as st

st.set_page_config(page_title="Observability", page_icon="📊", layout="wide")
st.title("📊 Observability Dashboard")
st.caption("Live metrics, traces, and hook logs from the Investment Advisor POC")

with st.sidebar:
    st.markdown("## 🔗 Quick Links")
    st.markdown("**App Pages**")
    st.markdown("💰 [Investment Advisor](http://localhost:8501)")
    st.divider()
    st.markdown("**External Endpoints**")
    st.markdown("🟢 [Prometheus Metrics](http://localhost:9090/metrics)")
    st.markdown("🟢 [MCP Health](http://localhost:8765/health)")
    st.markdown("🟢 [MCP Tools](http://localhost:8765/tools)")

auto_refresh = st.toggle("Auto-refresh every 5s", value=False)
if st.button("🔄 Refresh Now") or auto_refresh:
    st.rerun() if auto_refresh else None

# ── Prometheus metrics ────────────────────────────────────────────────────────

def _parse_prometheus(text: str) -> dict:
    """Parse flat Prometheus text into {metric_name: [(labels, value), ...]}."""
    result: dict = {}
    for line in text.splitlines():
        if line.startswith("#") or not line.strip():
            continue
        try:
            lhs, val = line.rsplit(" ", 1)
            val = float(val)
        except ValueError:
            continue
        if "{" in lhs:
            name, rest = lhs.split("{", 1)
            labels_str = rest.rstrip("}")
            labels = {}
            for pair in labels_str.split(","):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    labels[k.strip()] = v.strip('"')
        else:
            name = lhs
            labels = {}
        result.setdefault(name, []).append((labels, val))
    return result


def _fetch_metrics() -> dict:
    try:
        import urllib.request
        with urllib.request.urlopen("http://localhost:9090/metrics", timeout=2) as r:
            return _parse_prometheus(r.read().decode())
    except Exception:
        return {}


metrics = _fetch_metrics()

st.subheader("🔢 Live Counters")

col1, col2, col3, col4 = st.columns(4)

total_requests = sum(
    v for _, v in metrics.get("investment_requests_total", [])
)
active_sessions = next(
    (v for _, v in metrics.get("investment_active_sessions", [])), 0.0
)
total_tokens_in = sum(
    v for lbl, v in metrics.get("investment_token_usage_total", [])
    if lbl.get("direction") == "input"
)
total_tokens_out = sum(
    v for lbl, v in metrics.get("investment_token_usage_total", [])
    if lbl.get("direction") == "output"
)

col1.metric("Total Requests", int(total_requests))
col2.metric("Active Sessions", int(active_sessions))
col3.metric("Input Tokens", int(total_tokens_in))
col4.metric("Output Tokens", int(total_tokens_out))

# ── Request breakdown by risk × goal ─────────────────────────────────────────

st.subheader("📈 Requests by Risk Level & Goal")

request_data = metrics.get("investment_requests_total", [])
if request_data:
    risk_goal_counts: dict = {}
    for labels, val in request_data:
        key = f"{labels.get('risk_level','?')} / {labels.get('goal','?')}"
        risk_goal_counts[key] = risk_goal_counts.get(key, 0) + val

    fig, ax = plt.subplots(figsize=(8, 3))
    keys = list(risk_goal_counts.keys())
    vals = list(risk_goal_counts.values())
    colours = plt.cm.Set2.colors[:len(keys)]
    bars = ax.barh(keys, vals, color=colours)
    ax.bar_label(bars, fmt="%g", padding=3)
    ax.set_xlabel("Request count")
    ax.set_title("Requests per Risk × Goal combination")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
else:
    st.info("No requests recorded yet — make an advisory request from the main page first.")

# ── Latency histogram ─────────────────────────────────────────────────────────

st.subheader("⏱ Request Latency Histogram")

latency_buckets = [
    (lbl, v) for lbl, v in metrics.get("investment_request_latency_seconds_bucket", [])
    if lbl.get("le") != "+Inf"
]
if latency_buckets and any(v > 0 for _, v in latency_buckets):
    bucket_labels = [lbl["le"] + "s" for lbl, _ in latency_buckets]
    bucket_vals = [v for _, v in latency_buckets]
    # Convert cumulative to per-band counts
    band_vals = [bucket_vals[0]] + [
        max(0, bucket_vals[i] - bucket_vals[i - 1]) for i in range(1, len(bucket_vals))
    ]
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.bar(bucket_labels, band_vals, color="#4C72B0")
    ax.set_xlabel("Latency bucket (upper bound)")
    ax.set_ylabel("Request count")
    ax.set_title("Request latency distribution")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
else:
    st.info("No latency data yet — latency is recorded per advisory request.")

# ── Token usage by agent ──────────────────────────────────────────────────────

st.subheader("🪙 Token Usage by Agent")

token_data = metrics.get("investment_token_usage_total", [])
if token_data and any(v > 0 for _, v in token_data):
    agents: dict = {}
    for labels, val in token_data:
        agent = labels.get("agent", "unknown")
        direction = labels.get("direction", "?")
        agents.setdefault(agent, {"input": 0, "output": 0})
        agents[agent][direction] = agents[agent].get(direction, 0) + val

    agent_names = list(agents.keys())
    input_vals = [agents[a]["input"] for a in agent_names]
    output_vals = [agents[a]["output"] for a in agent_names]
    x = range(len(agent_names))

    fig, ax = plt.subplots(figsize=(8, 3))
    width = 0.35
    ax.bar([i - width / 2 for i in x], input_vals, width, label="Input tokens", color="#55A868")
    ax.bar([i + width / 2 for i in x], output_vals, width, label="Output tokens", color="#C44E52")
    ax.set_xticks(list(x))
    ax.set_xticklabels(agent_names, rotation=15, ha="right")
    ax.set_ylabel("Tokens")
    ax.set_title("Token usage per agent")
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
else:
    st.info("No token data yet — tokens are tracked per advisory request.")

# ── Triage scores ─────────────────────────────────────────────────────────────

st.subheader("🔍 Triage Quality Scores")

triage_buckets = [
    (lbl, v) for lbl, v in metrics.get("investment_triage_score_bucket", [])
    if lbl.get("le") != "+Inf"
]
if triage_buckets and any(v > 0 for _, v in triage_buckets):
    labels_t = [f"≤{lbl['le']}" for lbl, _ in triage_buckets]
    vals_t = [v for _, v in triage_buckets]
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(labels_t, vals_t, color="#8172B2")
    ax.set_xlabel("Score bucket")
    ax.set_ylabel("Count")
    ax.set_title("Triage score distribution (1=fail, 5=perfect)")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
else:
    st.info("No triage scores yet — run /review after an advisory request.")

# ── OTel traces ───────────────────────────────────────────────────────────────

st.subheader("🔭 OpenTelemetry Traces")

traces_file = Path("reports/otel_traces.jsonl")
if traces_file.exists() and traces_file.stat().st_size > 0:
    traces = []
    for line in traces_file.read_text().splitlines():
        try:
            traces.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    st.caption(f"Showing last 10 of {len(traces)} spans")
    for t in reversed(traces[-10:]):
        with st.expander(f"**{t.get('name','span')}** — {t.get('status','?')}"):
            st.json(t)
else:
    st.info("No trace data yet — traces are written after advisory requests.")

# ── Hook log ─────────────────────────────────────────────────────────────────

st.subheader("🪝 Hook Log")

hook_log = Path("reports/hook_log.txt")
if hook_log.exists() and hook_log.stat().st_size > 0:
    lines = hook_log.read_text().splitlines()
    st.text_area("Last 20 hook events", "\n".join(lines[-20:]), height=200)
else:
    st.info("No hook events yet.")

# ── Auto-refresh loop ─────────────────────────────────────────────────────────

if auto_refresh:
    time.sleep(5)
    st.rerun()
