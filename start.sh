#!/bin/bash
set -e

echo "[STARTUP] Starting Database Sync..."
python3 /app/backend/populate_vector_db.py

echo "[STARTUP] Database Ready. Starting Server..."
exec uvicorn backend.server:app --host 0.0.0.0 --port 8000

