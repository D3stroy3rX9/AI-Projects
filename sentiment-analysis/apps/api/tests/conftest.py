"""
Pytest configuration and fixtures
"""

import pytest
from datetime import datetime, timedelta
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from db import Base, get_db
from db.models import Analysis, Model, TrainingData, AnalyticsSummary, SentimentLabelEnum, SourceEnum
from config import get_settings


# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> TestClient:
    """Create a test client with database dependency override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_model(db_session: Session) -> Model:
    """Create a sample model for testing"""
    model = Model(
        name="test_model_v1",
        version="1.0.0",
        algorithm="MultinomialNB + TF-IDF",
        f1_score=0.78,
        training_samples=1000,
        vocabulary_size=500,
        is_active=True,
        model_path="models/test-model.joblib",
        metrics={
            "precision": {"positive": 0.80, "neutral": 0.75, "negative": 0.79},
            "recall": {"positive": 0.82, "neutral": 0.72, "negative": 0.80},
            "f1": {"positive": 0.81, "neutral": 0.73, "negative": 0.79}
        }
    )
    db_session.add(model)
    db_session.commit()
    db_session.refresh(model)
    return model


@pytest.fixture
def sample_training_data(db_session: Session) -> list[TrainingData]:
    """Create sample training data"""
    samples = [
        TrainingData(
            text="This is amazing!",
            label=SentimentLabelEnum.POSITIVE,
            source="test",
            used_in_training=False
        ),
        TrainingData(
            text="This is terrible.",
            label=SentimentLabelEnum.NEGATIVE,
            source="test",
            used_in_training=False
        ),
        TrainingData(
            text="This is okay.",
            label=SentimentLabelEnum.NEUTRAL,
            source="test",
            used_in_training=False
        ),
    ]
    db_session.bulk_save_objects(samples)
    db_session.commit()

    # Query back to get IDs
    return db_session.query(TrainingData).filter(TrainingData.source == "test").all()


@pytest.fixture
def sample_analyses(db_session: Session) -> list[Analysis]:
    """Create sample analysis records"""
    now = datetime.now()
    analyses = [
        Analysis(
            text_hash="hash1",
            text="Great product!",
            sentiment_scores={"positive": 0.85, "neutral": 0.10, "negative": 0.05},
            emotion_scores={"joy": 0.80, "anger": 0.05, "sadness": 0.05, "surprise": 0.05, "fear": 0.03, "love": 0.02},
            predicted_label=SentimentLabelEnum.POSITIVE,
            confidence=0.85,
            analyzed_at=now - timedelta(hours=2),
            source=SourceEnum.API,
            metadata={"test": True}
        ),
        Analysis(
            text_hash="hash2",
            text="Terrible experience.",
            sentiment_scores={"positive": 0.05, "neutral": 0.10, "negative": 0.85},
            emotion_scores={"joy": 0.02, "anger": 0.80, "sadness": 0.10, "surprise": 0.03, "fear": 0.03, "love": 0.02},
            predicted_label=SentimentLabelEnum.NEGATIVE,
            confidence=0.85,
            analyzed_at=now - timedelta(hours=1),
            source=SourceEnum.API,
            metadata={"test": True}
        ),
        Analysis(
            text_hash="hash3",
            text="It's okay.",
            sentiment_scores={"positive": 0.30, "neutral": 0.60, "negative": 0.10},
            emotion_scores={"joy": 0.20, "anger": 0.10, "sadness": 0.10, "surprise": 0.10, "fear": 0.10, "love": 0.40},
            predicted_label=SentimentLabelEnum.NEUTRAL,
            confidence=0.60,
            analyzed_at=now,
            source=SourceEnum.BATCH,
            metadata={"test": True}
        ),
    ]
    db_session.bulk_save_objects(analyses)
    db_session.commit()

    return db_session.query(Analysis).filter(Analysis.metadata["test"].astext == "true").all()


@pytest.fixture
def sample_analytics_summary(db_session: Session) -> AnalyticsSummary:
    """Create sample analytics summary"""
    now = datetime.now()
    summary = AnalyticsSummary(
        date=now.replace(hour=0, minute=0, second=0, microsecond=0),
        hour=None,
        sentiment_avg=0.25,
        positive_count=100,
        neutral_count=50,
        negative_count=50,
        total_count=200
    )
    db_session.add(summary)
    db_session.commit()
    db_session.refresh(summary)
    return summary
