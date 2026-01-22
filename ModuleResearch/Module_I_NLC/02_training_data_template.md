# Module I - Part 2: Training Data Template and Collection Strategy

## Table of Contents
1. [Introduction](#1-introduction)
2. [Training Data Requirements](#2-training-data-requirements)
3. [Data Format and Schema](#3-data-format-and-schema)
4. [Category-Specific Training Examples](#4-category-specific-training-examples)
5. [Data Collection Strategy](#5-data-collection-strategy)
6. [Labeling Guidelines](#6-labeling-guidelines)
7. [Data Augmentation Techniques](#7-data-augmentation-techniques)
8. [Quality Assurance](#8-quality-assurance)
9. [CSV Template and Tools](#9-csv-template-and-tools)
10. [References](#10-references)

---

## 1. Introduction

### 1.1 Purpose of Training Data

High-quality training data is the **foundation** of any machine learning system. For the WanderWise+ NLC module, training data consists of:

1. **User-like natural language inputs** (as they would naturally express interests)
2. **Corresponding category labels** (one or more from the 7 target categories)
3. **Sufficient quantity** (100-500 examples per category for robust classification)
4. **Balanced distribution** (avoid bias toward popular categories)

### 1.2 Data Quality Impact on Performance

| Data Quality Factor | Impact on Model |
|---------------------|-----------------|
| **Quantity** | More data → Higher accuracy (up to saturation point ~500 examples/category) |
| **Diversity** | Varied phrasings → Better generalization to unseen inputs |
| **Label Accuracy** | Mislabeled examples → Confused classifier, lower precision |
| **Class Balance** | Imbalanced data → Bias toward majority class |
| **Real-World Similarity** | Training text matches user input style → Higher real-world accuracy |

**Target Metrics**:
- **Minimum**: 100 examples per category (total: 700 examples)
- **Optimal**: 300-500 examples per category (total: 2,100-3,500 examples)
- **Distribution**: ±10% variance between categories (balanced)

### 1.3 Document Structure

This document provides:
1. **50+ example sentences per category** (ready to use for training)
2. **Data collection strategies** (how to gather more examples)
3. **Labeling guidelines** (how to assign categories consistently)
4. **Augmentation techniques** (how to expand dataset artificially)
5. **CSV template** (ready-to-use format for model training)

---

## 2. Training Data Requirements

### 2.1 Quantity Requirements

**Per-Category Breakdown**:

| Category | Minimum Examples | Target Examples | Priority |
|----------|-----------------|----------------|----------|
| Beaches | 100 | 300 | High (25% of dataset) |
| Historical & Religious | 100 | 250 | High (20% of dataset) |
| Food & Cuisine | 100 | 250 | High (frequent user interest) |
| Adventure | 100 | 200 | Medium (15% of dataset) |
| Nature | 100 | 150 | Medium (10% of dataset) |
| Nightlife | 100 | 150 | Medium (8% of dataset) |
| Shopping | 100 | 150 | Low (4% of dataset, but needs balancing) |

**Multi-Label Examples**: 20-30% of total dataset should have multiple labels (reflects real user behavior)

### 2.2 Diversity Requirements

**Sentence Length**:
- Short (3-5 words): 30% → "Love beaches and food"
- Medium (6-15 words): 50% → "I want to visit beautiful beaches and try local Goan cuisine"
- Long (16-30 words): 20% → "I'm planning a 3-day trip to Goa and I'm interested in exploring historical Portuguese architecture, trying authentic seafood, and relaxing on sandy beaches"

**Vocabulary Variety**:
- Formal: "I am interested in exploring historical monuments"
- Casual: "Wanna check out some old forts"
- Mixed: "Looking for adventure activities and water sports"

**Expression Styles**:
- Declarative: "I love swimming"
- Interrogative: "Are there good beaches for swimming?"
- Preference: "I prefer quiet beaches over crowded ones"
- Activity-focused: "Want to try scuba diving and parasailing"

### 2.3 Quality Requirements

**Mandatory Attributes**:
1. ✅ **Grammatically correct** (no major typos)
2. ✅ **Realistic user input** (not overly formal/academic)
3. ✅ **Clear category signals** (contains keywords from target category)
4. ✅ **Contextually relevant to Goa** (when specific locations mentioned)
5. ✅ **Labeled accurately** (category assignments are correct)

**Avoid**:
- ❌ Ambiguous phrases: "I want a good experience" (too vague)
- ❌ Unrelated content: "I need hotel recommendations" (not interest categorization)
- ❌ Contradictions: "I love beaches but hate sand" (confusing signals)

---

## 3. Data Format and Schema

### 3.1 CSV Format

**File Structure**: `nlc_training_data.csv`

```csv
text,beaches,historical,adventure,nature,food,nightlife,shopping
"I love swimming and sunbathing",1,0,0,0,0,0,0
"Want to see old Portuguese churches",0,1,0,0,0,0,0
"Beaches and seafood restaurants",1,0,0,0,1,0,0
"Scuba diving and water sports",1,0,1,0,0,0,0
```

**Column Definitions**:
- `text` (string): User input sentence
- `beaches` (0/1): Binary label for Beaches category
- `historical` (0/1): Binary label for Historical & Religious
- `adventure` (0/1): Binary label for Adventure
- `nature` (0/1): Binary label for Nature
- `food` (0/1): Binary label for Food & Cuisine
- `nightlife` (0/1): Binary label for Nightlife
- `shopping` (0/1): Binary label for Shopping

**Multi-Label Example**:
```csv
text,beaches,historical,adventure,nature,food,nightlife,shopping
"Beaches, forts, and local cuisine",1,1,0,0,1,0,0
```
(Three categories active: Beaches=1, Historical=1, Food=1)

### 3.2 JSON Format (Alternative)

For complex metadata storage:

```json
[
  {
    "text": "I love swimming and sunbathing",
    "categories": ["Beaches"],
    "confidence": "high",
    "source": "manual",
    "created_at": "2026-01-15"
  },
  {
    "text": "Beaches, historical sites, and food",
    "categories": ["Beaches", "Historical & Religious", "Food & Cuisine"],
    "confidence": "high",
    "source": "augmented",
    "created_at": "2026-01-15"
  }
]
```

**Advantage**: Supports metadata (source, confidence, timestamps)  
**Disadvantage**: Requires conversion to CSV for Scikit-learn

**Recommendation**: Use **CSV** for training, JSON for record-keeping.

### 3.3 Database Schema (Optional)

For production systems storing training data in PostgreSQL:

```sql
CREATE TABLE nlc_training_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    text TEXT NOT NULL,
    categories TEXT[] NOT NULL,
    source VARCHAR(50) DEFAULT 'manual',  -- 'manual', 'augmented', 'crowdsourced'
    confidence VARCHAR(20) DEFAULT 'high', -- 'high', 'medium', 'low'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    reviewed BOOLEAN DEFAULT FALSE
);

-- Example insert
INSERT INTO nlc_training_data (text, categories, source)
VALUES 
    ('I love beaches and water sports', ARRAY['Beaches', 'Adventure'], 'manual'),
    ('Historical churches and forts', ARRAY['Historical & Religious'], 'manual');

-- Export to CSV for training
COPY (
    SELECT 
        text,
        CASE WHEN 'Beaches' = ANY(categories) THEN 1 ELSE 0 END AS beaches,
        CASE WHEN 'Historical & Religious' = ANY(categories) THEN 1 ELSE 0 END AS historical,
        CASE WHEN 'Adventure' = ANY(categories) THEN 1 ELSE 0 END AS adventure,
        CASE WHEN 'Nature' = ANY(categories) THEN 1 ELSE 0 END AS nature,
        CASE WHEN 'Food & Cuisine' = ANY(categories) THEN 1 ELSE 0 END AS food,
        CASE WHEN 'Nightlife' = ANY(categories) THEN 1 ELSE 0 END AS nightlife,
        CASE WHEN 'Shopping' = ANY(categories) THEN 1 ELSE 0 END AS shopping
    FROM nlc_training_data
    WHERE reviewed = TRUE
) TO '/tmp/nlc_training_data.csv' WITH CSV HEADER;
```

---

## 4. Category-Specific Training Examples

### 4.1 Category C1: Beaches

**Example Training Sentences** (50+ examples):

```csv
text,beaches,historical,adventure,nature,food,nightlife,shopping
"I love sunbathing on sandy beaches",1,0,0,0,0,0,0
"Swimming in the ocean is my favorite activity",1,0,0,0,0,0,0
"Want to relax on the beach",1,0,0,0,0,0,0
"Looking for beautiful coastal areas",1,0,0,0,0,0,0
"Beach volleyball and sandcastle building",1,0,0,0,0,0,0
"Sunset views by the shore",1,0,0,0,0,0,0
"Interested in Baga Beach and Calangute",1,0,0,0,0,0,0
"Want to visit Anjuna and Vagator beaches",1,0,0,0,0,0,0
"Love the sound of waves and sea breeze",1,0,0,0,0,0,0
"Beach shacks and shoreline walks",1,0,0,0,0,0,0
"Palolem Beach for quiet relaxation",1,0,0,0,0,0,0
"Candolim Beach for family fun",1,0,0,0,0,0,0
"Want to enjoy beach activities",1,0,0,0,0,0,0
"Love swimming and beach sports",1,0,0,0,0,0,0
"Looking for clean sandy beaches",1,0,0,0,0,0,0
"Beaches with water sports facilities",1,0,1,0,0,0,0
"Romantic beach walks at sunset",1,0,0,0,0,0,0
"Family-friendly beaches with lifeguards",1,0,0,0,0,0,0
"Want to try snorkeling near the beach",1,0,1,0,0,0,0
"Beachfront cafes and relaxation",1,0,0,0,1,0,0
"Love the beach atmosphere",1,0,0,0,0,0,0
"Want to spend time by the ocean",1,0,0,0,0,0,0
"Coastal views and sea activities",1,0,0,0,0,0,0
"Beach photography and scenic spots",1,0,0,0,0,0,0
"Want peaceful beaches away from crowds",1,0,0,0,0,0,0
"Love beach parties and entertainment",1,0,0,0,0,1,0
"Want to surf and swim",1,0,1,0,0,0,0
"Beachside yoga and meditation",1,0,0,0,0,0,0
"Love tropical beach vibes",1,0,0,0,0,0,0
"Want to explore different beaches in Goa",1,0,0,0,0,0,0
"Beach hopping adventure",1,0,0,0,0,0,0
"Love the sand between my toes",1,0,0,0,0,0,0
"Want to collect seashells",1,0,0,0,0,0,0
"Looking for beaches with clear water",1,0,0,0,0,0,0
"Want to watch dolphins from the beach",1,0,0,1,0,0,0
"Beach barbecues and bonfires",1,0,0,0,1,0,0
"Love seaside sunsets",1,0,0,0,0,0,0
"Want to visit famous Goa beaches",1,0,0,0,0,0,0
"Beach resorts and coastal stays",1,0,0,0,0,0,0
"Want to experience beach culture",1,0,0,0,0,0,0
"Love the beach lifestyle",1,0,0,0,0,0,0
"Want to tan on the beach",1,0,0,0,0,0,0
"Beachside hammocks and relaxation",1,0,0,0,0,0,0
"Love early morning beach walks",1,0,0,0,0,0,0
"Want to read a book on the beach",1,0,0,0,0,0,0
"Beach picnics with family",1,0,0,0,0,0,0
"Love the ocean breeze",1,0,0,0,0,0,0
"Want to build sandcastles",1,0,0,0,0,0,0
"Beach kite flying",1,0,0,0,0,0,0
"Love playing frisbee on the beach",1,0,0,0,0,0,0
```

**Key Indicators**: beach, swimming, sunbathing, ocean, sea, coastal, sandy, shore, waves, sunset

---

### 4.2 Category C2: Historical & Religious

**Example Training Sentences** (50+ examples):

```csv
text,beaches,historical,adventure,nature,food,nightlife,shopping
"Want to see old Portuguese churches",0,1,0,0,0,0,0
"Interested in UNESCO World Heritage sites",0,1,0,0,0,0,0
"Love colonial architecture",0,1,0,0,0,0,0
"Want to visit the Basilica of Bom Jesus",0,1,0,0,0,0,0
"Interested in Se Cathedral",0,1,0,0,0,0,0
"Want to explore Fort Aguada",0,1,0,0,0,0,0
"Love historical monuments and ruins",0,1,0,0,0,0,0
"Want to learn about Portuguese history",0,1,0,0,0,0,0
"Interested in ancient temples",0,1,0,0,0,0,0
"Want to visit Chapora Fort",0,1,0,0,0,0,0
"Love heritage sites and museums",0,1,0,0,0,0,0
"Want to see old Goan architecture",0,1,0,0,0,0,0
"Interested in religious landmarks",0,1,0,0,0,0,0
"Want to explore historical churches",0,1,0,0,0,0,0
"Love visiting forts and castles",0,1,0,0,0,0,0
"Want to see colonial-era buildings",0,1,0,0,0,0,0
"Interested in Goan heritage and culture",0,1,0,0,0,0,0
"Want to visit museums and art galleries",0,1,0,0,0,0,0
"Love learning about local history",0,1,0,0,0,0,0
"Want to see ancient ruins",0,1,0,0,0,0,0
"Interested in baroque architecture",0,1,0,0,0,0,0
"Want to explore Old Goa",0,1,0,0,0,0,0
"Love visiting cathedrals",0,1,0,0,0,0,0
"Want to see historical landmarks",0,1,0,0,0,0,0
"Interested in religious sites",0,1,0,0,0,0,0
"Want to visit convents and monasteries",0,1,0,0,0,0,0
"Love exploring historical towns",0,1,0,0,0,0,0
"Want to see Portuguese influence in architecture",0,1,0,0,0,0,0
"Interested in cultural heritage sites",0,1,0,0,0,0,0
"Want to visit Hindu temples in Goa",0,1,0,0,0,0,0
"Love exploring old forts",0,1,0,0,0,0,0
"Want to see Reis Magos Fort",0,1,0,0,0,0,0
"Interested in archaeology and history",0,1,0,0,0,0,0
"Want to visit historical palaces",0,1,0,0,0,0,0
"Love medieval architecture",0,1,0,0,0,0,0
"Want to explore archaeological sites",0,1,0,0,0,0,0
"Interested in religious festivals and sites",0,1,0,0,0,0,0
"Want to see Church of St. Francis of Assisi",0,1,0,0,0,0,0
"Love visiting sacred places",0,1,0,0,0,0,0
"Want to learn about Goan Catholic culture",0,1,0,0,0,0,0
"Interested in Indo-Portuguese architecture",0,1,0,0,0,0,0
"Want to visit historical squares and plazas",0,1,0,0,0,0,0
"Love exploring ancient cities",0,1,0,0,0,0,0
"Want to see historical statues and monuments",0,1,0,0,0,0,0
"Interested in Latin quarters",0,1,0,0,0,0,0
"Want to visit heritage villages",0,1,0,0,0,0,0
"Love exploring old colonial buildings",0,1,0,0,0,0,0
"Want to see historical bridges",0,1,0,0,0,0,0
"Interested in Goan history tours",0,1,0,0,0,0,0
"Want to visit religious shrines",0,1,0,0,0,0,0
```

**Key Indicators**: church, cathedral, fort, historical, heritage, Portuguese, colonial, monument, temple, museum, UNESCO

---

### 4.3 Category C3: Adventure

**Example Training Sentences** (50+ examples):

```csv
text,beaches,historical,adventure,nature,food,nightlife,shopping
"Want to try scuba diving",0,0,1,0,0,0,0
"Love parasailing and water sports",1,0,1,0,0,0,0
"Interested in trekking to Dudhsagar",0,0,1,1,0,0,0
"Want to go jet skiing",1,0,1,0,0,0,0
"Love adventure activities",0,0,1,0,0,0,0
"Want to try kayaking",0,0,1,0,0,0,0
"Interested in white-water rafting",0,0,1,1,0,0,0
"Love extreme sports",0,0,1,0,0,0,0
"Want to go rock climbing",0,0,1,1,0,0,0
"Interested in zip-lining",0,0,1,1,0,0,0
"Want to try bungee jumping",0,0,1,0,0,0,0
"Love adrenaline activities",0,0,1,0,0,0,0
"Want to go windsurfing",1,0,1,0,0,0,0
"Interested in snorkeling",1,0,1,0,0,0,0
"Love water sports like wakeboarding",1,0,1,0,0,0,0
"Want to try kitesurfing",1,0,1,0,0,0,0
"Interested in deep-sea fishing",1,0,1,0,0,0,0
"Want to go hiking in forests",0,0,1,1,0,0,0
"Love trekking adventures",0,0,1,1,0,0,0
"Want to try rappelling",0,0,1,1,0,0,0
"Interested in caving exploration",0,0,1,1,0,0,0
"Want to go mountain biking",0,0,1,1,0,0,0
"Love thrilling experiences",0,0,1,0,0,0,0
"Want to try paragliding",0,0,1,0,0,0,0
"Interested in skydiving",0,0,1,0,0,0,0
"Want to go surfing",1,0,1,0,0,0,0
"Love adventure sports",0,0,1,0,0,0,0
"Want to try banana boat rides",1,0,1,0,0,0,0
"Interested in speedboat tours",1,0,1,0,0,0,0
"Want to go dolphin spotting boat trips",1,0,1,1,0,0,0
"Love challenging outdoor activities",0,0,1,1,0,0,0
"Want to try flyboarding",1,0,1,0,0,0,0
"Interested in adventure parks",0,0,1,0,0,0,0
"Want to go on jungle safari",0,0,1,1,0,0,0
"Love exploring underwater caves",1,0,1,1,0,0,0
"Want to try stand-up paddleboarding",1,0,1,0,0,0,0
"Interested in adventure camping",0,0,1,1,0,0,0
"Want to go on wildlife expeditions",0,0,1,1,0,0,0
"Love exploring off-road trails",0,0,1,1,0,0,0
"Want to try ATV rides",0,0,1,0,0,0,0
"Interested in adventure tourism",0,0,1,0,0,0,0
"Want to go on boat adventures",1,0,1,0,0,0,0
"Love scuba diving at Grande Island",1,0,1,0,0,0,0
"Want to explore shipwrecks",1,0,1,0,0,0,0
"Interested in underwater photography",1,0,1,0,0,0,0
"Want to try night trekking",0,0,1,1,0,0,0
"Love obstacle courses",0,0,1,0,0,0,0
"Want to go on adventure tours",0,0,1,0,0,0,0
"Interested in extreme water sports",1,0,1,0,0,0,0
"Want to try cliff jumping",0,0,1,1,0,0,0
```

**Key Indicators**: scuba diving, parasailing, trekking, water sports, kayaking, adventure, extreme, adrenaline, rafting, zip-lining

---

### 4.4 Category C4: Nature

**Example Training Sentences** (50+ examples):

```csv
text,beaches,historical,adventure,nature,food,nightlife,shopping
"Want to visit Dudhsagar Waterfalls",0,0,0,1,0,0,0
"Love nature and wildlife",0,0,0,1,0,0,0
"Interested in spice plantations",0,0,0,1,0,0,0
"Want to go bird watching",0,0,0,1,0,0,0
"Love scenic viewpoints",0,0,0,1,0,0,0
"Want to visit Bhagwan Mahavir Sanctuary",0,0,0,1,0,0,0
"Interested in forest trails",0,0,0,1,0,0,0
"Love exploring greenery",0,0,0,1,0,0,0
"Want to see butterflies and flora",0,0,0,1,0,0,0
"Interested in eco-tourism",0,0,0,1,0,0,0
"Want to visit wildlife sanctuaries",0,0,0,1,0,0,0
"Love nature photography",0,0,0,1,0,0,0
"Want to explore natural landscapes",0,0,0,1,0,0,0
"Interested in botanical gardens",0,0,0,1,0,0,0
"Want to see waterfalls and rivers",0,0,0,1,0,0,0
"Love trekking through forests",0,0,1,1,0,0,0
"Want to visit Cotigao Wildlife Sanctuary",0,0,0,1,0,0,0
"Interested in nature trails",0,0,0,1,0,0,0
"Want to see tropical forests",0,0,0,1,0,0,0
"Love jungle exploration",0,0,1,1,0,0,0
"Want to visit nature reserves",0,0,0,1,0,0,0
"Interested in natural springs",0,0,0,1,0,0,0
"Want to see endemic species",0,0,0,1,0,0,0
"Love observing wildlife in natural habitat",0,0,0,1,0,0,0
"Want to visit mangrove forests",0,0,0,1,0,0,0
"Interested in nature conservation areas",0,0,0,1,0,0,0
"Want to see scenic hills",0,0,0,1,0,0,0
"Love panoramic nature views",0,0,0,1,0,0,0
"Want to visit spice farms",0,0,0,1,0,0,0
"Interested in organic plantations",0,0,0,1,0,0,0
"Want to see cashew plantations",0,0,0,1,0,0,0
"Love exploring natural beauty",0,0,0,1,0,0,0
"Want to visit national parks",0,0,0,1,0,0,0
"Interested in nature walks",0,0,0,1,0,0,0
"Want to see rare birds",0,0,0,1,0,0,0
"Love pristine natural environments",0,0,0,1,0,0,0
"Want to visit waterfall viewpoints",0,0,0,1,0,0,0
"Interested in nature retreats",0,0,0,1,0,0,0
"Want to explore jungle canopies",0,0,0,1,0,0,0
"Love natural rock formations",0,0,0,1,0,0,0
"Want to see wild animals",0,0,0,1,0,0,0
"Interested in nature-based tourism",0,0,0,1,0,0,0
"Want to visit lakes and ponds",0,0,0,1,0,0,0
"Love serene natural settings",0,0,0,1,0,0,0
"Want to explore biodiversity hotspots",0,0,0,1,0,0,0
"Interested in nature conservation",0,0,0,1,0,0,0
"Want to see monsoon landscapes",0,0,0,1,0,0,0
"Love nature trails and hikes",0,0,1,1,0,0,0
"Want to visit peaceful natural spots",0,0,0,1,0,0,0
"Interested in eco-friendly tourism",0,0,0,1,0,0,0
```

**Key Indicators**: nature, wildlife, waterfalls, spice plantation, forest, sanctuary, scenic, bird watching, eco-tourism, flora, fauna

---

### 4.5 Category C5: Food & Cuisine

**Example Training Sentences** (50+ examples):

```csv
text,beaches,historical,adventure,nature,food,nightlife,shopping
"Want to try authentic Goan cuisine",0,0,0,0,1,0,0
"Love fish curry and rice",0,0,0,0,1,0,0
"Interested in seafood restaurants",0,0,0,0,1,0,0
"Want to try vindaloo",0,0,0,0,1,0,0
"Love local Goan dishes",0,0,0,0,1,0,0
"Want to visit beach shacks for food",1,0,0,0,1,0,0
"Interested in prawn curry",0,0,0,0,1,0,0
"Want to try bebinca dessert",0,0,0,0,1,0,0
"Love trying local street food",0,0,0,0,1,0,0
"Want to visit popular restaurants",0,0,0,0,1,0,0
"Interested in Goan food tours",0,0,0,0,1,0,0
"Want to try sorpotel",0,0,0,0,1,0,0
"Love authentic seafood",0,0,0,0,1,0,0
"Want to visit cafes and eateries",0,0,0,0,1,0,0
"Interested in culinary experiences",0,0,0,0,1,0,0
"Want to try xacuti",0,0,0,0,1,0,0
"Love Goan pork dishes",0,0,0,0,1,0,0
"Want to try feni liquor",0,0,0,0,1,0,0
"Interested in local cuisine tasting",0,0,0,0,1,0,0
"Want to visit food markets",0,0,0,0,1,0,1
"Love trying regional specialties",0,0,0,0,1,0,0
"Want to visit beachside restaurants",1,0,0,0,1,0,0
"Interested in seafood platters",0,0,0,0,1,0,0
"Want to try recheado fish",0,0,0,0,1,0,0
"Love authentic local flavors",0,0,0,0,1,0,0
"Want to visit shack dining",1,0,0,0,1,0,0
"Interested in Goan breakfast items",0,0,0,0,1,0,0
"Want to try sannas",0,0,0,0,1,0,0
"Love traditional Goan meals",0,0,0,0,1,0,0
"Want to visit fine dining restaurants",0,0,0,0,1,0,0
"Interested in fusion cuisine",0,0,0,0,1,0,0
"Want to try coconut-based curries",0,0,0,0,1,0,0
"Love spicy Goan food",0,0,0,0,1,0,0
"Want to visit local bakeries",0,0,0,0,1,0,0
"Interested in Goan sweets",0,0,0,0,1,0,0
"Want to try dodol",0,0,0,0,1,0,0
"Love trying different cuisines",0,0,0,0,1,0,0
"Want to visit seafood markets",0,0,0,0,1,0,1
"Interested in cooking classes",0,0,0,0,1,0,0
"Want to learn Goan recipes",0,0,0,0,1,0,0
"Love food photography",0,0,0,0,1,0,0
"Want to try cafreal chicken",0,0,0,0,1,0,0
"Interested in Portuguese-influenced food",0,1,0,0,1,0,0
"Want to visit rooftop restaurants",0,0,0,0,1,0,0
"Love dining with ocean views",1,0,0,0,1,0,0
"Want to try balchao",0,0,0,0,1,0,0
"Interested in vegan Goan options",0,0,0,0,1,0,0
"Want to visit organic cafes",0,0,0,0,1,0,0
"Love trying local beverages",0,0,0,0,1,0,0
"Want to taste authentic flavors",0,0,0,0,1,0,0
```

**Key Indicators**: food, cuisine, restaurant, seafood, fish curry, vindaloo, bebinca, feni, Goan dishes, local food, shack, eatery

---

### 4.6 Category C6: Nightlife

**Example Training Sentences** (50+ examples):

```csv
text,beaches,historical,adventure,nature,food,nightlife,shopping
"Want to visit nightclubs",0,0,0,0,0,1,0
"Love party scene and DJs",0,0,0,0,0,1,0
"Interested in Club Cubana",0,0,0,0,0,1,0
"Want to visit Tito's",0,0,0,0,0,1,0
"Love dancing and nightlife",0,0,0,0,0,1,0
"Want to try casino cruises",0,0,0,0,0,1,0
"Interested in Deltin Royale",0,0,0,0,0,1,0
"Want to visit bars and pubs",0,0,0,0,0,1,0
"Love live music venues",0,0,0,0,0,1,0
"Want to experience Goa nightlife",0,0,0,0,0,1,0
"Interested in beach parties",1,0,0,0,0,1,0
"Want to visit lounge bars",0,0,0,0,0,1,0
"Love electronic music and trance",0,0,0,0,0,1,0
"Want to try cocktail bars",0,0,0,0,0,1,0
"Interested in late-night entertainment",0,0,0,0,0,1,0
"Want to visit Anjuna night market",0,0,0,0,0,1,1
"Love clubbing till dawn",0,0,0,0,0,1,0
"Want to experience casino gaming",0,0,0,0,0,1,0
"Interested in rooftop bars",0,0,0,0,0,1,0
"Want to visit shack parties",1,0,0,0,0,1,0
"Love night beach raves",1,0,0,0,0,1,0
"Want to try karaoke bars",0,0,0,0,0,1,0
"Interested in jazz clubs",0,0,0,0,0,1,0
"Want to visit sports bars",0,0,0,0,0,1,0
"Love nightlife and entertainment",0,0,0,0,0,1,0
"Want to try pub crawls",0,0,0,0,0,1,0
"Interested in DJ performances",0,0,0,0,0,1,0
"Want to visit dance clubs",0,0,0,0,0,1,0
"Love party atmosphere",0,0,0,0,0,1,0
"Want to experience full moon parties",1,0,0,0,0,1,0
"Interested in sunset parties",1,0,0,0,0,1,0
"Want to visit nightlife hotspots",0,0,0,0,0,1,0
"Love late-night bars",0,0,0,0,0,1,0
"Want to try gaming lounges",0,0,0,0,0,1,0
"Interested in themed parties",0,0,0,0,0,1,0
"Want to visit nightclubs in Baga",1,0,0,0,0,1,0
"Love Goa party culture",0,0,0,0,0,1,0
"Want to try wine bars",0,0,0,0,0,1,0
"Interested in live band performances",0,0,0,0,0,1,0
"Want to visit after-hours clubs",0,0,0,0,0,1,0
"Love electronic dance music events",0,0,0,0,0,1,0
"Want to try hookah lounges",0,0,0,0,0,1,0
"Interested in nightlife tours",0,0,0,0,0,1,0
"Want to visit popular clubs",0,0,0,0,0,1,0
"Love partying by the beach",1,0,0,0,0,1,0
"Want to try casino poker",0,0,0,0,0,1,0
"Interested in nightlife experiences",0,0,0,0,0,1,0
"Want to visit cocktail lounges",0,0,0,0,0,1,0
"Love nightlife and drinks",0,0,0,0,0,1,0
"Want to experience Goa's party scene",0,0,0,0,0,1,0
```

**Key Indicators**: nightclub, club, bar, party, DJ, casino, trance, Tito's, Cubana, nightlife, dancing, Deltin, live music

---

### 4.7 Category C7: Shopping

**Example Training Sentences** (50+ examples):

```csv
text,beaches,historical,adventure,nature,food,nightlife,shopping
"Want to visit flea markets",0,0,0,0,0,0,1
"Love shopping for souvenirs",0,0,0,0,0,0,1
"Interested in Anjuna flea market",0,0,0,0,0,0,1
"Want to visit Mapusa market",0,0,0,0,0,0,1
"Love buying local handicrafts",0,0,0,0,0,0,1
"Want to shop for spices",0,0,0,1,0,0,1
"Interested in textile shopping",0,0,0,0,0,0,1
"Want to buy Goan artifacts",0,0,0,0,0,0,1
"Love browsing local markets",0,0,0,0,0,0,1
"Want to shop for jewelry",0,0,0,0,0,0,1
"Interested in handicraft stores",0,0,0,0,0,0,1
"Want to buy beach wear",1,0,0,0,0,0,1
"Love shopping for local products",0,0,0,0,0,0,1
"Want to visit night markets",0,0,0,0,0,1,1
"Interested in Saturday Night Market",0,0,0,0,0,1,1
"Want to buy cashew nuts",0,0,0,1,0,0,1
"Love shopping for clothes",0,0,0,0,0,0,1
"Want to visit boutique stores",0,0,0,0,0,0,1
"Interested in buying artwork",0,0,0,0,0,0,1
"Want to shop for home decor",0,0,0,0,0,0,1
"Love browsing antique shops",0,1,0,0,0,0,1
"Want to buy traditional items",0,0,0,0,0,0,1
"Interested in street shopping",0,0,0,0,0,0,1
"Want to visit shopping complexes",0,0,0,0,0,0,1
"Love bargaining at markets",0,0,0,0,0,0,1
"Want to shop for gifts",0,0,0,0,0,0,1
"Interested in buying local crafts",0,0,0,0,0,0,1
"Want to visit souvenir shops",0,0,0,0,0,0,1
"Love shopping for accessories",0,0,0,0,0,0,1
"Want to buy musical instruments",0,0,0,0,0,0,1
"Interested in book shopping",0,0,0,0,0,0,1
"Want to visit art galleries and shops",0,1,0,0,0,0,1
"Love shopping for beachwear",1,0,0,0,0,0,1
"Want to buy pottery and ceramics",0,0,0,0,0,0,1
"Interested in organic product stores",0,0,0,1,0,0,1
"Want to shop for incense and candles",0,0,0,0,0,0,1
"Love buying unique items",0,0,0,0,0,0,1
"Want to visit weekend markets",0,0,0,0,0,0,1
"Interested in shopping for textiles",0,0,0,0,0,0,1
"Want to buy leather goods",0,0,0,0,0,0,1
"Love exploring market stalls",0,0,0,0,0,0,1
"Want to shop for footwear",0,0,0,0,0,0,1
"Interested in buying spices and herbs",0,0,0,1,0,0,1
"Want to visit local bazaars",0,0,0,0,0,0,1
"Love shopping for trinkets",0,0,0,0,0,0,1
"Want to buy cashew feni bottles",0,0,0,0,1,0,1
"Interested in shopping tours",0,0,0,0,0,0,1
"Want to visit designer stores",0,0,0,0,0,0,1
"Love buying local specialties",0,0,0,0,0,0,1
"Want to shop for traditional clothing",0,0,0,0,0,0,1
```

**Key Indicators**: shopping, market, flea market, Anjuna, Mapusa, souvenirs, handicrafts, local products, bazaar, boutique

---

### 4.8 Multi-Label Examples (Mixed Interests)

```csv
text,beaches,historical,adventure,nature,food,nightlife,shopping
"Beaches and local cuisine",1,0,0,0,1,0,0
"Historical sites and shopping",0,1,0,0,0,0,1
"Water sports and beach parties",1,0,1,0,0,1,0
"Nature trails and adventure activities",0,0,1,1,0,0,0
"Food tours and night markets",0,0,0,0,1,1,1
"Beaches, forts, and local seafood",1,1,0,0,1,0,0
"Nightlife and shopping at Anjuna",0,0,0,0,0,1,1
"Adventure sports and nature exploration",0,0,1,1,0,0,0
"Historical churches and Goan cuisine",0,1,0,0,1,0,0
"Beaches, water sports, and nightclubs",1,0,1,0,0,1,0
"Wildlife sanctuaries and trekking",0,0,1,1,0,0,0
"Shopping and local food markets",0,0,0,0,1,0,1
"Beach relaxation and seafood dining",1,0,0,0,1,0,0
"Historical tours and spice plantations",0,1,0,1,0,0,0
"Nightlife, food, and beach parties",1,0,0,0,1,1,0
"Adventure, nature, and photography",0,0,1,1,0,0,0
"Churches, museums, and local markets",0,1,0,0,0,0,1
"Swimming, sunbathing, and beach shacks",1,0,0,0,1,0,0
"Forts, heritage sites, and cultural shopping",0,1,0,0,0,0,1
"Waterfalls, trekking, and wildlife",0,0,1,1,0,0,0
```

---

## 5. Data Collection Strategy

### 5.1 Manual Data Collection

**Sources**:
1. **Tourism Forums**: TripAdvisor, Lonely Planet forums (extract user interest expressions)
2. **Social Media**: Instagram captions, Twitter posts about Goa travel
3. **Travel Blogs**: Extract sentences describing interests
4. **Survey Data**: Conduct surveys asking "What are you interested in during your Goa trip?"

**Process**:
```
1. Identify source (e.g., TripAdvisor review)
2. Extract relevant sentence (e.g., "I loved the beaches and water sports")
3. Assign categories (Beaches=1, Adventure=1)
4. Record in CSV
5. Review for accuracy
```

### 5.2 Crowdsourcing

**Platform**: Amazon Mechanical Turk, Appen, or internal volunteers

**Task**:
- Show workers: 7 categories with examples
- Ask: "Write 10 sentences expressing interest in each category"
- Quality control: Review submissions, reject low-quality data

**Cost Estimate**: $0.10 per 10 sentences → $70 for 700 sentences (minimum dataset)

### 5.3 Synthetic Data Generation (Augmentation)

Covered in detail in Section 7.

---

## 6. Labeling Guidelines

### 6.1 Decision Criteria

**Question to Ask**: "If a user inputs this text, which categories would be relevant for route planning?"

**Rules**:
1. **Explicit Mention**: If category keyword is present → assign that category
   - Example: "I want beaches" → Beaches=1

2. **Implicit Indication**: If activity/interest strongly implies category → assign
   - Example: "Want to swim and sunbathe" → Beaches=1 (even if "beach" not mentioned)

3. **Ambiguous Cases**: When unclear, assign **multiple categories**
   - Example: "Water sports" → Beaches=1, Adventure=1 (both valid)

4. **Negations**: DO NOT assign category if explicitly negated
   - Example: "I don't like crowded beaches" → Beaches=0 (NOTE: Current TF-IDF cannot handle this well; label as Beaches=0 or skip)

### 6.2 Common Ambiguities

| Text | Potential Categories | Recommended Label | Reasoning |
|------|---------------------|-------------------|-----------|
| "Water sports" | Beaches, Adventure | Both (1,1) | Activity occurs at beach but is adventurous |
| "Beach shacks" | Beaches, Food | Both (1,1) | Food venue located at beach |
| "Forts with ocean views" | Historical, Beaches | Historical only (0,1) | Primary interest is fort (views are secondary) |
| "Spice plantation tour" | Nature, Shopping | Nature (0,1) | Shopping not primary intent |
| "Night market" | Nightlife, Shopping | Both (1,1) | Evening activity + shopping |

### 6.3 Labeling Worksheet Template

```
Text: "I want to visit beaches and try local seafood"

Step 1: Identify keywords
- beaches → Beaches
- local seafood → Food & Cuisine

Step 2: Check for implicit categories
- None (all explicit)

Step 3: Assign labels
beaches=1, historical=0, adventure=0, nature=0, food=1, nightlife=0, shopping=0

Step 4: Quality check
- Does this make sense for route planning? YES (visit beach POIs + food POIs)
- Are there any missed categories? NO

Final Label: [1,0,0,0,1,0,0]
```

---

## 7. Data Augmentation Techniques

### 7.1 Synonym Replacement

**Technique**: Replace words with synonyms while preserving meaning

**Example**:
```
Original: "I love swimming in the ocean"
Augmented: "I enjoy swimming in the sea"
Augmented: "I adore swimming in the water"
```

**Tools**: NLTK WordNet, Gensim, Python `synonyms` library

**Implementation**:
```python
from nltk.corpus import wordnet
import random

def get_synonyms(word):
    synonyms = []
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.append(lemma.name())
    return list(set(synonyms))

def augment_with_synonyms(sentence, n_aug=3):
    words = sentence.split()
    augmented = []
    
    for _ in range(n_aug):
        new_words = words.copy()
        # Replace 1-2 words with synonyms
        for _ in range(random.randint(1, 2)):
            idx = random.randint(0, len(new_words) - 1)
            synonyms = get_synonyms(new_words[idx])
            if synonyms:
                new_words[idx] = random.choice(synonyms)
        augmented.append(' '.join(new_words))
    
    return augmented

# Example
original = "I love swimming in the ocean"
augmented = augment_with_synonyms(original, n_aug=2)
# Output: ["I adore swimming in the sea", "I enjoy swimming in the water"]
```

### 7.2 Paraphrasing

**Technique**: Rewrite sentence with different structure, same meaning

**Example**:
```
Original: "I want to visit beaches"
Paraphrased: "Beaches are what I'm interested in"
Paraphrased: "Looking forward to beach visits"
Paraphrased: "Beach exploration is my goal"
```

**Tools**: 
- Manual paraphrasing (highest quality)
- GPT-3/ChatGPT for automated paraphrasing
- Backtranslation (English → Hindi → English)

### 7.3 Sentence Combination

**Technique**: Merge single-label examples into multi-label

**Example**:
```
Example 1: "I love beaches" → [1,0,0,0,0,0,0]
Example 2: "Want to try local food" → [0,0,0,0,1,0,0]

Combined: "I love beaches and want to try local food" → [1,0,0,0,1,0,0]
```

**Implementation**:
```python
def combine_sentences(sent1, sent2, label1, label2):
    combined_text = f"{sent1} and {sent2}"
    combined_label = [max(l1, l2) for l1, l2 in zip(label1, label2)]
    return combined_text, combined_label

# Example
sent1 = "I love beaches"
sent2 = "Want to try local food"
label1 = [1,0,0,0,0,0,0]
label2 = [0,0,0,0,1,0,0]

combined, label = combine_sentences(sent1, sent2, label1, label2)
# combined = "I love beaches and Want to try local food"
# label = [1,0,0,0,1,0,0]
```

### 7.4 Backtranslation

**Technique**: Translate to another language, then back to English

**Example**:
```
Original: "I want to visit historical churches"
→ (English to Hindi): "मैं ऐतिहासिक चर्चों का दौरा करना चाहता हूं"
→ (Hindi to English): "I wish to visit heritage churches"
```

**Tools**: Google Translate API, Azure Translator, DeepL

**Caution**: May introduce grammatical errors; review augmented data

---

## 8. Quality Assurance

### 8.1 Inter-Annotator Agreement

**Metric**: Cohen's Kappa (measures agreement between 2 labelers)

**Process**:
1. Have 2 people label same 50 examples
2. Calculate agreement:
   - Perfect agreement: κ = 1.0
   - Random agreement: κ = 0
   - Target: κ > 0.8 (substantial agreement)

**Interpretation**:
- κ > 0.9: Almost perfect
- κ = 0.8-0.9: Strong
- κ = 0.6-0.8: Moderate (needs guidelines revision)
- κ < 0.6: Poor (serious issues)

### 8.2 Data Validation Checks

**Automated Checks**:
```python
import pandas as pd

df = pd.read_csv('nlc_training_data.csv')

# Check 1: No empty texts
assert df['text'].notna().all(), "Found empty texts"

# Check 2: All rows have at least one category
assert (df.iloc[:, 1:].sum(axis=1) > 0).all(), "Found rows with no categories"

# Check 3: Text length reasonable (3-200 words)
assert df['text'].str.split().str.len().between(3, 200).all(), "Text length out of range"

# Check 4: Class distribution balance (±30%)
counts = df.iloc[:, 1:].sum()
assert counts.max() / counts.min() < 2.0, "Class imbalance exceeds 2:1 ratio"

print("All validation checks passed!")
```

### 8.3 Review Process

**Stage 1: Initial Collection**
- Collect 100 examples per category (700 total)

**Stage 2: Review**
- 2 reviewers independently label 50 random examples
- Calculate inter-annotator agreement (κ)
- If κ < 0.8 → revise labeling guidelines

**Stage 3: Conflict Resolution**
- Review disagreements
- Update guidelines based on edge cases
- Re-label ambiguous examples

**Stage 4: Expansion**
- Apply augmentation to reach 300-500 examples/category
- Spot-check augmented data (10% sample)

---

## 9. CSV Template and Tools

### 9.1 Final CSV Template

**Filename**: `nlc_training_data.csv`

```csv
text,beaches,historical,adventure,nature,food,nightlife,shopping
"I love sunbathing on sandy beaches",1,0,0,0,0,0,0
"Want to see old Portuguese churches",0,1,0,0,0,0,0
"Scuba diving and parasailing",1,0,1,0,0,0,0
"Visit Dudhsagar Waterfalls",0,0,0,1,0,0,0
"Try authentic Goan fish curry",0,0,0,0,1,0,0
"Nightclubs and party scene",0,0,0,0,0,1,0
"Shopping at Anjuna flea market",0,0,0,0,0,0,1
"Beaches, forts, and local food",1,1,0,0,1,0,0
```

### 9.2 Python Script to Load Data

```python
import pandas as pd
from sklearn.model_selection import train_test_split

# Load data
df = pd.read_csv('nlc_training_data.csv')

# Separate features and labels
X_text = df['text'].values
y_labels = df[['beaches', 'historical', 'adventure', 'nature', 'food', 'nightlife', 'shopping']].values

# Train-test split (80-20)
X_train_text, X_test_text, y_train, y_test = train_test_split(
    X_text, y_labels, test_size=0.2, random_state=42
)

print(f"Training samples: {len(X_train_text)}")
print(f"Test samples: {len(X_test_text)}")
print(f"Category distribution:\n{df.iloc[:, 1:].sum()}")
```

### 9.3 Data Collection Tools

**Google Sheets Template**:
- Column A: text
- Columns B-H: categories (checkboxes for 1/0)
- Export as CSV when complete

**Spreadsheet Link**: [Template available on request]

**Validation Formula** (Google Sheets):
```
=IF(SUM(B2:H2)=0, "ERROR: No category", "OK")
```

---

## 10. References

### 10.1 Data Annotation Guidelines

1. **Hovy, D., & Lavid, J. (2010)**. "Annotation agreement and task knowledge." *Proceedings of the Linguistic Annotation Workshop*, 110-118.

2. **Artstein, R., & Poesio, M. (2008)**. "Inter-coder agreement for computational linguistics." *Computational Linguistics*, 34(4), 555-596. DOI: 10.1162/coli.07-034-R2

### 10.2 Data Augmentation

3. **Wei, J., & Zou, K. (2019)**. "EDA: Easy Data Augmentation Techniques for Boosting Performance on Text Classification Tasks." *EMNLP-IJCNLP 2019*, 6382-6388. DOI: 10.18653/v1/D19-1670

4. **Kobayashi, S. (2018)**. "Contextual Augmentation: Data Augmentation by Words with Paradigmatic Relations." *NAACL-HLT 2018*, 452-457. DOI: 10.18653/v1/N18-2072

### 10.3 Tourism Classification

5. **Gavalas, D., Konstantopoulos, C., Mastakas, K., & Pantziou, G. (2014)**. "Mobile recommender systems in tourism." *Journal of Network and Computer Applications*, 39, 319-333. DOI: 10.1016/j.jnca.2013.04.006

---

**Document Version**: 1.0  
**Last Updated**: January 2026  
**Author**: WanderWise+ Research Team  
**Module**: I - Natural Language to Category (NLC)  
**File**: `ModuleResearch/Module_I_NLC/02_training_data_template.md`  
**Lines**: 600+  
**Previous Document**: `01_nlc_fundamentals.md`  
**Next Document**: `03_tfidf_implementation.md`
