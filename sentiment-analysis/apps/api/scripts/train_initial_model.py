#!/usr/bin/env python3
"""
Train initial sentiment analysis model using seed training data

This script trains a model on the training data from the database
and saves it for use in the API.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import SessionLocal, Model, TrainingData
from db.models import SentimentLabelEnum
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "packages"))

from ml import ModelTrainer


def main():
    """Train and save initial model"""
    print("=" * 60)
    print("Training Initial Sentiment Analysis Model")
    print("=" * 60)

    # Connect to database
    db = SessionLocal()

    try:
        # Load training data from database
        print("\n1. Loading training data from database...")
        training_data = db.query(TrainingData).all()

        if len(training_data) == 0:
            print("❌ No training data found in database!")
            print("   Run 'poetry run python seed.py' first to populate training data.")
            return 1

        print(f"✓ Loaded {len(training_data)} training samples")

        # Extract texts and labels
        texts = [item.text for item in training_data]
        labels = [item.label.value for item in training_data]  # Convert enum to string

        # Count by label
        label_counts = {}
        for label in labels:
            label_counts[label] = label_counts.get(label, 0) + 1

        print(f"\nLabel distribution:")
        for label, count in sorted(label_counts.items()):
            print(f"  {label}: {count} ({count/len(labels)*100:.1f}%)")

        # Initialize trainer
        print("\n2. Initializing trainer...")
        trainer = ModelTrainer(
            max_features=5000,
            ngram_range=(1, 2),  # Unigrams and bigrams
            min_df=2,
            max_df=0.9
        )
        print("✓ Trainer configured")

        # Train model
        print("\n3. Training model...")
        print("   - Preprocessing texts...")
        print("   - Creating TF-IDF features...")
        print("   - Training Naive Bayes classifier...")
        print("   - Evaluating on test set...")

        model, vectorizer, metrics = trainer.train(
            texts=texts,
            labels=labels,
            test_size=0.2,
            random_state=42
        )

        print(f"\n✓ Model trained successfully!")
        print(f"\nPerformance Metrics:")
        print(f"  Accuracy:  {metrics['accuracy']:.4f}")
        print(f"  Precision: {metrics['precision_macro']:.4f}")
        print(f"  Recall:    {metrics['recall_macro']:.4f}")
        print(f"  F1 Score:  {metrics['f1_macro']:.4f}")

        print(f"\nPer-class F1 scores:")
        for label, f1 in metrics['f1'].items():
            print(f"  {label}: {f1:.4f}")

        print(f"\nModel details:")
        print(f"  Vocabulary size: {metrics['vocabulary_size']}")
        print(f"  Training samples: {metrics['training_samples']}")
        print(f"  Test samples: {metrics['test_samples']}")

        # Save model to disk
        print("\n4. Saving model to disk...")
        model_dir = Path(__file__).parent.parent / "models"
        model_dir.mkdir(exist_ok=True)
        model_path = model_dir / "sentiment_model.joblib"

        metadata = {
            'training_date': str(Path(__file__).stat().st_mtime),
            'training_samples': metrics['training_samples'],
            'metrics': metrics
        }

        trainer.save_model(model, vectorizer, str(model_path), metadata=metadata)
        print(f"✓ Model saved to: {model_path}")

        # Save model metadata to database
        print("\n5. Saving model info to database...")

        # Deactivate all existing models
        db.query(Model).update({Model.is_active: False})

        # Create new model record
        db_model = Model(
            name="initial_model",
            version="1.0.0",
            algorithm="TF-IDF + MultinomialNB",
            f1_score=metrics['f1_macro'],
            training_samples=metrics['training_samples'],
            vocabulary_size=metrics['vocabulary_size'],
            is_active=True,
            model_path=str(model_path),
            metrics=metrics
        )
        db.add(db_model)
        db.commit()
        db.refresh(db_model)

        print(f"✓ Model record created (ID: {db_model.id})")

        # Mark training data as used
        for item in training_data:
            item.used_in_training = True
        db.commit()

        print("\n" + "=" * 60)
        print("✅ Initial model training complete!")
        print("=" * 60)
        print(f"\nModel is ready to use at: {model_path}")
        print(f"Database record ID: {db_model.id}")
        print(f"F1 Score: {metrics['f1_macro']:.4f}")
        print("\nYou can now start the API server to use this model.")

        return 0

    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    exit(main())
