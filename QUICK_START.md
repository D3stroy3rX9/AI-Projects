# Quick Start Guide

## What You Have

**7 comprehensive documents** for building 3 production-grade AI portfolio projects:

```
AI-Projects/
├── README.md                           # Overview & comparison
├── PROJECT_1_LEGAL_DOC_INTELLIGENCE.md # Legal doc RAG spec + 8 prompts
├── PROJECT_1_BUILD_GUIDE.md            # Build validation & deployment
├── PROJECT_2_SUPPORT_TRIAGE_SYSTEM.md  # Support triage spec + 8 prompts
├── PROJECT_2_BUILD_GUIDE.md            # Build validation & deployment ⭐ START HERE
├── PROJECT_3_CODE_REVIEW_ASSISTANT.md  # Code review spec + 8 prompts
└── PROJECT_3_BUILD_GUIDE.md            # Build validation & deployment
```

---

## How to Build (Step-by-Step)

### 1. Choose Your Project

**Recommended order:**
- 🥇 **Project 2** (Support Triage) - 12-16hrs - Best for learning
- 🥈 **Project 3** (Code Review) - 14-18hrs - GitHub integration
- 🥉 **Project 1** (Legal Docs) - 16-20hrs - Most complex RAG

### 2. Read the Spec

Open `PROJECT_X_*.md` to understand:
- Architecture decisions
- AI system design
- Engineering challenges solved

### 3. Follow the Build Guide

Open `PROJECT_X_BUILD_GUIDE.md` and:

**For each of the 8 prompts (a-h):**

1. **Copy the prompt** from the spec
2. **Paste into Claude Code** (in this chat or new session)
3. **Wait for completion**
4. **Run the validation checklist** from build guide
5. **Troubleshoot if needed** (guide has solutions)
6. **Proceed to next prompt** only when validation passes

### 4. Verify Complete System

After all 8 prompts:
- Run the **complete health check** script
- Verify all **success criteria** checkboxes

### 5. Deploy to Production

Follow deployment section in build guide:
- **Railway + Vercel** (easiest, recommended)
- **Docker VPS** (more control)
- **Kubernetes** (enterprise scale)

### 6. Run Production Smoke Tests

Execute the production test suite to verify:
- End-to-end functionality
- Performance targets (latency, throughput)
- Eval metrics (F1, accuracy, cost)

---

## Example: Building Project 2 (Support Triage)

```bash
# 1. Create a new folder for the project
mkdir support-triage-system
cd support-triage-system

# 2. Open PROJECT_2_SUPPORT_TRIAGE_SYSTEM.md
# Copy prompt (a) - scaffold

# 3. Paste into Claude Code:
"Create a Turborepo monorepo with:
- apps/web: Next.js 14 with App Router, TypeScript, Tailwind CSS, Zustand for state
- apps/api: Python FastAPI with uvicorn, poetry for deps (fastapi, sqlalchemy, celery, redis, opentelemetry)
- packages/contracts: OpenAPI spec, generate TypeScript client with openapi-python-client
- Root pyproject.toml, turbo.json for task orchestration
..."

# 4. Wait for Claude to generate files

# 5. Open PROJECT_2_BUILD_GUIDE.md → Step 1 validation:
ls -la  # Check structure
pnpm install  # Install deps
docker-compose up -d  # Start services
pnpm build  # Test build
pnpm dev  # Start dev servers

# 6. Verify all checks pass ✓

# 7. Move to prompt (b) - contracts
# Repeat steps 3-6...

# Continue through all 8 prompts (a-h)
```

---

## Validation is Critical

**Why validate after each step?**

❌ **Without validation:**
- Step 3 fails → continue to step 4 → step 5 breaks → spend hours debugging
- Hard to know which step caused the issue
- Might build entire system on broken foundation

✅ **With validation:**
- Step 3 fails → fix immediately with troubleshooting guide
- Each step verified before proceeding
- Know exactly when things work

**Each validation checklist includes:**
- Commands to run (curl, psql, docker, etc.)
- Expected output (exact values or patterns)
- Troubleshooting if output doesn't match

---

## What Makes These Projects Production-Grade?

### Real Engineering Concerns ✓
- **Idempotency**: Duplicate handling (content hashes, unique constraints)
- **Backpressure**: Rate limiting, priority queues, circuit breakers
- **Partial failures**: Granular error logging, resumable states
- **Retries**: Exponential backoff, dead-letter queues
- **Pagination**: Cursor-based with stable ordering
- **Schema migrations**: Versioned with rollback scripts

### AI Best Practices ✓
- **Precise evals**: Golden datasets with F1/accuracy metrics
- **Multi-model**: Right model for each task (GPT-4o extraction, Claude reasoning)
- **Cost tracking**: Per-operation logging, daily aggregations
- **Latency targets**: p95/p99 SLOs enforced in tests

### Observability ✓
- **OpenTelemetry**: Distributed tracing with custom spans
- **Prometheus**: Metrics (latency histograms, counters, gauges)
- **Grafana**: Pre-built dashboards (4-5 panels)
- **Health checks**: Comprehensive system validation

### Testing ✓
- **Unit tests**: 80%+ coverage requirement
- **Integration tests**: End-to-end flows with mocked APIs
- **Load tests**: k6/locust with latency assertions
- **CI gates**: Coverage, eval scores, build success

---

## Common Questions

### Q: Can I use these prompts with other AI coding assistants?
**A:** Yes! The prompts are designed to be clear and specific. They work with:
- Claude Code (optimal)
- GitHub Copilot Workspace
- Cursor
- Any AI that can generate code from natural language

### Q: Do I need all the API keys upfront?
**A:** No. You can:
- Start with just OpenAI for initial build
- Add Anthropic when you reach prompt (f) - AI pipeline
- Use free tiers for Voyage/Cohere initially
- Supabase has generous free tier

### Q: What if a prompt doesn't work exactly as written?
**A:**
1. Check validation output for specific errors
2. Consult troubleshooting section in build guide
3. Adjust prompt slightly (e.g., specify different package versions)
4. Ask follow-up: "The build failed with error X, how do I fix?"

### Q: Can I customize/extend the projects?
**A:** Absolutely! Each project is a foundation. Ideas:
- **Project 1**: Add multi-language OCR, table extraction, contract comparison
- **Project 2**: Add sentiment analysis trends, auto-translation, CSAT prediction
- **Project 3**: Add security scanning, test generation, code style enforcement

### Q: How do I show these in my portfolio?
**A:**
1. **Deploy live** (Railway is easiest)
2. **Create demo video** (Loom) showing:
   - Upload/trigger flow
   - AI processing in real-time
   - Grafana dashboard with metrics
3. **Write blog post** documenting:
   - Architectural decisions
   - Cost optimizations ($X per operation)
   - Eval improvements (F1 0.75 → 0.82)
4. **GitHub README** with:
   - Architecture diagram
   - Screenshots of UI + dashboard
   - Performance benchmarks
   - Links to deployed app

---

## Getting Help

### If validation fails:
1. Check **Troubleshooting** section in build guide
2. Verify **Prerequisites** (Node version, Docker, API keys)
3. Check Docker logs: `docker-compose logs -f`
4. Search error message in project's Issue tracker

### If deployment fails:
1. Check **Deployment** section for platform-specific notes
2. Verify environment variables set correctly
3. Check platform logs (Railway dashboard, Vercel deployment)
4. Try local Docker deployment first to isolate issues

### If evals don't meet targets:
1. Check **golden dataset** quality (diverse examples?)
2. Adjust **prompts** (more specific instructions)
3. Increase **context** (more examples, better retrieval)
4. Try **different model** (o1 instead of GPT-4, etc.)

---

## Success Metrics

You'll know you're successful when:

### Technical Metrics
- [ ] All 8 validation checklists pass
- [ ] Health check script returns all green
- [ ] Load test meets latency targets (p95)
- [ ] Eval metrics exceed thresholds (F1, accuracy)
- [ ] Test coverage ≥ 80%
- [ ] CI pipeline passes on GitHub

### Deployment Metrics
- [ ] Production URL is live and accessible
- [ ] Can complete end-to-end flow (upload → process → query)
- [ ] Grafana dashboard shows real-time metrics
- [ ] No errors in logs for 10+ minutes
- [ ] Smoke tests pass on production

### Portfolio Metrics
- [ ] GitHub repo is public with good README
- [ ] Demo video uploaded (3-5 min walkthrough)
- [ ] Blog post written (1000+ words)
- [ ] Added to LinkedIn/portfolio site
- [ ] Cost per operation documented (<$1 target)

---

## Time Breakdown (Realistic)

### Project 2 (Support Triage) - 12-16 hours

| Phase | Time | Notes |
|-------|------|-------|
| Setup + Scaffold | 1-2h | Docker, deps, monorepo structure |
| Contracts + Data | 2-3h | OpenAPI, Prisma, migrations, seed |
| Workers | 2-3h | Celery tasks, retries, idempotency |
| Tests | 1-2h | Jest/pytest, mocks, load tests |
| AI Pipeline | 3-4h | Agents, RAG, evals (most time here) |
| CI/CD | 1h | GitHub Actions, Docker builds |
| Instrumentation | 1-2h | OpenTelemetry, Grafana |
| Deployment | 1-2h | Railway setup, production smoke tests |

### Project 3 (Code Review) - 14-18 hours
- **+2-4h** for GitHub App setup + tree-sitter parsing

### Project 1 (Legal Docs) - 16-20 hours
- **+2-4h** for PDF processing + hybrid search tuning

---

## Next Steps After Building

### 1. Optimize Costs
- Cache embeddings for duplicate content
- Batch API calls (100 at a time)
- Use cheaper models for simple tasks
- **Target**: Reduce cost per operation by 50%

### 2. Improve Evals
- Expand golden dataset (50 → 200 samples)
- Add edge cases (empty inputs, malformed data)
- Track eval scores over time (prevent regression)
- **Target**: Increase F1 by 0.05-0.10

### 3. Scale Testing
- Run load tests at 2x, 5x, 10x target load
- Identify bottlenecks (DB queries, API calls)
- Add caching, connection pooling
- **Target**: Support 10x load with <2x cost

### 4. Add Features
Each project has a clear extension path in the build guide.

### 5. Blog & Share
Write about:
- "How I built a production RAG system in 16 hours"
- "Cost optimization techniques that saved $X/month"
- "Eval harness that caught 5 regressions before production"

---

## You're Ready!

Pick a project, open the spec + build guide, and start with prompt (a).

**Remember**: Validate after EVERY step. That's the secret to success.

Good luck! 🚀

---

**Questions?** Each build guide has troubleshooting sections. The prompts are designed to be self-contained and executable.
