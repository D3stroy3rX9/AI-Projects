"""
Celery background tasks
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import List, Dict
import joblib
from pathlib import Path

from celery import Task
from celery.exceptions import Reject

from workers.celery_app import celery_app
from db import SessionLocal, Analysis, Model, TrainingData, AnalyticsSummary
from db.models import SentimentLabelEnum, SourceEnum

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session management"""

    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="workers.tasks.train_model_task",
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,  # 10 minutes max
    retry_jitter=True,
)
def train_model_task(self, training_data_ids: List[int], model_name: str = None):
    """
    Train a new sentiment analysis model

    Args:
        training_data_ids: List of TrainingData IDs to use for training
        model_name: Optional name for the model

    Returns:
        Dict with model_id and metrics
    """
    logger.info(f"Starting model training with {len(training_data_ids)} samples")

    try:
        # 1. Check idempotency - has this exact dataset been trained?
        data_hash = hashlib.sha256(
            "".join(str(i) for i in sorted(training_data_ids)).encode()
        ).hexdigest()[:16]

        existing_model = (
            self.db.query(Model)
            .filter(Model.name == f"model_{data_hash}")
            .first()
        )

        if existing_model:
            logger.info(f"Model already exists for this dataset: {existing_model.id}")
            return {
                "model_id": existing_model.id,
                "status": "already_exists",
                "f1_score": existing_model.f1_score,
            }

        # 2. Load training data
        self.update_state(state="PROGRESS", meta={"stage": "loading_data", "progress": 10})

        training_samples = (
            self.db.query(TrainingData)
            .filter(TrainingData.id.in_(training_data_ids))
            .all()
        )

        if not training_samples:
            raise Reject("No training data found for provided IDs")

        texts = [sample.text for sample in training_samples]
        labels = [sample.label.value for sample in training_samples]

        logger.info(f"Loaded {len(texts)} training samples")

        # 3. Train model (placeholder - will be implemented in prompt f)
        self.update_state(state="PROGRESS", meta={"stage": "training", "progress": 30})

        # For now, create a mock model with realistic metrics
        # This will be replaced with actual ML training in prompt (f)
        import time
        time.sleep(2)  # Simulate training

        self.update_state(state="PROGRESS", meta={"stage": "evaluating", "progress": 70})

        # Mock metrics (will be real in prompt f)
        metrics = {
            "f1": {"positive": 0.81, "neutral": 0.73, "negative": 0.79, "overall": 0.78},
            "precision": {"positive": 0.80, "neutral": 0.75, "negative": 0.79},
            "recall": {"positive": 0.82, "neutral": 0.72, "negative": 0.80},
        }

        # 4. Save model to disk
        self.update_state(state="PROGRESS", meta={"stage": "saving", "progress": 85})

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"{timestamp}-model_{data_hash}.joblib"
        model_path = Path("models") / model_filename
        model_path.parent.mkdir(exist_ok=True)

        # Mock model save (will be real model in prompt f)
        model_data = {
            "vectorizer": None,  # Placeholder
            "classifier": None,  # Placeholder
            "metadata": {
                "trained_at": timestamp,
                "training_samples": len(texts),
                "data_hash": data_hash,
            }
        }
        joblib.dump(model_data, model_path)

        # 5. Update database
        self.update_state(state="PROGRESS", meta={"stage": "updating_db", "progress": 95})

        # Deactivate old models
        self.db.query(Model).filter(Model.is_active == True).update({"is_active": False})

        # Create new model entry
        new_model = Model(
            name=model_name or f"model_{data_hash}",
            version=timestamp,
            algorithm="MultinomialNB + TF-IDF",
            f1_score=metrics["f1"]["overall"],
            training_samples=len(texts),
            vocabulary_size=5000,  # Placeholder, will be real in prompt f
            is_active=True,
            model_path=str(model_path),
            metrics=metrics,
        )

        self.db.add(new_model)

        # Mark training data as used
        self.db.query(TrainingData).filter(
            TrainingData.id.in_(training_data_ids)
        ).update({"used_in_training": True})

        self.db.commit()
        self.db.refresh(new_model)

        logger.info(f"Training complete. Model ID: {new_model.id}, F1: {new_model.f1_score:.3f}")

        return {
            "model_id": new_model.id,
            "status": "success",
            "f1_score": new_model.f1_score,
            "model_path": str(model_path),
            "metrics": metrics,
        }

    except Reject:
        raise
    except Exception as e:
        logger.error(f"Error training model: {e}", exc_info=True)
        self.db.rollback()
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="workers.tasks.batch_analyze_task",
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,  # 5 minutes max
    retry_jitter=True,
)
def batch_analyze_task(self, texts: List[str], source: str = "batch"):
    """
    Analyze sentiment for a batch of texts

    Args:
        texts: List of texts to analyze
        source: Source of the data (batch, api, webhook)

    Returns:
        Dict with count of analyzed texts and skipped duplicates
    """
    logger.info(f"Starting batch analysis of {len(texts)} texts")

    try:
        analyzed_count = 0
        skipped_count = 0

        source_enum = SourceEnum(source) if source in [e.value for e in SourceEnum] else SourceEnum.BATCH

        for i, text in enumerate(texts):
            # Update progress every 10%
            if i % max(1, len(texts) // 10) == 0:
                progress = int((i / len(texts)) * 100)
                self.update_state(
                    state="PROGRESS",
                    meta={"stage": "analyzing", "progress": progress, "current": i, "total": len(texts)}
                )

            # Check for duplicates using text hash
            text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()

            existing = self.db.query(Analysis).filter(Analysis.text_hash == text_hash).first()
            if existing:
                logger.debug(f"Skipping duplicate text (hash: {text_hash[:8]}...)")
                skipped_count += 1
                continue

            # Analyze sentiment (placeholder - will be implemented in prompt f)
            # For now, generate mock predictions
            import random
            label = random.choice(list(SentimentLabelEnum))

            if label == SentimentLabelEnum.POSITIVE:
                sentiment_scores = {
                    "positive": round(random.uniform(0.70, 0.95), 4),
                    "neutral": round(random.uniform(0.02, 0.15), 4),
                    "negative": round(random.uniform(0.01, 0.10), 4),
                }
            elif label == SentimentLabelEnum.NEGATIVE:
                sentiment_scores = {
                    "positive": round(random.uniform(0.01, 0.10), 4),
                    "neutral": round(random.uniform(0.02, 0.15), 4),
                    "negative": round(random.uniform(0.70, 0.95), 4),
                }
            else:  # NEUTRAL
                sentiment_scores = {
                    "positive": round(random.uniform(0.10, 0.30), 4),
                    "neutral": round(random.uniform(0.50, 0.80), 4),
                    "negative": round(random.uniform(0.10, 0.30), 4),
                }

            # Normalize to sum to 1.0
            total = sum(sentiment_scores.values())
            sentiment_scores = {k: round(v / total, 4) for k, v in sentiment_scores.items()}

            confidence = max(sentiment_scores.values())

            # Create analysis record
            analysis = Analysis(
                text_hash=text_hash,
                text=text,
                sentiment_scores=sentiment_scores,
                emotion_scores={
                    "joy": round(random.uniform(0.01, 0.30), 4),
                    "anger": round(random.uniform(0.01, 0.30), 4),
                    "sadness": round(random.uniform(0.01, 0.30), 4),
                    "surprise": round(random.uniform(0.01, 0.30), 4),
                    "fear": round(random.uniform(0.01, 0.30), 4),
                    "love": round(random.uniform(0.01, 0.30), 4),
                },
                predicted_label=label,
                confidence=confidence,
                source=source_enum,
                metadata={"batch_task_id": self.request.id},
            )

            self.db.add(analysis)
            analyzed_count += 1

            # Commit in batches of 100 for performance
            if analyzed_count % 100 == 0:
                self.db.commit()
                logger.info(f"Committed {analyzed_count} analyses")

        # Final commit
        self.db.commit()

        logger.info(f"Batch analysis complete: {analyzed_count} analyzed, {skipped_count} skipped")

        return {
            "status": "success",
            "analyzed": analyzed_count,
            "skipped": skipped_count,
            "total": len(texts),
        }

    except Exception as e:
        logger.error(f"Error in batch analysis: {e}", exc_info=True)
        self.db.rollback()
        raise


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="workers.tasks.aggregate_analytics_task",
    max_retries=3,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def aggregate_analytics_task(self):
    """
    Aggregate analytics data hourly
    Scheduled to run every hour via Celery Beat

    Returns:
        Dict with count of summaries created
    """
    logger.info("Starting analytics aggregation")

    try:
        # Get the last hour's data
        now = datetime.now()
        hour_start = now.replace(minute=0, second=0, microsecond=0)
        hour_end = hour_start + timedelta(hours=1)

        # Check if summary already exists for this hour (idempotency)
        existing = (
            self.db.query(AnalyticsSummary)
            .filter(
                AnalyticsSummary.date == hour_start,
                AnalyticsSummary.hour == hour_start.hour
            )
            .first()
        )

        if existing:
            logger.info(f"Summary already exists for {hour_start}")
            return {
                "status": "already_exists",
                "date": hour_start.isoformat(),
                "hour": hour_start.hour,
            }

        # Get analyses for the last hour
        analyses = (
            self.db.query(Analysis)
            .filter(
                Analysis.analyzed_at >= hour_start,
                Analysis.analyzed_at < hour_end
            )
            .all()
        )

        if not analyses:
            logger.info(f"No analyses found for {hour_start}")
            return {
                "status": "no_data",
                "date": hour_start.isoformat(),
                "hour": hour_start.hour,
            }

        # Count by label
        positive_count = sum(
            1 for a in analyses if a.predicted_label == SentimentLabelEnum.POSITIVE
        )
        neutral_count = sum(
            1 for a in analyses if a.predicted_label == SentimentLabelEnum.NEUTRAL
        )
        negative_count = sum(
            1 for a in analyses if a.predicted_label == SentimentLabelEnum.NEGATIVE
        )
        total_count = len(analyses)

        # Calculate average sentiment (-1 to 1 scale)
        sentiment_values = [
            (a.sentiment_scores['positive'] - a.sentiment_scores['negative'])
            for a in analyses
        ]
        sentiment_avg = sum(sentiment_values) / len(sentiment_values)

        # Create summary
        summary = AnalyticsSummary(
            date=hour_start,
            hour=hour_start.hour,
            sentiment_avg=round(sentiment_avg, 4),
            positive_count=positive_count,
            neutral_count=neutral_count,
            negative_count=negative_count,
            total_count=total_count,
        )

        self.db.add(summary)
        self.db.commit()

        logger.info(
            f"Created analytics summary for {hour_start}: "
            f"{total_count} total, avg sentiment: {sentiment_avg:.3f}"
        )

        return {
            "status": "success",
            "date": hour_start.isoformat(),
            "hour": hour_start.hour,
            "total_count": total_count,
            "sentiment_avg": sentiment_avg,
        }

    except Exception as e:
        logger.error(f"Error aggregating analytics: {e}", exc_info=True)
        self.db.rollback()
        raise
