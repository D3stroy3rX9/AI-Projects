# Local Setup Guide

Complete guide to running the Sentiment Analysis Dashboard locally on your machine.

## Table of Contents

- [Prerequisites](#prerequisites)
- [System Requirements](#system-requirements)
- [Software Installation](#software-installation)
- [Project Setup](#project-setup)
- [Running the Application](#running-the-application)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Minimum System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **OS** | Windows 10/11, macOS 10.15+, Ubuntu 20.04+ | Latest stable |
| **RAM** | 8 GB | 16 GB |
| **Disk Space** | 10 GB free | 20 GB free |
| **CPU** | 2 cores | 4+ cores |
| **Internet** | Required for initial setup | - |

### Required Software Versions

| Software | Version | Purpose |
|----------|---------|---------|
| **Docker** | 20.10+ | Container runtime |
| **Docker Compose** | 2.0+ | Multi-container orchestration |
| **Python** | 3.11 or 3.12 | API backend |
| **Poetry** | 1.7+ | Python dependency management |
| **Node.js** | 20.x LTS | Frontend |
| **pnpm** | 8.x | Node package manager |
| **Git** | 2.30+ | Version control |

---

## Software Installation

### 1. Install Git

**Windows:**
```bash
# Download from https://git-scm.com/download/win
# Or use Chocolatey:
choco install git
```

**macOS:**
```bash
# Using Homebrew:
brew install git

# Or download from https://git-scm.com/download/mac
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install git -y
```

**Verify installation:**
```bash
git --version
# Expected: git version 2.30.0 or higher
```

---

### 2. Install Docker & Docker Compose

**Windows:**
1. Download Docker Desktop: https://www.docker.com/products/docker-desktop/
2. Run installer
3. Start Docker Desktop
4. Verify in terminal:
```bash
docker --version
docker-compose --version
```

**macOS:**
```bash
# Using Homebrew:
brew install --cask docker

# Or download Docker Desktop:
# https://www.docker.com/products/docker-desktop/

# Start Docker Desktop from Applications
```

**Linux (Ubuntu/Debian):**
```bash
# Install Docker
sudo apt update
sudo apt install ca-certificates curl gnupg lsb-release -y

sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y

# Add your user to docker group (avoid sudo)
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
docker compose version
```

**Verify Docker:**
```bash
docker run hello-world
# Should download and run successfully
```

---

### 3. Install Python 3.11 or 3.12

**Windows:**
```bash
# Download from https://www.python.org/downloads/
# During installation, check "Add Python to PATH"

# Or using Chocolatey:
choco install python311
```

**macOS:**
```bash
# Using Homebrew:
brew install python@3.11

# Or download from https://www.python.org/downloads/
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev -y

# Make Python 3.11 default (optional)
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
```

**Verify:**
```bash
python3 --version
# Expected: Python 3.11.x or 3.12.x
```

---

### 4. Install Poetry

**All Platforms:**
```bash
# Official installer (recommended)
curl -sSL https://install.python-poetry.org | python3 -

# Or using pip
pip install poetry

# Add Poetry to PATH if needed
export PATH="$HOME/.local/bin:$PATH"
```

**Verify:**
```bash
poetry --version
# Expected: Poetry (version 1.7.0+)
```

**Configure Poetry:**
```bash
# Create virtualenvs in project directory
poetry config virtualenvs.in-project true
```

---

### 5. Install Node.js 20.x LTS

**Windows:**
```bash
# Download from https://nodejs.org/
# Choose LTS version (20.x)

# Or using Chocolatey:
choco install nodejs-lts
```

**macOS:**
```bash
# Using Homebrew:
brew install node@20

# Or download from https://nodejs.org/
```

**Linux (Ubuntu/Debian):**
```bash
# Using NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y
```

**Verify:**
```bash
node --version
# Expected: v20.x.x

npm --version
# Expected: 10.x.x
```

---

### 6. Install pnpm

**All Platforms:**
```bash
# Using npm
npm install -g pnpm

# Or using standalone script
curl -fsSL https://get.pnpm.io/install.sh | sh -
```

**Verify:**
```bash
pnpm --version
# Expected: 8.x.x
```

---

## Project Setup

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/AI-Projects.git

# Navigate to project
cd AI-Projects/sentiment-analysis

# Verify you're on the correct branch
git branch
git status
```

---

### Step 2: Start Infrastructure Services

```bash
# Start PostgreSQL, Redis, Jaeger, Prometheus, Grafana
docker-compose up -d

# Verify all services are running
docker-compose ps

# Expected services:
# - postgres (port 5432)
# - redis (port 6379)
# - jaeger (port 16686)
# - prometheus (port 9090)
# - grafana (port 3001)
```

**Check service health:**
```bash
# PostgreSQL
docker exec -it sentiment-analysis-postgres-1 pg_isready -U postgres

# Redis
docker exec -it sentiment-analysis-redis-1 redis-cli ping

# View logs if any service fails
docker-compose logs [service-name]
```

---

### Step 3: Setup API Backend

```bash
cd apps/api

# Install dependencies with Poetry (skip installing the project itself)
poetry install --no-root

# This will:
# - Create virtual environment
# - Install all Python packages (~123 dependencies)
# - May take 5-10 minutes
```

**Note:** The `.env` file is already in the project root (`sentiment-analysis/.env`), so you don't need to create it.

**Create database tables:**
```bash
# Create all database tables (replaces Alembic migrations)
poetry run python create_tables.py

# This creates:
# - analysis table (TimescaleDB hypertable)
# - models table
# - training_data table
# - analytics_summary table
```

**Seed the database:**
```bash
# Populate with sample data
poetry run python seed.py

# Answer 'y' when prompted
# This creates:
# - 300 training samples
# - 1000 analysis records
# - 1 initial model
# - Analytics summaries
```

**Train initial model:**
```bash
# Train ML model from seed data
poetry run python scripts/train_initial_model.py

# This will:
# - Load 300 training samples
# - Train TF-IDF + Naive Bayes model
# - Evaluate on test set
# - Save model to models/sentiment_model.joblib
# - Create database record
# Expected F1 score: ~0.75-0.80
```

---

### Step 4: Setup Web Frontend

```bash
# Go to web directory
cd ../web

# Install dependencies with pnpm
pnpm install

# This will:
# - Download all npm packages
# - Create node_modules directory
# - May take 3-5 minutes
```

**Create .env.local file:**
```bash
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
```

---

## Running the Application

You'll need **4 terminal windows** to run all components.

### Terminal 1: API Server

```bash
cd apps/api

# Start FastAPI server
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete.
```

**Keep this terminal running!**

---

### Terminal 2: Celery Worker

```bash
cd apps/api

# Start Celery worker
poetry run celery -A workers worker --loglevel=info

# Expected output:
# [2024-11-07 20:00:00,000: INFO/MainProcess] Connected to redis://localhost:6379/0
# [2024-11-07 20:00:00,000: INFO/MainProcess] celery@hostname ready.
```

**Keep this terminal running!**

---

### Terminal 3: Celery Beat (Optional - for scheduled tasks)

```bash
cd apps/api

# Start Celery Beat scheduler
poetry run celery -A workers beat --loglevel=info

# Expected output:
# [2024-11-07 20:00:00,000: INFO/MainProcess] beat: Starting...
```

**Keep this terminal running if you want scheduled tasks!**

---

### Terminal 4: Web Frontend

```bash
cd apps/web

# Start Next.js development server
pnpm dev

# Expected output:
# ▲ Next.js 14.x.x
# - Local:        http://localhost:3000
# - Ready in 2.3s
```

**Keep this terminal running!**

---

## Verification

### 1. Check All Services

Open these URLs in your browser:

| Service | URL | Expected |
|---------|-----|----------|
| **Web App** | http://localhost:3000 | Sentiment analysis interface |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **API Health** | http://localhost:8000/health | `{"status": "ok"}` |
| **Prometheus** | http://localhost:9090 | Prometheus dashboard |
| **Grafana** | http://localhost:3001 | Grafana login (admin/admin) |
| **Jaeger** | http://localhost:16686 | Jaeger tracing UI |

---

### 2. Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Expected: {"status":"ok","version":"1.0.0","environment":"development"}

# Single text analysis
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "This product is amazing!", "include_emotions": false}'

# Expected: JSON response with sentiment scores

# Batch analysis
curl -X POST http://localhost:8000/analyze/batch \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Great!", "Terrible.", "Okay."], "source": "api"}'

# Expected: JSON response with results array

# Get analytics trends
curl http://localhost:8000/analytics/trends?time_range=LAST_7_DAYS

# Expected: JSON response with trend data

# List models
curl http://localhost:8000/models

# Expected: JSON response with model list
```

---

### 3. Test Web Interface

1. **Open** http://localhost:3000
2. **Type** text in the input box: "This is an amazing product!"
3. **Click** "Analyze Sentiment"
4. **Verify** you see:
   - Sentiment scores (positive/neutral/negative)
   - Confidence percentage
   - Color-coded results

---

### 4. Check Database

```bash
# Connect to PostgreSQL
docker exec -it sentiment-analysis-postgres-1 psql -U postgres -d sentiment

# Check tables
\dt

# Expected tables:
# - analysis
# - models
# - training_data
# - analytics_summary

# Count records
SELECT COUNT(*) FROM analysis;
# Expected: ~1000

SELECT COUNT(*) FROM training_data;
# Expected: ~300

SELECT * FROM models;
# Expected: 1 row with initial model

# Exit
\q
```

---

### 5. Test Celery Tasks

```bash
# In Python shell
cd apps/api
poetry run python

# Test batch analysis task
from workers.tasks import batch_analyze_task

result = batch_analyze_task.delay(
    ["Great product!", "Terrible service.", "It's okay."],
    source="api"
)

print(f"Task ID: {result.id}")
print(f"Status: {result.status}")

# Wait a few seconds
import time
time.sleep(3)

print(f"Result: {result.result}")
# Expected: {'status': 'success', 'analyzed': 3, 'skipped': 0, 'total': 3}

# Exit
exit()
```

---

### 6. View Observability Data

**Prometheus Metrics:**
1. Open http://localhost:9090
2. Go to Graph tab
3. Query: `sentiment_predictions_total`
4. Click "Execute"
5. Should see prediction counts

**Grafana Dashboards:**
1. Open http://localhost:3001
2. Login: admin/admin (change password when prompted)
3. Go to Dashboards → Import
4. Click "Upload JSON file"
5. Import: `observability/grafana/dashboards/api-overview.json`
6. Import: `observability/grafana/dashboards/ml-metrics.json`
7. View dashboards

**Jaeger Traces:**
1. Open http://localhost:16686
2. Service: `sentiment-analysis-api`
3. Click "Find Traces"
4. Should see HTTP requests
5. Click a trace to view details

---

## Troubleshooting

### Issue: Docker services won't start

**Check Docker is running:**
```bash
docker ps

# If error, start Docker Desktop (Windows/Mac)
# Or start Docker daemon (Linux):
sudo systemctl start docker
```

**Check ports are available:**
```bash
# Windows
netstat -ano | findstr "5432 6379 9090"

# macOS/Linux
lsof -i :5432
lsof -i :6379
lsof -i :9090

# If ports are in use, stop conflicting services or change ports in docker-compose.yml
```

**Reset Docker services:**
```bash
docker-compose down -v
docker-compose up -d
```

---

### Issue: Poetry installation fails

**Clear Poetry cache:**
```bash
poetry cache clear pypi --all
poetry install
```

**Use pip instead:**
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

### Issue: Database migration fails

**Reset database:**
```bash
# Drop and recreate database
docker exec -it sentiment-analysis-postgres-1 psql -U postgres -c "DROP DATABASE IF EXISTS sentiment;"
docker exec -it sentiment-analysis-postgres-1 psql -U postgres -c "CREATE DATABASE sentiment;"

# Create tables again
cd apps/api
poetry run python create_tables.py
```

**Check database connection:**
```bash
poetry run python -c "from db import engine; print(engine.connect())"
```

---

### Issue: Model training fails

**Check dependencies:**
```bash
poetry run python -c "import sklearn; print(sklearn.__version__)"
```

**Install manually:**
```bash
poetry add scikit-learn==1.3.2 joblib==1.3.2 numpy==1.26.2
```

**Check training data:**
```bash
poetry run python -c "
from db import SessionLocal, TrainingData
db = SessionLocal()
count = db.query(TrainingData).count()
print(f'Training samples: {count}')
# Should be 300+
"
```

---

### Issue: Next.js build fails

**Clear cache:**
```bash
cd apps/web
rm -rf .next node_modules
pnpm install
pnpm dev
```

**Check Node version:**
```bash
node --version
# Must be v20.x.x
```

---

### Issue: API returns 500 errors

**Check logs:**
```bash
# In API terminal, you'll see error details

# Or check with curl
curl -v http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "test"}'
```

**Check model is loaded:**
```bash
ls -lh apps/api/models/
# Should see sentiment_model.joblib
```

**Test manually:**
```bash
cd apps/api
poetry run python

from ml import SentimentPredictor
predictor = SentimentPredictor("models/sentiment_model.joblib")
result = predictor.predict("This is great!")
print(result)
# Should return sentiment scores
```

---

### Issue: Celery worker not processing tasks

**Check Redis connection:**
```bash
docker exec -it sentiment-analysis-redis-1 redis-cli ping
# Expected: PONG
```

**Check worker is running:**
```bash
cd apps/api
poetry run celery -A workers inspect active
# Should show worker status
```

**Check task registration:**
```bash
poetry run celery -A workers inspect registered
# Should list: train_model_task, batch_analyze_task, aggregate_analytics_task
```

---

### Issue: Memory issues

**Reduce Docker memory:**
```bash
# In Docker Desktop settings:
# Resources → Memory → Set to 4GB (minimum)
```

**Close unnecessary services:**
```bash
# Don't need Grafana/Jaeger for basic testing
docker-compose stop grafana jaeger prometheus
```

---

### Issue: Port conflicts

**Change API port:**
```bash
# In apps/api/.env
API_PORT=8001

# Start with new port
poetry run uvicorn main:app --reload --port 8001
```

**Change web port:**
```bash
# In apps/web
pnpm dev -p 3001
```

---

## Quick Reference Commands

### Start Everything
```bash
# Terminal 1: Infrastructure
docker-compose up -d

# Terminal 2: API
cd apps/api && poetry run uvicorn main:app --reload

# Terminal 3: Worker
cd apps/api && poetry run celery -A workers worker --loglevel=info

# Terminal 4: Web
cd apps/web && pnpm dev
```

### Stop Everything
```bash
# Stop web (Ctrl+C in Terminal 4)
# Stop worker (Ctrl+C in Terminal 3)
# Stop API (Ctrl+C in Terminal 2)

# Stop infrastructure
docker-compose down

# Stop and remove volumes (WARNING: deletes data)
docker-compose down -v
```

### Reset Everything
```bash
# Stop all
docker-compose down -v

# Remove Python virtual env
rm -rf apps/api/.venv

# Remove Node modules
rm -rf apps/web/node_modules apps/web/.next

# Start fresh
docker-compose up -d
cd apps/api && poetry install --no-root && poetry run python create_tables.py && poetry run python seed.py && poetry run python scripts/train_initial_model.py
cd ../web && pnpm install
```

---

## Production Deployment

For production deployment, see:
- `CI_CD_GUIDE.md` - GitHub Actions, Docker, deployment
- `INSTRUMENTATION_GUIDE.md` - Monitoring and observability
- `apps/api/README_DATABASE.md` - Database setup

---

## Getting Help

1. **Check logs:**
   - API: Terminal where uvicorn is running
   - Worker: Terminal where celery is running
   - Docker: `docker-compose logs [service]`

2. **Common log files:**
   - API errors: Check terminal output
   - Database: `docker-compose logs postgres`
   - Redis: `docker-compose logs redis`

3. **Debug mode:**
   ```bash
   # API with debug logging
   LOG_LEVEL=DEBUG poetry run uvicorn main:app --reload

   # Worker with debug logging
   poetry run celery -A workers worker --loglevel=debug
   ```

4. **Test individual components:**
   ```bash
   # Test database
   docker exec -it sentiment-analysis-postgres-1 psql -U postgres -d sentiment

   # Test Redis
   docker exec -it sentiment-analysis-redis-1 redis-cli

   # Test Python imports
   cd apps/api && poetry run python -c "import main; print('OK')"

   # Test ML package
   cd apps/api && poetry run python -c "from ml import ModelTrainer; print('OK')"
   ```

---

## Success Checklist

- [ ] All software installed (Docker, Python, Node, Poetry, pnpm)
- [ ] Repository cloned
- [ ] Docker services running (`docker-compose ps`)
- [ ] Database migrated (`alembic current` shows 001)
- [ ] Database seeded (1000+ analysis records)
- [ ] Model trained (sentiment_model.joblib exists)
- [ ] API running (http://localhost:8000/health returns OK)
- [ ] Worker running (Celery shows "ready")
- [ ] Web running (http://localhost:3000 loads)
- [ ] Can analyze text via web interface
- [ ] Grafana accessible (http://localhost:3001)

If all items are checked, you're ready to go! 🎉

---

## Next Steps

1. **Explore the API:** http://localhost:8000/docs
2. **Try the web interface:** http://localhost:3000
3. **View metrics:** http://localhost:9090
4. **Check traces:** http://localhost:16686
5. **Review code:** Start with `apps/api/main.py`
6. **Run tests:** `cd apps/api && poetry run pytest`
7. **Train custom model:** Add your own training data
8. **Deploy:** Follow `CI_CD_GUIDE.md`

---

**Questions? Issues?**
- Check troubleshooting section above
- Review logs in terminals
- Verify all prerequisites installed correctly
- Ensure all Docker services are running
