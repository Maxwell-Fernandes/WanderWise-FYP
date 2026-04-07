# Genetic Algorithm Notebook - Fixed Issues

## Problems Found

The `module4_genetic_algorithm.ipynb` notebook had several undefined functions that were referenced but never defined:

1. **`Individual` class** - Missing completely
2. **`initialize_population()`** - Missing completely  
3. **`tournament_selection()`** - Missing completely
4. **`swap_mutation()`** - Missing completely
5. **`optimize_route_ga()` return value** - Only returned `best_individual`, but callers expected `(best_individual, fitness_history)`
6. **Debug cell function names** - Used `order_crossover()` and `mutate()` instead of the correct `single_point_crossover()` and `swap_mutation()`

## Fixes Applied

### 1. Added Individual Class
```python
class Individual:
    """Represents a single route chromosome in the GA population."""
    def __init__(self, route, candidate_pois)
    def evaluate(self, start_time=TOUR_START_TIME)
    def copy(self)
    def __repr__(self)
```

### 2. Added Population Initialization
```python
def initialize_population(candidate_pois, population_size):
    """Initialize population with random routes of varying lengths."""
    # Creates random routes between MIN_POIS_PER_ROUTE and MAX_POIS_PER_ROUTE
    # Prefers high-WPI POIs (70% from top half, 30% from bottom half)
```

### 3. Added Tournament Selection
```python
def tournament_selection(population, tournament_size=TOURNAMENT_SIZE):
    """Select individual using tournament selection (TPOS spec: k=2)."""
```

### 4. Added Swap Mutation
```python
def swap_mutation(individual):
    """Swap mutation: randomly swap two POIs in the route (TPOS spec)."""
```

### 5. Fixed optimize_route_ga Return Value
Changed from:
```python
return best_individual
```

To:
```python
return best_individual, best_fitness_history
```

### 6. Fixed Debug Cell Function Names
- Replaced `order_crossover()` → `single_point_crossover()`
- Replaced `mutate()` → `swap_mutation()`

## Implementation Details

### Individual Class
- Stores route (list of POI objects)
- Stores reference to candidate_pois for crossover operations
- Caches fitness value and evaluation result
- Provides copy() method for creating offspring
- Integrates with existing `evaluate_fitness()` function

### Population Initialization
- Creates diverse initial population
- Ensures all routes meet minimum length (MIN_POIS_PER_ROUTE = 4)
- Biases toward high-value POIs but includes variety
- Respects maximum route length (MAX_POIS_PER_ROUTE = 15)

### Tournament Selection (TPOS Aligned)
- k=2 tournament size (TPOS specification)
- Selects best from random sample
- Provides selection pressure while maintaining diversity

### Swap Mutation (TPOS Aligned)
- 20% mutation rate (MUTATION_RATE = 0.2)
- Simple swap of two random positions
- Preserves POIs in route (no additions/deletions)
- Invalidates fitness after mutation for re-evaluation

## Verification

All fixes verified:
- ✅ Individual class defined
- ✅ initialize_population() defined
- ✅ tournament_selection() defined
- ✅ swap_mutation() defined
- ✅ optimize_route_ga() returns tuple (individual, history)
- ✅ No undefined function calls

## How to Run

The notebook should now run without undefined variable errors. Execute cells in order:

1. Setup and imports
2. Load data
3. Define POI class and functions
4. Run test optimization (single day)
5. Run full multi-day optimization (optional)

## Notes

- The notebook follows TPOS paper specifications for GA parameters
- Fitness function uses REWARD + PENALTY model: `fitness = poi_value_sum / (1 + delta)`
- OSRM integration for real-world travel times/distances
- Penalty values scaled for Goa data (different from Paris-calibrated TPOS values)
