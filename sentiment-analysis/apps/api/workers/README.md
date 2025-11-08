# Celery Workers Documentation

## Overview

Background task processing using Celery with Redis as broker and result backend.

## Tasks

### 1. `train_model_task`

Train a new sentiment analysis model.

**Parameters:**
- `training_data_ids`: List[int] - IDs of TrainingData records to use
- `model_name`: str (optional) - Custom name for the model

**Features:**
- ✅ Idempotent: Checks if model with same dataset exists
- ✅ Retry logic: 3 attempts with exponential backoff
- ✅ Progress tracking: Reports progress percentage
- ✅ Automatic model activation: Deactivates old models

**Example:**
```python
from workers.tasks import train_model_task

# Async
result = train_model_task.delay([1, 2, 3, 4, 5])

# Sync (blocking)
result = train_model_task([1, 2, 3, 4, 5])

# Check status
print(result.state)  # 'PENDING', 'PROGRESS', 'SUCCESS', 'FAILURE'

# Get result
if result.ready():
    print(result.result)  # {'model_id': 1, 'f1_score': 0.78, ...}
```

**Progress States:**
1. `loading_data` (10%)
2. `training` (30%)
3. `evaluating` (70%)
4. `saving` (85%)
5. `updating_db` (95%)
6. `SUCCESS` (100%)

---

### 2. `batch_analyze_task`

Analyze sentiment for multiple texts in batch.

**Parameters:**
- `texts`: List[str] - Texts to analyze
- `source`: str - Source identifier ('api', 'batch', 'webhook')

**Features:**
- ✅ Deduplication: Skips texts already analyzed (by hash)
- ✅ Batch commits: Commits every 100 records for performance
- ✅ Progress tracking: Reports current item and percentage
- ✅ Retry logic: 3 attempts with exponential backoff

**Example:**
```python
from workers.tasks import batch_analyze_task

texts = [
    "This is amazing!",
    "Terrible experience.",
    "It's okay, nothing special."
]

result = batch_analyze_task.delay(texts, source="api")

# Wait and get result
result.get(timeout=60)
# {'analyzed': 3, 'skipped': 0, 'total': 3}
```

**Performance:**
- ~100 texts/second
- Commits in batches of 100
- Skips duplicates automatically

---

### 3. `aggregate_analytics_task`

Compute hourly analytics summaries.

**Parameters:** None (scheduled task)

**Features:**
- ✅ Scheduled: Runs automatically every hour
- ✅ Idempotent: Won't duplicate summaries
- ✅ Automatic: No manual invocation needed

**Example:**
```python
from workers.tasks import aggregate_analytics_task

# Manual trigger (not normally needed)
result = aggregate_analytics_task.delay()

# Check result
result.get()
# {'status': 'success', 'total_count': 150, 'sentiment_avg': 0.23}
```

**Schedule:**
- Runs: Every hour at :00 (via Celery Beat)
- Creates: AnalyticsSummary records
- Aggregates: Previous hour's data

---

## Running Workers

### Development

```bash
# Terminal 1: Start worker
cd apps/api
poetry run celery -A workers worker --loglevel=info

# Terminal 2: Start beat (for scheduled tasks)
poetry run celery -A workers beat --loglevel=info

# Terminal 3: Optional - Flower (monitoring UI)
poetry run celery -A workers flower
# Visit: http://localhost:5555
```

### Production

```bash
# Worker with concurrency
celery -A workers worker \
  --loglevel=info \
  --concurrency=4 \
  --max-tasks-per-child=100

# Beat scheduler
celery -A workers beat --loglevel=info

# Or use systemd/supervisor to manage processes
```

### Docker

Already configured in `docker-compose.yml`:

```yaml
services:
  worker:
    command: celery -A workers worker --loglevel=info

  beat:
    command: celery -A workers beat --loglevel=info
```

---

## Monitoring

### Celery Flower

Web-based monitoring tool:

```bash
poetry run celery -A workers flower
```

Visit: http://localhost:5555

Features:
- Task history
- Worker status
- Real-time monitoring
- Task retries
- Performance stats

### CLI Inspection

```bash
# List active tasks
celery -A workers inspect active

# List scheduled tasks
celery -A workers inspect scheduled

# List registered tasks
celery -A workers inspect registered

# Worker stats
celery -A workers inspect stats

# Ping workers
celery -A workers inspect ping
```

### Logs

```bash
# Worker logs
celery -A workers worker --loglevel=debug

# Beat logs
celery -A workers beat --loglevel=debug
```

---

## Task Retry Logic

All tasks are configured with:

- **Max retries**: 3
- **Backoff**: Exponential (2^retry_count * 60 seconds)
- **Jitter**: Random delay to prevent thundering herd
- **Max backoff**:
  - `train_model_task`: 10 minutes
  - `batch_analyze_task`: 5 minutes
  - `aggregate_analytics_task`: Default

**Example retry timeline:**
1. First attempt: Immediate
2. Retry 1: ~60 seconds later
3. Retry 2: ~120 seconds later
4. Retry 3: ~240 seconds later
5. Fails permanently after 3 retries

---

## Idempotency

### train_model_task
Creates hash of training data IDs. If model exists with same hash, returns existing model instead of retraining.

```python
data_hash = sha256(sorted(training_data_ids)).hexdigest()[:16]
existing = db.query(Model).filter(Model.name == f"model_{data_hash}").first()
if existing:
    return existing  # Don't retrain
```

### batch_analyze_task
Uses SHA-256 hash of text content to detect duplicates.

```python
text_hash = sha256(text.encode('utf-8')).hexdigest()
if db.query(Analysis).filter(Analysis.text_hash == text_hash).first():
    skip()  # Don't re-analyze
```

### aggregate_analytics_task
Checks if summary exists for hour before creating.

```python
existing = db.query(AnalyticsSummary).filter(
    date == hour_start, hour == hour_start.hour
).first()
if existing:
    return existing  # Don't re-aggregate
```

---

## Error Handling

### Automatic Retries

Tasks auto-retry on exceptions:

```python
@celery_app.task(
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
```

### Dead Letter Queue

Failed tasks (after max retries) go to dead letter queue.

View failed tasks:
```bash
celery -A workers inspect failed
```

Retry failed tasks:
```python
# Programmatically
from celery.result import AsyncResult
result = AsyncResult(task_id)
result.retry()
```

### Logging

All tasks log to standard output with structured logging:

```python
logger.info(f"Task started: {self.request.id}")
logger.error(f"Task failed: {e}", exc_info=True)
```

---

## Configuration

Located in `workers/celery_app.py`:

```python
celery_app.conf.update(
    task_serializer="json",           # Use JSON for messages
    task_track_started=True,          # Track when tasks start
    task_time_limit=3600,             # 1 hour max
    worker_prefetch_multiplier=1,     # One task at a time
    worker_max_tasks_per_child=100,   # Restart after 100 tasks
)
```

### Beat Schedule

```python
celery_app.conf.beat_schedule = {
    'aggregate-analytics-hourly': {
        'task': 'workers.tasks.aggregate_analytics_task',
        'schedule': crontab(minute=0),  # Every hour
    },
}
```

---

## Troubleshooting

### Worker Not Starting

```bash
# Check Redis connection
redis-cli ping
# Should return: PONG

# Check Redis URL
echo $REDIS_URL

# Test connection
poetry run python -c "from celery import Celery; app = Celery(broker='redis://localhost:6379'); print(app.broker_connection().connect())"
```

### Tasks Not Running

```bash
# Check worker is registered
celery -A workers inspect registered

# Check active tasks
celery -A workers inspect active

# Check if queue has tasks
celery -A workers inspect reserved
```

### Tasks Failing

```bash
# View failed tasks
celery -A workers inspect failed

# Check worker logs
celery -A workers worker --loglevel=debug

# Check task traceback
from celery.result import AsyncResult
result = AsyncResult(task_id)
print(result.traceback)
```

### Beat Not Scheduling

```bash
# Check beat is running
ps aux | grep celery

# Check schedule
celery -A workers inspect scheduled

# Force trigger (for testing)
from workers.tasks import aggregate_analytics_task
aggregate_analytics_task.delay()
```

---

## Performance Tips

1. **Concurrency**: Use multiple workers for parallel processing
   ```bash
   celery -A workers worker --concurrency=4
   ```

2. **Prefetch**: Limit prefetch for long tasks
   ```python
   worker_prefetch_multiplier=1
   ```

3. **Batch Processing**: Commit database changes in batches
   ```python
   for i, item in enumerate(items):
       process(item)
       if i % 100 == 0:
           db.commit()
   ```

4. **Task Routing**: Use different queues for different priorities
   ```python
   batch_analyze_task.apply_async(args=[texts], queue='high_priority')
   ```

---

## Next Steps

- Implement actual ML training in `train_model_task` (prompt f)
- Implement actual sentiment analysis in `batch_analyze_task` (prompt f)
- Add more scheduled tasks (daily reports, model retraining)
- Implement task progress tracking in frontend
- Add task result caching
