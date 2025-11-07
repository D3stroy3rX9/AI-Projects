"""
API Models
Pydantic models for request/response validation
"""

from .sentiment import (
    AnalyzeRequest,
    SentimentScores,
    EmotionScores,
    TopWord,
    Explanation,
    SentimentResult,
    BatchAnalyzeRequest,
    BatchAnalyzeResponse,
)

from .analytics import (
    TrendPoint,
    TrendsResponse,
    AnalyticsSummary,
)

from .model_management import (
    TrainingJobResponse,
    ModelInfo,
    ModelEvaluation,
)

from .common import (
    Error,
    ValidationError,
    WebhookResponse,
)

__all__ = [
    # Sentiment
    "AnalyzeRequest",
    "SentimentScores",
    "EmotionScores",
    "TopWord",
    "Explanation",
    "SentimentResult",
    "BatchAnalyzeRequest",
    "BatchAnalyzeResponse",
    # Analytics
    "TrendPoint",
    "TrendsResponse",
    "AnalyticsSummary",
    # Model Management
    "TrainingJobResponse",
    "ModelInfo",
    "ModelEvaluation",
    # Common
    "Error",
    "ValidationError",
    "WebhookResponse",
]
