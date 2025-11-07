# Project 3: Code Review Assistant - Build & Deployment Guide

## Pre-requisites

```bash
# Required tools
node >= 20.x
docker & docker-compose
pnpm (or npm/yarn)
GitHub account (for OAuth app and webhook testing)

# Required API keys (add to .env)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...  # for o1-preview security reviews
VOYAGE_API_KEY=...  # for code embeddings
DATABASE_URL=postgresql://...
REDIS_URL=redis://localhost:6379
GITHUB_APP_ID=...
GITHUB_PRIVATE_KEY=...
GITHUB_WEBHOOK_SECRET=...
```

---

## Build Steps with Validation

### Step 1: Scaffold (Prompt a)

**Validation checklist:**
```bash
# 1. Check structure
ls -la
# Should see: apps/web, apps/api, packages/analyzer, packages/db

# 2. Install deps
pnpm install

# 3. Start Docker
docker-compose up -d postgres redis

# 4. Verify tree-sitter bindings
cd packages/analyzer
node -e "const Parser = require('tree-sitter'); console.log('✓')"

# 5. Build
pnpm build

# 6. Start dev
pnpm dev
# web: http://localhost:3000 (NextAuth login)
# api: http://localhost:3002/webhooks/github
```

**Expected:** ✅ Monorepo built, tree-sitter installed, servers running

---

### Step 2: Contracts (Prompt b)

**Validation checklist:**
```bash
# 1. Check OpenAPI spec
cat openapi.yaml | grep "/repos/{owner}/{repo}/prs"

# 2. Generate types
cd packages/shared
pnpm generate

# 3. Test GitHub webhook signature validation
curl -X POST http://localhost:3002/webhooks/github \
  -H "X-Hub-Signature-256: sha256=..." \
  -H "X-GitHub-Event: pull_request" \
  -d @test-webhook.json
# Should return 401 (invalid signature) or 200 (valid)

# 4. Verify GraphQL subscriptions
cat schema.graphql | grep "reviewStatusChanged"
```

**Expected:** ✅ Webhook endpoint validates signatures, types generated

---

### Step 3: Data (Prompt c)

**Validation checklist:**
```bash
# 1. Run migrations
cd packages/db
npx prisma migrate dev

# 2. Verify tables
npx prisma studio
# Should see: Repository, PullRequest, Review, Finding, CodeEmbedding

# 3. Check pgvector
psql $DATABASE_URL -c "SELECT * FROM pg_extension WHERE extname='vector';"

# 4. Check indexes
psql $DATABASE_URL -c "\d code_embeddings"
# Should show: embedding_idx (ivfflat)

# 5. Run seed
npx tsx seed.ts

# 6. Verify seed data
psql $DATABASE_URL -c "SELECT COUNT(*) FROM pull_requests;"
# Should return: 200
```

**Expected:** ✅ Schema migrated, pgvector enabled, seed data loaded

---

### Step 4: Workers (Prompt d)

**Validation checklist:**
```bash
# 1. Start worker
cd apps/api
pnpm worker
# Should show: BullMQ worker started

# 2. Trigger manual review
curl -X POST http://localhost:3002/repos/owner/repo/prs/123/review

# 3. Check job processing
redis-cli LLEN "bull:pr-analysis:active"
# Should go from 1 → 0 as job completes

# 4. Verify findings stored
psql $DATABASE_URL -c "SELECT type, severity, message FROM findings WHERE pr_id = (SELECT id FROM pull_requests WHERE number = 123);"
# Should return: list of findings

# 5. Test idempotency
# Trigger same review twice
# Should skip re-analysis or return cached results

# 6. Test incremental analysis
# Simulate force-push (new commit on same PR)
# Should only analyze changed files

# 7. Check blast radius calculation
psql $DATABASE_URL -c "SELECT * FROM findings WHERE message LIKE '%blast radius%';"
# Should show: usage counts for modified functions
```

**Expected:** ✅ Worker analyzes PRs, stores findings, handles incremental updates

---

### Step 5: Tests (Prompt e)

**Validation checklist:**
```bash
# 1. Run unit tests
cd apps/api
pnpm test:unit
# Should pass: tree-sitter parsing, finding deduplication, blast radius calc

# 2. Test tree-sitter with real code
cd packages/analyzer
node -e "
const { parseFile } = require('./index');
const ast = parseFile('function test() { return 42; }', 'typescript');
console.log(ast.rootNode.type);  // 'program'
"

# 3. Run integration tests
cd apps/api
pnpm test:integration
# Should pass: PR review flow, incremental review

# 4. Check coverage
pnpm test:coverage
# Should show: ≥80%

# 5. Run load test
k6 run tests/load-test.js
# Should show: p95 < 10s for small PRs
```

**Expected:** ✅ Tests pass, coverage meets target, load test succeeds

---

### Step 6: AI (Prompt f)

**Validation checklist:**
```bash
# 1. Test code parsing
cd packages/analyzer
node -e "
const { CodeAnalyzer } = require('./index');
const analyzer = new CodeAnalyzer();
analyzer.parseFile('const x = 1; x = 2;', 'typescript').then(ast => {
  console.log('AST nodes:', ast.rootNode.descendantCount);
});
"

# 2. Test code embedding
node -e "
const { embedFunctions } = require('./index');
embedFunctions([
  {name: 'calculateTotal', code: 'function calculateTotal(a,b) { return a+b; }'}
]).then(embeddings => {
  console.log('Embedding dim:', embeddings[0].length);  // 512
});
"

# 3. Test AI review
curl -X POST http://localhost:3002/repos/test/repo/prs/1/review

# Wait for completion, then check findings
curl http://localhost:3002/reviews/{review_id} | jq '.findings'
# Should show: array of {type, severity, line_start, message, suggested_fix}

# 4. Verify fix suggestions have diffs
curl http://localhost:3002/reviews/{review_id} | jq '.findings[0].suggested_fix'
# Should show: unified diff format (@@, -, +)

# 5. Run eval harness
cd eval
node run-eval.js

# 6. Check results
cat eval-results.json | jq '.metrics'
# Should show:
# {
#   "bug_detection_f1": 0.78,
#   "security_detection_f1": 0.81,
#   "overall_f1": 0.76,
#   "false_positive_rate": 0.18,
#   "acceptance_rate": 0.52
# }

# 7. Verify meets targets
# F1 >= 0.75: ✓
# FP rate <= 0.20: ✓
# Acceptance >= 0.50: ✓
```

**Expected:** ✅ AI pipeline works, evals meet all targets

---

### Step 7: CI/CD (Prompt g)

**Validation checklist:**
```bash
# 1. Check workflows
ls .github/workflows/
# Should see: ci.yml, release.yml, deploy.yml

# 2. Test locally
act pull_request -j ci

# 3. Push to GitHub
git add . && git commit -m "Test CI" && git push

# 4. Verify CI steps
# GitHub Actions should show:
# - Lint ✓
# - Test (coverage >= 80%) ✓
# - Eval (F1 >= 0.75, FP <= 0.2) ✓
# - Build Docker images ✓

# 5. Test Docker images
docker build -f apps/api/Dockerfile -t code-review-api .
docker run -p 3002:3002 code-review-api

# 6. Verify smoke test
# CI should run: trigger review on test repo, assert completion
```

**Expected:** ✅ CI runs all checks, gates enforce quality, Docker builds

---

### Step 8: Instrumentation (Prompt h)

**Validation checklist:**
```bash
# 1. Start observability stack
docker-compose up -d tempo prometheus grafana

# 2. Make test requests
# Trigger 5 reviews
for i in {1..5}; do
  curl -X POST http://localhost:3002/repos/test/repo/prs/$i/review
done

# 3. Check traces in Grafana
# Open: http://localhost:3001
# Tempo → Search for: analyze_pr
# Should see: 5 traces with tags (repo, pr_number, loc)

# 4. Verify custom spans
# Click trace → Expand spans
# Should see: parse_file, ai_review, blast_radius

# 5. Check metrics in Prometheus
# Open: http://localhost:9090
# Query: review_duration_seconds
# Should show: histogram buckets

# 6. Import dashboard
# Grafana → Import → grafana/dashboard.json
# Should show 5 panels:
# - Latency heatmap (by LOC bucket)
# - Findings by type/severity
# - AI cost per day
# - Fix acceptance rate
# - Queue depth

# 7. Generate load and watch
k6 run tests/load-test.js --duration 60s
# Dashboard should update in real-time
```

**Expected:** ✅ Traces flowing, metrics populating, dashboard showing data

---

## GitHub App Setup

**Required for production:**

```bash
# 1. Create GitHub App
# Go to: GitHub → Settings → Developer settings → GitHub Apps → New
# Set:
# - Name: "AI Code Reviewer"
# - Webhook URL: https://your-api.com/webhooks/github
# - Webhook secret: (generate random, add to .env)
# - Permissions:
#   - Pull requests: Read & Write
#   - Contents: Read
# - Subscribe to events: pull_request, pull_request_review

# 2. Install app on repo
# GitHub App page → Install App → Select repositories

# 3. Download private key
# Save to: apps/api/github-app-key.pem
# Add to .env: GITHUB_PRIVATE_KEY=$(cat github-app-key.pem)

# 4. Test webhook delivery
# Go to: Settings → Webhooks → Recent Deliveries
# Should see: successful deliveries (green checkmark)
```

---

## Complete Health Check

```bash
#!/bin/bash

# 1. Services running
docker ps | grep -E "postgres|redis|tempo" | wc -l  # 3

# 2. API health
curl http://localhost:3002/health  # {"status":"ok"}

# 3. Worker active
redis-cli LLEN "bull:pr-analysis:active"  # 0 (idle)

# 4. Database populated
psql $DATABASE_URL -c "SELECT COUNT(*) FROM repositories;"  # >0

# 5. GitHub webhook reachable (use ngrok for local)
ngrok http 3002
# Update GitHub App webhook URL to ngrok URL
# Trigger test PR → Should see webhook delivered

# 6. Review completes
curl -X POST http://localhost:3002/repos/test/repo/prs/1/review
# Wait 10s, check status
curl http://localhost:3002/reviews/{id} | jq '.status'  # "completed"

# 7. Eval passing
cat eval/eval-results.json | jq '.metrics.overall_f1 >= 0.75'  # true

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

# Deploy services
railway up --service api
railway up --service worker

# Set environment
railway variables set ANTHROPIC_API_KEY=sk-ant-...
railway variables set GITHUB_APP_ID=123456
railway variables set GITHUB_PRIVATE_KEY="$(cat github-app-key.pem)"
railway variables set GITHUB_WEBHOOK_SECRET=...

# Migrate DB
railway run npx prisma migrate deploy

# Update GitHub App webhook URL
# Set to: https://{your-api}.railway.app/webhooks/github

# Deploy web to Vercel
cd apps/web
vercel --prod
# Set env vars: NEXTAUTH_SECRET, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
```

### Docker VPS

```bash
# On server
git clone {repo} && cd {repo}
cp .env.example .env
# Fill in: API keys, GitHub app credentials

docker-compose -f docker-compose.prod.yml up -d
docker-compose exec api npx prisma migrate deploy
docker-compose exec api npx tsx seed.ts

# Setup nginx
# Proxy: your-domain.com → localhost:3002

# Update GitHub App webhook
# Set to: https://your-domain.com/webhooks/github
```

---

## Production Smoke Tests

```bash
# 1. Health check
curl https://api.yourdomain.com/health

# 2. Trigger review via GitHub
# Open PR on installed repo → Should auto-trigger review

# 3. Check review status
curl https://api.yourdomain.com/repos/{owner}/{repo}/reviews | jq '.[0].status'
# → "completed"

# 4. Verify findings posted to GitHub
# Go to PR → Files changed → Should see inline comments from bot

# 5. Test fix suggestion
# Click "Commit suggestion" on a comment
# Check acceptance rate metric in Grafana

# 6. Load test (staging)
k6 run load-test.js --duration 5m --vus 20
# → p95 < 10s for small PRs
```

---

## Monitoring Production

```bash
# Check review latency by PR size
curl https://grafana.yourdomain.com/api/datasources/proxy/1/query \
  -d 'query=histogram_quantile(0.95, rate(review_duration_seconds_bucket[5m]))'

# Check AI costs
psql $DATABASE_URL -c "
SELECT DATE_TRUNC('day', created_at) as day,
       SUM((metadata->>'tokens_in')::int * 0.000003 +
           (metadata->>'tokens_out')::int * 0.000015) as cost_usd
FROM findings
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY day;
"

# Check error rate
redis-cli LLEN "bull:pr-analysis:failed"
```

---

## Success Criteria

- [ ] All validation checklists pass
- [ ] GitHub App installed and receiving webhooks
- [ ] Review completes on test PR with findings
- [ ] Findings posted as GitHub comments
- [ ] Eval F1 ≥ 0.75, FP ≤ 20%, acceptance ≥ 50%
- [ ] Load test: p95 < 10s (small PRs)
- [ ] Coverage ≥ 80%
- [ ] CI passes
- [ ] Production deployed
- [ ] Grafana dashboard live

**Estimated time:** 14-18 hours

---

## Troubleshooting

### Webhook not received
```bash
# Check ngrok/public URL
curl https://your-api.com/health

# Check GitHub webhook logs
# Settings → Webhooks → Recent Deliveries → Redeliver

# Check API logs
docker-compose logs -f api | grep webhook
```

### Tree-sitter parsing fails
```bash
# Verify language bindings installed
ls node_modules/tree-sitter-{typescript,python}

# Test parsing manually
node -e "
const Parser = require('tree-sitter');
const TypeScript = require('tree-sitter-typescript').typescript;
const parser = new Parser();
parser.setLanguage(TypeScript);
console.log(parser.parse('const x = 1;').rootNode);
"
```

### High AI costs
```bash
# Cache embeddings for frequently accessed code
# Batch API calls (review 100 functions together)
# Use cheaper models for initial triage (GPT-4o-mini)
# Only use o1-preview for security-critical files
```

Good luck! 🚀
