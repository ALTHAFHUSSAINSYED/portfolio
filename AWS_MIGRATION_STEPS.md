# AWS Migration: Step-by-Step Guide

This guide separates tasks into **AI Responsibilities** (files I create) and **User Responsibilities** (actions you take in the AWS Console).

## ✅ Phase 1: Preparation (Completed by AI)
I have already prepared the necessary configuration files so you don't have to write them.
- **`backend/Dockerfile`**: Created. Defines how your Python backend runs in a container.
- **`backend/nginx.conf`**: Created. Will be used later for setting up a web server on EC2.

---

## 🚀 Phase 2: Frontend Migration (Automated via Amplify)
**Priority:** High
**Why first?** It's the easiest win and gives you a live URL immediately.

**Step 1: Deploy to AWS Amplify**
1.  Log in to your [AWS Console](https://console.aws.amazon.com/).
2.  Search for **"Amplify"** and open it.
3.  Click **"Create new app"** (or "Host my web app").
4.  Select **GitHub** as the source.
5.  Authorize AWS to access your GitHub account and select the `portfolio` repository.
6.  **Build Settings:** Amplify should auto-detect the settings from the `amplify.yml` file I just created.
    - **App Root:** `frontend`
    - **Build Command:** `npm run build`
    - **Output Directory:** `build`
7.  **Environment Variables:**
    - Go to **Hosting > Environment variables**.
    - Add Key: `REACT_APP_BACKEND_URL`
    - Value: `http://localhost:8000` (Temporary placeholder until Backend is ready).
8.  **Rewrites and Redirects:**
    - Go to **Hosting > Rewrites and redirects**.
    - Add Rule:
        - **Source address:** `</^[^.]+$|\.(?!(css|gif|ico|jpg|js|png|txt|svg|woff|woff2|ttf|map|json)$)([^.]+$)/>`
        - **Target address:** `/index.html`
        - **Type:** `200 (Rewrite)`
9.  Click **"Save and Deploy"**.

**Note:** Amplify has a **built-in CI/CD pipeline**. Every time you push to `main`, it will automatically redeploy your frontend. You don't need a separate GitHub Action for this.

**🛑 STOP HERE.**
Once the deployment finishes, you will get a URL like `https://main.d12345.amplifyapp.com`.
**Please reply with "Done" and paste that URL here.** I will then give you the instructions for the Backend (EC2) setup.

---

## ⚙️ Phase 3: Backend Infrastructure (One-Time Setup)

**Step 1: Launch EC2 Instance**
1.  Go to **EC2 Dashboard** -> **Launch Instance**.
2.  **Name:** `Portfolio-Backend`.
3.  **OS Image:** Amazon Linux 2023 AMI.
4.  **Instance Type:** `t2.micro` (Free Tier).
5.  **Key Pair:** Create new -> `portfolio-key` -> Download `.pem` file.
6.  **Network Settings:** Allow SSH, HTTP, HTTPS.
7.  **User Data (Advanced Details):**
    ```bash
    #!/bin/bash
    dnf update -y
    dnf install git docker -y
    service docker start
    usermod -a -G docker ec2-user
    chkconfig docker on
    ```
8.  **Launch.**

**Step 2: Initial Server Setup**
1.  SSH into your server:
    ```bash
    ssh -i "portfolio-key.pem" ec2-user@<YOUR-EC2-IP>
    ```
2.  Clone the repo:
    ```bash
    git clone https://github.com/ALTHAFHUSSAINSYED/portfolio.git
    ```
3.  Create the secrets file:
    ```bash
    cd portfolio/backend
    nano .env
    # PASTE YOUR .env CONTENT HERE
    # Save with Ctrl+X, Y, Enter
    ```

---

## 🔄 Phase 4: Backend Pipeline (GitHub Actions)

I have created `.github/workflows/deploy-backend.yml`. To enable it:

1.  Go to your GitHub Repository -> **Settings** -> **Secrets and variables** -> **Actions**.
2.  Add the following Repository Secrets:
    - `EC2_HOST`: Your EC2 Public IP (e.g., `54.123.45.67`).
    - `EC2_USER`: `ec2-user`
    - `EC2_SSH_KEY`: Open your downloaded `.pem` file with a text editor and paste the *entire* content here.

**Result:** Now, whenever you push changes to the `backend/` folder, GitHub Actions will automatically SSH into your server and update the application.
