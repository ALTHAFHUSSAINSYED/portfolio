FROM python:3.12-slim

WORKDIR /app

# Install dependencies, Nginx, and Certbot
RUN apt-get update \
    && apt-get install -y build-essential curl nginx certbot python3-certbot-nginx \
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

# Copy Nginx configuration to standard location
# Note: Ensure backend/nginx.conf.ec2 is properly configured to proxy pass to 127.0.0.1:8000
RUN cp backend/nginx.conf.ec2 /etc/nginx/nginx.conf

# Expose HTTP and HTTPS ports
EXPOSE 80
EXPOSE 443

# Start the application using our custom startup script
CMD ["bash", "startup.sh"]
