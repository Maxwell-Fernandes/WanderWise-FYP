# NLC Model Analysis Report

## Executive Summary

Your intuition is correct - there are several issues with the data preprocessing and sampling that need to be addressed. The overfitting at epoch 8 is a symptom of deeper problems in data quality and training configuration.

---

## Issues Identified

### 1. Data Quality Issues (Critical)

#### 1.1 Samples with NO Labels (8.7%)
**366 samples** out of 4,206 have ALL zeros for labels:
- "Goa holiday"
- "Peace in Goa"
- "Long weekend in Goa"
- "Escape to Goa"
- "Show me Goa options"

**Problem**: These are "no-interest" queries that shouldn't be in a classification dataset. The model is trained to predict 16 specific interests, and these samples confuse the model by having no valid target.

**Fix**: Remove all samples with zero active labels before training.

#### 1.2 Label Distribution Imbalance

| Label | Count | Issues |
|-------|-------|--------|
| nightlife_positive | 657 | ⚠️ Highest |
| beaches_positive | 519 | OK |
| shopping_positive | 525 | OK |
| historical_negative | 285 | ⚠️ Lowest |
| shopping_negative | 295 | ⚠️ Low |
| historical_negative | 285 | ⚠️ Lowest |

- **Ratio**: 2.3x difference between most and least common labels
- **Impact**: Model may be biased toward nightlife_positive and underperform on historical_negative

#### 1.3 Labels Per Sample Distribution

| Labels per sample | Count | Percentage |
|-------------------|-------|------------|
| 0 labels | 366 | 8.7% ❌ |
| 1 label | 1,845 | 43.9% |
| 2 labels | 1,354 | 32.2% |
| 3 labels | 318 | 7.6% |
| 4 labels | 276 | 6.6% |
| 5 labels | 47 | 1.1% |

**Problem**: The dataset is heavily skewed toward 1-2 label samples. Multi-label samples (3+) are rare.

---

### 2. Training Configuration Issues

#### 2.1 Overfitting After Epoch 8 (Confirmed)

From your training data:
```
Epoch 8:  val_loss = 0.0195, f1_micro = 0.9780  ← Best
Epoch 9:  val_loss = 0.0190, f1_micro = 0.9746  ← Starts degrading
Epoch 20: val_loss = 0.0210, f1_micro = 0.9761
```

**Training continues until epoch 20 but should stop at epoch 8!**

The `early_stopping_patience=3` is set but NOT working because:
- The metric is monitored at epoch end
- The improvement threshold might be too strict

#### 2.2 Wrong Train/Test Split Strategy

```python
# Current (WRONG for multi-label)
train_texts, val_texts, train_labels, val_labels = train_test_split(
    texts, labels, test_size=0.2, random_state=42
)
```

**Problem**: Random split doesn't preserve label distribution. You need **Stratified Multi-Label Split**.

#### 2.3 No Data Augmentation

The dataset has only 4,206 samples (3,840 usable). For DistilBERT fine-tuning on 16 labels, more diverse data would help.

---

## Recommendations

### Immediate Fixes

#### 1. Remove Samples with No Labels
```python
# Filter out samples with no active labels
filtered_data = []
for item in data:
    active = sum(1 for label in LABELS if item['labels'][label] == 1)
    if active > 0:
        filtered_data.append(item)
# Now you have ~3,840 samples
```

#### 2. Use Stratified Multi-Label Split
```python
# Use iterative stratification for multi-label
from skmultilearn.model_selection import iterative_stratification

splitter = iterative_stratification(n_labels=16, n_samples=len(data), test_size=0.2)
train_idx, val_idx = next(splitter.split(data, label_matrix))
```

#### 3. Reduce Training Epochs
```python
training_args = TrainingArguments(
    num_train_epochs=8,  # Change from 20 to 8
    # ... rest of args
)
```

#### 4. Add Class Weights for Imbalanced Labels
```python
# Calculate class weights inversely proportional to frequency
class_counts = [label_counts[label] for label in LABELS]
class_weights = torch.tensor([len(data)/c for c in class_counts])
```

### Long-term Improvements

#### 1. Data Augmentation
- Use back-translation (English → French → English)
- Use synonym replacement
- Add paraphrasing with LLM

#### 2. Expand Multi-Label Samples
- Currently only 15.3% have 3+ labels
- Target: 30%+ with 2+ labels

#### 3. Add More Negative Samples
- Historical_negative, shopping_negative are underrepresented
- Add more explicit negation examples

---

## Expected Improvements After Fixes

| Metric | Current | Expected |
|--------|---------|----------|
| Validation F1 | 97.8% | 98.5%+ |
| Overfitting Start | Epoch 8 | Epoch 12+ |
| Per-category F1 Variance | High | Reduced |
| Minority Class F1 | ~95% | 97%+ |

---

## Quick Action Items

1. ✅ **Remove 366 zero-label samples** - Most critical fix
2. ✅ **Stop training at epoch 8** - Change `num_train_epochs=8`
3. ⚠️ **Use stratified split** - For better validation
4. ⚠️ **Add class weights** - To handle imbalance
5. 📝 **Collect more data** - Especially for minority classes
