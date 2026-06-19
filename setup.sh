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
