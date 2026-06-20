# SOP: Deploying Backend to a New EC2 Instance (Step-by-Step)

This standard operating procedure (SOP) outlines the exact steps to deploy the portfolio backend on a fresh AWS EC2 instance, configure SSL certificates, run the Docker containers, and integrate with the frontend.

---

## Phase 1: AWS Infrastructure Setup

### 1. EC2 Instance Launch
1. Launch a new EC2 Instance using **Amazon Linux 2023** (AMI).
2. **Specs**: Minimum **2 vCPUs**, **2GB RAM** (e.g., `t3.medium` or higher), **30GB gp3 root volume**.
3. Allocate and associate an **Elastic IP (EIP)** to the instance so the public IP remains static.

### 2. Security Group Configuration (Crucial Security best practices)
In the EC2 Security Group, allow only the following inbound traffic:
- **SSH (Port 22)**: Restrict to your specific IP address/range.
- **HTTP (Port 80)**: Allow from anywhere (`0.0.0.0/0`) for Let's Encrypt validation and HTTP->HTTPS redirect.
- **HTTPS (Port 443)**: Allow from anywhere (`0.0.0.0/0`) for secure client API requests.

> [!WARNING]
> **Do NOT open Port 8000** to the internet. The backend container runs inside a private Docker bridge network (`portfolio-net`). Nginx handles all external requests on port 443 and proxies them to the backend internally. Keeping port 8000 closed prevents unauthorized bypasses of Nginx.

---

## Phase 2: DNS Configuration

1. Log into your domain registrar (e.g., Namecheap, GoDaddy).
2. Add a new **A Record** for your API subdomain:
   - **Type**: `A Record`
   - **Host**: `api` (resolves to `api.althafportfolio.site`)
   - **Value (IP)**: The Elastic IP of your EC2 instance.
   - **TTL**: `Automatic`

---

## Phase 3: Host Setup & Bootstrapping

### 1. Connect to EC2
```bash
ssh -i "portfolio.key.pem" ec2-user@<YOUR_EC2_IP>
```

### 2. Copy and Run the Bootstrap Script
The local file is located at [bootstrap.sh](file:///c:/portfolio/portfolio/bootstrap.sh) in the workspace.
Create the bootstrap script on the host at `/home/ec2-user/bootstrap.sh`:

```bash
nano /home/ec2-user/bootstrap.sh
```

Paste the following content into it:
```bash
#!/bin/bash
set -e

echo "🐳 Installing Docker & Certbot..."
sudo dnf update -y
sudo dnf install docker certbot python3-certbot-nginx -y
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker ec2-user

echo "🌐 Setting up Docker network..."
docker network inspect portfolio-net >/dev/null 2>&1 || docker network create portfolio-net

echo "📁 Creating host persistence directories..."
mkdir -p \
  /home/ec2-user/portfolio/configs \
  /home/ec2-user/portfolio/logs/chatbot \
  /home/ec2-user/portfolio/logs/auto_blogger \
  /home/ec2-user/portfolio/nginx \
  /home/ec2-user/portfolio/uploads \
  /home/ec2-user/portfolio/backups

echo "⚠️ Creating empty .env.local..."
touch /home/ec2-user/portfolio/.env.local

echo "🎉 Host bootstrapped successfully!"
```

Save the file, make it executable, and run it:
```bash
chmod +x /home/ec2-user/bootstrap.sh
/home/ec2-user/bootstrap.sh
```

### 3. Apply Group Permissions
Log out and log back in to apply the `docker` group membership:
```bash
exit
ssh -i "portfolio.key.pem" ec2-user@<YOUR_EC2_IP>
```

---

## Phase 4: Configure Environment Variables

Edit the environment file on the host:
```bash
nano /home/ec2-user/portfolio/.env.local
```

Paste and configure the following variables (replacing placeholders with actual values, keeping secrets secure):
```ini
MONGO_URL="mongodb+srv://<username>:<password>@cluster0.mongodb.net/portfolioDB"
CLOUDINARY_CLOUD_NAME="your_cloudinary_cloud_name"
CLOUDINARY_API_KEY="your_cloudinary_api_key"
CLOUDINARY_API_SECRET="your_cloudinary_api_secret"
GEMINI_API_KEY="your_gemini_api_key"
CHROMA_API_KEY="your_chroma_api_key"
CHROMA_TENANT_ID="your_chroma_tenant_id"
CHROMA_DB_NAME="Development"
BLOG_KEY="your_blog_generator_secret_key"
CHATBOT_NEW_KEY="your_chatbot_secret_key"
SERPER_API_KEY="your_serper_dev_api_key"
RESEND_KEY="your_resend_email_api_key"
EMAIL_ADDRESS="althafhussain.sd@gmail.com"

# S3 Bucket Credentials (to access blogs from the S3 bucket of the old AWS account)
AWS_ACCESS_KEY_ID="your_aws_access_key_id"
AWS_SECRET_ACCESS_KEY="your_aws_secret_access_key"
AWS_REGION="ap-south-1"
S3_BLOG_BUCKET="althaf-blogs-storage"
```

---

## Phase 5: SSL Certificate Generation & Renewal

Let's Encrypt requires port 80 to verify domain ownership. Run the following command to request standalone certificates:

```bash
sudo certbot certonly --standalone -d api.althafportfolio.site --agree-tos --email althafhussain.sd@gmail.com
```

### Configure Auto-Renewal
Setup a crontab on the host to check and auto-renew the certificates daily, then reload the Nginx container to load the new certs:
```bash
sudo crontab -e
```

Add the following line at the end of the file:
```cron
0 0 * * * certbot renew --post-hook "docker exec portfolio-nginx nginx -s reload"
```

---

## Phase 6: Configure Nginx

Create the Nginx configuration file on the host at `/home/ec2-user/portfolio/nginx/nginx.conf`:
```bash
nano /home/ec2-user/portfolio/nginx/nginx.conf
```

Paste the following configuration:
```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log notice;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # HTTP -> HTTPS Redirect
    server {
        listen 80;
        listen [::]:80;
        server_name api.althafportfolio.site;

        return 301 https://$host$request_uri;
    }

    # HTTPS Reverse Proxy
    server {
        listen 443 ssl;
        listen [::]:443 ssl;
        http2 on;

        server_name api.althafportfolio.site;

        ssl_certificate /etc/letsencrypt/live/api.althafportfolio.site/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/api.althafportfolio.site/privkey.pem;

        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_prefer_server_ciphers off;

        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 1d;
        ssl_session_tickets off;

        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;

        client_max_body_size 25M;

        location / {
            proxy_pass http://portfolio-backend:8000;
            proxy_http_version 1.1;

            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;
            proxy_set_header X-Forwarded-Host $host;
            proxy_set_header X-Forwarded-Port 443;

            proxy_connect_timeout 300;
            proxy_send_timeout 300;
            proxy_read_timeout 300;
            proxy_buffering off;
        }
    }
}
```

---

## Phase 7: Launch Docker Containers

Run the following commands on the EC2 host to pull the latest backend image and run the containers:

### 1. Pull the Backend Image
```bash
docker pull kubealthaf/portfolio-backend:latest
```

### 2. Run the Backend Container
```bash
docker run -d \
  --name portfolio-backend \
  --network portfolio-net \
  --restart unless-stopped \
  --env-file /home/ec2-user/portfolio/.env.local \
  -v /home/ec2-user/portfolio/configs:/app/backend/runtime_configs \
  -v /home/ec2-user/portfolio/logs:/app/backend/logs \
  -v /home/ec2-user/portfolio/uploads:/app/backend/uploads \
  kubealthaf/portfolio-backend:latest
```

### 3. Run the Nginx Proxy Container
```bash
docker run -d \
  --name portfolio-nginx \
  --network portfolio-net \
  -p 80:80 \
  -p 443:443 \
  --restart unless-stopped \
  -v /home/ec2-user/portfolio/nginx/nginx.conf:/etc/nginx/nginx.conf:ro \
  -v /etc/letsencrypt:/etc/letsencrypt:ro \
  nginx:alpine
```

### 4. Sync ChromaDB Vector Database
To sync all portfolio assets and blogs from the S3 bucket into the ChromaDB collection:
```bash
docker exec -it portfolio-backend python3 populate_vector_db.py
```

---

## Phase 8: Connect Frontend with Backend

To connect your frontend application to the new backend:
1. Open the frontend `.env` configuration file and set `REACT_APP_API_URL` to point to the secure subdomain:
   ```ini
   REACT_APP_API_URL=https://api.althafportfolio.site
   ```
2. Build/Deploy the frontend application (e.g., via AWS Amplify console or Vercel). The application will now route all API and chatbot requests to `https://api.althafportfolio.site`.

---

## Verification & Checks

### 1. Verify Container Status
Check that both containers are running:
```bash
docker ps
```

### 2. Verify Endpoint Connectivity
Test the API health endpoint from your local computer:
```bash
curl -i https://api.althafportfolio.site/health
```
*(Should return HTTP status `200 OK` and response body `{"status":"healthy"}`)*.
