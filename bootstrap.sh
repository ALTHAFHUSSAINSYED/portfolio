#!/bin/bash
# Bootstrap script for a fresh EC2 instance

set -e

echo "🚀 Bootstrapping Althaf's Portfolio Backend Server..."

# 1. Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    sudo dnf update -y
    sudo dnf install docker -y
    sudo systemctl enable docker
    sudo systemctl start docker
    sudo usermod -aG docker ec2-user
    echo "✅ Docker installed and started."
else
    echo "✅ Docker already installed."
fi

# 2. Create the external persistent directories
echo "📁 Creating host persistence directories..."
mkdir -p /home/ec2-user/portfolio/configs
mkdir -p /home/ec2-user/portfolio/logs/chatbot
mkdir -p /home/ec2-user/portfolio/logs/auto_blogger
mkdir -p /home/ec2-user/portfolio/certbot
mkdir -p /home/ec2-user/portfolio/ssl

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
echo "3. Pull and run the immutable container:"
echo "   docker pull althafhussainsyed/portfolio-backend:latest"
echo ""
echo "   docker run -d \\"
echo "   --name portfolio-backend \\"
echo "   -p 80:80 \\"
echo "   -p 443:443 \\"
echo "   -p 8000:8000 \\"
echo "   --restart unless-stopped \\"
echo "   --env-file /home/ec2-user/portfolio/.env.local \\"
echo "   -v /home/ec2-user/portfolio/configs:/app/backend/runtime_configs \\"
echo "   -v /home/ec2-user/portfolio/logs:/app/backend/logs \\"
echo "   -v /home/ec2-user/portfolio/certbot:/etc/letsencrypt \\"
echo "   -v /home/ec2-user/portfolio/ssl:/app/ssl \\"
echo "   althafhussainsyed/portfolio-backend:latest"
echo "=========================================================="
