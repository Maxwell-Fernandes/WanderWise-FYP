# ========================================================
# FILTER ZERO-LABEL SAMPLES FROM DATASET
# ========================================================
# 
# This script removes samples with NO active labels from the dataset.
# These are queries like "Goa holiday", "Peace in Goa" that have all zeros.
#
# Run this BEFORE training to clean your data.
# ========================================================

import json
import os

# Configuration
INPUT_FILE = "nlc/nlc_dataset_new.jsonl"
OUTPUT_FILE = "nlc/nlc_dataset_cleaned.jsonl"

# Labels (in the order they appear in your data)
LABELS = [
    'adventure_negative', 'adventure_positive', 'beaches_negative', 'beaches_positive',
    'food_negative', 'food_positive', 'historical_negative', 'historical_positive',
    'nature_negative', 'nature_positive', 'nightlife_negative', 'nightlife_positive',
    'religious_negative', 'religious_positive', 'shopping_negative', 'shopping_positive'
]

def has_active_labels(labels_dict):
    """Check if any label is set to 1."""
    return any(labels_dict.get(label, 0) == 1 for label in LABELS)

def filter_dataset(input_path, output_path):
    """Filter out samples with no active labels."""
    
    # Load data
    data = []
    with open(input_path, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    
    print(f"Original dataset: {len(data)} samples")
    
    # Filter
    filtered_data = []
    removed_count = 0
    
    for item in data:
        if has_active_labels(item['labels']):
            filtered_data.append(item)
        else:
            removed_count += 1
            print(f"  Removed: {item['text'][:50]}...")
    
    print(f"\nFiltered dataset: {len(filtered_data)} samples")
    print(f"Removed: {removed_count} samples ({removed_count/len(data)*100:.1f}%)")
    
    # Save cleaned data
    with open(output_path, 'w') as f:
        for item in filtered_data:
            f.write(json.dumps(item) + '\n')
    
    print(f"\nSaved cleaned dataset to: {output_path}")
    
    # Show label distribution after filtering
    from collections import Counter
    label_counts = Counter()
    for item in filtered_data:
        for label in LABELS:
            if item['labels'][label] == 1:
                label_counts[label] += 1
    
    print("\n--- New Label Distribution ---")
    for label in LABELS:
        print(f"  {label:25s}: {label_counts[label]}")
    
    return filtered_data

if __name__ == "__main__":
    filter_dataset(INPUT_FILE, OUTPUT_FILE)
