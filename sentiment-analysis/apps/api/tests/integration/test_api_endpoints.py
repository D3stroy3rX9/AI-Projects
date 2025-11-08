"""
Integration tests for API endpoints
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from db.models import Analysis, Model, TrainingData, SentimentLabelEnum, SourceEnum


@pytest.mark.integration
class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check(self, client: TestClient):
        """Should return health status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data


@pytest.mark.integration
class TestAnalyzeEndpoints:
    """Test sentiment analysis endpoints"""

    def test_analyze_single_text_success(self, client: TestClient, sample_model):
        """Should analyze single text successfully"""
        response = client.post(
            "/analyze",
            json={
                "text": "This product is amazing!",
                "include_emotions": True,
                "include_explanation": False
            }
        )
        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "text" in data
        assert "sentiment" in data
        assert "predicted_label" in data
        assert "confidence" in data
        assert "analyzed_at" in data

        # Check sentiment scores
        sentiment = data["sentiment"]
        assert "positive" in sentiment
        assert "neutral" in sentiment
        assert "negative" in sentiment

        # Scores should sum to ~1.0
        total = sentiment["positive"] + sentiment["neutral"] + sentiment["negative"]
        assert 0.99 <= total <= 1.01

        # Check confidence is in valid range
        assert 0.0 <= data["confidence"] <= 1.0

    def test_analyze_invalid_text_empty(self, client: TestClient):
        """Should reject empty text"""
        response = client.post(
            "/analyze",
            json={"text": ""}
        )
        assert response.status_code == 422  # Validation error

    def test_analyze_invalid_text_too_long(self, client: TestClient):
        """Should reject text over 10000 chars"""
        response = client.post(
            "/analyze",
            json={"text": "a" * 10001}
        )
        assert response.status_code == 422

    def test_analyze_with_emotions(self, client: TestClient, sample_model):
        """Should include emotion scores when requested"""
        response = client.post(
            "/analyze",
            json={
                "text": "I'm so happy!",
                "include_emotions": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "emotion" in data
        assert data["emotion"] is not None

    def test_batch_analyze_success(self, client: TestClient, sample_model):
        """Should analyze multiple texts"""
        response = client.post(
            "/analyze/batch",
            json={
                "texts": [
                    "Great product!",
                    "Terrible experience.",
                    "It's okay."
                ],
                "source": "api"
            }
        )
        assert response.status_code == 200
        data = response.json()

        assert "results" in data
        assert "analyzed_count" in data
        assert "skipped_count" in data
        assert "total_count" in data

        assert len(data["results"]) == 3
        assert data["analyzed_count"] == 3
        assert data["total_count"] == 3

    def test_batch_analyze_empty_list(self, client: TestClient):
        """Should reject empty texts list"""
        response = client.post(
            "/analyze/batch",
            json={"texts": []}
        )
        assert response.status_code == 422

    def test_batch_analyze_too_many(self, client: TestClient):
        """Should reject more than 1000 texts"""
        response = client.post(
            "/analyze/batch",
            json={"texts": ["text"] * 1001}
        )
        assert response.status_code == 422

    def test_batch_analyze_deduplication(self, client: TestClient, sample_model, db_session):
        """Should skip duplicate texts"""
        # First batch
        response1 = client.post(
            "/analyze/batch",
            json={
                "texts": ["Unique text 1", "Unique text 2"],
                "source": "api"
            }
        )
        assert response1.status_code == 200

        # Second batch with one duplicate
        response2 = client.post(
            "/analyze/batch",
            json={
                "texts": ["Unique text 1", "Unique text 3"],
                "source": "api"
            }
        )
        assert response2.status_code == 200
        data2 = response2.json()

        # Should have skipped one duplicate
        assert data2["skipped_count"] >= 1


@pytest.mark.integration
class TestAnalyticsEndpoints:
    """Test analytics endpoints"""

    def test_get_trends_last_7_days(self, client: TestClient, sample_analyses):
        """Should get trend data for last 7 days"""
        response = client.get("/analytics/trends?time_range=LAST_7_DAYS")
        assert response.status_code == 200
        data = response.json()

        assert "time_range" in data
        assert "data_points" in data
        assert isinstance(data["data_points"], list)

    def test_get_trends_custom_range(self, client: TestClient, sample_analyses):
        """Should get trends for custom date range"""
        now = datetime.now()
        start = (now - timedelta(days=3)).isoformat()
        end = now.isoformat()

        response = client.get(
            f"/analytics/trends?start_date={start}&end_date={end}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "data_points" in data

    def test_get_trends_invalid_time_range(self, client: TestClient):
        """Should reject invalid time range"""
        response = client.get("/analytics/trends?time_range=INVALID")
        assert response.status_code == 422

    def test_get_summary(self, client: TestClient, sample_analyses):
        """Should get analytics summary"""
        response = client.get("/analytics/summary")
        assert response.status_code == 200
        data = response.json()

        assert "total_analyzed" in data
        assert "sentiment_distribution" in data
        assert "avg_sentiment" in data
        assert "avg_confidence" in data

        # Check distribution structure
        dist = data["sentiment_distribution"]
        assert "positive" in dist
        assert "neutral" in dist
        assert "negative" in dist
        assert "total" in dist

    def test_get_summary_with_time_range(self, client: TestClient, sample_analyses):
        """Should get summary for specific time range"""
        response = client.get("/analytics/summary?time_range=LAST_24_HOURS")
        assert response.status_code == 200
        data = response.json()
        assert "total_analyzed" in data


@pytest.mark.integration
class TestModelEndpoints:
    """Test model management endpoints"""

    def test_list_models(self, client: TestClient, sample_model):
        """Should list all models"""
        response = client.get("/models")
        assert response.status_code == 200
        data = response.json()

        assert "models" in data
        assert len(data["models"]) >= 1

        # Check model structure
        model = data["models"][0]
        assert "id" in model
        assert "name" in model
        assert "version" in model
        assert "f1_score" in model
        assert "is_active" in model

    def test_get_active_model(self, client: TestClient, sample_model):
        """Should get active model"""
        response = client.get("/models/active")
        assert response.status_code == 200
        data = response.json()

        assert data["is_active"] is True
        assert "f1_score" in data

    def test_train_model_success(self, client: TestClient, sample_training_data):
        """Should start model training task"""
        training_ids = [item.id for item in sample_training_data]

        # Add more training data to meet minimum
        from db.models import TrainingData
        from tests.conftest import db_session

        response = client.post(
            "/models/train",
            json={
                "training_data_ids": training_ids,
                "model_name": "test_custom_model"
            }
        )

        # Should return task info (202 Accepted or 200 OK)
        assert response.status_code in [200, 202]
        data = response.json()
        assert "task_id" in data or "model_id" in data

    def test_train_model_insufficient_data(self, client: TestClient):
        """Should reject training with insufficient data"""
        response = client.post(
            "/models/train",
            json={
                "training_data_ids": [1, 2, 3]  # Less than minimum
            }
        )
        assert response.status_code == 422


@pytest.mark.integration
class TestTrainingDataEndpoints:
    """Test training data management endpoints"""

    def test_add_training_data_success(self, client: TestClient):
        """Should add training data"""
        response = client.post(
            "/training-data",
            json={
                "items": [
                    {"text": "Great product!", "label": "positive"},
                    {"text": "Terrible service.", "label": "negative"},
                    {"text": "It's okay.", "label": "neutral"}
                ],
                "source": "user_upload"
            }
        )
        assert response.status_code == 200
        data = response.json()

        assert "added_count" in data
        assert data["added_count"] == 3

    def test_add_training_data_empty_list(self, client: TestClient):
        """Should reject empty items list"""
        response = client.post(
            "/training-data",
            json={"items": []}
        )
        assert response.status_code == 422

    def test_list_training_data(self, client: TestClient, sample_training_data):
        """Should list training data with pagination"""
        response = client.get("/training-data?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data

        assert len(data["items"]) >= 1

    def test_list_training_data_filter_by_label(self, client: TestClient, sample_training_data):
        """Should filter by label"""
        response = client.get("/training-data?label=positive")
        assert response.status_code == 200
        data = response.json()

        # All items should be positive
        for item in data["items"]:
            assert item["label"] == "positive"

    def test_list_training_data_pagination(self, client: TestClient, sample_training_data):
        """Should paginate results"""
        response = client.get("/training-data?skip=1&limit=1")
        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) <= 1
        assert data["skip"] == 1
        assert data["limit"] == 1


@pytest.mark.integration
class TestTaskEndpoints:
    """Test background task endpoints"""

    def test_get_task_status_not_found(self, client: TestClient):
        """Should return 404 for non-existent task"""
        response = client.get("/tasks/invalid_task_id")
        assert response.status_code == 404

    def test_get_task_status_format(self, client: TestClient):
        """Should return task status format"""
        # This test would need a real task ID
        # Skipping for now as it requires Celery worker
        pass
