# Module IV - Part 1: Genetic Algorithm Fundamentals

## Table of Contents
1. [Introduction to Genetic Algorithms](#introduction-to-genetic-algorithms)
2. [Biological Inspiration](#biological-inspiration)
3. [Core GA Components](#core-ga-components)
4. [GA Workflow](#ga-workflow)
5. [When to Use Genetic Algorithms](#when-to-use-genetic-algorithms)
6. [GA for Tourism Route Planning](#ga-for-tourism-route-planning)
7. [Advantages and Limitations](#advantages-and-limitations)
8. [Basic Example](#basic-example)
9. [References](#references)

---

## 1. Introduction to Genetic Algorithms

### 1.1 What is a Genetic Algorithm?

A **Genetic Algorithm (GA)** is a metaheuristic optimization technique inspired by the process of natural selection and evolution. GAs belong to the larger class of **evolutionary algorithms** and are used to find approximate solutions to optimization and search problems.

**Key Idea**: 
> Start with a population of candidate solutions, then iteratively improve them through processes mimicking biological evolution: selection, crossover (reproduction), and mutation.

### 1.2 Brief History

- **1960s**: John Holland at University of Michigan pioneers evolutionary computation
- **1975**: Holland publishes "Adaptation in Natural and Artificial Systems"
- **1989**: David Goldberg's "Genetic Algorithms in Search, Optimization, and Machine Learning" popularizes GAs
- **1990s-Present**: Wide adoption in engineering, scheduling, routing, machine learning

### 1.3 Why Genetic Algorithms?

Traditional optimization methods (gradient descent, linear programming) struggle with:
- **Non-differentiable** objective functions
- **Discrete** search spaces (e.g., route permutations)
- **Multi-modal** landscapes (many local optima)
- **NP-hard** problems (Traveling Salesman, job scheduling)

**GAs excel at**:
✅ Exploring large search spaces efficiently  
✅ Avoiding local optima through diversity maintenance  
✅ Finding "good enough" solutions quickly (not always optimal)  
✅ Handling complex constraints

---

## 2. Biological Inspiration

### 2.1 Natural Selection Principles

**Darwin's Theory of Evolution**:
1. **Variation**: Individuals in a population have different traits
2. **Inheritance**: Traits are passed from parents to offspring
3. **Selection**: Individuals with advantageous traits survive better
4. **Time**: Over generations, beneficial traits become more common

### 2.2 Mapping Biology to Computation

| Biological Concept | GA Equivalent | Tourism Route Planning |
|-------------------|---------------|------------------------|
| **Individual** | Candidate solution | A specific route through POIs |
| **Chromosome** | Encoded solution | List of POI IDs in order |
| **Gene** | Solution component | Single POI in the route |
| **Population** | Set of solutions | 100 different routes |
| **Fitness** | Quality measure | Route value - travel time - penalties |
| **Selection** | Choose parents | Pick best routes for breeding |
| **Crossover** | Recombination | Combine two routes to create new one |
| **Mutation** | Random change | Swap two POIs in a route |
| **Generation** | Iteration | One cycle of selection + crossover + mutation |

### 2.3 Evolution Process (Simplified)

```
Generation 1: [Random routes with varying quality]
    ↓ Selection (keep best routes)
Generation 2: [Slightly better routes]
    ↓ Crossover (combine good features)
    ↓ Mutation (introduce novelty)
Generation 3: [Even better routes]
    ↓ ... continue for N generations ...
Generation 50: [Highly optimized routes]
```

---

## 3. Core GA Components

### 3.1 Chromosome Representation

**Definition**: How we encode a candidate solution as data.

**For Tourism Routes**:
```python
# Chromosome: List of POI UUIDs
route = [
    'uuid-baga-beach',
    'uuid-basilica',
    'uuid-fort-aguada',
    'uuid-calangute'
]
```

**Requirements**:
- Must represent a complete solution
- Must be manipulable by genetic operators
- Should preserve validity after crossover/mutation

### 3.2 Fitness Function

**Definition**: Evaluates how good a solution is.

**For WanderWise+**:
```
fitness(route) = POI_value - travel_penalty - constraint_penalty
```

**Properties of Good Fitness Function**:
- ✅ **Quantitative**: Returns a number (higher = better)
- ✅ **Fast to compute**: Evaluated thousands of times
- ✅ **Differentiating**: Clearly distinguishes good from bad solutions
- ✅ **Smooth**: Small changes in solution → small changes in fitness (ideally)

### 3.3 Population

**Definition**: A set of candidate solutions maintained simultaneously.

**Typical Size**: 50-200 individuals
- **Too small** (< 20): Poor diversity, premature convergence
- **Too large** (> 500): Slow computation, diminishing returns

**WanderWise+ Setting**: Population = 100

**Population Types**:
- **Initial Population**: Randomly generated or seeded
- **Working Population**: Current generation being evaluated
- **Offspring Population**: Children created via crossover/mutation

### 3.4 Selection

**Definition**: Choose which individuals become parents for the next generation.

**Methods**:
1. **Roulette Wheel**: Probability proportional to fitness
2. **Tournament**: Pick K random, choose best (WanderWise uses this)
3. **Rank**: Based on rank order, not raw fitness
4. **Elitism**: Best N automatically survive

**Tournament Selection (K=5)**:
```python
def tournament_selection(population, k=5):
    tournament = random.sample(population, k)
    winner = max(tournament, key=lambda x: x.fitness)
    return winner
```

### 3.5 Crossover (Recombination)

**Definition**: Combine genetic material from two parents to create offspring.

**Why?**: Inherit good "building blocks" from multiple solutions.

**For Routes**: Use specialized permutation crossover
- PMX (Partially Mapped Crossover) - Recommended for WanderWise
- COX (Copy Order Crossover) - Novel method, best performance
- OX, CX - Alternatives

**Example** (simplified):
```
Parent1: [A, B, C, D, E]
Parent2: [C, A, E, B, D]
         ↓ Crossover
Child1:  [A, C, B, D, E]  (inherits structure from both)
```

### 3.6 Mutation

**Definition**: Randomly alter a chromosome to introduce novelty.

**Why?**: Prevent premature convergence, explore new areas.

**For Routes**: Swap mutation
```python
def swap_mutation(route, mutation_rate=0.2):
    if random.random() < mutation_rate:
        i, j = random.sample(range(len(route)), 2)
        route[i], route[j] = route[j], route[i]
    return route
```

**Example**:
```
Before: [Baga, Basilica, Fort, Calangute]
After:  [Baga, Fort, Basilica, Calangute]  (Basilica ↔ Fort swapped)
```

---

## 4. GA Workflow

### 4.1 Standard GA Algorithm

```
1. INITIALIZE population with random solutions
2. EVALUATE fitness of each individual
3. WHILE termination condition not met:
    a. SELECT parents from population
    b. CROSSOVER parents to create offspring
    c. MUTATE offspring with small probability
    d. EVALUATE fitness of offspring
    e. REPLACE old population with new generation
4. RETURN best solution found
```

### 4.2 Detailed Flowchart

```
┌─────────────────────────┐
│ Start                   │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ Initialize Population   │
│ (100 random routes)     │
└───────────┬─────────────┘
            ↓
┌─────────────────────────┐
│ Evaluate Fitness        │
│ (all 100 routes)        │
└───────────┬─────────────┘
            ↓
      ┌─────────────┐
      │ Generation  │←──────────┐
      │ Loop        │           │
      └──────┬──────┘           │
             ↓                  │
   ┌─────────────────────┐     │
   │ Selection           │     │
   │ (Tournament k=5)    │     │
   └──────┬──────────────┘     │
          ↓                    │
   ┌─────────────────────┐     │
   │ Crossover           │     │
   │ (PMX, rate=0.8)     │     │
   └──────┬──────────────┘     │
          ↓                    │
   ┌─────────────────────┐     │
   │ Mutation            │     │
   │ (Swap, rate=0.2)    │     │
   └──────┬──────────────┘     │
          ↓                    │
   ┌─────────────────────┐     │
   │ Evaluate Offspring  │     │
   └──────┬──────────────┘     │
          ↓                    │
   ┌─────────────────────┐     │
   │ Replace Population  │     │
   └──────┬──────────────┘     │
          ↓                    │
   ┌─────────────────────┐     │
   │ Check Termination   │     │
   │ (Max gen or         │     │
   │  convergence?)      │─No──┘
   └──────┬──────────────┘
          │ Yes
          ↓
   ┌─────────────────────┐
   │ Return Best Route   │
   └──────┬──────────────┘
          ↓
   ┌─────────────────────┐
   │ End                 │
   └─────────────────────┘
```

### 4.3 Generational vs Steady-State

**Generational GA** (WanderWise uses this):
- Replace entire population each generation
- Clear separation between generations
- Easier to implement

**Steady-State GA**:
- Replace only a few individuals each iteration
- Continuous evolution
- Can be more efficient

### 4.4 Termination Conditions

When to stop evolving:

1. **Maximum Generations**: Fixed limit (e.g., 50 generations)
2. **Convergence**: No fitness improvement for N generations
3. **Fitness Threshold**: Reached satisfactory quality
4. **Time Limit**: Computational budget exhausted
5. **Combination**: Multiple criteria (WanderWise uses max gen + convergence)

---

## 5. When to Use Genetic Algorithms

### 5.1 Ideal Use Cases

✅ **Combinatorial Optimization**
- Traveling Salesman Problem (TSP)
- Job Shop Scheduling
- Vehicle Routing
- **Tourism Itinerary Planning** ← WanderWise

✅ **Search Spaces with Properties**:
- Large (billions+ solutions)
- Discrete (not continuous)
- Multi-modal (many local optima)
- Black-box (no gradient information)

✅ **Constraint Handling**:
- Multiple competing objectives
- Complex constraint interactions
- Penalty-based fitness

### 5.2 When NOT to Use GAs

❌ **Simple Problems**: Linear programming works better  
❌ **Continuous Optimization**: Gradient descent is faster  
❌ **Need Guaranteed Optimal**: Use exact algorithms (if feasible)  
❌ **Real-time Requirements**: GAs can be slow  
❌ **No Fitness Function**: Can't evaluate solutions

### 5.3 Comparison with Other Methods

| Method | Speed | Quality | Guaranteed Optimal? | Best For |
|--------|-------|---------|-------------------|----------|
| **Exact (Dynamic Programming)** | Slow (O(2^n)) | Optimal | ✅ Yes | Small TSP (≤15 cities) |
| **Greedy Nearest Neighbor** | Fast (O(n²)) | Poor | ❌ No | Quick approximation |
| **Simulated Annealing** | Medium | Good | ❌ No | Single-solution search |
| **Genetic Algorithm** | Medium | Very Good | ❌ No | ✅ **Population-based, TTDP** |
| **OR-Tools (Google)** | Fast-Medium | Optimal* | ⚠️ Often | Production routing |

*OR-Tools uses sophisticated branch-and-bound, not always optimal for TTDP variant

---

## 6. GA for Tourism Route Planning

### 6.1 Why GA is Perfect for TTDP

**Tourism Trip Design Problem (TTDP)** characteristics:
- **Permutation-based**: Order matters (route sequence)
- **Multi-objective**: Maximize value, minimize travel, satisfy constraints
- **NP-hard**: No polynomial-time exact solution
- **Medium-sized**: 5-15 POIs per day (sweet spot for GA)

**GA Advantages**:
1. Handles permutations naturally (with right crossover)
2. Balances multiple objectives via fitness function
3. Explores many routes in parallel (population)
4. Finds very good solutions in reasonable time (30-50 generations)

### 6.2 TTDP vs Classic TSP

| Aspect | Classic TSP | TTDP (Tourism) |
|--------|-------------|----------------|
| **Objective** | Minimize distance | Maximize value - distance |
| **Node Weights** | All equal | POIs have ratings, popularity |
| **Constraints** | None (just visit all) | Opening hours, lunch, time budget |
| **Start/End** | Return to origin | May be open tour |
| **Solution Quality** | Distance only | Multifaceted fitness |

### 6.3 WanderWise+ GA Configuration

**Parameters** (based on IEEE Access 2020 research):
```python
GA_CONFIG = {
    'population_size': 100,
    'max_generations': 50,
    'crossover_method': 'pmx',  # or 'cox'
    'crossover_rate': 0.8,
    'mutation_method': 'swap',
    'mutation_rate': 0.2,
    'selection_method': 'tournament',
    'tournament_size': 5,
    'elitism_count': 2,  # Keep 2 best routes
}
```

**Why These Values?**
- **Pop=100**: Large enough for diversity, small enough to run fast
- **Gen=50**: Typically converges in 30-40 generations
- **Crossover=0.8**: High mixing, proven effective
- **Mutation=0.2**: Enough novelty without destroying good solutions
- **Tournament=5**: Balanced selection pressure

---

## 7. Advantages and Limitations

### 7.1 Advantages

✅ **No gradient needed**: Works on discrete, non-differentiable problems  
✅ **Global search**: Population explores multiple regions simultaneously  
✅ **Parallelizable**: Fitness evaluations can run in parallel  
✅ **Flexible**: Easy to add constraints, change objectives  
✅ **Robust**: Works across many problem types  
✅ **Interpretable**: Solutions are human-understandable routes

### 7.2 Limitations

❌ **No optimality guarantee**: May find local optimum  
❌ **Hyperparameter sensitive**: Needs tuning (pop size, rates)  
❌ **Computationally expensive**: Many fitness evaluations  
❌ **Premature convergence**: Can get stuck if not tuned well  
❌ **Fitness design critical**: Bad fitness → bad solutions  
❌ **Stochastic**: Different runs give different results

### 7.3 Mitigations for Limitations

**Problem**: Premature convergence  
**Solution**: Diversity maintenance (adaptive mutation, crowding)

**Problem**: Expensive fitness evaluation  
**Solution**: Caching, parallel evaluation, pre-computed distance matrix

**Problem**: Hyperparameter tuning  
**Solution**: Use proven values from literature (IEEE 2020 paper)

**Problem**: No optimality guarantee  
**Solution**: Compare with exact method on small instances, validate quality

---

## 8. Basic Example

### 8.1 Toy Problem: 5-City TSP

**Cities**: A, B, C, D, E  
**Distances** (symmetric):
```
   A  B  C  D  E
A  0  2  5  7  4
B  2  0  3  8  6
C  5  3  0  1  5
D  7  8  1  0  2
E  4  6  5  2  0
```

**Goal**: Find shortest route visiting all cities once.

### 8.2 GA Application

**Step 1: Initialize Population**
```python
population = [
    ['A', 'B', 'C', 'D', 'E'],  # Random route 1
    ['B', 'D', 'A', 'E', 'C'],  # Random route 2
    ['C', 'A', 'D', 'B', 'E'],  # Random route 3
    # ... 97 more random routes
]
```

**Step 2: Evaluate Fitness**
```python
def fitness(route):
    total_distance = sum(distance[route[i]][route[i+1]] for i in range(len(route)-1))
    return -total_distance  # Negative because we minimize distance

# Example:
# Route ['A', 'B', 'C', 'D', 'E']
# Distance: A→B(2) + B→C(3) + C→D(1) + D→E(2) = 8
# Fitness: -8
```

**Step 3: Selection** (Tournament, k=3)
```python
tournament = random.sample(population, 3)
# Tournament: [['A','B','C','D','E'], ['B','D','A','E','C'], ['C','A','D','B','E']]
# Fitness:    [-8,                    -18,                   -15]
parent1 = ['A', 'B', 'C', 'D', 'E']  # Best fitness in tournament
```

**Step 4: Crossover** (PMX)
```python
parent1 = ['A', 'B', 'C', 'D', 'E']
parent2 = ['C', 'A', 'D', 'B', 'E']
# After PMX crossover:
child = ['A', 'C', 'D', 'B', 'E']
```

**Step 5: Mutation** (Swap)
```python
# Before: ['A', 'C', 'D', 'B', 'E']
# Swap positions 1 and 3:
# After:  ['A', 'B', 'D', 'C', 'E']
```

**Step 6: Repeat** for 50 generations

**Expected Result**:
- Generation 1 avg fitness: -15
- Generation 25 avg fitness: -10
- Generation 50 best fitness: -7 (optimal route found)

### 8.3 Pseudocode

```python
def genetic_algorithm(problem, pop_size=100, max_gen=50):
    # Initialize
    population = initialize_random_population(pop_size)
    best_ever = None
    
    for generation in range(max_gen):
        # Evaluate
        fitness_scores = [fitness(individual) for individual in population]
        
        # Track best
        best_idx = max(range(len(fitness_scores)), key=lambda i: fitness_scores[i])
        if best_ever is None or fitness_scores[best_idx] > fitness(best_ever):
            best_ever = population[best_idx].copy()
        
        # Create next generation
        new_population = []
        
        # Elitism: keep top 2
        sorted_pop = sorted(zip(population, fitness_scores), key=lambda x: x[1], reverse=True)
        new_population.extend([ind for ind, _ in sorted_pop[:2]])
        
        # Fill rest with offspring
        while len(new_population) < pop_size:
            # Selection
            parent1 = tournament_selection(population, fitness_scores, k=5)
            parent2 = tournament_selection(population, fitness_scores, k=5)
            
            # Crossover
            if random.random() < 0.8:
                child1, child2 = pmx_crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()
            
            # Mutation
            child1 = swap_mutation(child1, rate=0.2)
            child2 = swap_mutation(child2, rate=0.2)
            
            new_population.extend([child1, child2])
        
        population = new_population[:pop_size]
        
        # Print progress
        print(f"Gen {generation}: Best fitness = {fitness(best_ever)}")
    
    return best_ever
```

---

## 9. References

### Foundational Papers

1. **Holland, J. H. (1975)**. "Adaptation in Natural and Artificial Systems"
   - Original GA framework

2. **Goldberg, D. E. (1989)**. "Genetic Algorithms in Search, Optimization, and Machine Learning"
   - Popularized GAs, still definitive textbook

3. **Whitley, D. (1994)**. "A Genetic Algorithm Tutorial"
   - Excellent introductory tutorial
   - Statistics and Computing, 4(2), 65-85

### Tourism-Specific Applications

4. **IEEE Access 2020**: Vanessa Echeverría et al.
   - "Improving Itinerary Recommendations for Tourists Through Metaheuristic Algorithms"
   - DOI: 10.1109/ACCESS.2020.2990348
   - **Direct application to WanderWise**

5. **PeerJ 2024**: Şehab & Turan
   - Novel COX crossover method
   - 43.89% improvement reported

### WanderWise+ Implementation

- **File**: `backend/app/services/genetic_algorithm.py`
- **Related Docs**:
  - Module IV Part 4: Fitness Function
  - Module IV Part 6: Crossover Comparison
  - Module IV Part 7: Mutation Strategies

---

**Document Version**: 1.0  
**Last Updated**: January 2026  
**Author**: WanderWise+ Research Team  
**Status**: Educational Foundation
