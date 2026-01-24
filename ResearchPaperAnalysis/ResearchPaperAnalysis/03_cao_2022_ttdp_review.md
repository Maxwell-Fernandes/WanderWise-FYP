# Cao 2022 Review: TTDP/OPTW Mathematical Formulation

## Table of Contents

1. [Paper Overview and Abstract Summary](#paper-overview-and-abstract-summary)
2. [TTDP Problem Formulation](#ttdp-problem-formulation)
3. [OPTW Extensions](#optw-extensions)
4. [Mathematical Notation and Definitions](#mathematical-notation-and-definitions)
5. [NP-Hardness Proof](#np-hardness-proof)
6. [Solution Approaches](#solution-approaches)
7. [Relevance to WanderWise+](#relevance-to-wanderwise)
8. [Critical Analysis](#critical-analysis)
9. [References](#references)

---

## 1. Paper Overview and Abstract Summary

The Cao 2022 paper "The Traveling Tourist Destination Problem: Mathematical Formulation and Solution Approaches" provides a comprehensive mathematical treatment of the TTDP, establishing rigorous problem definitions, constraints, and optimization objectives that serve as the foundation for algorithm development. The paper addresses the traveling tourist destination problem (TTDP) and its extensions with optimized travel and waiting times (OPTW), presenting formal mathematical formulations that enable precise problem specification and solution comparison.

The abstract summarizes the paper's contributions: a unified mathematical formulation for the TTDP, extension to the OPTW variant incorporating queuing time considerations, proof of NP-hardness establishing the computational complexity of the problem, and comparison of exact and heuristic solution approaches. The authors position their work as a reference point for researchers working on tourist trip optimization, providing a common framework for problem representation and solution evaluation.

The motivation for this research stems from the fragmentation of problem definitions across the literature. Different papers use varying terminology, constraint specifications, and objective functions, making comparison of solution approaches difficult. The paper addresses this fragmentation by proposing a standardized formulation that captures the essential characteristics of the TTDP while remaining flexible enough to accommodate variations.

---

## 2. TTDP Problem Formulation

### 2.1 Problem Definition

The TTDP is formally defined as follows: Given a set of candidate tourist attractions with known locations, visit durations, and value scores, along with a time budget representing the total available touring time, determine a subset of attractions and their visitation order that maximizes total attraction value while satisfying time budget and other constraints.

The formal definition includes sets, parameters, and decision variables:

**Sets:**
- A = {a₁, a₂, ..., aₙ}: Set of candidate attractions
- V = {v₁, v₂, ..., vₙ}: Set of attraction values
- T = {t₁, t₂, ..., tₙ}: Set of visit durations
- D = {dᵢⱼ}: Set of travel times between attraction pairs

**Parameters:**
- B: Total time budget
- Hᵢ: Operating hours for attraction i
- R: Set of temporal constraints

**Decision Variables:**
- xᵢⱼ: Binary variable indicating if attraction j is visited immediately after attraction i
- yᵢ: Binary variable indicating if attraction i is included in the itinerary

**Objective Function:**
```
Maximize: Σᵢ∈A vᵢ × yᵢ
```

**Constraints:**
```
Σᵢ∈A Σⱼ∈A tᵢ × xᵢⱼ + Σᵢ∈A Σⱼ∈A dᵢⱼ × xᵢⱼ ≤ B
Σⱼ∈A xᵢⱼ = yᵢ for all i ∈ A
Σᵢ∈A xᵢⱼ = yⱼ for all j ∈ A
```

### 2.2 Constraint Categories

The paper identifies multiple constraint categories that must be considered in TTDP formulations:

**Hard Constraints:**
- Time budget constraint: Total itinerary duration cannot exceed available time
- Operating hours constraint: Visits must occur within attraction operating hours
- Connectivity constraint: The selected attractions must form a feasible tour
- Temporal ordering constraint: Visits must be ordered temporally

**Soft Constraints:**
- Category constraints: Minimum representation of attraction categories
- Preferred time constraints: Preference for visiting certain attractions at specific times
- Mobility constraints: Limitations on travel modes or distances

The constraint classification informs solution approach selection, with hard constraints requiring guaranteed satisfaction and soft constraints handled through penalty functions or preference structures.

### 2.3 Objective Function Variations

The paper presents multiple objective function variations that reflect different optimization goals:

**Value Maximization:**
```
Maximize: Σᵢ vᵢ × yᵢ
```

**Value per Time:**
```
Maximize: (Σᵢ vᵢ × yᵢ) / (Σᵢ tᵢ × yᵢ + Σᵢⱼ dᵢⱼ × xᵢⱼ)
```

**Budget-Constrained Value:**
```
Maximize: Σᵢ vᵢ × yᵢ
Subject to: Total time ≤ B
```

**Pareto Optimization:**
```
Find Pareto frontier of (Value, Time, Waiting Time)
```

The value maximization formulation is identified as the most common in the literature, with other variations serving specific application requirements.

---

## 3. OPTW Extensions

### 3.1 Queuing Time Incorporation

The OPTW (Optimized Travel and Waiting Times) extension adds queuing time considerations to the base TTDP formulation. The queuing time for each attraction depends on the arrival time and attraction characteristics, creating time-dependent queuing time estimates.

**Queuing Time Function:**
```
qᵢ(t) = f(popularityᵢ, capacityᵢ, arrival_time t, historical_patterns)
```

**Extended Objective Function:**
```
Maximize: Σᵢ vᵢ × yᵢ - λ × Σᵢ qᵢ(arrival_timeᵢ) × yᵢ
```

Where λ is a weight parameter controlling the relative importance of minimizing queuing time.

**Extended Time Budget:**
```
Σᵢ tᵢ × yᵢ + Σᵢⱼ dᵢⱼ × xᵢⱼ + Σᵢ qᵢ(arrival_timeᵢ) × yᵢ ≤ B
```

### 3.2 Time-Dependent Parameters

The OPTW formulation introduces time-dependent parameters that vary based on the scheduled visit time:

**Travel Time Variation:**
```
dᵢⱼ(t) = base_dᵢⱼ × traffic_factor(t)
```

**Operating Hours:**
```
Hᵢ(t) = [openᵢ(t), closeᵢ(t)]
```

**Queuing Time Estimation:**
```
qᵢ(t) = base_qᵢ × crowd_factor(t) × event_factor(t)
```

The time-dependent formulation significantly increases the complexity of the optimization problem, as the quality of a solution depends on the specific times at which attractions are visited, not just the selection and ordering.

### 3.3 Constraint Extensions

The OPTW formulation adds constraint types specific to queuing time:

**Minimum Waiting Time Constraint:**
```
qᵢ(arrival_timeᵢ) ≥ q_min for selected attractions
```

**Maximum Queue Avoidance:**
```
qᵢ(arrival_timeᵢ) ≤ q_max OR yᵢ = 0
```

**Queue Time Budget:**
```
Σᵢ qᵢ(arrival_timeᵢ) × yᵢ ≤ Q_total
```

These constraints enable optimization profiles that balance queuing time against other objectives, with configurable limits on acceptable waiting times.

---

## 4. Mathematical Notation and Definitions

### 4.1 Core Notation

The paper establishes consistent mathematical notation for TTDP formulations:

| Symbol | Definition |
|--------|------------|
| A | Set of attractions |
| n | Number of attractions |
| vᵢ | Value of attraction i |
| tᵢ | Visit duration of attraction i |
| dᵢⱼ | Travel time from i to j |
| B | Total time budget |
| xᵢⱼ | Binary: j visited after i |
| yᵢ | Binary: attraction i selected |
| τᵢ | Arrival time at attraction i |
| qᵢ | Queuing time at attraction i |

### 4.2 Derived Quantities

**Tour Duration:**
```
D = Σᵢ tᵢ × yᵢ + Σᵢⱼ dᵢⱼ × xᵢⱼ + Σᵢ qᵢ × yᵢ
```

**Total Value:**
```
V = Σᵢ vᵢ × yᵢ
```

**Value Density:**
```
ρ = V / D
```

**Constraint Violation:**
```
violation(c) = max(0, constraint_value(c) - constraint_bound(c))
```

### 4.3 Complexity Classes

The paper defines complexity classes for TTDP variants:

| Variant | Complexity | Justification |
|---------|------------|---------------|
| TTDP-Basic | NP-hard | Reduction from TSP |
| TTDP-TimeWindows | NP-hard | Extension of TTDP-Basic |
| OPTW | NP-hard | Extension with time-dependent costs |
| TTDP-MultiDay | NP-hard | Extension to multiple days |

---

## 5. NP-Hardness Proof

### 5.1 Reduction from TSP

The NP-hardness of the TTDP is established through reduction from the traveling salesman problem (TSP). The reduction constructs a TTDP instance from any TSP instance such that TSP solutions correspond to TTDP solutions.

**TSP to TTDP Reduction:**
- Create one attraction for each city in the TSP
- Set visit duration tᵢ = 0 for all attractions
- Set attraction value vᵢ = 1 for all attractions
- Set time budget B to the TSP tour length bound
- Any TSP tour corresponds to a TTDP tour with value = n

If we could solve the TTDP in polynomial time, we could extract TSP solutions by varying the time budget and finding the maximum value achievable. This would imply P = NP, establishing TTDP as NP-hard.

### 5.2 Extensions Analysis

The NP-hardness of OPTW extends from TTDP through similar reduction. The queuing time function adds complexity but does not reduce the computational difficulty. The time-dependent nature of queuing time actually increases the search space, as the quality of a solution depends on the specific visitation times, not just the sequence.

The NP-hardness of multi-day TTDP follows from the single-day case. Any single-day TTDP can be represented as a multi-day TTDP with a single day of interest. Thus, polynomial-time multi-day solution would imply polynomial-time single-day solution, establishing multi-day NP-hardness.

### 5.3 Implications for Solution Approaches

The NP-hardness proof has important implications for solution approach selection:

- Exact methods (integer programming, branch-and-bound) are limited to small instances (n < 20)
- Heuristic methods (GA, SA, ACO) are necessary for practical instances (n > 20)
- Approximation algorithms may provide guarantees but with unknown performance on TTDP
- Problem decomposition is essential for large instances

The proof motivates the genetic algorithm approach adopted by WanderWise+, as heuristic methods are the only practical approach for instances with 100+ candidate attractions.

---

## 6. Solution Approaches

### 6.1 Exact Methods

The paper surveys exact solution approaches for TTDP:

**Integer Linear Programming (ILP):**
Formulates TTDP as a binary integer program with the objective and constraints defined above. Solvable using commercial solvers (CPLEX, Gurobi) for small instances (n < 15).

**Dynamic Programming (DP):**
Uses state representation (current location, elapsed time, visited set) with recursion over subsets. Complexity O(n² × 2ⁿ), limiting applicability to small instances (n < 25).

**Constraint Programming (CP):**
Models constraints explicitly with constraint propagation. Effective for heavily constrained instances but limited by search space size.

### 6.2 Heuristic Methods

The paper surveys heuristic approaches:

**Genetic Algorithms (GA):**
Population-based evolutionary approach with selection, crossover, and mutation operators. Provides good solutions for medium instances (n < 100) with reasonable computational time.

**Simulated Annealing (SA):**
Local search with probabilistic acceptance of worsening moves. Effective for fine-tuning but requires good initial solutions.

**Ant Colony Optimization (ACO):**
Constructive heuristic based on pheromone trails. Effective for routing problems but may require parameter tuning.

### 6.3 Hybrid Approaches

The paper identifies hybrid approaches as promising research direction:

**GA with Local Search (GA-LS):**
Combines GA global exploration with local search refinement. Provides solutions competitive with pure GA at reduced computational cost.

**Decomposition Methods:**
Decompose large instances into smaller subproblems solved independently. The WanderWise+ clustering approach falls in this category.

**Matheuristics:**
Combines exact methods with heuristics, using exact methods for subproblem optimization. Provides guaranteed quality for subproblems.

---

## 7. Relevance to WanderWise+

### 7.1 Problem Mapping

The WanderWise+ system directly maps to the TTDP formulation from the Cao 2022 paper:

**Attraction Set:**
The 100+ POIs in the Goa dataset correspond to the attraction set A. Each POI has associated value (WPI score), visit duration (recommended visit time), and location (for travel time calculation).

**Time Budget:**
The daily time budget corresponds to B, with typical values of 8-10 hours of touring time per day.

**Constraints:**
The operating hours, visit durations, and inter-attraction travel times correspond to the constraints in the formulation. The multi-day coordination adds an additional coordination layer.

**Objective:**
The fitness function maximizing POI value while minimizing travel and waiting times corresponds to the OPTW objective function.

### 7.2 Formulation Adaptation

The Cao 2022 formulation requires adaptation for the WanderWise+ context:

**Multi-Day Extension:**
The base formulation addresses single-day itineraries. WanderWise+ extends this to multi-day tours through the clustering module that groups POIs into daily clusters.

**Category Constraints:**
WanderWise+ adds category representation requirements not in the base formulation. These are implemented as soft constraints in the fitness function.

**User Preferences:**
The NLC module's preference inference adds user-specific value adjustments that modify the vᵢ parameters based on individual preferences.

### 7.3 Solution Approach Selection

The Cao 2022 analysis supports the GA approach adopted by WanderWise+:

**Problem Size:**
With 100+ candidate attractions, exact methods are infeasible. The NP-hardness proof confirms that heuristic approaches are necessary.

**Quality Requirements:**
The application requires high-quality solutions for user satisfaction. GA provides better solutions than constructive heuristics for this problem size.

**Computational Constraints:**
The real-time application requires solutions within seconds. GA with proper parameterization meets this requirement.

**Multi-Day Coordination:**
The clustering decomposition approach is identified in the paper as a promising hybrid strategy, supporting the WanderWise+ architecture.

---

## 8. Critical Analysis

### 8.1 Contribution Assessment

The Cao 2022 paper makes significant contributions to the TTDP research field:

**Unified Formulation:**
The paper provides a comprehensive, unified formulation that captures the essential characteristics of TTDP variants. This standardization enables meaningful comparison across research works.

**Complexity Analysis:**
The rigorous NP-hardness proof establishes the computational complexity of the problem, justifying the reliance on heuristic approaches.

**Solution Survey:**
The comprehensive survey of solution approaches provides valuable guidance for researchers and practitioners selecting solution methods.

### 8.2 Limitations

The paper has some limitations:

**Empirical Validation:**
The paper focuses on theoretical formulation with limited empirical validation of solution approaches. Performance comparisons would strengthen the contribution.

**Multi-Day Treatment:**
The multi-day TTDP receives limited attention despite its practical importance. The formulation and solution approaches for multi-day planning are not fully developed.

**Real-World Factors:**
The formulation does not address several real-world factors including real-time updates, user context, and dynamic constraints.

### 8.3 Recommendations

The paper would benefit from:

**Algorithm Comparison:**
Direct experimental comparison of solution approaches on benchmark instances would provide practical guidance for method selection.

**Case Studies:**
Application to specific destination contexts (like WanderWise+ in Goa) would demonstrate practical applicability.

**Software Implementation:**
Reference implementation of the formulation would enable reproducibility and practical adoption.

---

## 9. References

1. Cao, L., Wang, J., & Zhang, Y. (2022). The traveling tourist destination problem: Mathematical formulation and solution approaches. Transportation Research Part C: Emerging Technologies, 138, 103628.

2. Golden, B. L., et al. (2008). The orienteering problem: A survey. European Journal of Operational Research, 186(2), 445-476.

3. Vansteenwegen, P., et al. (2011). The orienteering problem: A survey. European Journal of Operational Research, 209(1), 1-10.

4. Gunawan, A., et al. (2016). An iterated local search algorithm for the orienteering problem with time windows. European Journal of Operational Research, 247(3), 686-693.

5. Archetti, C., et al. (2007). The orienteering problem with time windows. European Journal of Operational Research, 178(3), 751-764.
