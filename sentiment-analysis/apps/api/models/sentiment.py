"""
Sentiment analysis models
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class SentimentLabel(str, Enum):
    """Sentiment label enum"""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class AnalyzeRequest(BaseModel):
    """Request to analyze single text"""
    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Text to analyze",
        examples=["This product exceeded my expectations!"]
    )


class SentimentScores(BaseModel):
    """Sentiment probability scores"""
    positive: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Positive sentiment score"
    )
    neutral: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Neutral sentiment score"
    )
    negative: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Negative sentiment score"
    )


class EmotionScores(BaseModel):
    """Emotion probability scores"""
    joy: Optional[float] = Field(None, ge=0.0, le=1.0)
    anger: Optional[float] = Field(None, ge=0.0, le=1.0)
    sadness: Optional[float] = Field(None, ge=0.0, le=1.0)
    surprise: Optional[float] = Field(None, ge=0.0, le=1.0)
    fear: Optional[float] = Field(None, ge=0.0, le=1.0)
    love: Optional[float] = Field(None, ge=0.0, le=1.0)


class TopWord(BaseModel):
    """Top influential word with weight"""
    word: str = Field(..., description="Influential word")
    weight: float = Field(..., description="Feature weight (positive or negative)")


class Explanation(BaseModel):
    """Explanation of prediction"""
    top_words: List[TopWord] = Field(
        default_factory=list,
        description="Top influential words"
    )


class SentimentResult(BaseModel):
    """Sentiment analysis result"""
    text: str = Field(..., description="Original text analyzed")
    sentiment: SentimentScores
    emotion: Optional[EmotionScores] = None
    explanation: Optional[Explanation] = None
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Prediction confidence"
    )
    predicted_label: SentimentLabel = Field(
        ...,
        description="Primary sentiment label"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "This is amazing!",
                    "sentiment": {
                        "positive": 0.92,
                        "neutral": 0.06,
                        "negative": 0.02
                    },
                    "emotion": {
                        "joy": 0.85,
                        "anger": 0.01,
                        "sadness": 0.01,
                        "surprise": 0.10,
                        "fear": 0.01,
                        "love": 0.02
                    },
                    "explanation": {
                        "top_words": [
                            {"word": "amazing", "weight": 0.85}
                        ]
                    },
                    "confidence": 0.92,
                    "predicted_label": "positive"
                }
            ]
        }
    }


class BatchAnalyzeRequest(BaseModel):
    """Request to analyze multiple texts"""
    texts: List[str] = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Array of texts to analyze"
    )


class BatchAnalyzeResponse(BaseModel):
    """Response for batch analysis"""
    results: List[SentimentResult]
    total: int = Field(..., description="Total number of texts analyzed")
