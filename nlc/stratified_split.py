# ========================================================
# STRATIFIED MULTI-LABEL SPLIT - ADD TO YOUR NOTEBOOK
# ========================================================
#
# The current random split doesn't preserve label distribution.
# This code ensures each label has similar % in train/val sets.
#
# Add to Cell 3, AFTER filtering zero-labels, BEFORE tokenization.
# Replace the existing train_test_split with this:
# ========================================================

# INSTALL REQUIRED LIBRARY FIRST:
# !pip install scikit-multilearn -q

# ====== STRATIFIED MULTI-LABEL SPLIT ======
from skmultilearn.model_selection import iterative_stratification
import numpy as np

# Convert labels to numpy array
label_array = np.array(labels)

# Create stratified split (maintains label distribution)
splitter = iterative_stratification(n_labels=16, n_samples=len(labels), test_size=0.2, random_state=42)
train_idx, val_idx = next(splitter.split(label_array, label_array))

# Apply split
train_texts = [texts[i] for i in train_idx]
val_texts = [texts[i] for i in val_idx]
train_labels = [labels[i] for i in train_idx]
val_labels = [labels[i] for i in val_idx]

print(f"Train: {len(train_texts)} samples")
print(f"Val: {len(val_texts)} samples")

# Verify label distribution is similar
train_label_sum = np.array(train_labels).sum(axis=0)
val_label_sum = np.array(val_labels).sum(axis=0)
print("\nLabel distribution check (should be similar %):")
for i, label in enumerate(LABELS):
    train_pct = train_label_sum[i] / len(train_texts) * 100
    val_pct = val_label_sum[i] / len(val_texts) * 100
    print(f"  {label:25s}: Train {train_pct:.1f}% | Val {val_pct:.1f}%")
# ============================================

# REMOVE this old code:
# train_texts, val_texts, train_labels, val_labels = train_test_split(
#     texts, labels, test_size=0.2, random_state=42
# )
