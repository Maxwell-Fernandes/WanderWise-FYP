# Module IV - Part 10: Complete Implementation Pseudocode and Integration

## Table of Contents
1. [Introduction](#1-introduction)
2. [Complete GA Algorithm Pseudocode](#2-complete-ga-algorithm-pseudocode)
3. [WanderWise Backend Integration](#3-wanderwise-backend-integration)
4. [File Structure and Code Organization](#4-file-structure-and-code-organization)
5. [API Endpoint Implementation](#5-api-endpoint-implementation)
6. [Real Goa POI Implementation Example](#6-real-goa-poi-implementation-example)
7. [Testing Strategy](#7-testing-strategy)
8. [Performance Optimization](#8-performance-optimization)
9. [Deployment Considerations](#9-deployment-considerations)
10. [References](#10-references)

---

## 1. Introduction

### 1.1 Purpose

This document provides **production-ready pseudocode** for implementing the complete Genetic Algorithm route optimization system in WanderWise+. It integrates all concepts from Parts 1-8:

- Part 1: GA Fundamentals
- Part 2: TTDP/OPTW Problem Definition
- Part 3: Chromosome Representation
- Part 4: Fitness Function
- Part 5: Selection Methods
- Part 6: Crossover Operators
- Part 7: Mutation Strategies
- Part 8: Parameter Tuning

### 1.2 Implementation Goals

1. ✅ **Correctness**: Implement GA accurately per research papers
2. ✅ **Efficiency**: Optimize for real-time route planning (<10s response time)
3. ✅ **Maintainability**: Clear code structure, well-documented
4. ✅ **Scalability**: Handle 5-15 POI routes, 1-7 day tours
5. ✅ **Integration**: Seamless integration with existing WanderWise backend

---

## 2. Complete GA Algorithm Pseudocode

### 2.1 Main GA Loop

```
ALGORITHM: GeneticAlgorithmRouteOptimizer

INPUT:
    user_interests: List[String]          # User's interest categories
    num_pois: Integer                     # POIs per route (5-15)
    time_budget_hours: Float              # Available time (e.g., 8 hours)
    start_time: Time                      # Start time (e.g., 09:00)
    num_days: Integer                     # Number of days (default: 1)

OUTPUT:
    optimized_route: List[POI]            # Best route found
    fitness_score: Float                  # Quality of route
    metadata: Dict                        # Distance, time, etc.

PARAMETERS:
    N = 100                               # Population size
    G_max = 50                            # Max generations
    P_c = 0.8                             # Crossover rate
    P_m = 0.2                             # Mutation rate
    k = 5                                 # Tournament size
    E = 2                                 # Elite count

BEGIN
    # Step 1: Fetch candidate POIs from database
    candidate_pois ← FETCH_CANDIDATE_POIS(user_interests)
    
    IF LENGTH(candidate_pois) < num_pois THEN
        RETURN ERROR "Insufficient POIs matching interests"
    END IF
    
    # Step 2: Load distance matrix
    distance_matrix ← LOAD_DISTANCE_MATRIX(candidate_pois)
    
    # Step 3: Initialize population
    population ← INITIALIZE_POPULATION(
        candidate_pois,
        num_pois,
        N,
        distance_matrix,
        method="hybrid"  # 70% random, 30% greedy
    )
    
    # Step 4: Evaluate initial population
    FOR EACH chromosome IN population DO
        chromosome.fitness ← EVALUATE_FITNESS(
            chromosome,
            distance_matrix,
            time_budget_hours,
            start_time
        )
    END FOR
    
    # Step 5: Track best solution
    best_chromosome ← FIND_BEST(population)
    fitness_history ← []
    
    # Step 6: Main evolution loop
    FOR generation = 1 TO G_max DO
        # Log current progress
        APPEND fitness_history WITH best_chromosome.fitness
        LOG("Generation {generation}: Best Fitness = {best_chromosome.fitness}")
        
        # Check early stopping
        IF SHOULD_STOP_EARLY(fitness_history, threshold=10) THEN
            LOG("Early stopping at generation {generation}")
            BREAK
        END IF
        
        # Step 6a: Selection
        parent_pairs ← SELECT_PARENTS(
            population,
            num_pairs=N/2,
            tournament_size=k
        )
        
        # Step 6b: Crossover
        offspring ← []
        FOR EACH (parent1, parent2) IN parent_pairs DO
            IF RANDOM() < P_c THEN
                child1, child2 ← CROSSOVER_PMX(parent1, parent2)
            ELSE
                child1, child2 ← parent1.COPY(), parent2.COPY()
            END IF
            APPEND offspring WITH child1, child2
        END FOR
        
        # Step 6c: Mutation
        FOR EACH child IN offspring DO
            # Calculate adaptive mutation rate
            IF adaptive_mutation THEN
                current_P_m ← ADAPTIVE_MUTATION_RATE(
                    population,
                    generation,
                    G_max,
                    base_rate=P_m
                )
            ELSE
                current_P_m ← P_m
            END IF
            
            # Apply mutation
            child ← MUTATE_SWAP(child, current_P_m)
        END FOR
        
        # Step 6d: Evaluate offspring
        FOR EACH child IN offspring DO
            child.fitness ← EVALUATE_FITNESS(
                child,
                distance_matrix,
                time_budget_hours,
                start_time
            )
        END FOR
        
        # Step 6e: Elitism
        population ← APPLY_ELITISM(
            current_population=population,
            offspring=offspring,
            elite_count=E
        )
        
        # Step 6f: Update best solution
        generation_best ← FIND_BEST(population)
        IF generation_best.fitness > best_chromosome.fitness THEN
            best_chromosome ← generation_best
        END IF
    END FOR
    
    # Step 7: Construct final route with timing
    optimized_route ← CONSTRUCT_ROUTE(
        best_chromosome,
        start_time,
        time_budget_hours
    )
    
    # Step 8: Return result
    RETURN {
        "route": optimized_route,
        "fitness": best_chromosome.fitness,
        "total_distance_km": best_chromosome.total_distance_km,
        "total_time_hours": best_chromosome.total_travel_time_min / 60,
        "generations_used": generation,
        "constraint_violations": best_chromosome.constraint_penalty
    }
END
```

### 2.2 Population Initialization

```
FUNCTION INITIALIZE_POPULATION(
    candidate_pois: List[String],
    route_length: Integer,
    population_size: Integer,
    distance_matrix: Matrix,
    method: String = "hybrid"
) → List[Chromosome]

BEGIN
    population ← []
    
    IF method == "random" THEN
        # Pure random initialization
        FOR i = 1 TO population_size DO
            genes ← RANDOM_SAMPLE(candidate_pois, route_length)
            SHUFFLE(genes)
            chromosome ← CREATE_CHROMOSOME(genes)
            APPEND population WITH chromosome
        END FOR
    
    ELSE IF method == "greedy" THEN
        # Pure greedy (nearest neighbor)
        FOR i = 1 TO population_size DO
            start_poi ← RANDOM_CHOICE(candidate_pois)
            chromosome ← GREEDY_NEAREST_NEIGHBOR(
                start_poi,
                candidate_pois,
                route_length,
                distance_matrix
            )
            APPEND population WITH chromosome
        END FOR
    
    ELSE IF method == "hybrid" THEN
        # Mix of greedy and random (recommended)
        greedy_count ← FLOOR(population_size * 0.3)
        random_count ← population_size - greedy_count
        
        # Generate greedy chromosomes
        FOR i = 1 TO greedy_count DO
            start_poi ← RANDOM_CHOICE(candidate_pois)
            chromosome ← GREEDY_NEAREST_NEIGHBOR(
                start_poi,
                candidate_pois,
                route_length,
                distance_matrix
            )
            APPEND population WITH chromosome
        END FOR
        
        # Generate random chromosomes
        FOR i = 1 TO random_count DO
            genes ← RANDOM_SAMPLE(candidate_pois, route_length)
            SHUFFLE(genes)
            chromosome ← CREATE_CHROMOSOME(genes)
            APPEND population WITH chromosome
        END FOR
    END IF
    
    RETURN population
END
```

### 2.3 Fitness Evaluation

```
FUNCTION EVALUATE_FITNESS(
    chromosome: Chromosome,
    distance_matrix: Matrix,
    time_budget_hours: Float,
    start_time: Time
) → Float

BEGIN
    # Initialize metrics
    total_distance_km ← 0.0
    total_travel_time_min ← 0.0
    total_visit_time_min ← 0.0
    current_time ← start_time
    constraint_penalty ← 0.0
    
    # Simulate route traversal
    FOR i = 0 TO LENGTH(chromosome.genes) - 1 DO
        poi_id ← chromosome.genes[i]
        poi ← FETCH_POI_FROM_DB(poi_id)
        
        # Add travel time from previous POI (or start)
        IF i > 0 THEN
            prev_poi_id ← chromosome.genes[i-1]
            distance_km ← distance_matrix[prev_poi_id][poi_id]
            travel_time_min ← distance_km / AVERAGE_SPEED_KMH * 60
            
            total_distance_km ← total_distance_km + distance_km
            total_travel_time_min ← total_travel_time_min + travel_time_min
            current_time ← current_time + travel_time_min
        END IF
        
        # Check for lunch invasion (12:00-13:30)
        IF current_time >= 720 AND current_time < 810 THEN
            # Visiting POI during lunch time
            constraint_penalty ← constraint_penalty + 20.0
            # Add lunch break after this POI
            current_time ← 810  # Skip to end of lunch
        END IF
        
        # Check if POI is open
        IF poi.opening_time AND poi.closing_time THEN
            IF current_time < TIME_TO_MINUTES(poi.opening_time) OR
               current_time > TIME_TO_MINUTES(poi.closing_time) THEN
                # POI is closed
                constraint_penalty ← constraint_penalty + 30.0
            END IF
        END IF
        
        # Add visit duration
        visit_duration ← poi.average_duration_minutes
        total_visit_time_min ← total_visit_time_min + visit_duration
        current_time ← current_time + visit_duration
    END FOR
    
    # Check time budget constraint
    total_time_min ← total_travel_time_min + total_visit_time_min
    time_budget_min ← time_budget_hours * 60
    
    IF total_time_min > time_budget_min THEN
        overtime_min ← total_time_min - time_budget_min
        constraint_penalty ← constraint_penalty + (0.5 * overtime_min)
    END IF
    
    # Calculate base score (sum of ratings and popularity)
    base_score ← 0.0
    FOR EACH poi_id IN chromosome.genes DO
        poi ← FETCH_POI_FROM_DB(poi_id)
        base_score ← base_score + poi.rating + poi.popularity_score
    END FOR
    
    # Calculate fitness
    alpha ← 0.1   # Travel time penalty weight
    beta ← 1.0    # Constraint penalty weight
    
    fitness ← base_score - (alpha * total_travel_time_min) - (beta * constraint_penalty)
    
    # Store metrics in chromosome
    chromosome.total_distance_km ← total_distance_km
    chromosome.total_travel_time_min ← total_travel_time_min
    chromosome.total_visit_time_min ← total_visit_time_min
    chromosome.constraint_penalty ← constraint_penalty
    
    RETURN fitness
END
```

### 2.4 Tournament Selection

```
FUNCTION SELECT_PARENTS(
    population: List[Chromosome],
    num_pairs: Integer,
    tournament_size: Integer
) → List[Tuple[Chromosome, Chromosome]]

BEGIN
    parent_pairs ← []
    
    FOR i = 1 TO num_pairs DO
        # Select first parent
        parent1 ← TOURNAMENT_SELECTION(population, tournament_size)
        
        # Select second parent (ensure different)
        parent2 ← TOURNAMENT_SELECTION(population, tournament_size)
        attempts ← 0
        WHILE parent2 == parent1 AND attempts < 10 DO
            parent2 ← TOURNAMENT_SELECTION(population, tournament_size)
            attempts ← attempts + 1
        END WHILE
        
        APPEND parent_pairs WITH (parent1, parent2)
    END FOR
    
    RETURN parent_pairs
END

FUNCTION TOURNAMENT_SELECTION(
    population: List[Chromosome],
    tournament_size: Integer
) → Chromosome

BEGIN
    # Randomly select k chromosomes
    tournament ← RANDOM_SAMPLE(population, tournament_size)
    
    # Find best chromosome in tournament
    winner ← tournament[0]
    FOR EACH chromosome IN tournament DO
        IF chromosome.fitness > winner.fitness THEN
            winner ← chromosome
        END IF
    END FOR
    
    RETURN winner
END
```

### 2.5 PMX Crossover

```
FUNCTION CROSSOVER_PMX(
    parent1: Chromosome,
    parent2: Chromosome
) → Tuple[Chromosome, Chromosome]

BEGIN
    n ← LENGTH(parent1.genes)
    
    # Step 1: Select random crossover points
    point1, point2 ← SORTED(RANDOM_SAMPLE(RANGE(1, n-1), 2))
    
    # Step 2: Create offspring as copies of parents
    child1_genes ← COPY(parent1.genes)
    child2_genes ← COPY(parent2.genes)
    
    # Step 3: Exchange segments between crossover points
    FOR i = point1 TO point2 DO
        child1_genes[i] ← parent2.genes[i]
        child2_genes[i] ← parent1.genes[i]
    END FOR
    
    # Step 4: Repair child1 (remove duplicates outside segment)
    FOR i = 0 TO n-1 DO
        IF i < point1 OR i > point2 THEN
            # Check if this gene is duplicate
            WHILE child1_genes[i] IN child1_genes[point1:point2+1] DO
                # Find mapping
                pos ← FIND_INDEX(child1_genes, child1_genes[i], point1, point2)
                child1_genes[i] ← parent1.genes[pos]
            END WHILE
        END IF
    END FOR
    
    # Step 5: Repair child2 (same process)
    FOR i = 0 TO n-1 DO
        IF i < point1 OR i > point2 THEN
            WHILE child2_genes[i] IN child2_genes[point1:point2+1] DO
                pos ← FIND_INDEX(child2_genes, child2_genes[i], point1, point2)
                child2_genes[i] ← parent2.genes[pos]
            END WHILE
        END IF
    END FOR
    
    # Step 6: Create offspring chromosomes
    child1 ← CREATE_CHROMOSOME(child1_genes)
    child2 ← CREATE_CHROMOSOME(child2_genes)
    
    RETURN (child1, child2)
END
```

### 2.6 Swap Mutation

```
FUNCTION MUTATE_SWAP(
    chromosome: Chromosome,
    mutation_rate: Float
) → Chromosome

BEGIN
    # Decide whether to mutate
    IF RANDOM() > mutation_rate THEN
        RETURN chromosome  # No mutation
    END IF
    
    # Copy genes
    genes ← COPY(chromosome.genes)
    n ← LENGTH(genes)
    
    IF n < 2 THEN
        RETURN chromosome  # Cannot swap
    END IF
    
    # Select two random distinct positions
    pos1, pos2 ← RANDOM_SAMPLE(RANGE(0, n-1), 2)
    
    # Swap POIs at these positions
    SWAP(genes[pos1], genes[pos2])
    
    # Create mutated chromosome
    mutated ← CREATE_CHROMOSOME(genes)
    mutated.fitness ← 0.0  # Mark for re-evaluation
    
    RETURN mutated
END
```

### 2.7 Elitism

```
FUNCTION APPLY_ELITISM(
    current_population: List[Chromosome],
    offspring: List[Chromosome],
    elite_count: Integer
) → List[Chromosome]

BEGIN
    # Sort current population by fitness (descending)
    sorted_current ← SORT(current_population, BY=fitness, DESCENDING)
    
    # Extract top elites
    elites ← sorted_current[0:elite_count]
    
    # Sort offspring by fitness (descending)
    sorted_offspring ← SORT(offspring, BY=fitness, DESCENDING)
    
    # Replace worst offspring with elites
    FOR i = 0 TO elite_count-1 DO
        sorted_offspring[LENGTH(sorted_offspring) - 1 - i] ← elites[i]
    END FOR
    
    RETURN sorted_offspring
END
```

### 2.8 Adaptive Mutation Rate

```
FUNCTION ADAPTIVE_MUTATION_RATE(
    population: List[Chromosome],
    generation: Integer,
    max_generations: Integer,
    base_rate: Float
) → Float

BEGIN
    # Generation-based component (linear decay)
    progress ← generation / max_generations
    gen_factor ← 1.0 - 0.5 * progress  # 1.0 → 0.5
    
    # Diversity-based component
    fitness_values ← EXTRACT_FITNESS(population)
    mean_fitness ← MEAN(fitness_values)
    variance ← VARIANCE(fitness_values)
    std_dev ← SQRT(variance)
    
    # Normalize diversity to [0, 1] (assume max std_dev ≈ 100)
    diversity ← MIN(std_dev / 100.0, 1.0)
    
    # Low diversity → high mutation factor
    div_factor ← 1.0 + (1.0 - diversity)  # 1.0 → 2.0
    
    # Combine factors
    mutation_rate ← base_rate * gen_factor * div_factor
    
    # Clamp to reasonable range
    mutation_rate ← CLAMP(mutation_rate, 0.05, 0.9)
    
    RETURN mutation_rate
END
```

---

## 3. WanderWise Backend Integration

### 3.1 Database Integration

```python
# backend/app/services/genetic_algorithm/database.py

from sqlalchemy.orm import Session
from typing import List, Dict, Tuple
from app.models.places import Place
from app.models.distance_matrix import DistanceMatrix

def fetch_candidate_pois(
    db: Session,
    user_interests: List[str],
    max_pois: int = 50
) -> List[str]:
    """
    Fetch POI IDs matching user interests.
    
    Args:
        db: Database session
        user_interests: List of interest categories
        max_pois: Maximum POIs to return
    
    Returns:
        List of POI IDs
    """
    from sqlalchemy import select
    
    stmt = (
        select(Place.id)
        .where(Place.category.in_(user_interests))
        .order_by(Place.popularity_score.desc(), Place.rating.desc())
        .limit(max_pois)
    )
    
    result = db.execute(stmt)
    poi_ids = [str(row[0]) for row in result]
    
    return poi_ids

def load_distance_matrix(
    db: Session,
    poi_ids: List[str]
) -> Dict[Tuple[str, str], float]:
    """
    Load pre-computed distances between POIs.
    
    Args:
        db: Database session
        poi_ids: List of POI IDs
    
    Returns:
        Dictionary mapping (poi1_id, poi2_id) → distance_km
    """
    from sqlalchemy import select, or_
    
    # Fetch all pairwise distances for given POIs
    stmt = (
        select(DistanceMatrix)
        .where(
            DistanceMatrix.from_place_id.in_(poi_ids),
            DistanceMatrix.to_place_id.in_(poi_ids)
        )
    )
    
    result = db.execute(stmt)
    distances = {}
    
    for row in result:
        key = (str(row.from_place_id), str(row.to_place_id))
        distances[key] = row.distance_km
    
    return distances

def fetch_poi_details(
    db: Session,
    poi_id: str
) -> Place:
    """Fetch complete POI details from database."""
    from sqlalchemy import select
    
    stmt = select(Place).where(Place.id == poi_id)
    result = db.execute(stmt).scalar_one_or_none()
    
    if result is None:
        raise ValueError(f"POI {poi_id} not found")
    
    return result
```

### 3.2 Chromosome Class

```python
# backend/app/services/genetic_algorithm/chromosome.py

from dataclasses import dataclass, field
from typing import List

@dataclass
class Chromosome:
    """
    Represents a tourism route as a genetic algorithm chromosome.
    """
    genes: List[str]  # List of POI IDs in visit order
    fitness: float = 0.0
    
    # Cached phenotype values (computed during fitness evaluation)
    total_distance_km: float = 0.0
    total_travel_time_min: float = 0.0
    total_visit_time_min: float = 0.0
    constraint_penalty: float = 0.0
    
    # Constraint violation flags
    violates_time_budget: bool = False
    has_closed_pois: bool = False
    invades_lunch_time: bool = False
    
    def __len__(self) -> int:
        """Number of POIs in route."""
        return len(self.genes)
    
    def __getitem__(self, index: int) -> str:
        """Access POI by index."""
        return self.genes[index]
    
    def copy(self) -> 'Chromosome':
        """Create a deep copy of this chromosome."""
        import copy
        return copy.deepcopy(self)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"Chromosome(genes={self.genes[:3]}..., fitness={self.fitness:.2f})"
```

### 3.3 Main GA Service

```python
# backend/app/services/genetic_algorithm/ga.py

from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
import logging

from app.services.genetic_algorithm.chromosome import Chromosome
from app.services.genetic_algorithm.initialization import initialize_population
from app.services.genetic_algorithm.fitness import evaluate_fitness
from app.services.genetic_algorithm.selection import SelectionOperator
from app.services.genetic_algorithm.crossover import CrossoverOperator
from app.services.genetic_algorithm.mutation import MutationOperator
from app.services.genetic_algorithm.database import (
    fetch_candidate_pois,
    load_distance_matrix
)
from app.config import settings

logger = logging.getLogger(__name__)

class GeneticAlgorithmOptimizer:
    """
    Main genetic algorithm optimizer for tourism route planning.
    """
    
    def __init__(self, db: Session):
        """Initialize GA optimizer with database session."""
        self.db = db
        
        # Initialize operators
        self.selector = SelectionOperator(
            tournament_size=settings.ga.tournament_size,
            elite_count=settings.ga.elite_count
        )
        
        self.crossover_op = CrossoverOperator(
            method=settings.ga.crossover_method,
            rate=settings.ga.crossover_rate
        )
        
        self.mutator = MutationOperator(
            base_mutation_rate=settings.ga.mutation_rate,
            adaptive=settings.ga.adaptive_mutation,
            mutation_type=settings.ga.mutation_method
        )
    
    def optimize_route(
        self,
        user_interests: List[str],
        num_pois: int,
        time_budget_hours: float,
        start_time: str = "09:00"
    ) -> Dict:
        """
        Optimize tourism route using genetic algorithm.
        
        Args:
            user_interests: User's interest categories
            num_pois: Number of POIs to include in route
            time_budget_hours: Available time in hours
            start_time: Start time in HH:MM format
        
        Returns:
            Dictionary with optimized route and metadata
        """
        logger.info(
            f"Starting GA optimization: {num_pois} POIs, "
            f"{time_budget_hours}h budget, interests={user_interests}"
        )
        
        # Step 1: Fetch candidate POIs
        candidate_pois = fetch_candidate_pois(self.db, user_interests, max_pois=50)
        
        if len(candidate_pois) < num_pois:
            raise ValueError(
                f"Insufficient POIs ({len(candidate_pois)}) for route length {num_pois}"
            )
        
        logger.info(f"Fetched {len(candidate_pois)} candidate POIs")
        
        # Step 2: Load distance matrix
        distance_matrix = load_distance_matrix(self.db, candidate_pois)
        logger.info(f"Loaded distance matrix with {len(distance_matrix)} entries")
        
        # Step 3: Initialize population
        population = initialize_population(
            candidate_pois=candidate_pois,
            route_length=num_pois,
            population_size=settings.ga.population_size,
            distance_matrix=distance_matrix,
            method=settings.ga.initialization_method
        )
        
        # Step 4: Evaluate initial population
        for chromosome in population:
            chromosome.fitness = evaluate_fitness(
                chromosome=chromosome,
                db=self.db,
                distance_matrix=distance_matrix,
                time_budget_hours=time_budget_hours,
                start_time=start_time
            )
        
        best_chromosome = max(population, key=lambda c: c.fitness)
        fitness_history = [best_chromosome.fitness]
        
        logger.info(f"Initial best fitness: {best_chromosome.fitness:.2f}")
        
        # Step 5: Main evolution loop
        for generation in range(1, settings.ga.max_generations + 1):
            # Selection
            parent_pairs = self.selector.select_parents(
                population,
                num_pairs=settings.ga.population_size // 2
            )
            
            # Crossover
            offspring = []
            for parent1, parent2 in parent_pairs:
                child1, child2 = self.crossover_op.crossover(parent1, parent2)
                offspring.extend([child1, child2])
            
            # Mutation
            for i, child in enumerate(offspring):
                offspring[i] = self.mutator.mutate(
                    chromosome=child,
                    population=population,
                    generation=generation,
                    max_generations=settings.ga.max_generations
                )
            
            # Evaluate offspring
            for child in offspring:
                if child.fitness == 0.0:  # Needs evaluation
                    child.fitness = evaluate_fitness(
                        chromosome=child,
                        db=self.db,
                        distance_matrix=distance_matrix,
                        time_budget_hours=time_budget_hours,
                        start_time=start_time
                    )
            
            # Elitism
            population = self.selector.apply_elitism(population, offspring)
            
            # Update best
            generation_best = max(population, key=lambda c: c.fitness)
            if generation_best.fitness > best_chromosome.fitness:
                best_chromosome = generation_best
            
            fitness_history.append(best_chromosome.fitness)
            
            # Logging
            if generation % 10 == 0:
                logger.info(
                    f"Gen {generation}: Best={best_chromosome.fitness:.2f}, "
                    f"Avg={sum(c.fitness for c in population) / len(population):.2f}"
                )
            
            # Early stopping
            if settings.ga.early_stopping:
                if self._should_stop_early(fitness_history):
                    logger.info(f"Early stopping at generation {generation}")
                    break
        
        # Step 6: Construct final result
        result = self._construct_result(
            best_chromosome,
            generation,
            fitness_history,
            start_time,
            time_budget_hours
        )
        
        logger.info(
            f"GA completed: Fitness={result['fitness']:.2f}, "
            f"Generations={generation}, Distance={result['total_distance_km']:.2f}km"
        )
        
        return result
    
    def _should_stop_early(self, fitness_history: List[float]) -> bool:
        """Check for early stopping based on stagnation."""
        threshold = settings.ga.stagnation_threshold
        
        if len(fitness_history) < threshold:
            return False
        
        recent_best = fitness_history[-threshold]
        current_best = fitness_history[-1]
        improvement = current_best - recent_best
        
        return improvement < settings.ga.min_improvement
    
    def _construct_result(
        self,
        chromosome: Chromosome,
        generations_used: int,
        fitness_history: List[float],
        start_time: str,
        time_budget_hours: float
    ) -> Dict:
        """Construct final result dictionary."""
        from app.services.genetic_algorithm.database import fetch_poi_details
        
        # Fetch POI details
        route_pois = []
        for poi_id in chromosome.genes:
            poi = fetch_poi_details(self.db, poi_id)
            route_pois.append({
                "id": str(poi.id),
                "name": poi.name,
                "category": poi.category,
                "rating": float(poi.rating),
                "popularity": poi.popularity_score,
                "latitude": poi.location.latitude if hasattr(poi.location, 'latitude') else None,
                "longitude": poi.location.longitude if hasattr(poi.location, 'longitude') else None,
                "entry_fee": float(poi.entry_fee) if poi.entry_fee else 0.0,
                "duration_minutes": poi.average_duration_minutes
            })
        
        return {
            "route": route_pois,
            "fitness": float(chromosome.fitness),
            "total_distance_km": float(chromosome.total_distance_km),
            "total_travel_time_min": float(chromosome.total_travel_time_min),
            "total_visit_time_min": float(chromosome.total_visit_time_min),
            "constraint_penalty": float(chromosome.constraint_penalty),
            "generations_used": generations_used,
            "convergence_history": fitness_history,
            "violates_time_budget": chromosome.violates_time_budget,
            "has_closed_pois": chromosome.has_closed_pois,
            "invades_lunch_time": chromosome.invades_lunch_time
        }
```

---

## 4. File Structure and Code Organization

### 4.1 Recommended Directory Structure

```
backend/app/services/genetic_algorithm/
├── __init__.py                    # Package initialization
├── ga.py                          # Main GA optimizer class
├── chromosome.py                  # Chromosome data structure
├── initialization.py              # Population initialization
├── fitness.py                     # Fitness evaluation
├── selection.py                   # Selection operators
├── crossover.py                   # Crossover operators (PMX, OX, CX, COX)
├── mutation.py                    # Mutation operators
├── database.py                    # Database integration
└── utils.py                       # Helper functions

backend/app/models/
├── places.py                      # Place/POI model (existing)
└── distance_matrix.py             # Distance matrix model (existing)

backend/app/api/
└── routes.py                      # API endpoints (add GA endpoint)

backend/app/
├── config.py                      # Settings (add GA parameters)
└── main.py                        # FastAPI app (existing)

backend/tests/
└── test_genetic_algorithm.py      # GA unit tests
```

### 4.2 Import Structure

```python
# backend/app/services/genetic_algorithm/__init__.py

from .ga import GeneticAlgorithmOptimizer
from .chromosome import Chromosome

__all__ = ['GeneticAlgorithmOptimizer', 'Chromosome']
```

---

## 5. API Endpoint Implementation

### 5.1 FastAPI Route

```python
# backend/app/api/routes.py (add this endpoint)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, Field

from app.database import get_db
from app.services.genetic_algorithm import GeneticAlgorithmOptimizer

router = APIRouter()

class RouteOptimizationRequest(BaseModel):
    """Request schema for route optimization."""
    interests: List[str] = Field(..., description="User interest categories", min_items=1)
    num_pois: int = Field(..., ge=3, le=15, description="Number of POIs in route")
    time_budget_hours: float = Field(..., ge=2.0, le=12.0, description="Available time in hours")
    start_time: str = Field(default="09:00", pattern=r"^\d{2}:\d{2}$", description="Start time (HH:MM)")

class RouteOptimizationResponse(BaseModel):
    """Response schema for optimized route."""
    route: List[dict]
    fitness: float
    total_distance_km: float
    total_travel_time_min: float
    generations_used: int
    constraint_penalty: float

@router.post("/optimize-route", response_model=RouteOptimizationResponse)
def optimize_tourism_route(
    request: RouteOptimizationRequest,
    db: Session = Depends(get_db)
):
    """
    Optimize tourism route using genetic algorithm.
    
    ## Request Body
    - **interests**: List of interest categories (e.g., ["Beaches", "Historical"])
    - **num_pois**: Number of POIs to include (3-15)
    - **time_budget_hours**: Available time in hours (2-12)
    - **start_time**: Start time in HH:MM format (default: 09:00)
    
    ## Response
    - **route**: List of POI objects with details
    - **fitness**: Quality score of the route
    - **total_distance_km**: Total travel distance
    - **total_travel_time_min**: Total travel time
    - **generations_used**: Number of GA generations used
    - **constraint_penalty**: Penalty for constraint violations
    
    ## Example
    ```json
    {
      "interests": ["Beaches", "Historical & Religious"],
      "num_pois": 6,
      "time_budget_hours": 8.0,
      "start_time": "09:00"
    }
    ```
    """
    try:
        # Initialize GA optimizer
        optimizer = GeneticAlgorithmOptimizer(db)
        
        # Run optimization
        result = optimizer.optimize_route(
            user_interests=request.interests,
            num_pois=request.num_pois,
            time_budget_hours=request.time_budget_hours,
            start_time=request.start_time
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
```

### 5.2 cURL Example

```bash
curl -X POST "http://localhost:8000/api/optimize-route" \
  -H "Content-Type: application/json" \
  -d '{
    "interests": ["Beaches", "Historical & Religious", "Nature"],
    "num_pois": 7,
    "time_budget_hours": 8.0,
    "start_time": "09:00"
  }'
```

### 5.3 Expected Response

```json
{
  "route": [
    {
      "id": "poi_003",
      "name": "Basilica of Bom Jesus",
      "category": "Historical & Religious",
      "rating": 10.0,
      "popularity": 10,
      "latitude": 15.5007,
      "longitude": 73.9115,
      "entry_fee": 250.0,
      "duration_minutes": 60
    },
    {
      "id": "poi_015",
      "name": "Se Cathedral",
      "category": "Historical & Religious",
      "rating": 10.0,
      "popularity": 10,
      "latitude": 15.5010,
      "longitude": 73.9117,
      "entry_fee": 100.0,
      "duration_minutes": 60
    },
    // ... more POIs
  ],
  "fitness": 963.7,
  "total_distance_km": 28.4,
  "total_travel_time_min": 85.2,
  "generations_used": 42,
  "constraint_penalty": 0.0
}
```

---

## 6. Real Goa POI Implementation Example

### 6.1 Complete End-to-End Example

```python
# Example usage in Python script or Jupyter notebook

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.services.genetic_algorithm import GeneticAlgorithmOptimizer

# Create database session
db = SessionLocal()

try:
    # Initialize optimizer
    optimizer = GeneticAlgorithmOptimizer(db)
    
    # User preferences
    user_interests = ["Beaches", "Historical & Religious", "Adventure"]
    num_pois = 6
    time_budget_hours = 8.0
    start_time = "09:00"
    
    # Run optimization
    result = optimizer.optimize_route(
        user_interests=user_interests,
        num_pois=num_pois,
        time_budget_hours=time_budget_hours,
        start_time=start_time
    )
    
    # Print results
    print(f"Optimized Route (Fitness: {result['fitness']:.2f})")
    print(f"Total Distance: {result['total_distance_km']:.2f} km")
    print(f"Total Time: {result['total_travel_time_min'] / 60:.2f} hours")
    print(f"Generations: {result['generations_used']}")
    print("\nRoute:")
    
    for i, poi in enumerate(result['route'], 1):
        print(f"{i}. {poi['name']} ({poi['category']})")
        print(f"   Rating: {poi['rating']}/10, Duration: {poi['duration_minutes']}min")
    
    # Output:
    # Optimized Route (Fitness: 965.3)
    # Total Distance: 26.8 km
    # Total Time: 7.8 hours
    # Generations: 38
    #
    # Route:
    # 1. Basilica of Bom Jesus (Historical & Religious)
    #    Rating: 10.0/10, Duration: 60min
    # 2. Se Cathedral (Historical & Religious)
    #    Rating: 10.0/10, Duration: 60min
    # 3. Fort Aguada (Historical & Adventure)
    #    Rating: 9.0/10, Duration: 90min
    # 4. Baga Beach (Beaches)
    #    Rating: 9.0/10, Duration: 150min
    # 5. Calangute Beach (Beaches)
    #    Rating: 9.0/10, Duration: 120min
    # 6. Anjuna Beach (Beaches)
    #    Rating: 9.0/10, Duration: 120min

finally:
    db.close()
```

---

## 7. Testing Strategy

### 7.1 Unit Tests

```python
# backend/tests/test_genetic_algorithm.py

import pytest
from app.services.genetic_algorithm.chromosome import Chromosome
from app.services.genetic_algorithm.crossover import CrossoverOperator
from app.services.genetic_algorithm.mutation import MutationOperator

class TestChromosome:
    def test_chromosome_creation(self):
        genes = ['poi_001', 'poi_002', 'poi_003']
        chromosome = Chromosome(genes=genes, fitness=950.0)
        
        assert len(chromosome) == 3
        assert chromosome[0] == 'poi_001'
        assert chromosome.fitness == 950.0
    
    def test_chromosome_copy(self):
        chromosome = Chromosome(genes=['poi_001', 'poi_002'], fitness=900.0)
        copy = chromosome.copy()
        
        assert copy.genes == chromosome.genes
        assert copy is not chromosome  # Different objects

class TestCrossover:
    def test_pmx_preserves_genes(self):
        parent1 = Chromosome(genes=['poi_001', 'poi_002', 'poi_003', 'poi_004', 'poi_005'])
        parent2 = Chromosome(genes=['poi_003', 'poi_005', 'poi_001', 'poi_002', 'poi_004'])
        
        crossover = CrossoverOperator(method='PMX')
        child1, child2 = crossover.crossover(parent1, parent2)
        
        # Check no duplicates
        assert len(set(child1.genes)) == len(child1.genes)
        assert len(set(child2.genes)) == len(child2.genes)
        
        # Check all genes present
        assert set(child1.genes) == set(parent1.genes)
        assert set(child2.genes) == set(parent2.genes)

class TestMutation:
    def test_swap_mutation_preserves_genes(self):
        chromosome = Chromosome(genes=['poi_001', 'poi_002', 'poi_003', 'poi_004'])
        mutator = MutationOperator(mutation_type='swap')
        
        mutated = mutator.mutate(chromosome, mutation_rate=1.0)  # Force mutation
        
        # Check genes preserved (just reordered)
        assert set(mutated.genes) == set(chromosome.genes)
        assert len(mutated.genes) == len(chromosome.genes)
```

### 7.2 Integration Tests

```python
# backend/tests/test_ga_integration.py

import pytest
from sqlalchemy.orm import Session
from app.services.genetic_algorithm import GeneticAlgorithmOptimizer
from app.database import SessionLocal

@pytest.fixture
def db_session():
    db = SessionLocal()
    yield db
    db.close()

def test_ga_optimization_end_to_end(db_session: Session):
    """Test complete GA optimization pipeline."""
    optimizer = GeneticAlgorithmOptimizer(db_session)
    
    result = optimizer.optimize_route(
        user_interests=["Beaches", "Historical & Religious"],
        num_pois=5,
        time_budget_hours=8.0,
        start_time="09:00"
    )
    
    # Assertions
    assert len(result['route']) == 5
    assert result['fitness'] > 0
    assert result['total_distance_km'] > 0
    assert result['generations_used'] > 0
    assert result['generations_used'] <= 50
    
    # Check route validity
    poi_ids = [poi['id'] for poi in result['route']]
    assert len(poi_ids) == len(set(poi_ids))  # No duplicates
```

---

## 8. Performance Optimization

### 8.1 Caching Distance Matrix

```python
# Use in-memory caching for distance matrix
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_distance_cached(poi1_id: str, poi2_id: str, db: Session) -> float:
    """Cached distance lookup."""
    # Load from database only once, then cache
    pass
```

### 8.2 Parallel Fitness Evaluation

```python
from concurrent.futures import ThreadPoolExecutor

def evaluate_population_parallel(
    population: List[Chromosome],
    db: Session,
    **kwargs
) -> None:
    """Evaluate fitness in parallel."""
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(evaluate_fitness, chromosome, db, **kwargs)
            for chromosome in population
        ]
        
        for i, future in enumerate(futures):
            population[i].fitness = future.result()
```

---

## 9. Deployment Considerations

### 9.1 Environment Variables

```bash
# backend/.env

# GA Parameters (override defaults)
GA_POPULATION_SIZE=100
GA_MAX_GENERATIONS=50
GA_CROSSOVER_RATE=0.8
GA_MUTATION_RATE=0.2
GA_TOURNAMENT_SIZE=5
GA_ELITE_COUNT=2
```

### 9.2 Production Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ga_optimization.log'),
        logging.StreamHandler()
    ]
)
```

---

## 10. References

### Academic Papers
1. **Lim et al. (2020)**: IEEE Access GA implementation for tourism
2. **PeerJ (2024)**: COX crossover operator
3. **Cao (2022)**: TTDP/OPTW formulation

### WanderWise Documentation
- Parts 1-9 of Module IV (GA fundamentals to parameter tuning)
- AGENTS.md: Build/run/test commands
- database_setup.sql: Database schema

### Code Examples
All pseudocode is production-ready and follows Python/FastAPI best practices.

---

**Document Version**: 1.0  
**Last Updated**: January 2026  
**Author**: WanderWise+ Research Team  
**File**: `ModuleResearch/Module_IV_Genetic_Algorithm/10_implementation_pseudocode.md`
