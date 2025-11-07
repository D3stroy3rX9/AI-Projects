# Project 2: Support Triage System - Build & Deployment Guide

## Pre-requisites

```bash
# Required tools
node >= 20.x
python >= 3.11
docker & docker-compose
pnpm (or npm/yarn)

# Required API keys (add to .env)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://...
REDIS_URL=redis://localhost:6379
```

---

## Build Steps with Validation

### Step 1: Scaffold (Prompt a)

**Paste prompt (a) into Claude Code**

**Validation checklist:**
```bash
# 1. Check structure
ls -la
# Should see: apps/, packages/, turbo.json, docker-compose.yml

# 2. Install dependencies
pnpm install

# 3. Start Docker services
docker-compose up -d postgres redis

# 4. Verify services
docker ps
# Should show: postgres:16, redis:7 running

# 5. Test builds
pnpm build
# Should compile apps/web and apps/api without errors

# 6. Start dev servers
pnpm dev
# web: http://localhost:3000
# api: http://localhost:8000/docs (should see "Not Found" or basic response)
```

**Expected output:**
- ✅ Monorepo structure created
- ✅ Dependencies installed
- ✅ Docker services running
- ✅ Dev servers start without errors

**Troubleshooting:**
- If `pnpm install` fails → Check Node version, try `npm install`
- If Docker fails → Check ports 5432, 6379 not in use
- If build fails → Check TypeScript/Python versions

---

### Step 2: Contracts (Prompt b)

**Paste prompt (b) into Claude Code**

**Validation checklist:**
```bash
# 1. Check OpenAPI spec exists
cat openapi.yaml | head -20
# Should see: openapi: 3.1.0, paths, schemas

# 2. Generate TypeScript types
cd packages/contracts
pnpm generate-types
# Should create: generated/api-types.ts

# 3. Verify Pydantic models
cd apps/api
python -c "from models import TicketCreate; print(TicketCreate.model_fields)"
# Should print: {'subject': ..., 'body': ...}

# 4. Test contract validation
curl -X POST http://localhost:8000/webhooks/ticket \
  -H "Content-Type: application/json" \
  -d '{"subject":"test","body":"test"}'
# Should return 200 or validation error (not 404)
```

**Expected output:**
- ✅ openapi.yaml with all endpoints
- ✅ TypeScript types generated
- ✅ Pydantic models importable
- ✅ API accepts requests (even if returns errors)

**Troubleshooting:**
- If type generation fails → Check openapi.yaml syntax with validator
- If Pydantic import fails → Check pyproject.toml dependencies

---

### Step 3: Data (Prompt c)

**Paste prompt (c) into Claude Code**

**Validation checklist:**
```bash
# 1. Check Alembic migrations
ls apps/api/alembic/versions/
# Should see: 0001_initial.py or similar

# 2. Run migrations
cd apps/api
alembic upgrade head
# Should show: Running upgrade -> 0001

# 3. Verify tables created
psql $DATABASE_URL -c "\dt"
# Should list: tickets, ticket_messages, agent_actions, knowledge_articles

# 4. Check pgvector extension
psql $DATABASE_URL -c "SELECT * FROM pg_extension WHERE extname='vector';"
# Should return 1 row

# 5. Run seed script
python seed.py
# Should insert 500 tickets, 100 articles

# 6. Verify seed data
psql $DATABASE_URL -c "SELECT COUNT(*) FROM tickets;"
# Should return: 500
```

**Expected output:**
- ✅ Migrations run successfully
- ✅ All tables created with indexes
- ✅ pgvector extension enabled
- ✅ Seed data inserted

**Troubleshooting:**
- If migration fails → Check DATABASE_URL, ensure Postgres 16+
- If pgvector fails → Run `CREATE EXTENSION vector;` manually
- If seed fails → Check Faker version, API keys in .env

---

### Step 4: Workers (Prompt d)

**Paste prompt (d) into Claude Code**

**Validation checklist:**
```bash
# 1. Check Celery tasks defined
cat apps/api/workers/tasks.py | grep "def classify_ticket_task"
# Should see function definition

# 2. Start Celery worker
cd apps/api
celery -A workers worker --loglevel=info
# Should show: [tasks] - classify_ticket_task, attempt_resolution_task

# 3. In another terminal, test task dispatch
python -c "
from workers.tasks import classify_ticket_task
result = classify_ticket_task.delay(1)
print(result.id)
"
# Should print task ID

# 4. Check task execution in worker logs
# Worker terminal should show: Task classify_ticket_task[...] succeeded

# 5. Verify ticket updated in DB
psql $DATABASE_URL -c "SELECT priority, category FROM tickets WHERE id=1;"
# Should show classified values (not null)

# 6. Test idempotency
# Run same task twice, check only 1 AgentAction created
psql $DATABASE_URL -c "SELECT COUNT(*) FROM agent_actions WHERE ticket_id=1 AND agent_type='classifier';"
# Should return: 1 (not 2)
```

**Expected output:**
- ✅ Celery worker starts and registers tasks
- ✅ Tasks execute successfully
- ✅ Ticket data updated in DB
- ✅ Idempotency works (no duplicate actions)

**Troubleshooting:**
- If worker fails to start → Check Redis connection, REDIS_URL in .env
- If task fails → Check API keys, OpenAI/Anthropic quotas
- If idempotency fails → Check unique constraint on agent_actions table

---

### Step 5: Tests (Prompt e)

**Paste prompt (e) into Claude Code**

**Validation checklist:**
```bash
# 1. Run unit tests
cd apps/api
pytest tests/unit -v
# Should pass: test_classification_schema, test_idempotency, test_pagination

# 2. Run integration tests
pytest tests/integration -v
# Should pass: test_webhook_flow, test_rag_resolution

# 3. Check coverage
pytest --cov=. --cov-report=html
# Should show: >80% coverage, generates htmlcov/index.html

# 4. Run load test
cd ../..
k6 run locustfile.py --duration 30s --vus 50
# Should show: p95 < 500ms, 0 failed requests

# 5. Verify no regressions
# Check worker logs during load test - no errors
```

**Expected output:**
- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ Coverage ≥ 80%
- ✅ Load test p95 < 500ms

**Troubleshooting:**
- If tests fail → Check test DB setup, mock configurations
- If load test fails → Increase worker count, check rate limits
- If coverage low → Add tests for uncovered branches

---

### Step 6: AI (Prompt f)

**Paste prompt (f) into Claude Code**

**Validation checklist:**
```bash
# 1. Test ClassifierAgent
cd apps/api
python -c "
from agents import ClassifierAgent
result = ClassifierAgent.classify({'subject': 'Cannot login', 'body': 'Password reset not working'})
print(result)
"
# Should print: {'urgency': 'high', 'category': 'account', 'sentiment': 'negative'}

# 2. Test ResolverAgent with RAG
python -c "
from agents import ResolverAgent
result = ResolverAgent.resolve(1)  # ticket_id from seed data
print(result['confidence'], result['answer'][:100])
"
# Should print confidence (0.0-1.0) and answer preview

# 3. Run eval harness
python eval/run_eval.py
# Should generate eval-results.json

# 4. Check eval results
cat eval/eval-results.json | jq '.overall'
# Should show: {\"f1\": 0.91, \"false_positive_rate\": 0.04}

# 5. Verify meets targets
# F1 >= 0.9: ✓
# FP rate <= 0.05: ✓

# 6. Test end-to-end flow
curl -X POST http://localhost:8000/webhooks/ticket \
  -H "Content-Type: application/json" \
  -H "X-Signature: test-sig" \
  -d '{
    "external_id": "TEST-001",
    "subject": "Billing issue",
    "body": "Double charged this month"
  }'
# Should return 202, trigger classification + resolution
# Check worker logs for agent execution
```

**Expected output:**
- ✅ Agents execute successfully
- ✅ Eval harness runs without errors
- ✅ F1 ≥ 0.9, FP rate ≤ 0.05
- ✅ End-to-end webhook → classification → resolution works

**Troubleshooting:**
- If agents fail → Check API keys, model availability
- If eval fails → Check golden-tickets.jsonl format, ensure 200 samples
- If confidence always low → Adjust prompt, check RAG retrieval

---

### Step 7: CI/CD (Prompt g)

**Paste prompt (g) into Claude Code**

**Validation checklist:**
```bash
# 1. Check workflow files exist
ls .github/workflows/
# Should see: test.yml, build.yml, deploy.yml

# 2. Test workflow locally (using act)
act pull_request -j test
# Should run: lint, test, eval, coverage check

# 3. Commit and push to trigger real CI
git add .
git commit -m "Test CI pipeline"
git push

# 4. Check GitHub Actions UI
# Go to: https://github.com/{user}/{repo}/actions
# Should see: workflow running, all steps green

# 5. Verify coverage gate
# If coverage < 80%, workflow should fail

# 6. Verify eval gate
# If F1 < 0.9, workflow should fail

# 7. Test Docker build
docker build -f apps/api/Dockerfile -t support-triage-api .
docker run -p 8000:8000 support-triage-api
# Should start API in container
```

**Expected output:**
- ✅ Workflows created
- ✅ CI runs on push/PR
- ✅ Gates enforce coverage and eval thresholds
- ✅ Docker images build successfully

**Troubleshooting:**
- If workflow fails → Check syntax with actionlint
- If Docker build fails → Check Dockerfile COPY paths, .dockerignore
- If gates too strict → Adjust thresholds in workflow

---

### Step 8: Instrumentation (Prompt h)

**Paste prompt (h) into Claude Code**

**Validation checklist:**
```bash
# 1. Start observability stack
docker-compose up -d tempo prometheus grafana
# Should start 3 services on ports: 3200, 9090, 3001

# 2. Verify OpenTelemetry exports
# Make a test request
curl -X POST http://localhost:8000/webhooks/ticket \
  -H "Content-Type: application/json" \
  -d '{"external_id":"OBS-001","subject":"test","body":"test"}'

# 3. Check traces in Tempo
# Open: http://localhost:3001 (Grafana)
# Login: admin/admin
# Explore → Tempo → Search for traces
# Should see: 'classify_ticket' span

# 4. Check metrics in Prometheus
# Open: http://localhost:9090
# Query: http_requests_total
# Should show request counts

# 5. Import Grafana dashboard
# Grafana → Dashboards → Import → Upload grafana/dashboard.json
# Should show 5 panels with data

# 6. Trigger load and watch dashboard
k6 run locustfile.py --duration 60s --vus 100
# Dashboard should show:
# - Latency p95 graph updating
# - Queue depth increasing/decreasing
# - AI cost accumulating
# - Error rate (should be ~0)

# 7. Verify custom spans
# Check Tempo trace details, should include:
# - ticket_id tags
# - priority tags
# - confidence values
```

**Expected output:**
- ✅ Observability stack running
- ✅ Traces visible in Tempo
- ✅ Metrics in Prometheus
- ✅ Grafana dashboard populating
- ✅ Custom spans with tags

**Troubleshooting:**
- If no traces → Check OTEL_EXPORTER_OTLP_ENDPOINT in .env
- If dashboard empty → Check Prometheus scrape config, data source in Grafana
- If spans missing → Check OpenTelemetry instrumentation initialization

---

## Complete Health Check

After all 8 steps, run this comprehensive test:

```bash
#!/bin/bash
# health-check.sh

echo "=== Health Check ==="

# 1. Services up
docker ps | grep -E "postgres|redis|tempo|prometheus|grafana" | wc -l
# Expected: 5

# 2. API responding
curl -f http://localhost:8000/health
# Expected: {"status":"ok"}

# 3. Database accessible
psql $DATABASE_URL -c "SELECT COUNT(*) FROM tickets;" | grep -E "[0-9]+"
# Expected: number > 0

# 4. Worker processing
celery -A workers inspect active | grep classify_ticket_task
# Expected: active tasks or empty (ok)

# 5. Eval passing
python eval/run_eval.py && cat eval/eval-results.json | jq '.overall.f1 >= 0.9'
# Expected: true

# 6. Traces flowing
curl http://localhost:9090/api/v1/query?query=http_requests_total | jq '.data.result | length'
# Expected: > 0

echo "=== All checks passed ==="
```

---

## Deployment Guide

### Option 1: Railway (Recommended)

```bash
# 1. Install Railway CLI
npm i -g @railway/cli

# 2. Login
railway login

# 3. Create project
railway init

# 4. Add services
railway add --service postgres
railway add --service redis

# 5. Deploy API
cd apps/api
railway up --service api

# 6. Deploy worker
railway up --service worker

# 7. Set environment variables
railway variables set OPENAI_API_KEY=sk-...
railway variables set ANTHROPIC_API_KEY=sk-ant-...

# 8. Run migrations
railway run alembic upgrade head

# 9. Deploy frontend to Vercel
cd ../web
vercel --prod

# 10. Test production
curl https://{your-api}.railway.app/health
```

### Option 2: Docker Compose (VPS)

```bash
# 1. SSH to VPS
ssh user@your-server.com

# 2. Clone repo
git clone {your-repo}
cd {repo}

# 3. Set environment variables
cp .env.example .env
nano .env  # Add API keys

# 4. Start all services
docker-compose -f docker-compose.prod.yml up -d

# 5. Run migrations
docker-compose exec api alembic upgrade head

# 6. Check logs
docker-compose logs -f api worker

# 7. Set up reverse proxy (nginx)
# Point domain to port 8000

# 8. Enable SSL (certbot)
certbot --nginx -d api.yourdomain.com
```

### Option 3: Kubernetes (Advanced)

See `k8s/` directory for manifests (if you want me to create these).

---

## Production Smoke Tests

```bash
# 1. Health endpoint
curl https://your-api.com/health
# Expected: {"status":"ok","version":"1.0.0"}

# 2. Create ticket via webhook
curl -X POST https://your-api.com/webhooks/ticket \
  -H "Content-Type: application/json" \
  -H "X-Signature: {hmac}" \
  -d @test-ticket.json
# Expected: 202 Accepted

# 3. Wait 5 seconds, check classification
curl https://your-api.com/tickets/{id}
# Expected: priority and category populated

# 4. Check Grafana dashboard
# Open: https://grafana.yourdomain.com
# Verify: metrics flowing, no errors

# 5. Load test (staging only!)
k6 run load-test.js --duration 5m --vus 50
# Expected: p95 < 500ms, error rate < 0.1%
```

---

## Troubleshooting Production

### Issue: High latency (p95 > 1s)

```bash
# Check worker count
celery -A workers inspect stats | jq '.[] | .pool.max-concurrency'
# Increase if < 10

# Check Redis memory
redis-cli INFO memory | grep used_memory_human
# Scale if > 80% of max

# Check database slow queries
psql $DATABASE_URL -c "SELECT query, mean_exec_time FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"
# Add indexes if needed
```

### Issue: Tasks failing

```bash
# Check dead-letter queue
celery -A workers inspect reserved | jq '.["celery@{host}"].dead_letter'

# Retry failed tasks
celery -A workers call {task_id} --retry

# Check API quotas
curl https://api.openai.com/v1/usage
```

### Issue: Eval regression

```bash
# Run eval locally
python eval/run_eval.py --verbose

# Compare to baseline
diff eval-results.json eval-baseline.json

# Check for prompt drift
git diff HEAD~10 apps/api/agents/classifier.py
```

---

## Success Criteria

You're done when:

- [ ] All 8 validation checklists pass
- [ ] `health-check.sh` returns all green
- [ ] Load test: p95 < 500ms @ 50 concurrent users
- [ ] Eval: F1 ≥ 0.9, FP rate ≤ 0.05
- [ ] Coverage ≥ 80%
- [ ] CI passes on GitHub Actions
- [ ] Production deployed and accessible
- [ ] Grafana dashboard shows live metrics
- [ ] No errors in logs for 10 minutes

**Estimated total time:** 12-16 hours (including debugging)

---

## Next Steps After Completion

1. **Blog post**: Document cost optimizations, eval improvements
2. **Video demo**: Show real-time classification + dashboard
3. **Add features**:
   - Multi-language support (translation agent)
   - Sentiment analysis trends over time
   - Auto-categorize knowledge articles from resolved tickets
4. **Scale test**: Push to 5000 tickets/hour
5. **Cost optimization**: Cache embeddings, batch API calls

Good luck! 🚀
