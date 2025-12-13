# AWS Migration Plan: Free Tier Strategy (EC2 + Amplify)

## Executive Summary
**Goal:** Migrate to AWS using **Free Tier** resources to avoid monthly bills while solving the memory issue.
**Strategy:** "Lift and Shift" to **Amazon EC2** (Backend) and **AWS Amplify** (Frontend).
**Budget:** $0/month (utilizing AWS Free Tier). The $150 credit acts as a safety buffer.
**Memory Upgrade:** Moves from Render's 512MB to EC2's **1GB RAM** (t2.micro/t3.micro), doubling capacity.

---

## Architecture Changes

| Component | Current (Render) | New (AWS Free Tier) | Cost |
|-----------|------------------|---------------------|------|
| **Backend** | Render Web Service | **EC2 Instance** (t2.micro or t3.micro) | Free (750 hrs/mo for 12 mos) |
| **Frontend** | Render Static Site | **AWS Amplify** | Free (1000 build mins/mo) |
| **Database** | MongoDB Atlas | **MongoDB Atlas** | Free (Shared Cluster) |
| **Vector DB** | ChromaDB Cloud | **ChromaDB Cloud** | Free Tier |

---

## Phase 1: Containerization (Local Preparation)

We will use Docker to package the backend. This ensures it runs exactly the same on the EC2 server as it does locally.

**Action:** Create `backend/Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Phase 2: Frontend Migration (AWS Amplify)

*Do this first as it's the easiest part.*

1.  **Go to AWS Amplify Console.**
2.  Select **"Host my web app"** (Get started).
3.  **Connect Repository:** Select GitHub and choose your portfolio repo.
4.  **Build Settings:** Amplify usually auto-detects React. Ensure `baseDirectory` is `build`.
5.  **Deploy:** Click "Save and Deploy".
6.  **Result:** You get a `https://...amplifyapp.com` URL.

---

## Phase 3: Backend Migration (EC2 Setup)

### 1. Launch Instance
1.  Go to **EC2 Dashboard** -> **Launch Instance**.
2.  **Name:** `Portfolio-Backend`.
3.  **OS Image:** Amazon Linux 2023 AMI (Free tier eligible).
4.  **Instance Type:** `t2.micro` (or `t3.micro` if t2 is unavailable). **This gives you 1GB RAM.**
5.  **Key Pair:** Create a new key pair (e.g., `portfolio-key.pem`) and **download it**.
6.  **Network Settings:**
    *   Allow SSH traffic from **My IP**.
    *   Allow HTTP traffic from the internet.
    *   Allow HTTPS traffic from the internet.
7.  **Advanced Details -> User Data:** (Paste this script to auto-install software)
    ```bash
    #!/bin/bash
    dnf update -y
    dnf install git docker -y
    service docker start
    usermod -a -G docker ec2-user
    chkconfig docker on
    ```
8.  **Launch Instance.**

### 2. Deploy Code to EC2
1.  **Connect:** Open your terminal where the `.pem` key is.
    ```powershell
    ssh -i "portfolio-key.pem" ec2-user@<YOUR-EC2-PUBLIC-IP>
    ```
2.  **Clone Repo:**
    ```bash
    git clone https://github.com/ALTHAFHUSSAINSYED/portfolio.git
    cd portfolio
    ```
3.  **Create .env file:**
    ```bash
    nano backend/.env
    # Paste your environment variables here (MONGO_URL, API Keys, etc.)
    # Ctrl+X, Y, Enter to save
    ```
4.  **Build and Run:**
    ```bash
    cd backend
    docker build -t portfolio-backend .
    docker run -d -p 80:8000 --env-file .env --restart always portfolio-backend
    ```
    *Note: We map port 80 (HTTP) to 8000 (Container) so you can access it without a port number.*

---

## Phase 4: Final Configuration

### 1. Update Frontend
1.  Get your **EC2 Public IP** (e.g., `http://54.123.45.67`).
2.  Go to **AWS Amplify Console** -> Environment Variables.
3.  Add/Update `REACT_APP_API_URL` to `http://<YOUR-EC2-IP>`.
4.  Trigger a new build in Amplify (Redeploy).

### 2. Database Access
1.  Go to **MongoDB Atlas**.
2.  Network Access -> Add IP Address.
3.  Add the **Public IP** of your EC2 instance.

---

## Phase 5: (Optional) Free SSL with Nginx
To get `https://` for your backend (required if your frontend is https):
1.  Install Nginx and Certbot on the EC2 instance.
2.  Use Certbot to generate a free Let's Encrypt certificate.
3.  Configure Nginx to proxy requests to `localhost:8000`.
*(We can do this step once the basic HTTP setup is working).*
