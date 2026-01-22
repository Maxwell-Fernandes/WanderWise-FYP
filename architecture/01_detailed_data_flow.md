# WanderWise+ System Architecture & Data Flow

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Module Architecture](#2-module-architecture)
3. [Detailed Data Flow](#3-detailed-data-flow)
4. [Database Schema](#4-database-schema)
5. [API Endpoints](#5-api-endpoints)
6. [Technology Stack](#6-technology-stack)
7. [Deployment Architecture](#7-deployment-architecture)

---

## 1. System Overview

### 1.1 What is WanderWise+?

WanderWise+ is an AI-powered intelligent tourism recommendation system for Goa, India. It provides personalized, optimized multi-day trip itineraries based on user interests, preferences, and constraints.

### 1.2 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           WANDERWISE+ SYSTEM                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         FRONTEND (React 19+)                         │   │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌────────────────────┐  │   │
│  │  │ Interest  │ │  Trip     │ │  Itinerary│ │      Map           │  │   │
│  │  │  Input    │ │  Config   │ │  Display  │ │    Visualization  │  │   │
│  │  └───────────┘ └───────────┘ └───────────┘ └────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      BACKEND API (FastAPI)                           │   │
│  │  ┌───────────────┐ ┌───────────────┐ ┌──────────────────────────┐  │   │
│  │  │   /api/nlc    │ │ /api/cluster  │ │     /api/route/optimize  │  │   │
│  │  │   (Module I)  │ │  (Module III) │ │       (Module IV)        │  │   │
│  │  └───────────────┘ └───────────────┘ └──────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     GENETIC ALGORITHM (Module IV)                    │   │
│  │  ┌───────────────┐ ┌───────────────┐ ┌──────────────────────────┐  │   │
│  │  │   Selection   │ │   Crossover   │ │      Mutation +          │  │   │
│  │  │   (Tournament)│ │   (COX)       │ │      Fitness Eval        │  │   │
│  │  └───────────────┘ └───────────────┘ └──────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    POPULARITY SERVICE (Module II)                    │   │
│  │  ┌───────────────┐ ┌───────────────┐ ┌──────────────────────────┐  │   │
│  │  │  Review       │ │  Engagement   │ │  Temporal + Geographic   │  │   │
│  │  │  Scoring      │ │  Scoring      │ │      Component           │  │   │
│  │  └───────────────┘ └───────────────┘ └──────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                   CLUSTERING SERVICE (Module III)                    │   │
│  │  ┌───────────────┐ ┌───────────────┐ ┌──────────────────────────┐  │   │
│  │  │ K-means++     │ │  Haversine    │ │  Edge Case               │  │   │
│  │  │ Initialization│ │  Distance     │ │  Handling                │  │   │
│  │  └───────────────┘ └───────────────┘ └──────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      POSTGRESQL + POSTGIS                            │   │
│  │  ┌───────────────┐ ┌───────────────┐ ┌──────────────────────────┐  │   │
│  │  │   goa_places  │ │ distance_matrix│ │    user_trips           │  │   │
│  │  └───────────────┘ └───────────────┘ └──────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Module Architecture

### 2.1 Module I: Natural Language Classifier (NLC)

**Purpose**: Transform user text input into structured interest categories

```
┌─────────────────────────────────────────────────────────────────┐
│                    MODULE I: NLC CLASSIFIER                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  INPUT: "I want beaches and historical sites for 5 days"       │
│         │                                                       │
│         ▼                                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    PRE-PROCESSING                          │  │
│  │  • Lowercase conversion                                    │  │
│  │  • Remove punctuation                                       │  │
│  │  • Tokenization                                            │  │
│  │  • Stop word removal                                       │  │
│  │  • Lemmatization                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│         │                                                       │
│         ▼                                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    TF-IDF VECTORIZATION                    │  │
│  │  Input: Preprocessed text                                  │  │
│  │  Output: Vector of TF-IDF scores (vocabulary size: 5000)  │  │
│  └───────────────────────────────────────────────────────────┘  │
│         │                                                       │
│         ▼                                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              LOGISTIC REGRESSION CLASSIFIER                │  │
│  │  Multi-label classification with sigmoid outputs           │  │
│  │  Categories:                                               │  │
│  │  • beaches (0.92)                                          │  │
│  │  • historical (0.85)                                       │  │
│  │  • nature (0.31)                                           │  │
│  │  • adventure (0.18)                                        │  │
│  │  • dining (0.45)                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│         │                                                       │
│         ▼                                                       │
│  OUTPUT: {"beaches": 0.92, "historical": 0.85, "dining": 0.45}  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Module II: POI Popularity Scoring

**Purpose**: Calculate comprehensive popularity scores for fitness function

```
┌─────────────────────────────────────────────────────────────────┐
│               MODULE II: POPULARITY SCORING (WPI)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  WPI Formula:                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ WPI = α×Review + β×Engagement + γ×Temporal + δ×Geographic│   │
│  │     (0.35)        (0.25)          (0.25)       (0.15)    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  INPUT: POI ID, temporal context, review data                   │
│         │                                                       │
│         ▼                                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    REVIEW COMPONENT (35%)                  │  │
│  │  • Google Maps ratings (45% weight)                        │  │
│  │  • TripAdvisor ratings (35% weight)                        │  │
│  │  • Booking.com ratings (15% weight)                        │  │
│  │  • Sentiment analysis (5% weight)                          │  │
│  └───────────────────────────────────────────────────────────┘  │
│         │                                                       │
│         ▼                                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   ENGAGEMENT COMPONENT (25%)               │  │
│  │  • Photo uploads count                                     │  │
│  │  • Social media mentions                                   │  │
│  │  • Search trend velocity                                   │  │
│  │  • Content shares/reposts                                  │  │
│  └───────────────────────────────────────────────────────────┘  │
│         │                                                       │
│         ▼                                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   TEMPORAL COMPONENT (25%)                 │  │
│  │  • Seasonal popularity factors                             │  │
│  │  • Day-of-week patterns                                    │  │
│  │  • Time-of-day preferences                                 │  │
│  │  • Event impacts                                           │  │
│  └───────────────────────────────────────────────────────────┘  │
│         │                                                       │
│         ▼                                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                  GEOGRAPHIC COMPONENT (15%)                │  │
│  │  • Regional popularity index                               │  │
│  │  • Accessibility score                                     │  │
│  │  • Diversity contribution                                  │  │
│  └───────────────────────────────────────────────────────────┘  │
│         │                                                       │
│         ▼                                                       │
│  OUTPUT: WPI Score (0-100)                                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 Module III: Geographic Clustering (K-Means)

**Purpose**: Group POIs into daily clusters for multi-day tours

```
┌─────────────────────────────────────────────────────────────────┐
│               MODULE III: GEOGRAPHIC CLUSTERING                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  INPUT: 50 POIs, K = 5 (trip duration)                          │
│         │                                                       │
│         ▼                                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │               K-MEANS++ INITIALIZATION                      │  │
│  │  Step 1: Select 1st centroid randomly                      │  │
│  │  Step 2-N: Select with probability ∝ D(x)²                 │  │
│  │  (D(x) = distance to nearest existing centroid)            │  │
│  └───────────────────────────────────────────────────────────┘  │
│         │                                                       │
│         ▼                                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                    ITERATIVE LOOP                          │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │           ASSIGNMENT STEP                            │  │  │
│  │  │  For each POI:                                       │  │  │
│  │  │    Assign to cluster with nearest centroid            │  │  │
│  │  │    Using Haversine distance formula                   │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                         │                                  │  │
│  │                         ▼                                  │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │            UPDATE STEP                               │  │  │
│  │  │  For each cluster:                                   │  │  │
│  │  │    centroid = mean(lat, lon) of assigned POIs        │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  │                         │                                  │  │
│  │                         ▼                                  │  │
│  │  Check convergence (WCSS improvement < 1e-4) or            │  │
│  │  max iterations reached (100)                              │  │
│  └───────────────────────────────────────────────────────────┘  │
│         │                                                       │
│         ▼                                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   EDGE CASE HANDLING                       │  │
│  │  • Rebalance imbalanced clusters (min 6, max 15 POIs)     │  │
│  │  • Handle empty clusters (reinitialize)                    │  │
│  │  • Detect and flag outlier POIs (>30km from center)       │  │
│  └───────────────────────────────────────────────────────────┘  │
│         │                                                       │
│         ▼                                                       │
│  OUTPUT: {day_1: [POIs...], day_2: [POIs...], ...}             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.4 Module IV: Genetic Algorithm Routing

**Purpose**: Optimize daily routes for minimum travel time, maximum popularity

```
┌─────────────────────────────────────────────────────────────────┐
│               MODULE IV: GENETIC ALGORITHM                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  INPUT: Day cluster POIs, WPI scores, distance_matrix           │
│         │                                                       │
│         ▼                                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   POPULATION INITIALIZATION                │  │
│  │  Generate 100 random routes (permutations)                 │  │
│  └───────────────────────────────────────────────────────────┘  │
│         │                                                       │
│         ▼                                                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │               GENERATION LOOP (max 75)                     │  │
│  │  ┌───────────────────────────────────────────────────────┐│  │
│  │  │              TOURNAMENT SELECTION                      ││  │
│  │  │  • Tournament size: 4                                 ││  │
│  │  │  • Select parents based on fitness                    ││  │
│  │  │  • Maintains selection pressure                        ││  │
│  │  └───────────────────────────────────────────────────────┘│  │
│  │                         │                                  │  │
│  │                         ▼                                  │  │
│  │  ┌───────────────────────────────────────────────────────┐│  │
│  │  │               COX CROSSOVER (85%)                     ││  │
│  │  │  Copy Order Crossover:                                 ││  │
│  │  │  1. Copy subsequence from Parent 1                     ││  │
│  │  │  2. Fill remaining from Parent 2 in order              ││  │
│  │  │  Result: 43.89% better than PMX                        ││  │
│  │  └───────────────────────────────────────────────────────┘│  │
│  │                         │                                  │  │
│  │                         ▼                                  │  │
│  │  ┌───────────────────────────────────────────────────────┐│  │
│  │  │               SWAP MUTATION (15%)                     ││  │
│  │  │  Randomly swap two POIs in route                       ││  │
│  │  │  Maintains population diversity                        ││  │
│  │  └───────────────────────────────────────────────────────┘│  │
│  │                         │                                  │  │
│  │                         ▼                                  │  │
│  │  ┌───────────────────────────────────────────────────────┐│  │
│  │  │               FITNESS EVALUATION                      ││  │
│  │  │                                                         ││  │
│  │  │  fitness = w_travel×travel_score                       ││  │
│  │  │         + w_popularity×popularity_score                ││  │
│  │  │         + w_waiting×waiting_score                      ││  │
│  │  │         + w_constraints×constraint_score               ││  │
│  │  │         × diversity_bonus (1.0 + 0.1×diversity)        ││  │
│  │  │                                                         ││  │
│  │  └───────────────────────────────────────────────────────┘│  │
│  │                         │                                  │  │
│  │                         ▼                                  │  │
│  │  ┌───────────────────────────────────────────────────────┐│  │
│  │  │                   ELITISM (2 best)                    ││  │
│  │  │  Preserve top 2 solutions unchanged                    ││  │
│  │  └───────────────────────────────────────────────────────┘│  │
│  └───────────────────────────────────────────────────────────┘  │
│         │                                                       │
│         ▼                                                       │
│  OUTPUT: Optimized daily route with visit order                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Data Flow

### 3.1 End-to-End Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     COMPLETE DATA FLOW DIAGRAM                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  USER INTERFACE LAYER                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ User Input: "I want a relaxing 5-day beach trip with history"       │    │
│  │ Trip Config: duration=5, start_date=2024-12-15, budget=standard     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ POST /api/planning/start-trip                                       │    │
│  │ {user_input, trip_duration_days, start_date, budget}                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ FASTAPI GATEWAY                                                     │    │
│  │ Route to appropriate module endpoint                                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ MODULE I: NLC CLASSIFIER                                            │    │
│  │                                                                     │    │
│  │ Input: "I want a relaxing 5-day beach trip with history"           │    │
│  │                                                                     │    │
│  │ Process: TF-IDF → Logistic Regression                              │    │
│  │                                                                     │    │
│  │ Output: {                                                           │    │
│  │   "beaches": 0.92,                                                  │    │
│  │   "historical": 0.85,                                               │    │
│  │   "nature": 0.31,                                                   │    │
│  │   "adventure": 0.18,                                                │    │
│  │   "dining": 0.45                                                    │    │
│  │ }                                                                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ DATABASE: POI RETRIEVAL                                             │    │
│  │                                                                     │    │
│  │ Query: SELECT * FROM goa_places                                     │    │
│  │       WHERE category IN ('beaches', 'historical', 'dining')        │    │
│  │                                                                     │    │
│  │ Output: [                                                           │    │
│  │   {id, name, lat, lon, category, popularity_score, ...},           │    │
│  │   {id, name, lat, lon, category, popularity_score, ...},           │    │
│  │   ...  // 45-60 POIs                                                │    │
│  │ ]                                                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ MODULE II: POPULARITY SCORING                                       │    │
│  │                                                                     │    │
│  │ For each POI:                                                       │    │
│  │   - Fetch review scores from APIs                                   │    │
│  │   - Calculate engagement metrics                                    │    │
│  │   - Apply temporal factors                                          │    │
│  │   - Compute geographic score                                        │    │
│  │   - WPI = 0.35×review + 0.25×engagement + 0.25×temporal + 0.15×geo  │    │
│  │                                                                     │    │
│  │ Output: {poi_id: wpi_score, ...}                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ MODULE III: GEOGRAPHIC CLUSTERING                                   │    │
│  │                                                                     │    │
│  │ Input:                                                              │    │
│  │   - POIs: [list with WPI scores]                                    │    │
│  │   - K: 5 (trip_duration_days)                                       │    │
│  │                                                                     │    │
│  │ Process: K-means++ initialization → Iterative assignment/update    │    │
│  │   - Haversine distance for geographic accuracy                      │    │
│  │   - Edge case handling (imbalanced, empty, outliers)               │    │
│  │                                                                     │    │
│  │ Output: {                                                           │    │
│  │   "day_1": [POI-1, POI-5, POI-12, ...],  // North Goa              │    │
│  │   "day_2": [POI-3, POI-8, POI-15, ...],  // Central                │    │
│  │   "day_3": [POI-2, POI-9, POI-21, ...],  // North Interior         │    │
│  │   "day_4": [POI-7, POI-11, POI-19, ...],  // South Beaches         │    │
│  │   "day_5": [POI-4, POI-14, POI-23, ...]   // Nature                │    │
│  │ }                                                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ MODULE IV: GENETIC ALGORITHM                                        │    │
│  │                                                                     │    │
│  │ For each day cluster:                                               │    │
│  │   1. Initialize population (100 random routes)                      │    │
│  │   2. For each generation (max 75):                                  │    │
│  │      a. Tournament selection (size=4)                               │    │
│  │      b. COX crossover (85% rate)                                    │    │
│  │      c. Swap mutation (15% rate)                                    │    │
│  │      d. Fitness evaluation:                                         │    │
│  │         fitness =                                                   │    │
│  │           0.25×travel_time_score +                                  │    │
│  │           0.25×popularity_score +                                   │    │
│  │           0.25×waiting_time_score +                                 │    │
│  │           0.25×constraint_score +                                   │    │
│  │           0.10×diversity_bonus                                      │    │
│  │   3. Return best route from final population                        │    │
│  │                                                                     │    │
│  │ Note: Uses distance_matrix table or API for travel times           │    │
│  │                                                                     │    │
│  │ Output: {                                                           │    │
│  │   "day_1": {                                                         │    │
│  │     "route": ["POI-12", "POI-1", "POI-5", "POI-8"],                │    │
│  │     "total_distance_km": 32.5,                                      │    │
│  │     "estimated_duration_hours": 7.2,                                │    │
│  │     "fitness_score": 0.85                                           │    │
│  │   },                                                                │    │
│  │   ...                                                                │    │
│  │ }                                                                    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ RESPONSE ASSEMBLY                                                   │    │
│  │                                                                     │    │
│  │ Combine all module outputs into final itinerary                     │    │
│  │ Add metadata (total distance, hours, warnings)                      │    │
│  │                                                                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ API RESPONSE                                                        │    │
│  │ {                                                                   │    │
│  │   "success": true,                                                  │    │
│  │   "itinerary_id": "uuid-1234",                                      │    │
│  │   "daily_itineraries": [...],                                       │    │
│  │   "total_distance_km": 156.8,                                       │    │
│  │   "estimated_total_hours": 38.5                                     │    │
│  │ }                                                                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │ FRONTEND DISPLAY                                                    │    │
│  │ • Interactive map with route visualization                          │    │
│  │ • Day-by-day itinerary cards                                        │    │
│  │ • POI details with photos and ratings                               │    │
│  │ • Total trip cost and timing estimates                              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Data Flow Between Modules

| From Module | To Module | Data Format | Frequency |
|-------------|-----------|-------------|-----------|
| User Input | Module I | JSON: {"text": "...", "duration": 5} | Per request |
| Module I | Database | Category list | Per request |
| Database | Module III | List of POI objects | Per request |
| Module II | Module IV | Dict: {poi_id: wpi_score} | Per request |
| Module III | Module IV | Dict: {day_num: [POI_ids]} | Per request |
| Module IV | Response | Structured itinerary JSON | Per request |

---

## 4. Database Schema

### 4.1 Core Tables

```sql
-- Main POI table
CREATE TABLE goa_places (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    latitude DECIMAL(9, 6) NOT NULL,
    longitude DECIMAL(9, 6) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    popularity_score DECIMAL(3, 2) DEFAULT 5.0,
    opening_time TIME,
    closing_time TIME,
    avg_visit_duration_minutes INTEGER DEFAULT 60,
    description TEXT,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Precomputed distance matrix
CREATE TABLE distance_matrix (
    poi1_id UUID REFERENCES goa_places(id),
    poi2_id UUID REFERENCES goa_places(id),
    distance_km DECIMAL(10, 2) NOT NULL,
    travel_time_minutes INTEGER,
    PRIMARY KEY (poi1_id, poi2_id)
);

-- User trip sessions
CREATE TABLE user_trips (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID,
    trip_duration_days INTEGER NOT NULL,
    start_date DATE,
    end_date DATE,
    status VARCHAR(50) DEFAULT 'planning',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Generated itineraries
CREATE TABLE itineraries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trip_id UUID REFERENCES user_trips(id),
    day_number INTEGER NOT NULL,
    route_pois UUID[],
    total_distance_km DECIMAL(10, 2),
    estimated_duration_hours DECIMAL(4, 1),
    fitness_score DECIMAL(3, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- NLC training data
CREATE TABLE nlc_training_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    text_input TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    label INTEGER NOT NULL,
    source VARCHAR(50) DEFAULT 'manual'
);
```

---

## 5. API Endpoints

### 5.1 Core Endpoints

| Endpoint | Method | Module | Description |
|----------|--------|--------|-------------|
| `/api/nlc/classify` | POST | I | Classify user interests |
| `/api/clustering/geographic` | POST | III | Cluster POIs by location |
| `/api/route/optimize` | POST | IV | Optimize daily route |
| `/api/places/search` | GET | DB | Search POIs by filters |
| `/api/places/{id}` | GET | DB | Get POI details |
| `/api/itinerary/generate` | POST | ALL | Generate complete itinerary |

### 5.2 Request/Response Examples

```json
// POST /api/itinerary/generate
{
    "user_input": "I want beaches and historical sites for 5 days",
    "trip_duration_days": 5,
    "start_date": "2024-12-15",
    "budget": "standard",
    "style": "balanced"
}

// Response
{
    "success": true,
    "itinerary_id": "uuid-1234",
    "daily_itineraries": [
        {
            "day": 1,
            "theme": "North Goa Beaches",
            "poi_count": 9,
            "route": [
                {"poi_id": "uuid-001", "name": "Baga Beach", "arrival": "09:00"},
                {"poi_id": "uuid-005", "name": "Calangute Beach", "arrival": "11:00"},
                {"poi_id": "uuid-012", "name": "Anjuna Beach", "arrival": "14:00"}
            ],
            "total_distance_km": 15.4,
            "total_hours": 7.5
        }
    ],
    "total_stats": {
        "total_pois": 45,
        "total_distance_km": 156.8,
        "total_hours": 38.5,
        "avg_daily_pois": 9
    }
}
```

---

## 6. Technology Stack

### 6.1 Backend

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | FastAPI | REST API |
| Database | PostgreSQL + PostGIS | Spatial data |
| ORM | SQLAlchemy 2.0 | Database access |
| GA Library | Custom + python-tsp | Route optimization |
| NLP | Scikit-learn (TF-IDF, LogisticRegression) | Text classification |

### 6.2 Frontend

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | React 19 + Vite | UI rendering |
| Routing | React Router 7 | Navigation |
| Styling | TailwindCSS 4 | Styling |
| Maps | Leaflet.js | Route visualization |

### 6.3 Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| Containerization | Docker | Deployment |
| Caching | Redis | API response cache |
| API | OpenRouteService (free tier) | Distance matrix |

---

## 7. Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DEPLOYMENT ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                         LOAD BALANCER (Nginx)                        │   │
│   │                  SSL Termination, Rate Limiting                      │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│              ┌─────────────────────┼─────────────────────┐                  │
│              ▼                     ▼                     ▼                  │
│   ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│   │  Backend Server 1 │  │  Backend Server 2 │  │  Backend Server 3 │          │
│   │  (FastAPI)        │  │  (FastAPI)        │  │  (FastAPI)        │          │
│   │  :8000            │  │  :8000            │  │  :8000            │          │
│   └──────────────────┘  └──────────────────┘  └──────────────────┘          │
│              │                     │                     │                  │
│              └─────────────────────┼─────────────────────┘                  │
│                                    ▼                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                    REDIS CACHE (Optional)                            │   │
│   │              Session storage, API response cache                     │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                         │
│                                    ▼                                         │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                    POSTGRESQL + POSTGIS                              │   │
│   │              goa_places, distance_matrix, user_trips                 │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Summary

This architecture document provides complete visibility into:

1. **Module Responsibilities** - What each module does
2. **Data Flow** - How data moves through the system
3. **Technology Choices** - Why specific technologies were selected
4. **Integration Points** - How modules communicate
5. **Deployment Strategy** - How to deploy in production

All architectural decisions have been validated and documented for implementation.
