#!/bin/bash
# Bootstrap script for a fresh EC2 instance

set -e

echo "🚀 Bootstrapping Althaf's Portfolio Server (Two-Container Architecture)..."

# 1. Install Docker and Certbot if not present
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker & Certbot..."
    sudo dnf update -y
    sudo dnf install docker certbot -y
    sudo systemctl enable docker
    sudo systemctl start docker
    sudo usermod -aG docker ec2-user
    echo "✅ Docker & Certbot installed and started."
else
    echo "✅ Docker already installed."
fi

# 2. Create the external persistent directories
echo "📁 Creating host persistence directories..."
mkdir -p /home/ec2-user/portfolio/configs
mkdir -p /home/ec2-user/portfolio/logs/chatbot
mkdir -p /home/ec2-user/portfolio/logs/auto_blogger
mkdir -p /home/ec2-user/portfolio/nginx

# 3. Create .env.local if it doesn't exist
if [ ! -f /home/ec2-user/portfolio/.env.local ]; then
    touch /home/ec2-user/portfolio/.env.local
    echo "⚠️ Created empty .env.local. Please edit this file to add your secrets."
fi

echo "✅ Directories initialized."

echo ""
echo "=========================================================="
echo "🎉 Server is Bootstrapped!"
echo "Next Steps:"
echo "1. Log out and log back in (to apply Docker group permissions)."
echo "2. Edit your environment variables:"
echo "   nano /home/ec2-user/portfolio/.env.local"
echo "3. Pull and run the backend container:"
echo "   docker pull kubealthaf/portfolio-backend:latest"
echo ""
echo "   docker run -d \\"
echo "   --name portfolio-backend \\"
echo "   --restart unless-stopped \\"
echo "   --env-file /home/ec2-user/portfolio/.env.local \\"
echo "   -v /home/ec2-user/portfolio/configs:/app/backend/runtime_configs \\"
echo "   -v /home/ec2-user/portfolio/logs:/app/backend/logs \\"
echo "   kubealthaf/portfolio-backend:latest"
echo ""
echo "4. Pull and run the Nginx container:"
echo "   docker run -d \\"
echo "   --name portfolio-nginx \\"
echo "   --link portfolio-backend:backend \\"
echo "   -p 80:80 \\"
echo "   -p 443:443 \\"
echo "   --restart unless-stopped \\"
echo "   -v /home/ec2-user/portfolio/nginx/nginx.conf:/etc/nginx/nginx.conf \\"
echo "   -v /etc/letsencrypt:/etc/letsencrypt \\"
echo "   nginx:alpine"
echo "=========================================================="

