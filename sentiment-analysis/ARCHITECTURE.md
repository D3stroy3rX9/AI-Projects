# Sentiment Analysis Dashboard - Architecture Overview

## 📋 Executive Summary

A production-grade sentiment analysis system using classical machine learning (TF-IDF + Naive Bayes) to classify text as positive, negative, or neutral. Built with FastAPI, Next.js, and TimescaleDB, featuring real-time analysis, background processing, and comprehensive observability.

---

## 🏗️ System Architecture

### High-Level Components

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Next.js   │ ───> │   FastAPI    │ ───> │ PostgreSQL  │
│  Frontend   │ <─── │   Backend    │ <─── │ TimescaleDB │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ├──> ML Pipeline (TF-IDF + NB)
                            │
                            ├──> Redis (Celery)
                            │
                            └──> Observability Stack
                                 (Prometheus, Jaeger, Grafana)
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 14, React, TypeScript, Tailwind CSS | User interface & visualization |
| **Backend** | FastAPI, Python 3.12, Pydantic | REST API & business logic |
| **ML Pipeline** | scikit-learn, pandas, numpy, joblib | Text classification & training |
| **Database** | PostgreSQL 16, TimescaleDB | Data persistence & time-series |
| **Cache/Queue** | Redis 7 | Celery broker & result backend |
| **Workers** | Celery, Celery Beat | Background tasks & scheduling |
| **Observability** | Prometheus, Jaeger, Grafana | Monitoring & tracing |
| **DevOps** | Docker Compose, GitHub Actions | Development & CI/CD |

---

## 🔄 Data Flow

### 1. Real-Time Analysis Flow

```
User Input (Text)
    ↓
Next.js Frontend
    ↓
HTTP POST /analyze
    ↓
FastAPI Backend
    ↓
┌─────────────────────────┐
│ 1. Text Preprocessing   │ → Remove URLs, lowercase, clean
│ 2. TF-IDF Vectorization │ → Convert to feature vectors
│ 3. Naive Bayes Predict  │ → Classify sentiment
│ 4. Calculate Confidence │ → Probability scores
└─────────────────────────┘
    ↓
Save to Database (Analysis table)
    ↓
Return JSON Response
    ↓
Display Results + Update Stats
```

### 2. Model Training Flow

```
Training Data (Database)
    ↓
Extract texts & labels
    ↓
┌──────────────────────────┐
│ Text Preprocessing        │
│ ├─ Remove special chars  │
│ ├─ Lowercase             │
│ └─ Tokenization          │
└──────────────────────────┘
    ↓
┌──────────────────────────┐
│ TF-IDF Vectorization     │
│ ├─ max_features: 5000    │
│ ├─ ngram_range: (1, 2)   │
│ └─ stop_words: english   │
└──────────────────────────┘
    ↓
Train/Test Split (80/20)
    ↓
┌──────────────────────────┐
│ Multinomial Naive Bayes  │
│ ├─ Fit on training data  │
│ └─ alpha: 0.1            │
└──────────────────────────┘
    ↓
Evaluate on Test Set
    ↓
Save Model (.joblib) + Metadata (Database)
```

### 3. Background Processing Flow

```
Celery Beat Scheduler (Hourly)
    ↓
trigger: aggregate_analytics_task
    ↓
Query Analysis table for last hour
    ↓
Calculate aggregates:
    ├─ Total count
    ├─ Sentiment distribution
    └─ Average sentiment score
    ↓
Save to AnalyticsSummary table
```

---

## 🗄️ Database Schema

### Entity Relationship Diagram

```
┌─────────────────────┐
│   TrainingData      │
├─────────────────────┤
│ id (PK)            │
│ text               │
│ label              │◄───┐
│ source             │    │
│ created_at         │    │
│ used_in_training   │    │
└─────────────────────┘    │
                           │
                           │ Used for training
                           │
┌─────────────────────┐    │
│      Models         │    │
├─────────────────────┤    │
│ id (PK)            │    │
│ name               │    │
│ version            │    │
│ algorithm          │────┤
│ f1_score           │
│ training_samples   │
│ vocabulary_size    │
│ created_at         │
│ is_active          │
│ model_path         │
│ metrics (JSONB)    │
└─────────────────────┘
         │
         │ Referenced by
         │
┌─────────────────────┐
│     Analysis        │ ◄── TimescaleDB Hypertable
├─────────────────────┤
│ id (PK)            │
│ text_hash (Unique) │
│ text               │
│ sentiment_scores   │ (JSONB: {pos, neu, neg})
│ emotion_scores     │ (JSONB: optional)
│ predicted_label    │ (ENUM: pos/neu/neg)
│ confidence         │
│ analyzed_at        │ ◄── Partition key
│ source             │ (ENUM: api/batch/webhook)
│ extra_metadata     │ (JSONB)
└─────────────────────┘
         │
         │ Aggregated into
         │
┌─────────────────────┐
│ AnalyticsSummary    │
├─────────────────────┤
│ id (PK)            │
│ date               │
│ hour               │
│ sentiment_avg      │
│ positive_count     │
│ neutral_count      │
│ negative_count     │
│ total_count        │
└─────────────────────┘
```

---

## 🧠 ML Pipeline Architecture

### Components

```
┌─────────────────────────────────────────────────┐
│              ML Pipeline (packages/ml/)          │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────┐    ┌──────────────┐          │
│  │ Preprocessor │───>│   Trainer    │          │
│  └──────────────┘    └──────────────┘          │
│         │                    │                  │
│         │                    ├──> Model.joblib  │
│         │                    └──> Vectorizer    │
│         │                                        │
│  ┌──────────────┐    ┌──────────────┐          │
│  │  Predictor   │<───│  Evaluator   │          │
│  └──────────────┘    └──────────────┘          │
│         │                    │                  │
│         └──> Predictions     └──> Metrics       │
│                                                  │
└─────────────────────────────────────────────────┘
```

### Algorithm Details

**TF-IDF (Term Frequency-Inverse Document Frequency)**
- Converts text to numerical feature vectors
- Captures word importance across documents
- Configuration:
  - Max features: 5000
  - N-grams: unigrams + bigrams (1-2 words)
  - Min document frequency: 2
  - Max document frequency: 90%
  - Stop words: English

**Multinomial Naive Bayes**
- Probabilistic classifier based on Bayes' theorem
- Well-suited for text classification
- Assumes feature independence
- Fast training and prediction
- Configuration:
  - Alpha (smoothing): 0.1

**Performance Metrics**
- Accuracy: Overall correctness
- Precision: True positives / (True positives + False positives)
- Recall: True positives / (True positives + False negatives)
- F1 Score: Harmonic mean of precision & recall
- Confusion Matrix: Per-class performance

---

## 🚀 API Endpoints

### Core Endpoints

| Endpoint | Method | Purpose | Request | Response |
|----------|--------|---------|---------|----------|
| `/` | GET | Root info | - | API metadata |
| `/health` | GET | Health check | - | Status, version |
| `/analyze` | POST | Analyze text | `{text: string}` | Sentiment result |
| `/stats` | GET | Dashboard stats | - | Analytics summary |
| `/docs` | GET | OpenAPI docs | - | Interactive docs |

### Request/Response Examples

**Analyze Sentiment:**
```json
POST /analyze
{
  "text": "This product is absolutely fantastic!"
}

Response:
{
  "text": "This product is absolutely fantastic!",
  "sentiment": {
    "positive": 0.85,
    "neutral": 0.10,
    "negative": 0.05
  },
  "confidence": 0.85,
  "predicted_label": "positive"
}
```

**Get Stats:**
```json
GET /stats

Response:
{
  "total_analyzed": 1247,
  "avg_sentiment": 0.23,
  "model_f1_score": 0.724
}
```

---

## 🔧 Background Workers

### Celery Tasks

**1. train_model_task**
- **Trigger**: Manual or API call
- **Purpose**: Train new ML model
- **Input**: List of training_data IDs
- **Output**: Model saved to disk + DB record
- **Features**:
  - Idempotency (checks if model exists)
  - Progress tracking
  - Retry on failure (max 3 attempts)
  - Metrics logging

**2. batch_analyze_task**
- **Trigger**: Manual or scheduled
- **Purpose**: Analyze multiple texts
- **Input**: Array of texts
- **Output**: Analysis results saved to DB
- **Features**:
  - Deduplication (text hash)
  - Bulk processing
  - Error handling per text

**3. aggregate_analytics_task**
- **Trigger**: Celery Beat (hourly)
- **Purpose**: Compute analytics summaries
- **Input**: Time range
- **Output**: Aggregated stats in DB
- **Features**:
  - Scheduled execution
  - Time-series aggregation
  - Performance optimization

---

## 📊 Observability Stack

### Monitoring Architecture

```
Application Metrics
    ↓
┌─────────────────┐
│  Prometheus     │ ← Scrapes metrics from FastAPI
│  (Port 9090)    │
└─────────────────┘
    ↓
┌─────────────────┐
│    Grafana      │ ← Visualizes metrics
│  (Port 3001)    │   - API performance
└─────────────────┘   - ML model stats
                      - System health

Application Traces
    ↓
┌─────────────────┐
│OpenTelemetry SDK│ ← Instruments code
└─────────────────┘
    ↓
┌─────────────────┐
│     Jaeger      │ ← Distributed tracing
│  (Port 16686)   │   - Request flows
└─────────────────┘   - Latency analysis
```

### Metrics Tracked

**Application Metrics:**
- `sentiment_predictions_total` - Total predictions by sentiment
- `sentiment_prediction_duration_seconds` - Prediction latency
- `http_requests_total` - API request count
- `http_request_duration_seconds` - Request latency
- `model_f1_score` - Current model accuracy

**System Metrics:**
- CPU usage
- Memory consumption
- Database connections
- Queue depth (Celery)

---

## 🔐 Security & Best Practices

### Implemented

✅ **Input Validation**
- Pydantic models for type safety
- Text length limits (10,000 chars)
- SQL injection prevention (ORM)

✅ **Data Privacy**
- Text hashing for deduplication
- No PII storage
- Configurable data retention

✅ **API Security**
- CORS configuration
- Rate limiting ready (commented)
- Health check endpoints

✅ **Error Handling**
- Graceful degradation
- Detailed logging
- User-friendly error messages

### Production Recommendations

🔒 **Add Authentication**
- JWT tokens
- API keys
- OAuth2 integration

🔒 **Enable HTTPS**
- TLS certificates
- Secure cookies
- HSTS headers

🔒 **Input Sanitization**
- HTML/script removal
- Content filtering
- Spam detection

---

## 📈 Scalability Considerations

### Horizontal Scaling

**Frontend:**
- Stateless Next.js instances
- CDN for static assets
- Load balancer (nginx/Traefik)

**Backend:**
- Multiple FastAPI workers (Gunicorn/Uvicorn)
- Load balancing
- API Gateway (Kong/AWS API Gateway)

**Workers:**
- Multiple Celery workers
- Task prioritization
- Auto-scaling based on queue depth

**Database:**
- Read replicas for analytics
- Connection pooling
- Query optimization
- TimescaleDB compression

### Performance Optimizations

**Implemented:**
- Database indexing (text_hash, labels, timestamps)
- Model caching (loaded once at startup)
- Deduplication (avoids re-analyzing same text)

**Future Improvements:**
- Redis caching for predictions
- Batch processing API endpoint
- Model versioning & A/B testing
- Feature store for ML

---

## 🧪 Testing Strategy

### Test Coverage

**Unit Tests:**
- Pydantic model validation
- ML preprocessing functions
- Database model constraints
- Utility functions

**Integration Tests:**
- API endpoint responses
- Database CRUD operations
- Celery task execution
- ML pipeline end-to-end

**Load Tests:**
- Locust scenarios
- Concurrent users simulation
- Performance benchmarking
- Stress testing

---

## 🚢 Deployment Architecture

### Docker Compose (Development)

```yaml
services:
  - postgres (TimescaleDB)
  - redis
  - jaeger (tracing)
  - prometheus (metrics)
  - grafana (dashboards)
  - api (FastAPI)
  - worker (Celery)
  - beat (Celery scheduler)
  - web (Next.js)
```

### Production (Recommended)

**Infrastructure:**
- Kubernetes cluster (EKS/GKE/AKS)
- Managed PostgreSQL (RDS/Cloud SQL)
- Managed Redis (ElastiCache/MemoryStore)
- Object storage (S3) for models
- Container registry (ECR/GCR/ACR)

**CI/CD Pipeline:**
- GitHub Actions workflows
- Automated testing
- Docker image building
- Multi-stage deployments
- Rollback capabilities

---

## 📚 Project Structure

```
sentiment-analysis/
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── main.py            # Application entry
│   │   ├── config.py          # Settings
│   │   ├── models/            # Pydantic models
│   │   ├── db/                # Database models & migrations
│   │   ├── workers/           # Celery tasks
│   │   ├── scripts/           # Utility scripts
│   │   └── tests/             # Test suites
│   │
│   └── web/                   # Next.js frontend
│       ├── app/               # App router pages
│       ├── components/        # React components
│       ├── lib/               # API client
│       └── types/             # TypeScript types
│
├── packages/
│   └── ml/                    # ML pipeline
│       ├── preprocessor.py
│       ├── trainer.py
│       ├── predictor.py
│       └── evaluator.py
│
├── observability/             # Monitoring configs
│   ├── prometheus/
│   └── grafana/
│
├── .github/workflows/         # CI/CD pipelines
├── docker-compose.yml         # Local development
└── SETUP.md                   # Setup instructions
```

---

## 🎯 Key Design Decisions

### Why Classical ML (not Deep Learning)?

✅ **Advantages:**
- No GPU required
- Fast training (minutes vs hours)
- Small model size (< 10MB)
- Explainable predictions
- Lower operational costs
- Easy to iterate

❌ **Limitations:**
- Lower accuracy (~70-75% vs 85-90%)
- Struggles with sarcasm
- Limited context understanding
- No transfer learning

**Conclusion:** Appropriate for portfolio/demonstration. Production systems handling complex language would benefit from BERT/transformers.

### Why TimescaleDB?

- Optimized for time-series queries
- PostgreSQL compatibility
- Automatic partitioning
- Compression for historical data
- SQL interface (familiar)

### Why Celery?

- Mature, battle-tested
- Flexible scheduling
- Multiple broker support
- Task retry mechanisms
- Monitoring tools

---

## 🔮 Future Enhancements

### Short-Term
- [ ] Batch upload API (CSV/JSON)
- [ ] Export functionality (download results)
- [ ] User authentication
- [ ] Rate limiting
- [ ] API versioning

### Medium-Term
- [ ] Multi-language support
- [ ] Emotion detection (beyond sentiment)
- [ ] Sarcasm detection
- [ ] Aspect-based sentiment analysis
- [ ] Historical trend visualization

### Long-Term
- [ ] Upgrade to BERT/RoBERTa
- [ ] Active learning pipeline
- [ ] Real-time streaming (Kafka)
- [ ] Mobile app (React Native)
- [ ] GraphQL API

---

## 📞 Support & Documentation

- **API Documentation**: http://localhost:8000/docs
- **Setup Guide**: [SETUP.md](./SETUP.md)
- **CI/CD Guide**: [CI_CD_GUIDE.md](./CI_CD_GUIDE.md)
- **Instrumentation**: [INSTRUMENTATION_GUIDE.md](./INSTRUMENTATION_GUIDE.md)
- **ML Package**: [packages/ml/README.md](./packages/ml/README.md)

---

## 📄 License & Credits

**Built with:**
- FastAPI (Sebastián Ramírez)
- Next.js (Vercel)
- scikit-learn (BSD)
- TimescaleDB (Apache 2.0)

**Author:** Claude & User Collaboration
**Version:** 1.0.0
**Last Updated:** 2025-01-08
