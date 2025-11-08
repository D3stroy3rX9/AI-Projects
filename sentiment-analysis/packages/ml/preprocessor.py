"""
Text preprocessing utilities for sentiment analysis
"""

import re
import string
from typing import List


class TextPreprocessor:
    """Preprocessing pipeline for text data"""

    def __init__(self, lowercase: bool = True, remove_punctuation: bool = False):
        """
        Initialize preprocessor

        Args:
            lowercase: Convert text to lowercase
            remove_punctuation: Remove punctuation marks
        """
        self.lowercase = lowercase
        self.remove_punctuation = remove_punctuation

    def preprocess(self, text: str) -> str:
        """
        Preprocess a single text

        Args:
            text: Raw input text

        Returns:
            Preprocessed text
        """
        # Convert to string if not already
        text = str(text)

        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)

        # Remove HTML tags
        text = re.sub(r'<.*?>', '', text)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Lowercase
        if self.lowercase:
            text = text.lower()

        # Remove punctuation (optional - can help or hurt depending on dataset)
        if self.remove_punctuation:
            text = text.translate(str.maketrans('', '', string.punctuation))

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    def preprocess_batch(self, texts: List[str]) -> List[str]:
        """
        Preprocess multiple texts

        Args:
            texts: List of raw texts

        Returns:
            List of preprocessed texts
        """
        return [self.preprocess(text) for text in texts]


def create_default_preprocessor() -> TextPreprocessor:
    """
    Create preprocessor with default settings

    Returns:
        Configured TextPreprocessor
    """
    return TextPreprocessor(
        lowercase=True,
        remove_punctuation=False  # Keep punctuation for better sentiment detection
    )
