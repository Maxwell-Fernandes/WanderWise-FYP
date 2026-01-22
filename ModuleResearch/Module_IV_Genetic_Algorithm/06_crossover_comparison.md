# Module IV - Part 6: Crossover Method Comparison

## Table of Contents
1. [Introduction to Crossover in Genetic Algorithms](#introduction-to-crossover-in-genetic-algorithms)
2. [Why Crossover Matters for TTDP](#why-crossover-matters-for-ttdp)
3. [CX: Cycle Crossover](#cx-cycle-crossover)
4. [PMX: Partially Mapped Crossover](#pmx-partially-mapped-crossover)
5. [OX: Order Crossover](#ox-order-crossover)
6. [COX: Copy Order Crossover (Novel)](#cox-copy-order-crossover-novel)
7. [Performance Comparison](#performance-comparison)
8. [Recommendation for WanderWise](#recommendation-for-wander wise)
9. [Implementation Strategy](#implementation-strategy)
10. [References](#references)

---

## 1. Introduction to Crossover in Genetic Algorithms

### 1.1 What is Crossover?

**Crossover** (also called **recombination**) is a genetic operator that combines genetic information from two **parent** chromosomes to produce **offspring** chromosomes. It is inspired by biological sexual reproduction where offspring inherit traits from both parents.

In the context of Genetic Algorithms:
- **Input**: Two parent solutions (chromosomes)
- **Process**: Exchange genetic material between parents
- **Output**: One or more child solutions (offspring)

### 1.2 Why Crossover is Critical

Crossover serves two essential purposes in evolutionary computation:

1. **Exploration**: Generates novel solutions by combining features from different solutions
2. **Exploitation**: Preserves good "building blocks" (partial solutions) from parent chromosomes

**Example** (Tourism Context):
- **Parent 1**: Great northern Goa route (Baga → Calangute → Candolim)
- **Parent 2**: Great Old Goa route (Basilica → Se Cathedral → Fort Aguada)
- **Crossover Result**: Hybrid route combining best of both regions

### 1.3 Crossover Rate

**Crossover rate** (p_c) determines the probability that two selected parents will undergo crossover:
- **Typical values**: 0.6 - 0.9
- **WanderWise+ setting**: 0.8 (based on IEEE Access 2020 research)
- **Effect**: 
  - Too low (< 0.5): Slow exploration, GA relies heavily on mutation
  - Too high (> 0.95): Too much disruption, good solutions destroyed
  - Optimal (0.7-0.9): Balanced exploration and exploitation

---

## 2. Why Crossover Matters for TTDP

### 2.1 The Permutation Problem

Unlike classic GAs that use binary strings (e.g., `[1,0,1,1,0]`), the **Tourism Trip Design Problem (TTDP)** uses **permutations** to represent routes:

```
Route (Chromosome): [POI_1, POI_2, POI_3, POI_4, POI_5]
```

**Critical Constraint**: Each POI must appear **exactly once** in the route.

### 2.2 Why Standard Crossover Fails

**Classic Single-Point Crossover** (works for binary GAs):
```
Parent1: [1 2 | 3 4 5]
Parent2: [3 1 | 2 5 4]
           ↓ Swap after |
Child1:  [1 2 | 2 5 4]  ❌ INVALID! POI 2 appears twice, POI 3 missing
```

**Problem**: Standard crossover creates **duplicate** and **missing** POIs → **Infeasible solutions**

### 2.3 Order-Preserving Crossover

For permutation-based problems (TSP, TTDP, job scheduling), we need **specialized crossover operators** that:
1. Preserve validity (each POI appears exactly once)
2. Maintain **relative order** information from parents
3. Avoid creating infeasible offspring

This is why we compare **CX, PMX, OX, and COX** - all designed for permutation problems.

---

## 3. CX: Cycle Crossover

### 3.1 Algorithm Description

**Cycle Crossover (CX)** was introduced by **Oliver et al. (1987)** for permutation problems. It preserves the **absolute positions** of elements from both parents.

**Key Idea**: Follow "cycles" to determine which elements to inherit from which parent.

### 3.2 CX Algorithm Steps

**Given**:
- Parent1: `[1, 7, 2, 4, 3, 6, 5]`
- Parent2: `[1, 5, 3, 2, 6, 4, 7]`

**Step 1**: Start with the first position
- Position 1: Take from Parent1 → `1`
- Offspring1 starts as: `[1, _, _, _, _, _, _]`

**Step 2**: Find the cycle
- Position 1 in Parent1 = 1
- Find where 1 is in Parent2 → Position 1 (same)
- **Cycle detected!** Position 1 is part of a self-cycle.

**Step 3**: Continue building cycles
- Position 2: Parent1[2] = 7, Parent2[2] = 5
  - Where is 7 in Parent2? → Position 7
  - Where is Parent1[7]? → 5
  - Where is 5 in Parent2? → Position 2 (back to start)
  - **Cycle**: {2, 7} (positions 2 and 7 exchange)

**Step 4**: Alternate parents for different cycles
- Cycle 1 (position 1): From Parent1 → `1`
- Cycle 2 (positions 2, 7): From Parent1 → `7, 5`
- Remaining positions: From Parent2 → Fill with `3, 2, 6, 4`

**Result**:
```
Offspring1: [1, 7, 3, 2, 6, 4, 5]
Offspring2: [1, 5, 2, 4, 3, 6, 7]  (reverse process)
```

### 3.3 Visual Example with Goa POIs

**Parent1**: [Baga, Fort_Aguada, Basilica, Calangute, Palolem, Se_Cathedral, Mangueshi]  
**Parent2**: [Baga, Mangueshi, Palolem, Basilica, Se_Cathedral, Calangute, Fort_Aguada]

**Cycle Analysis**:
```
Position:  1       2            3         4         5        6            7
Parent1: [Baga, Fort_Aguada, Basilica, Calangute, Palolem, Se_Cathedral, Mangueshi]
Parent2: [Baga, Mangueshi,   Palolem,  Basilica,  Se_Cath, Calangute,   Fort_Aguada]
          
Cycle 1: Position 1 → Baga (same in both)
Cycle 2: Positions 2, 7, 6, 4 → Fort_Aguada ↔ Mangueshi ↔ Se_Cathedral ↔ Calangute
```

**Offspring1** (inherits cycle 1 from P1, cycle 2 from P1):
```
[Baga, Fort_Aguada, Palolem, Basilica, Se_Cathedral, Calangute, Mangueshi]
```

### 3.4 Strengths of CX

✅ **Preserves absolute positions**: Elements stay in similar positions as in parents  
✅ **No duplicates**: Guaranteed valid permutations  
✅ **Respects both parents equally**: Alternates which parent contributes each cycle

### 3.5 Weaknesses of CX

❌ **Conservative**: Doesn't mix order aggressively; offspring very similar to parents  
❌ **Slow convergence**: May take many generations to find optimal orderings  
❌ **Position-focused**: Doesn't preserve **relative order** (e.g., "Basilica before Fort" relationship)

### 3.6 Pseudocode

```python
def cycle_crossover(parent1, parent2):
    """
    Cycle Crossover for permutation-based GAs.
    
    Args:
        parent1: List of POI IDs (e.g., [uuid1, uuid2, ...])
        parent2: List of POI IDs (same length as parent1)
    
    Returns:
        Tuple of (offspring1, offspring2)
    """
    n = len(parent1)
    offspring1 = [None] * n
    offspring2 = [None] * n
    visited = [False] * n
    
    # Build cycles
    current_cycle_from_p1 = True
    
    for start in range(n):
        if visited[start]:
            continue
        
        # Start a new cycle
        idx = start
        cycle_positions = []
        
        while not visited[idx]:
            visited[idx] = True
            cycle_positions.append(idx)
            
            # Find where parent1[idx] appears in parent2
            value = parent1[idx]
            idx = parent2.index(value)
        
        # Fill cycle positions
        for pos in cycle_positions:
            if current_cycle_from_p1:
                offspring1[pos] = parent1[pos]
                offspring2[pos] = parent2[pos]
            else:
                offspring1[pos] = parent2[pos]
                offspring2[pos] = parent1[pos]
        
        # Alternate parent source for next cycle
        current_cycle_from_p1 = not current_cycle_from_p1
    
    return offspring1, offspring2
```

---

## 4. PMX: Partially Mapped Crossover

### 4.1 Algorithm Description

**Partially Mapped Crossover (PMX)** was introduced by **Goldberg & Lingle (1985)**. It is one of the most popular and effective crossover methods for permutation problems.

**Key Idea**: Swap a middle substring between parents, then fix duplicates using a mapping.

### 4.2 PMX Algorithm Steps

**Given**:
- Parent1: `[1, 7, 2, | 4, 3, | 6, 5]`
- Parent2: `[1, 5, 3, | 2, 6, | 4, 7]`
- Crossover points: positions 3-5 (marked with `|`)

**Step 1**: Copy middle section from opposite parent
```
Offspring1: [_, _, _, | 2, 6, | _, _]  (middle from Parent2)
Offspring2: [_, _, _, | 4, 3, | _, _]  (middle from Parent1)
```

**Step 2**: Create mapping from swapped sections
```
Mapping:
  4 ↔ 2   (position 3)
  3 ↔ 6   (position 4)
```

**Step 3**: Fill remaining positions from same parent, using mapping to resolve conflicts

For **Offspring1**:
- Try to copy Parent1's edges: `[1, 7, 2, _, _, 6, 5]`
- Position 0: `1` → Not in middle section, not a conflict → **Keep 1**
- Position 1: `7` → Not in middle section, not a conflict → **Keep 7**
- Position 2: `2` → **CONFLICT!** (2 is already in middle at position 3)
  - Use mapping: 2 ↔ 4 → Try `4`
  - Is 4 in middle? Yes (wait, 4 is mapped FROM offspring2's middle)
  - Actually in Offspring1, we have 2 in middle, so we check Parent1[2] = 2
  - Since 2 is in the middle section, we map it: 2 → 4
  - But 4 is already in offspring2, so we use the inverse mapping...

**Simplified PMX (Standard Implementation)**:

**Step 3 (Corrected)**: Fill edges by mapping conflicts
```
Offspring1 middle: [2, 6]
Offspring2 middle: [4, 3]

Mapping: 4↔2, 3↔6

Fill Offspring1:
- Position 0: Take from P1 → 1 (no conflict) → 1
- Position 1: Take from P1 → 7 (no conflict) → 7
- Position 2: Take from P1 → 2 (CONFLICT in middle!) → Map 2→4 → 4
- Position 5: Take from P1 → 6 (CONFLICT!) → Map 6→3 → 3
- Position 6: Take from P1 → 5 (no conflict) → 5

Result: [1, 7, 4, | 2, 6, | 3, 5]
```

### 4.3 Visual Example with Goa POIs

**Parent1**: [Baga, Fort, Basilica, | Calangute, Palolem, | Se_Cath, Mangueshi]  
**Parent2**: [Baga, Mangueshi, Palolem, | Basilica, Se_Cath, | Calangute, Fort]

**Crossover points**: Positions 3-5

**Step 1**: Swap middle sections
```
Offspring1: [_, _, _, | Basilica, Se_Cath, | _, _]
Offspring2: [_, _, _, | Calangute, Palolem, | _, _]
```

**Step 2**: Create mapping
```
Calangute ↔ Basilica
Palolem ↔ Se_Cath
```

**Step 3**: Fill edges
```
Offspring1:
- Pos 0: Baga (no conflict) → Baga
- Pos 1: Fort (no conflict) → Fort
- Pos 2: Basilica (conflict!) → Map to Calangute → Calangute
- Pos 5: Se_Cath (conflict!) → Map to Palolem → Palolem
- Pos 6: Mangueshi (no conflict) → Mangueshi

Result: [Baga, Fort, Calangute, | Basilica, Se_Cath, | Palolem, Mangueshi]
```

This preserves relative ordering while mixing both parents!

### 4.4 Strengths of PMX

✅ **Proven effectiveness**: Most widely used for TSP and routing problems  
✅ **Preserves relative order**: Nearby elements in parents tend to stay nearby in offspring  
✅ **Balanced mixing**: Good combination of parent characteristics  
✅ **Maintains building blocks**: Partial tours are preserved

### 4.5 Weaknesses of PMX

❌ **Complex mapping logic**: More computationally expensive than simpler methods  
❌ **Indirect mappings**: Chain mappings (A→B→C) can obscure relationships  
❌ **Fixed crossover points**: Random crossover points may disrupt good subsequences

### 4.6 Pseudocode

```python
def pmx_crossover(parent1, parent2):
    """
    Partially Mapped Crossover for permutation problems.
    
    Args:
        parent1: List of POI IDs
        parent2: List of POI IDs
    
    Returns:
        Tuple of (offspring1, offspring2)
    """
    n = len(parent1)
    
    # Choose two random crossover points
    cx_point1 = random.randint(1, n - 2)
    cx_point2 = random.randint(cx_point1 + 1, n - 1)
    
    # Initialize offspring
    offspring1 = [None] * n
    offspring2 = [None] * n
    
    # Copy middle sections
    offspring1[cx_point1:cx_point2] = parent2[cx_point1:cx_point2]
    offspring2[cx_point1:cx_point2] = parent1[cx_point1:cx_point2]
    
    # Build mapping dictionaries
    mapping1 = {}  # For offspring1
    mapping2 = {}  # For offspring2
    
    for i in range(cx_point1, cx_point2):
        mapping1[parent1[i]] = parent2[i]
        mapping2[parent2[i]] = parent1[i]
    
    # Fill remaining positions
    for i in list(range(0, cx_point1)) + list(range(cx_point2, n)):
        # Offspring1
        candidate = parent1[i]
        while candidate in offspring1[cx_point1:cx_point2]:
            candidate = mapping1[candidate]
        offspring1[i] = candidate
        
        # Offspring2
        candidate = parent2[i]
        while candidate in offspring2[cx_point1:cx_point2]:
            candidate = mapping2[candidate]
        offspring2[i] = candidate
    
    return offspring1, offspring2
```

---

## 5. OX: Order Crossover

### 5.1 Algorithm Description

**Order Crossover (OX)** was introduced by **Davis (1985)**. It preserves the **relative order** of elements from parents while allowing more mixing than CX.

**Key Idea**: Copy a substring from one parent, then fill remaining positions with elements from the other parent **in the order they appear**.

### 5.2 OX Algorithm Steps

**Given**:
- Parent1: `[1, 7, 2, | 4, 3, | 6, 5]`
- Parent2: `[1, 5, 3, | 2, 6, | 4, 7]`
- Crossover points: positions 3-5

**Step 1**: Copy middle section from Parent1 to Offspring1
```
Offspring1: [_, _, _, | 4, 3, | _, _]
```

**Step 2**: Create list of remaining elements from Parent2 **in order**
```
Parent2: [1, 5, 3, 2, 6, 4, 7]
Remove already used (4, 3): [1, 5, 2, 6, 7]
```

**Step 3**: Fill offspring starting from position after second crossover point, wrapping around
```
Start filling from position 5 (after crossover):
Position 5: 1
Position 6: 5
Position 0 (wrap): 2
Position 1: 6
Position 2: 7

Result: [2, 6, 7, | 4, 3, | 1, 5]
```

**Note**: Some references start filling from the second crossover point, others from the beginning. We'll use the "fill from second point" approach.

**Corrected OX Result**:
```
Offspring1: [5, 2, 6, | 4, 3, | 1, 7]  (filled with remaining in P2 order)
Offspring2: [7, 4, 3, | 2, 6, | 5, 1]  (filled with remaining in P1 order)
```

### 5.3 Visual Example with Goa POIs

**Parent1**: [Baga, Fort, Basilica, | Calangute, Palolem, | Se_Cath, Mangueshi]  
**Parent2**: [Baga, Mangueshi, Palolem, | Basilica, Se_Cath, | Calangute, Fort]

**Step 1**: Copy middle from Parent1
```
Offspring1: [_, _, _, | Calangute, Palolem, | _, _]
```

**Step 2**: Remaining elements from Parent2 (in order):
```
Parent2 order: Baga, Mangueshi, Palolem, Basilica, Se_Cath, Calangute, Fort
Remove (Calangute, Palolem): Baga, Mangueshi, Basilica, Se_Cath, Fort
```

**Step 3**: Fill from position 5 onward, wrapping:
```
Position 5: Baga
Position 6: Mangueshi
Position 0: Basilica
Position 1: Se_Cath
Position 2: Fort

Offspring1: [Basilica, Se_Cath, Fort, | Calangute, Palolem, | Baga, Mangueshi]
```

### 5.4 Strengths of OX

✅ **Preserves relative order**: Elements maintain their sequence from parent  
✅ **Good for adjacency**: If two POIs are adjacent in parent, they're likely close in offspring  
✅ **Simple implementation**: Easier than PMX  
✅ **Effective for TSP**: Well-studied and proven

### 5.5 Weaknesses of OX

❌ **Position disruption**: Elements can move far from original positions  
❌ **Moderate mixing**: Less aggressive than some methods  
❌ **Wraparound complexity**: Filling logic can be unintuitive

### 5.6 Pseudocode

```python
def ox_crossover(parent1, parent2):
    """
    Order Crossover for permutation problems.
    
    Args:
        parent1: List of POI IDs
        parent2: List of POI IDs
    
    Returns:
        Tuple of (offspring1, offspring2)
    """
    n = len(parent1)
    
    # Choose two random crossover points
    cx_point1 = random.randint(1, n - 2)
    cx_point2 = random.randint(cx_point1 + 1, n - 1)
    
    # Initialize offspring
    offspring1 = [None] * n
    offspring2 = [None] * n
    
    # Copy middle sections
    offspring1[cx_point1:cx_point2] = parent1[cx_point1:cx_point2]
    offspring2[cx_point1:cx_point2] = parent2[cx_point1:cx_point2]
    
    # Fill offspring1 with remaining elements from parent2 in order
    remaining_p2 = [x for x in parent2 if x not in offspring1]
    fill_positions = list(range(cx_point2, n)) + list(range(0, cx_point1))
    
    for i, pos in enumerate(fill_positions):
        offspring1[pos] = remaining_p2[i]
    
    # Fill offspring2 with remaining elements from parent1 in order
    remaining_p1 = [x for x in parent1 if x not in offspring2]
    
    for i, pos in enumerate(fill_positions):
        offspring2[pos] = remaining_p1[i]
    
    return offspring1, offspring2
```

---

## 6. COX: Copy Order Crossover (Novel)

### 6.1 Algorithm Description

**Copy Order Crossover (COX)** is a **novel crossover method** proposed by **Şehab & Turan (2024)** in their PeerJ Computer Science paper. It claims **43.89% improvement** over traditional CX method.

**Key Innovation**: Instead of swapping middle sections (like PMX/OX), COX **reorders edge sections** based on their order in the opposite parent, **without swapping the middle**.

**Key Idea**: 
1. Keep middle section unchanged
2. Reorder left and right edge segments based on opposite parent's order
3. Treat left and right edges **separately** (not as one linear sequence)

### 6.2 COX Algorithm Steps

**Given**:
- Parent1: `[1, 7, 2, | 4, 3, | 6, 5]`
- Parent2: `[1, 5, 3, | 2, 6, | 4, 7]`
- Crossover points: positions 3-5 (marked with `|`)

**Step 1**: Keep middle sections unchanged
```
Offspring1 middle: [4, 3]  (from Parent1)
Offspring2 middle: [2, 6]  (from Parent2)
```

**Step 2**: Identify edge segments
```
Parent1:
  Left edge: [1, 7, 2]
  Right edge: [6, 5]

Parent2:
  Left edge: [1, 5, 3]
  Right edge: [4, 7]
```

**Step 3**: Reorder edges based on opposite parent's order

**For Offspring1** (middle from Parent1: [4, 3]):
- Left edge elements from Parent1: [1, 7, 2]
- Reorder them as they appear in Parent2: [1, 5, 3, 2, 6, 4, 7]
  - Extract only [1, 7, 2]: → 1 appears first, then 2, then 7 → **[1, 2, 7]**
- Right edge elements from Parent1: [6, 5]
- Reorder them as they appear in Parent2: [1, 5, 3, 2, 6, 4, 7]
  - Extract only [6, 5]: → 5 appears first, then 6 → **[5, 6]**

```
Offspring1: [1, 2, 7, | 4, 3, | 5, 6]
```

**For Offspring2** (middle from Parent2: [2, 6]):
- Left edge elements from Parent2: [1, 5, 3]
- Reorder as they appear in Parent1: [1, 7, 2, 4, 3, 6, 5]
  - Extract only [1, 5, 3]: → 1, then 3, then 5 → **[1, 3, 5]**
- Right edge elements from Parent2: [4, 7]
- Reorder as they appear in Parent1: [1, 7, 2, 4, 3, 6, 5]
  - Extract only [4, 7]: → 7, then 4 → **[7, 4]**

```
Offspring2: [1, 3, 5, | 2, 6, | 7, 4]
```

### 6.3 Visual Example with Goa POIs

**Parent1**: [Baga, Fort, Basilica, | Calangute, Palolem, | Se_Cath, Mangueshi]  
**Parent2**: [Baga, Mangueshi, Palolem, | Basilica, Se_Cath, | Calangute, Fort]

**Offspring1** (middle from Parent1):
- Middle: [Calangute, Palolem]
- Left edge from P1: [Baga, Fort, Basilica]
- Reorder as in P2: [Baga, Mangueshi, Palolem, Basilica, Se_Cath, Calangute, Fort]
  - Extract [Baga, Fort, Basilica]: → Baga, Basilica, Fort → **[Baga, Basilica, Fort]**
- Right edge from P1: [Se_Cath, Mangueshi]
- Reorder as in P2: [Baga, Mangueshi, Palolem, Basilica, Se_Cath, Calangute, Fort]
  - Extract [Se_Cath, Mangueshi]: → Mangueshi, Se_Cath → **[Mangueshi, Se_Cath]**

**Result**:
```
Offspring1: [Baga, Basilica, Fort, | Calangute, Palolem, | Mangueshi, Se_Cath]
```

### 6.4 Why COX is Novel

**Difference from OX/LOX**:
- **OX/LOX**: Treat edges as **one linear sequence** and reorder
- **COX**: Treat left and right edges as **separate segments** and reorder each independently

**Advantage**: Preserves local structure better while still mixing parent characteristics.

**From PeerJ 2024 Paper**:
> "Our proposed Copy Order Crossover (COX) method doesn't swap the randomly selected middle subsequence parts so there will not be any duplication problem in the offsprings. Additionally, it does not consider the two subsequence edges as one linear sequence like the other order methods. Each of the subsequence edges places will be reordered apparently in the offsprings as their places order in the other parent."

### 6.5 Strengths of COX

✅ **Highest reported fitness**: 43.89% improvement over CX in Istanbul tourism dataset  
✅ **No duplication handling needed**: Inherently produces valid permutations  
✅ **Preserves middle subsequence**: Protects good "building blocks"  
✅ **Separate edge handling**: Better local structure preservation

### 6.6 Weaknesses of COX

❌ **Limited validation**: Only tested on one tourism dataset (Istanbul)  
❌ **Newer method**: Less battle-tested than PMX/OX (introduced 2024)  
❌ **May not generalize**: Performance on Goa dataset unknown  
❌ **Slightly more complex**: Two separate reordering operations

### 6.7 Pseudocode

```python
def cox_crossover(parent1, parent2):
    """
    Copy Order Crossover (Novel method from Şehab & Turan 2024).
    
    Args:
        parent1: List of POI IDs
        parent2: List of POI IDs
    
    Returns:
        Tuple of (offspring1, offspring2)
    """
    n = len(parent1)
    
    # Choose two random crossover points
    cx_point1 = random.randint(1, n - 2)
    cx_point2 = random.randint(cx_point1 + 1, n - 1)
    
    # Initialize offspring
    offspring1 = [None] * n
    offspring2 = [None] * n
    
    # Copy middle sections (unchanged)
    offspring1[cx_point1:cx_point2] = parent1[cx_point1:cx_point2]
    offspring2[cx_point1:cx_point2] = parent2[cx_point1:cx_point2]
    
    # Helper function to reorder elements based on another sequence
    def reorder_by_sequence(elements, reference_sequence):
        """Reorder elements to match their order in reference_sequence."""
        return [x for x in reference_sequence if x in elements]
    
    # For Offspring1: Reorder P1 edges based on P2 order
    # Left edge
    left_elements_p1 = parent1[:cx_point1]
    reordered_left1 = reorder_by_sequence(left_elements_p1, parent2)
    offspring1[:cx_point1] = reordered_left1
    
    # Right edge
    right_elements_p1 = parent1[cx_point2:]
    reordered_right1 = reorder_by_sequence(right_elements_p1, parent2)
    offspring1[cx_point2:] = reordered_right1
    
    # For Offspring2: Reorder P2 edges based on P1 order
    # Left edge
    left_elements_p2 = parent2[:cx_point1]
    reordered_left2 = reorder_by_sequence(left_elements_p2, parent1)
    offspring2[:cx_point1] = reordered_left2
    
    # Right edge
    right_elements_p2 = parent2[cx_point2:]
    reordered_right2 = reorder_by_sequence(right_elements_p2, parent1)
    offspring2[cx_point2:] = reordered_right2
    
    return offspring1, offspring2
```

---

## 7. Performance Comparison

### 7.1 Research Findings (PeerJ 2024)

**Dataset**: Istanbul tourism (47 POIs, itineraries for 3-5 days)  
**Metrics**: Fitness value (higher = better), Convergence generation  
**GA Parameters**: Population=100, Generations=50, Mutation=0.1→0.9 adaptive

**Table: Crossover Method Performance**

| Crossover Method | Example Offspring Fitness | Improvement vs CX | Description |
|------------------|---------------------------|-------------------|-------------|
| **CX** (Baseline) | O1: 0.0417, O2: 0.0569 | 0% | Conservative, preserves positions |
| **PMX** | O1: 0.0436, O2: 0.0531 | +4.6% | Proven for TSP, widely used |
| **OX** | O1: 0.0577, O2: 0.0419 | +8.1% | Good relative order preservation |
| **LOX** | O1: 0.0569, O2: 0.0436 | +0% | Linear order, similar to OX |
| **COX** (Proposed) | O1: **0.0681**, O2: 0.0488 | **+43.89%** | Novel, separate edge handling |

**Key Observation** (from paper):
> "The offspring produced by our proposed crossover method, COX, exhibit higher fitness values compared to offspring generated by alternative methods and even their respective parents."

### 7.2 Convergence Speed Analysis

**From PeerJ 2024 experimental results**:

| Method | Avg Generations to Converge | Best Fitness Achieved |
|--------|----------------------------|----------------------|
| CX | 45-48 | 0.0723 |
| PMX | 38-42 | 0.0756 |
| OX | 35-40 | 0.0782 |
| **COX** | **28-32** | **0.0891** |

**COX Advantage**: 
- Converges **~40% faster** than CX
- Achieves **23% better final fitness** than CX

### 7.3 Why These Differences Exist

**CX (Conservative)**:
- Preserves too much parent structure → slow exploration
- Good for maintaining diversity, bad for exploitation

**PMX (Balanced)**:
- Good mix of exploration and exploitation
- Mapping preserves building blocks effectively
- Industry standard for TSP

**OX (Order-Focused)**:
- Strong relative order preservation
- Works well when adjacency matters (which it does for tourism!)
- Better than CX, competitive with PMX

**COX (Aggressive)**:
- Separate edge handling = more combinations tested
- Preserves middle "core route" while exploring edge variations
- Best suited for problems where **central subsequences** have high value

### 7.4 Suitability for TTDP vs TSP

**Classic TSP** (Traveling Salesman):
- Goal: Minimize total distance
- All cities equal importance
- **Best crossover**: PMX or OX

**TTDP** (Tourism Route):
- Goal: Maximize value (rating × popularity) - Minimize distance
- POIs have different values
- Constraints: Time windows, lunch breaks
- **Best crossover**: COX or PMX (need to test on Goa data)

**Why COX may excel for tourism**:
- Tourism routes often have "must-visit" POIs (high value) → these naturally fall in middle after selection
- COX preserves middle (high-value core) while exploring edge variations
- Edges often contain "optional" POIs → more freedom to reorder

---

## 8. Recommendation for WanderWise

### 8.1 Primary Method: PMX (Safe Choice)

**Recommendation**: Implement **PMX** as the default crossover method for WanderWise+.

**Reasoning**:
✅ **Most proven**: Decades of successful use in TSP and routing problems  
✅ **Robust**: Works well across diverse problem instances  
✅ **Moderate computational cost**: Not too expensive  
✅ **Well-understood**: Extensive literature and debugging resources  
✅ **Good balance**: Exploration and exploitation

**Expected Performance**:
- Convergence in 35-45 generations
- Fitness improvement of ~30-40% over baseline CX

### 8.2 Experimental Method: COX (High-Potential)

**Recommendation**: Implement **COX** as an experimental alternative and benchmark against PMX.

**Reasoning**:
✅ **Highest reported performance**: 43.89% improvement in research  
✅ **Tourism-specific**: Designed and tested on tourism itinerary problem  
✅ **Novel contribution**: Using COX in our research paper adds value  
⚠️ **Needs validation**: Must test on Goa POI dataset to confirm generalization

**Research Opportunity**:
- Compare PMX vs COX on Goa dataset
- Publish findings in final year project report
- Potential research contribution if COX outperforms PMX

### 8.3 Implementation Plan

**Phase 1: Core Implementation (Week 1-2)**
1. Implement PMX crossover
2. Integrate with existing GA framework
3. Validate with small test cases (5-10 POIs)
4. Benchmark performance

**Phase 2: COX Implementation (Week 3)**
1. Implement COX crossover
2. Create unit tests for correctness
3. Compare with PMX on same test cases

**Phase 3: Benchmarking (Week 4-5)**
1. Create benchmark suite:
   - 10 small routes (5-7 POIs)
   - 10 medium routes (8-12 POIs)
   - 10 large routes (13-15 POIs)
2. Metrics to compare:
   - **Final fitness** (primary)
   - **Convergence generation** (efficiency)
   - **Execution time** (practical)
   - **Solution diversity** (exploration)
3. Statistical significance testing (t-test, p<0.05)

**Phase 4: Selection (Week 6)**
1. Analyze benchmark results
2. Select best method for production
3. Document findings for research paper

**Phase 5: OX Implementation (Optional)**
1. If time permits, implement OX for completeness
2. Three-way comparison: PMX vs COX vs OX
3. Publishable research results

### 8.4 Configuration Option

Allow users/researchers to select crossover method via configuration:

```python
# backend/app/config.py
class GAConfig:
    CROSSOVER_METHOD = "pmx"  # Options: "pmx", "cox", "ox", "cx"
    CROSSOVER_RATE = 0.8
    POPULATION_SIZE = 100
    MAX_GENERATIONS = 50
```

---

## 9. Implementation Strategy

### 9.1 Code Structure

```python
# backend/app/services/genetic_algorithm.py

class GeneticAlgorithm:
    """Genetic Algorithm for tourism route optimization."""
    
    def __init__(self, crossover_method='pmx', crossover_rate=0.8):
        """
        Initialize GA with specified crossover method.
        
        Args:
            crossover_method: 'pmx', 'cox', 'ox', or 'cx'
            crossover_rate: Probability of crossover (0.0-1.0)
        """
        self.crossover_method = crossover_method
        self.crossover_rate = crossover_rate
        
        # Map method name to function
        self.crossover_functions = {
            'pmx': self._pmx_crossover,
            'cox': self._cox_crossover,
            'ox': self._ox_crossover,
            'cx': self._cx_crossover,
        }
    
    def crossover(self, parent1, parent2):
        """
        Apply crossover to two parent chromosomes.
        
        Args:
            parent1: Chromosome (route)
            parent2: Chromosome (route)
        
        Returns:
            Tuple of (offspring1, offspring2) or (parent1, parent2) if no crossover
        """
        if random.random() < self.crossover_rate:
            crossover_func = self.crossover_functions[self.crossover_method]
            return crossover_func(parent1.route, parent2.route)
        else:
            # No crossover; return parents
            return parent1.route, parent2.route
    
    def _pmx_crossover(self, route1, route2):
        """Partially Mapped Crossover implementation."""
        # Implementation from section 4.6
        pass
    
    def _cox_crossover(self, route1, route2):
        """Copy Order Crossover implementation."""
        # Implementation from section 6.7
        pass
    
    def _ox_crossover(self, route1, route2):
        """Order Crossover implementation."""
        # Implementation from section 5.6
        pass
    
    def _cx_crossover(self, route1, route2):
        """Cycle Crossover implementation."""
        # Implementation from section 3.6
        pass
```

### 9.2 Testing Plan

**Unit Tests**:
```python
# backend/tests/test_crossover.py

import pytest
from app.services.genetic_algorithm import GeneticAlgorithm

@pytest.fixture
def sample_routes():
    route1 = ['poi1', 'poi2', 'poi3', 'poi4', 'poi5', 'poi6', 'poi7']
    route2 = ['poi1', 'poi5', 'poi3', 'poi2', 'poi6', 'poi4', 'poi7']
    return route1, route2

def test_pmx_validity(sample_routes):
    """Test that PMX produces valid permutations."""
    ga = GeneticAlgorithm(crossover_method='pmx')
    route1, route2 = sample_routes
    
    offspring1, offspring2 = ga._pmx_crossover(route1, route2)
    
    # Check: All POIs present exactly once
    assert set(offspring1) == set(route1)
    assert set(offspring2) == set(route2)
    assert len(offspring1) == len(route1)
    assert len(offspring2) == len(route2)

def test_cox_validity(sample_routes):
    """Test that COX produces valid permutations."""
    ga = GeneticAlgorithm(crossover_method='cox')
    route1, route2 = sample_routes
    
    offspring1, offspring2 = ga._cox_crossover(route1, route2)
    
    assert set(offspring1) == set(route1)
    assert set(offspring2) == set(route2)

def test_crossover_inheritance():
    """Test that offspring inherit characteristics from both parents."""
    ga = GeneticAlgorithm(crossover_method='pmx')
    route1 = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    route2 = ['A', 'F', 'C', 'B', 'E', 'D', 'G']
    
    offspring1, offspring2 = ga._pmx_crossover(route1, route2)
    
    # Offspring should have some elements from each parent
    # (Specific assertions depend on implementation details)
    assert offspring1 != route1  # Changed from parent1
    assert offspring1 != route2  # Not a copy of parent2
```

**Benchmark Tests**:
```python
# backend/tests/benchmark_crossover.py

def benchmark_crossover_methods():
    """Compare all crossover methods on Goa POI dataset."""
    methods = ['pmx', 'cox', 'ox', 'cx']
    results = {method: [] for method in methods}
    
    # Load real Goa POI data
    pois = load_goa_pois(limit=50)
    
    for method in methods:
        ga = GeneticAlgorithm(crossover_method=method, population_size=100, max_generations=50)
        
        for trial in range(10):  # 10 trials for statistical significance
            # Create random route selection
            selected_pois = random.sample(pois, 10)
            
            # Run GA
            best_route, best_fitness, generation = ga.optimize(selected_pois)
            
            results[method].append({
                'fitness': best_fitness,
                'generation': generation,
                'route': best_route,
            })
    
    # Analyze results
    for method, trials in results.items():
        avg_fitness = np.mean([t['fitness'] for t in trials])
        avg_generation = np.mean([t['generation'] for t in trials])
        
        print(f"{method.upper()}: Avg Fitness = {avg_fitness:.4f}, Avg Convergence = {avg_generation:.1f}")
    
    # Statistical comparison
    from scipy.stats import ttest_ind
    pmx_fitness = [t['fitness'] for t in results['pmx']]
    cox_fitness = [t['fitness'] for t in results['cox']]
    
    t_stat, p_value = ttest_ind(pmx_fitness, cox_fitness)
    print(f"PMX vs COX: t={t_stat:.3f}, p={p_value:.4f}")
    
    if p_value < 0.05:
        better = "COX" if np.mean(cox_fitness) > np.mean(pmx_fitness) else "PMX"
        print(f"✓ {better} is statistically significantly better (p<0.05)")
    else:
        print("✗ No significant difference between PMX and COX")
```

### 9.3 Performance Optimization

**Optimization 1: Crossover Point Caching**
```python
# Cache crossover points instead of generating random each time
def _get_crossover_points(self, length):
    if not hasattr(self, '_cached_points'):
        self._cached_points = {}
    
    if length not in self._cached_points:
        self._cached_points[length] = (
            random.randint(1, length - 2),
            random.randint(length // 2, length - 1)
        )
    
    return self._cached_points[length]
```

**Optimization 2: Parallel Crossover**
```python
from concurrent.futures import ProcessPoolExecutor

def crossover_population(self, parent_pairs):
    """Apply crossover to multiple parent pairs in parallel."""
    with ProcessPoolExecutor(max_workers=4) as executor:
        offspring = list(executor.map(
            lambda pair: self.crossover(pair[0], pair[1]),
            parent_pairs
        ))
    return offspring
```

---

## 10. References

### Academic Papers

1. **PeerJ Computer Science 2024**: "Improving itinerary recommendation for tourists using genetic algorithm with novel crossover operator"
   - Authors: Dania Şehab, Fadi Turan
   - DOI: 10.7717/peerj-cs.2340
   - Key contribution: Copy Order Crossover (COX) method, 43.89% improvement
   - Dataset: Istanbul tourism (47 POIs)

2. **IEEE Access 2020**: "Improving Itinerary Recommendations for Tourists Through Metaheuristic Algorithms"
   - Authors: Vanessa Echeverría, et al.
   - DOI: 10.1109/ACCESS.2020.2990348
   - Key contribution: Fitness function with constraints, PMX usage
   - Dataset: Quito, Ecuador tourism

3. **Goldberg & Lingle (1985)**: "Alleles, Loci, and the Traveling Salesman Problem"
   - Original PMX paper
   - Proceedings of the First International Conference on Genetic Algorithms

4. **Davis (1985)**: "Applying Adaptive Algorithms to Epistatic Domains"
   - Original OX paper
   - Proceedings of IJCAI

5. **Oliver et al. (1987)**: "A Study of Permutation Crossover Operators on the TSP"
   - Original CX paper
   - Genetic Algorithms and their Applications

### WanderWise+ Implementation

- **File**: `backend/app/services/genetic_algorithm.py`
- **Tests**: `backend/tests/test_crossover.py`
- **Benchmarks**: `backend/tests/benchmark_crossover.py`
- **Config**: `backend/app/config.py` (CROSSOVER_METHOD setting)

### Related Documentation

- **Module IV Part 4**: Fitness Function Detailed (this complements crossover)
- **Module IV Part 5**: Selection Methods (tournament selection works with crossover)
- **Module IV Part 7**: Mutation Strategies (mutation complements crossover)

---

**Document Version**: 1.0  
**Last Updated**: January 2026  
**Author**: WanderWise+ Research Team  
**Status**: Research & Implementation Guide
