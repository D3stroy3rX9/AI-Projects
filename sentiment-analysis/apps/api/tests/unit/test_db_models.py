"""
Unit tests for SQLAlchemy database models
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

from db.models import Analysis, Model, TrainingData, AnalyticsSummary, SentimentLabelEnum, SourceEnum


@pytest.mark.unit
class TestAnalysisModel:
    """Test Analysis model"""

    def test_create_analysis(self, db_session):
        """Should create analysis record"""
        analysis = Analysis(
            text_hash="test_hash_123",
            text="This is a test",
            sentiment_scores={"positive": 0.7, "neutral": 0.2, "negative": 0.1},
            emotion_scores={"joy": 0.8, "anger": 0.1, "sadness": 0.05, "surprise": 0.02, "fear": 0.02, "love": 0.01},
            predicted_label=SentimentLabelEnum.POSITIVE,
            confidence=0.7,
            source=SourceEnum.API,
            metadata={"test": True}
        )
        db_session.add(analysis)
        db_session.commit()

        assert analysis.id is not None
        assert analysis.text == "This is a test"
        assert analysis.predicted_label == SentimentLabelEnum.POSITIVE

    def test_analysis_unique_text_hash(self, db_session):
        """Text hash should be unique"""
        analysis1 = Analysis(
            text_hash="duplicate_hash",
            text="First",
            sentiment_scores={"positive": 0.7, "neutral": 0.2, "negative": 0.1},
            predicted_label=SentimentLabelEnum.POSITIVE,
            confidence=0.7,
            source=SourceEnum.API
        )
        db_session.add(analysis1)
        db_session.commit()

        # Try to create duplicate
        analysis2 = Analysis(
            text_hash="duplicate_hash",
            text="Second",
            sentiment_scores={"positive": 0.7, "neutral": 0.2, "negative": 0.1},
            predicted_label=SentimentLabelEnum.POSITIVE,
            confidence=0.7,
            source=SourceEnum.API
        )
        db_session.add(analysis2)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_analysis_default_analyzed_at(self, db_session):
        """analyzed_at should default to now()"""
        analysis = Analysis(
            text_hash="hash1",
            text="Test",
            sentiment_scores={"positive": 0.7, "neutral": 0.2, "negative": 0.1},
            predicted_label=SentimentLabelEnum.POSITIVE,
            confidence=0.7,
            source=SourceEnum.API
        )
        db_session.add(analysis)
        db_session.commit()

        assert analysis.analyzed_at is not None
        assert isinstance(analysis.analyzed_at, datetime)


@pytest.mark.unit
class TestModelModel:
    """Test Model model"""

    def test_create_model(self, db_session):
        """Should create model record"""
        model = Model(
            name="test_model",
            version="1.0.0",
            algorithm="MultinomialNB",
            f1_score=0.78,
            training_samples=1000,
            vocabulary_size=500,
            is_active=True,
            model_path="models/test.joblib",
            metrics={"precision": 0.80, "recall": 0.76}
        )
        db_session.add(model)
        db_session.commit()

        assert model.id is not None
        assert model.name == "test_model"
        assert model.f1_score == 0.78

    def test_model_default_created_at(self, db_session):
        """created_at should default to now()"""
        model = Model(
            name="test_model",
            version="1.0.0",
            algorithm="MultinomialNB",
            f1_score=0.78,
            training_samples=1000,
            vocabulary_size=500,
            is_active=False
        )
        db_session.add(model)
        db_session.commit()

        assert model.created_at is not None
        assert isinstance(model.created_at, datetime)

    def test_multiple_active_models(self, db_session):
        """Should allow multiple models but track active one"""
        model1 = Model(
            name="model_v1",
            version="1.0.0",
            algorithm="MultinomialNB",
            f1_score=0.75,
            training_samples=1000,
            vocabulary_size=500,
            is_active=False
        )
        model2 = Model(
            name="model_v2",
            version="2.0.0",
            algorithm="MultinomialNB",
            f1_score=0.80,
            training_samples=2000,
            vocabulary_size=800,
            is_active=True
        )
        db_session.add_all([model1, model2])
        db_session.commit()

        # Query active model
        active = db_session.query(Model).filter(Model.is_active == True).first()
        assert active.name == "model_v2"


@pytest.mark.unit
class TestTrainingDataModel:
    """Test TrainingData model"""

    def test_create_training_data(self, db_session):
        """Should create training data record"""
        data = TrainingData(
            text="This is great!",
            label=SentimentLabelEnum.POSITIVE,
            source="user_upload",
            used_in_training=False
        )
        db_session.add(data)
        db_session.commit()

        assert data.id is not None
        assert data.text == "This is great!"
        assert data.label == SentimentLabelEnum.POSITIVE

    def test_training_data_default_values(self, db_session):
        """Should have correct defaults"""
        data = TrainingData(
            text="Test",
            label=SentimentLabelEnum.NEUTRAL
        )
        db_session.add(data)
        db_session.commit()

        assert data.created_at is not None
        assert data.used_in_training is False

    def test_query_by_label(self, db_session):
        """Should query by label"""
        positive = TrainingData(text="Great!", label=SentimentLabelEnum.POSITIVE)
        negative = TrainingData(text="Bad.", label=SentimentLabelEnum.NEGATIVE)
        db_session.add_all([positive, negative])
        db_session.commit()

        results = db_session.query(TrainingData).filter(
            TrainingData.label == SentimentLabelEnum.POSITIVE
        ).all()

        assert len(results) == 1
        assert results[0].text == "Great!"


@pytest.mark.unit
class TestAnalyticsSummaryModel:
    """Test AnalyticsSummary model"""

    def test_create_summary(self, db_session):
        """Should create analytics summary"""
        summary = AnalyticsSummary(
            date=datetime.now(),
            hour=12,
            sentiment_avg=0.25,
            positive_count=100,
            neutral_count=50,
            negative_count=50,
            total_count=200
        )
        db_session.add(summary)
        db_session.commit()

        assert summary.id is not None
        assert summary.total_count == 200
        assert summary.sentiment_avg == 0.25

    def test_daily_vs_hourly_summary(self, db_session):
        """Should support both daily and hourly summaries"""
        now = datetime.now()

        # Daily summary (hour=None)
        daily = AnalyticsSummary(
            date=now.replace(hour=0, minute=0, second=0, microsecond=0),
            hour=None,
            sentiment_avg=0.15,
            positive_count=500,
            neutral_count=300,
            negative_count=200,
            total_count=1000
        )

        # Hourly summary
        hourly = AnalyticsSummary(
            date=now.replace(minute=0, second=0, microsecond=0),
            hour=now.hour,
            sentiment_avg=0.20,
            positive_count=50,
            neutral_count=30,
            negative_count=20,
            total_count=100
        )

        db_session.add_all([daily, hourly])
        db_session.commit()

        # Query daily summaries
        daily_summaries = db_session.query(AnalyticsSummary).filter(
            AnalyticsSummary.hour == None
        ).all()
        assert len(daily_summaries) == 1

    def test_query_by_date_range(self, db_session):
        """Should query summaries by date range"""
        now = datetime.now()

        summaries = [
            AnalyticsSummary(
                date=now - timedelta(days=i),
                sentiment_avg=0.1 * i,
                positive_count=100,
                neutral_count=50,
                negative_count=50,
                total_count=200
            )
            for i in range(7)
        ]
        db_session.bulk_save_objects(summaries)
        db_session.commit()

        # Query last 3 days
        three_days_ago = now - timedelta(days=3)
        recent = db_session.query(AnalyticsSummary).filter(
            AnalyticsSummary.date >= three_days_ago
        ).all()

        assert len(recent) >= 3
