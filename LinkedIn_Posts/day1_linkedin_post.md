Day 1: Why I Outgrew the Free Tier

I turned a static portfolio into an AI-powered platform that runs 24/7, handles concurrent users, and costs $18/month.

The Breaking Point

Render's free tier gave me:
- 512MB RAM (crashed on chatbot queries)
- No SSH access (couldn't debug)
- Cold starts after 15 min
- No persistent storage

I chose control over convenience.

The Decision: EC2 Over Managed Services

Why EC2 instead of Fargate/App Runner?
- SSH access for real-time debugging
- Persistent logs (volume mounts)
- Self-hosted CI/CD runner ($0 GitHub Actions costs)
- Full Docker control

Why t3.small?
- AI workloads need burst CPU
- 2GB RAM handles ChromaDB + FastAPI + background jobs
- $15/month vs $40+ for t3.medium

Tradeoff accepted: Single EC2 instance (no redundancy), no autoscaling, manual ops burden.

When traffic justifies it: ALB + Auto Scaling + DocumentDB.

What I Built (Constraints → Design)

Zero-cost CI/CD → Self-hosted GitHub Actions runner
Persistent logs → Volume mounts survive rebuilds
No cold starts → Always-on EC2
SSL + future LB → Nginx reverse proxy (decouples app from ingress)

Cost: $18/month (EC2 $15 + EBS $2.80 + Amplify $0 + LLMs $0)

Results

- API: <200ms (vs 2-3s cold starts)
- Chatbot: ~5-6s (fallbacks handle rate limits and model failures)
- Uptime: 99.9%
- Deploy: 4-5 min automated
- Rollback: Instant

The Lesson

Operational control > managed convenience.

With EC2, I can fine-tune Docker limits, debug via SSH, implement custom logging, and scale on-demand.

Tradeoff: manual ops burden-but that's the cost of learning how systems work.

When to migrate:
- Background jobs (cron, schedulers)
- AI-enabled workloads (vector DBs, LLM-backed services)
- Debugging requirements (SSH, live logs)
- Consistent performance (no cold starts)

What's Next

Known limitations: Single EC2, no autoscaling, self-managed security

Future: Multi-AZ + ALB + Auto Scaling + DocumentDB + CloudWatch alarms

But for now: 50+ concurrent users, daily blogs, <$20/month.

---

🔗 Live demo: https://althafportfolio.site (see how it behaves under real traffic)
🤖 Test the chatbot: Watch the 4-tier fallback in action

For recruiters: Demonstrates hands-on AWS DevOps-EC2, Dockerized services, CI/CD automation, cost optimization, operating AI-enabled workloads in production. Hiring for AWS/DevOps? Let's connect.

#AWS #DevOps #CloudMigration #Docker #CICD #FastAPI #BuildInPublic #SystemDesign #AWSJobs #DevOpsEngineer #RAG #Ai #cloud #DevSecOps
