# Project 1: Legal Document Intelligence - Build & Deployment Guide

## Pre-requisites

```bash
# Required tools
node >= 20.x
docker & docker-compose
pnpm (or npm/yarn)

# Required API keys (add to .env)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
COHERE_API_KEY=...  # for reranking
DATABASE_URL=postgresql://...
REDIS_URL=redis://localhost:6379
SUPABASE_URL=https://...
SUPABASE_KEY=...
```

---

## Build Steps with Validation

### Step 1: Scaffold (Prompt a)

**Validation checklist:**
```bash
# 1. Check structure
ls -la
# Should see: apps/, packages/, turbo.json, docker-compose.yml

# 2. Install dependencies
pnpm install

# 3. Start services (postgres with pgvector, redis)
docker-compose up -d

# 4. Verify pgvector
docker exec -it postgres psql -U postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 5. Test builds
pnpm build

# 6. Start dev
pnpm dev
# web: http://localhost:3000
# api: http://localhost:3001/docs
```

**Expected:** ✅ Monorepo built, Docker services running, dev servers start

---

### Step 2: Contracts (Prompt b)

**Validation checklist:**
```bash
# 1. Check OpenAPI spec
cat openapi.yaml | grep -A 5 "/documents/upload"

# 2. Generate types
cd packages/shared
pnpm generate

# 3. Verify types exist
cat generated/api-types.ts | grep "DocumentStatus"

# 4. Test upload endpoint
curl -X POST http://localhost:3001/documents/upload \
  -F "file=@test.pdf"
# Should return 202 or validation error
```

**Expected:** ✅ Spec defined, types generated, endpoints respond

---

### Step 3: Data (Prompt c)

**Validation checklist:**
```bash
# 1. Run migrations
cd packages/db
npx prisma migrate dev

# 2. Verify tables
npx prisma studio
# Open http://localhost:5555
# Should see: Document, Chunk, Query, ProcessingLog tables

# 3. Check indexes
psql $DATABASE_URL -c "\d chunks"
# Should show: embedding_idx (ivfflat), content_idx (gin)

# 4. Run seed
npx tsx seed.ts

# 5. Verify data
psql $DATABASE_URL -c "SELECT COUNT(*) FROM documents;"
# Should return: 100
```

**Expected:** ✅ Schema migrated, indexes created, seed data inserted

---

### Step 4: Workers (Prompt d)

**Validation checklist:**
```bash
# 1. Start worker
cd apps/api
pnpm worker
# Should show: BullMQ worker started, listening for jobs

# 2. Upload test PDF
curl -X POST http://localhost:3001/documents/upload \
  -F "file=@test-legal-doc.pdf" \
  -H "Content-Type: multipart/form-data"
# Should return: {"job_id": "...", "document_id": "..."}

# 3. Check job status
curl http://localhost:3001/documents/{document_id}/status
# Should show: {"status": "processing"} → "completed"

# 4. Verify chunks created
psql $DATABASE_URL -c "SELECT COUNT(*) FROM chunks WHERE document_id = '{id}';"
# Should return: >0 (number of chunks)

# 5. Test idempotency
# Upload same PDF twice
# Should return: "Document already exists" or skip re-processing

# 6. Check dead-letter queue
redis-cli LLEN "bull:document-ingestion:failed"
# Should return: 0
```

**Expected:** ✅ Worker processes PDFs, creates chunks, handles duplicates

---

### Step 5: Tests (Prompt e)

**Validation checklist:**
```bash
# 1. Run unit tests
cd apps/api
pnpm test:unit
# Should pass: chunking logic, idempotency check

# 2. Run integration tests
pnpm test:integration
# Should pass: /query endpoint, chunk retrieval, citation tracking

# 3. Check coverage
pnpm test:coverage
# Should show: ≥80%

# 4. Run load test
k6 run tests/load-test.js
# Should show: p95 < 3s for queries
```

**Expected:** ✅ Tests pass, coverage ≥80%, load test meets targets

---

### Step 6: AI (Prompt f)

**Validation checklist:**
```bash
# 1. Test hybrid search
node -e "
const { hybridSearch } = require('./packages/ai');
hybridSearch('What are the payment terms?').then(console.log);
"
# Should return: array of chunks with scores

# 2. Test RAG pipeline
curl -X POST http://localhost:3001/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Who are the parties to this contract?"}'
# Should return: {"answer": "...", "citations": [...], "chunks_used": [...]}

# 3. Run eval harness
cd eval
node run-eval.js
# Should generate: eval-results.json

# 4. Check eval results
cat eval-results.json | jq '.metrics'
# Should show: {
#   "answer_accuracy": 0.87,
#   "citation_precision": 0.82,
#   "citation_recall": 0.79
# }

# 5. Verify meets targets
# Accuracy >= 0.85: ✓
# Citation recall >= 0.8: (close, tune prompts if needed)
```

**Expected:** ✅ RAG pipeline works, evals meet targets

---

### Step 7: CI/CD (Prompt g)

**Validation checklist:**
```bash
# 1. Check workflows
ls .github/workflows/
# Should see: ci.yml, deploy.yml

# 2. Test locally (act)
act pull_request

# 3. Push to GitHub
git add . && git commit -m "Test CI" && git push

# 4. Verify CI passes
# Check GitHub Actions: all steps green

# 5. Test Docker build
docker build -f apps/api/Dockerfile -t legal-doc-api .
docker run -p 3001:3001 legal-doc-api
```

**Expected:** ✅ CI runs, gates enforce, Docker builds

---

### Step 8: Instrumentation (Prompt h)

**Validation checklist:**
```bash
# 1. Start observability
docker-compose up -d tempo prometheus grafana

# 2. Make requests
for i in {1..10}; do
  curl -X POST http://localhost:3001/query \
    -H "Content-Type: application/json" \
    -d '{"question": "Test query '$i'"}'
done

# 3. Check Grafana
# Open: http://localhost:3001 (or 3000)
# Import: grafana/dashboard.json
# Should show: latency, queue depth, AI cost

# 4. Verify custom spans
# Tempo → Search traces → Find "query_pipeline"
# Should have tags: question_hash, chunks_retrieved
```

**Expected:** ✅ Traces flowing, dashboard populated

---

## Complete Health Check

```bash
#!/bin/bash
# Check all systems

# 1. Services
docker ps | grep -E "postgres|redis|tempo" | wc -l  # 3

# 2. API health
curl http://localhost:3001/health  # {"status":"ok"}

# 3. Document count
psql $DATABASE_URL -c "SELECT COUNT(*) FROM documents;"  # 100

# 4. Query works
curl -X POST http://localhost:3001/query \
  -H "Content-Type: application/json" \
  -d '{"question":"test"}' | jq '.answer'  # non-empty

# 5. Eval passing
cat eval/eval-results.json | jq '.metrics.answer_accuracy >= 0.85'  # true

echo "✅ All systems operational"
```

---

## Deployment

### Railway + Vercel

```bash
# API & Worker to Railway
railway init
railway add --service postgres
railway add --service redis
railway up --service api
railway up --service worker

railway variables set OPENAI_API_KEY=sk-...
railway variables set ANTHROPIC_API_KEY=sk-ant-...

cd packages/db && railway run npx prisma migrate deploy

# Frontend to Vercel
cd apps/web
vercel --prod
```

### Docker VPS

```bash
# On server
docker-compose -f docker-compose.prod.yml up -d
docker-compose exec api npx prisma migrate deploy
docker-compose exec api npx tsx seed.ts

# Setup nginx reverse proxy
# Point domain → port 3001
```

---

## Production Smoke Tests

```bash
# 1. Upload document
curl -X POST https://api.yourdomain.com/documents/upload \
  -F "file=@sample-contract.pdf"
# → Returns document_id

# 2. Wait for processing (check status endpoint)
curl https://api.yourdomain.com/documents/{id}/status
# → {"status": "completed"}

# 3. Query document
curl -X POST https://api.yourdomain.com/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the termination clause?"}'
# → Returns answer with citations

# 4. Verify citation tracking
# Check response includes: page_num, chunk_id

# 5. Load test (staging)
k6 run load-test.js --duration 5m
# → p95 < 3s
```

---

## Success Criteria

- [ ] All validation checklists pass
- [ ] Upload 10 PDFs → all process successfully
- [ ] Query latency p95 < 3s
- [ ] Eval accuracy ≥ 0.85
- [ ] Coverage ≥ 80%
- [ ] CI passes
- [ ] Production deployed
- [ ] Grafana shows metrics

**Estimated time:** 16-20 hours
