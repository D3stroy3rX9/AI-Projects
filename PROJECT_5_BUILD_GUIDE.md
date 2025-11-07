# Project 5: Sentiment Analysis Dashboard - Build & Deployment Guide

## Pre-requisites

```bash
# Required tools
python >= 3.11
node >= 20.x
docker & docker-compose
pnpm (or npm/yarn)

# No API keys needed! 🎉
# Everything runs locally
```

---

## Build Steps with Validation

### Step 1: Scaffold (Prompt a)

**Paste prompt (a) into Claude Code**

**Validation checklist:**
```bash
# 1. Check structure
ls -la
# Should see: apps/web, apps/api, packages/ml, docker-compose.yml

# 2. Install Python dependencies
cd apps/api
poetry install
# Should install: fastapi, scikit-learn, pandas, numpy, celery, redis

# 3. Install Node dependencies
cd ../web
pnpm install

# 4. Start Docker services
cd ../..
docker-compose up -d
# Should start: postgres, redis

# 5. Verify services running
docker ps
# Should show 2 containers: postgres:16, redis:7

# 6. Test Python imports
cd apps/api
poetry run python -c "from sklearn.naive_bayes import MultinomialNB; print('✓ scikit-learn')"
poetry run python -c "import fastapi; print('✓ FastAPI')"
# Should print: ✓ scikit-learn, ✓ FastAPI

# 7. Start dev servers
cd ../..
# Terminal 1: API
cd apps/api && poetry run uvicorn main:app --reload
# Should start on: http://localhost:8000

# Terminal 2: Web
cd apps/web && pnpm dev
# Should start on: http://localhost:3000

# 8. Test API
curl http://localhost:8000/health
# Expected: {"status":"ok"} or 404 (ok for now)
```

**Expected output:**
- ✅ Monorepo structure created
- ✅ Dependencies installed (no errors)
- ✅ Docker services running
- ✅ Dev servers start successfully
- ✅ No import errors

**Troubleshooting:**
- If `poetry install` fails → Check Python version (3.11+), try `pip install poetry`
- If Docker fails → Check ports 5432, 6379 not in use: `lsof -ti:5432 | xargs kill -9`
- If scikit-learn import fails → Try `poetry add scikit-learn==1.5.0` (specific version)

---

### Step 2: Contracts (Prompt b)

**Paste prompt (b) into Claude Code**

**Validation checklist:**
```bash
# 1. Check OpenAPI spec exists
cat openapi.yaml | head -30
# Should see: openapi: 3.1.0, paths: /analyze, /analytics/trends

# 2. Check Pydantic models generated
cd apps/api
ls models/
# Should see: sentiment.py, analytics.py, training.py

# 3. Verify models importable
poetry run python -c "from models.sentiment import SentimentResult; print(SentimentResult.model_fields)"
# Should print: {'text': ..., 'sentiment': ..., 'emotion': ...}

# 4. Check TypeScript types
cd ../web
cat types/api.ts | grep "SentimentResult"
# Should see: export interface SentimentResult { ... }

# 5. Test contract validation
cd ../api
poetry run python -c "
from models.sentiment import SentimentResult
result = SentimentResult(
    text='test',
    sentiment={'positive': 0.8, 'neutral': 0.1, 'negative': 0.1},
    emotion={},
    explanation={'top_words': []},
    confidence=0.8
)
print('✓ Validation works')
"
# Should print: ✓ Validation works

# 6. Start API and test endpoint structure
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "test"}'
# Expected: 422 (validation error) or 500 (ML not ready) - both OK
# NOT 404 (endpoint exists)
```

**Expected output:**
- ✅ OpenAPI spec with all endpoints
- ✅ Pydantic models generated and importable
- ✅ TypeScript types generated
- ✅ Models validate correctly
- ✅ Endpoints exist (even if not implemented)

**Troubleshooting:**
- If type generation fails → Check openapi.yaml syntax: `yamllint openapi.yaml`
- If Pydantic fails → Check Python 3.11+, try `poetry add pydantic==2.7.0`
- If TypeScript types missing → Run `pnpm run generate-types` manually

---

### Step 3: Data (Prompt c)

**Validation checklist:**
```bash
# 1. Check migrations exist
cd apps/api
ls alembic/versions/
# Should see: 0001_initial_schema.py (or similar)

# 2. Run migrations
poetry run alembic upgrade head
# Should output: Running upgrade -> 0001_initial_schema

# 3. Verify tables created
psql postgresql://postgres:postgres@localhost:5432/sentiment -c "\dt"
# Should list: analysis, models, training_data, analytics_summary

# 4. Check TimescaleDB extension
psql postgresql://postgres:postgres@localhost:5432/sentiment -c "SELECT extname FROM pg_extension WHERE extname='timescaledb';"
# Should return: timescaledb

# 5. Verify hypertable created
psql postgresql://postgres:postgres@localhost:5432/sentiment -c "SELECT hypertable_name FROM timescaledb_information.hypertables;"
# Should return: analysis

# 6. Check indexes
psql postgresql://postgres:postgres@localhost:5432/sentiment -c "\d analysis"
# Should show indexes on: text_hash, analyzed_at, source

# 7. Download datasets (if not included)
cd data/
wget https://ai.stanford.edu/~amaas/data/sentiment/aclImdb_v1.tar.gz
tar -xzf aclImdb_v1.tar.gz
# Or use provided sample data

# 8. Run seed script
cd ../apps/api
poetry run python seed.py
# Should output: Inserted 1000 sample analyses

# 9. Verify seed data
psql postgresql://postgres:postgres@localhost:5432/sentiment -c "SELECT COUNT(*) FROM analysis;"
# Should return: 1000

# 10. Check sentiment distribution
psql postgresql://postgres:postgres@localhost:5432/sentiment -c "
SELECT predicted_label, COUNT(*)
FROM analysis
GROUP BY predicted_label;
"
# Should show: positive: ~400, neutral: ~300, negative: ~300
```

**Expected output:**
- ✅ Migrations run successfully
- ✅ All tables created
- ✅ TimescaleDB extension enabled
- ✅ Hypertable configured on analysis table
- ✅ Indexes created
- ✅ Seed data inserted with realistic distribution

**Troubleshooting:**
- If migration fails → Check DATABASE_URL in .env: `postgresql://postgres:postgres@localhost:5432/sentiment`
- If TimescaleDB fails → Run `docker-compose down -v && docker-compose up -d` (recreate with timescaledb image)
- If seed fails → Check if Stanford Sentiment data downloaded, or use faker to generate synthetic data
- If psql command fails → Install postgresql-client: `apt-get install postgresql-client` or `brew install postgresql`

---

### Step 4: Workers (Prompt d)

**Validation checklist:**
```bash
# 1. Check Celery tasks defined
cd apps/api
cat workers/tasks.py | grep "def train_model_task"
# Should see function definitions

# 2. Start Celery worker
poetry run celery -A workers worker --loglevel=info
# Should show: [tasks] - train_model_task, batch_analyze_task, aggregate_analytics_task

# 3. In another terminal, test task dispatch
cd apps/api
poetry run python -c "
from workers.tasks import batch_analyze_task
texts = ['This is great!', 'This is terrible!']
result = batch_analyze_task.delay(texts, 'api')
print(f'Task ID: {result.id}')
"
# Should print task ID

# 4. Check worker logs
# Worker terminal should show: Task batch_analyze_task[...] succeeded

# 5. Verify data in DB
psql postgresql://postgres:postgres@localhost:5432/sentiment -c "SELECT text, predicted_label FROM analysis ORDER BY analyzed_at DESC LIMIT 2;"
# Should show the 2 texts with predicted labels

# 6. Test training task
poetry run python -c "
from workers.tasks import train_model_task
# Get some training data IDs
import sqlalchemy as sa
from models import TrainingData
# ... (query to get IDs)
result = train_model_task.delay([1, 2, 3, 4, 5])
print(f'Training task: {result.id}')
"
# Should trigger training

# 7. Check model created
ls models/*.joblib
# Should see: {timestamp}-model.joblib

# 8. Test idempotency
# Run batch_analyze with same text twice
poetry run python -c "
from workers.tasks import batch_analyze_task
text = 'Identical text for testing'
batch_analyze_task.delay([text], 'api')
batch_analyze_task.delay([text], 'api')  # Second time
"
# Check DB: only 1 entry (deduped by text_hash)
psql postgresql://postgres:postgres@localhost:5432/sentiment -c "SELECT COUNT(*) FROM analysis WHERE text = 'Identical text for testing';"
# Should return: 1
```

**Expected output:**
- ✅ Celery worker starts and registers tasks
- ✅ Tasks execute successfully
- ✅ Predictions stored in database
- ✅ Model training completes
- ✅ Idempotency works (no duplicate analyses)

**Troubleshooting:**
- If worker fails → Check Redis connection: `redis-cli ping` (should return PONG)
- If tasks fail → Check CELERY_BROKER_URL and CELERY_RESULT_BACKEND in .env
- If training fails → Ensure training data exists: `SELECT COUNT(*) FROM training_data;`
- If idempotency fails → Check text_hash index: `\d analysis` should show unique constraint

---

### Step 5: Tests (Prompt e)

**Validation checklist:**
```bash
# 1. Check test structure
cd apps/api
ls tests/
# Should see: unit/, integration/, performance/, conftest.py

# 2. Run unit tests
poetry run pytest tests/unit -v
# Should pass:
# - test_tfidf_vectorization
# - test_sentiment_prediction
# - test_text_preprocessing
# - test_feature_importance
# - test_model_serialization

# 3. Check test output
poetry run pytest tests/unit/test_ml.py -v
# Example output:
# tests/unit/test_ml.py::test_tfidf_vectorization PASSED
# tests/unit/test_ml.py::test_sentiment_prediction PASSED

# 4. Run integration tests
poetry run pytest tests/integration -v
# Should pass:
# - test_analyze_endpoint
# - test_batch_analysis
# - test_training_flow
# - test_analytics_trends
# - test_idempotency

# 5. Check coverage
poetry run pytest --cov=. --cov-report=html --cov-report=term
# Should show: >= 80% coverage
# Generates: htmlcov/index.html

# 6. View coverage report
open htmlcov/index.html  # or navigate in browser

# 7. Run performance test
poetry run pytest tests/performance/test_throughput.py -v
# Should show: > 1000 predictions/sec

# 8. Test with locust
poetry run locust -f locustfile.py --headless --users 100 --spawn-rate 10 --run-time 30s --host http://localhost:8000
# Should output:
# RPS: ~500-1000
# p95 latency: <50ms
# 0 failures

# 9. Check specific test
poetry run pytest tests/integration/test_api.py::test_analyze_endpoint -v -s
# Should show request/response details
```

**Expected output:**
- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ Coverage >= 80%
- ✅ Performance test shows >1000 pred/sec
- ✅ Load test p95 <50ms

**Troubleshooting:**
- If tests fail → Check test database connection (use separate test DB)
- If coverage low → Run `pytest --cov=. --cov-report=term-missing` to see uncovered lines
- If performance test slow → Check if model loaded in memory (not disk I/O per request)
- If locust fails → Ensure API running: `curl http://localhost:8000/health`

---

### Step 6: AI (Prompt f)

**Validation checklist:**
```bash
# 1. Check ML package structure
cd packages/ml
ls
# Should see: trainer.py, predictor.py, evaluator.py, __init__.py

# 2. Test ModelTrainer
poetry run python -c "
from packages.ml.trainer import ModelTrainer
trainer = ModelTrainer()
# Use sample data
texts = ['I love this!', 'This is bad', 'Okay product'] * 100
labels = ['positive', 'negative', 'neutral'] * 100
model, vectorizer, metrics = trainer.train(texts, labels)
print(f'F1 Score: {metrics[\"f1_score\"]:.3f}')
"
# Should print: F1 Score: 0.xxx (likely 0.7-0.9)

# 3. Test Predictor
poetry run python -c "
from packages.ml.predictor import Predictor
predictor = Predictor()
predictor.load_model('models/latest-model.joblib')  # Or trained model path
result = predictor.predict('This movie was amazing!')
print(f'Sentiment: {result}')
"
# Should print: Sentiment: {'positive': 0.8x, 'neutral': 0.1x, 'negative': 0.0x}

# 4. Test explanation
poetry run python -c "
from packages.ml.predictor import Predictor
predictor = Predictor()
predictor.load_model('models/latest-model.joblib')
result = predictor.predict('This movie was terrible and boring')
explanation = predictor.explain('This movie was terrible and boring', result)
print('Top words:', explanation['top_words'][:5])
"
# Should show: Top words: [('terrible', -0.8), ('boring', -0.6), ...]

# 5. Test batch prediction
poetry run python -c "
from packages.ml.predictor import Predictor
predictor = Predictor()
predictor.load_model('models/latest-model.joblib')
texts = ['Great!', 'Bad!', 'Okay'] * 100  # 300 texts
import time
start = time.time()
results = predictor.predict_batch(texts)
duration = time.time() - start
print(f'Predicted {len(texts)} in {duration:.3f}s ({len(texts)/duration:.0f} per sec)')
"
# Should show: >1000 predictions per second

# 6. Download Stanford Sentiment Treebank
cd data/
wget https://nlp.stanford.edu/~senteval/stanfordSentimentTreebank.zip
unzip stanfordSentimentTreebank.zip
# Or use pre-downloaded data

# 7. Run eval harness
cd ../apps/api
poetry run python eval/run_eval.py
# Should output:
# Loading test data...
# Running predictions...
# Computing metrics...
# Overall F1: 0.78
# Positive F1: 0.82
# Neutral F1: 0.71
# Negative F1: 0.80

# 8. Check eval results
cat eval/eval-results.json | jq
# Should show:
# {
#   "overall_f1": 0.78,
#   "per_class": {...},
#   "confusion_matrix": [[...], ...],
#   "top_errors": [...]
# }

# 9. Verify meets target
cat eval/eval-results.json | jq '.overall_f1 >= 0.75'
# Should return: true

# 10. Test feature importance
poetry run python -c "
from packages.ml.evaluator import Evaluator
from packages.ml.predictor import Predictor
predictor = Predictor()
predictor.load_model('models/latest-model.joblib')
evaluator = Evaluator()
importance = evaluator.feature_importance(predictor.vectorizer, predictor.model)
print('Top positive words:', importance['positive'][:10])
print('Top negative words:', importance['negative'][:10])
"
# Should show meaningful words:
# Positive: ['excellent', 'amazing', 'great', 'love', 'perfect', ...]
# Negative: ['terrible', 'worst', 'awful', 'bad', 'horrible', ...]
```

**Expected output:**
- ✅ Model trains successfully
- ✅ Predictions work correctly
- ✅ Explanations show relevant words
- ✅ Batch prediction >1000/sec
- ✅ Eval harness runs without errors
- ✅ F1 >= 0.75 on test set
- ✅ Feature importance makes sense

**Troubleshooting:**
- If training fails → Check data format (texts and labels same length)
- If F1 too low → Try larger training dataset, adjust TF-IDF parameters
- If predictions slow → Ensure vectorizer in memory, not reloading from disk
- If feature importance wrong → Check if model and vectorizer match (train together)

---

### Step 7: CI/CD (Prompt g)

**Validation checklist:**
```bash
# 1. Check workflows exist
ls .github/workflows/
# Should see: test.yml, build.yml, deploy.yml

# 2. Check test workflow syntax
cat .github/workflows/test.yml
# Should have:
# - pytest with coverage
# - eval harness
# - locust load test
# - coverage >= 80% assertion
# - F1 >= 0.75 assertion

# 3. Test locally with act (optional)
act pull_request -j test
# Should run: all tests, eval, load test

# 4. Commit and push to trigger CI
git add .
git commit -m "Add sentiment analysis ML pipeline"
git push

# 5. Check GitHub Actions
# Go to: https://github.com/{user}/{repo}/actions
# Should see: workflow running

# 6. Verify test job passes
# Click on workflow run → test job
# Should show:
# ✓ Run pytest (80%+ coverage)
# ✓ Run eval harness (F1 >= 0.75)
# ✓ Run load test (p95 <50ms)

# 7. Test Docker build locally
docker build -f apps/api/Dockerfile -t sentiment-api .
# Should build successfully

# 8. Run Docker container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/sentiment \
  -e REDIS_URL=redis://host.docker.internal:6379 \
  sentiment-api
# Should start API

# 9. Test containerized API
curl http://localhost:8000/health
# Should return: {"status":"ok"}

# 10. Test with trained model in container
docker run -v $(pwd)/models:/app/models -p 8000:8000 sentiment-api
curl -X POST http://localhost:8000/analyze -H "Content-Type: application/json" -d '{"text":"This is great!"}'
# Should return sentiment prediction
```

**Expected output:**
- ✅ Workflows created with correct syntax
- ✅ CI runs on push/PR
- ✅ All checks pass (tests, eval, coverage)
- ✅ Docker image builds successfully
- ✅ Containerized API works

**Troubleshooting:**
- If workflow fails → Check YAML syntax: `yamllint .github/workflows/test.yml`
- If Docker build fails → Check Dockerfile COPY paths, ensure all files exist
- If container can't connect to DB → Use `host.docker.internal` on Mac/Windows, `172.17.0.1` on Linux
- If model not found in container → Mount models directory with `-v` flag

---

### Step 8: Instrumentation (Prompt h)

**Validation checklist:**
```bash
# 1. Start observability stack
docker-compose up -d jaeger prometheus grafana
# Should start 3 services

# 2. Verify services
docker ps | grep -E "jaeger|prometheus|grafana"
# Should show 3 containers running

# 3. Check ports
curl http://localhost:16686  # Jaeger UI
curl http://localhost:9090   # Prometheus
curl http://localhost:3001   # Grafana (or 3000)
# All should return HTML

# 4. Make test requests to generate traces
for i in {1..20}; do
  curl -X POST http://localhost:8000/analyze \
    -H "Content-Type: application/json" \
    -d "{\"text\":\"Test sentiment $i\"}"
done

# 5. Check traces in Jaeger
# Open: http://localhost:16686
# Service: sentiment-api
# Operation: POST /analyze
# Click "Find Traces"
# Should see: 20 traces

# 6. Verify custom spans
# Click a trace → Expand spans
# Should see:
# - analyze_text (with tags: text_length, sentiment_label, confidence)
# - predict (child span)
# - vectorize (child span)

# 7. Check metrics in Prometheus
# Open: http://localhost:9090
# Query: sentiment_predictions_total
# Should show: counter increasing with labels (positive, neutral, negative)

# 8. Query prediction latency
# Prometheus query: histogram_quantile(0.95, rate(prediction_duration_seconds_bucket[5m]))
# Should show: p95 latency <0.01 (10ms)

# 9. Import Grafana dashboard
# Open: http://localhost:3001 (admin/admin)
# Go to: Dashboards → Import
# Upload: grafana/dashboard.json
# Should create dashboard with 6 panels

# 10. Verify dashboard panels
# Open imported dashboard
# Should show:
# - Panel 1: Predictions per second (real-time graph)
# - Panel 2: Sentiment distribution (pie chart)
# - Panel 3: Latency percentiles (line graph)
# - Panel 4: Model F1 score (gauge)
# - Panel 5: Cache hit rate (gauge)
# - Panel 6: Top keywords (bar chart)

# 11. Generate load to populate dashboard
poetry run locust -f locustfile.py --headless --users 50 --spawn-rate 5 --run-time 60s --host http://localhost:8000

# 12. Watch dashboard update in real-time
# Refresh Grafana dashboard
# Should see:
# - Predictions/sec spike to ~500
# - Latency stay <10ms
# - Sentiment distribution updating

# 13. Check custom metrics
curl http://localhost:8000/metrics
# Should return Prometheus format:
# sentiment_predictions_total{label="positive"} 1234
# prediction_duration_seconds_bucket{le="0.005"} 5678
# model_f1_score 0.78
```

**Expected output:**
- ✅ Observability stack running
- ✅ Traces visible in Jaeger with custom spans
- ✅ Metrics in Prometheus
- ✅ Grafana dashboard showing real-time data
- ✅ All 6 panels populated
- ✅ Metrics endpoint working

**Troubleshooting:**
- If no traces → Check OTEL_EXPORTER_OTLP_ENDPOINT in .env: `http://localhost:4318`
- If metrics missing → Check Prometheus scrape config in docker-compose.yml
- If dashboard empty → Verify data source configured: Settings → Data Sources → Add Prometheus
- If panels show "No data" → Generate load with locust, wait 30s for aggregation

---

## Complete Health Check

After all 8 steps, run this comprehensive validation:

```bash
#!/bin/bash
# health-check.sh

echo "=== Sentiment Analysis System Health Check ==="

# 1. Services running
echo -n "Docker services: "
SERVICES=$(docker ps | grep -E "postgres|redis|jaeger|prometheus|grafana" | wc -l)
[ "$SERVICES" -eq 5 ] && echo "✓ (5/5)" || echo "✗ ($SERVICES/5)"

# 2. API responding
echo -n "API health: "
curl -sf http://localhost:8000/health > /dev/null && echo "✓" || echo "✗"

# 3. Database accessible
echo -n "Database: "
psql postgresql://postgres:postgres@localhost:5432/sentiment -c "SELECT COUNT(*) FROM analysis;" > /dev/null 2>&1 && echo "✓" || echo "✗"

# 4. Model exists
echo -n "ML model: "
[ -f "apps/api/models/latest-model.joblib" ] && echo "✓" || echo "✗"

# 5. Prediction works
echo -n "Prediction: "
RESULT=$(curl -sf -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"This is great!"}' | jq -r '.sentiment.positive')
[ $(echo "$RESULT > 0.5" | bc) -eq 1 ] && echo "✓ (confident positive)" || echo "✗"

# 6. Celery worker active
echo -n "Celery worker: "
poetry run celery -A workers inspect active > /dev/null 2>&1 && echo "✓" || echo "✗"

# 7. Tests passing
echo -n "Tests: "
cd apps/api && poetry run pytest -q > /dev/null 2>&1 && echo "✓" || echo "✗"

# 8. Eval meets target
echo -n "Model F1 >= 0.75: "
F1=$(cat eval/eval-results.json | jq -r '.overall_f1')
[ $(echo "$F1 >= 0.75" | bc) -eq 1 ] && echo "✓ ($F1)" || echo "✗ ($F1)"

# 9. Traces flowing
echo -n "Traces (Jaeger): "
curl -sf http://localhost:16686/api/services > /dev/null && echo "✓" || echo "✗"

# 10. Metrics available
echo -n "Metrics (Prometheus): "
curl -sf http://localhost:9090/-/healthy > /dev/null && echo "✓" || echo "✗"

echo ""
echo "=== Health Check Complete ==="
```

Run with: `bash health-check.sh`

**Expected output:**
```
=== Sentiment Analysis System Health Check ===
Docker services: ✓ (5/5)
API health: ✓
Database: ✓
ML model: ✓
Prediction: ✓ (confident positive)
Celery worker: ✓
Tests: ✓
Model F1 >= 0.75: ✓ (0.78)
Traces flowing: ✓
Metrics available: ✓

=== Health Check Complete ===
```

---

## Deployment

### Option 1: Railway + Vercel (Recommended)

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

# 6. Set environment variables
railway variables set DATABASE_URL=${{ DATABASE_URL }}
railway variables set REDIS_URL=${{ REDIS_URL }}

# 7. Run migrations
railway run poetry run alembic upgrade head

# 8. Upload pre-trained model (or train on first deploy)
# Option A: Upload via Railway CLI
railway run poetry run python -c "
from packages.ml.trainer import ModelTrainer
# ... train model ...
"
# Option B: Train locally, commit model file
git add apps/api/models/latest-model.joblib
git commit -m "Add pre-trained model"
git push

# 9. Deploy Celery worker
railway up --service worker

# 10. Deploy frontend to Vercel
cd ../web
vercel --prod
# Set environment variable: NEXT_PUBLIC_API_URL=https://{your-api}.railway.app

# 11. Test production
curl https://{your-api}.railway.app/health
# Expected: {"status":"ok"}

curl -X POST https://{your-api}.railway.app/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"This is amazing!"}'
# Expected: {"sentiment": {"positive": 0.9, ...}, ...}
```

**Cost**: $0-5/month (Railway $5 credit covers development)

---

### Option 2: Docker VPS (DigitalOcean, Hetzner)

```bash
# 1. SSH to VPS
ssh root@your-server.com

# 2. Install Docker
curl -fsSL https://get.docker.com | sh

# 3. Clone repo
git clone https://github.com/{user}/{repo}.git
cd {repo}

# 4. Set environment variables
cp .env.example .env
nano .env
# Set: DATABASE_URL, REDIS_URL (use docker hostnames)

# 5. Build and start services
docker-compose -f docker-compose.prod.yml up -d

# 6. Run migrations
docker-compose exec api poetry run alembic upgrade head

# 7. Train initial model
docker-compose exec api poetry run python -c "
from packages.ml.trainer import ModelTrainer
from packages.ml.predictor import Predictor
# Download Stanford Sentiment data
# Train model
# Save to /app/models/
"

# 8. Verify services
docker-compose ps
# Should show: api, web, postgres, redis, celery, jaeger, prometheus, grafana

# 9. Set up nginx reverse proxy
apt install nginx
cat > /etc/nginx/sites-available/sentiment <<EOF
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}
EOF
ln -s /etc/nginx/sites-available/sentiment /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# 10. Enable SSL (Let's Encrypt)
apt install certbot python3-certbot-nginx
certbot --nginx -d yourdomain.com
```

**Cost**: $5-10/month (basic VPS)

---

### Option 3: Run Locally (Free)

```bash
# Perfect for portfolio demos

# 1. Start all services
docker-compose up -d

# 2. Train model
cd apps/api
poetry run python scripts/train_initial_model.py

# 3. Start API
poetry run uvicorn main:app --host 0.0.0.0

# 4. Start Celery worker
poetry run celery -A workers worker

# 5. Start frontend
cd ../web
pnpm dev

# 6. Record demo video
# Use QuickTime/OBS to record:
# - Analyze text via UI
# - Show real-time dashboard updates
# - Demonstrate batch analysis
# - Show model metrics

# 7. Take screenshots for portfolio
# - Dashboard with live data
# - Prediction with explanation
# - Grafana metrics
```

**Cost**: $0 (runs on laptop)

---

## Production Smoke Tests

```bash
# After deployment, verify everything works:

# 1. Health check
curl https://your-api.com/health
# Expected: {"status":"ok","version":"1.0.0"}

# 2. Single prediction
curl -X POST https://your-api.com/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"This product is absolutely fantastic!"}'
# Expected: sentiment.positive > 0.8

# 3. Negative sentiment
curl -X POST https://your-api.com/analyze \
  -H "Content-Type: application/json" \
  -d '{"text":"Terrible experience, very disappointed."}'
# Expected: sentiment.negative > 0.8

# 4. Batch analysis
curl -X POST https://your-api.com/analyze/batch \
  -H "Content-Type: application/json" \
  -d '{"texts":["Great!","Bad!","Okay"]}'
# Expected: array of 3 predictions

# 5. Analytics trends
curl "https://your-api.com/analytics/trends?interval=hour&limit=24"
# Expected: 24 data points with timestamps

# 6. Model info
curl https://your-api.com/models
# Expected: [{name, version, f1_score, training_samples}]

# 7. Feature importance
curl https://your-api.com/models/latest/evaluate
# Expected: {confusion_matrix, f1_scores, top_words}

# 8. Load test (use staging URL!)
k6 run load-test.js --duration 2m --vus 50
# Expected:
# - p95 < 50ms
# - throughput > 500 RPS
# - error rate < 0.1%
```

---

## Success Criteria

You're done when ALL of these pass:

- [ ] All 8 validation checklists complete
- [ ] Health check script returns all ✓
- [ ] Model F1 >= 0.75 on test set
- [ ] Single prediction <10ms p95
- [ ] Batch 100 predictions <100ms
- [ ] Test coverage >= 80%
- [ ] CI passes on GitHub
- [ ] Production deployed and accessible
- [ ] Dashboard shows live metrics
- [ ] Can record working demo video

**Estimated time**: 6-8 hours

---

## Next Steps After Building

### 1. Create Golden Demo Dataset
```bash
# Curate 100 diverse examples
- Product reviews (20)
- Customer support tickets (20)
- Social media posts (20)
- Movie reviews (20)
- Restaurant reviews (20)

# Show model handles various domains
```

### 2. Add Advanced Features
- **Aspect-based sentiment**: "Great food, bad service" → separate scores
- **Emotion detection**: joy, anger, sadness, surprise (already in schema!)
- **Sarcasm detection**: Rule-based + context
- **Trend alerts**: Email when sentiment drops >10%

### 3. Portfolio Presentation
- **Demo video** (3-5 min): Upload text → show prediction → explain features → dashboard
- **Blog post**: "Building a 10k req/sec sentiment analyzer with $0 API costs"
- **GitHub README**: Architecture diagram, performance benchmarks, screenshots

### 4. Optimize for Resume
Highlight these talking points:
- "Achieved F1 0.78 (95% of BERT accuracy) using classical ML, 100x faster"
- "Process 10,000 predictions/sec on single CPU core"
- "Zero API costs - runs on free tier"
- "Built production-grade observability with OpenTelemetry"

---

## Troubleshooting Production

### High latency (p95 > 50ms)
```bash
# Check model in memory
# Bad: Loading from disk each request
# Good: Load once at startup

# Check vectorizer caching
# Use Redis to cache TF-IDF vectors for common phrases

# Profile with cProfile
poetry run python -m cProfile -s cumtime main.py
```

### Low accuracy (F1 < 0.70)
```bash
# Expand training data (10k → 50k samples)
# Tune TF-IDF parameters:
#   - Increase max_features (10k → 20k)
#   - Try trigrams (ngram_range=(1,3))
#   - Adjust min_df/max_df

# Try different classifier
from sklearn.linear_model import LogisticRegression
# Often better than Naive Bayes for sentiment
```

### Memory issues
```bash
# Model too large (>100MB)
# Solution: Reduce vocabulary size
vectorizer = TfidfVectorizer(max_features=5000)  # Down from 10k

# Or use feature selection
from sklearn.feature_selection import SelectKBest
selector = SelectKBest(k=5000)
```

Good luck! 🚀 Remember to validate after each step.
