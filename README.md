# AI-Native Portfolio Projects

Three production-grade AI systems demonstrating modern ML engineering practices, each with 8 concrete prompts for Claude Code pairing.

> 💡 **Want free alternatives?** Check out [5 Free-Tier AI Projects](./FREE_TIER_AI_PROJECTS.md) that use open-source models and no paid API keys ($0/month instead of $20-50/month).

## Projects Overview

### 1. Legal Document Intelligence Platform
**Domain**: Document processing + RAG
**Stack**: Next.js 14 + Node/Fastify + Postgres (pgvector) + BullMQ + OpenAI + Anthropic
**Key Challenges**: Multi-page PDF ingestion, semantic chunking with overlap, hybrid search (vector + BM25), citation tracking, idempotent processing
**Evals**: 50-question golden dataset, GPT-4-as-judge accuracy ≥0.85, citation precision/recall
**Performance**: p95 query <3s, <$0.10 per document

📄 [Full spec + prompts](./PROJECT_1_LEGAL_DOC_INTELLIGENCE.md)
🛠️ [Build & deployment guide](./PROJECT_1_BUILD_GUIDE.md)

---

### 2. Real-Time Customer Support Triage System
**Domain**: Multi-agent orchestration + classification
**Stack**: Next.js 14 + FastAPI + Postgres + Celery + Redis + OpenAI + Anthropic
**Key Challenges**: Webhook ingestion, multi-agent state machine, real-time routing, escalation logic, SSE updates, conversation context tracking
**Evals**: 200-ticket golden dataset, classification F1 ≥0.9, auto-resolution rate 40%, false-positive <5%
**Performance**: p95 classification <500ms, 1000 tickets/hour throughput

📄 [Full spec + prompts](./PROJECT_2_SUPPORT_TRIAGE_SYSTEM.md)
🛠️ [Build & deployment guide](./PROJECT_2_BUILD_GUIDE.md) ⭐ **Start here**

---

### 3. AI-Powered Code Review Assistant
**Domain**: Static analysis + GitHub automation
**Stack**: Next.js 14 + Node/Fastify + Postgres (pgvector) + BullMQ + tree-sitter + Claude + o1
**Key Challenges**: GitHub App webhooks, incremental diff analysis, AST parsing, semantic code search, blast radius estimation, fix suggestion diffs
**Evals**: 100-PR golden dataset, detection F1 ≥0.75, false-positive ≤20%, fix acceptance ≥50%
**Performance**: p95 <10s for <200 LOC, <5min for <1000 LOC, <$0.50 per review

📄 [Full spec + prompts](./PROJECT_3_CODE_REVIEW_ASSISTANT.md)
🛠️ [Build & deployment guide](./PROJECT_3_BUILD_GUIDE.md)

---

## Why These Projects Stand Out

### Engineering Rigor
- **No toy apps**: Every project handles backpressure, retries, idempotency, partial failures, pagination, schema migrations
- **Real-world scale**: 10k+ documents, 1000+ tickets/hour, 100k LOC codebases
- **Production patterns**: Queue-based async processing, circuit breakers, rate limiting, cursor pagination, dead-letter queues

### AI-Native Design
- **Precise evals**: Golden datasets (50-200 samples), quantitative metrics (F1, accuracy, latency, cost)
- **Multi-model orchestration**: GPT-4o for structured extraction, Claude for long-context reasoning, o1 for deep analysis
- **RAG sophistication**: Hybrid search, reranking, citation tracking, semantic similarity

### Observability
- **OpenTelemetry**: Custom spans for AI calls, queue depth, error tracking
- **Grafana dashboards**: Latency percentiles, cost monitoring, eval scores, queue health
- **Cost tracking**: Per-operation cost logging, daily/hourly aggregations

### Distinct Problem Spaces
1. **Document intelligence**: Extraction + RAG + Q&A (unstructured → structured)
2. **Support triage**: Real-time classification + multi-agent routing + escalation (event-driven)
3. **Code review**: Static analysis + semantic search + automated fixes (developer tooling)

---

## How to Use

Each project includes **2 documents**:

### 1. Project Spec (PROJECT_X_*.md)
- Architecture overview (500-700 words)
- Key engineering concerns (specific solutions to hard problems)
- AI system details (model selection, prompt strategies, eval metrics)
- 8 Claude Code prompts (copy-paste ready)

### 2. Build Guide (PROJECT_X_BUILD_GUIDE.md) ⭐
- **Validation checklists** after each prompt (how to verify it worked)
- **Troubleshooting** for common issues
- **Health checks** to ensure everything is working
- **Deployment instructions** (Railway, Vercel, Docker VPS)
- **Production smoke tests** to verify live deployment

### The 8 Prompts:
   - a) Scaffold monorepo
   - b) Write contracts (OpenAPI + GraphQL)
   - c) Design database + migrations
   - d) Implement queue workers
   - e) Create test suites (unit + integration + load)
   - f) Build AI pipeline + eval harness
   - g) Author CI/CD workflows
   - h) Integrate observability

### Recommended Build Order
1. **Start with Project 2** (Support Triage) — fastest to MVP, clearest eval metrics
2. **Then Project 3** (Code Review) — builds on multi-model patterns, adds GitHub integration
3. **Finally Project 1** (Legal Docs) — most complex RAG pipeline, longest processing times

### Time Estimates (with Claude Code)
- Project 2: 12-16 hours
- Project 3: 14-18 hours
- Project 1: 16-20 hours

---

## Tech Stack Decision Matrix

| Concern | Project 1 | Project 2 | Project 3 |
|---------|-----------|-----------|-----------|
| **Frontend** | Next.js 14 RSC | Next.js 14 SSE | Next.js 14 OAuth |
| **Backend** | Node + Fastify | Python FastAPI | Node + Fastify |
| **ORM** | Prisma | SQLAlchemy | Prisma |
| **Queue** | BullMQ | Celery | BullMQ |
| **Vector DB** | pgvector | pgvector | pgvector |
| **Cache** | Redis | Redis | Redis |
| **Storage** | Supabase S3 | N/A | Supabase S3 |
| **Primary LLM** | Claude (200k ctx) | Claude Sonnet | Claude Sonnet 3.5 |
| **Secondary LLM** | GPT-4 Turbo | GPT-4o | OpenAI o1 |
| **Embeddings** | text-embedding-3 | Voyage | Voyage Code |

---

## Common Patterns Across All Projects

### Idempotency
- Content hash deduplication (P1)
- External ID uniqueness constraints (P2)
- Commit SHA composite keys (P3)

### Backpressure
- BullMQ/Celery rate limiting
- Priority queues (urgent first)
- Circuit breakers for AI APIs

### Partial Failures
- Granular error logging
- Resumable processing states
- Dead-letter queues

### Observability
- OpenTelemetry custom spans
- Prometheus metrics (latency, cost, queue depth)
- Grafana dashboards (4-5 panels each)

### Testing
- Jest/pytest with 80%+ coverage
- Integration tests with mocked LLM calls
- k6/locust load tests with latency assertions

### Evals
- Golden datasets (50-200 samples)
- Automated scoring (F1, accuracy, recall)
- CI gates (fail on regression)

---

## Next Steps

1. **Pick a project** based on domain interest
2. **Clone template**: Use prompts (a)-(h) in sequence with Claude Code
3. **Customize eval dataset**: Replace seed data with your domain examples
4. **Deploy**: Use GitHub Actions to push to Vercel (web) + Railway (api)
5. **Blog about it**: Document cost optimizations, eval improvements, production war stories

---

## License
MIT — feel free to use these specs for portfolio projects, tutorials, or commercial work.

## Contributing
These specs are living documents. PRs welcome for:
- Alternative stack implementations (e.g., Go + Chi, Rust + Axum)
- Additional eval metrics
- Cost optimization techniques
- New project ideas following the same rigor

---

**Built with Claude Code** 🤖
