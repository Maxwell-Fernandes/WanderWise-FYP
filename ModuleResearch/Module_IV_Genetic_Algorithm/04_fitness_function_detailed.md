# Module IV - Part 4: Fitness Function Detailed Analysis

## Table of Contents
1. [Introduction & Context](#introduction--context)
2. [TTDP/OPTW Problem Definition](#ttdpoptw-problem-definition)
3. [Complete Fitness Function Formula](#complete-fitness-function-formula)
4. [Component Breakdown](#component-breakdown)
5. [Real Goa POI Example Walkthrough](#real-goa-poi-example-walkthrough)
6. [Constraint Penalties Deep Dive](#constraint-penalties-deep-dive)
7. [Edge Cases & Special Scenarios](#edge-cases--special-scenarios)
8. [Implementation Considerations](#implementation-considerations)
9. [Pseudocode](#pseudocode)
10. [References](#references)

---

## 1. Introduction & Context

### 1.1 What is a Fitness Function?

In Genetic Algorithms (GAs), the **fitness function** is the core evaluation mechanism that determines the quality of a solution (chromosome). It serves as the "judge" that tells the algorithm which solutions are better than others, guiding the evolutionary process toward optimal solutions.

For the **WanderWise+ tourism itinerary planning system**, the fitness function must balance multiple competing objectives:
- **Maximize**: Tourist satisfaction (visiting highly-rated, popular places)
- **Minimize**: Travel time between locations
- **Satisfy**: Hard constraints (opening hours, lunch breaks, daily time budgets)

### 1.2 Why Fitness Function Design is Critical

The fitness function is arguably the **most important component** of our GA implementation because:

1. **Poor fitness function** → GA converges to suboptimal solutions (e.g., routes that violate opening hours)
2. **Good fitness function** → GA finds high-quality itineraries that tourists will actually enjoy
3. **Parameterized fitness function** → Adaptable to different user preferences and tourism contexts

Our fitness function is based on research from:
- **IEEE Access 2020**: "Improving Itinerary Recommendations for Tourists Through Metaheuristic Algorithms"
- **PeerJ 2024**: Enhanced genetic algorithm approaches
- **Computational Intelligence 2022 (Cao et al.)**: TTDP/OPTW mathematical foundations

---

## 2. TTDP/OPTW Problem Definition

### 2.1 Tourist Trip Design Problem (TTDP)

The **Tourist Trip Design Problem (TTDP)** is a variant of the Traveling Salesman Problem (TSP) with additional real-world constraints:

**Classic TSP**:
- Visit N cities exactly once
- Minimize total travel distance
- Return to starting city

**TTDP** (Tourism Context):
- Visit N Points of Interest (POIs) exactly once
- Maximize tourist satisfaction (not just minimize distance)
- Respect POI opening hours
- Stay within daily time budget
- Consider lunch breaks
- May NOT return to starting point (open tour)

### 2.2 Orienteering Problem with Time Windows (OPTW)

**OPTW** extends TTDP by adding:
- Each POI has a **score/profit** (in our case: rating × popularity)
- Each POI has a **time window** (opening_time to closing_time)
- Total tour time is limited (e.g., 8 hours per day)
- Goal: **Maximize total score** while respecting all time constraints

### 2.3 Mathematical Formulation

Let:
- **P** = {p₁, p₂, ..., pₙ} = Set of N POIs to visit
- **I** = (p_{i1}, p_{i2}, ..., p_{ik}) = Itinerary (ordered sequence of POIs)
- **R(pᵢ)** = Rating of POI i (scale 0-10)
- **Pop(pᵢ)** = Popularity score of POI i (scale 0-10)
- **t_{ij}** = Travel time from POI i to POI j (minutes)
- **v(pᵢ)** = Visit duration at POI i (minutes)
- **[o(pᵢ), c(pᵢ)]** = Opening and closing time of POI i
- **T_max** = Maximum daily tour duration (minutes)
- **L** = [L_start, L_end] = Lunch break interval (default: 12:00-13:30)

**Objective**: Find itinerary I that maximizes:

```
Fitness(I) = Total_POI_Value(I) - α × Travel_Penalty(I) - β × Constraint_Penalty(I)
```

Where:
- **α** = Travel time penalty weight (recommended: 0.1)
- **β** = Constraint violation penalty weight (recommended: 1.0)

---

## 3. Complete Fitness Function Formula

### 3.1 Full Mathematical Expression

Based on IEEE Access 2020 research paper:

```
Fitness(I) = k × T_available - Σ(Penalties + VisitTime + TravelTime)

Where:
  k = Scaling constant
  T_available = Tour end time - Tour start time
  Penalties = ClosedPOI_Penalty + LunchInvasion_Penalty + Overtime_Penalty
```

### 3.2 Alternative Formulation (Used in WanderWise+)

We adapt the formula to focus on **maximizing value**:

```
Fitness(I) = Σ POI_Value(pᵢ) - α × Total_Travel_Time(I) - β × Total_Penalties(I)

Where:
  POI_Value(pᵢ) = Rating(pᵢ) × Popularity(pᵢ)
  
  Total_Travel_Time(I) = Σ travel_time(p_{i}, p_{i+1}) for all consecutive pairs
  
  Total_Penalties(I) = Closed_POI_Penalty 
                       + Lunch_Invasion_Penalty 
                       + Overtime_Penalty
```

### 3.3 Parameter Values (From Research)

Based on empirical testing in IEEE Access 2020 paper:

| Parameter | Value | Justification |
|-----------|-------|---------------|
| **α (alpha)** | 0.1 | Travel time has moderate importance; prevents extremely long routes |
| **β (beta)** | 1.0 | Constraint violations are critical; heavily penalize infeasible solutions |
| **Closed POI Penalty** | 30 points | High penalty; visiting closed POI ruins tourist experience |
| **Lunch Invasion Penalty** | 20 points | Moderate penalty; tourists prefer proper lunch breaks |
| **Overtime Penalty** | 0.5 points/min | Linear penalty; slight preference for shorter tours |

**Why these specific values?**
- α = 0.1: A 100-minute travel time reduces fitness by only 10 points, equivalent to a POI with value ~1.0 (rating 5, popularity 2). This prevents the GA from obsessing over minimizing travel at the expense of visiting great POIs.
- β = 1.0: Constraint penalties directly subtract from fitness, making infeasible solutions clearly worse.
- Closed POI = 30: Equivalent to losing a top-tier POI (rating 10, popularity 3 = value 30).

---

## 4. Component Breakdown

### 4.1 POI Value Score

**Formula**:
```
POI_Value(p) = Rating(p) × Popularity(p)
```

**Example** (Basilica of Bom Jesus, Goa):
- Rating: 10 (from Google Reviews, tourist surveys)
- Popularity: 10 (UNESCO site, very famous)
- **POI Value = 10 × 10 = 100**

**Rationale**:
- **Multiplicative** (not additive) because a low-rated but popular place (tourist trap) should score lower than a high-rated popular place
- Both factors matter: 
  - High rating + Low popularity = Hidden gem (medium value)
  - Low rating + High popularity = Overhyped (medium value)
  - High rating + High popularity = Must-visit (high value)

**Value Ranges**:
- **Elite POIs** (90-100): Basilica of Bom Jesus, Se Cathedral
- **Excellent POIs** (70-89): Baga Beach, Fort Aguada, Palolem Beach
- **Good POIs** (50-69): Calangute Beach, Shri Mangueshi Temple
- **Decent POIs** (30-49): Miramar Beach, Local markets
- **Mediocre POIs** (10-29): Lesser-known spots

### 4.2 Travel Time Penalty

**Formula**:
```
Travel_Penalty(I) = α × Σ travel_time(pᵢ, pᵢ₊₁)
```

**Example** (Baga Beach → Basilica of Bom Jesus):
- Distance: ~15 km
- Average speed: 40 km/h (Goa traffic conditions)
- Travel time: 15/40 × 60 = 22.5 minutes
- **Penalty contribution = 0.1 × 22.5 = 2.25 points**

**Rationale**:
- α = 0.1 means travel time has **10% the weight** of POI value
- A 10-minute detour costs 1 fitness point
- Prevents routing through distant POIs unless they're significantly better
- Balance: Don't obsess over distance, but don't ignore it either

**Special Case - Using Distance Matrix**:
In WanderWise+, we use **pre-computed distance_matrix table** from PostGIS:
```sql
SELECT estimated_time_minutes 
FROM distance_matrix 
WHERE place_id_from = 'baga_beach_uuid' 
  AND place_id_to = 'basilica_uuid';
```

### 4.3 Constraint Penalties

#### 4.3.1 Closed POI Penalty

**Trigger**: Arrival time at POI is outside its opening hours

**Formula**:
```
If (arrival_time < opening_time OR arrival_time > closing_time):
    Penalty += 30 points
```

**Example**:
- POI: Basilica of Bom Jesus (opens 09:00, closes 18:30)
- Scheduled arrival: 19:00
- **Penalty = 30 points**

**Why 30 points?**
- Equivalent to losing a medium-value POI (e.g., rating 6, popularity 5 = 30)
- Forces GA to strongly avoid closed POIs
- Makes such solutions clearly inferior to feasible ones

#### 4.3.2 Lunch Invasion Penalty

**Trigger**: POI visit overlaps with designated lunch break time

**Default Lunch Window**: 12:00 - 13:30 (90 minutes)

**Formula**:
```
If POI visit overlaps [12:00, 13:30]:
    Penalty += 20 points
```

**Example**:
- POI visit: 11:30 - 12:45 (75 minutes)
- Lunch window: 12:00 - 13:30
- Overlap: 11:30-12:45 overlaps 12:00-12:45 = 45 minutes
- **Penalty = 20 points** (fixed, not proportional to overlap duration)

**Algorithm** (from IEEE Access 2020 paper):
```python
def check_lunch_invasion(visit_start, visit_duration, lunch_start=12*60, lunch_duration=90):
    """
    Check if POI visit invades lunch time.
    
    Args:
        visit_start: Visit start time (minutes since midnight)
        visit_duration: Duration of POI visit (minutes)
        lunch_start: Lunch start time (default 12:00 = 720 minutes)
        lunch_duration: Lunch duration (default 90 minutes)
    
    Returns:
        bool: True if invasion detected
    """
    visit_end = visit_start + visit_duration
    lunch_end = lunch_start + lunch_duration
    
    # Check for overlap
    if lunch_start >= visit_start and lunch_start <= visit_end:
        return True  # Lunch starts during POI visit
    if visit_start >= lunch_start and visit_start < lunch_end:
        return True  # POI visit starts during lunch
    
    return False
```

**Why 20 points?**
- Lower than closed POI penalty (tourists might tolerate late lunch)
- Still significant enough to influence route optimization
- Equivalent to losing a smaller POI (rating 5, popularity 4 = 20)

#### 4.3.3 Overtime Penalty

**Trigger**: Total tour duration exceeds daily time budget

**Formula**:
```
If total_time > T_max:
    Penalty += 0.5 × (total_time - T_max)
```

**Example**:
- Daily time budget: 480 minutes (8 hours)
- Actual tour duration: 520 minutes (8h 40min)
- Overtime: 520 - 480 = 40 minutes
- **Penalty = 0.5 × 40 = 20 points**

**Why 0.5 points/minute?**
- Linear scaling: Each extra minute costs a small amount
- 30 minutes overtime = 15 points (moderate penalty)
- 60 minutes overtime = 30 points (equivalent to closed POI)
- Allows GA to slightly exceed budget if POI value justifies it

---

## 5. Real Goa POI Example Walkthrough

### 5.1 Example Scenario Setup

**Itinerary Details**:
- **Duration**: 1 day
- **Start time**: 09:00
- **Daily time budget**: 8 hours (480 minutes)
- **Lunch break**: 12:00 - 13:30
- **POIs to visit**: 4 locations in North Goa

**Selected POIs** (from Wanderwise_datasetnew.csv):

| POI | Rating | Popularity | Duration | Opening | Closing | POI Value |
|-----|--------|-----------|----------|---------|---------|-----------|
| Baga Beach | 9 | 9 | 150 min | 00:00 | 23:59 | 81 |
| Basilica of Bom Jesus | 10 | 10 | 60 min | 09:00 | 18:30 | 100 |
| Fort Aguada | 9 | 8 | 90 min | 09:00 | 18:00 | 72 |
| Calangute Beach | 9 | 9 | 120 min | 00:00 | 23:59 | 81 |

**Distance Matrix** (travel times in minutes):

|  | Baga | Basilica | Fort | Calangute |
|--|------|----------|------|-----------|
| **Baga** | 0 | 22 | 15 | 8 |
| **Basilica** | 22 | 0 | 12 | 18 |
| **Fort** | 15 | 12 | 0 | 10 |
| **Calangute** | 8 | 18 | 10 | 0 |

### 5.2 Route Option A: [Baga → Basilica → Fort Aguada → Calangute]

#### Step 1: Calculate Total POI Value
```
POI_Value_Total = 81 + 100 + 72 + 81 = 334 points
```

#### Step 2: Calculate Travel Time & Penalty
```
Travel sequence:
  Baga → Basilica: 22 min
  Basilica → Fort Aguada: 12 min
  Fort Aguada → Calangute: 10 min

Total_Travel_Time = 22 + 12 + 10 = 44 minutes
Travel_Penalty = 0.1 × 44 = 4.4 points
```

#### Step 3: Simulate Timeline & Check Constraints

Starting at **09:00**:

```
09:00 - 11:30  | Baga Beach (150 min)                    | ✓ Open 24/7
11:30 - 11:52  | Travel to Basilica (22 min)             | 
11:52 - 12:52  | Basilica visit (60 min)                 | ⚠️ LUNCH INVASION! (12:00-13:30)
12:52 - 13:04  | Travel to Fort Aguada (12 min)          |
13:04 - 14:34  | Fort Aguada visit (90 min)              | ⚠️ LUNCH INVASION! (13:04-13:30 overlap)
14:34 - 14:44  | Travel to Calangute (10 min)            |
14:44 - 16:44  | Calangute Beach (120 min)               | ✓ Open 24/7
--------------------------------
End time: 16:44 (total duration: 464 minutes = 7h 44min)
```

**Constraint Violations**:
- ❌ **Basilica** visit (11:52-12:52) overlaps lunch (12:00-13:30) → **+20 penalty**
- ❌ **Fort Aguada** visit (13:04-14:34) overlaps lunch (13:04-13:30) → **+20 penalty**
- ✓ No closed POIs (all visited during opening hours)
- ✓ No overtime (464 min < 480 min budget)

```
Total_Constraint_Penalty = 20 + 20 = 40 points
```

#### Step 4: Calculate Final Fitness

```
Fitness(Route A) = POI_Value - Travel_Penalty - Constraint_Penalty
                 = 334 - 4.4 - (1.0 × 40)
                 = 334 - 4.4 - 40
                 = 289.6 points
```

### 5.3 Route Option B: [Fort Aguada → Basilica → Calangute → Baga]

Let's try a different order to avoid lunch invasion.

#### Step 1: POI Value (Same)
```
POI_Value_Total = 72 + 100 + 81 + 81 = 334 points
```

#### Step 2: Calculate Travel Time
```
Travel sequence:
  Fort Aguada → Basilica: 12 min
  Basilica → Calangute: 18 min
  Calangute → Baga: 8 min

Total_Travel_Time = 12 + 18 + 8 = 38 minutes
Travel_Penalty = 0.1 × 38 = 3.8 points
```

#### Step 3: Simulate Timeline

Starting at **09:00**:

```
09:00 - 10:30  | Fort Aguada (90 min)                    | ✓ Open 09:00-18:00
10:30 - 10:42  | Travel to Basilica (12 min)             |
10:42 - 11:42  | Basilica visit (60 min)                 | ✓ Open 09:00-18:30, before lunch
11:42 - 12:00  | Travel to Calangute (18 min)            |
12:00 - 14:00  | LUNCH BREAK (120 min)                   | 🍽️ Scheduled lunch at Calangute
14:00 - 16:00  | Calangute Beach (120 min)               | ✓ Open 24/7, after lunch
16:00 - 16:08  | Travel to Baga (8 min)                  |
16:08 - 18:38  | Baga Beach (150 min)                    | ✓ Open 24/7
--------------------------------
End time: 18:38 (total duration: 578 minutes = 9h 38min)
```

**Wait!** This exceeds our time budget. Let's adjust by **skipping lunch auto-insertion** and just checking for invasions:

**Revised Timeline** (without explicit lunch break):

```
09:00 - 10:30  | Fort Aguada (90 min)                    | ✓ Open 09:00-18:00
10:30 - 10:42  | Travel to Basilica (12 min)             |
10:42 - 11:42  | Basilica visit (60 min)                 | ✓ Before lunch window
11:42 - 12:00  | Travel to Calangute (18 min)            |
12:00 - 14:00  | Calangute Beach (120 min)               | ⚠️ LUNCH INVASION! (12:00-13:30)
14:00 - 14:08  | Travel to Baga (8 min)                  |
14:08 - 16:38  | Baga Beach (150 min)                    | ✓ After lunch
--------------------------------
End time: 16:38 (total duration: 458 minutes = 7h 38min)
```

**Constraint Violations**:
- ❌ **Calangute** visit (12:00-14:00) overlaps lunch (12:00-13:30) → **+20 penalty**
- ✓ No other violations

```
Total_Constraint_Penalty = 20 points
```

#### Step 4: Calculate Final Fitness

```
Fitness(Route B) = 334 - 3.8 - (1.0 × 20)
                 = 334 - 3.8 - 20
                 = 310.2 points
```

**Route B is better!** (310.2 > 289.6)

### 5.4 Route Option C: OPTIMAL [Fort Aguada → Calangute → Basilica → Baga]

Let's try to completely avoid lunch invasion:

#### Timeline:

```
09:00 - 10:30  | Fort Aguada (90 min)                    | ✓ Open 09:00-18:00
10:30 - 10:40  | Travel to Calangute (10 min)            |
10:40 - 12:40  | Calangute Beach (120 min)               | ⚠️ LUNCH INVASION! (12:00-12:40)
12:40 - 12:58  | Travel to Basilica (18 min)             |
12:58 - 13:58  | Basilica visit (60 min)                 | ⚠️ LUNCH INVASION! (12:58-13:30)
13:58 - 14:20  | Travel to Baga (22 min)                 |
14:20 - 16:50  | Baga Beach (150 min)                    | ✓ After lunch
--------------------------------
End time: 16:50 (total duration: 470 minutes = 7h 50min)
```

Still has invasions. Let's try **starting later** to schedule lunch properly:

#### Timeline (Start 10:00):

```
10:00 - 11:30  | Fort Aguada (90 min)                    | ✓ Open 09:00-18:00
11:30 - 11:40  | Travel to Calangute (10 min)            |
11:40 - 12:00  | Calangute Beach start (20 min)          | ✓ Before lunch
12:00 - 13:30  | NATURAL LUNCH BREAK                     | 🍽️ (beach has food shacks)
13:30 - 15:10  | Calangute Beach continue (100 min)      | ✓ After lunch (total 120min)
15:10 - 15:28  | Travel to Basilica (18 min)             |
15:28 - 16:28  | Basilica visit (60 min)                 | ✓ Open until 18:30
16:28 - 16:50  | Travel to Baga (22 min)                 |
16:50 - 19:20  | Baga Beach (150 min)                    | ✓ Open 24/7
--------------------------------
End time: 19:20 (total duration: 560 minutes = 9h 20min)
```

**Over budget!** This demonstrates the **tradeoff**: avoiding lunch invasion may require longer total time.

**Best feasible solution**: Route B with 1 lunch invasion is better than extending tour beyond budget.

### 5.5 Comparison Summary

| Route | POI Value | Travel Penalty | Constraint Penalty | **Final Fitness** |
|-------|-----------|----------------|--------------------|-------------------|
| **A**: Baga→Basilica→Fort→Calangute | 334 | 4.4 | 40 (2 invasions) | **289.6** |
| **B**: Fort→Basilica→Calangute→Baga | 334 | 3.8 | 20 (1 invasion) | **310.2** ✓ |
| **C**: With lunch break | 334 | ~4 | 0 | **~330** BUT overtime! |

**Key Insight**: The fitness function successfully guides the GA to prefer Route B, which:
- Minimizes lunch invasions
- Has slightly lower travel time
- Stays within time budget

---

## 6. Constraint Penalties Deep Dive

### 6.1 Why Penalties Matter

Penalties serve two critical purposes:

1. **Feasibility Enforcement**: Make infeasible solutions clearly worse than feasible ones
2. **Soft Constraint Handling**: Allow slight violations if compensated by higher POI value

### 6.2 Penalty Weight Tuning (α and β)

**Experiment** (from IEEE Access 2020):

| α | β | Result |
|---|---|--------|
| 0.01 | 0.5 | GA ignores travel time; produces zig-zag routes |
| 0.5 | 0.5 | GA over-emphasizes distance; misses great distant POIs |
| **0.1** | **1.0** | **Balanced: Good POIs, reasonable travel, respects constraints** |
| 0.1 | 2.0 | Over-penalizes violations; may skip good POIs to avoid risk |

**Recommended**: α=0.1, β=1.0

### 6.3 Adaptive Penalties (Future Enhancement)

**Idea**: Increase penalty over generations if constraints are frequently violated.

```python
def adaptive_penalty(base_penalty, violation_rate, generation):
    """
    Increase penalty if violations are common in population.
    
    Args:
        base_penalty: Initial penalty value
        violation_rate: % of population violating constraint
        generation: Current generation number
    
    Returns:
        Adjusted penalty
    """
    if violation_rate > 0.5:  # More than 50% violate
        return base_penalty * (1 + 0.1 * generation / 10)
    return base_penalty
```

---

## 7. Edge Cases & Special Scenarios

### 7.1 All POIs Closed at Desired Visit Time

**Scenario**: User wants afternoon tour (14:00 start), but all selected POIs close at 13:00.

**GA Behavior**:
- Every chromosome gets massive closed POI penalties
- Fitness values all very negative
- GA struggles to converge

**Solution**:
- **Pre-filtering**: Remove closed POIs before GA runs
- **Time shifting**: Suggest earlier start time to user
- **Penalty cap**: Limit max penalty to prevent -∞ fitness

### 7.2 Impossible Time Budget

**Scenario**: User selects 10 POIs with average duration 60 min each, but time budget is only 120 min.

**GA Behavior**:
- Every route gets huge overtime penalties
- GA tries to minimize penalties by removing POIs (but our encoding assumes fixed POI set)

**Solution**:
- **Pre-validation**: Check if `Σ(durations) + min_travel_time > budget`
- **Suggest reduction**: "These 10 POIs need ~8 hours. Reduce to 3-4 POIs or extend budget."

### 7.3 POI at Lunch Time Only

**Scenario**: Saturday Night Market (operates 18:00-23:00) - can never invade lunch.

**GA Behavior**: No issue; penalty correctly remains 0.

### 7.4 Clustered POIs (All in Same Area)

**Scenario**: 5 POIs in Old Goa, all within 2km of each other.

**Fitness Impact**:
- Travel penalties very low (short distances)
- POI values dominate fitness
- GA focuses on constraint satisfaction and POI selection order

**Risk**: GA might not explore distant but valuable POIs if cluster has high cumulative value.

**Mitigation**: Use K-means clustering (Module III) to pre-group POIs by day.

---

## 8. Implementation Considerations

### 8.1 Fitness Caching

**Problem**: Fitness calculation is expensive (database queries, time simulation).

**Solution**: Cache fitness values per chromosome.

```python
class Chromosome:
    def __init__(self, route):
        self.route = route
        self._fitness = None  # Cached fitness
        self._hash = hash(tuple(route))
    
    def get_fitness(self, fitness_calculator):
        if self._fitness is None:
            self._fitness = fitness_calculator.calculate(self.route)
        return self._fitness
```

### 8.2 Parallel Fitness Evaluation

For population size 100, we evaluate fitness 100 times per generation. With 50 generations = 5000 evaluations!

**Optimization**: Evaluate fitness in parallel.

```python
from concurrent.futures import ProcessPoolExecutor

def evaluate_population(population, fitness_func):
    with ProcessPoolExecutor(max_workers=4) as executor:
        fitness_values = list(executor.map(fitness_func, population))
    return fitness_values
```

### 8.3 Database Query Optimization

**Inefficient** (N² database queries):
```python
for i in range(len(route)-1):
    travel_time = db.query(DistanceMatrix).filter(
        DistanceMatrix.place_id_from == route[i],
        DistanceMatrix.place_id_to == route[i+1]
    ).first().estimated_time_minutes
```

**Efficient** (1 database query):
```python
# Pre-load entire distance matrix for selected POIs
place_ids = set(route)
distances = db.query(DistanceMatrix).filter(
    DistanceMatrix.place_id_from.in_(place_ids),
    DistanceMatrix.place_id_to.in_(place_ids)
).all()

# Build lookup dictionary
distance_dict = {
    (d.place_id_from, d.place_id_to): d.estimated_time_minutes
    for d in distances
}

# Fast lookup
travel_time = distance_dict[(route[i], route[i+1])]
```

### 8.4 Handling Missing Distance Data

**Problem**: New POI added; distance_matrix incomplete.

**Fallback**:
```python
def get_travel_time(from_poi, to_poi, distance_dict):
    # Try cache first
    if (from_poi, to_poi) in distance_dict:
        return distance_dict[(from_poi, to_poi)]
    
    # Fallback: Calculate on-the-fly using Haversine
    distance_km = haversine(from_poi.coords, to_poi.coords)
    return distance_km / 40 * 60  # 40 km/h average speed
```

---

## 9. Pseudocode

### 9.1 Complete Fitness Function

```python
def calculate_fitness(route, pois_data, distance_matrix, start_time, daily_budget_minutes):
    """
    Calculate fitness score for a tourism route.
    
    Args:
        route: List[UUID] - Ordered sequence of POI IDs to visit
        pois_data: Dict[UUID, POI] - POI metadata (rating, popularity, opening hours, duration)
        distance_matrix: Dict[(UUID, UUID), float] - Travel times between POIs (minutes)
        start_time: int - Tour start time (minutes since midnight, e.g., 540 for 09:00)
        daily_budget_minutes: int - Maximum tour duration (e.g., 480 for 8 hours)
    
    Returns:
        float: Fitness score (higher is better)
    """
    
    # ========== COMPONENT 1: POI Value ==========
    total_poi_value = 0
    for poi_id in route:
        poi = pois_data[poi_id]
        poi_value = poi.rating * poi.popularity_score
        total_poi_value += poi_value
    
    # ========== COMPONENT 2: Travel Penalty ==========
    total_travel_time = 0
    for i in range(len(route) - 1):
        from_poi = route[i]
        to_poi = route[i + 1]
        travel_time = distance_matrix.get((from_poi, to_poi), 0)
        total_travel_time += travel_time
    
    travel_penalty = ALPHA * total_travel_time  # ALPHA = 0.1
    
    # ========== COMPONENT 3: Constraint Penalties ==========
    constraint_penalty = 0
    current_time = start_time  # minutes since midnight
    
    LUNCH_START = 12 * 60  # 12:00 = 720 minutes
    LUNCH_END = 13.5 * 60  # 13:30 = 810 minutes
    
    for i, poi_id in enumerate(route):
        poi = pois_data[poi_id]
        
        # Penalty 1: Check if POI is closed at arrival time
        opening_minutes = time_to_minutes(poi.opening_time)  # e.g., 09:00 → 540
        closing_minutes = time_to_minutes(poi.closing_time)  # e.g., 18:00 → 1080
        
        # Handle 24-hour POIs (beaches)
        if opening_minutes == 0 and closing_minutes == 1439:  # 00:00-23:59
            is_open = True
        else:
            is_open = (current_time >= opening_minutes and current_time <= closing_minutes)
        
        if not is_open:
            constraint_penalty += CLOSED_POI_PENALTY  # 30 points
        
        # Penalty 2: Check for lunch invasion
        visit_duration = poi.duration_minutes
        visit_end_time = current_time + visit_duration
        
        # Does [current_time, visit_end_time] overlap [LUNCH_START, LUNCH_END]?
        lunch_invasion = (
            (current_time <= LUNCH_START and visit_end_time > LUNCH_START) or  # Visit starts before, ends during
            (current_time >= LUNCH_START and current_time < LUNCH_END)          # Visit starts during lunch
        )
        
        if lunch_invasion:
            constraint_penalty += LUNCH_INVASION_PENALTY  # 20 points
        
        # Update current time: add visit duration + travel to next POI
        current_time += visit_duration
        if i < len(route) - 1:  # Not the last POI
            next_poi = route[i + 1]
            current_time += distance_matrix.get((poi_id, next_poi), 0)
    
    # Penalty 3: Check for overtime
    total_tour_time = current_time - start_time
    if total_tour_time > daily_budget_minutes:
        overtime_minutes = total_tour_time - daily_budget_minutes
        constraint_penalty += OVERTIME_PENALTY_PER_MINUTE * overtime_minutes  # 0.5 per minute
    
    # ========== FINAL FITNESS CALCULATION ==========
    fitness = total_poi_value - travel_penalty - (BETA * constraint_penalty)
    
    return fitness


# ========== HELPER FUNCTION ==========
def time_to_minutes(time_obj):
    """
    Convert time object to minutes since midnight.
    
    Args:
        time_obj: datetime.time object (e.g., time(9, 30) for 09:30)
    
    Returns:
        int: Minutes since midnight
    """
    if time_obj is None:
        return 0
    return time_obj.hour * 60 + time_obj.minute


# ========== CONSTANTS ==========
ALPHA = 0.1  # Travel time penalty weight
BETA = 1.0   # Constraint violation penalty weight

CLOSED_POI_PENALTY = 30            # Points
LUNCH_INVASION_PENALTY = 20        # Points
OVERTIME_PENALTY_PER_MINUTE = 0.5  # Points per minute
```

### 9.2 Usage Example

```python
# Sample data
pois_data = {
    'baga_uuid': POI(rating=9, popularity=9, duration_minutes=150, opening_time=time(0,0), closing_time=time(23,59)),
    'basilica_uuid': POI(rating=10, popularity=10, duration_minutes=60, opening_time=time(9,0), closing_time=time(18,30)),
    'fort_uuid': POI(rating=9, popularity=8, duration_minutes=90, opening_time=time(9,0), closing_time=time(18,0)),
    'calangute_uuid': POI(rating=9, popularity=9, duration_minutes=120, opening_time=time(0,0), closing_time=time(23,59)),
}

distance_matrix = {
    ('baga_uuid', 'basilica_uuid'): 22,
    ('basilica_uuid', 'fort_uuid'): 12,
    ('fort_uuid', 'calangute_uuid'): 10,
    # ... other pairs
}

route = ['baga_uuid', 'basilica_uuid', 'fort_uuid', 'calangute_uuid']
start_time = 9 * 60  # 09:00
daily_budget = 8 * 60  # 8 hours

fitness = calculate_fitness(route, pois_data, distance_matrix, start_time, daily_budget)
print(f"Fitness: {fitness}")  # Output: Fitness: 289.6
```

---

## 10. References

### Academic Papers

1. **IEEE Access 2020**: "Improving Itinerary Recommendations for Tourists Through Metaheuristic Algorithms: A Case Study of Quito, Ecuador"
   - Authors: Vanessa Echeverría, et al.
   - Key contribution: Parameterized fitness function with k-means clustering + GA
   - Link: DOI 10.1109/ACCESS.2020.2990348

2. **PeerJ Computer Science 2024**: "Enhanced Genetic Algorithm with Novel Crossover for Tourism Itinerary Optimization"
   - Authors: Şehab & Turan
   - Key contribution: Copy Order Crossover (COX) method, 43.89% improvement
   - Focus: Istanbul tourism dataset

3. **Computational Intelligence and Neuroscience 2022**: "An Optimal Round-Trip Route Planning Method for Tourism Based on TTDP"
   - Authors: Cao et al.
   - Key contribution: Mathematical formulation of TTDP/OPTW problem
   - Constraint handling techniques

### WanderWise+ Implementation

- **File**: `backend/app/services/genetic_algorithm.py` (to be created)
- **Database**: `distance_matrix` table for O(1) distance lookups
- **Models**: `backend/app/models/places.py` - Place model with rating, popularity, opening hours

### Related Modules

- **Module III**: K-Means Clustering (groups POIs by days before GA runs)
- **Module II**: POI Popularity Analysis (calculates popularity_score from Google Reviews)
- **Module I**: Natural Language Classification (extracts user preferences for POI filtering)

---

**Document Version**: 1.0  
**Last Updated**: January 2026  
**Author**: WanderWise+ Research Team  
**Status**: Draft for Implementation
