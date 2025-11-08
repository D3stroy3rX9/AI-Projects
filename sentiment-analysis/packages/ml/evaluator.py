"""
Model evaluation module
Handles model performance evaluation with comprehensive metrics
"""

import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix as sklearn_confusion_matrix,
    classification_report
)


class ModelEvaluator:
    """Evaluate sentiment analysis model performance"""

    def evaluate(
        self,
        y_true: List[str],
        y_pred: List[str],
        y_pred_proba: Optional[np.ndarray] = None,
        class_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive model evaluation

        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Prediction probabilities (optional)
            class_names: List of class names (optional)

        Returns:
            Dictionary with evaluation metrics
        """
        # Overall metrics
        accuracy = accuracy_score(y_true, y_pred)

        # Per-class metrics (macro average)
        precision_macro = precision_score(y_true, y_pred, average='macro', zero_division=0)
        recall_macro = recall_score(y_true, y_pred, average='macro', zero_division=0)
        f1_macro = f1_score(y_true, y_pred, average='macro', zero_division=0)

        # Per-class metrics (weighted average)
        precision_weighted = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        recall_weighted = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        f1_weighted = f1_score(y_true, y_pred, average='weighted', zero_division=0)

        # Per-class breakdown
        if class_names is None:
            class_names = sorted(list(set(y_true)))

        precision_per_class = precision_score(
            y_true, y_pred, average=None, labels=class_names, zero_division=0
        )
        recall_per_class = recall_score(
            y_true, y_pred, average=None, labels=class_names, zero_division=0
        )
        f1_per_class = f1_score(
            y_true, y_pred, average=None, labels=class_names, zero_division=0
        )

        # Build per-class dictionaries
        precision_dict = {
            class_names[i]: float(precision_per_class[i])
            for i in range(len(class_names))
        }
        recall_dict = {
            class_names[i]: float(recall_per_class[i])
            for i in range(len(class_names))
        }
        f1_dict = {
            class_names[i]: float(f1_per_class[i])
            for i in range(len(class_names))
        }

        # Confusion matrix
        cm = sklearn_confusion_matrix(y_true, y_pred, labels=class_names)

        # Average confidence (if probabilities provided)
        avg_confidence = None
        if y_pred_proba is not None:
            confidences = np.max(y_pred_proba, axis=1)
            avg_confidence = float(np.mean(confidences))

        return {
            'accuracy': float(accuracy),
            'precision_macro': float(precision_macro),
            'recall_macro': float(recall_macro),
            'f1_macro': float(f1_macro),
            'precision_weighted': float(precision_weighted),
            'recall_weighted': float(recall_weighted),
            'f1_weighted': float(f1_weighted),
            'precision': precision_dict,
            'recall': recall_dict,
            'f1': f1_dict,
            'confusion_matrix': cm.tolist(),
            'avg_confidence': avg_confidence,
            'n_samples': len(y_true)
        }

    def confusion_matrix(
        self,
        y_true: List[str],
        y_pred: List[str],
        class_names: Optional[List[str]] = None
    ) -> np.ndarray:
        """
        Generate confusion matrix

        Args:
            y_true: True labels
            y_pred: Predicted labels
            class_names: List of class names (optional)

        Returns:
            Confusion matrix as numpy array
        """
        return sklearn_confusion_matrix(y_true, y_pred, labels=class_names)

    def classification_report_dict(
        self,
        y_true: List[str],
        y_pred: List[str]
    ) -> Dict[str, Any]:
        """
        Generate classification report as dictionary

        Args:
            y_true: True labels
            y_pred: Predicted labels

        Returns:
            Classification report dictionary
        """
        return classification_report(y_true, y_pred, output_dict=True, zero_division=0)

    def calculate_confidence_metrics(
        self,
        y_true: List[str],
        y_pred: List[str],
        y_pred_proba: np.ndarray
    ) -> Dict[str, float]:
        """
        Calculate confidence-related metrics

        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Prediction probabilities

        Returns:
            Dictionary with confidence metrics
        """
        # Get max probability for each prediction
        confidences = np.max(y_pred_proba, axis=1)

        # Check which predictions were correct
        correct = np.array(y_true) == np.array(y_pred)

        # Average confidence
        avg_confidence = float(np.mean(confidences))
        avg_confidence_correct = float(np.mean(confidences[correct])) if correct.any() else 0.0
        avg_confidence_incorrect = float(np.mean(confidences[~correct])) if (~correct).any() else 0.0

        # Confidence calibration: split into bins
        bins = [0.0, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        calibration = {}

        for i in range(len(bins) - 1):
            bin_mask = (confidences >= bins[i]) & (confidences < bins[i + 1])
            if bin_mask.any():
                bin_accuracy = float(np.mean(correct[bin_mask]))
                bin_count = int(np.sum(bin_mask))
                calibration[f"{bins[i]:.1f}-{bins[i+1]:.1f}"] = {
                    'accuracy': bin_accuracy,
                    'count': bin_count
                }

        return {
            'avg_confidence': avg_confidence,
            'avg_confidence_correct': avg_confidence_correct,
            'avg_confidence_incorrect': avg_confidence_incorrect,
            'calibration': calibration
        }

    def get_misclassifications(
        self,
        texts: List[str],
        y_true: List[str],
        y_pred: List[str],
        y_pred_proba: Optional[np.ndarray] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get examples of misclassified samples

        Args:
            texts: Original texts
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Prediction probabilities (optional)
            limit: Maximum number of examples to return

        Returns:
            List of misclassification examples
        """
        misclassified = []

        for i, (text, true_label, pred_label) in enumerate(zip(texts, y_true, y_pred)):
            if true_label != pred_label:
                example = {
                    'text': text,
                    'true_label': true_label,
                    'predicted_label': pred_label
                }

                if y_pred_proba is not None:
                    example['confidence'] = float(np.max(y_pred_proba[i]))

                misclassified.append(example)

                if len(misclassified) >= limit:
                    break

        return misclassified
