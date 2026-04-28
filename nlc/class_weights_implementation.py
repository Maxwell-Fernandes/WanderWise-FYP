# ========================================================
# CLASS WEIGHTS IMPLEMENTATION FOR NLC MODEL
# ========================================================
# 
# Add this code to Cell 4 (Metrics & Model Initialization)
# Insert it AFTER loading the metrics and BEFORE compute_metrics function
#
# Location: After line "accuracy_metric = evaluate.load("accuracy")"
# ========================================================

# ====== STEP 1: Calculate Class Weights ======
# Calculate inverse frequency weights for each label
# Formula: weight = total_samples / (num_classes * count_of_label)

# First, count how many times each label appears
label_counts = np.array([
    sum(1 for item in labels if item[i] == 1) for i in range(len(LABELS))
])

total_samples = len(labels)
num_classes = len(LABELS)

# Calculate class weights (higher weight for rarer labels)
# Example: If nightlife_positive has 657 samples, weight = 4206/(16*657) = 0.40
#          If historical_negative has 285 samples, weight = 4206/(16*285) = 0.92
class_weights = (total_samples / (num_classes * label_counts))

# Normalize weights to have mean = 1 (for stability)
class_weights = class_weights / class_weights.mean()

# Convert to tensor for PyTorch
class_weights_tensor = torch.tensor(class_weights, dtype=torch.float32)

print("===== CLASS WEIGHTS (for handling label imbalance) =====")
for i, label in enumerate(LABELS):
    print(f"  {label:25s}: {class_weights[i]:.3f} (samples: {label_counts[i]})")
print("=" * 60)
# ========================================================

# ====== STEP 2: Create Custom Trainer with Weighted Loss ======
# Add this BEFORE the model initialization (around line 330 in your notebook)

class WeightedLossTrainer(Trainer):
    """
    Custom Trainer that applies class weights to the loss function
    for multi-label classification with imbalanced labels.
    """
    def __init__(self, class_weights=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights
        
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        
        # Apply class weights to BCE loss
        # pos_weight shapes the weights for each class
        if self.class_weights is not None:
            pos_weight = self.class_weights.to(logits.device)
            loss_fct = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight)
        else:
            loss_fct = torch.nn.BCEWithLogitsLoss()
            
        loss = loss_fct(logits, labels)
        return (loss, outputs) if return_outputs else loss


# ====== STEP 3: Replace Trainer initialization ======
# Find this section in your notebook (around line 365):
#     trainer = Trainer(
#         model=model,
#         ...
#     )

# REPLACE it with:

trainer = WeightedLossTrainer(
    class_weights=class_weights_tensor,  # Add this parameter
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    tokenizer=tokenizer,
    data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
    compute_metrics=compute_metrics
)

# ========================================================
# SUMMARY OF CHANGES
# ========================================================
# 
# 1. After loading metrics (line ~273), add class weights calculation
# 2. Create WeightedLossTrainer class before Trainer initialization
# 3. Replace "Trainer(" with "WeightedLossTrainer(class_weights=class_weights_tensor,"
#
# This will make the model pay MORE attention to underrepresented classes
# like historical_negative and shopping_negative during training.
# ========================================================
