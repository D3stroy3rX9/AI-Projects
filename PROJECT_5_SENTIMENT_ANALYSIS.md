# Project 5: Real-Time Sentiment Analysis Dashboard

## Overview
A production-grade sentiment analysis system that classifies text sentiment (positive, neutral, negative) and emotions (joy, anger, sadness, surprise) using **classical machine learning** (scikit-learn). Processes 10,000+ samples/second on a single CPU, provides real-time analytics dashboard, and supports custom model training. Built for analyzing customer reviews, social media, support tickets, or any text feedback at scale.

## Architecture
- **Frontend**: Next.js 14 App Router + Chart.js for real-time visualizations
- **API**: Python FastAPI with async/await for high throughput
- **ML**: scikit-learn (Multinomial Naive Bayes + TF-IDF)
  - Training: <1 minute on 100k samples
  - Inference: <5ms per prediction
  - Model size: <10MB serialized
- **Database**: Postgres + TimescaleDB (time-series analytics)
- **Queue**: Celery + Redis for batch processing
- **Cache**: Redis for predictions (70%+ cache hit rate)
- **Deployment**: Railway + Vercel (both free tier)

## Key Engineering Concerns
- **High Throughput**: Process 10k samples/sec on single CPU core
- **Explainability**: Show which words influenced the prediction (feature importance)
- **Custom Training**: Upload labeled data, retrain model in <1 min
- **Real-time Analytics**: Time-series sentiment trends, rolling averages
- **Multi-source**: API, batch CSV upload, webhook integrations
- **Idempotency**: Dedupe on content hash, don't re-analyze same text
- **Pagination**: Cursor-based on (analyzed_at, id) composite
- **A/B Testing**: Compare multiple model versions in production

## ML System Details
- **Feature Engineering**:
  - TF-IDF vectorization (10k vocabulary, bigrams + unigrams)
  - Lowercase normalization, stop word removal (customizable)
  - Handle emojis, URLs, mentions (@user)
  - N-gram features (1-2 grams for context)

- **Model Architecture**:
  - **Sentiment**: Multinomial Naive Bayes (3-class: pos/neu/neg)
  - **Emotion**: Multi-label classifier (joy, anger, sadness, surprise, fear, love)
  - **Training data**: Use public datasets (Stanford Sentiment, GoEmotions)
  - **Incremental learning**: Update model with new labeled data

- **Performance Optimizations**:
  - Vectorizer stored in memory (avoid disk I/O)
  - Batch predictions (100 at a time)
  - Cache frequent phrases (Redis, 1hr TTL)
  - Compressed model files (joblib with compression)

- **Evaluation Metrics**:
  - F1 score per class (target: >0.75)
  - Confusion matrix (identify misclassifications)
  - Calibration curve (confidence accuracy)
  - Feature importance (top 50 words per class)

- **Latency Target**: p95 < 10ms for single prediction, < 100ms for batch of 100
- **Accuracy Target**: F1 > 0.75 (competitive with BERT for sentiment)
- **Throughput**: 10k predictions/sec on 4-core CPU
- **Cost**: $0/month (no APIs, runs on free tier)

## Prompts for Claude Code Pairing

### a) Scaffold
```
Create a monorepo with:
- apps/web: Next.js 14 with App Router, TypeScript, Tailwind CSS, Chart.js for visualizations, TanStack Query
- apps/api: Python FastAPI with uvicorn, async endpoints, poetry for dependency management
  - Dependencies: fastapi, scikit-learn, pandas, numpy, redis, celery, sqlalchemy, asyncpg
- packages/ml: Python module for model training, inference, evaluation
  - Separate module for reusability
- Root pyproject.toml with workspace configuration
- docker-compose.yml: postgres, timescaledb extension, redis
- Dockerfile for FastAPI (multi-stage build, python:3.11-slim base)
- .env.example with required configuration
- Basic README with project structure
```

### b) Contracts
```
Write OpenAPI 3.1 spec (openapi.yaml) with these endpoints:
- POST /analyze (single text sentiment analysis, returns scores + explanation)
- POST /analyze/batch (array of texts, returns array of predictions)
- GET /analytics/trends (time-series sentiment over time, query params: start_date, end_date, interval)
- GET /analytics/summary (aggregate stats: avg sentiment, distribution, top keywords)
- POST /models/train (upload labeled data CSV, trigger training job)
- GET /models (list available models with metrics)
- GET /models/{id}/evaluate (confusion matrix, F1 scores, feature importance)
- POST /webhooks/{source} (receive text from external sources)

Response schemas:
- SentimentResult: {text, sentiment: {positive, neutral, negative}, emotion: {joy, anger, ...}, explanation: {top_words: [{word, weight}]}, confidence}
- TrendPoint: {timestamp, avg_sentiment, count, distribution: {pos, neu, neg}}

Use openapi-python-client or datamodel-code-generator to generate Pydantic models.
Create TypeScript types for frontend using openapi-typescript.
```

### c) Data
```
Design SQLAlchemy models (alembic/models.py):
- Analysis: id, text_hash (unique index), text, sentiment_scores jsonb (pos/neu/neg), emotion_scores jsonb, predicted_label, confidence, analyzed_at (timestamp), source (api/batch/webhook), metadata jsonb
- Model: id, name, version, algorithm, f1_score, training_samples, vocabulary_size, created_at, is_active boolean
- TrainingData: id, text, label, source, created_at, used_in_training boolean
- AnalyticsSummary: id, date, hour, sentiment_avg, positive_count, neutral_count, negative_count, total_count (materialized view or aggregation)

Enable TimescaleDB extension for Analysis table (hypertable on analyzed_at).
Create indexes:
- text_hash (unique for idempotency)
- analyzed_at (for time-series queries)
- source (for filtering)
- (predicted_label, analyzed_at) composite for fast filtering

Write Alembic migrations in alembic/versions/.
Create seed script (seed.py):
- Download Stanford Sentiment Treebank dataset (or use sample)
- Insert 1000 sample analyses with realistic sentiment distribution (40% pos, 30% neu, 30% neg)
- Create initial model entry
```

### d) Workers
```
Set up Celery in apps/api/workers/:
- Configure Redis as broker and result backend
- Define tasks:
  1. train_model_task(training_data_ids):
     - Load data from DB
     - Train TF-IDF + Naive Bayes
     - Evaluate on test split
     - Save model to disk (models/{timestamp}-model.joblib)
     - Update Model table with metrics
  2. batch_analyze_task(texts, source):
     - Vectorize with TF-IDF
     - Predict batch
     - Store in DB with deduplication (check text_hash)
  3. aggregate_analytics_task():
     - Scheduled hourly
     - Compute hourly aggregates
     - Store in AnalyticsSummary

Make train_model_task idempotent: check if model with same data hash exists.
Add retry logic: 3 attempts, exponential backoff.
Implement progress tracking: report percentage during training for long jobs.
```

### e) Tests
```
Set up pytest in apps/api/tests/ with pytest-asyncio, httpx for async testing.

Unit tests (tests/unit/):
- test_tfidf_vectorization: verify vocabulary size, bigram extraction
- test_sentiment_prediction: known inputs → expected outputs
- test_text_preprocessing: emoji handling, URL removal, lowercase
- test_feature_importance: verify top words extracted correctly
- test_model_serialization: save/load model, predictions match

Integration tests (tests/integration/):
- test_analyze_endpoint: POST text → returns sentiment + explanation
- test_batch_analysis: 100 texts → all analyzed, no duplicates
- test_training_flow: upload CSV → train job → model created → predictions use new model
- test_analytics_trends: insert 100 analyses → query trends → correct aggregation
- test_idempotency: analyze same text twice → only 1 DB entry

Mock external dependencies with pytest-mock.

Performance test (tests/performance/):
- test_throughput: measure predictions/sec (assert > 1000/sec)
- Use locust or pytest-benchmark

Create locustfile.py for load testing:
- Simulate 100 concurrent users
- POST /analyze with random texts
- Assert p95 < 50ms
```

### f) AI
```
Implement ML pipeline in packages/ml/:

1. ModelTrainer class (trainer.py):
   - load_data(training_data_ids): fetch from DB or CSV
   - preprocess(texts): lowercase, remove stop words, handle emojis
   - train(texts, labels):
     - Split 80/20 train/test
     - Fit TF-IDF vectorizer (max_features=10000, ngram_range=(1,2))
     - Train MultinomialNB for sentiment
     - Train MultiOutputClassifier for emotions
     - Return metrics (F1, confusion matrix)
   - save_model(model, vectorizer, path)

2. Predictor class (predictor.py):
   - load_model(path): deserialize joblib
   - predict(text): vectorize → predict → return scores
   - explain(text, prediction): get top 10 feature weights
   - predict_batch(texts): vectorize batch → predict all

3. Evaluator class (evaluator.py):
   - evaluate(model, test_data): compute F1, precision, recall per class
   - confusion_matrix(predictions, labels)
   - feature_importance(vectorizer, model): top 50 words per class
   - calibration_curve(predictions, true_labels): confidence vs accuracy

Create eval harness (eval/run_eval.py):
- Load held-out test set (1000 samples from Stanford Sentiment)
- Run predictions
- Compute metrics:
  - Overall F1 (target >= 0.75)
  - Per-class F1 (pos, neu, neg)
  - Confusion matrix (identify common errors)
  - Top misclassified examples
- Save results to eval-results.json
- Assert F1 >= 0.75 (fail if below)

Provide sample datasets:
- Download Stanford Sentiment Treebank (train: 8000, test: 1000)
- Download GoEmotions (for emotion labels)
- Store in data/ directory
```

### g) CI/CD
```
Create .github/workflows/test.yml:
- On PR: run pytest with coverage
- Assert coverage >= 80%
- Run eval harness (python eval/run_eval.py)
- Assert F1 >= 0.75 (gate on model quality)
- Run locust load test (30s, 50 users)
- Assert p95 < 50ms

Create .github/workflows/build.yml (on main merge):
- Build Docker image for API
- Tag with git SHA and 'latest'
- Push to GitHub Container Registry (GHCR)
- Run smoke test: analyze sample text, assert response

Create .github/workflows/deploy.yml (manual trigger):
- Deploy to Railway (api) and Vercel (web)
- Run post-deploy health check
- Run smoke test on production URL

Add pre-commit hooks:
- black (Python formatting)
- flake8 (linting)
- mypy (type checking)
```

### h) Instrumentation
```
Integrate OpenTelemetry in apps/api/main.py:
- Use FastAPIInstrumentor for auto-instrumentation
- Add custom spans:
  - 'analyze_text' (tag: text_length, sentiment_label, confidence)
  - 'predict_batch' (tag: batch_size, avg_confidence)
  - 'train_model' (tag: training_samples, f1_score, duration)
  - 'aggregate_analytics' (tag: records_processed, date_range)
- Export traces to Jaeger or Tempo (docker-compose service)

Add Prometheus metrics:
- sentiment_predictions_total (counter, label: predicted_label)
- prediction_confidence_histogram (histogram)
- prediction_duration_seconds (histogram)
- model_f1_score (gauge, updated after training)
- cache_hit_rate (gauge, computed from Redis stats)

Create grafana/dashboard.json with panels:
1. Predictions per second (graph, by label)
2. Sentiment distribution over time (stacked area chart)
3. Prediction latency p50/p95/p99 (graph)
4. Model performance (F1 score gauge)
5. Cache hit rate (gauge)
6. Top positive/negative keywords (bar chart from feature importance)

Add observability stack to docker-compose.yml:
- Jaeger (tracing): port 16686
- Prometheus (metrics): port 9090
- Grafana (dashboards): port 3000

Include sample dashboard with pre-configured data sources.
```

## Success Metrics
- Train model on 10k samples in <60 seconds
- Predict single sample in <5ms p95
- Batch predict 100 samples in <50ms p95
- F1 score >= 0.75 on Stanford Sentiment test set
- Cache hit rate >= 70% in production
- Zero cost (runs on free tier)
- 80%+ test coverage
- Dashboard shows real-time sentiment trends

## Advanced Features (Optional Extensions)

### Aspect-Based Sentiment
Extract sentiment per aspect (e.g., "Great food but terrible service")
- Use dependency parsing (spaCy)
- Extract noun phrases
- Predict sentiment per phrase

### Comparative Sentiment
Track sentiment changes over time for same entity
- "Product X sentiment improved 15% this month"
- Alert on significant drops

### Keyword Extraction
Extract important phrases, not just words
- Use TF-IDF on n-grams
- Identify trending topics

### Multi-Language Support
Train separate models per language
- Detect language with langdetect
- Route to appropriate model

### Active Learning
Surface uncertain predictions for labeling
- Confidence < 0.6 → request human label
- Retrain model with new labels

## Dataset Sources (All Free)

1. **Stanford Sentiment Treebank**: 11,855 sentences from movie reviews
   - Labels: positive, negative, neutral
   - Download: https://nlp.stanford.edu/sentiment/

2. **IMDB Reviews**: 50k movie reviews
   - Labels: positive, negative
   - Download: https://ai.stanford.edu/~amaas/data/sentiment/

3. **GoEmotions**: 58k Reddit comments with emotion labels
   - Labels: 27 emotions + neutral
   - Download: https://github.com/google-research/google-research/tree/master/goemotions

4. **Twitter Sentiment140**: 1.6M tweets
   - Labels: positive, negative
   - Download: http://help.sentiment140.com/for-students

Use combinations for diverse training data.

## Why Classical ML vs Deep Learning?

### Advantages of Naive Bayes + TF-IDF:
✅ **Speed**: 100-1000x faster inference (<5ms vs 500ms)
✅ **Cost**: No GPU required, runs on free tier
✅ **Explainability**: Can show exact words that influenced decision
✅ **Training**: Minutes vs hours for BERT
✅ **Size**: 10MB model vs 500MB+ for BERT
✅ **Good enough**: F1 ~0.75-0.80 for sentiment (BERT: 0.85-0.90)

### When to use Deep Learning instead:
- Need >0.85 F1 (5-10% accuracy gain)
- Complex language (sarcasm, context-dependent)
- Multi-lingual (transformers handle better)
- Have GPU budget ($50-200/month)

**For portfolio projects**: Classical ML is perfect - shows ML fundamentals, not just API usage.

---

## Technical Deep Dive

### TF-IDF Vectorization
```python
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer(
    max_features=10000,      # Top 10k words by frequency
    ngram_range=(1, 2),      # Unigrams + bigrams
    min_df=5,                # Word must appear in 5+ docs
    max_df=0.8,              # Remove words in >80% docs
    stop_words='english',    # Remove common words
    sublinear_tf=True        # Log scaling for term frequency
)
```

### Naive Bayes Training
```python
from sklearn.naive_bayes import MultinomialNB

model = MultinomialNB(alpha=1.0)  # Laplace smoothing
model.fit(X_train, y_train)       # X_train: TF-IDF matrix
```

### Feature Importance
```python
# Get top words per class
feature_names = vectorizer.get_feature_names_out()
for idx, class_name in enumerate(['negative', 'neutral', 'positive']):
    top_indices = model.feature_log_prob_[idx].argsort()[-20:]
    top_words = [feature_names[i] for i in top_indices]
    print(f"{class_name}: {top_words}")
```

Output:
```
negative: ['terrible', 'worst', 'horrible', 'bad', 'waste', 'awful', 'boring', 'poor']
positive: ['excellent', 'amazing', 'great', 'best', 'love', 'perfect', 'wonderful', 'fantastic']
```

---

**Estimated Build Time**: 6-8 hours with Claude Code
**Cost**: $0/month
**Lines of Code**: ~2000 (including tests)
**Deployment**: Free tier sufficient for 10k+ requests/day
