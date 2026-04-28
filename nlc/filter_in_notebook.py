# ========================================================
# FILTER ZERO-LABEL SAMPLES - ADD TO YOUR NOTEBOOK
# ========================================================
# 
# Add this code to Cell 3 (Data Loading Section)
# AFTER loading the data, BEFORE the train_test_split
#
# Find this section in your notebook:
#     texts, labels = load_and_process_data(MOUNT_PATH, DATA_FILE)
#
# Then add the filter code AFTER it:
# ========================================================

# Add AFTER: texts, labels = load_and_process_data(MOUNT_PATH, DATA_FILE)

# ====== FILTER ZERO-LABEL SAMPLES ======
print(f"Before filtering: {len(texts)} samples")

# Filter out samples with no active labels
filtered_texts = []
filtered_labels = []

LABELS_ORDER = [
    'adventure_negative', 'adventure_positive', 'beaches_negative', 'beaches_positive',
    'food_negative', 'food_positive', 'historical_negative', 'historical_positive',
    'nature_negative', 'nature_positive', 'nightlife_negative', 'nightlife_positive',
    'religious_negative', 'religious_positive', 'shopping_negative', 'shopping_positive'
]

for text, label in zip(texts, labels):
    # Check if any label is 1
    if sum(label) > 0:
        filtered_texts.append(text)
        filtered_labels.append(label)
    else:
        print(f"  Removing: {text[:50]}...")

# Replace original data
texts = filtered_texts
labels = filtered_labels

print(f"After filtering: {len(texts)} samples")
print(f"Removed {4206 - len(texts)} zero-label samples")
# ========================================================

# Continue with existing code:
# train_texts, val_texts, train_labels, val_labels = train_test_split(...)
