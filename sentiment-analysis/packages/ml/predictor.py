"""
Model inference module
Handles prediction with trained sentiment models
"""

import numpy as np
import joblib
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

from .preprocessor import TextPreprocessor, create_default_preprocessor


class SentimentPredictor:
    """Make predictions with trained sentiment models"""

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize predictor

        Args:
            model_path: Path to trained model file (optional, can load later)
        """
        self.model: Optional[MultinomialNB] = None
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.metadata: Dict[str, Any] = {}
        self.preprocessor = create_default_preprocessor()

        if model_path:
            self.load_model(model_path)

    def load_model(self, path: str) -> None:
        """
        Load trained model from disk

        Args:
            path: Path to model file
        """
        if not Path(path).exists():
            raise FileNotFoundError(f"Model file not found: {path}")

        model_data = joblib.load(path)

        self.model = model_data['model']
        self.vectorizer = model_data['vectorizer']
        self.metadata = model_data.get('metadata', {})

    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None and self.vectorizer is not None

    def predict(
        self,
        text: str,
        include_probabilities: bool = True
    ) -> Dict[str, Any]:
        """
        Predict sentiment for single text

        Args:
            text: Input text to analyze
            include_probabilities: Include probability scores

        Returns:
            Dictionary with prediction results
        """
        if not self.is_loaded():
            raise RuntimeError("Model not loaded. Call load_model() first.")

        # Preprocess text
        preprocessed = self.preprocessor.preprocess(text)

        # Vectorize
        text_vector = self.vectorizer.transform([preprocessed])

        # Predict
        predicted_label = self.model.predict(text_vector)[0]
        predicted_proba = self.model.predict_proba(text_vector)[0]

        # Get class names
        class_names = self.model.classes_

        # Build sentiment scores dict
        sentiment_scores = {
            class_names[i]: float(predicted_proba[i])
            for i in range(len(class_names))
        }

        # Ensure all sentiment types are present
        for sentiment in ['positive', 'neutral', 'negative']:
            if sentiment not in sentiment_scores:
                sentiment_scores[sentiment] = 0.0

        # Get confidence (max probability)
        confidence = float(np.max(predicted_proba))

        result = {
            'predicted_label': predicted_label,
            'confidence': confidence,
            'sentiment_scores': sentiment_scores
        }

        return result

    def predict_batch(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Predict sentiment for batch of texts

        Args:
            texts: List of texts to analyze
            batch_size: Process texts in batches (for memory efficiency)

        Returns:
            List of prediction results
        """
        if not self.is_loaded():
            raise RuntimeError("Model not loaded. Call load_model() first.")

        results = []

        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]

            # Preprocess batch
            preprocessed = self.preprocessor.preprocess_batch(batch_texts)

            # Vectorize
            text_vectors = self.vectorizer.transform(preprocessed)

            # Predict
            predicted_labels = self.model.predict(text_vectors)
            predicted_probas = self.model.predict_proba(text_vectors)

            # Get class names
            class_names = self.model.classes_

            # Build results
            for j, text in enumerate(batch_texts):
                sentiment_scores = {
                    class_names[k]: float(predicted_probas[j][k])
                    for k in range(len(class_names))
                }

                # Ensure all sentiment types are present
                for sentiment in ['positive', 'neutral', 'negative']:
                    if sentiment not in sentiment_scores:
                        sentiment_scores[sentiment] = 0.0

                confidence = float(np.max(predicted_probas[j]))

                result = {
                    'predicted_label': predicted_labels[j],
                    'confidence': confidence,
                    'sentiment_scores': sentiment_scores
                }

                results.append(result)

        return results

    def explain(
        self,
        text: str,
        top_n: int = 10
    ) -> Dict[str, Any]:
        """
        Explain prediction with top contributing features (words)

        Args:
            text: Input text
            top_n: Number of top features to return

        Returns:
            Dictionary with explanation (top words per class)
        """
        if not self.is_loaded():
            raise RuntimeError("Model not loaded. Call load_model() first.")

        # Preprocess and vectorize
        preprocessed = self.preprocessor.preprocess(text)
        text_vector = self.vectorizer.transform([preprocessed])

        # Get feature names
        feature_names = self.vectorizer.get_feature_names_out()

        # Get which features are present in this text
        feature_indices = text_vector.nonzero()[1]

        if len(feature_indices) == 0:
            return {
                'top_positive_words': [],
                'top_negative_words': [],
                'reasoning': "No recognizable features found in text"
            }

        # Get log probabilities for each class
        class_names = self.model.classes_
        feature_log_probs = self.model.feature_log_prob_

        # Calculate contribution of each present feature to each class
        contributions = {}

        for class_idx, class_name in enumerate(class_names):
            class_contributions = []

            for feature_idx in feature_indices:
                feature_name = feature_names[feature_idx]
                # TF-IDF weight in document
                tfidf_weight = text_vector[0, feature_idx]
                # Log probability of feature for this class
                log_prob = feature_log_probs[class_idx, feature_idx]
                # Contribution = tfidf * log_prob
                contribution = tfidf_weight * log_prob

                class_contributions.append((feature_name, float(contribution)))

            # Sort by contribution
            class_contributions.sort(key=lambda x: x[1], reverse=True)
            contributions[class_name] = class_contributions[:top_n]

        # Get top words for positive and negative
        top_positive = contributions.get('positive', [])[:top_n]
        top_negative = contributions.get('negative', [])[:top_n]

        # Simple reasoning
        predicted = self.predict(text)
        reasoning = f"Text classified as {predicted['predicted_label']} with {predicted['confidence']:.2%} confidence"

        return {
            'top_positive_words': [word for word, _ in top_positive],
            'top_negative_words': [word for word, _ in top_negative],
            'reasoning': reasoning,
            'detailed_contributions': contributions
        }

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about loaded model

        Returns:
            Dictionary with model metadata
        """
        if not self.is_loaded():
            raise RuntimeError("Model not loaded")

        return {
            'classes': self.model.classes_.tolist(),
            'n_features': len(self.vectorizer.vocabulary_),
            'metadata': self.metadata
        }
