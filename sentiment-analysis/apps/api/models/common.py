"""
Common models
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Any
from .sentiment import SentimentResult


class Error(BaseModel):
    """Error response"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")


class ValidationErrorDetail(BaseModel):
    """Validation error detail"""
    loc: List[str]
    msg: str
    type: str


class ValidationError(BaseModel):
    """Validation error response"""
    detail: List[ValidationErrorDetail]


class WebhookResponse(BaseModel):
    """Response for webhook"""
    received: bool
    sentiment_result: Optional[SentimentResult] = None
