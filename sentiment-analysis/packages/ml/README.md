# ML Package - Sentiment Analysis

Classical machine learning implementation for sentiment analysis using TF-IDF and Multinomial Naive Bayes.

## Overview

This package provides:
- **Text Preprocessing**: Clean and normalize text data
- **Model Training**: Train sentiment classifiers with TF-IDF + Naive Bayes
- **Inference**: Fast sentiment prediction on new texts
- **Evaluation**: Comprehensive metrics and model analysis

## Architecture

```
ml/
├── preprocessor.py    # Text cleaning and normalization
├── trainer.py         # Model training with TF-IDF + NB
├── predictor.py       # Inference and prediction
├── evaluator.py       # Metrics and evaluation
└── __init__.py        # Package exports
```

## Quick Start

### Training a Model

```python
from ml import ModelTrainer

# Initialize trainer
trainer = ModelTrainer(
    max_features=5000,      # TF-IDF vocabulary size
    ngram_range=(1, 2),     # Unigrams + bigrams
    min_df=2,               # Minimum document frequency
    max_df=0.9              # Maximum document frequency
)

# Train on labeled data
texts = ["Great product!", "Terrible experience.", "It's okay."]
labels = ["positive", "negative", "neutral"]

model, vectorizer, metrics = trainer.train(
    texts=texts,
    labels=labels,
    test_size=0.2
)

# Save model
trainer.save_model(model, vectorizer, "models/sentiment.joblib")

print(f"F1 Score: {metrics['f1_macro']:.3f}")
```

### Making Predictions

```python
from ml import SentimentPredictor

# Load model
predictor = SentimentPredictor("models/sentiment.joblib")

# Predict single text
result = predictor.predict("This is amazing!")

print(result)
# {
#     'predicted_label': 'positive',
#     'confidence': 0.87,
#     'sentiment_scores': {
#         'positive': 0.87,
#         'neutral': 0.10,
#         'negative': 0.03
#     }
# }

# Batch prediction
texts = ["Great!", "Bad.", "Okay."]
results = predictor.predict_batch(texts)
```

### Explaining Predictions

```python
# Get explanation for prediction
explanation = predictor.explain("This product is fantastic!")

print(explanation['top_positive_words'])  # ['fantastic', 'product', ...]
print(explanation['top_negative_words'])  # []
print(explanation['reasoning'])           # "Classified as positive with 92% confidence"
```

## Components

### 1. TextPreprocessor

Cleans and normalizes text data.

**Features:**
- URL removal
- Email removal
- HTML tag stripping
- Whitespace normalization
- Lowercasing
- Optional punctuation removal

**Usage:**
```python
from ml import TextPreprocessor

preprocessor = TextPreprocessor(
    lowercase=True,
    remove_punctuation=False  # Keep punctuation for better sentiment
)

clean_text = preprocessor.preprocess("Check out http://example.com!!!")
# "check out"

batch = preprocessor.preprocess_batch(["Text 1", "Text 2"])
```

### 2. ModelTrainer

Trains sentiment classifiers using TF-IDF + Multinomial Naive Bayes.

**Parameters:**
- `max_features`: Maximum vocabulary size (default: 5000)
- `ngram_range`: N-gram range tuple (default: (1, 2) for unigrams + bigrams)
- `min_df`: Minimum document frequency (default: 2)
- `max_df`: Maximum document frequency (default: 0.9)

**Methods:**
- `train(texts, labels, test_size, random_state)`: Train model
- `save_model(model, vectorizer, path, metadata)`: Save to disk
- `load_model(path)`: Load from disk
- `get_feature_importance(model, vectorizer, top_n)`: Get top features per class

**Example:**
```python
trainer = ModelTrainer(max_features=10000)

model, vectorizer, metrics = trainer.train(
    texts=training_texts,
    labels=training_labels
)

# Get top words for each sentiment
importance = trainer.get_feature_importance(model, vectorizer, top_n=20)
print(importance['positive'])  # [('great', -2.3), ('amazing', -2.5), ...]
```

### 3. SentimentPredictor

Fast inference with trained models.

**Methods:**
- `load_model(path)`: Load model from disk
- `predict(text)`: Predict single text
- `predict_batch(texts, batch_size)`: Predict multiple texts
- `explain(text, top_n)`: Explain prediction with feature contributions
- `get_model_info()`: Get model metadata

**Features:**
- Batch processing for efficiency
- Explainable predictions
- Probability scores for all classes

**Example:**
```python
predictor = SentimentPredictor()
predictor.load_model("models/sentiment.joblib")

# Check if loaded
if predictor.is_loaded():
    result = predictor.predict("Amazing product!")

# Batch with custom batch size
results = predictor.predict_batch(large_list, batch_size=500)

# Get model info
info = predictor.get_model_info()
print(f"Classes: {info['classes']}")
print(f"Features: {info['n_features']}")
```

### 4. ModelEvaluator

Comprehensive model evaluation and metrics.

**Methods:**
- `evaluate(y_true, y_pred, y_pred_proba, class_names)`: Full evaluation
- `confusion_matrix(y_true, y_pred)`: Confusion matrix
- `classification_report_dict(y_true, y_pred)`: sklearn classification report
- `calculate_confidence_metrics(y_true, y_pred, y_pred_proba)`: Confidence analysis
- `get_misclassifications(texts, y_true, y_pred, limit)`: Misclassification examples

**Metrics Provided:**
- Accuracy
- Precision (macro, weighted, per-class)
- Recall (macro, weighted, per-class)
- F1 Score (macro, weighted, per-class)
- Confusion matrix
- Average confidence
- Confidence calibration

**Example:**
```python
from ml import ModelEvaluator

evaluator = ModelEvaluator()

metrics = evaluator.evaluate(
    y_true=test_labels,
    y_pred=predictions,
    y_pred_proba=probabilities,
    class_names=['positive', 'neutral', 'negative']
)

print(f"Accuracy: {metrics['accuracy']:.3f}")
print(f"F1 (macro): {metrics['f1_macro']:.3f}")
print(f"Per-class F1: {metrics['f1']}")

# Confidence analysis
conf_metrics = evaluator.calculate_confidence_metrics(
    y_true, y_pred, y_pred_proba
)
print(f"Avg confidence (correct): {conf_metrics['avg_confidence_correct']:.3f}")
print(f"Calibration: {conf_metrics['calibration']}")

# Get misclassifications
errors = evaluator.get_misclassifications(
    texts=test_texts,
    y_true=test_labels,
    y_pred=predictions,
    limit=10
)
for error in errors:
    print(f"Text: {error['text']}")
    print(f"True: {error['true_label']}, Predicted: {error['predicted_label']}")
```

## Training Script

Train initial model using seed data:

```bash
cd apps/api
poetry run python scripts/train_initial_model.py
```

This script:
1. Loads training data from database
2. Trains TF-IDF + Naive Bayes model
3. Evaluates on held-out test set
4. Saves model to `apps/api/models/`
5. Creates database record

## Performance

### Speed
- **Training**: ~1-2 seconds for 1000 samples
- **Inference**: <1ms per prediction
- **Batch**: ~10,000 predictions/second

### Accuracy
- **F1 Score**: Typically 0.75-0.85 on balanced datasets
- **Suitable for**: Product reviews, customer feedback, social media
- **Limitations**: Struggles with sarcasm (~30-40% accuracy)

### Memory
- **Model size**: ~1-5 MB (depending on vocabulary)
- **Runtime memory**: ~50-100 MB

## Algorithm Details

### TF-IDF (Term Frequency-Inverse Document Frequency)

Converts text to numerical features based on word importance.

**Formula:**
```
tfidf(t, d) = tf(t, d) × idf(t)

where:
  tf(t, d) = frequency of term t in document d
  idf(t) = log(N / df(t))
  N = total number of documents
  df(t) = number of documents containing term t
```

**Configuration:**
- Sublinear TF scaling: `1 + log(tf)` instead of raw `tf`
- L2 normalization of vectors
- English stop words removed
- 1-grams and 2-grams (captures phrases like "not good")

### Multinomial Naive Bayes

Probabilistic classifier based on Bayes' theorem.

**Formula:**
```
P(class|document) ∝ P(class) × ∏ P(word|class)^count(word)
```

**Advantages:**
- Fast training and inference
- Works well with high-dimensional data
- Interpretable (can inspect feature weights)
- Good baseline for text classification

**Smoothing:**
- Laplace smoothing with α=0.1
- Prevents zero probabilities for unseen words

## Model File Format

Models are saved using `joblib` with the following structure:

```python
{
    'model': MultinomialNB object,
    'vectorizer': TfidfVectorizer object,
    'metadata': {
        'trained_at': timestamp,
        'training_samples': int,
        'metrics': dict,
        ...
    },
    'version': '1.0.0'
}
```

## Improving Performance

### More Training Data
```python
# Add more labeled examples
# Aim for:
#  - 1000+ samples per class (positive, neutral, negative)
#  - Balanced distribution
#  - Diverse language and topics
```

### Hyperparameter Tuning
```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    'max_features': [3000, 5000, 10000],
    'ngram_range': [(1, 1), (1, 2), (1, 3)],
    'alpha': [0.01, 0.1, 1.0]  # For MultinomialNB
}

# Use GridSearchCV with your data
```

### Feature Engineering
```python
# Add custom preprocessing
preprocessor = TextPreprocessor(
    lowercase=True,
    remove_punctuation=False  # Punctuation helps ("!!!", "?")
)

# Consider:
# - Negation handling ("not good" → "not_good")
# - Emoji processing
# - Spell correction
```

## Limitations

1. **Sarcasm**: Poor at detecting sarcasm and irony
2. **Context**: No understanding of broader context
3. **Negation**: Limited negation handling ("not good" may be misclassified)
4. **Domain-specific**: Requires retraining for new domains
5. **Language**: English only (current implementation)

## Next Steps

- [ ] Add negation handling (e.g., "not_good" bigrams)
- [ ] Implement emotion classification (separate model)
- [ ] Support for other languages
- [ ] Ensemble methods (combine multiple models)
- [ ] Active learning for labeling
- [ ] Model versioning and A/B testing

## References

- [TF-IDF Wikipedia](https://en.wikipedia.org/wiki/Tf%E2%80%93idf)
- [Naive Bayes Text Classification](https://nlp.stanford.edu/IR-book/html/htmledition/naive-bayes-text-classification-1.html)
- [scikit-learn TfidfVectorizer](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
- [scikit-learn MultinomialNB](https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.MultinomialNB.html)
