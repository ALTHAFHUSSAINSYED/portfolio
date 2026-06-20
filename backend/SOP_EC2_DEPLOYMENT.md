# Standard Operating Procedure (SOP): EC2 Backend Deployment & Integration

This document outlines the step-by-step procedure to deploy the portfolio backend application on a new AWS EC2 instance, configure SSL certificates, connect the frontend, and manage security permissions for S3 bucket access.

---

## Architecture Overview

The system uses a **Two-Container Architecture** running on a Docker bridge network:
1. **`portfolio-backend`**: A Python container running the FastAPI/Uvicorn application on port `8000` (not exposed directly to the internet).
2. **`portfolio-nginx`**: An Nginx container exposing ports `80` and `443`, proxying HTTPS requests to the backend container, and automatically redirecting HTTP traffic to HTTPS.

```
       Internet (HTTPS)
              │
              ▼
   ┌──────────────────────┐
   │    Docker Host       │
   │  ┌────────────────┐  │
   │  │ portfolio-nginx│  │ (Port 80/443, SSL Termination)
   │  └───────┬────────┘  │
   │          │ (Docker bridge network: portfolio-net)
   │          ▼
   │  ┌────────────────┐  │
   │  │portfolio-backnd│  │ (Port 8000, Python FastAPI app)
   │  └────────────────┘  │
   └──────────────────────┘
```

---

## Phase 1: AWS Infrastructure Setup

### 1. EC2 Instance Launch
1. Launch a new EC2 Instance using **Amazon Linux 2023** (AMI).
2. Instance type: `t3.micro` or higher (depending on CPU/Memory usage).
3. **AWS Credentials**: S3 bucket credentials from the bucket's home account are configured directly via `.env.local` variables (see **Phase 5** below).

### 2. Security Group Configuration
In the EC2 Security Group, allow the following inbound traffic:
- **SSH (Port 22)**: Restrict to your IP range (or allow custom port if changed).
- **HTTP (Port 80)**: Allow from anywhere (`0.0.0.0/0`) for certificate verification and redirects.
- **HTTPS (Port 443)**: Allow from anywhere (`0.0.0.0/0`) for secure client access.

### 3. Elastic IP (EIP) Setup
1. Allocate an Elastic IP in the AWS VPC Console.
2. Associate the Elastic IP with your EC2 instance. This prevents the IP from changing when the instance is restarted.

---

## Phase 2: DNS Configuration

1. Log into your Domain Registrar (e.g., Namecheap, Route53, GoDaddy).
2. Go to the DNS Zone Editor for your domain (e.g., `althafportfolio.site`).
3. Add a new **A Record** for your API subdomain:
   - **Type**: `A Record`
   - **Host (Name)**: `api` (resolves to `api.althafportfolio.site`)
   - **Value (IP Address)**: The Elastic IP of your EC2 instance (e.g., `15.206.73.138`).
   - **TTL**: `Automatic` or `3600` seconds.

---

## Phase 3: Host Bootstrapping & Setup

### 1. SSH into the Server
Connect to your EC2 instance using your private key:
```bash
ssh -i "your-key.pem" ec2-user@<YOUR_EC2_IP>
```

### 2. Run the Bootstrap Script
Create and run the bootstrap script `bootstrap.sh`. This installs Docker, configures the network, sets up directories, and installs Certbot.

```bash
# Download or create the bootstrap.sh file on the host
chmod +x bootstrap.sh
./bootstrap.sh
```

*(Refer to the repository's `bootstrap.sh` template, which installs `docker`, `certbot`, and `python3-certbot-nginx` via `dnf`, creates directories in `/home/ec2-user/portfolio`, and creates the Docker network `portfolio-net`)*.

### 3. Log out and back in
Run `exit` and reconnect to apply Docker group permissions:
```bash
exit
ssh -i "your-key.pem" ec2-user@<YOUR_EC2_IP>
```

### 4. Create the Environment File
Edit `/home/ec2-user/portfolio/.env.local` to populate production credentials:
```bash
nano /home/ec2-user/portfolio/.env.local
```

Populate the required secrets:
```ini
MONGO_URL="mongodb+srv://..."
CLOUDINARY_CLOUD_NAME="..."
CLOUDINARY_API_KEY="..."
CLOUDINARY_API_SECRET="..."
GEMINI_API_KEY="..."
CHROMA_API_KEY="..."
CHROMA_TENANT_ID="..."
CHROMA_DB_NAME="Development"
BLOG_KEY="..."
CHATBOT_NEW_KEY="..."
SERPER_API_KEY="..."
RESEND_KEY="..."
EMAIL_ADDRESS="..."
S3_BLOG_BUCKET="althaf-blogs-storage"
AWS_ACCESS_KEY_ID="your_aws_access_key_id"
AWS_SECRET_ACCESS_KEY="your_aws_secret_access_key"
AWS_REGION="ap-south-1"
```

---

## Phase 4: SSL Certificate Generation (Let's Encrypt)

Certbot requires port 80 to be free to execute a standalone challenge to verify domain ownership.

1. **Verify DNS Propagation**: Ensure `api.yourdomain.com` points to the EC2 IP.
2. **Generate the Certificate**:
   ```bash
   sudo certbot certonly --standalone -d api.althafportfolio.site --agree-tos --email althafhussain.sd@gmail.com
   ```
3. This creates files in:
   - Certificate: `/etc/letsencrypt/live/api.althafportfolio.site/fullchain.pem`
   - Private Key: `/etc/letsencrypt/live/api.althafportfolio.site/privkey.pem`
4. **Auto-Renewal Setup**:
   Let's Encrypt certificates are valid for 90 days. Set up a system crontab on the host to auto-renew certificates:
   ```bash
   sudo crontab -e
   ```
   Add the following line to check and renew daily at midnight, then reload the Nginx container:
   ```cron
   0 0 * * * certbot renew --post-hook "docker exec portfolio-nginx nginx -s reload"
   ```

---

## Phase 5: S3 Bucket Access & Credentials Security

To fetch and publish blogs from/to the S3 bucket (`althaf-blogs-storage`), the backend utilizes `boto3`. 

### 1. Cross-Account S3 Access Solution
Since the target S3 bucket resides in a separate (old) AWS account and cross-account IAM role assumptions are restricted/failed, we use a **dedicated IAM User** created in the bucket's owner AWS account.

This user requires Programmatic Access keys which are injected into the Docker container via `.env.local` to allow `boto3` to communicate with the S3 bucket.

### 2. Credentials Configuration
Add the following keys to your `/home/ec2-user/portfolio/.env.local` file:
- `AWS_ACCESS_KEY_ID`: Access key ID of the IAM user from the bucket's AWS account.
- `AWS_SECRET_ACCESS_KEY`: Secret access key of the IAM user.
- `AWS_REGION`: Set to `ap-south-1` (the region hosting the S3 bucket).
- `S3_BLOG_BUCKET`: Set to the bucket name `althaf-blogs-storage`.

### 3. IAM User Minimal Policy Setup (Old S3 Account)
The IAM User in the bucket's owner account must have a policy attached with these minimal permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:GetBucketLocation"
            ],
            "Resource": "arn:aws:s3:::althaf-blogs-storage"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::althaf-blogs-storage/*"
        }
    ]
}
```

### 4. Docker Integration
Because the Docker run command uses the `--env-file` parameter pointing to `/home/ec2-user/portfolio/.env.local`, these environment variables are automatically loaded into the container runtime. `boto3` detects them automatically in the container environment and uses them to authenticate S3 API calls.


---

## Phase 6: Running the Containers

### 1. Configure Nginx Conf
Create `/home/ec2-user/portfolio/nginx/nginx.conf` on the EC2 host:
```bash
nano /home/ec2-user/portfolio/nginx/nginx.conf
```
Paste the configuration (substituting your custom domain name):
*(Ensure path references matching `/etc/letsencrypt/live/api.althafportfolio.site/...`)*.

### 2. Build and Run the Backend Container
Run the backend application on the `portfolio-net` network:
```bash
# Navigate to directory and build local image (or pull from repository)
cd /home/ec2-user/portfolio
docker pull kubealthaf/portfolio-backend:latest

# Run backend container
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

### 3. Run the Nginx Reverse Proxy Container
Run Nginx, mounting the configuration file and the Let's Encrypt certificates directory:
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

### 4. Initialize Database
For the first-time setup, load files into ChromaDB:
```bash
docker exec -it portfolio-backend python3 populate_vector_db.py
```

---

## Phase 7: Connecting Frontend to Backend

In order for the frontend application (React/Vite/Next.js) to communicate with your backend, it must call the HTTPS domain `https://api.althafportfolio.site`.

### 1. Frontend Configuration
Ensure environment files (like `.env` or `.env.production`) configure the base URL:
```ini
REACT_APP_API_URL=https://api.althafportfolio.site
```
If using custom environment fallbacks, make sure the production fallback is updated:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://api.althafportfolio.site';
```

### 2. Re-building the Frontend
After configuring the environment variables, rebuild your frontend deployment (e.g., triggering a build on AWS Amplify, Vercel, or Netlify) so the static files embed the new API URL.

---

## Verification & Troubleshooting

### Check Container Status
```bash
docker ps
```
Both `portfolio-nginx` and `portfolio-backend` should display status `Up`.

### Check Logs
- **Backend Logs**:
  ```bash
  docker logs portfolio-backend -f
  ```
- **Nginx Access/Error Logs**:
  ```bash
  docker logs portfolio-nginx -f
  ```

### Verify Endpoints
Test local accessibility (from the EC2 host):
```bash
curl -i http://localhost:8000/health
```
Test external HTTPS accessibility (from any machine):
```bash
curl -i https://api.althafportfolio.site/health
```
*(Should return `HTTP/1.1 200 OK` and `{"status":"healthy"}`)*.
