#!/bin/bash

# Define the log prefix
PREFIX="[Startup]"

echo "$PREFIX Booting Portfolio Backend Container..."

# 1. Startup Validation
echo "$PREFIX Running Startup Validations..."

# Environment variables are passed via docker --env-file, so we just check if they exist

if [ -z "$CHATBOT_NEW_KEY" ]; then
    echo "$PREFIX 🚨 ERROR: CHATBOT_NEW_KEY is missing in .env.local!"
    exit 1
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "$PREFIX 🚨 ERROR: GEMINI_API_KEY is missing in .env.local!"
    exit 1
fi

# 2. Print Version Metadata
if [ -f "version.json" ]; then
    echo "========================================"
    echo "Portfolio Backend"
    
    # Simple grep/awk to parse the flat JSON safely without installing jq
    VERSION=$(grep -o '"image_version": *"[^"]*"' version.json | grep -o '"[^"]*"$' | tr -d '"')
    COMMIT=$(grep -o '"git_commit": *"[^"]*"' version.json | grep -o '"[^"]*"$' | tr -d '"')
    BUILD=$(grep -o '"build_date": *"[^"]*"' version.json | grep -o '"[^"]*"$' | tr -d '"')
    
    echo "Version: $VERSION"
    echo "Commit: $COMMIT"
    echo "Built: $BUILD"
    echo "========================================"
else
    echo "========================================"
    echo "Portfolio Backend"
    echo "Version: Development Build"
    echo "========================================"
fi

# 3. DB Sync
echo "$PREFIX Synchronizing S3 to ChromaDB..."
python backend/sync_s3_to_chroma.py

# 4. Start Server
echo "$PREFIX Starting Uvicorn (FastAPI) in the foreground..."
exec uvicorn backend.server:app --host 0.0.0.0 --port 8000
