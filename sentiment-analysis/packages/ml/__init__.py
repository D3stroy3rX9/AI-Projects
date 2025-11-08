"""
Machine Learning package for sentiment analysis
Contains model training, inference, and evaluation modules
"""

from .trainer import ModelTrainer
from .predictor import SentimentPredictor
from .evaluator import ModelEvaluator
from .preprocessor import TextPreprocessor, create_default_preprocessor

__version__ = "1.0.0"

__all__ = [
    'ModelTrainer',
    'SentimentPredictor',
    'ModelEvaluator',
    'TextPreprocessor',
    'create_default_preprocessor',
]
