# LinkedIn Posts - Required Screenshots Guide

This document outlines the specific screenshots needed for each LinkedIn post to maximize engagement and provide visual proof of the technical achievements.

---

## Day 1: From Static Resume to AI-Powered Platform - The AWS Migration Story

### Required Screenshots (2-3 images recommended)

**Screenshot 1: Architecture Diagram**
- **What to show**: Complete system architecture showing:
  - Frontend (AWS Amplify)
  - Backend (EC2 t3.small)
  - AI Components (ChromaDB, MongoDB, S3)
  - Data flow: User → Frontend → Backend → AI Services
  - Dual AI engines: RAG Chatbot + Auto-Blogger
- **Tool**: Create using draw.io, Lucidchart, or Excalidraw
- **Highlight**: Use boxes/arrows to show the migration from Render to AWS

**Screenshot 2: Render vs AWS Comparison**
- **What to show**: Side-by-side comparison table or infographic:
  - Render Free Tier: 512MB RAM, 1 vCPU, No SSH, Ephemeral Storage
  - AWS EC2: 2GB RAM, 2 vCPUs, Full SSH, Persistent Storage
- **Tool**: Create using Canva or PowerPoint
- **Highlight**: Red X marks on Render limitations, Green checkmarks on AWS benefits

**Screenshot 3 (Optional): Live Chatbot Demo**
- **What to show**: Screenshot of the chatbot in action on your portfolio
  - User asking a question
  - Chatbot providing a detailed response
- **Highlight**: Circle the chatbot widget to draw attention

---

## Day 2: Zero-Touch Frontend Deployment - AWS Amplify CI/CD Magic

### Required Screenshots (2-3 images recommended)

**Screenshot 1: Amplify Build Logs**
- **What to capture**: AWS Amplify Console showing:
  - Build in progress or completed
  - Build time: 3-5 minutes
  - Green checkmarks for successful stages (Provision → Build → Deploy → Verify)
  - Deployment status: "Deployment successfully completed"
- **Where**: AWS Amplify Console → App → Deployments → Click on latest deployment
- **Highlight**: Use red box around "Build time: 4m 23s" and green box around "Success"

**Screenshot 2: CI/CD Pipeline Flow**
- **What to show**: Visual diagram of the automated flow:
  ```
  Developer Push → GitHub Webhook → Amplify Build → CloudFront Distribution → Live
  ```
- **Tool**: Create using draw.io or screenshot your `amplify.yml` with annotations
- **Highlight**: Add arrows and time stamps (e.g., "Push at 10:00 AM → Live at 10:05 AM")

**Screenshot 3: Lighthouse Performance Score**
- **What to capture**: Chrome DevTools Lighthouse report showing:
  - Performance: 95+
  - Accessibility: 95+
  - Best Practices: 95+
  - SEO: 95+
- **Where**: Chrome DevTools → Lighthouse tab → Run audit on https://althafportfolio.site
- **Highlight**: Circle the 95+ scores in green

**Screenshot 4 (Optional): CloudFront Distribution Map**
- **What to show**: AWS CloudFront console showing global edge locations
- **Where**: AWS CloudFront Console → Distributions → Your distribution
- **Highlight**: Show "200+ edge locations" or global map

---

## Day 3: Running AI Workloads on a Budget - Self-Hosted CI/CD on EC2

### Required Screenshots (3-4 images recommended)

**Screenshot 1: Docker Container Uptime**
- **What to capture**: Terminal showing:
  ```bash
  docker ps
  ```
  - Container name: `portfolio-backend`
  - Status: `Up 12 days`
  - Ports: `80->8000/tcp`
- **Where**: SSH into EC2 and run `docker ps`
- **Highlight**: Red box around "Up 12 days" and green box around "STATUS: Up"

**Screenshot 2: Resource Utilization**
- **What to capture**: Terminal showing:
  ```bash
  free -h
  df -h
  ```
  - Memory: 1.1GB / 1.9GB (58% utilization)
  - Disk: 11GB / 35GB (31% utilization)
- **Where**: SSH into EC2 and run both commands
- **Highlight**: Green box around "58% memory" and "31% disk" to show efficient usage

**Screenshot 3: GitHub Actions Deployment Success**
- **What to capture**: GitHub Actions workflow run showing:
  - Workflow: "Deploy Backend to EC2"
  - Status: Green checkmark (Success)
  - Duration: 4-5 minutes
  - Steps: Checkout → Build → Deploy → Health Check (all green)
- **Where**: GitHub → Actions tab → Latest workflow run
- **Highlight**: Circle the "Health check passed" step in green

**Screenshot 4: Self-Hosted Runner Status**
- **What to capture**: GitHub Settings showing:
  - Self-hosted runner: "Online" (green dot)
  - Runner name: Your EC2 instance
  - Status: "Idle" or "Active"
- **Where**: GitHub → Settings → Actions → Runners
- **Highlight**: Green box around "Online" status

**Screenshot 5 (Optional): Cost Breakdown**
- **What to show**: AWS Cost Explorer or billing dashboard showing:
  - EC2 t3.small: ~$15/month
  - EBS 35GB: ~$2.80/month
  - Total: ~$18-20/month
- **Where**: AWS Console → Billing Dashboard → Cost Explorer
- **Highlight**: Circle the total cost in green to emphasize affordability

---

## General Screenshot Guidelines

### Visual Style (The "Glitch" Aesthetic)
1. **Dark Mode**: Always use dark mode for terminal/console screenshots (more professional)
2. **Highlighting**:
   - Red boxes: Errors, failures, or "before" states
   - Green boxes: Success, achievements, or "after" states
   - Yellow boxes: Important metrics or key data points
3. **Annotations**: Add arrows and text labels to guide the viewer's eye
4. **Resolution**: Use high-resolution screenshots (at least 1920x1080)

### Tools for Creating Diagrams
- **Architecture Diagrams**: draw.io, Lucidchart, Excalidraw
- **Infographics**: Canva, PowerPoint, Google Slides
- **Screenshot Annotation**: macOS Preview, Windows Snipping Tool + Paint, or Greenshot

### Carousel Format (Recommended)
For each post, create a 3-slide carousel:
- **Slide 1**: The Architecture/Diagram (The logic)
- **Slide 2**: The Code/Configuration (The implementation)
- **Slide 3**: The Real-Time Result (The proof)

This format keeps viewers engaged and increases post reach on LinkedIn.

---

## Screenshot Checklist

Before posting, ensure each screenshot:
- [ ] Is high resolution and clearly readable
- [ ] Has annotations (boxes, arrows, labels) to guide attention
- [ ] Uses consistent color scheme (red = error/before, green = success/after)
- [ ] Shows timestamps or dates to prove recency
- [ ] Hides sensitive information (IPs, credentials, API keys)
- [ ] Is cropped to remove unnecessary UI elements
- [ ] Has a clear focal point (what you want viewers to see first)

---

## Notes
- LinkedIn allows up to 10 images per post, but 2-4 is optimal for engagement
- Use carousel format (swipeable images) for better storytelling
- First image should be the most eye-catching (architecture diagram or success metric)
- Last image should reinforce the "proof" (logs, metrics, live demo)
