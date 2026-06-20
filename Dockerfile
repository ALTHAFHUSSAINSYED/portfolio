FROM python:3.12-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update \
    && apt-get install -y build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Copy python requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y build-essential \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /root/.cache/pip /tmp/*

# Create necessary directories for runtime configs and logs
RUN mkdir -p /app/backend/logs /app/backend/runtime_configs

# Copy the entire project
COPY . .

# Expose HTTP port for Uvicorn
EXPOSE 8000

# Add Health Check (Assuming your FastAPI app has a /health endpoint, if not, it will check the root)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start the application using our custom startup script
CMD ["bash", "startup.sh"]
