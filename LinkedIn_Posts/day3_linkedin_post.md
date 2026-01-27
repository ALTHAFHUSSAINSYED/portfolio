# Day 3: From Manual SSH Deploys to Push-to-Prod in 5 Minutes

I automated backend deployments on EC2 with zero GitHub Actions costs and built-in health checks.

Here's how I went from manual Docker commands to a reliable CI/CD pipeline.

The Problem: Manual Deployments Are Risky

Manual process: SSH → pull code → rebuild image → stop old container → start new → hope nothing broke

What could go wrong: Port conflicts, build failures, app crashes, no quick rollback

I needed automation with safety rails.

The Decision: Self-Hosted GitHub Actions Runner

Why self-hosted?
- Cost: GitHub-hosted $0.008/min vs self-hosted $0
- Direct Docker access: Build and deploy on same machine, no registry push/pull
- Tradeoff: I maintain the runner, single point of failure

For a solo project, this is right.

What I Built

Pipeline:
1. Push to main
2. Cleanup old containers/images
3. Build fresh Docker image
4. Deploy with restart policy
5. Health check (5 retries, 5s interval)
6. Rollback if health check fails

The critical part: Health checks prevent broken deploys from taking down the site.

Timing: 4-5 min (build 2-3 min, deploy 30s, health checks 30s-1 min)
Rollback: Instant (swap containers)

What's Running

Instance: t3.small (2 vCPU, 2GB RAM)
Workloads: FastAPI backend, AI-enabled services, GitHub Actions runner
Resources: ~60% memory, ~30% disk (comfortable headroom)

The Tradeoffs

Gave up: Multi-instance redundancy, auto-scaling, managed CI/CD

Gained: $0 CI/CD costs, full deployment control, faster iteration, learning how CI/CD works

For a portfolio project, intentionally simple.

Future: ALB + Auto Scaling + managed CI/CD when traffic justifies it.

The Lesson

Automation without safety checks is just faster failure.

Bad pipeline: Push → deploy blindly → hope it works
Good pipeline: Push → deploy with validation → verify health → rollback on failure

The health check is the most important part. It's the difference between "deploy broke production at 2 AM" and "deploy failed health check, old version still running."

This complements Day 2's managed frontend by focusing operational effort where failures are more costly.

What's Next

Limitations: Single runner, brief downtime during container swap, no CloudWatch alarms

Future: Blue-green deployments, CloudWatch alarms, automated rollback on error spikes

But for now: 5-min deploys, $0/month, health checks have caught failed deploys before they reached production.

---

🔗 Live demo: althafportfolio.site (deployed 50+ times via this pipeline—zero manual SSH since automation)

For recruiters: Demonstrates hands-on AWS DevOps—automated deployments, health check validation, rollback strategies, operating production services reliably. Hiring for AWS/DevOps? Let's connect.

#AWS #DevOps #CICD #Docker #Automation #BuildInPublic #SystemDesign #AWSJobs #DevOpsEngineer #cloud #DevSecOps #aws     
