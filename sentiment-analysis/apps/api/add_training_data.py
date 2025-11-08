"""
Add additional training data to improve model accuracy
Run this script, then retrain the model with run_train.bat
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import SessionLocal, TrainingData
from db.models import SentimentLabelEnum

def main():
    print("Adding more training data to improve model accuracy...")

    # Extended training data with more diverse examples
    additional_data = [
        # More negative examples
        ("This is absolutely terrible and disappointing", "negative"),
        ("I'm very upset and frustrated with this situation", "negative"),
        ("Horrible experience, would not recommend at all", "negative"),
        ("This made me feel sad and depressed", "negative"),
        ("Tragic events have unfolded before our eyes", "negative"),
        ("Disaster struck and everything went wrong", "negative"),
        ("Awful, just awful. Complete waste of time", "negative"),
        ("I hate this so much, it's unbearable", "negative"),
        ("Disgusting and unacceptable behavior", "negative"),
        ("Terrible service, very disappointed", "negative"),
        ("This broke my heart completely", "negative"),
        ("Worst experience I've ever had", "negative"),
        ("Absolutely miserable and depressing", "negative"),
        ("Failed miserably, total disaster", "negative"),
        ("Deeply saddened by these events", "negative"),
        ("Catastrophic failure on all fronts", "negative"),
        ("Heartbreaking news that shocked everyone", "negative"),
        ("Dreadful experience from start to finish", "negative"),
        ("Devastating loss and tragedy", "negative"),
        ("Appalling and completely unacceptable", "negative"),

        # More positive examples
        ("This is absolutely wonderful and amazing", "positive"),
        ("I'm so happy and excited about this", "positive"),
        ("Fantastic experience, highly recommend it", "positive"),
        ("This made me feel joyful and grateful", "positive"),
        ("Incredible success beyond our expectations", "positive"),
        ("Brilliant work, exceeded all my hopes", "positive"),
        ("I love this so much, it's perfect", "positive"),
        ("Outstanding and exceptional quality", "positive"),
        ("Excellent service, very impressed", "positive"),
        ("This warmed my heart completely", "positive"),
        ("Best experience I've ever had", "positive"),
        ("Absolutely delightful and charming", "positive"),
        ("Succeeded wonderfully, total triumph", "positive"),
        ("Deeply moved by these positive events", "positive"),
        ("Remarkable achievement on all fronts", "positive"),
        ("Uplifting news that inspired everyone", "positive"),
        ("Wonderful experience from start to finish", "positive"),
        ("Amazing victory and celebration", "positive"),
        ("Impressive and completely satisfactory", "positive"),
        ("Thrilled with the fantastic results", "positive"),

        # More neutral examples
        ("The meeting is scheduled for tomorrow", "neutral"),
        ("I received the package on Monday", "neutral"),
        ("The report contains five sections", "neutral"),
        ("It happened last week", "neutral"),
        ("The event took place as planned", "neutral"),
        ("This is the third attempt", "neutral"),
        ("The document was updated yesterday", "neutral"),
        ("They arrived at noon", "neutral"),
        ("The process takes about two hours", "neutral"),
        ("It costs fifty dollars", "neutral"),
        ("The building has ten floors", "neutral"),
        ("We need to submit by Friday", "neutral"),
        ("The temperature is 72 degrees", "neutral"),
        ("It weighs approximately five pounds", "neutral"),
        ("The distance is twenty miles", "neutral"),
        ("They operate from 9 to 5", "neutral"),
        ("The color is blue", "neutral"),
        ("It's located on the second floor", "neutral"),
        ("The file size is 2 megabytes", "neutral"),
        ("There are twelve participants", "neutral"),

        # More nuanced negative examples
        ("I'm disappointed by the lack of progress", "negative"),
        ("This doesn't meet my expectations at all", "negative"),
        ("Frustrating delays and poor communication", "negative"),
        ("Unpleasant situation that could have been avoided", "negative"),
        ("Regrettable decision with bad consequences", "negative"),

        # More nuanced positive examples
        ("Pleasant surprise that exceeded expectations", "positive"),
        ("Satisfying results from hard work", "positive"),
        ("Enjoyable time spent with good people", "positive"),
        ("Grateful for the wonderful opportunity", "positive"),
        ("Delighted with the positive outcome", "positive"),

        # More nuanced neutral examples
        ("The situation is neither good nor bad", "neutral"),
        ("It's acceptable but nothing special", "neutral"),
        ("Average performance, as expected", "neutral"),
        ("Standard procedure was followed", "neutral"),
        ("Typical results for this type of work", "neutral"),
    ]

    db = SessionLocal()
    try:
        added = 0
        skipped = 0

        for text, label in additional_data:
            # Check if already exists
            existing = db.query(TrainingData).filter(TrainingData.text == text).first()
            if existing:
                skipped += 1
                continue

            # Add new training sample
            training_item = TrainingData(
                text=text,
                label=SentimentLabelEnum(label),
                source="manual_enhancement",
                used_in_training=False
            )
            db.add(training_item)
            added += 1

        db.commit()

        print(f"\n✅ Successfully added {added} new training samples")
        print(f"   (Skipped {skipped} duplicates)")

        total = db.query(TrainingData).count()
        print(f"\nTotal training samples in database: {total}")

        print("\n" + "="*60)
        print("Next step: Retrain the model to use this new data")
        print("="*60)
        print("\nRun: run_train.bat")
        print("\nThis will retrain the model with all training data,")
        print("including the new samples you just added.")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
