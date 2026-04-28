# Module IV - Part 2: TTDP/OPTW Problem Definition

## Table of Contents
1. [Problem Overview](#problem-overview)
2. [TTDP Mathematical Formulation](#ttdp-mathematical-formulation)
3. [OPTW Extensions](#optw-extensions)
4. [Constraints](#constraints)
5. [Complexity Analysis](#complexity-analysis)
6. [WanderWise Adaptation](#wanderwise-adaptation)

---

## 1. Problem Overview

### 1.1 Tourist Trip Design Problem (TTDP)

**Definition**: Given a set of Points of Interest (POIs) and a tourist with limited time, design an itinerary that maximizes tourist satisfaction while respecting temporal and spatial constraints.

**Formal Statement**:
- **Input**:
  - Set of N POIs: P = {p₁, p₂, ..., pₙ}
  - Travel times: t(pᵢ, pⱼ) between all POI pairs
  - Visit durations: d(pᵢ) for each POI
  - POI values: v(pᵢ) representing attractiveness
  - Time budget: T_max
  - Opening hours: [o(pᵢ), c(pᵢ)] for each POI

- **Output**:
  - Ordered sequence: I = ⟨p_{i₁}, p_{i₂}, ..., p_{iₖ}⟩ where k ≤ N
  - Start time for each POI visit

- **Objective**: Maximize total value while satisfying all constraints

### 1.2 Relationship to Other Problems

**TTDP ⊂ OPTW ⊂ OP ⊂ TSP**

```
TSP (Traveling Salesman)
  └─ OP (Orienteering Problem)
      └─ OPTW (OP with Time Windows)
          └─ TTDP (Tourist-specific variant)
```

| Problem | Visit All POIs? | Time Budget? | POI Values? | Time Windows? |
|---------|----------------|--------------|-------------|---------------|
| **TSP** | ✅ Yes | ❌ No | ❌ No (all equal) | ❌ No |
| **OP** | ❌ No (subset) | ✅ Yes | ✅ Yes | ❌ No |
| **OPTW** | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes |
| **TTDP** | ❌ No | ✅ Yes | ✅ Yes | ✅ Yes + tourism |

---

## 2. TTDP Mathematical Formulation

### 2.1 Variables

- **N**: Total number of POIs
- **P** = {p₁, ..., pₙ}: Set of POIs
- **xᵢⱼ** ∈ {0, 1}: Binary variable (1 if edge i→j in route)
- **sᵢ**: Start time of visit at POI i (decision variable)
- **I** = ⟨p_{i₁}, ..., p_{iₖ}⟩: Itinerary (ordered sequence)

### 2.2 Parameters

- **v(pᵢ)**: Value/score of POI i (e.g., rating × popularity)
- **t(pᵢ, pⱼ)**: Travel time from POI i to j (minutes)
- **d(pᵢ)**: Visit duration at POI i (minutes)
- **[o(pᵢ), c(pᵢ)]**: Opening and closing times of POI i
- **T_max**: Maximum tour duration (minutes)
- **T_start**: Tour start time

### 2.3 Objective Function

**Maximize**:
```
Z = Σ v(pᵢ) × xᵢⱼ  for all i,j
```

Where xᵢⱼ = 1 indicates POI i is visited.

**Alternatively (penalty-based for GA)**:
```
fitness(I) = Σ v(pᵢ) - α × Σ t(pᵢ, pⱼ) - β × penalties(I)
            i∈I         (i,j)∈I
```

### 2.4 Constraints

**C1. Time Budget**:
```
Σ d(pᵢ) + Σ t(pᵢ, pⱼ) ≤ T_max
i∈I       (i,j)∈I
```

**C2. Time Windows** (each POI must be visited during opening hours):
```
o(pᵢ) ≤ sᵢ ≤ c(pᵢ)  ∀ i ∈ I
```

**C3. Visit Duration Respect**:
```
sᵢ + d(pᵢ) + t(pᵢ, pⱼ) ≤ sⱼ  ∀ consecutive (i,j) ∈ I
```

**C4. Each POI Visited At Most Once**:
```
Σ xᵢⱼ ≤ 1  ∀ i
j
```

**C5. Route Continuity**:
```
Σ xᵢₖ = Σ xₖⱼ  ∀ k (flow conservation)
i       j
```

---

## 3. OPTW Extensions

### 3.1 Orienteering Problem with Time Windows

OPTW adds:
- **Profit collection**: Each POI has a score
- **Time windows**: Must visit during [earliest, latest]
- **Selective visiting**: Don't need to visit all POIs

**Key Difference from TTDP**:
- OPTW: General framework
- TTDP: Tourism-specific (lunch breaks, day divisions, tourist preferences)

### 3.2 Multi-Day TTDP

**Extension for multi-day tours**:
- K days with budget T_max^(d) for day d
- Overnight accommodation (hotel location)
- Inter-day travel constraints

**Formulation**:
```
For each day d = 1..K:
  I_d = itinerary for day d
  Σ d(pᵢ) + Σ t(pᵢ,pⱼ) ≤ T_max^(d)
  i∈I_d     (i,j)∈I_d
  
Constraint: P = I_1 ∪ I_2 ∪ ... ∪ I_K (partition POIs across days)
```

---

## 4. Constraints

### 4.1 Hard vs Soft Constraints

**Hard Constraints** (must satisfy):
- Time budget (daily max duration)
- Each POI visited once
- Route continuity

**Soft Constraints** (penalized if violated):
- Opening hours (penalty if closed)
- Lunch time (penalty if invaded)
- Travel distance minimization

### 4.2 Tourism-Specific Constraints

**Lunch Break Constraint**:
```
∀ i ∈ I: NOT (sᵢ ≤ 12:00 AND sᵢ + d(pᵢ) ≥ 13:30)
```
Or apply penalty if lunch time (12:00-13:30) is invaded.

**Daily Fatigue Constraint**:
```
Number of POIs per day ≤ POI_max (e.g., 7-8 POIs)
```

**Geographic Clustering** (handled by Module III):
```
For multi-day tours: POIs should be geographically grouped by day
```

---

## 5. Complexity Analysis

### 5.1 NP-Hardness Proof

**TTDP is NP-hard** (reduction from TSP):

1. TSP is NP-hard
2. TTDP ⊇ TSP (TSP is special case with no constraints)
3. Therefore, TTDP is NP-hard

**Implication**: No polynomial-time exact algorithm exists (unless P=NP).

### 5.2 Search Space Size

For N POIs:
- **Total permutations**: N!
- **Valid routes** (subset of k POIs): N!/(N-k)!

**Example** (10 POIs, visit 6):
```
Search space = 10!/(10-6)! = 10!/4! = 151,200 possible routes
```

For 15 POIs visiting 10:
```
15!/(15-10)! = 15!/5! = 10,897,286,400 routes
```

This exponential growth justifies using metaheuristics (GA).

### 5.3 Why Exact Methods Fail

**Dynamic Programming (Held-Karp)**:
- Complexity: O(N² × 2^N)
- Works for N ≤ 20
- WanderWise: 15 POIs → 2^15 = 32,768 subproblems (feasible)
- But TTDP has additional constraints (time windows) → even harder

**Branch and Bound**:
- Can solve optimally for small instances
- Unpredictable runtime (hours for N=15 with constraints)

**Genetic Algorithm**:
- Approximate but very good solutions
- Predictable runtime (always 50 generations)
- **Chosen for WanderWise**

---

## 6. WanderWise Adaptation

### 6.1 Problem Instance for Goa Tourism

**Given**:
- 100+ POIs in Goa (from CSV dataset)
- User selects interests → filter to ~30 relevant POIs
- User specifies: days (K), daily budget (T_max), start time

**WanderWise Process**:
1. **Module I (NLC)**: User interests → filter POIs
2. **Module II (Popularity)**: Calculate v(pᵢ) = rating × popularity
3. **Module III (K-Means)**: Cluster 30 POIs into K days → 10 POIs/day
4. **Module IV (GA)**: For each day, optimize route through 10 POIs

### 6.2 Simplified TTDP for Single Day

**Input**:
- POIs: [Baga Beach, Basilica, Fort Aguada, Calangute, ...]
- Start time: 09:00
- Budget: 480 minutes (8 hours)

**GA Chromosome**: Permutation of POI IDs
```
route = [uuid_baga, uuid_basilica, uuid_fort, uuid_calangute]
```

**Fitness**:
```python
fitness = sum(rating[poi] * popularity[poi] for poi in route)
          - 0.1 * sum(travel_time[route[i]][route[i+1]])
          - 1.0 * penalties(route)
```

**Constraints** (via penalties):
- Closed POI: +30 penalty
- Lunch invasion: +20 penalty
- Overtime: +0.5 per minute

### 6.3 Extensions for WanderWise+

**Future Enhancements**:
1. **User Preferences**: Adjust v(pᵢ) based on user profile
2. **Weather Constraints**: Outdoor POIs in good weather
3. **Crowds**: Avoid peak hours at popular POIs
4. **Accessibility**: Filter by wheelchair access, parking
5. **Multi-objective**: Pareto front (cost vs value vs time)

---

## References

1. **Vansteenwegen et al. (2011)**. "The Orienteering Problem: A Survey"
   - Operations Research, comprehensive OPTW survey

2. **Gavalas et al. (2014)**. "A Survey on Algorithmic Approaches for Solving Tourist Trip Design Problems"
   - Journal of Heuristics, tourism-specific review

3. **Cao et al. (2022)**. "An Optimal Round-Trip Route Planning Method for Tourism Based on TTDP"
   - Computational Intelligence and Neuroscience
   - **WanderWise reference for mathematical formulation**

4. **IEEE Access 2020**: Echeverría et al.
   - Practical TTDP implementation with GA

---

**Document Version**: 1.0  
**Last Updated**: January 2026  
**Status**: Mathematical Foundation
