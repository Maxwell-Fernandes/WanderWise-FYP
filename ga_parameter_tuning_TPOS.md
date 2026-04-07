# Genetic Algorithm Parameter Tuning — TPOS (Travel Planning Optimization System)
> Based on: *"Travel Planning Optimization System Employing Genetic Algorithms with Multiple Parameters"*  
> Rusu & Alexandrescu, ICSTCC 2024, Gheorghe Asachi Technical University of Iași

---

## 1. Core GA Parameters

| Parameter | Value | Notes |
|---|---|---|
| Population size | 100 chromosomes | Fixed initial population per day |
| Max generations | 50 (tested) | Also stops on fitness plateau |
| Chromosome length (initial) | 6 genes | Trimmed dynamically based on available time |
| Day start time | 09:00 AM | Used for trimming |
| Day end/trim time | ~04:00 PM | Chromosome trimmed to fit this window |

---

## 2. Genetic Operators

### Selection
- **Method:** Tournament Selection
- Two random individuals compete; the fitter one becomes a parent.

### Crossover
- **Method:** Single-point crossover (adapted for variable-length chromosomes)
- **Probability:** `0.7`
- Crossover point chosen within the **minimum length** of both parents
- Duplicate genes are rejected post-crossover (no location revisits)

### Mutation
- **Method:** Swap Mutation (randomly swaps two genes in a chromosome)
- **Probability:** `0.2`
- Maintains chromosome structure while introducing diversity

### Elitism
- The best solution found is preserved across generations.

---

## 3. Fitness Function

Fitness is computed as:

```
fitness = 1 / (1 + Δ)
```

Where **Δ** is the sum of all penalties. Higher fitness = better solution.

### Penalty Components

#### a) User Preference Penalty
```
penalty(L) = (100 - percentage(L)) × 10
```
- `percentage(L)` = user-assigned interest level (0–100) for location type L
- Applied per location in the chromosome

#### b) Distance Penalty (applied per consecutive pair)
```
penalty(L1) = walking_distance(L1, L2) × 10000
```
- Distance computed via **Haversine formula** (great-circle distance)
- Applied to every consecutive gene pair except the last

#### c) Hard Violation Penalty
- **Value:** `10,000` per gene
- Triggers when:
  - Location is closed on the visited day/hour
  - Visit duration exceeds remaining open hours

#### d) Must-See Location Penalty
- Compares `α` (must-see locations included so far) vs `β` (unvisited must-see / days remaining)
- Day 1: penalizes if included count < β
- Subsequent days: α and β are updated based on visited locations and days left
- Penalty scales with the gap: `(β - α) × 1000`

#### e) Restaurant Placement Penalty
- Penalizes solutions that do not contain **exactly 2 restaurants**
- Penalizes if restaurants are not positioned correctly (lunch ≈ middle, dinner ≈ end)

---

## 4. Population Initialization Strategy

This is a key tuning area — the quality of the initial population significantly affects convergence speed.

### Location Scoring (avoids popularity bias)
```
score(L) = user_ratings_total(L) / max_reviews
```
- `max_reviews` = highest review count among all locations **in the same category**
- Ensures fair probability across location types (museums, parks, etc.)

### Restaurant Pre-insertion
- Restaurants are **not** randomly placed; they are inserted after chromosome generation:
  - **Lunch restaurant:** placed in the middle, position chosen to minimize distance to neighbors
  - **Dinner restaurant:** placed at the end, minimizing distance from last location
- This gives the initial population a head start on the restaurant constraint

---

## 5. Stop Conditions

The algorithm halts when **either** condition is met:

1. Fixed number of iterations reached (50 in experiments)
2. No significant fitness improvement over the last N iterations (plateau detection)

---

## 6. Multi-Day Execution Strategy

- GA runs **independently for each day**
- After each day, visited locations are **removed** from the available pool
- This reduces the search space progressively but maintains solution quality
- Later days take slightly longer to converge due to smaller location pools

### Trip Date Handling
| User Input | Algorithm Behavior |
|---|---|
| Start + end dates given | GA runs for each calendar day |
| Only duration given | GA runs for all 7 possible start days (Mon–Sun); best fitness start day selected; first future matching date used |

---

## 7. Visit Duration by Location Type

Predefined visit times used during chromosome trimming:

| Location Type | Visit Duration (minutes) |
|---|---|
| Museum | 120 |
| Park | 60 |
| Shopping Mall | 120 |
| Zoo | 180 |
| Restaurant (lunch/dinner) | Scheduled, not trimmed |

---

## 8. Caching

- **Redis** is used to cache:
  - Fitness values of already-evaluated chromosomes
  - Google Places API responses (with time-based invalidation)
- Avoids redundant API calls and fitness recalculations

---

## 9. Experimental Setup Summary

| Setting | Value |
|---|---|
| Test city | Paris, France (+ others) |
| Trip length tested | 4 days |
| Algorithm runs per test | 100 (for statistical robustness) |
| Must-see attractions weight | 38% |
| Museums weight | 81% |
| Parks weight | 79% |
| Other location types | 0% |
| Generations tracked | 50 |

---

## 10. Known Limitations & Future Work

- Distance uses **Haversine (straight-line)** approximation, not actual road/transit distance
- Google Maps API (with transport mode + time-of-day) would be more accurate but has query limits
- Future enhancements suggested:
  - Crowd levels at specific times
  - Weather at visited locations
  - Real-time traffic / transport mode recommendations
  - Distributed island genetic algorithm variant
