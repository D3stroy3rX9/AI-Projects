"""
Quick check of training data count in database
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import SessionLocal, TrainingData, Model
from db.models import SentimentLabelEnum

def main():
    db = SessionLocal()
    try:
        # Count total training data
        total = db.query(TrainingData).count()

        # Count by label
        positive = db.query(TrainingData).filter(TrainingData.label == SentimentLabelEnum.POSITIVE).count()
        negative = db.query(TrainingData).filter(TrainingData.label == SentimentLabelEnum.NEGATIVE).count()
        neutral = db.query(TrainingData).filter(TrainingData.label == SentimentLabelEnum.NEUTRAL).count()

        # Check used in training
        used = db.query(TrainingData).filter(TrainingData.used_in_training == True).count()
        unused = db.query(TrainingData).filter(TrainingData.used_in_training == False).count()

        # Check active model
        active_model = db.query(Model).filter(Model.is_active == True).first()

        print("=" * 70)
        print("TRAINING DATA COUNT CHECK")
        print("=" * 70)
        print(f"\n📊 Total samples in database: {total:,}")
        print(f"\nBreakdown by sentiment:")
        print(f"  ✓ Positive: {positive:,} ({positive/total*100:.1f}%)" if total > 0 else "  ✓ Positive: 0")
        print(f"  ✓ Negative: {negative:,} ({negative/total*100:.1f}%)" if total > 0 else "  ✓ Negative: 0")
        print(f"  ✓ Neutral:  {neutral:,} ({neutral/total*100:.1f}%)" if total > 0 else "  ✓ Neutral: 0")

        print(f"\nTraining status:")
        print(f"  ✓ Used in training: {used:,}")
        print(f"  ✓ Not yet used:     {unused:,}")

        if active_model:
            print(f"\n🤖 Active model info:")
            print(f"  ✓ Name: {active_model.name}")
            print(f"  ✓ Version: {active_model.version}")
            print(f"  ✓ Trained on: {active_model.training_samples:,} samples")
            print(f"  ✓ F1 Score: {active_model.f1_score:.4f}")
            print(f"  ✓ Created: {active_model.created_at}")
        else:
            print(f"\n⚠️  No active model found in database")

        print("\n" + "=" * 70)

        if total < 10000:
            print(f"⚠️  You need {10000 - total:,} more samples to reach 10K")
            print("   Run: generate_10k.bat")
        elif unused > 0:
            print(f"⚠️  You have {unused:,} new samples not yet used in training")
            print("   Run: run_train.bat")
        else:
            print("✅ All good! Dataset is ready and model is trained")

    finally:
        db.close()

if __name__ == "__main__":
    main()
