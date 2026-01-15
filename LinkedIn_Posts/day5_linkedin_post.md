# Day 5: Automating a Non-Critical Workflow (And Designing for Failure)

I automated daily blog publishing. It fails often, and that's okay.

Here's how I built automation that assumes failure.

## The Reality: Automation Doesn't Mean "Hands-Off"

In production, automation breaks constantly:
- External APIs go down
- Free-tier services hit rate limits
- Outputs are unpredictable
- Edge cases you didn't plan for

**I needed automation that could fail safely without creating messes.**

## The Design: Assume Every Step Will Fail

I didn't try to make it perfect. I designed for graceful failure.

**Key decisions:**
1. **Non-critical workflow** (blog publishing is nice-to-have, not core)
2. **Human-in-the-loop** (3-hour gap: 7 AM generation → 10 AM publishing, manual override window)
3. **Idempotent operations** (each step can retry without side effects, progress saved after each step)

## How I Handle Failures

**Problem 1: External API Failures**
**Solution:** Retry with fallbacks—primary API fails → try secondary → both fail → save progress, notify, retry tomorrow

**Problem 2: Unpredictable Outputs**
**Solution:** Validation gates (check length, validate structure, manual review window)
**Impact:** ~10-15% fail validation

**Problem 3: State Management**
**Solution:** Persistent state (save progress after each step, atomic publishing, survives crashes)

## What I Built (High-Level)

**Architecture:** Scheduler triggers daily job → Multi-step pipeline (Research → Generate → Review → Publish) → Each step saves progress → Failures trigger email notifications

**Known issues:**
- ~10-15% fail validation
- Free-tier API limits cause occasional failures
- Manual intervention is rare, but intentionally supported

**Intentionally best-effort, not production-critical.**

## The Tradeoffs

**Gave up:** "Fully autonomous" (manual review window exists), 100% success rate, instant publishing

**Gained:** $0/month cost, learning to automate unreliable workflows, understanding idempotency

## The Lesson

**Automation without guardrails is just faster failure.**

Good automation:
- Assumes every step will fail
- Saves progress incrementally
- Provides observability (notifications)
- Allows human intervention
- Favors consistency over speed

**Script vs Production:**
- Script: "Run and hope it works"
- Production: "Run, validate, notify, and allow intervention"

This builds on Days 3-4's work—failure handling matters in scheduled jobs just as much as in deployments and runtime.

## What's Next

**Limitations:** Free-tier APIs (unstable), single scheduler, no retry backoff, manual intervention occasionally needed

**Future:** Exponential backoff, dead-letter queue, CloudWatch alarms, upgrade to paid APIs if traffic justifies

But for now: Publishes daily (when it works), $0/month, fails safely.

---

🔗 **Live demo**: https://althafportfolio.site (check blogs section—content published by this system)

**For recruiters:** Demonstrates automating non-critical workflows—designing for failure, retry logic, state persistence, human-in-the-loop safety. Hiring for AWS/DevOps? Let's connect.

#AWS #DevOps #Automation #SystemDesign #BuildInPublic #AWSJobs #DevOpsEngineer
