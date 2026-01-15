# Quick Attachment Guide for LinkedIn Posts (Days 3-5)

## Day 3: Backend Dockerization - Self-Hosted CI/CD on EC2

**Must Have (2-3 images):**

1. **Docker Container Uptime**
   - SSH into EC2: `docker ps`
   - Show: Container running 12+ days, port 80->8000

2. **Resource Utilization**
   - SSH into EC2: `free -h` and `df -h`
   - Show: 58% memory (1.1GB/1.9GB), 31% disk (11GB/35GB)

3. **GitHub Actions Success**
   - GitHub → Actions tab
   - Show: Green checkmark, 4-5 min deployment, health check passed

**Optional:**
- Self-hosted runner status (GitHub Settings → Actions → Runners)
- AWS Cost Explorer showing ~$18-20/month

---

## Day 4: RAG Chatbot - 4-Tier Fallback System

**Must Have (2-3 images):**

1. **Fallback Logs**
   - FastAPI logs or OpenRouter dashboard
   - Show: Tier 1 fails (429 error) → Tier 2 succeeds (200 OK)
   - Response time: 5-6 seconds

2. **ChromaDB Migration Diagram**
   - Create diagram showing:
     - OLD: 3 collections (portfolio, Projects_data, Blogs_data)
     - NEW: 1 unified collection (portfolio_master) with metadata tags
   - Tool: draw.io or Excalidraw

3. **Chatbot Live Demo**
   - Screenshot from https://althafportfolio.site
   - Show: User question + accurate chatbot response

**Optional:**
- ChromaDB Cloud dashboard (https://app.trychroma.com)

---

## Day 5: Auto-Blogger - 6-Component Agentic Workflow

**Must Have (3-4 images):**

1. **Success Email** ✅ (You already have this!)
   - Subject: "✅ Blog Published: [Category]"
   - Show: Title, score (92/100), URL, timestamp

2. **Failure Email** ❌ (You already have this!)
   - Subject: "❌ Auto-Blogger FAILED"
   - Show: Error reason (Agent 1 failed, Title Extraction Failed, etc.)

3. **Scheduler Logs**
   - SSH into EC2: `cat /app/backend/logs/auto_blogger/*.log`
   - Show timeline:
     - 7:00 AM: Generation started
     - 7:06 AM: Critic approved
     - 10:00 AM: Published
     - Total: 6 minutes processing

4. **Published Blog on Website**
   - Screenshot from https://althafportfolio.site (blogs section on main page)
   - Show: Latest blog in the portfolio

**Optional:**
- OpenRouter dashboard showing 6-minute generation time

---

## Quick Commands for EC2 Screenshots

```bash
# SSH into EC2
ssh -i "PORTFOLIO.pem" ec2-user@[YOUR_IP]

# Day 3 - Docker & Resources
docker ps
free -h
df -h

# Day 5 - Auto-blogger logs
ls -la /app/backend/logs/auto_blogger/
cat /app/backend/logs/auto_blogger/scheduler_state.json
```

---

## Screenshot Tips

- **Dark Mode**: Use dark terminal for professional look
- **Highlighting**: Red boxes for errors, green for success
- **Resolution**: At least 1920x1080
- **Crop**: Remove unnecessary UI elements
- **Hide Sensitive**: No IPs, credentials, or API keys visible
