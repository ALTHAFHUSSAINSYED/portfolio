# Day 2: Why I Treated Frontend Hosting as an Ops Problem

I deployed a React SPA with zero server management, global CDN, and automatic SSL-for $0/month.

Here's why I chose a managed service over self-hosting.

The Decision: Managed Service Over Self-Hosted

After setting up EC2 for backend, I had a choice for frontend:

Self-host on EC2: Nginx config, SSL renewal, CloudFront setup, manual cache invalidation, server patching

AWS Amplify: Zero server management, automatic SSL, built-in CDN, automatic cache invalidation, Git-based deploys

I chose Amplify. Not because I couldn't self-host-but because frontend hosting is a solved problem that doesn't need my attention.

Why This Was Right

1. Cost: $0/month (vs $20/month Vercel/Netlify) = $240/year savings

2. Monorepo Optimization
- Config: appRoot: frontend
- Backend changes don't trigger frontend rebuilds
- 60% faster deployments

3. Rollback: Last 10 deployments saved, one-click rollback, zero downtime

What I Built

Deployment: Push to main → Amplify detects frontend changes → yarn build → S3 + CloudFront → Live in ~3 min

Metrics:
- Build: ~3 min
- Latency: <100ms globally
- High availability via AWS-managed hosting
- Cost: $0/month

The Tradeoff

Gave up: Full caching control, custom Nginx, edge compute

Gained: Zero ops burden, automatic SSL, global CDN, built-in monitoring

For a static SPA, this is the right tradeoff.

The Lesson

Not every component needs self-management.

Backend on EC2 = correct (needed SSH, Docker control, logs)
Frontend on Amplify = correct (static SPA, no custom logic)

This let me spend my operational budget on the backend, where control actually mattered.

When to use managed services: Solved problems (static hosting, DNS, CDN), low customization needs, cost-effective at your scale

What's Next

Limitations: No SSR, no edge compute, Amplify vendor lock-in

Future: Migrate to Next.js if SSR needed, add edge caching, preview deployments

But for now: 3-min deploys, $0/month, zero maintenance.

---

🔗 Live demo: althafportfolio.site (notice <100ms load times globally)

For recruiters: Demonstrates AWS-native deployment strategies, cost optimization, and knowing when to use managed services vs self-hosting. Hiring for AWS/DevOps? Let's connect.

#AWS #DevOps #Amplify #CloudFront #CICD #BuildInPublic #SystemDesign #AWSJobs #DevOpsEngineer
#aws #cloud #DevSecOps # amplify #frontend #react 