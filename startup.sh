#!/bin/bash

# Define the log prefix
PREFIX="[Startup]"

echo "$PREFIX Booting Portfolio Backend Container..."

# Print Version Metadata
if [ -f "version.json" ]; then
    echo "$PREFIX Version Information:"
    cat version.json
    echo ""
else
    echo "$PREFIX No version.json found (Development build)"
fi

echo "$PREFIX Synchronizing S3 to ChromaDB..."
python backend/sync_s3_to_chroma.py

echo "$PREFIX Starting Uvicorn (FastAPI) in the background..."
# We run Uvicorn on 127.0.0.1:8000. Nginx will proxy pass port 80/443 to this.
uvicorn backend.server:app --host 127.0.0.1 --port 8000 &

# Optional: You can add Certbot generation logic here later if needed
# if [ ! -d "/etc/letsencrypt/live/api.althafportfolio.site" ]; then
#     echo "$PREFIX Warning: No SSL certificates found."
# fi

echo "$PREFIX Starting Nginx..."
# Start Nginx in the foreground so the Docker container stays alive
nginx -g 'daemon off;'
