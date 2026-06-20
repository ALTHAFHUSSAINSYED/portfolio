#!/bin/bash

# Define the log prefix
PREFIX="[Startup]"

echo "$PREFIX Booting Portfolio Backend Container..."

# 1. Startup Validation
echo "$PREFIX Running Startup Validations..."

if [ ! -f "/app/.env.local" ]; then
    echo "$PREFIX 🚨 ERROR: /app/.env.local is missing! Please mount it."
    exit 1
fi

# Source env vars to check them
set -a
source /app/.env.local
set +a

if [ -z "$OPENROUTER_KEY" ]; then
    echo "$PREFIX 🚨 ERROR: OPENROUTER_KEY is missing in .env.local!"
    exit 1
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "$PREFIX 🚨 ERROR: GEMINI_API_KEY is missing in .env.local!"
    exit 1
fi

# 2. Print Version Metadata
if [ -f "version.json" ]; then
    echo "$PREFIX Version Information:"
    cat version.json
    echo ""
else
    echo "$PREFIX No version.json found (Development build)"
fi

# 3. DB Sync
echo "$PREFIX Synchronizing S3 to ChromaDB..."
python backend/sync_s3_to_chroma.py

# 4. Start Server
echo "$PREFIX Starting Uvicorn (FastAPI) in the foreground..."
exec uvicorn backend.server:app --host 0.0.0.0 --port 8000
