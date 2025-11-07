# Project 1: Legal Document Intelligence Platform

## Overview
A document processing pipeline that ingests multi-page legal PDFs, extracts structured metadata (parties, dates, clauses, obligations), chunks content with semantic overlap, embeds into Postgres+pgvector, and exposes a Next.js interface for conversational Q&A with citation tracking. Designed for 10k+ document corpus with incremental ingestion, deduplication, and versioning.

## Architecture
- **Frontend**: Next.js 14 App Router + React Server Components, TanStack Query for optimistic updates
- **API**: Node.js + Fastify, OpenAPI 3.1 spec with typed clients
- **Database**: Supabase Postgres (pgvector extension), Prisma ORM with migration history
- **Storage**: Supabase Storage for raw PDFs, S3-compatible
- **Queue**: BullMQ + Redis for async ingestion jobs (5-10min per 100-page doc)
- **AI**: OpenAI GPT-4 Turbo for extraction + embeddings (text-embedding-3-large), Anthropic Claude for Q&A with 200k context
- **Observability**: OpenTelemetry → Tempo + Prometheus + Grafana

## Key Engineering Concerns
- **Chunking Strategy**: Recursive split with 512-token overlap, preserves section headers as metadata
- **Idempotency**: SHA-256 content hash stored in `documents` table; skip re-processing
- **Backpressure**: BullMQ rate limiting (10 jobs/min to avoid OpenAI 429s), priority queue for user-uploaded vs bulk imports
- **Partial Failures**: Store extraction errors in `processing_logs`, mark doc status as `partial`, allow manual retry
- **Pagination**: Cursor-based on `created_at` + `id` composite key for stable ordering
- **Schema Migrations**: Prisma versioned migrations with rollback scripts in CI

## AI System Details
- **Extraction**: Structured output with JSON schema validation (zod), fallback to regex for dates/amounts
- **RAG Pipeline**: Hybrid search (0.7 * vector + 0.3 * full-text BM25), rerank top 20 → top 5 with Cohere
- **Citation Tracking**: Return chunk IDs + page numbers, highlight in PDF viewer
- **Evals**: Golden dataset of 50 Q&A pairs, measure answer accuracy (GPT-4-as-judge @ 0.85 agreement), citation precision/recall
- **Latency Target**: p95 < 3s for Q&A (including DB fetch + LLM call)
- **Cost Target**: <$0.10 per document ingestion, <$0.02 per query

## Prompts for Claude Code Pairing

### a) Scaffold
```
Create a Turborepo monorepo with:
- apps/web: Next.js 14 with App Router, TypeScript, Tailwind CSS, shadcn/ui
- apps/api: Node.js + Fastify + TypeScript
- packages/db: Prisma with Postgres, configured for pgvector extension
- packages/shared: Zod schemas for validation
- Root-level .eslintrc, .prettierrc, turbo.json for caching
- Dockerfiles for web and api with multi-stage builds
- docker-compose.yml with postgres, redis, and pgvector setup
```

### b) Contracts
```
Write OpenAPI 3.1 spec (openapi.yaml) with these endpoints:
- POST /documents/upload (multipart PDF)
- GET /documents (cursor pagination with limit/cursor query params)
- GET /documents/{id}/status (processing state)
- POST /query (question + optional doc filters)
Use openapi-typescript to generate types in packages/shared.
Create a GraphQL schema (schema.graphql) for subscriptions to document processing status.
Generate typed Apollo Client hooks.
```

### c) Data
```
Design Prisma schema with:
- Document table (id, s3_key, content_hash, status enum, metadata jsonb, created_at)
- Chunk table (id, document_id, content, embedding vector(3072), page_num, tokens)
- Query table (id, question, answer, chunks_used jsonb, latency_ms, cost_usd)
- ProcessingLog table (document_id, stage, error, retries)
Enable pgvector, create indexes on embedding (ivfflat), content (GIN for full-text).
Write migrations in prisma/migrations/.
Create seed.ts with Faker to generate 100 sample legal docs (use lorem + structured metadata).
```

### d) Workers
```
Add BullMQ queue in packages/queue with Redis connection.
Implement DocumentIngestionJob:
1. Download PDF from S3
2. Extract text with pdf-parse, metadata with GPT-4 (structured output)
3. Chunk with langchain RecursiveCharacterTextSplitter
4. Embed chunks with OpenAI (batch 100 at a time)
5. Store in DB with transaction
Make job idempotent using content_hash check.
Add retry logic (3 attempts, exponential backoff 1/2/4 min).
Implement dead-letter queue for permanent failures.
Add rate limiting (10 jobs/min).
```

### e) Tests
```
Set up Jest in apps/api with ts-jest.
Write unit tests for:
- chunking logic (test overlap preservation)
- idempotency check (duplicate hash rejection)
Write integration test for /query endpoint:
- Seed test DB with 5 docs + embeddings
- Assert query returns correct chunks and citations
- Mock OpenAI with msw
Set up pytest in a python/ folder if using FastAPI alternative.
Create k6 load test (load-test.js) for 100 concurrent queries, assert p95 < 3s.
```

### f) AI
```
Implement RAG pipeline in packages/ai:
- hybridSearch(query): combine pgvector similarity + pg full-text search
- rerank(chunks): call Cohere rerank API
- generateAnswer(question, chunks): call Claude with citation instructions
Create eval harness in eval/:
- Load golden-dataset.jsonl (50 Q&A pairs with expected chunks)
- For each question, run pipeline, compare answer with GPT-4-as-judge
- Measure citation precision/recall against expected chunks
- Output scores to eval-results.json
Add target: accuracy >= 0.85, citation recall >= 0.8.
```

### g) CI/CD
```
Create .github/workflows/ci.yml:
- On PR: run turbo lint, test, build
- Check Jest coverage >= 80% (fail if below)
- Run eval harness, fail if accuracy < 0.85
- On main merge: build Docker images, push to GHCR
- Tag with git SHA and 'latest'
Create .github/workflows/deploy.yml for optional cloud deploy (show structure only).
Add dependabot.yml for package updates.
```

### h) Instrumentation
```
Integrate OpenTelemetry in apps/api:
- @opentelemetry/sdk-node with auto-instrumentation
- Export traces to Tempo (local docker-compose endpoint)
- Export metrics (request count, latency histogram, queue depth) to Prometheus
Create custom spans for:
- Document ingestion (tag with document_id, page_count)
- Query pipeline (tag with question hash, chunks_retrieved)
Write grafana/dashboard.json with panels:
- Request latency p50/p95/p99
- Queue depth over time
- AI cost per hour (from query table)
- Error rate by endpoint
Add docker-compose services for Tempo, Prometheus, Grafana.
```

## Success Metrics
- Ingest 1000 documents in <2 hours
- Query latency p95 < 3s under 50 QPS
- Eval accuracy >= 0.85 on golden set
- Zero data loss on worker crashes (BullMQ durability)
- 80%+ test coverage
