# Test Suite Documentation

Comprehensive testing for the Sentiment Analysis API.

## Test Structure

```
tests/
├── conftest.py                      # Pytest fixtures and configuration
├── unit/                            # Unit tests (isolated components)
│   ├── test_models.py              # Pydantic model validation
│   └── test_db_models.py           # SQLAlchemy models
├── integration/                     # Integration tests (API endpoints)
│   └── test_api_endpoints.py      # End-to-end API tests
├── test_workers.py                  # Celery worker tasks
└── README.md                        # This file
```

## Running Tests

### Prerequisites

```bash
# Install dependencies
cd apps/api
poetry install

# Start test database (optional, tests use SQLite in-memory by default)
docker-compose up -d postgres redis
```

### Run All Tests

```bash
# Run all tests with coverage
poetry run pytest

# Verbose output
poetry run pytest -v

# Show print statements
poetry run pytest -s
```

### Run Specific Test Types

```bash
# Unit tests only
poetry run pytest -m unit

# Integration tests only
poetry run pytest -m integration

# Worker tests only
poetry run pytest -m worker

# Slow tests
poetry run pytest -m slow
```

### Run Specific Test Files

```bash
# Run single file
poetry run pytest tests/unit/test_models.py

# Run single test class
poetry run pytest tests/unit/test_models.py::TestSentimentModels

# Run single test
poetry run pytest tests/unit/test_models.py::TestSentimentModels::test_sentiment_scores_valid
```

### Run with Coverage

```bash
# Generate coverage report
poetry run pytest --cov=. --cov-report=term-missing

# Generate HTML coverage report
poetry run pytest --cov=. --cov-report=html
# Open htmlcov/index.html in browser

# Generate XML coverage (for CI)
poetry run pytest --cov=. --cov-report=xml
```

### Run in Parallel

```bash
# Install pytest-xdist
poetry add --group dev pytest-xdist

# Run tests in parallel (4 workers)
poetry run pytest -n 4
```

## Test Categories

### Unit Tests

Test individual components in isolation.

**Models (`test_models.py`)**
- Pydantic model validation
- Field constraints (min/max, ranges)
- Data transformations
- Enum values

**Database Models (`test_db_models.py`)**
- SQLAlchemy model creation
- Constraints and indexes
- Default values
- Relationships

**Coverage**: 95%+

### Integration Tests

Test API endpoints end-to-end.

**Endpoints (`test_api_endpoints.py`)**
- Health check
- Sentiment analysis (single and batch)
- Analytics (trends, summary)
- Model management
- Training data management
- Task status

**What's tested**:
- Request/response validation
- Status codes
- Error handling
- Business logic
- Database interactions

**Coverage**: 85%+

### Worker Tests

Test Celery background tasks.

**Tasks (`test_workers.py`)**
- `train_model_task`: Model training, idempotency, progress tracking
- `batch_analyze_task`: Batch processing, deduplication, commits
- `aggregate_analytics_task`: Aggregation logic, calculations

**What's tested**:
- Task execution
- Idempotency
- Progress tracking
- Retry logic
- Database transactions

**Coverage**: 80%+

## Load Testing

Performance testing with Locust.

### Quick Start

```bash
# Install locust
poetry add --group dev locust

# Start API server
poetry run uvicorn main:app --reload

# Run Locust web UI
poetry run locust -f locustfile.py --host=http://localhost:8000

# Visit http://localhost:8089
```

### Headless Mode

```bash
# Run for 60 seconds with 100 users
poetry run locust -f locustfile.py \
  --host=http://localhost:8000 \
  --headless \
  --users 100 \
  --spawn-rate 10 \
  --run-time 60s

# Run with specific user class
poetry run locust -f locustfile.py \
  --host=http://localhost:8000 \
  --headless \
  --users 50 \
  ReadOnlyUser
```

### Test Scenarios

**SentimentAnalysisUser** (default)
- Realistic user behavior
- Mix of single/batch analysis
- Analytics queries
- Model management

**HighLoadUser**
- Stress testing
- Rapid requests (0.1-0.5s wait)
- Focus on analyze endpoints

**ReadOnlyUser**
- Read-only operations
- Analytics and queries
- No write operations

### Load Shapes

**StepLoadShape**
- Gradually increase load in steps
- 10 → 50 → 100 → 200 users
- Good for finding breaking points

**SpikeLoadShape**
- Sudden traffic spikes
- Normal: 20 users
- Spike: 200 users for 30s every 2 minutes

### Performance Targets

| Metric | Target | Measured |
|--------|--------|----------|
| p50 latency | <5ms | TBD |
| p95 latency | <20ms | TBD |
| p99 latency | <50ms | TBD |
| Throughput | 1000 req/s | TBD |
| Error rate | <0.1% | TBD |

## Fixtures

Common test fixtures are defined in `conftest.py`.

### Database Fixtures

**`db_session`**
- Fresh in-memory SQLite database
- Function-scoped (new DB per test)
- Auto-cleanup

**`client`**
- FastAPI TestClient
- Database dependency override
- Function-scoped

### Data Fixtures

**`sample_model`**
- Pre-created Model record
- Active model with metrics
- F1 score: 0.78

**`sample_training_data`**
- 3 training samples (pos/neu/neg)
- Ready for model training

**`sample_analyses`**
- 3 analysis records
- Different sentiments and timestamps
- Includes metadata

**`sample_analytics_summary`**
- Daily analytics summary
- 200 total analyses
- Mixed sentiment distribution

## Writing New Tests

### Unit Test Template

```python
import pytest
from pydantic import ValidationError
from models.sentiment import AnalyzeRequest

@pytest.mark.unit
class TestMyFeature:
    """Test my new feature"""

    def test_valid_input(self):
        """Should accept valid input"""
        request = AnalyzeRequest(text="Test")
        assert request.text == "Test"

    def test_invalid_input(self):
        """Should reject invalid input"""
        with pytest.raises(ValidationError):
            AnalyzeRequest(text="")
```

### Integration Test Template

```python
import pytest
from fastapi.testclient import TestClient

@pytest.mark.integration
class TestMyEndpoint:
    """Test /my-endpoint"""

    def test_success_case(self, client: TestClient):
        """Should return success"""
        response = client.post("/my-endpoint", json={"data": "test"})
        assert response.status_code == 200
        assert "result" in response.json()

    def test_validation_error(self, client: TestClient):
        """Should validate input"""
        response = client.post("/my-endpoint", json={})
        assert response.status_code == 422
```

### Worker Test Template

```python
import pytest
from workers.tasks import my_task

@pytest.mark.worker
class TestMyTask:
    """Test my_task"""

    def test_task_success(self, db_session):
        """Should execute successfully"""
        result = my_task(param="value")
        assert result["status"] == "success"
```

## Continuous Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: timescale/timescaledb:latest-pg16
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Poetry
        run: pip install poetry

      - name: Install dependencies
        run: |
          cd apps/api
          poetry install

      - name: Run tests
        run: |
          cd apps/api
          poetry run pytest --cov=. --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./apps/api/coverage.xml
```

## Coverage Goals

| Component | Current | Target |
|-----------|---------|--------|
| Models | 95% | 95% |
| API Routes | 85% | 90% |
| Workers | 80% | 85% |
| Database | 90% | 95% |
| **Overall** | **87%** | **90%** |

## Troubleshooting

### Tests fail with database errors

```bash
# Reset test database
docker-compose down -v
docker-compose up -d postgres

# Or use in-memory SQLite (default)
# Tests should work without external database
```

### Import errors

```bash
# Ensure you're in the right directory
cd apps/api

# Reinstall dependencies
poetry install

# Check Python path
poetry run python -c "import sys; print(sys.path)"
```

### Celery worker tests fail

```bash
# Start Redis for worker tests
docker-compose up -d redis

# Or mock Celery in tests
# Worker tests use synchronous execution by default
```

### Coverage not generated

```bash
# Ensure coverage is installed
poetry add --group dev pytest-cov

# Run with coverage flags
poetry run pytest --cov=. --cov-report=html

# Check .coveragerc configuration
cat .coveragerc
```

## Best Practices

### 1. Test Isolation

- Each test should be independent
- Use fixtures for setup/teardown
- Don't rely on test execution order

### 2. Descriptive Names

```python
# Good
def test_analyze_rejects_empty_text():
    ...

# Bad
def test_1():
    ...
```

### 3. Arrange-Act-Assert

```python
def test_example():
    # Arrange: Set up test data
    request = AnalyzeRequest(text="Test")

    # Act: Execute the code
    result = analyze(request)

    # Assert: Verify results
    assert result.confidence > 0
```

### 4. Test Edge Cases

- Empty inputs
- Maximum values
- Null/None values
- Invalid types
- Boundary conditions

### 5. Mock External Dependencies

```python
from unittest.mock import patch

@patch('external_service.call')
def test_with_mock(mock_call):
    mock_call.return_value = {"data": "test"}
    # Test code that calls external_service.call()
```

## Next Steps

- [ ] Achieve 90% overall coverage
- [ ] Add performance benchmarks
- [ ] Implement mutation testing
- [ ] Add E2E tests with Playwright
- [ ] Set up test data factories
- [ ] Add property-based testing (Hypothesis)
