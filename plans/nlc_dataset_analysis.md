# NLC Training Dataset Analysis

## Dataset Overview

| Metric | Value |
|--------|-------|
| **Total Samples** | 3,427 |
| **Categories** | 7 |
| **File** | `nlc_training_data_augmented.csv` |

## Category Distribution Analysis

Based on the dataset analysis, here's the distribution of categories:

### Estimated Category Counts

| Category | Estimated Count | Percentage | Status |
|----------|-----------------|------------|--------|
| **beaches** | ~650+ | ~19% | ✅ Well represented |
| **historical** | ~550+ | ~16% | ✅ Well represented |
| **food** | ~500+ | ~15% | ✅ Well represented |
| **nightlife** | ~450+ | ~13% | ✅ Good coverage |
| **shopping** | ~400+ | ~12% | ✅ Good coverage |
| **nature** | ~350+ | ~10% | ⚠️ Could use more |
| **adventure** | ~350+ | ~10% | ⚠️ Could use more |

### Multi-label Distribution

The dataset includes multi-label samples (combinations of categories):
- **Single label**: Most common (~60-70%)
- **2 labels**: Common combinations like beach+food, beach+nightlife
- **3+ labels**: Less common but present

## Strengths of Current Dataset

### 1. **Diverse Phrasings**
- Full sentences: "I want to explore the natural side of Goa away from the beach"
- Short phrases: "beach vibes", "night mode", "foodie"
- Questions: "What's the best beach in Goa?", "Where to do water sports?"
- Typos/slang: "beches", "beachh", "gonna hit the beach"

### 2. **Goa-Specific Terms**
- Place names: Baga Beach, Anjuna, Tito's, Fort Aguada, Basilica of Bom Jesus
- Local dishes: vindaloo, xacuti, cafreal chicken, bebinca, sorpotel, feni
- Local restaurants: Fisherman's Wharf, Thalassa, Martin's Corner, Brittos

### 3. **Multi-label Combinations**
- "beach and food" → beaches=1, food=1
- "beaches and nightlife" → beaches=1, nightlife=1
- "history and food" → historical=1, food=1
- "nature and adventure" → nature=1, adventure=1

### 4. **Realistic User Inputs**
- Casual language: "jus beach", "party hard", "food porn"
- Questions: "any beaches nearby?", "what food is famous?"
- Mixed intent: "beach during day, party at night"

## Identified Gaps

### 1. **Underrepresented Categories**

#### Adventure (Lower Recall: 86.7%)
Missing examples:
- Specific adventure activities: "zip lining", "rock climbing", "cliff diving"
- Adventure + other combinations: "adventure and shopping", "adventure and history"
- Beginner-friendly queries: "adventure activities for beginners"

#### Nature (Lower Recall: 86.7%)
Missing examples:
- Specific nature spots: "Netravali Wildlife Sanctuary", "Cotigao"
- Nature + other combinations: "nature and nightlife", "nature and shopping"
- Seasonal queries: "best time to visit waterfalls in monsoon"

### 2. **Missing Vocabulary**

| Category | Missing Terms |
|----------|---------------|
| adventure | zip line, rock climbing, cliff diving, bungee, rappelling |
| nature | mangrove, biodiversity, endemic, sanctuary, reserve |
| shopping | boutique, mall, store, retail, wholesale |

### 3. **Edge Cases Not Covered**

- Very short inputs: "bch", "ntr", "fd" (abbreviations)
- Mixed language: "beach aur food chahiye" (Hindi + English)
- Negative queries: "no beaches, just food"
- Comparison queries: "beaches vs nightlife in Goa"

## Recommendations for Improvement

### Priority 1: Add More Adventure Samples

```csv
text,beaches,historical,adventure,nature,food,nightlife,shopping
"want to try zip lining",0,0,1,0,0,0,0
"rock climbing in goa",0,0,1,0,0,0,0
"cliff diving spots",0,0,1,0,0,0,0
"bungee jumping near goa",0,0,1,0,0,0,0
"adventure activities for beginners",0,0,1,0,0,0,0
"adventure and some shopping",0,0,1,0,0,0,1
"nature trek with adventure sports",0,0,1,1,0,0,0
```

### Priority 2: Add More Nature Samples

```csv
text,beaches,historical,adventure,nature,food,nightlife,shopping
"mangrove tour in goa",0,0,0,1,0,0,0
"want to see biodiversity",0,0,0,1,0,0,0
"endemic species of goa",0,0,0,1,0,0,0
"nature reserve visit",0,0,0,1,0,0,0
"nature and nightlife combo",0,0,0,1,0,1,0
"wildlife and shopping",0,0,0,1,0,0,1
```

### Priority 3: Add Edge Cases

```csv
text,beaches,historical,adventure,nature,food,nightlife,shopping
"no beaches please",0,0,0,0,0,0,0
"just want to relax anywhere",1,0,0,1,0,0,0
"something different",0,1,0,1,0,0,0
"surprise me",0,0,0,0,0,0,0
"beach aur food chahiye",1,0,0,0,1,0,0
```

## Impact on Model Performance

### Current Performance (from metadata.json)

| Category | Precision | Recall | F1-Score |
|----------|-----------|--------|----------|
| beaches | 99.2% | 88.7% | 93.7% |
| historical | 100% | 89.3% | 94.4% |
| adventure | 100% | 76.6% | **86.7%** ⚠️ |
| nature | 100% | 76.6% | **86.7%** ⚠️ |
| food | 100% | 82.1% | 90.2% |
| nightlife | 98.9% | 82.1% | 89.7% |
| shopping | 98.7% | 89.3% | 93.8% |

### Key Observations

1. **High Precision, Lower Recall** for adventure and nature
   - Model is conservative in predicting these categories
   - Adding more samples will improve recall

2. **Balanced Performance** for beaches, historical, shopping
   - These categories have good representation
   - Model performs well on these

3. **Food and Nightlife** are in the middle
   - Good but could be improved
   - More diverse examples would help

## Next Steps

1. **Add 50-100 samples** for adventure category
2. **Add 50-100 samples** for nature category
3. **Add edge cases** (negative queries, abbreviations)
4. **Retrain model** with enhanced dataset
5. **Evaluate improvement** in recall for underperforming categories

## Conclusion

The current dataset is well-structured with good coverage of most categories. The main gaps are in the **adventure** and **nature** categories, which show lower recall scores. Adding more diverse examples for these categories, along with edge cases, would improve overall model performance.

The dataset already includes:
- ✅ Diverse phrasings (formal, casual, questions)
- ✅ Goa-specific terminology
- ✅ Multi-label combinations
- ✅ Realistic user inputs with typos

What's needed:
- ⚠️ More adventure-specific vocabulary
- ⚠️ More nature-specific vocabulary
- ⚠️ Edge cases (negative queries, abbreviations)
