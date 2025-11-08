# Instrumentation Guide

Comprehensive observability setup with OpenTelemetry, Prometheus, Grafana, and structured logging.

## Overview

This project implements full-stack observability using:

1. **OpenTelemetry** - Distributed tracing and metrics
2. **Prometheus** - Metrics collection and alerting
3. **Grafana** - Visualization dashboards
4. **Jaeger** - Distributed tracing UI
5. **Structured Logging** - JSON logs with correlation IDs

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   FastAPI   │────▶│ OpenTelemetry│────▶│   Jaeger     │
│     API     │     │   Collector  │     │   (Traces)   │
└─────────────┘     └──────────────┘     └──────────────┘
       │                    │                     │
       │                    ▼                     │
       │            ┌──────────────┐              │
       ├───────────▶│  Prometheus  │              │
       │            │  (Metrics)   │              │
       │            └──────────────┘              │
       │                    │                     │
       │                    ▼                     │
       │            ┌──────────────┐              │
       └───────────▶│   Grafana    │◀─────────────┘
                    │ (Dashboards) │
                    └──────────────┘
```

## Quick Start

### 1. Start Observability Stack

```bash
cd sentiment-analysis

# Start all services
docker-compose up -d

# Verify services
docker-compose ps
```

Services available at:
- **API**: http://localhost:8000
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)
- **Jaeger**: http://localhost:16686

### 2. Enable Instrumentation

```bash
# Set environment variables
export ENABLE_TRACING=true
export ENABLE_METRICS=true
export PROMETHEUS_PORT=9090
export JAEGER_ENDPOINT=localhost:6831

# Start API with instrumentation
cd apps/api
poetry run uvicorn main:app --reload
```

### 3. Import Grafana Dashboards

1. Open Grafana: http://localhost:3001
2. Login (admin/admin)
3. Go to Dashboards → Import
4. Upload JSON files from `observability/grafana/dashboards/`

## Metrics

### Custom Metrics

#### Sentiment Analysis Metrics

**`sentiment_predictions_total`** (Counter)
- Total number of sentiment predictions
- Labels: `sentiment`, `source`

```promql
# Prediction rate by sentiment
rate(sentiment_predictions_total[5m])

# Total predictions in last hour
sum(increase(sentiment_predictions_total[1h]))
```

**`sentiment_prediction_duration_seconds`** (Histogram)
- Time spent on sentiment prediction
- Labels: `model_version`

```promql
# P95 prediction latency
histogram_quantile(0.95, rate(sentiment_prediction_duration_seconds_bucket[5m]))

# Average prediction time
rate(sentiment_prediction_duration_seconds_sum[5m]) / rate(sentiment_prediction_duration_seconds_count[5m])
```

**`sentiment_batch_size`** (Histogram)
- Size of batch analysis requests

```promql
# Average batch size
rate(sentiment_batch_size_sum[5m]) / rate(sentiment_batch_size_count[5m])
```

#### Model Metrics

**`model_training_duration_seconds`** (Histogram)
- Time spent training models

```promql
# P95 training time
histogram_quantile(0.95, rate(model_training_duration_seconds_bucket[1h]))
```

**`model_f1_score`** (Gauge)
- F1 score of the active model
- Labels: `model_name`

```promql
# Current model F1 score
model_f1_score

# Alert if F1 < 0.70
model_f1_score < 0.70
```

#### API Metrics

**`http_active_requests`** (Gauge)
- Number of active HTTP requests
- Labels: `method`, `endpoint`

```promql
# Total active requests
sum(http_active_requests)
```

#### Database Metrics

**`database_pool_size`** (Gauge)
- Current database connection pool size

**`database_pool_overflow`** (Gauge)
- Current database connection pool overflow

```promql
# Pool utilization
database_pool_overflow > 0
```

#### Celery Metrics

**`celery_tasks_total`** (Counter)
- Total number of Celery tasks
- Labels: `task_name`, `status`

```promql
# Task failure rate
rate(celery_tasks_total{status="failure"}[5m]) / rate(celery_tasks_total[5m])
```

**`celery_task_duration_seconds`** (Histogram)
- Time spent executing Celery tasks
- Labels: `task_name`

### Using Metrics in Code

```python
from instrumentation import (
    record_prediction,
    record_batch_analysis,
    record_model_training,
    record_celery_task
)

# Record a prediction
record_prediction(
    sentiment="positive",
    source="api",
    duration=0.005,
    model_version="1.0.0"
)

# Record batch analysis
record_batch_analysis(batch_size=100)

# Record model training
record_model_training(
    duration=120.5,
    f1_score=0.82,
    model_name="model_v2"
)

# Record Celery task
record_celery_task(
    task_name="train_model_task",
    status="success",
    duration=125.3
)
```

## Tracing

### Distributed Tracing with OpenTelemetry

Tracing is automatically enabled for:
- HTTP requests (FastAPI)
- Database queries (SQLAlchemy)
- Redis operations
- Celery tasks

### Custom Spans

```python
from instrumentation import get_tracer

tracer = get_tracer(__name__)

def analyze_sentiment(text: str):
    with tracer.start_as_current_span("analyze_sentiment") as span:
        span.set_attribute("text.length", len(text))
        span.set_attribute("model.version", "1.0.0")

        # Your code here
        result = predictor.predict(text)

        span.set_attribute("sentiment", result['predicted_label'])
        span.set_attribute("confidence", result['confidence'])

        return result
```

### Viewing Traces

1. Open Jaeger UI: http://localhost:16686
2. Select service: `sentiment-analysis-api`
3. Find traces by operation or tags
4. View detailed spans and timing

## Logging

### Structured Logging

Logs are structured JSON with correlation IDs for request tracing.

#### Configuration

```python
from logging_config import setup_logging

# Initialize logging
setup_logging()
```

#### Using Structured Logs

```python
from logging_config import (
    get_logger,
    log_api_request,
    log_prediction,
    log_model_training,
    log_error
)

logger = get_logger(__name__)

# Log API request
log_api_request(
    logger,
    method="POST",
    path="/analyze",
    status_code=200,
    duration_ms=5.2,
    user_id="123"
)

# Log prediction
log_prediction(
    logger,
    text="This is great!",
    predicted_sentiment="positive",
    confidence=0.87,
    duration_ms=3.1,
    model_version="1.0.0"
)

# Log model training
log_model_training(
    logger,
    model_name="model_v2",
    training_samples=5000,
    f1_score=0.82,
    duration_seconds=125.5
)

# Log error
try:
    risky_operation()
except Exception as e:
    log_error(logger, e, context="prediction")
```

#### Log Format

**JSON Format** (production):
```json
{
  "timestamp": "2024-11-07T20:00:00.123Z",
  "level": "INFO",
  "logger": "api.routes",
  "message": "Predicted positive with 87% confidence",
  "correlation_id": "abc123-def456",
  "service": "sentiment-analysis-api",
  "environment": "production",
  "version": "1.0.0",
  "event_type": "prediction",
  "predicted_sentiment": "positive",
  "confidence": 0.87,
  "duration_ms": 3.1
}
```

**Text Format** (development):
```
2024-11-07 20:00:00 [abc123-def456] INFO api.routes - Predicted positive with 87% confidence
```

### Correlation IDs

Correlation IDs link requests across services and logs.

```python
from logging_config import set_correlation_id, get_correlation_id

# In middleware
@app.middleware("http")
async def correlation_id_middleware(request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid4()))
    set_correlation_id(correlation_id)

    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response
```

## Alerts

### Prometheus Alerts

Alerts are configured in `observability/prometheus/alerts/api_alerts.yml`.

#### Critical Alerts

**High Error Rate**
```yaml
alert: HighErrorRate
expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
for: 5m
severity: critical
```

**Database Pool Exhausted**
```yaml
alert: DatabasePoolExhausted
expr: database_pool_overflow > 0
for: 5m
severity: critical
```

#### Warning Alerts

**High Latency**
```yaml
alert: HighLatency
expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1.0
for: 5m
severity: warning
```

**Low Model F1 Score**
```yaml
alert: LowModelF1Score
expr: model_f1_score < 0.70
for: 1m
severity: warning
```

### Viewing Alerts

1. Open Prometheus: http://localhost:9090
2. Go to "Alerts" tab
3. View firing and pending alerts

### Alert Notifications

Configure Alertmanager for notifications:

```yaml
# alertmanager.yml
route:
  group_by: ['alertname', 'severity']
  receiver: 'slack'

receivers:
  - name: 'slack'
    slack_configs:
      - api_url: 'YOUR_SLACK_WEBHOOK_URL'
        channel: '#alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ .CommonAnnotations.description }}'
```

## Dashboards

### Available Dashboards

#### 1. API Overview
- Request rate
- Error rate
- P95 latency
- Active requests
- Predictions by sentiment

**Import**: `observability/grafana/dashboards/api-overview.json`

#### 2. ML Metrics
- Model training duration
- Batch analysis distribution
- Celery task execution
- Sentiment distribution
- Model F1 score

**Import**: `observability/grafana/dashboards/ml-metrics.json`

### Creating Custom Dashboards

1. Open Grafana: http://localhost:3001
2. Click "+" → "Dashboard"
3. Add panels with PromQL queries
4. Save dashboard

**Example Query**:
```promql
# Request rate by endpoint
sum(rate(http_requests_total[5m])) by (endpoint)

# Error percentage
(rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])) * 100

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

## Performance Monitoring

### Key Metrics to Monitor

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| P95 Latency | <20ms | >50ms |
| Error Rate | <1% | >5% |
| Prediction Throughput | >100/s | <10/s |
| Model F1 Score | >0.75 | <0.70 |
| Database Pool | <80% | 100% (overflow) |
| Task Failure Rate | <5% | >10% |

### SLIs and SLOs

**Service Level Indicators (SLIs)**:
- Latency: P95 request duration
- Availability: % of successful requests
- Throughput: Requests per second

**Service Level Objectives (SLOs)**:
- 99% of requests complete in <100ms
- 99.9% availability
- Support 1000+ req/s

## Troubleshooting

### No Metrics Appearing

**Check Prometheus targets**:
1. Open Prometheus: http://localhost:9090
2. Go to Status → Targets
3. Ensure all targets are "UP"

**Check API metrics endpoint**:
```bash
curl http://localhost:9090/metrics
```

### Traces Not Showing in Jaeger

**Check Jaeger connection**:
```bash
# Test Jaeger endpoint
curl http://localhost:14268/api/traces

# Check environment variables
echo $JAEGER_ENDPOINT
```

**Verify tracing is enabled**:
```python
# In code
from config import get_settings
settings = get_settings()
print(f"Tracing enabled: {settings.ENABLE_TRACING}")
```

### High Memory Usage

**Check metrics**:
```promql
# Memory usage
process_resident_memory_bytes

# Database pool size
database_pool_size
```

**Solutions**:
- Reduce database pool size
- Limit concurrent requests
- Optimize batch sizes

### Slow Queries

**View slow queries in traces**:
1. Open Jaeger
2. Search for spans with tag: `db.statement`
3. Sort by duration

**Enable SQLAlchemy query logging**:
```python
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

## Production Deployment

### Environment Variables

```bash
# Observability
ENABLE_TRACING=true
ENABLE_METRICS=true
PROMETHEUS_PORT=9090
JAEGER_ENDPOINT=jaeger:6831
OTLP_ENDPOINT=http://otel-collector:4318

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Service info
ENVIRONMENT=production
VERSION=1.0.0
```

### Cloud Providers

#### AWS

**Use Amazon Managed Prometheus and Grafana**:
```bash
# Send metrics to AMP
OTLP_ENDPOINT=https://aps-workspaces.us-east-1.amazonaws.com/workspaces/ws-xxx

# Use CloudWatch for logs
# Use X-Ray for tracing
```

#### GCP

**Use Google Cloud Monitoring**:
```bash
# Send to Cloud Monitoring
OTLP_ENDPOINT=https://monitoring.googleapis.com/v1/projects/PROJECT_ID

# Use Cloud Logging
# Use Cloud Trace
```

#### Azure

**Use Azure Monitor**:
```bash
# Send to Azure Monitor
OTLP_ENDPOINT=https://DC_ENDPOINT.monitor.azure.com

# Use Application Insights
```

### Security

**Protect metrics endpoint**:
```python
# In FastAPI
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

@app.get("/metrics")
async def metrics(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != "admin" or credentials.password != "secret":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    # Return metrics
```

**Use TLS for OTLP**:
```python
# In instrumentation.py
otlp_exporter = OTLPSpanExporter(
    endpoint=settings.OTLP_ENDPOINT,
    insecure=False,  # Use TLS
    credentials=ChannelCredentials(
        root_certificates=open('/path/to/ca.pem', 'rb').read()
    )
)
```

## Best Practices

### Metrics

✅ **Do**:
- Use labels sparingly (high cardinality = memory issues)
- Increment counters, don't set them
- Use histograms for latency
- Record duration in seconds

❌ **Don't**:
- Use user IDs as labels
- Create metrics in hot paths without caching
- Use high-cardinality labels
- Mix units (use seconds, not milliseconds)

### Tracing

✅ **Do**:
- Add meaningful span attributes
- Create spans for significant operations
- Propagate context across services
- Sample traces in production (e.g., 10%)

❌ **Don't**:
- Create spans for every function call
- Add PII to span attributes
- Forget to close spans
- Trace health checks

### Logging

✅ **Do**:
- Use structured logging
- Include correlation IDs
- Log at appropriate levels
- Add context to logs

❌ **Don't**:
- Log sensitive data (passwords, tokens)
- Log in tight loops
- Use print() instead of logger
- Over-log in production

## Advanced Topics

### Custom Exporters

Create custom exporters for specific backends:

```python
from opentelemetry.sdk.trace.export import SpanExporter

class CustomExporter(SpanExporter):
    def export(self, spans):
        for span in spans:
            # Send to custom backend
            pass
```

### Sampling

Configure sampling to reduce trace volume:

```python
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

# Sample 10% of traces
sampler = TraceIdRatioBased(0.1)

tracer_provider = TracerProvider(
    resource=resource,
    sampler=sampler
)
```

### Multi-Service Tracing

Propagate context across services:

```python
from opentelemetry.propagate import inject
import httpx

# Inject trace context into headers
headers = {}
inject(headers)

# Make request with context
async with httpx.AsyncClient() as client:
    await client.post("http://other-service/api", headers=headers)
```

## Resources

- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [Prometheus Query Documentation](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [Structured Logging Best Practices](https://www.structlog.org/)

## Next Steps

- [ ] Set up alerting notifications (Slack, PagerDuty)
- [ ] Create service-level agreement (SLA) dashboards
- [ ] Implement distributed tracing across all services
- [ ] Set up log aggregation (ELK, Loki)
- [ ] Configure long-term metrics storage
- [ ] Create runbooks for common alerts
- [ ] Implement chaos engineering tests
