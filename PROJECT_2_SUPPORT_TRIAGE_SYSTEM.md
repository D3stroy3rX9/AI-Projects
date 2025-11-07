# Project 2: Real-Time Customer Support Triage System

## Overview
A multi-agent AI system that ingests support tickets from webhooks, classifies urgency/category in real-time, routes to appropriate specialists (human or AI), attempts automated resolution for common issues, and escalates complex cases. Handles 1000+ tickets/hour with sub-second classification, maintains conversation context across multiple turns, and tracks resolution metrics.

## Architecture
- **Frontend**: Next.js 14 with real-time updates via Server-Sent Events, shadcn/ui chat interface
- **API**: Python FastAPI + SQLAlchemy, async/await for concurrent processing
- **Database**: Postgres 16 (Supabase), Redis for session state + rate limiting
- **Queue**: Celery + Redis for async workflows (enrichment, notification, feedback loop)
- **AI**: OpenAI GPT-4o for classification (structured outputs), Claude Sonnet for response generation, Voyage embeddings for semantic ticket matching
- **Real-time**: Redis Pub/Sub for agent status updates, SSE endpoint for live ticket feed
- **Observability**: OpenTelemetry with FastAPI auto-instrumentation, custom metrics for agent success rate

## Key Engineering Concerns
- **Idempotency**: Webhook signature validation (HMAC), dedupe on `external_ticket_id` unique constraint
- **Backpressure**: Celery worker pools (10 workers), priority queues (urgent tickets first), circuit breaker for AI API failures
- **Partial Failures**: If classification succeeds but routing fails, store partial state, allow manual retry
- **Schema Migrations**: Alembic with up/down migrations, tested in CI before deploy
- **Pagination**: Keyset pagination on `(priority desc, created_at desc, id)` composite index
- **Agent Orchestration**: State machine (new → classifying → routing → resolving → closed) persisted in DB
- **Rate Limiting**: Redis sliding window (100 req/min per API key), backoff for AI calls

## AI System Details
- **Classification Agent**: GPT-4o with JSON schema (urgency: low/medium/high/critical, category: billing/technical/account, sentiment: positive/neutral/negative), <500ms p95
- **Resolution Agent**: Claude Sonnet with RAG over knowledge base (500 articles), generates draft response + confidence score
- **Escalation Logic**: If confidence < 0.7 or sentiment == negative, route to human queue
- **Context Tracking**: Store conversation history in `ticket_messages` table, include last 10 messages in LLM context
- **Semantic Matching**: Embed new ticket, find top 5 similar resolved tickets (pgvector), use as few-shot examples
- **Evals**: Golden dataset of 200 tickets with human-labeled urgency/category, measure classification accuracy (F1 > 0.9), auto-resolution rate (target 40%), false-positive escalations (<5%)
- **Latency Target**: Classification p95 < 500ms, full resolution attempt < 5s
- **Cost Target**: <$0.05 per ticket triage, <$0.15 per resolution attempt

## Prompts for Claude Code Pairing

### a) Scaffold
```
Create a monorepo with:
- apps/web: Next.js 14 with App Router, TypeScript, Tailwind, Zustand for state
- apps/api: Python FastAPI with uvicorn, poetry for deps (fastapi, sqlalchemy, celery, redis, opentelemetry)
- packages/contracts: OpenAPI spec, generate TypeScript client with openapi-python-client
- Root pyproject.toml, turbo.json for task orchestration
- Dockerfiles: multi-stage for FastAPI (slim base), Next.js (standalone output)
- docker-compose.yml: postgres, redis, celery worker, flower (celery monitoring)
- .env.example with required keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, REDIS_URL, DATABASE_URL)
```

### b) Contracts
```
Write OpenAPI 3.1 spec (openapi.yaml) with:
- POST /webhooks/ticket (validate HMAC signature, create ticket)
- GET /tickets (keyset pagination: priority/created_at/id cursor)
- GET /tickets/{id} (include messages, agent actions, current state)
- POST /tickets/{id}/messages (add customer reply, trigger re-triage)
- GET /tickets/{id}/stream (SSE endpoint for real-time updates)
- POST /admin/classify (manual classification override)
Use openapi-python-client to generate types in packages/contracts.
Create Pydantic models for: TicketCreate, TicketClassification, AgentAction, ResolutionAttempt.
```

### c) Data
```
Design SQLAlchemy models (alembic/models.py):
- Ticket: id, external_id (unique), subject, body, priority enum, category enum, status enum, assigned_to, created_at, updated_at
- TicketMessage: id, ticket_id, sender enum (customer/agent/system), content, created_at
- AgentAction: id, ticket_id, agent_type (classifier/resolver), action (classified/routed/resolved), confidence, metadata jsonb
- KnowledgeArticle: id, title, content, embedding vector(1024), category, views
Create indexes: external_id unique, (priority, created_at, id) composite for pagination, embedding ivfflat.
Write Alembic migrations in alembic/versions/.
Seed script (seed.py): use Faker to create 500 tickets (vary priority/category), 100 knowledge articles with embeddings.
```

### d) Workers
```
Set up Celery in apps/api/workers/:
- Configure Redis as broker and result backend
- Define tasks:
  1. classify_ticket_task(ticket_id): call GPT-4o, update ticket priority/category
  2. attempt_resolution_task(ticket_id): RAG search knowledge base, generate response, create AgentAction
  3. send_notification_task(ticket_id, recipient): async email/webhook
Make classify_ticket_task idempotent: check if classification exists in AgentAction table.
Add retry logic: 3 attempts, exponential backoff (2/4/8s), on_failure callback to mark ticket as 'classification_failed'.
Implement dead-letter queue for tasks failing after max retries.
Add priority queue: 'critical' tickets go to high-priority queue.
```

### e) Tests
```
Set up pytest in apps/api/tests/ with pytest-asyncio, httpx for async client.
Unit tests:
- test_classification_schema (validate JSON output matches Pydantic model)
- test_idempotency (duplicate external_id rejected with 409)
- test_keyset_pagination (correct cursor encoding/decoding)
Integration tests:
- test_webhook_to_classification_flow (POST webhook → Celery task → DB updated)
- test_rag_resolution (query knowledge base, assert correct article retrieved)
- Mock OpenAI/Anthropic with pytest-mock
Create locust load test (locustfile.py):
- Simulate 1000 tickets/hour, 50 concurrent users
- Assert classification p95 < 500ms, no 5xx errors
```

### f) AI
```
Implement agent system in apps/api/agents/:
- ClassifierAgent(ticket): call GPT-4o with structured output (use Pydantic model), parse urgency/category/sentiment
- ResolverAgent(ticket):
  1. Embed ticket body with Voyage
  2. Query pgvector for top 5 similar tickets + knowledge articles
  3. Build prompt with examples
  4. Call Claude Sonnet, extract confidence score from reasoning
- EscalationAgent(ticket, resolution): if confidence < 0.7, create human task
Create eval harness in apps/api/eval/:
- Load golden-tickets.jsonl (200 tickets with labels)
- Run ClassifierAgent, compute precision/recall/F1 per category
- Run ResolverAgent, measure auto-resolution rate (confidence >= 0.7) and false positives (resolved but should escalate)
- Save eval-results.json with scores
- Assert F1 >= 0.9, false-positive rate <= 0.05
```

### g) CI/CD
```
Create .github/workflows/test.yml:
- Run pytest with coverage (fail if < 80%)
- Run eval harness, fail if F1 < 0.9 or false-positive rate > 0.05
- Run locust test (1 min), assert p95 < 500ms
Create .github/workflows/build.yml (on main merge):
- Build Docker images (api, web, celery worker)
- Push to GHCR with tags: git SHA, 'latest'
- Run Alembic migration check (ensure no conflicts)
Create .github/workflows/deploy.yml (manual trigger):
- Deploy to staging/production (show structure with env vars)
- Run smoke tests (health check, single classification)
```

### h) Instrumentation
```
Integrate OpenTelemetry in apps/api/main.py:
- Use FastAPIInstrumentor for auto-instrumentation
- Add custom spans:
  - 'classify_ticket' (tag: ticket_id, priority, category)
  - 'resolve_ticket' (tag: ticket_id, confidence, resolved boolean)
  - 'rag_search' (tag: query, num_results)
- Export to Tempo (docker-compose service)
Add Prometheus metrics (prometheus-fastapi-instrumentator):
- ticket_classified_total (counter, label: category)
- resolution_confidence (histogram)
- celery_task_duration_seconds (histogram, label: task_name)
Create grafana/dashboard.json:
- Panel 1: Classification latency p50/p95/p99 (line chart)
- Panel 2: Auto-resolution rate over time (graph: resolved / total)
- Panel 3: Celery queue depth (gauge)
- Panel 4: AI cost per hour (from AgentAction table, compute sum of cost)
- Panel 5: Error rate by endpoint (bar chart)
Add Tempo, Prometheus, Grafana to docker-compose.yml.
```

## Success Metrics
- Classify 1000 tickets in <10 minutes (100/min throughput)
- Classification accuracy F1 >= 0.9 on golden set
- Auto-resolution rate >= 40% with <5% false positives
- E2E latency (webhook → classified) p95 < 1s
- Zero ticket loss on worker restarts (Celery Redis persistence)
- 80%+ test coverage
