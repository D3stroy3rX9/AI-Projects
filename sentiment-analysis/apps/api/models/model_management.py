"""
Model management models
"""

from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime
from enum import Enum
from .sentiment import TopWord


class TrainingStatus(str, Enum):
    """Training job status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TrainingJobResponse(BaseModel):
    """Response when training job is submitted"""
    job_id: str = Field(..., description="Training job ID")
    status: TrainingStatus
    message: str


class ModelInfo(BaseModel):
    """Information about a trained model"""
    id: int
    name: str
    version: str
    algorithm: str = Field(..., description="ML algorithm used")
    f1_score: float = Field(..., description="Model F1 score")
    training_samples: int = Field(..., description="Number of samples used for training")
    vocabulary_size: int = Field(..., description="Size of vocabulary")
    created_at: datetime
    is_active: bool = Field(..., description="Whether this model is currently active")


class F1Scores(BaseModel):
    """F1 scores per class"""
    positive: float
    neutral: float
    negative: float
    overall: float


class FeatureImportance(BaseModel):
    """Feature importance by class"""
    positive: List[TopWord]
    negative: List[TopWord]


class ModelEvaluation(BaseModel):
    """Model evaluation metrics"""
    model_id: int
    confusion_matrix: List[List[int]] = Field(
        ...,
        description="Confusion matrix (3x3 for pos/neu/neg)"
    )
    f1_scores: F1Scores
    feature_importance: FeatureImportance
