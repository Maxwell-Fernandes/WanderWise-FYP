# Module IV - Part 3: Chromosome Representation and Encoding

## Table of Contents
1. [Introduction](#1-introduction)
2. [Permutation Encoding for Tourism Routes](#2-permutation-encoding-for-tourism-routes)
3. [Chromosome Structure in WanderWise](#3-chromosome-structure-in-wanderwise)
4. [Initialization Strategies](#4-initialization-strategies)
5. [Validity Constraints and Repair Mechanisms](#5-validity-constraints-and-repair-mechanisms)
6. [Real Goa POI Examples](#6-real-goa-poi-examples)
7. [Implementation Details](#7-implementation-details)
8. [References](#8-references)

---

## 1. Introduction

### 1.1 What is a Chromosome?

In genetic algorithms, a **chromosome** is the data structure that encodes a candidate solution to the optimization problem. For the Tourism Trip Design Problem (TTDP), each chromosome represents a complete tourism itinerary—a sequence of Points of Interest (POIs) to visit.

**Key Concepts**:
- **Gene**: A single element in the chromosome (one POI)
- **Allele**: The specific value of a gene (the POI's unique identifier)
- **Locus**: The position of a gene in the chromosome (visit order)
- **Genotype**: The chromosome representation itself
- **Phenotype**: The actual tourism route with times, distances, and constraints

### 1.2 Why Permutation Encoding?

For TTDP, we use **permutation encoding** because:

1. **Order Matters**: The sequence of visits affects total travel time
2. **Uniqueness Required**: Each POI should appear at most once
3. **No Duplicates**: Visiting the same place twice is wasteful
4. **TSP-Like Structure**: TTDP is a constrained variant of the Traveling Salesman Problem

**Alternative Encodings (Not Used)**:
- ❌ **Binary encoding**: Cannot represent order efficiently
- ❌ **Real-valued encoding**: No natural ordering for discrete POIs
- ❌ **Tree encoding**: Overly complex for linear routes

---

## 2. Permutation Encoding for Tourism Routes

### 2.1 Basic Permutation Structure

A chromosome is represented as an ordered list of POI identifiers:

```
Chromosome = [POI₁, POI₂, POI₃, ..., POIₙ]
```

**Properties**:
- Length: `n` POIs (typically 5-15 for a single-day tour)
- Values: Unique POI identifiers (UUIDs or integer IDs)
- Order: Determines visit sequence from start to end

**Example (Using Goa POIs)**:
```python
# Chromosome representing a route through 6 Goa POIs
chromosome = [
    "poi_003",  # Basilica of Bom Jesus
    "poi_015",  # Se Cathedral
    "poi_042",  # Fort Aguada
    "poi_001",  # Baga Beach
    "poi_002",  # Calangute Beach
    "poi_089"   # Palolem Beach
]

# This represents the route:
# Start → Basilica → Cathedral → Fort → Baga → Calangute → Palolem → End
```

### 2.2 Mathematical Formulation

Let:
- `P = {p₁, p₂, ..., pₘ}` be the set of all available POIs (m = 100+ for Goa)
- `S ⊆ P` be the subset of POIs selected for the tour (|S| = n)
- `π: {1, 2, ..., n} → S` be a permutation function

Then a chromosome is:
```
C = [π(1), π(2), ..., π(n)]
```

Where:
- π(i) ≠ π(j) for all i ≠ j (no duplicates)
- Each π(i) ∈ S (all genes are valid POIs)

### 2.3 Search Space Size

The number of possible chromosomes (routes) is:

```
Search Space Size = m! / (m - n)!
```

**Example for Goa**:
- Total POIs (m): 100
- POIs per route (n): 10
- Search space: 100! / 90! ≈ 6.3 × 10¹⁹ possible routes

This enormous search space is why exhaustive search is infeasible and GAs are necessary.

---

## 3. Chromosome Structure in WanderWise

### 3.1 Complete Chromosome Definition

In WanderWise, a chromosome contains:

1. **Gene Sequence**: Ordered list of POI IDs
2. **Metadata** (computed during fitness evaluation):
   - Total travel distance (km)
   - Total travel time (minutes)
   - Total visit duration (minutes)
   - Constraint violations (penalties)
   - Fitness score

### 3.2 Python Class Structure

```python
from dataclasses import dataclass
from typing import List
from uuid import UUID

@dataclass
class Chromosome:
    """
    Represents a tourism route as a chromosome in the genetic algorithm.
    """
    genes: List[str]  # List of POI IDs in visit order
    fitness: float = 0.0  # Fitness score (higher is better)
    
    # Cached phenotype values (computed once)
    total_distance_km: float = 0.0
    total_travel_time_min: float = 0.0
    total_visit_time_min: float = 0.0
    constraint_penalty: float = 0.0
    
    # Constraint violation flags
    violates_time_budget: bool = False
    has_closed_pois: bool = False
    invades_lunch_time: bool = False
    
    def __len__(self) -> int:
        """Number of POIs in the route."""
        return len(self.genes)
    
    def __getitem__(self, index: int) -> str:
        """Access POI by index."""
        return self.genes[index]
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"Chromosome(genes={self.genes}, fitness={self.fitness:.2f})"
```

### 3.3 Example Chromosome Instance

```python
# Example: North Goa Heritage Tour
chromosome = Chromosome(
    genes=[
        "poi_003",  # Basilica of Bom Jesus
        "poi_015",  # Se Cathedral
        "poi_022",  # Church of St. Francis of Assisi
        "poi_042",  # Fort Aguada
        "poi_001"   # Baga Beach (sunset)
    ],
    fitness=952.5,  # After fitness evaluation
    total_distance_km=28.4,
    total_travel_time_min=85.2,
    total_visit_time_min=390.0,
    constraint_penalty=0.0,  # No violations
    violates_time_budget=False,
    has_closed_pois=False,
    invades_lunch_time=False
)

print(chromosome)
# Output: Chromosome(genes=['poi_003', 'poi_015', 'poi_022', 'poi_042', 'poi_001'], fitness=952.50)
```

---

## 4. Initialization Strategies

### 4.1 Random Initialization (Baseline)

The simplest approach: randomly select `n` POIs and shuffle them.

**Algorithm**:
```python
import random
from typing import List, Set

def random_initialization(
    available_pois: List[str],
    route_length: int,
    population_size: int
) -> List[Chromosome]:
    """
    Generate initial population with random chromosomes.
    
    Args:
        available_pois: List of all POI IDs
        route_length: Number of POIs per route
        population_size: Number of chromosomes to generate
    
    Returns:
        List of randomly initialized chromosomes
    """
    population = []
    
    for _ in range(population_size):
        # Randomly sample POIs without replacement
        selected_pois = random.sample(available_pois, route_length)
        
        # Shuffle to randomize order
        random.shuffle(selected_pois)
        
        # Create chromosome
        chromosome = Chromosome(genes=selected_pois)
        population.append(chromosome)
    
    return population
```

**Example Output** (for 3 chromosomes, 5 POIs each):
```python
population = random_initialization(
    available_pois=["poi_001", "poi_002", ..., "poi_100"],
    route_length=5,
    population_size=3
)

# Chromosome 1: ['poi_042', 'poi_003', 'poi_089', 'poi_015', 'poi_001']
# Chromosome 2: ['poi_002', 'poi_022', 'poi_003', 'poi_042', 'poi_089']
# Chromosome 3: ['poi_015', 'poi_001', 'poi_002', 'poi_042', 'poi_022']
```

**Pros**:
- ✅ Simple to implement
- ✅ Maximum diversity in initial population
- ✅ No bias toward specific solutions

**Cons**:
- ❌ Most random routes are infeasible (violate constraints)
- ❌ Low initial fitness scores
- ❌ May require many generations to converge

### 4.2 Greedy Seeding (Nearest Neighbor Heuristic)

Initialize some chromosomes using a constructive heuristic to provide good starting points.

**Nearest Neighbor Algorithm**:
1. Start at a random POI
2. Repeatedly visit the nearest unvisited POI
3. Continue until `n` POIs are visited

**Pseudocode**:
```python
def greedy_nearest_neighbor(
    start_poi: str,
    available_pois: List[str],
    route_length: int,
    distance_matrix: Dict[tuple, float]
) -> Chromosome:
    """
    Generate chromosome using nearest neighbor heuristic.
    
    Args:
        start_poi: Initial POI to start from
        available_pois: All available POI IDs
        route_length: Number of POIs to include
        distance_matrix: Pre-computed distances between POIs
    
    Returns:
        Greedily constructed chromosome
    """
    route = [start_poi]
    remaining_pois = set(available_pois) - {start_poi}
    
    current_poi = start_poi
    
    while len(route) < route_length and remaining_pois:
        # Find nearest unvisited POI
        nearest_poi = min(
            remaining_pois,
            key=lambda poi: distance_matrix.get((current_poi, poi), float('inf'))
        )
        
        route.append(nearest_poi)
        remaining_pois.remove(nearest_poi)
        current_poi = nearest_poi
    
    return Chromosome(genes=route)
```

**Example (Starting from Basilica of Bom Jesus)**:

```
Step 1: Start at Basilica (poi_003)
        Route: [poi_003]

Step 2: Nearest to Basilica → Se Cathedral (200m away)
        Route: [poi_003, poi_015]

Step 3: Nearest to Cathedral → Church of St. Francis (150m away)
        Route: [poi_003, poi_015, poi_022]

Step 4: Nearest to Church → Fort Aguada (8km away)
        Route: [poi_003, poi_015, poi_022, poi_042]

Step 5: Nearest to Fort → Baga Beach (5km away)
        Route: [poi_003, poi_015, poi_022, poi_042, poi_001]

Final Chromosome: [poi_003, poi_015, poi_022, poi_042, poi_001]
```

### 4.3 Hybrid Initialization (Recommended for WanderWise)

Combine random and greedy approaches to balance exploration and exploitation.

**Strategy**:
- 70% random chromosomes (exploration)
- 30% greedy chromosomes (exploitation)

**Implementation**:
```python
def hybrid_initialization(
    available_pois: List[str],
    route_length: int,
    population_size: int,
    distance_matrix: Dict[tuple, float],
    greedy_ratio: float = 0.3
) -> List[Chromosome]:
    """
    Generate initial population with mix of random and greedy chromosomes.
    
    Args:
        available_pois: All POI IDs
        route_length: POIs per route
        population_size: Total chromosomes to generate
        distance_matrix: Pre-computed POI distances
        greedy_ratio: Fraction of greedy chromosomes (default: 0.3)
    
    Returns:
        Hybrid population
    """
    population = []
    
    greedy_count = int(population_size * greedy_ratio)
    random_count = population_size - greedy_count
    
    # Generate greedy chromosomes (different starting points)
    for _ in range(greedy_count):
        start_poi = random.choice(available_pois)
        chromosome = greedy_nearest_neighbor(
            start_poi, available_pois, route_length, distance_matrix
        )
        population.append(chromosome)
    
    # Generate random chromosomes
    random_pop = random_initialization(available_pois, route_length, random_count)
    population.extend(random_pop)
    
    return population
```

**Example Output** (Population size 10, 30% greedy):
```
Greedy Chromosomes (3):
  1. [poi_003, poi_015, poi_022, poi_042, poi_001]  # Started from Basilica
  2. [poi_001, poi_002, poi_042, poi_003, poi_015]  # Started from Baga
  3. [poi_089, poi_067, poi_034, poi_001, poi_002]  # Started from Palolem

Random Chromosomes (7):
  4. [poi_042, poi_089, poi_003, poi_001, poi_015]
  5. [poi_015, poi_001, poi_042, poi_002, poi_022]
  6. [poi_002, poi_003, poi_001, poi_089, poi_042]
  7. [poi_022, poi_042, poi_015, poi_089, poi_003]
  8. [poi_089, poi_022, poi_001, poi_003, poi_015]
  9. [poi_003, poi_002, poi_089, poi_042, poi_022]
 10. [poi_001, poi_015, poi_003, poi_002, poi_042]
```

### 4.4 Cluster-Based Initialization (Advanced)

For multi-day tours, initialize chromosomes where POIs are geographically clustered per day.

**Use Case**: 3-day Goa tour → North Goa (Day 1), Central Goa (Day 2), South Goa (Day 3)

**Algorithm**:
1. Pre-cluster POIs using K-means (see Module III)
2. Assign one cluster to each chromosome
3. Randomize order within cluster

```python
def cluster_based_initialization(
    poi_clusters: Dict[int, List[str]],  # Cluster ID → POI IDs
    pois_per_route: int,
    population_size: int
) -> List[Chromosome]:
    """
    Initialize chromosomes with POIs from same geographic cluster.
    
    Args:
        poi_clusters: Pre-computed POI clusters
        pois_per_route: POIs per route
        population_size: Number of chromosomes
    
    Returns:
        Cluster-based population
    """
    population = []
    cluster_ids = list(poi_clusters.keys())
    
    for _ in range(population_size):
        # Randomly select a cluster
        cluster_id = random.choice(cluster_ids)
        cluster_pois = poi_clusters[cluster_id]
        
        # Sample POIs from this cluster
        if len(cluster_pois) >= pois_per_route:
            selected_pois = random.sample(cluster_pois, pois_per_route)
        else:
            # If cluster too small, sample remaining from other clusters
            selected_pois = cluster_pois.copy()
            other_pois = [p for cid, pois in poi_clusters.items() 
                         if cid != cluster_id for p in pois]
            selected_pois.extend(
                random.sample(other_pois, pois_per_route - len(selected_pois))
            )
        
        random.shuffle(selected_pois)
        population.append(Chromosome(genes=selected_pois))
    
    return population
```

---

## 5. Validity Constraints and Repair Mechanisms

### 5.1 Chromosome Validity Rules

A chromosome is **valid** if:
1. ✅ All genes are unique (no duplicate POIs)
2. ✅ All genes correspond to existing POIs
3. ✅ Chromosome length matches expected route length
4. ✅ No null/undefined genes

A chromosome is **feasible** if it also satisfies:
5. ✅ Total time ≤ time budget (e.g., 8 hours)
6. ✅ All POIs are open during visit times
7. ✅ Lunch break does not overlap with POI visits

**Note**: Validity is structural (must be enforced), feasibility is preferential (handled by fitness penalties).

### 5.2 Ensuring Validity During Initialization

**Check 1: Unique Genes**
```python
def is_valid_chromosome(chromosome: Chromosome) -> bool:
    """Check if chromosome has valid structure."""
    genes = chromosome.genes
    
    # Check for duplicates
    if len(genes) != len(set(genes)):
        return False
    
    # Check all genes are non-empty strings
    if any(not gene for gene in genes):
        return False
    
    return True
```

**Check 2: Existing POIs**
```python
def validate_against_database(
    chromosome: Chromosome,
    valid_poi_ids: Set[str]
) -> bool:
    """Verify all genes reference real POIs in database."""
    return all(gene in valid_poi_ids for gene in chromosome.genes)
```

### 5.3 Repair Mechanisms for Crossover/Mutation

Crossover and mutation can produce invalid chromosomes. **Repair mechanisms** fix them.

**Problem 1: Duplicate Genes**

After crossover, a child may have duplicate POIs:
```python
# After PMX crossover
child = ['poi_003', 'poi_015', 'poi_003', 'poi_042', 'poi_001']  # poi_003 appears twice!
```

**Repair Strategy 1: Replace Duplicates with Missing POIs**
```python
def repair_duplicates(
    chromosome: Chromosome,
    available_pois: List[str]
) -> Chromosome:
    """
    Remove duplicate genes and replace with missing POIs.
    
    Args:
        chromosome: Potentially invalid chromosome
        available_pois: Full set of valid POI IDs
    
    Returns:
        Repaired chromosome with unique genes
    """
    genes = chromosome.genes.copy()
    seen = set()
    duplicates_indices = []
    
    # Find duplicates
    for i, gene in enumerate(genes):
        if gene in seen:
            duplicates_indices.append(i)
        else:
            seen.add(gene)
    
    # Find missing POIs (candidates for replacement)
    used_pois = set(genes)
    missing_pois = [p for p in available_pois if p not in used_pois]
    
    # Replace duplicates with missing POIs
    for i, missing_poi in zip(duplicates_indices, missing_pois):
        genes[i] = missing_poi
    
    chromosome.genes = genes
    return chromosome
```

**Example**:
```python
# Before repair
child = ['poi_003', 'poi_015', 'poi_003', 'poi_042', 'poi_001']

# After repair (replace 2nd poi_003 with missing poi_022)
child = ['poi_003', 'poi_015', 'poi_022', 'poi_042', 'poi_001']
```

**Problem 2: Wrong Chromosome Length**

Rare but possible after mutation:
```python
# Mutation accidentally deleted a gene
chromosome = ['poi_003', 'poi_015', 'poi_042']  # Expected 5, got 3
```

**Repair Strategy 2: Pad or Truncate**
```python
def repair_length(
    chromosome: Chromosome,
    expected_length: int,
    available_pois: List[str]
) -> Chromosome:
    """Ensure chromosome has correct length."""
    genes = chromosome.genes
    
    if len(genes) < expected_length:
        # Pad with random unused POIs
        used = set(genes)
        candidates = [p for p in available_pois if p not in used]
        genes.extend(random.sample(candidates, expected_length - len(genes)))
    
    elif len(genes) > expected_length:
        # Truncate to correct length
        genes = genes[:expected_length]
    
    chromosome.genes = genes
    return chromosome
```

### 5.4 Lazy Repair vs. Eager Repair

**Lazy Repair** (Recommended):
- Only repair chromosomes when they are selected for next generation
- Saves computation on chromosomes that will be discarded

**Eager Repair**:
- Repair immediately after crossover/mutation
- Ensures all chromosomes are always valid

**WanderWise Recommendation**: Use **lazy repair** with validation checks before fitness evaluation.

---

## 6. Real Goa POI Examples

### 6.1 Example 1: North Goa Beach Hopping Tour

**User Preferences**:
- Interests: Beaches, Water Sports, Nightlife
- Duration: 1 day (8 hours)
- Start time: 9:00 AM

**Chromosome**:
```python
chromosome = Chromosome(genes=[
    "poi_001",  # Baga Beach (9:00-11:30, 150min)
    "poi_002",  # Calangute Beach (12:30-14:30, 120min) - after lunch
    "poi_008",  # Anjuna Beach (15:00-17:00, 120min)
    "poi_013",  # Vagator Beach (17:30-19:00, 90min)
])

# Phenotype:
# 09:00 - 11:30: Baga Beach (water sports)
# 11:30 - 12:00: Travel to Calangute (4km, 12min)
# 12:00 - 13:30: Lunch break
# 13:30 - 13:42: Travel to Calangute (3km, 12min)
# 13:42 - 15:42: Calangute Beach
# 15:42 - 16:00: Travel to Anjuna (8km, 18min)
# 16:00 - 18:00: Anjuna Beach
# 18:00 - 18:15: Travel to Vagator (3km, 15min)
# 18:15 - 19:45: Vagator Beach (sunset)
# Total: 8 hours, 4 POIs, 18km travel
```

### 6.2 Example 2: Old Goa Heritage Circuit

**User Preferences**:
- Interests: History, Architecture, Religious Sites
- Duration: 1 day (7 hours)
- Start time: 9:00 AM

**Chromosome**:
```python
chromosome = Chromosome(genes=[
    "poi_003",  # Basilica of Bom Jesus (9:00-10:00, 60min, entry ₹250)
    "poi_015",  # Se Cathedral (10:05-11:05, 60min, entry ₹100)
    "poi_022",  # Church of St. Francis of Assisi (11:10-11:50, 40min)
    "poi_042",  # Fort Aguada (13:30-15:00, 90min) - after lunch
    "poi_037",  # Reis Magos Fort (15:30-16:30, 60min)
])

# Phenotype:
# 09:00 - 10:00: Basilica of Bom Jesus (UNESCO site)
# 10:00 - 10:05: Walk to Se Cathedral (200m, 5min)
# 10:05 - 11:05: Se Cathedral
# 11:05 - 11:10: Walk to Church (150m, 5min)
# 11:10 - 11:50: Church of St. Francis
# 11:50 - 13:30: Lunch + travel to Fort Aguada (8km, 24min)
# 13:30 - 15:00: Fort Aguada (sunset point)
# 15:00 - 15:30: Travel to Reis Magos (12km, 30min)
# 15:30 - 16:30: Reis Magos Fort
# Total: 7.5 hours, 5 POIs, 20km travel, ₹350 entry fees
```

### 6.3 Example 3: Multi-Interest Balanced Tour

**User Preferences**:
- Interests: Nature, Culture, Food, Beaches
- Duration: 1 day (8 hours)
- Start time: 8:00 AM

**Chromosome**:
```python
chromosome = Chromosome(genes=[
    "poi_056",  # Dudhsagar Waterfalls (8:00-11:00, 180min, nature)
    "poi_028",  # Spice Plantation (11:30-13:30, 120min, culture + lunch included)
    "poi_003",  # Basilica of Bom Jesus (14:30-15:30, 60min, culture)
    "poi_001",  # Baga Beach (16:00-18:00, 120min, beach + sunset)
])

# Phenotype:
# 08:00 - 11:00: Dudhsagar Waterfalls (trekking, swimming)
# 11:00 - 11:30: Travel to Spice Plantation (25km, 45min)
# 11:30 - 13:30: Spice Plantation (tour + traditional Goan lunch)
# 13:30 - 14:30: Travel to Basilica (35km, 60min)
# 14:30 - 15:30: Basilica of Bom Jesus
# 15:30 - 16:00: Travel to Baga Beach (15km, 30min)
# 16:00 - 18:00: Baga Beach (relax, sunset)
# Total: 10 hours (long day), 4 POIs, 75km travel
```

---

## 7. Implementation Details

### 7.1 Database Schema for POIs

```sql
-- Goa Places Table (from database_setup.sql)
CREATE TABLE goa_places (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    opening_time TIME,
    closing_time TIME,
    entry_fee DECIMAL(10, 2),
    average_duration_minutes INTEGER,
    popularity_score INTEGER CHECK (popularity_score BETWEEN 1 AND 10),
    rating DECIMAL(3, 2) CHECK (rating BETWEEN 1.0 AND 10.0),
    description TEXT
);

-- Example POI record
INSERT INTO goa_places VALUES (
    'poi_003',
    'Basilica of Bom Jesus',
    'Historical & Religious',
    ST_GeogFromText('POINT(73.9115 15.5007)'),  -- Lat: 15.5007, Lon: 73.9115
    '09:00:00',
    '18:30:00',
    250.00,
    60,
    10,
    10.0,
    'UNESCO World Heritage Site, houses remains of St. Francis Xavier'
);
```

### 7.2 Python Data Access Layer

```python
from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import List
from app.models.places import Place

def fetch_candidate_pois(
    db: Session,
    user_interests: List[str],
    max_pois: int = 50
) -> List[str]:
    """
    Fetch POI IDs matching user interests for chromosome initialization.
    
    Args:
        db: Database session
        user_interests: List of interest categories (e.g., ["Beaches", "History"])
        max_pois: Maximum POIs to return
    
    Returns:
        List of POI IDs as strings
    """
    stmt = (
        select(Place.id)
        .where(Place.category.in_(user_interests))
        .order_by(Place.popularity_score.desc())
        .limit(max_pois)
    )
    
    result = db.execute(stmt)
    poi_ids = [str(row[0]) for row in result]
    
    return poi_ids
```

### 7.3 Complete Initialization Pipeline

```python
from typing import List, Dict
from sqlalchemy.orm import Session

def initialize_population(
    db: Session,
    user_interests: List[str],
    route_length: int,
    population_size: int,
    distance_matrix: Dict[tuple, float],
    initialization_method: str = "hybrid"
) -> List[Chromosome]:
    """
    Complete initialization pipeline for WanderWise genetic algorithm.
    
    Args:
        db: Database session
        user_interests: User's interest categories
        route_length: Number of POIs per route
        population_size: Number of chromosomes to generate
        distance_matrix: Pre-computed POI distances
        initialization_method: "random", "greedy", "hybrid", or "cluster"
    
    Returns:
        Initial population of valid chromosomes
    """
    # Step 1: Fetch candidate POIs from database
    candidate_pois = fetch_candidate_pois(db, user_interests, max_pois=50)
    
    if len(candidate_pois) < route_length:
        raise ValueError(
            f"Not enough POIs ({len(candidate_pois)}) for route length {route_length}"
        )
    
    # Step 2: Initialize population based on method
    if initialization_method == "random":
        population = random_initialization(candidate_pois, route_length, population_size)
    
    elif initialization_method == "greedy":
        population = []
        for _ in range(population_size):
            start_poi = random.choice(candidate_pois)
            chromosome = greedy_nearest_neighbor(
                start_poi, candidate_pois, route_length, distance_matrix
            )
            population.append(chromosome)
    
    elif initialization_method == "hybrid":
        population = hybrid_initialization(
            candidate_pois, route_length, population_size, distance_matrix, greedy_ratio=0.3
        )
    
    elif initialization_method == "cluster":
        # Requires pre-computed clusters (see Module III)
        from app.services.clustering import get_poi_clusters
        poi_clusters = get_poi_clusters(db, candidate_pois, k=3)
        population = cluster_based_initialization(poi_clusters, route_length, population_size)
    
    else:
        raise ValueError(f"Unknown initialization method: {initialization_method}")
    
    # Step 3: Validate all chromosomes
    valid_poi_set = set(candidate_pois)
    for chromosome in population:
        if not is_valid_chromosome(chromosome):
            raise ValueError(f"Invalid chromosome generated: {chromosome}")
        if not validate_against_database(chromosome, valid_poi_set):
            raise ValueError(f"Chromosome contains unknown POIs: {chromosome}")
    
    return population
```

### 7.4 Usage Example

```python
from app.database import get_db
from app.services.distance_matrix import load_distance_matrix

# User request
user_interests = ["Beaches", "Historical & Religious", "Nature"]
route_length = 6
population_size = 100

# Initialize database session
db = next(get_db())

# Load pre-computed distance matrix
distance_matrix = load_distance_matrix(db)

# Initialize population
population = initialize_population(
    db=db,
    user_interests=user_interests,
    route_length=route_length,
    population_size=population_size,
    distance_matrix=distance_matrix,
    initialization_method="hybrid"
)

print(f"Generated {len(population)} chromosomes")
print(f"Sample chromosome: {population[0]}")

# Output:
# Generated 100 chromosomes
# Sample chromosome: Chromosome(genes=['poi_003', 'poi_001', 'poi_042', 'poi_015', 'poi_089', 'poi_022'], fitness=0.00)
```

---

## 8. References

### Academic Papers
1. **Lim, K. H., Chan, J., Karunasekera, S., & Leckie, C. (2020)**: "Personalized Itinerary Recommendation with Queuing Time Awareness", *IEEE Access*, 8, 88573-88591. DOI: 10.1109/ACCESS.2020.2993344
   - Section 4.2: Chromosome encoding for tourism routes
   - Section 4.3: Population initialization strategies

2. **Gunawan, A., Lau, H. C., & Vansteenwegen, P. (2016)**: "Orienteering Problem: A survey of recent variants, solution approaches and applications", *European Journal of Operational Research*, 255(2), 315-332.
   - Permutation encoding for route optimization
   - Repair mechanisms for invalid solutions

3. **Gavalas, D., Konstantopoulos, C., Mastakas, K., & Pantziou, G. (2014)**: "Mobile recommender systems in tourism", *Journal of Network and Computer Applications*, 39, 319-333.
   - Initialization heuristics for tourism route planning

### WanderWise Codebase
- `backend/app/models/places.py`: POI database model
- `backend/app/services/genetic_algorithm.py`: GA implementation (to be created)
- `backend/app/services/distance_matrix.py`: Pre-computed distance access
- `database/database_setup.sql`: Database schema

### Related Modules
- **Module I**: Natural Language to Category mapping (determines candidate POIs)
- **Module II**: POI popularity scoring (influences POI selection probability)
- **Module III**: K-means clustering (for multi-day tour initialization)
- **Module IV - Part 4**: Fitness function (evaluates chromosome quality)
- **Module IV - Part 6**: Crossover operators (generate offspring chromosomes)
- **Module IV - Part 7**: Mutation operators (introduce diversity)

---

**Document Version**: 1.0  
**Last Updated**: January 2026  
**Author**: WanderWise+ Research Team  
**File**: `ModuleResearch/Module_IV_Genetic_Algorithm/03_chromosome_representation.md`
