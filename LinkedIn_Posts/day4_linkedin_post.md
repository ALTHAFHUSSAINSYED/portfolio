# Day 4: Operating an Unreliable AI Workload in Production

I run a chatbot powered by free-tier AI models that fail constantly.

Here's how I designed around failure-treating AI like any other flaky dependency.

The Reality: AI Systems Are Unreliable

In production, they break constantly:
- Free-tier APIs hit rate limits (429 errors)
- Models go offline for maintenance
- Responses are unpredictable (wrong language, verbose, off-topic)
- Latency spikes randomly

I needed a chatbot that could fail gracefully without ruining UX.

The Design: Failure is Normal

I didn't try to make AI reliable. I designed for it to fail safely.

Key decisions:
1. AI is non-critical (nice-to-have, not core)
2. Users never see failures (4-tier fallback, graceful degradation)
3. Cost = $0 (free-tier only, accepting instability)

How I Handle Failures

Problem 1: Rate Limits (429 Errors)
Solution: 4-tier fallback-try primary → fails → switch to secondary → succeeds in ~5-6s

Why 4 tiers? Single model = frequent failures, 4-tier = higher availability

Problem 2: Unpredictable Responses
Solution: Response cleaning (strip disclaimers, remove artifacts, truncate)
Impact: 3-5% need regeneration

Problem 3: Slow Response Times
Solution: Set expectations (loading indicator, no "instant" promises)
Tradeoff: Slower UX for $0 cost

What I Built

Architecture: User query → Vector DB → AI model → Response
Fallbacks: 4 models (if one fails, try next)
Data: Portfolio data in vector DB (prevents hallucination)

Known issues:
- 5-10% tense errors
- 3-5% strange responses
- 5-6s latency

Intentionally best-effort, not production-critical.

The Tradeoffs

Gave up: Guaranteed correctness, fast responses (<2s), 100% uptime

Gained: $0/month (vs $300+/month paid APIs), learning to operate unreliable systems

The Lesson

AI is just another flaky dependency.

You wouldn't put a flaky API in your critical path or skip error handling.

Same rules apply to AI:
- Design for failure, not success
- Isolate from critical paths
- Set user expectations

This builds on Day 3's CI/CD work-failure handling matters at runtime as much as deployment.

Demo vs Production:
- Demo: "Look how smart the AI is"
- Production: "Look how safely it fails"

What's Next

Limitations: Free-tier models, single vector DB, no caching

Future: Response caching (reduce calls 40%), rate limiting, upgrade if traffic justifies

But for now: 50+ concurrent users, $0/month, fails gracefully.

---

🔗 Live demo: althafportfolio.site
🤖 Test the chatbot: Watch how it handles failures

For recruiters: Demonstrates operating non-deterministic workloads-fallback systems, API failures, isolating non-critical features. Hiring for AWS/DevOps? Let's connect.

#AWS #DevOps #SystemDesign #BuildInPublic #AWSJobs #DevOpsEngineer
