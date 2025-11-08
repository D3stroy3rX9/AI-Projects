"""
Model training module
Handles training of sentiment analysis models using TF-IDF + Naive Bayes
"""

import joblib
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split

from .preprocessor import TextPreprocessor, create_default_preprocessor
from .evaluator import ModelEvaluator


class ModelTrainer:
    """Train sentiment analysis models using TF-IDF + Multinomial Naive Bayes"""

    def __init__(
        self,
        max_features: int = 5000,
        ngram_range: Tuple[int, int] = (1, 2),
        min_df: int = 2,
        max_df: float = 0.9,
        preprocessor: Optional[TextPreprocessor] = None
    ):
        """
        Initialize trainer

        Args:
            max_features: Maximum number of features for TF-IDF
            ngram_range: Range of n-grams to extract (1-2 = unigrams + bigrams)
            min_df: Minimum document frequency
            max_df: Maximum document frequency (ignore common words)
            preprocessor: Text preprocessor instance
        """
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.min_df = min_df
        self.max_df = max_df
        self.preprocessor = preprocessor or create_default_preprocessor()
        self.evaluator = ModelEvaluator()

    def preprocess_texts(self, texts: List[str]) -> List[str]:
        """
        Preprocess texts for training

        Args:
            texts: Raw text data

        Returns:
            Preprocessed texts
        """
        return self.preprocessor.preprocess_batch(texts)

    def create_vectorizer(self) -> TfidfVectorizer:
        """
        Create TF-IDF vectorizer

        Returns:
            Configured TfidfVectorizer
        """
        return TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range,
            min_df=self.min_df,
            max_df=self.max_df,
            strip_accents='unicode',
            analyzer='word',
            token_pattern=r'\w{1,}',
            stop_words='english',
            sublinear_tf=True  # Use sublinear TF scaling
        )

    def create_classifier(self) -> MultinomialNB:
        """
        Create Naive Bayes classifier

        Returns:
            Configured MultinomialNB
        """
        return MultinomialNB(
            alpha=0.1  # Smoothing parameter (lower = less smoothing)
        )

    def train(
        self,
        texts: List[str],
        labels: List[str],
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Tuple[MultinomialNB, TfidfVectorizer, Dict[str, Any]]:
        """
        Train sentiment analysis model

        Args:
            texts: Training texts
            labels: Sentiment labels ('positive', 'neutral', 'negative')
            test_size: Fraction of data to use for testing
            random_state: Random seed for reproducibility

        Returns:
            Tuple of (trained_model, vectorizer, metrics)
        """
        if len(texts) != len(labels):
            raise ValueError("Number of texts and labels must match")

        if len(texts) < 10:
            raise ValueError("Need at least 10 samples to train")

        # Preprocess texts
        preprocessed_texts = self.preprocess_texts(texts)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            preprocessed_texts,
            labels,
            test_size=test_size,
            random_state=random_state,
            stratify=labels  # Maintain class distribution
        )

        # Create and fit vectorizer
        vectorizer = self.create_vectorizer()
        X_train_tfidf = vectorizer.fit_transform(X_train)
        X_test_tfidf = vectorizer.transform(X_test)

        # Train classifier
        classifier = self.create_classifier()
        classifier.fit(X_train_tfidf, y_train)

        # Evaluate
        y_pred = classifier.predict(X_test_tfidf)
        y_pred_proba = classifier.predict_proba(X_test_tfidf)

        metrics = self.evaluator.evaluate(
            y_true=y_test,
            y_pred=y_pred,
            y_pred_proba=y_pred_proba,
            class_names=classifier.classes_.tolist()
        )

        # Add vocabulary size to metrics
        metrics['vocabulary_size'] = len(vectorizer.vocabulary_)
        metrics['training_samples'] = len(texts)
        metrics['test_samples'] = len(X_test)

        return classifier, vectorizer, metrics

    def save_model(
        self,
        model: MultinomialNB,
        vectorizer: TfidfVectorizer,
        path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Save trained model and vectorizer to disk

        Args:
            model: Trained classifier
            vectorizer: Fitted TF-IDF vectorizer
            path: Path to save model (will create parent dirs)
            metadata: Optional metadata to save with model
        """
        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)

        # Package model, vectorizer, and metadata together
        model_data = {
            'model': model,
            'vectorizer': vectorizer,
            'metadata': metadata or {},
            'version': '1.0.0'
        }

        joblib.dump(model_data, path)

    def load_model(self, path: str) -> Tuple[MultinomialNB, TfidfVectorizer, Dict[str, Any]]:
        """
        Load trained model and vectorizer from disk

        Args:
            path: Path to model file

        Returns:
            Tuple of (model, vectorizer, metadata)
        """
        model_data = joblib.load(path)

        return (
            model_data['model'],
            model_data['vectorizer'],
            model_data.get('metadata', {})
        )

    def get_feature_importance(
        self,
        model: MultinomialNB,
        vectorizer: TfidfVectorizer,
        top_n: int = 20
    ) -> Dict[str, List[Tuple[str, float]]]:
        """
        Get most important features (words) for each class

        Args:
            model: Trained classifier
            vectorizer: Fitted vectorizer
            top_n: Number of top features to return per class

        Returns:
            Dictionary mapping class name to list of (word, importance) tuples
        """
        feature_names = vectorizer.get_feature_names_out()
        feature_importance = {}

        for idx, class_name in enumerate(model.classes_):
            # Get log probabilities for this class
            log_probs = model.feature_log_prob_[idx]

            # Get top N features
            top_indices = np.argsort(log_probs)[-top_n:][::-1]
            top_features = [
                (feature_names[i], float(log_probs[i]))
                for i in top_indices
            ]

            feature_importance[class_name] = top_features

        return feature_importance
