# Database Setup Guide

## Prerequisites

- PostgreSQL 16+ with TimescaleDB extension
- Docker (recommended for local development)

## Quick Start

### 1. Start Database

```bash
# Using docker-compose (recommended)
docker-compose up -d postgres

# Verify TimescaleDB extension
docker exec -it sentiment-analysis-postgres-1 psql -U postgres -d sentiment \
  -c "SELECT * FROM pg_extension WHERE extname='timescaledb';"
```

### 2. Run Migrations

```bash
cd apps/api

# Run all migrations
poetry run alembic upgrade head

# Check current migration version
poetry run alembic current

# View migration history
poetry run alembic history
```

### 3. Seed Database

```bash
# Populate with sample data
poetry run python seed.py
```

## Database Schema

### Tables

#### 1. `analysis` (TimescaleDB Hypertable)
Stores all sentiment analysis results with time-series optimization.

```sql
CREATE TABLE analysis (
    id INTEGER PRIMARY KEY,
    text_hash VARCHAR(64) UNIQUE NOT NULL,
    text TEXT NOT NULL,
    sentiment_scores JSONB NOT NULL,  -- {positive, neutral, negative}
    emotion_scores JSONB,             -- {joy, anger, sadness, surprise, fear, love}
    predicted_label sentimentlabelenum NOT NULL,
    confidence FLOAT NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    analyzed_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    source sourceenum NOT NULL,
    metadata JSONB
);

-- Indexes
CREATE UNIQUE INDEX ix_analysis_text_hash ON analysis(text_hash);
CREATE INDEX ix_analysis_analyzed_at ON analysis(analyzed_at);
CREATE INDEX ix_analysis_predicted_label ON analysis(predicted_label);
CREATE INDEX ix_analysis_label_time ON analysis(predicted_label, analyzed_at);
```

#### 2. `models`
Stores trained ML model metadata.

```sql
CREATE TABLE models (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    algorithm VARCHAR(100) NOT NULL,
    f1_score FLOAT NOT NULL CHECK (f1_score >= 0 AND f1_score <= 1),
    training_samples INTEGER NOT NULL,
    vocabulary_size INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    model_path VARCHAR(500),
    metrics JSONB
);
```

#### 3. `training_data`
Stores labeled data for model training.

```sql
CREATE TABLE training_data (
    id INTEGER PRIMARY KEY,
    text TEXT NOT NULL,
    label sentimentlabelenum NOT NULL,
    source VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    used_in_training BOOLEAN NOT NULL DEFAULT FALSE
);
```

#### 4. `analytics_summary`
Aggregated analytics data for dashboard.

```sql
CREATE TABLE analytics_summary (
    id INTEGER PRIMARY KEY,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    hour INTEGER,
    sentiment_avg FLOAT NOT NULL,
    positive_count INTEGER NOT NULL DEFAULT 0,
    neutral_count INTEGER NOT NULL DEFAULT 0,
    negative_count INTEGER NOT NULL DEFAULT 0,
    total_count INTEGER NOT NULL
);
```

## Alembic Commands

### Create New Migration

```bash
# Auto-generate migration from model changes
poetry run alembic revision --autogenerate -m "description of changes"

# Create empty migration (manual)
poetry run alembic revision -m "description"
```

### Apply Migrations

```bash
# Upgrade to latest
poetry run alembic upgrade head

# Upgrade one version
poetry run alembic upgrade +1

# Downgrade one version
poetry run alembic downgrade -1

# Downgrade to specific version
poetry run alembic downgrade <revision_id>
```

### View Migration Info

```bash
# Current version
poetry run alembic current

# History
poetry run alembic history

# Show SQL for migration (don't execute)
poetry run alembic upgrade head --sql
```

## Seed Data

The seed script (`seed.py`) creates:

- **300 training samples** (100 per sentiment class)
- **1000 analysis records** with realistic distribution:
  - 400 positive (40%)
  - 300 neutral (30%)
  - 300 negative (30%)
- **1 initial model** entry (F1: 0.78)
- **Analytics summaries** aggregated by date

### Re-seed Database

```bash
# Clear all data and re-seed
poetry run python seed.py

# The script will ask for confirmation if data exists
```

## TimescaleDB Features

The `analysis` table is converted to a hypertable for time-series optimization:

```sql
SELECT create_hypertable(
    'analysis',
    'analyzed_at',
    if_not_exists => TRUE
);
```

### Benefits:
- Automatic data partitioning by time
- Optimized time-range queries
- Compression for old data
- Fast aggregation queries

### Example Queries:

```sql
-- Last 7 days trend
SELECT
    time_bucket('1 day', analyzed_at) AS day,
    predicted_label,
    COUNT(*) as count
FROM analysis
WHERE analyzed_at > NOW() - INTERVAL '7 days'
GROUP BY day, predicted_label
ORDER BY day;

-- Hourly aggregation
SELECT
    time_bucket('1 hour', analyzed_at) AS hour,
    AVG(confidence) as avg_confidence,
    COUNT(*) as total
FROM analysis
WHERE analyzed_at > NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour;
```

## Troubleshooting

### TimescaleDB Extension Not Found

```bash
# Install TimescaleDB extension in Docker
docker exec -it sentiment-analysis-postgres-1 psql -U postgres -c "CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;"

# Or use timescale/timescaledb Docker image (already in docker-compose.yml)
```

### Migration Conflicts

```bash
# If migrations are out of sync
poetry run alembic stamp head

# Or reset to specific version
poetry run alembic downgrade <revision>
poetry run alembic upgrade head
```

### Database Connection Issues

```bash
# Check DATABASE_URL in .env
echo $DATABASE_URL

# Test connection
poetry run python -c "from db import engine; engine.connect()"
```

## Production Considerations

### Backups

```bash
# Backup database
pg_dump -U postgres sentiment > backup.sql

# Restore
psql -U postgres sentiment < backup.sql
```

### Monitoring

- Monitor hypertable chunk sizes
- Set up compression policies for old data
- Create materialized views for common analytics queries

### Indexes

The schema includes optimized indexes for:
- Unique text lookup (text_hash)
- Time-range queries (analyzed_at)
- Filtering by label (predicted_label)
- Combined queries (label + time)

## Next Steps

After database setup:
1. Implement API endpoints (prompt d-f)
2. Connect ML models to database
3. Set up Celery workers for batch processing
4. Create analytics aggregation jobs
