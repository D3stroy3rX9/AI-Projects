"""
Analytics models
"""

from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from enum import Enum


class TimeInterval(str, Enum):
    """Time interval for aggregation"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


class SentimentDistribution(BaseModel):
    """Distribution of sentiment labels"""
    positive: int = Field(..., ge=0)
    neutral: int = Field(..., ge=0)
    negative: int = Field(..., ge=0)


class TrendPoint(BaseModel):
    """Single data point in time series"""
    timestamp: datetime = Field(..., description="Timestamp for this data point")
    avg_sentiment: float = Field(..., description="Average sentiment score (-1 to 1)")
    count: int = Field(..., ge=0, description="Number of analyses in this interval")
    distribution: SentimentDistribution


class TrendsResponse(BaseModel):
    """Response for trends endpoint"""
    trends: List[TrendPoint]
    interval: TimeInterval


class AnalyticsSummary(BaseModel):
    """Aggregate sentiment statistics"""
    total_analyzed: int = Field(..., ge=0, description="Total number of texts analyzed")
    avg_sentiment: float = Field(..., description="Average sentiment score")
    distribution: SentimentDistribution
    top_positive_words: List[str] = Field(
        default_factory=list,
        description="Most common positive words"
    )
    top_negative_words: List[str] = Field(
        default_factory=list,
        description="Most common negative words"
    )
