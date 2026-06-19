import sys
import os

# Ensure project root is on the path when running via `streamlit run frontend/app.py`
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

from config.settings import config
from observability.metrics import start_metrics_server
from observability.telemetry import setup_telemetry

# Initialise observability once per process
if "observability_started" not in st.session_state:
    setup_telemetry(config.otel_service_name, config.otel_log_file)
    try:
        start_metrics_server(config.metrics_port)
    except OSError:
        pass  # already running (Streamlit reruns the script on each interaction)
    st.session_state["observability_started"] = True

# Start MCP server in background once per process
if "mcp_started" not in st.session_state:
    from mcp.server import start_mcp_server
    start_mcp_server(config.mcp_host, config.mcp_port, daemon=True)
    st.session_state["mcp_started"] = True

from orchestrator.orchestrator import InvestmentOrchestrator
from frontend.components.chart import render_pie_chart
from frontend.components.recommendation_card import render_recommendation
from frontend.components.user_form import render_form

st.set_page_config(page_title="Investment Advisor", page_icon="💰", layout="centered")
st.title("💰 Investment Advisor")
st.caption("Educational demo for banking customers — not real financial advice")

with st.sidebar:
    st.markdown("## 🔗 Quick Links")
    st.markdown("**App Pages**")
    st.markdown("💰 [Investment Advisor](http://localhost:8501)")
    st.divider()
    st.markdown("**External Endpoints**")
    st.markdown("🟢 [Prometheus Metrics](http://localhost:9090/metrics)")
    st.markdown("🟢 [MCP Health](http://localhost:8765/health)")
    st.markdown("🟢 [MCP Tools](http://localhost:8765/tools)")

# Cache orchestrator across reruns
if "orchestrator" not in st.session_state:
    st.session_state["orchestrator"] = InvestmentOrchestrator()

orchestrator: InvestmentOrchestrator = st.session_state["orchestrator"]

form_data = render_form()
if form_data:
    with st.spinner("Analysing your profile..."):
        try:
            response = orchestrator.process_advisory_request(form_data)
        except ValueError as e:
            st.error(f"Validation error: {e}")
            st.stop()
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            st.stop()

    render_pie_chart(response.allocation.model_dump())
    render_recommendation(response.explanation, response.disclaimer, response.allocation.model_dump())
