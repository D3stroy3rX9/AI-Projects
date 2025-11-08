"""
Seed script - populate database with sample data
"""

import asyncio
import hashlib
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session

from db import SessionLocal, Analysis, Model, TrainingData, AnalyticsSummary
from db.models import SentimentLabelEnum, SourceEnum

# Sample texts for each sentiment
POSITIVE_TEXTS = [
    "This product is absolutely fantastic! Exceeded all my expectations.",
    "I'm so happy with this purchase. Best decision ever!",
    "Amazing quality and great customer service. Highly recommended!",
    "Love it! Works perfectly and arrived quickly.",
    "Excellent experience from start to finish. Will buy again!",
    "Outstanding product! Worth every penny.",
    "Incredible! This has changed my life for the better.",
    "Five stars! Couldn't ask for anything better.",
    "Perfect! Exactly what I was looking for.",
    "Wonderful product and fantastic value for money.",
]

NEUTRAL_TEXTS = [
    "The product arrived on time as expected.",
    "It's okay, nothing special but does the job.",
    "Average quality, meets basic requirements.",
    "Delivered as described. No complaints.",
    "Standard product, no surprises good or bad.",
    "It works as intended. Nothing more, nothing less.",
    "Fair price for what you get.",
    "Acceptable quality for the price point.",
    "Met my expectations, nothing outstanding.",
    "Ordinary product, serves its purpose.",
]

NEGATIVE_TEXTS = [
    "Terrible experience. Would not recommend to anyone.",
    "Very disappointed with the quality. Complete waste of money.",
    "Poor customer service and defective product.",
    "Broke after one use. Total disappointment.",
    "Horrible! Nothing like the description.",
    "Worst purchase I've ever made. Avoid at all costs.",
    "Extremely dissatisfied. Requesting a refund.",
    "Low quality materials and doesn't work properly.",
    "Frustrating experience from beginning to end.",
    "Not worth the price. Very unhappy with this.",
]


def create_text_hash(text: str) -> str:
    """Create SHA-256 hash of text for deduplication"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def generate_sentiment_scores(label: SentimentLabelEnum) -> dict:
    """Generate realistic sentiment scores based on label"""
    if label == SentimentLabelEnum.POSITIVE:
        pos = random.uniform(0.70, 0.95)
        neg = random.uniform(0.01, 0.10)
        neu = 1.0 - pos - neg
    elif label == SentimentLabelEnum.NEGATIVE:
        neg = random.uniform(0.70, 0.95)
        pos = random.uniform(0.01, 0.10)
        neu = 1.0 - pos - neg
    else:  # NEUTRAL
        neu = random.uniform(0.50, 0.80)
        pos = random.uniform(0.10, 0.40)
        neg = 1.0 - pos - neu

    return {
        "positive": round(pos, 4),
        "neutral": round(neu, 4),
        "negative": round(neg, 4)
    }


def generate_emotion_scores() -> dict:
    """Generate random emotion scores"""
    emotions = ["joy", "anger", "sadness", "surprise", "fear", "love"]
    scores = {emotion: round(random.uniform(0.01, 0.30), 4) for emotion in emotions}

    # Make one emotion dominant
    dominant = random.choice(emotions)
    scores[dominant] = round(random.uniform(0.50, 0.90), 4)

    return scores


def seed_training_data(db: Session):
    """Seed training data table"""
    print("Seeding training data...")

    training_samples = []

    # Add positive samples
    for i, text in enumerate(POSITIVE_TEXTS * 10):  # 100 samples
        sample = TrainingData(
            text=f"{text} (variant {i})",
            label=SentimentLabelEnum.POSITIVE,
            source="seed_script",
            used_in_training=False
        )
        training_samples.append(sample)

    # Add neutral samples
    for i, text in enumerate(NEUTRAL_TEXTS * 10):  # 100 samples
        sample = TrainingData(
            text=f"{text} (variant {i})",
            label=SentimentLabelEnum.NEUTRAL,
            source="seed_script",
            used_in_training=False
        )
        training_samples.append(sample)

    # Add negative samples
    for i, text in enumerate(NEGATIVE_TEXTS * 10):  # 100 samples
        sample = TrainingData(
            text=f"{text} (variant {i})",
            label=SentimentLabelEnum.NEGATIVE,
            source="seed_script",
            used_in_training=False
        )
        training_samples.append(sample)

    db.bulk_save_objects(training_samples)
    db.commit()
    print(f"✓ Created {len(training_samples)} training samples")


def seed_analyses(db: Session):
    """Seed analysis table with realistic distribution"""
    print("Seeding analysis data...")

    analyses = []
    now = datetime.now()

    # Distribution: 40% positive, 30% neutral, 30% negative
    distributions = [
        (POSITIVE_TEXTS, SentimentLabelEnum.POSITIVE, 400),
        (NEUTRAL_TEXTS, SentimentLabelEnum.NEUTRAL, 300),
        (NEGATIVE_TEXTS, SentimentLabelEnum.NEGATIVE, 300),
    ]

    analysis_id = 1
    for texts, label, count in distributions:
        for i in range(count):
            # Select random text and add variation
            text = f"{random.choice(texts)} (sample {analysis_id})"
            text_hash = create_text_hash(text)

            # Generate random timestamp within last 30 days
            days_ago = random.randint(0, 29)
            hours_ago = random.randint(0, 23)
            analyzed_at = now - timedelta(days=days_ago, hours=hours_ago)

            sentiment_scores = generate_sentiment_scores(label)
            confidence = max(sentiment_scores.values())

            analysis = Analysis(
                text_hash=text_hash,
                text=text,
                sentiment_scores=sentiment_scores,
                emotion_scores=generate_emotion_scores(),
                predicted_label=label,
                confidence=round(confidence, 4),
                analyzed_at=analyzed_at,
                source=random.choice(list(SourceEnum)),
                metadata={"seed": True, "id": analysis_id}
            )
            analyses.append(analysis)
            analysis_id += 1

    db.bulk_save_objects(analyses)
    db.commit()
    print(f"✓ Created {len(analyses)} analysis records")


def seed_model(db: Session):
    """Create initial model entry"""
    print("Creating initial model entry...")

    model = Model(
        name="seed_model_v1",
        version="1.0.0",
        algorithm="MultinomialNB + TF-IDF",
        f1_score=0.78,
        training_samples=10000,
        vocabulary_size=5000,
        is_active=True,
        model_path="models/seed-model.joblib",
        metrics={
            "precision": {"positive": 0.80, "neutral": 0.75, "negative": 0.79},
            "recall": {"positive": 0.82, "neutral": 0.72, "negative": 0.80},
            "f1": {"positive": 0.81, "neutral": 0.73, "negative": 0.79, "overall": 0.78}
        }
    )

    db.add(model)
    db.commit()
    print(f"✓ Created model: {model.name} (F1: {model.f1_score})")


def seed_analytics_summary(db: Session):
    """Generate analytics summaries from existing analyses"""
    print("Generating analytics summaries...")

    # Get all analyses
    analyses = db.query(Analysis).all()

    # Group by date
    date_groups = {}
    for analysis in analyses:
        date_key = analysis.analyzed_at.replace(hour=0, minute=0, second=0, microsecond=0)
        if date_key not in date_groups:
            date_groups[date_key] = []
        date_groups[date_key].append(analysis)

    # Create summaries
    summaries = []
    for date, group in date_groups.items():
        # Count by label
        positive_count = sum(1 for a in group if a.predicted_label == SentimentLabelEnum.POSITIVE)
        neutral_count = sum(1 for a in group if a.predicted_label == SentimentLabelEnum.NEUTRAL)
        negative_count = sum(1 for a in group if a.predicted_label == SentimentLabelEnum.NEGATIVE)
        total_count = len(group)

        # Calculate average sentiment (-1 to 1 scale)
        sentiment_values = []
        for a in group:
            # Convert to -1 to 1 scale
            value = (a.sentiment_scores['positive'] - a.sentiment_scores['negative'])
            sentiment_values.append(value)

        sentiment_avg = sum(sentiment_values) / len(sentiment_values) if sentiment_values else 0

        summary = AnalyticsSummary(
            date=date,
            hour=None,  # Daily aggregation
            sentiment_avg=round(sentiment_avg, 4),
            positive_count=positive_count,
            neutral_count=neutral_count,
            negative_count=negative_count,
            total_count=total_count
        )
        summaries.append(summary)

    db.bulk_save_objects(summaries)
    db.commit()
    print(f"✓ Created {len(summaries)} analytics summaries")


def main():
    """Main seed function"""
    print("=" * 50)
    print("Starting database seed...")
    print("=" * 50)

    db = SessionLocal()

    try:
        # Check if already seeded
        existing_count = db.query(Analysis).count()
        if existing_count > 0:
            print(f"\n⚠️  Database already has {existing_count} analysis records.")
            response = input("Do you want to re-seed (this will add more data)? (y/N): ")
            if response.lower() != 'y':
                print("Seed cancelled.")
                return

        # Seed data
        seed_training_data(db)
        seed_analyses(db)
        seed_model(db)
        seed_analytics_summary(db)

        # Print summary
        print("\n" + "=" * 50)
        print("Seed Summary:")
        print("=" * 50)
        print(f"Training data: {db.query(TrainingData).count()} records")
        print(f"Analyses: {db.query(Analysis).count()} records")
        print(f"Models: {db.query(Model).count()} records")
        print(f"Analytics summaries: {db.query(AnalyticsSummary).count()} records")

        # Print distribution
        pos_count = db.query(Analysis).filter(Analysis.predicted_label == SentimentLabelEnum.POSITIVE).count()
        neu_count = db.query(Analysis).filter(Analysis.predicted_label == SentimentLabelEnum.NEUTRAL).count()
        neg_count = db.query(Analysis).filter(Analysis.predicted_label == SentimentLabelEnum.NEGATIVE).count()
        total = pos_count + neu_count + neg_count

        print(f"\nSentiment distribution:")
        print(f"  Positive: {pos_count} ({pos_count/total*100:.1f}%)")
        print(f"  Neutral:  {neu_count} ({neu_count/total*100:.1f}%)")
        print(f"  Negative: {neg_count} ({neg_count/total*100:.1f}%)")

        print("\n✅ Database seeding complete!")

    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
