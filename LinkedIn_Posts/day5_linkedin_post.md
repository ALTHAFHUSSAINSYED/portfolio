# Day 5: Automating a Non-Critical Workflow (And Designing for Failure)

Final day of my application series.

I automated daily blog publishing. It fails often, and that's okay.

Here's how I built automation that assumes failure.

The Reality: Automation Doesn't Mean "Hands-Off"

In production, automation breaks constantly:
- External APIs go down
- Free-tier services hit rate limits
- Outputs are unpredictable
- Edge cases you didn't plan for

I needed automation that could fail safely without creating messes.

The Design: Assume Every Step Will Fail

I didn't try to make it perfect. I designed for graceful failure.

Key decisions:
1. Non-critical workflow (nice-to-have, not core)
2. Human-in-the-loop (3-hour gap: 7 AM → 10 AM, manual override)
3. Idempotent operations (retry without side effects, progress saved)

How I Handle Failures

Problem 1: External API Failures
Solution: Retry with fallbacks—primary fails → try secondary → both fail → save, notify, retry tomorrow

Problem 2: Unpredictable Outputs
Solution: Validation gates (check length, structure, manual review)
Impact: ~10-15% fail validation

Problem 3: State Management
Solution: Persistent state (save after each step, atomic publishing, survives crashes)

What I Built

Architecture: Scheduler → Multi-step pipeline (Research → Generate → Review → Publish) → Save progress → Email on failures

Known issues:
- ~10-15% fail validation
- Free-tier API limits cause failures
- Manual intervention rare but supported

Intentionally best-effort, not production-critical.

The Tradeoffs

Gave up: "Fully autonomous", 100% success rate, instant publishing

Gained: $0/month, learning to automate unreliable workflows, understanding idempotency

The Lesson

Automation without guardrails is just faster failure.

Good automation:
- Assumes every step will fail
- Saves progress incrementally
- Provides observability
- Allows human intervention
- Favors consistency over speed

Script vs Production:
- Script: "Run and hope"
- Production: "Run, validate, notify, intervene"

This builds on Days 3-4—failure handling matters in scheduled jobs as much as deployments.

What's Next

Limitations: Free-tier APIs, single scheduler, no retry backoff

Future: Exponential backoff, dead-letter queue, CloudWatch alarms

But for now: Publishes daily (when it works), $0/month, fails safely.

---

🔗 Live demo: althafportfolio.site (check blogs section)

For recruiters: Demonstrates automating non-critical workflows—failure design, retry logic, state persistence, human-in-the-loop. Hiring for AWS/DevOps? Let's connect.

#AWS #DevOps #Automation #SystemDesign #BuildInPublic #AWSJobs #DevOpsEngineer