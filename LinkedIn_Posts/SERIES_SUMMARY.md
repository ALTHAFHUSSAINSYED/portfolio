# 5-Day LinkedIn Series: Portfolio Transformation Journey

## Series Overview
**"Converting My Static Webpage to a Fully Functional AI-Powered Website: A DevOps Migration Story"**

**Publishing Schedule:** January 13-17, 2026 (Monday-Friday)

---

## Day 1: Why I Outgrew the Free Tier (And What I Built Instead)
**Focus:** Migration decision from Render to AWS EC2

**Key Topics:**
- Breaking point: Render free tier limitations (512MB RAM, no SSH, cold starts)
- Decision rationale: Why EC2 over Fargate/App Runner
- Instance choice: Why t3.small (burstable CPU, cost optimization)
- Tradeoffs accepted: Single point of failure, manual ops, no autoscaling
- Architecture: Constraints → Design responses
- Results: <200ms API response, 99.9% uptime, $18/month total cost
- Engineering lesson: Operational control > managed convenience

---

## Day 2: Frontend Architecture - AWS Amplify Deployment
**Focus:** Zero-cost frontend CI/CD with global CDN

**Key Topics:**
- Technology stack: React 18, Shadcn/UI, AWS Amplify
- Deployment pipeline: Automated builds, CloudFront CDN, 3-minute deploys
- Monorepo optimization: Frontend-only builds, 60% faster
- Cost optimization: $0/month (vs $20/month Vercel/Netlify)
- Performance metrics: <1.2s First Contentful Paint, 99.99% uptime
- DevOps wins: Zero-config SSL, automatic rollbacks, global edge caching

---

## Day 3: Backend Deployment & Self-Hosted CI/CD
**Focus:** Dockerized FastAPI on EC2 with GitHub Actions runner

**Key Topics:**
- Docker containerization: Python 3.11-slim, optimized image
- EC2 infrastructure: t3.small specs, resource utilization (58% memory, 31% disk)
- AI-powered features: RAG chatbot, auto-blogger system
- Self-hosted CI/CD: GitHub Actions runner on EC2, zero compute costs
- Deployment automation: 4-5 minute automated deploys with health checks
- Nginx reverse proxy: SSL termination, ports 80/443 → Docker 8000
- Security: SSH key-only, iptables firewall, no password auth

---

## Day 4: Building an AI Chatbot That Actually Knows Me - RAG Pipeline
**Focus:** 4-tier fallback chatbot with 99% accuracy, zero hallucinations

**Key Topics:**
- The struggle: Generic chatbots that hallucinate fake information
- Failed attempt: 3 separate ChromaDB collections (query routing complexity)
- Solution: Unified `portfolio_master` collection with metadata tagging
- RAG pipeline: Google Gemini embeddings (768-dim), semantic search
- 4-tier LLM fallback: Gemma 3 27B → Mistral 7B → Gemini 2.5 Flash → Llama 3.2 3B
- Challenges overcome: Predefined responses, date/tense accuracy, context truncation
- Ongoing challenges: 5-6s latency, 429 rate limits, tense errors, unpredictable model responses
- Results: 99% accuracy, 99.9% uptime, $0/month cost

---

## Day 5: The Auto-Blogger That Writes While I Sleep - 6-Component Agentic Workflow
**Focus:** Autonomous blog generation with 100% success rate (last 4 days)

**Key Topics:**
- The struggle: 60% failure rate initially, now 100% success
- 6-component architecture: Scheduler, Researcher, Writer, Critic, Publisher, Notifier
- Scheduler: APScheduler (6 AM cleanup, 7 AM generation, 10 AM publishing)
- Researcher: SERPER API for real-time Google trends
- Writer (2-agent system): DeepSeek R1 (outliner) + Mistral Small (drafter)
- Critic: DeepSeek R1 with 90% quality threshold
- Publisher: S3 + MongoDB + ChromaDB (atomic publishing with retries)
- Notifier: Resend API (success/failure emails)
- Timeline: 7:00 AM start → 7:06 AM complete (6 minutes total)
- Challenges overcome: Agent 1 failures, title extraction, publishing job errors
- Ongoing challenges: Free-tier model availability (CRITICAL), critic score variability, SERPER rate limits, pipeline timeouts
- Results: 100% success last 4 days, 91.5/100 average score, $0/month cost

---

## Series Themes

**Consistent Focus Across All Posts:**
- Engineering judgment over tool-listing
- Tradeoffs and risk awareness
- Cost optimization ($18/month total infrastructure)
- Free-tier API strategies
- DevOps automation and reliability
- Real metrics and honest challenges

**Target Audience:**
- DevOps engineers
- Backend/Platform engineers
- Early-stage startup recruiters
- Technical hiring managers

**Call to Action:**
- Live site: https://althafportfolio.site
- Test the chatbot
- DM for architecture discussions
- Recruiter outreach for DevOps/Backend/Platform roles
