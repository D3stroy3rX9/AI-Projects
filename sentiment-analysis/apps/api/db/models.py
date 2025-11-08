"""
SQLAlchemy database models
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Text,
    Enum,
    Index,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from datetime import datetime
import enum

from .database import Base


class SentimentLabelEnum(str, enum.Enum):
    """Sentiment label enumeration"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class SourceEnum(str, enum.Enum):
    """Data source enumeration"""
    API = "api"
    BATCH = "batch"
    WEBHOOK = "webhook"


class Analysis(Base):
    """
    Analysis table - stores sentiment analysis results
    TimescaleDB hypertable for time-series data
    """
    __tablename__ = "analysis"

    id = Column(Integer, primary_key=True, index=True)
    text_hash = Column(String(64), unique=True, nullable=False, index=True)
    text = Column(Text, nullable=False)
    sentiment_scores = Column(JSONB, nullable=False)  # {positive, neutral, negative}
    emotion_scores = Column(JSONB)  # {joy, anger, sadness, surprise, fear, love}
    predicted_label = Column(
        Enum(SentimentLabelEnum),
        nullable=False,
        index=True
    )
    confidence = Column(Float, nullable=False)
    analyzed_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    source = Column(
        Enum(SourceEnum),
        nullable=False,
        default=SourceEnum.API,
        index=True
    )
    metadata = Column(JSONB)  # Additional metadata

    __table_args__ = (
        Index('ix_analysis_label_time', 'predicted_label', 'analyzed_at'),
        CheckConstraint('confidence >= 0 AND confidence <= 1', name='confidence_range'),
    )

    def __repr__(self):
        return f"<Analysis(id={self.id}, label={self.predicted_label}, confidence={self.confidence:.2f})>"


class Model(Base):
    """
    Model table - stores trained ML models metadata
    """
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    version = Column(String(50), nullable=False)
    algorithm = Column(String(100), nullable=False, default="MultinomialNB")
    f1_score = Column(Float, nullable=False)
    training_samples = Column(Integer, nullable=False)
    vocabulary_size = Column(Integer, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    is_active = Column(Boolean, default=False, nullable=False, index=True)
    model_path = Column(String(500))  # Path to saved model file
    metrics = Column(JSONB)  # Additional metrics (precision, recall, etc.)

    __table_args__ = (
        Index('ix_models_active_created', 'is_active', 'created_at'),
        CheckConstraint('f1_score >= 0 AND f1_score <= 1', name='f1_range'),
    )

    def __repr__(self):
        return f"<Model(id={self.id}, name={self.name}, f1={self.f1_score:.3f}, active={self.is_active})>"


class TrainingData(Base):
    """
    TrainingData table - stores labeled data for model training
    """
    __tablename__ = "training_data"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    label = Column(
        Enum(SentimentLabelEnum),
        nullable=False,
        index=True
    )
    source = Column(String(100))  # e.g., "stanford_sentiment", "user_upload"
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    used_in_training = Column(Boolean, default=False, nullable=False, index=True)

    def __repr__(self):
        return f"<TrainingData(id={self.id}, label={self.label}, used={self.used_in_training})>"


class AnalyticsSummary(Base):
    """
    AnalyticsSummary table - aggregated analytics data
    Can be materialized view or computed table
    """
    __tablename__ = "analytics_summary"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    hour = Column(Integer)  # 0-23, optional for hourly aggregation
    sentiment_avg = Column(Float, nullable=False)  # -1 to 1 scale
    positive_count = Column(Integer, default=0, nullable=False)
    neutral_count = Column(Integer, default=0, nullable=False)
    negative_count = Column(Integer, default=0, nullable=False)
    total_count = Column(Integer, nullable=False)

    __table_args__ = (
        Index('ix_summary_date_hour', 'date', 'hour'),
        CheckConstraint('total_count = positive_count + neutral_count + negative_count', name='count_sum'),
    )

    def __repr__(self):
        return f"<AnalyticsSummary(date={self.date}, total={self.total_count}, avg={self.sentiment_avg:.2f})>"
