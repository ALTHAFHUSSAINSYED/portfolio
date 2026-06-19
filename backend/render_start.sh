#!/bin/bash

# This script is used by Render to start the application

# Install required packages
echo "Installing required packages..."
pip install bleach
pip install python-dotenv
pip install motor
pip install pymongo
pip install fastapi
pip install uvicorn
pip install sendgrid

# Set log level for better debugging
export LOG_LEVEL=INFO

# Set default values for missing environment variables
if [ -z "$DB_NAME" ]; then
    export DB_NAME="portfolio"
    echo "Setting default DB_NAME: portfolio"
fi

if [ -z "$PORT" ]; then
    export PORT="10000"
    echo "Setting default PORT: 10000"
fi

# Print environment configuration (without sensitive values)
echo "Starting server with the following configuration:"
echo "ENVIRONMENT: $ENVIRONMENT"
echo "DB_NAME: $DB_NAME"
echo "PORT: $PORT"

# Check essential environment variables
if [ -z "$MONGO_URL" ]; then
    echo "Warning: MONGO_URL is not set. Database features will be disabled."
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "Warning: GEMINI_API_KEY is not set. AI features will be disabled."
fi

if [ -z "$SERPER_API_KEY" ]; then
    echo "Warning: SERPER_API_KEY is not set. Web search will use DuckDuckGo fallback."
fi

if [ -z "$CLOUDINARY_CLOUD_NAME" ] || [ -z "$CLOUDINARY_API_KEY" ] || [ -z "$CLOUDINARY_API_SECRET" ]; then
    echo "Warning: Cloudinary credentials are incomplete. Image upload features may not work properly."
fi

# Make sure we are in the correct directory
cd /opt/render/project/src/backend || cd backend || echo "Warning: Cannot find backend directory"

# Check if server.py exists
if [ ! -f "server.py" ]; then
    echo "Error: server.py not found in the current directory"
    echo "Current directory: $(pwd)"
    echo "Directory contents: $(ls -la)"
    exit 1
fi

# Start the server with uvicorn instead of python directly
echo "Starting server with uvicorn..."
exec uvicorn server:app --host 0.0.0.0 --port $PORT
