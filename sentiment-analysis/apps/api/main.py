"""
Sentiment Analysis API
FastAPI application for real-time sentiment analysis with classical ML
"""

import sys
from pathlib import Path

# Add packages directory to Python path for ML imports
packages_path = Path(__file__).parent.parent.parent / "packages"
if str(packages_path) not in sys.path:
    sys.path.insert(0, str(packages_path))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import hashlib

from config import settings
from models.sentiment import AnalyzeRequest, SentimentResult, SentimentScores, SentimentLabel
from db.database import SessionLocal
from db.models import Analysis, SentimentLabelEnum, SourceEnum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global ML predictor
predictor = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    global predictor

    # Startup
    logger.info("Starting Sentiment Analysis API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Load ML model
    try:
        from ml.predictor import SentimentPredictor
        model_path = Path(settings.MODEL_PATH)
        if model_path.exists():
            predictor = SentimentPredictor(model_path=str(model_path))
            logger.info(f"ML model loaded from {model_path}")
        else:
            logger.warning(f"ML model not found at {model_path}. Train a model first.")
    except Exception as e:
        logger.error(f"Failed to load ML model: {e}")

    yield

    # Shutdown
    logger.info("Shutting down Sentiment Analysis API...")


# Create FastAPI app
app = FastAPI(
    title="Sentiment Analysis API",
    description="Production-grade sentiment analysis with classical ML",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Sentiment Analysis API",
        "docs": "/docs",
        "health": "/health"
    }


@app.post("/analyze", response_model=SentimentResult)
async def analyze_sentiment(request: AnalyzeRequest):
    """Analyze sentiment of text"""
    if predictor is None:
        raise HTTPException(
            status_code=503,
            detail="ML model not loaded. Please train a model first by running: python scripts/train_initial_model.py"
        )

    try:
        # Get prediction from ML model
        prediction = predictor.predict(request.text)

        # Create hash for deduplication
        text_hash = hashlib.sha256(request.text.encode()).hexdigest()

        # Save to database
        db = SessionLocal()
        try:
            # Check if already analyzed
            existing = db.query(Analysis).filter(Analysis.text_hash == text_hash).first()

            if not existing:
                # Create new analysis record
                analysis = Analysis(
                    text_hash=text_hash,
                    text=request.text,
                    sentiment_scores=prediction['sentiment_scores'],
                    predicted_label=SentimentLabelEnum(prediction['predicted_label']),
                    confidence=prediction['confidence'],
                    source=SourceEnum.API
                )
                db.add(analysis)
                db.commit()
                logger.info(f"Analyzed text (hash: {text_hash[:8]}...): {prediction['predicted_label']}")
        finally:
            db.close()

        # Return result
        return SentimentResult(
            text=request.text,
            sentiment=SentimentScores(**prediction['sentiment_scores']),
            confidence=prediction['confidence'],
            predicted_label=SentimentLabel(prediction['predicted_label'])
        )

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD
    )
