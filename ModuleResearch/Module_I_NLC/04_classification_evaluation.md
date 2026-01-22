# Module I - Part 4: Classification, Evaluation, and Deployment

## Table of Contents
1. [Introduction](#1-introduction)
2. [Logistic Regression for Multi-Label Classification](#2-logistic-regression-for-multi-label-classification)
3. [Training Pipeline](#3-training-pipeline)
4. [Train-Test Split Strategy](#4-train-test-split-strategy)
5. [Evaluation Metrics](#5-evaluation-metrics)
6. [Confusion Matrix Analysis](#6-confusion-matrix-analysis)
7. [Model Persistence](#7-model-persistence)
8. [API Integration](#8-api-integration)
9. [Testing and Validation](#9-testing-and-validation)
10. [Complete Production Code](#10-complete-production-code)
11. [References](#11-references)

---

## 1. Introduction

### 1.1 From Features to Categories

This document completes the NLC pipeline by covering the **classification** step:

```
┌─────────────────────────────────────────────────────────┐
│           Complete NLC Pipeline (Module I)              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  User Input: "I want beaches and water sports"        │
│                       │                                 │
│                       ▼                                 │
│  ┌──────────────────────────────────────────┐          │
│  │  TF-IDF Vectorization (Covered)          │          │
│  │  Output: [0.0, 0.52, ..., 0.31]          │          │
│  │          (1000-dim vector)                │          │
│  └──────────────────────────────────────────┘          │
│                       │                                 │
│                       ▼                                 │
│  ┌──────────────────────────────────────────┐          │
│  │  Logistic Regression (THIS DOCUMENT)     │          │
│  │  • Train on labeled data                 │          │
│  │  • Predict categories (multi-label)       │          │
│  │  Output: [1, 0, 1, 0, 0, 0, 0]           │          │
│  │          (7 binary predictions)           │          │
│  └──────────────────────────────────────────┘          │
│                       │                                 │
│                       ▼                                 │
│  Categories: ["Beaches", "Adventure"]                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Learning Objectives

By the end of this document, you will be able to:
1. Train a multi-label Logistic Regression classifier for 7 tourism categories
2. Evaluate model performance using Precision, Recall, F1-Score
3. Interpret confusion matrices to identify misclassification patterns
4. Save and load trained models for production deployment
5. Integrate the NLC module into WanderWise+ backend API
6. Test the complete system with real user inputs

---

## 2. Logistic Regression for Multi-Label Classification

### 2.1 Why Logistic Regression?

**Logistic Regression** is a linear classifier that models the probability of class membership.

**Advantages for NLC**:
1. **Fast training**: O(n × m) complexity (n=samples, m=features)
2. **Fast inference**: <10ms for 1000-feature vectors
3. **Probabilistic output**: Can set confidence thresholds
4. **Interpretable**: Can inspect feature weights to understand decisions
5. **Low memory**: ~10MB model size

**Comparison to Alternatives**:

| Classifier | Accuracy | Training Time | Inference Time | Model Size |
|------------|----------|---------------|----------------|------------|
| **Logistic Regression** | 88-92% | <5 min | <10ms | 10MB ✅ |
| Naive Bayes | 85-88% | <2 min | <5ms | 5MB |
| SVM (Linear) | 90-93% | 10-15 min | <20ms | 15MB |
| Random Forest | 86-90% | 5-10 min | <30ms | 50MB |
| Neural Network | 90-94% | 15-30 min | <50ms | 80MB |

**Verdict**: Logistic Regression offers best speed-accuracy trade-off for 7-class problem.

### 2.2 Binary Logistic Regression (Single Category)

**Problem**: Predict if user is interested in "Beaches" (yes/no)

**Model**:
```
P(y=1 | x) = sigmoid(w·x + b)

Where:
sigmoid(z) = 1 / (1 + e^(-z))
w = learned weight vector (1000 dimensions)
b = bias term (scalar)
x = TF-IDF feature vector (1000 dimensions)
P(y=1 | x) = probability of Beaches category
```

**Training**: Find optimal weights `w` that maximize likelihood of training labels

**Decision Rule**:
```
If P(y=1 | x) > 0.5:
    Predict: Beaches = YES
Else:
    Predict: Beaches = NO
```

**Example**:
```
User Input: "I love swimming and beaches"
TF-IDF vector x: [0.0, 0.52, 0.67, 0.0, ...]

Weights w (learned): [0.0, 2.1, 3.4, 0.0, ...]
                      └─────────────────────── High weights for "swimming", "beaches"

Compute: w·x = (0.0 × 0.0) + (2.1 × 0.52) + (3.4 × 0.67) + ...
             = 0.0 + 1.092 + 2.278 + ...
             = 4.87

Apply sigmoid: P(y=1 | x) = 1 / (1 + e^(-4.87))
                          = 1 / (1 + 0.008)
                          = 0.992 → 99.2% confidence

Decision: 0.992 > 0.5 → Predict Beaches = YES ✅
```

### 2.3 Multi-Label Extension (7 Categories)

**Approach**: Train **7 independent binary classifiers** (One-vs-Rest strategy)

```
Classifier 1: Beaches vs Not-Beaches
Classifier 2: Historical vs Not-Historical
Classifier 3: Adventure vs Not-Adventure
Classifier 4: Nature vs Not-Nature
Classifier 5: Food vs Not-Food
Classifier 6: Nightlife vs Not-Nightlife
Classifier 7: Shopping vs Not-Shopping
```

**Prediction Process**:
```python
# For each category, get probability
P_beaches = classifier_1.predict_proba(x)[0, 1]       # 0.92
P_historical = classifier_2.predict_proba(x)[0, 1]    # 0.12
P_adventure = classifier_3.predict_proba(x)[0, 1]     # 0.87
P_nature = classifier_4.predict_proba(x)[0, 1]        # 0.23
P_food = classifier_5.predict_proba(x)[0, 1]          # 0.15
P_nightlife = classifier_6.predict_proba(x)[0, 1]     # 0.08
P_shopping = classifier_7.predict_proba(x)[0, 1]      # 0.05

# Apply threshold (e.g., 0.5)
threshold = 0.5
predictions = [
    1 if P_beaches > threshold else 0,      # 1 (YES)
    1 if P_historical > threshold else 0,   # 0 (NO)
    1 if P_adventure > threshold else 0,    # 1 (YES)
    1 if P_nature > threshold else 0,       # 0 (NO)
    1 if P_food > threshold else 0,         # 0 (NO)
    1 if P_nightlife > threshold else 0,    # 0 (NO)
    1 if P_shopping > threshold else 0      # 0 (NO)
]

# Result: [1, 0, 1, 0, 0, 0, 0] → Beaches + Adventure
```

**Scikit-learn Implementation**:
```python
from sklearn.linear_model import LogisticRegression
from sklearn.multioutput import MultiOutputClassifier

# Initialize
base_classifier = LogisticRegression(
    max_iter=1000,
    C=1.0,
    random_state=42
)

# Wrap for multi-label
classifier = MultiOutputClassifier(base_classifier)

# Train (y_train shape: [n_samples, 7])
classifier.fit(X_train, y_train)

# Predict (returns [n_samples, 7] binary matrix)
predictions = classifier.predict(X_test)
```

---

## 3. Training Pipeline

### 3.1 Complete Training Code

```python
# backend/scripts/train_nlc_classifier.py

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score
import joblib
from pathlib import Path

def train_nlc_model():
    """
    Train complete NLC model (TF-IDF + Logistic Regression).
    """
    
    # ===== 1. LOAD DATA =====
    print("Loading training data...")
    df = pd.read_csv('data/nlc_training_data.csv')
    
    X_text = df['text'].values
    y_labels = df[['beaches', 'historical', 'adventure', 'nature', 
                   'food', 'nightlife', 'shopping']].values
    
    print(f"Total examples: {len(X_text)}")
    print(f"Label distribution:\n{df.iloc[:, 1:].sum()}")
    
    # ===== 2. TRAIN-TEST SPLIT =====
    print("\nSplitting train/test (80/20)...")
    X_train_text, X_test_text, y_train, y_test = train_test_split(
        X_text, y_labels, test_size=0.2, random_state=42, stratify=y_labels[:, 0]
    )
    
    print(f"Training samples: {len(X_train_text)}")
    print(f"Test samples: {len(X_test_text)}")
    
    # ===== 3. TF-IDF VECTORIZATION =====
    print("\nTraining TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(
        max_features=1000,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.8,
        stop_words='english',
        norm='l2'
    )
    
    X_train = vectorizer.fit_transform(X_train_text)
    X_test = vectorizer.transform(X_test_text)
    
    print(f"Feature matrix shape: {X_train.shape}")
    print(f"Vocabulary size: {len(vectorizer.get_feature_names_out())}")
    
    # ===== 4. TRAIN CLASSIFIER =====
    print("\nTraining Logistic Regression classifier...")
    classifier = MultiOutputClassifier(
        LogisticRegression(
            max_iter=1000,
            C=1.0,
            random_state=42,
            solver='lbfgs'
        )
    )
    
    classifier.fit(X_train, y_train)
    
    # ===== 5. EVALUATE =====
    print("\nEvaluating on test set...")
    y_pred = classifier.predict(X_test)
    
    # Per-category metrics
    categories = ['Beaches', 'Historical', 'Adventure', 'Nature', 
                  'Food', 'Nightlife', 'Shopping']
    
    for i, cat in enumerate(categories):
        f1 = f1_score(y_test[:, i], y_pred[:, i])
        print(f"  {cat}: F1={f1:.3f}")
    
    # Overall metrics
    f1_macro = f1_score(y_test, y_pred, average='macro')
    f1_micro = f1_score(y_test, y_pred, average='micro')
    
    print(f"\nOverall Performance:")
    print(f"  Macro F1: {f1_macro:.3f}")
    print(f"  Micro F1: {f1_micro:.3f}")
    
    # ===== 6. SAVE MODELS =====
    print("\nSaving models...")
    Path('models').mkdir(exist_ok=True)
    
    joblib.dump(vectorizer, 'models/tfidf_vectorizer.pkl')
    joblib.dump(classifier, 'models/logistic_classifier.pkl')
    
    print("✅ Training complete!")
    print("Models saved to:")
    print("  - models/tfidf_vectorizer.pkl")
    print("  - models/logistic_classifier.pkl")
    
    return vectorizer, classifier

if __name__ == "__main__":
    train_nlc_model()
```

### 3.2 Hyperparameter Tuning (Optional)

**Key Hyperparameters**:

| Parameter | Description | Default | Tuning Range | Optimal (WanderWise+) |
|-----------|-------------|---------|--------------|----------------------|
| `C` | Regularization strength (inverse) | 1.0 | [0.1, 1.0, 10.0] | **1.0** ✅ |
| `max_iter` | Maximum iterations | 100 | [500, 1000, 2000] | **1000** |
| `solver` | Optimization algorithm | 'lbfgs' | ['lbfgs', 'liblinear'] | **'lbfgs'** |
| `class_weight` | Handle imbalanced classes | None | [None, 'balanced'] | **None** (data is balanced) |

**Grid Search Example**:
```python
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import make_scorer, f1_score

# Define parameter grid
param_grid = {
    'estimator__C': [0.1, 1.0, 10.0],
    'estimator__max_iter': [500, 1000, 2000]
}

# Multi-label scorer
scorer = make_scorer(f1_score, average='macro')

# Grid search
grid_search = GridSearchCV(
    MultiOutputClassifier(LogisticRegression(random_state=42)),
    param_grid,
    cv=5,
    scoring=scorer,
    n_jobs=-1
)

grid_search.fit(X_train, y_train)

print(f"Best params: {grid_search.best_params_}")
print(f"Best F1 score: {grid_search.best_score_:.3f}")

# Result (typical):
# Best params: {'estimator__C': 1.0, 'estimator__max_iter': 1000}
# Best F1 score: 0.892
```

---

## 4. Train-Test Split Strategy

### 4.1 Standard Split (80/20)

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X_text, y_labels,
    test_size=0.2,      # 20% for testing
    random_state=42,    # Reproducibility
    stratify=y_labels[:, 0]  # Maintain class balance (first category)
)
```

**Rationale**:
- **80%** training: Need sufficient data for robust learning
- **20%** testing: Enough samples for reliable evaluation (100+ test examples)
- **Stratification**: Ensures test set has similar class distribution as training

### 4.2 Cross-Validation (K-Fold)

For smaller datasets (<500 examples), use K-Fold cross-validation:

```python
from sklearn.model_selection import cross_val_score

# 5-fold cross-validation
scores = cross_val_score(
    classifier, X_train, y_train,
    cv=5,
    scoring='f1_macro',
    n_jobs=-1
)

print(f"Cross-validation F1 scores: {scores}")
print(f"Mean F1: {scores.mean():.3f} ± {scores.std():.3f}")

# Output:
# Cross-validation F1 scores: [0.87, 0.89, 0.88, 0.91, 0.86]
# Mean F1: 0.882 ± 0.018
```

**When to Use**:
- Dataset < 500 examples: Use 5-fold or 10-fold CV
- Dataset > 500 examples: Simple 80/20 split is sufficient

### 4.3 Temporal Split (Time-Based)

If data has timestamps (e.g., user inputs collected over time):

```python
# Sort by timestamp
df_sorted = df.sort_values('created_at')

# Split: First 80% for training, last 20% for testing
split_idx = int(len(df_sorted) * 0.8)
df_train = df_sorted[:split_idx]
df_test = df_sorted[split_idx:]
```

**Advantage**: Simulates real-world deployment (train on past, test on future data)

---

## 5. Evaluation Metrics

### 5.1 Confusion Matrix (Per Category)

**Example: Beaches Category**

```
                Predicted
                NO   YES
Actual  NO    [[50    3]
        YES   [ 2   45]]

True Negatives (TN): 50  ← Correctly predicted NO
False Positives (FP): 3  ← Incorrectly predicted YES (should be NO)
False Negatives (FN): 2  ← Incorrectly predicted NO (should be YES)
True Positives (TP): 45  ← Correctly predicted YES
```

### 5.2 Precision, Recall, F1-Score

**Precision**: Of all predicted YES, how many are correct?
```
Precision = TP / (TP + FP)
          = 45 / (45 + 3)
          = 45 / 48
          = 0.938 (93.8%)
```
**Interpretation**: When model predicts "Beaches", it's right 93.8% of the time.

**Recall**: Of all actual YES, how many did we find?
```
Recall = TP / (TP + FN)
       = 45 / (45 + 2)
       = 45 / 47
       = 0.957 (95.7%)
```
**Interpretation**: Model catches 95.7% of actual "Beaches" interests.

**F1-Score**: Harmonic mean of Precision and Recall
```
F1 = 2 × (Precision × Recall) / (Precision + Recall)
   = 2 × (0.938 × 0.957) / (0.938 + 0.957)
   = 2 × 0.897 / 1.895
   = 0.947 (94.7%)
```
**Interpretation**: Balanced measure of classification quality.

### 5.3 Multi-Label Metrics

**Macro-Average**: Average F1 across all categories (equal weight per category)
```python
from sklearn.metrics import f1_score

f1_macro = f1_score(y_test, y_pred, average='macro')
# Computes F1 for each category, then averages
# Example: (0.94 + 0.88 + 0.85 + 0.81 + 0.90 + 0.87 + 0.76) / 7 = 0.86
```

**Micro-Average**: Aggregate all TPs, FPs, FNs, then compute F1
```python
f1_micro = f1_score(y_test, y_pred, average='micro')
# Treats all predictions equally (larger categories have more weight)
```

**Weighted-Average**: Weight by category frequency
```python
f1_weighted = f1_score(y_test, y_pred, average='weighted')
# Accounts for class imbalance
```

**WanderWise+ Focus**: **Macro F1** (we care about all categories equally)

### 5.4 Expected Performance Targets

| Category | Expected Precision | Expected Recall | Expected F1 | Priority |
|----------|-------------------|----------------|-------------|----------|
| Beaches | 92-95% | 90-93% | **91-94%** | High |
| Historical & Religious | 88-91% | 85-89% | **86-90%** | High |
| Adventure | 85-89% | 82-87% | **83-88%** | Medium |
| Nature | 87-90% | 80-85% | **83-87%** | Medium |
| Food & Cuisine | 90-93% | 88-91% | **89-92%** | High |
| Nightlife | 86-89% | 84-88% | **85-88%** | Medium |
| Shopping | 80-85% | 75-82% | **77-83%** | Low |

**Overall Target**: Macro F1 > 0.85 (85%)

---

## 6. Confusion Matrix Analysis

### 6.1 Multi-Label Confusion Matrix

```python
from sklearn.metrics import multilabel_confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Generate confusion matrices (one per category)
cm_multi = multilabel_confusion_matrix(y_test, y_pred)

# Plot
categories = ['Beaches', 'Historical', 'Adventure', 'Nature', 
              'Food', 'Nightlife', 'Shopping']

fig, axes = plt.subplots(2, 4, figsize=(16, 8))
axes = axes.ravel()

for i, (cm, cat) in enumerate(zip(cm_multi, categories)):
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[i])
    axes[i].set_title(f'{cat}')
    axes[i].set_xlabel('Predicted')
    axes[i].set_ylabel('Actual')

plt.tight_layout()
plt.savefig('confusion_matrices.png')
```

### 6.2 Common Misclassification Patterns

**Pattern 1: Adventure ↔ Beaches Overlap**
```
User Input: "Water sports like jet skiing"
True Labels: [Adventure=1, Beaches=1]  (multi-label correct)
Predicted:   [Adventure=1, Beaches=1]  ✅

Issue: Some annotators might label as only "Adventure" (inconsistent labeling)
Solution: Review training data, accept overlap as valid
```

**Pattern 2: Food ↔ Nightlife Confusion**
```
User Input: "Beach shack parties with drinks"
True Labels: [Beaches=1, Food=1, Nightlife=1]
Predicted:   [Beaches=1, Nightlife=1]  (missed Food)

Reason: "Drinks" associated with Nightlife, not Food
Solution: Add training examples: "beach shack food", "drinks and snacks"
```

**Pattern 3: Shopping Underperformance**
```
Shopping has lowest F1 (77-83%) because:
1. Fewer training examples (imbalanced dataset)
2. Generic keywords: "market" could be food market or shopping
3. Often combined with other interests ("night market" = Shopping + Nightlife)

Solution:
- Collect 50+ more Shopping-only examples
- Add specific keywords: "flea market", "souvenirs", "handicrafts"
```

### 6.3 Error Analysis Script

```python
# backend/scripts/analyze_errors.py

import pandas as pd
import numpy as np

def analyze_misclassifications(X_test_text, y_test, y_pred):
    """
    Identify and categorize prediction errors.
    """
    categories = ['Beaches', 'Historical', 'Adventure', 'Nature', 
                  'Food', 'Nightlife', 'Shopping']
    
    errors = []
    
    for i, (text, true, pred) in enumerate(zip(X_test_text, y_test, y_pred)):
        if not np.array_equal(true, pred):
            # Find differences
            true_cats = [categories[j] for j in range(7) if true[j] == 1]
            pred_cats = [categories[j] for j in range(7) if pred[j] == 1]
            
            errors.append({
                'text': text,
                'true_categories': true_cats,
                'predicted_categories': pred_cats,
                'missed': set(true_cats) - set(pred_cats),
                'extra': set(pred_cats) - set(true_cats)
            })
    
    # Report
    print(f"Total misclassifications: {len(errors)} / {len(y_test)} ({len(errors)/len(y_test)*100:.1f}%)")
    
    # Show examples
    print("\nSample misclassifications:")
    for error in errors[:5]:
        print(f"\nText: \"{error['text']}\"")
        print(f"  True: {error['true_categories']}")
        print(f"  Predicted: {error['predicted_categories']}")
        if error['missed']:
            print(f"  Missed: {error['missed']}")
        if error['extra']:
            print(f"  Extra: {error['extra']}")
    
    return errors

# Usage
errors = analyze_misclassifications(X_test_text, y_test, y_pred)
```

---

## 7. Model Persistence

### 7.1 Saving Models

```python
import joblib

# Save TF-IDF vectorizer
joblib.dump(vectorizer, 'models/tfidf_vectorizer.pkl', compress=3)

# Save classifier
joblib.dump(classifier, 'models/logistic_classifier.pkl', compress=3)

# File sizes (approximate):
#   tfidf_vectorizer.pkl: ~8-12 MB
#   logistic_classifier.pkl: ~2-5 MB
```

**Compression Levels**:
- `compress=0`: No compression (fastest save/load)
- `compress=3`: Medium compression (good balance) ✅
- `compress=9`: Maximum compression (smallest file, slower)

### 7.2 Loading Models

```python
import joblib

# Load models
vectorizer = joblib.load('models/tfidf_vectorizer.pkl')
classifier = joblib.load('models/logistic_classifier.pkl')

# Predict
user_input = "I want beaches and water sports"
X = vectorizer.transform([user_input])
prediction = classifier.predict(X)

# Output: [[1, 0, 1, 0, 0, 0, 0]]
```

### 7.3 Model Versioning

**Strategy**: Include timestamp or version number in filename

```python
from datetime import datetime

# Save with version
version = datetime.now().strftime('%Y%m%d_%H%M%S')
joblib.dump(vectorizer, f'models/tfidf_vectorizer_{version}.pkl')
joblib.dump(classifier, f'models/logistic_classifier_{version}.pkl')

# Create symlink to "latest"
import os
os.symlink(f'tfidf_vectorizer_{version}.pkl', 'models/tfidf_vectorizer_latest.pkl')
os.symlink(f'logistic_classifier_{version}.pkl', 'models/logistic_classifier_latest.pkl')

# Load latest
vectorizer = joblib.load('models/tfidf_vectorizer_latest.pkl')
```

---

## 8. API Integration

### 8.1 NLC Service Class

```python
# backend/app/services/nlc_classifier.py

import joblib
from pathlib import Path
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

CATEGORIES = [
    "Beaches",
    "Historical & Religious",
    "Adventure",
    "Nature",
    "Food & Cuisine",
    "Nightlife",
    "Shopping"
]

class NLCClassifier:
    """
    Natural Language to Category classifier for WanderWise+.
    
    Converts user natural language input into structured interest categories.
    """
    
    def __init__(self, model_dir: str = "models"):
        """
        Initialize classifier by loading trained models.
        
        Args:
            model_dir: Directory containing model files
        """
        model_path = Path(model_dir)
        
        try:
            self.vectorizer = joblib.load(model_path / "tfidf_vectorizer.pkl")
            self.classifier = joblib.load(model_path / "logistic_classifier.pkl")
            logger.info("NLC models loaded successfully")
        except FileNotFoundError as e:
            logger.error(f"Model files not found: {e}")
            raise RuntimeError("NLC models not available. Run training script first.")
    
    def predict(self, text: str) -> List[str]:
        """
        Predict interest categories from text.
        
        Args:
            text: User input (natural language)
        
        Returns:
            List of predicted category names
        """
        # Validate input
        if not text or len(text.strip()) < 3:
            raise ValueError("Text must be at least 3 characters")
        
        # Transform
        X = self.vectorizer.transform([text])
        
        # Predict
        predictions = self.classifier.predict(X)[0]
        
        # Convert to category names
        categories = [CATEGORIES[i] for i in range(len(CATEGORIES)) if predictions[i] == 1]
        
        # Fallback: if no categories predicted, return most confident
        if not categories:
            probas = self.get_probabilities(text)
            top_cat = max(probas, key=probas.get)
            categories = [top_cat]
            logger.warning(f"No categories above threshold for '{text}', returning top: {top_cat}")
        
        return categories
    
    def get_probabilities(self, text: str) -> dict:
        """
        Get probability scores for all categories.
        
        Args:
            text: User input
        
        Returns:
            Dictionary mapping category names to probabilities
        """
        X = self.vectorizer.transform([text])
        
        # Get probability scores (7 classifiers)
        probas = []
        for estimator in self.classifier.estimators_:
            proba = estimator.predict_proba(X)[0, 1]  # P(category=1)
            probas.append(proba)
        
        return dict(zip(CATEGORIES, probas))
    
    def predict_with_confidence(self, text: str, threshold: float = 0.3) -> Tuple[List[str], dict]:
        """
        Predict categories with confidence filtering.
        
        Args:
            text: User input
            threshold: Minimum confidence (0-1)
        
        Returns:
            (categories, confidence_scores)
        """
        probas = self.get_probabilities(text)
        
        # Filter by threshold
        categories = [cat for cat, prob in probas.items() if prob > threshold]
        confidence_scores = {cat: probas[cat] for cat in categories}
        
        # Fallback
        if not categories:
            top_cat = max(probas, key=probas.get)
            categories = [top_cat]
            confidence_scores = {top_cat: probas[top_cat]}
        
        return categories, confidence_scores
```

### 8.2 FastAPI Endpoint

```python
# backend/app/api/routes.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.nlc_classifier import NLCClassifier
from typing import List

router = APIRouter()

# Lazy-load classifier (initialize once on first request)
_nlc_classifier = None

def get_nlc_classifier():
    global _nlc_classifier
    if _nlc_classifier is None:
        _nlc_classifier = NLCClassifier()
    return _nlc_classifier

# ===== REQUEST/RESPONSE SCHEMAS =====

class InterestRequest(BaseModel):
    text: str = Field(..., min_length=3, max_length=500, 
                     example="I love beaches and water sports")

class InterestResponse(BaseModel):
    categories: List[str]
    confidence_scores: dict[str, float]

# ===== ENDPOINT =====

@router.post("/api/nlc/predict", response_model=InterestResponse, tags=["NLC"])
def predict_interests(request: InterestRequest):
    """
    Predict interest categories from natural language input.
    
    **Example Request**:
    ```json
    {
        "text": "I want to visit beaches and try local Goan cuisine"
    }
    ```
    
    **Example Response**:
    ```json
    {
        "categories": ["Beaches", "Food & Cuisine"],
        "confidence_scores": {
            "Beaches": 0.92,
            "Food & Cuisine": 0.87
        }
    }
    ```
    """
    try:
        classifier = get_nlc_classifier()
        categories, scores = classifier.predict_with_confidence(request.text, threshold=0.3)
        
        return InterestResponse(
            categories=categories,
            confidence_scores=scores
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
```

### 8.3 Frontend Integration

```javascript
// frontend/src/services/nlcService.js

export async function predictInterests(userText) {
    const response = await fetch('/api/nlc/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: userText })
    });
    
    if (!response.ok) {
        throw new Error(`Failed to predict interests: ${response.statusText}`);
    }
    
    const data = await response.json();
    return data;  // { categories: [...], confidence_scores: {...} }
}

// Usage in React component
import { predictInterests } from '@/services/nlcService';

function InterestInputPage() {
    const [interests, setInterests] = useState([]);
    
    const handleSubmit = async (text) => {
        try {
            const result = await predictInterests(text);
            setInterests(result.categories);
            console.log('Confidence scores:', result.confidence_scores);
        } catch (error) {
            console.error('Prediction failed:', error);
        }
    };
    
    return (
        <div>
            <textarea onChange={(e) => handleSubmit(e.target.value)} />
            <div>Predicted interests: {interests.join(', ')}</div>
        </div>
    );
}
```

---

## 9. Testing and Validation

### 9.1 Unit Tests

```python
# backend/tests/test_nlc_classifier.py

import pytest
from app.services.nlc_classifier import NLCClassifier

@pytest.fixture
def classifier():
    return NLCClassifier(model_dir='models')

def test_predict_beaches(classifier):
    result = classifier.predict("I love swimming and sunbathing on beaches")
    assert "Beaches" in result

def test_predict_historical(classifier):
    result = classifier.predict("Want to visit old Portuguese churches and forts")
    assert "Historical & Religious" in result

def test_predict_multi_label(classifier):
    result = classifier.predict("Beaches, water sports, and local cuisine")
    assert "Beaches" in result
    assert "Adventure" in result or "Food & Cuisine" in result

def test_confidence_scores(classifier):
    categories, scores = classifier.predict_with_confidence("beaches")
    assert "Beaches" in categories
    assert scores["Beaches"] > 0.5

def test_empty_input_raises_error(classifier):
    with pytest.raises(ValueError):
        classifier.predict("")

def test_short_input_raises_error(classifier):
    with pytest.raises(ValueError):
        classifier.predict("ab")
```

### 9.2 Integration Tests

```python
# backend/tests/test_nlc_api.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_predict_endpoint():
    response = client.post("/api/nlc/predict", json={
        "text": "I want beaches and water sports"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert "confidence_scores" in data
    assert len(data["categories"]) > 0

def test_invalid_input():
    response = client.post("/api/nlc/predict", json={
        "text": "ab"  # Too short
    })
    assert response.status_code == 400
```

### 9.3 Manual Test Cases

```python
# backend/scripts/manual_test_nlc.py

from app.services.nlc_classifier import NLCClassifier

def test_nlc_manual():
    classifier = NLCClassifier()
    
    test_cases = [
        # (input_text, expected_categories)
        ("I love beaches and swimming", ["Beaches"]),
        ("Want to see historical churches", ["Historical & Religious"]),
        ("Scuba diving and parasailing", ["Adventure"]),
        ("Dudhsagar Waterfalls", ["Nature"]),
        ("Fish curry and seafood", ["Food & Cuisine"]),
        ("Nightclubs and party", ["Nightlife"]),
        ("Shopping at flea markets", ["Shopping"]),
        ("Beaches, food, and nightlife", ["Beaches", "Food & Cuisine", "Nightlife"]),
    ]
    
    print("=== Manual NLC Test ===\n")
    
    for text, expected in test_cases:
        categories, scores = classifier.predict_with_confidence(text)
        
        # Check if expected categories are in predictions
        match = all(cat in categories for cat in expected)
        status = "✅ PASS" if match else "❌ FAIL"
        
        print(f"{status} Input: \"{text}\"")
        print(f"  Expected: {expected}")
        print(f"  Predicted: {categories}")
        print(f"  Scores: {scores}\n")

if __name__ == "__main__":
    test_nlc_manual()
```

---

## 10. Complete Production Code

### 10.1 Full Module Structure

```
backend/
├── app/
│   ├── services/
│   │   ├── nlc_classifier.py          ← Main classifier service
│   │   └── tfidf_vectorizer.py        ← TF-IDF wrapper (from Part 3)
│   ├── api/
│   │   └── routes.py                  ← FastAPI endpoints
│   └── models/                        ← (Empty, for code organization)
│
├── models/                            ← Trained model files
│   ├── tfidf_vectorizer.pkl
│   └── logistic_classifier.pkl
│
├── data/
│   └── nlc_training_data.csv          ← Training data (from Part 2)
│
├── scripts/
│   ├── train_nlc_classifier.py        ← Training script
│   ├── test_tfidf.py                  ← TF-IDF testing
│   ├── manual_test_nlc.py             ← Manual validation
│   └── analyze_errors.py              ← Error analysis
│
└── tests/
    ├── test_nlc_classifier.py         ← Unit tests
    └── test_nlc_api.py                ← Integration tests
```

### 10.2 Deployment Checklist

```markdown
## Pre-Deployment Checklist

### 1. Training Data ✅
- [ ] Collected 100+ examples per category
- [ ] Balanced distribution (±30% variance)
- [ ] Multi-label examples (20-30% of dataset)
- [ ] Data quality reviewed (no duplicates, typos)

### 2. Model Training ✅
- [ ] Trained TF-IDF vectorizer (max_features=1000, ngram_range=(1,2))
- [ ] Trained Logistic Regression (C=1.0, max_iter=1000)
- [ ] Macro F1 > 0.85 on test set
- [ ] Per-category F1 > 0.75 (acceptable for Shopping)

### 3. Model Files ✅
- [ ] Saved to `models/` directory
- [ ] File sizes reasonable (<20MB total)
- [ ] Models load without errors

### 4. API Integration ✅
- [ ] FastAPI endpoint created (`/api/nlc/predict`)
- [ ] Request validation (Pydantic schema)
- [ ] Error handling (400, 500 status codes)
- [ ] Response format documented

### 5. Testing ✅
- [ ] Unit tests pass (pytest)
- [ ] Integration tests pass (TestClient)
- [ ] Manual test cases validated
- [ ] Edge cases handled (empty input, very long input)

### 6. Documentation ✅
- [ ] API endpoint documented (OpenAPI/Swagger)
- [ ] Code comments added
- [ ] README updated with usage examples

### 7. Performance ✅
- [ ] Inference time <100ms per request
- [ ] Memory usage <50MB (model + runtime)
- [ ] Can handle 10+ concurrent requests
```

---

## 11. References

### 11.1 Machine Learning

1. **Hosmer, D. W., Lemeshow, S., & Sturdivant, R. X. (2013)**. "Applied Logistic Regression." Wiley, 3rd Edition. ISBN: 978-0470582473

2. **Tsoumakas, G., & Katakis, I. (2007)**. "Multi-label classification: An overview." *International Journal of Data Warehousing and Mining*, 3(3), 1-13. DOI: 10.4018/jdwm.2007070101

### 11.2 Evaluation Metrics

3. **Sokolova, M., & Lapalme, G. (2009)**. "A systematic analysis of performance measures for classification tasks." *Information Processing & Management*, 45(4), 427-437. DOI: 10.1016/j.ipm.2009.03.002

4. **Powers, D. M. (2011)**. "Evaluation: from precision, recall and F-measure to ROC, informedness, markedness and correlation." *Journal of Machine Learning Technologies*, 2(1), 37-63.

### 11.3 Scikit-learn

5. **Pedregosa, F., et al. (2011)**. "Scikit-learn: Machine Learning in Python." *Journal of Machine Learning Research*, 12, 2825-2830.

6. **Scikit-learn MultiOutput Classification**. https://scikit-learn.org/stable/modules/multiclass.html

---

**Document Version**: 1.0  
**Last Updated**: January 2026  
**Author**: WanderWise+ Research Team  
**Module**: I - Natural Language to Category (NLC)  
**File**: `ModuleResearch/Module_I_NLC/04_classification_evaluation.md`  
**Lines**: 500+  
**Previous Document**: `03_tfidf_implementation.md`  
**Module I Status**: ✅ **COMPLETE** (4/4 files)
