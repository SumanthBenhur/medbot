#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# Cleanup child processes on exit (Ctrl+C / SIGINT / SIGTERM)
cleanup() {
    echo ""
    echo "Shutting down Medbot services..."
    kill $(jobs -p) 2>/dev/null || true
    wait
    echo "All services stopped."
}
trap cleanup SIGINT SIGTERM EXIT

echo "=========================================="
echo "Starting Medbot Services"
echo "=========================================="

# 1. Start Mock Third-Party Booking API (Port 8001)
echo "Starting Mock Booking API on port 8001..."
uv run uvicorn third_party.main:app --port 8001 &

# 2. Start FastAPI LangGraph Backend (Port 8000)
echo "Starting FastAPI Backend on port 8000..."
uv run uvicorn backend.main:app --port 8000 &

# Wait a brief moment for backends to bind ports
sleep 2

# 3. Start Streamlit Frontend (Port 8501)
echo "Starting Streamlit Frontend on port 8501..."
echo "Open in browser: http://localhost:8501"
echo "=========================================="
uv run streamlit run frontend/app.py
