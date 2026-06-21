#!/bin/bash
set -e

DOMAIN="api.althafportfolio.site"
EMAIL="althafhussain.sd@gmail.com"
PORTFOLIO_DIR="/home/ec2-user/portfolio"

echo "🏁 Starting Deployment Pipeline..."

# 1. Idempotent Software Installation
if ! command -v docker &> /dev/null || ! command -v certbot &> /dev/null; then
  echo "📦 Installing Docker & Certbot..."
  sudo dnf update -y
  sudo dnf install docker certbot python3-certbot-nginx -y
  sudo systemctl enable docker
  sudo systemctl start docker
  sudo usermod -aG docker ec2-user
else
  echo "✅ Docker & Certbot are already installed."
fi

# 2. Setup Directories
echo "📁 Setting up host persistence directories..."
mkdir -p \
  "$PORTFOLIO_DIR/configs" \
  "$PORTFOLIO_DIR/logs/chatbot" \
  "$PORTFOLIO_DIR/logs/auto_blogger" \
  "$PORTFOLIO_DIR/nginx" \
  "$PORTFOLIO_DIR/uploads" \
  "$PORTFOLIO_DIR/backups"

# 3. Create Docker Network
sudo docker network inspect portfolio-net >/dev/null 2>&1 || sudo docker network create portfolio-net

# 4. Write env and config files (copied from GitHub Workspace to /tmp)
mv /tmp/nginx.conf "$PORTFOLIO_DIR/nginx/nginx.conf"
mv /tmp/.env.local "$PORTFOLIO_DIR/.env.local"

# 5. Idempotent SSL Certificate Setup
if [ ! -d "/etc/letsencrypt/live/$DOMAIN" ]; then
  echo "🔒 Requesting SSL Certificate via Certbot standalone..."
  sudo systemctl stop nginx || true
  sudo certbot certonly --standalone -d "$DOMAIN" --agree-tos --email "$EMAIL" --non-interactive
  
  echo "⏰ Configuring Certbot daily auto-renewal cronjob..."
  (sudo crontab -l 2>/dev/null | grep -F "certbot renew" || echo "0 0 * * * certbot renew --pre-hook \"sudo docker stop portfolio-nginx\" --post-hook \"sudo docker start portfolio-nginx\"") | sudo crontab -
else
  echo "✅ SSL Certificates already exist for $DOMAIN."
fi

# 6. Pull latest Backend Docker Image
echo "🐳 Pulling latest backend image..."
sudo docker pull kubealthaf/portfolio-backend:latest

# 7. Start/Recreate backend container
echo "🔄 Recreating backend container..."
sudo docker stop portfolio-backend 2>/dev/null || true
sudo docker rm portfolio-backend 2>/dev/null || true
sudo docker run -d \
  --name portfolio-backend \
  --network portfolio-net \
  --restart unless-stopped \
  --env-file "$PORTFOLIO_DIR/.env.local" \
  -v "$PORTFOLIO_DIR/configs:/app/backend/runtime_configs" \
  -v "$PORTFOLIO_DIR/logs:/app/backend/logs" \
  -v "$PORTFOLIO_DIR/uploads:/app/backend/uploads" \
  kubealthaf/portfolio-backend:latest

# 8. Start/Recreate Nginx proxy container
echo "🔄 Recreating Nginx proxy container..."
sudo docker stop portfolio-nginx 2>/dev/null || true
sudo docker rm portfolio-nginx 2>/dev/null || true
sudo docker run -d \
  --name portfolio-nginx \
  --network portfolio-net \
  -p 80:80 \
  -p 443:443 \
  --restart unless-stopped \
  -v "$PORTFOLIO_DIR/nginx/nginx.conf:/etc/nginx/nginx.conf:ro" \
  -v /etc/letsencrypt:/etc/letsencrypt:ro \
  nginx:alpine

# 9. Sync ChromaDB Vector Database
echo "📥 Syncing ChromaDB Vector Database..."
sudo docker exec portfolio-backend python3 populate_vector_db.py

echo "🎉 Deployment complete!"

