"""
Unit tests for Pydantic models
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from models.sentiment import (
    SentimentLabel,
    SentimentScores,
    EmotionScores,
    AnalyzeRequest,
    SentimentResult,
    BatchAnalyzeRequest,
    BatchAnalyzeResponse,
    Explanation,
)
from models.analytics import (
    TimeRange,
    TrendPoint,
    SentimentDistribution,
    TrendResponse,
    AnalyticsSummaryResponse,
)
from models.training import (
    TrainModelRequest,
    ModelInfo,
    TrainingDataItem,
    AddTrainingDataRequest,
)


class TestSentimentModels:
    """Test sentiment-related models"""

    def test_sentiment_scores_valid(self):
        """Valid sentiment scores should pass"""
        scores = SentimentScores(positive=0.7, neutral=0.2, negative=0.1)
        assert scores.positive == 0.7
        assert scores.neutral == 0.2
        assert scores.negative == 0.1

    def test_sentiment_scores_sum_validation(self):
        """Sentiment scores must sum to 1.0 (within tolerance)"""
        # This should pass (sums to 1.0)
        SentimentScores(positive=0.5, neutral=0.3, negative=0.2)

        # This should fail (sums to 1.5)
        with pytest.raises(ValidationError):
            SentimentScores(positive=0.7, neutral=0.5, negative=0.3)

    def test_sentiment_scores_range_validation(self):
        """Sentiment scores must be between 0 and 1"""
        with pytest.raises(ValidationError):
            SentimentScores(positive=1.5, neutral=0.0, negative=-0.5)

    def test_emotion_scores_valid(self):
        """Valid emotion scores should pass"""
        emotions = EmotionScores(
            joy=0.8, anger=0.1, sadness=0.05,
            surprise=0.02, fear=0.02, love=0.01
        )
        assert emotions.joy == 0.8
        assert emotions.anger == 0.1

    def test_analyze_request_valid(self):
        """Valid analyze request should pass"""
        request = AnalyzeRequest(
            text="This is a test",
            include_emotions=True,
            include_explanation=True
        )
        assert request.text == "This is a test"
        assert request.include_emotions is True

    def test_analyze_request_empty_text(self):
        """Empty text should fail validation"""
        with pytest.raises(ValidationError):
            AnalyzeRequest(text="")

    def test_analyze_request_text_too_long(self):
        """Text longer than 10000 chars should fail"""
        with pytest.raises(ValidationError):
            AnalyzeRequest(text="a" * 10001)

    def test_sentiment_result_valid(self):
        """Valid sentiment result should pass"""
        result = SentimentResult(
            text="Great product!",
            sentiment=SentimentScores(positive=0.85, neutral=0.10, negative=0.05),
            predicted_label=SentimentLabel.POSITIVE,
            confidence=0.85,
            analyzed_at=datetime.now()
        )
        assert result.predicted_label == SentimentLabel.POSITIVE
        assert result.confidence == 0.85

    def test_batch_analyze_request_valid(self):
        """Valid batch request should pass"""
        request = BatchAnalyzeRequest(
            texts=["Text 1", "Text 2", "Text 3"],
            source="api"
        )
        assert len(request.texts) == 3

    def test_batch_analyze_request_empty_list(self):
        """Empty texts list should fail"""
        with pytest.raises(ValidationError):
            BatchAnalyzeRequest(texts=[])

    def test_batch_analyze_request_too_many(self):
        """More than 1000 texts should fail"""
        with pytest.raises(ValidationError):
            BatchAnalyzeRequest(texts=["text"] * 1001)

    def test_explanation_valid(self):
        """Valid explanation should pass"""
        explanation = Explanation(
            top_positive_words=["great", "amazing"],
            top_negative_words=["terrible", "bad"],
            reasoning="Text contains positive words"
        )
        assert "great" in explanation.top_positive_words


class TestAnalyticsModels:
    """Test analytics-related models"""

    def test_time_range_valid(self):
        """Valid time range should pass"""
        time_range = TimeRange.LAST_7_DAYS
        assert time_range == TimeRange.LAST_7_DAYS

    def test_sentiment_distribution_valid(self):
        """Valid distribution should pass"""
        dist = SentimentDistribution(
            positive=100,
            neutral=50,
            negative=50
        )
        assert dist.positive == 100
        assert dist.total == 200

    def test_sentiment_distribution_percentages(self):
        """Distribution should calculate percentages correctly"""
        dist = SentimentDistribution(
            positive=100,
            neutral=50,
            negative=50
        )
        assert dist.positive_pct == 50.0
        assert dist.neutral_pct == 25.0
        assert dist.negative_pct == 25.0

    def test_trend_point_valid(self):
        """Valid trend point should pass"""
        point = TrendPoint(
            timestamp=datetime.now(),
            avg_sentiment=0.25,
            count=100,
            distribution=SentimentDistribution(positive=60, neutral=30, negative=10)
        )
        assert point.avg_sentiment == 0.25
        assert point.count == 100


class TestTrainingModels:
    """Test training-related models"""

    def test_train_model_request_valid(self):
        """Valid train request should pass"""
        request = TrainModelRequest(
            training_data_ids=[1, 2, 3, 4, 5],
            model_name="custom_model"
        )
        assert len(request.training_data_ids) == 5

    def test_train_model_request_min_samples(self):
        """Less than 10 samples should fail"""
        with pytest.raises(ValidationError):
            TrainModelRequest(training_data_ids=[1, 2, 3])

    def test_model_info_valid(self):
        """Valid model info should pass"""
        model = ModelInfo(
            id=1,
            name="test_model",
            version="1.0.0",
            algorithm="MultinomialNB",
            f1_score=0.78,
            training_samples=1000,
            vocabulary_size=500,
            created_at=datetime.now(),
            is_active=True
        )
        assert model.f1_score == 0.78
        assert model.is_active is True

    def test_training_data_item_valid(self):
        """Valid training data item should pass"""
        item = TrainingDataItem(
            text="This is great!",
            label=SentimentLabel.POSITIVE
        )
        assert item.label == SentimentLabel.POSITIVE

    def test_add_training_data_request_valid(self):
        """Valid add training data request should pass"""
        request = AddTrainingDataRequest(
            items=[
                TrainingDataItem(text="Great!", label=SentimentLabel.POSITIVE),
                TrainingDataItem(text="Bad.", label=SentimentLabel.NEGATIVE),
            ],
            source="user_upload"
        )
        assert len(request.items) == 2

    def test_add_training_data_request_max_items(self):
        """More than 10000 items should fail"""
        items = [
            TrainingDataItem(text=f"Text {i}", label=SentimentLabel.POSITIVE)
            for i in range(10001)
        ]
        with pytest.raises(ValidationError):
            AddTrainingDataRequest(items=items)
