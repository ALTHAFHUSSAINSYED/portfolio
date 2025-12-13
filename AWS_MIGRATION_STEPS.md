# AWS Migration: Step-by-Step Guide

This guide separates tasks into **AI Responsibilities** (files I create) and **User Responsibilities** (actions you take in the AWS Console).

## ✅ Phase 1: Preparation (Completed by AI)
I have already prepared the necessary configuration files so you don't have to write them.
- **`backend/Dockerfile`**: Created. Defines how your Python backend runs in a container.
- **`backend/nginx.conf`**: Created. Will be used later for setting up a web server on EC2.

---

## 🚀 Phase 2: Frontend Migration (User Action Required)
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

**🛑 STOP HERE.**
Once the deployment finishes, you will get a URL like `https://main.d12345.amplifyapp.com`.
**Please reply with "Done" and paste that URL here.** I will then give you the instructions for the Backend (EC2) setup.
