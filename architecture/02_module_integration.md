# WanderWise+ Module Integration Guide

## Quick Reference

| Module | Input | Output | Dependencies |
|--------|-------|--------|--------------|
| I (NLC) | User text | Category scores | sklearn, TF-IDF |
| II (Popularity) | POI IDs | WPI scores | Review APIs |
| III (Clustering) | POIs + K | Day clusters | Haversine |
| IV (GA) | Clusters + WPI | Optimized routes | distance_matrix |

---

## Inter-Module Data Contracts

### Module I → Module III

```python
# Output from Module I (NLC)
nlc_output = {
    "categories": {
        "beaches": 0.92,
        "historical": 0.85,
        "nature": 0.31,
        "adventure": 0.18,
        "dining": 0.45
    },
    "threshold_applied": 0.30,
    "selected_categories": ["beaches", "historical", "dining"]
}

# Input to Module III (Clustering)
# System queries database for POIs matching selected_categories
```

### Module II → Module IV

```python
# Output from Module II (Popularity)
popularity_output = {
    "poi_scores": {
        "uuid-001": 87.3,  # Baga Beach
        "uuid-005": 82.1,  # Calangute Beach
        "uuid-012": 91.2,  # Basilica of Bom Jesus
        # ...
    },
    "component_breakdown": {
        "uuid-001": {
            "review": 0.85,
            "engagement": 0.78,
            "temporal": 0.92,
            "geographic": 0.88
        }
    }
}

# Input to Module IV (GA)
# WPI scores used in fitness function
```

### Module III → Module IV

```python
# Output from Module III (Clustering)
clustering_output = {
    "day_1": {
        "pois": ["uuid-001", "uuid-005", "uuid-012", "uuid-015", ...],
        "centroid": {"lat": 15.55, "lon": 73.75},
        "count": 9
    },
    "day_2": {
        "pois": ["uuid-003", "uuid-008", "uuid-021", ...],
        "centroid": {"lat": 15.50, "lon": 73.82},
        "count": 8
    },
    # ...
}

# Input to Module IV (GA)
# Each day cluster processed independently
```

---

## Error Handling

### NLC Errors
- Empty input → Return error
- Language not English → Return warning
- No categories above threshold → Return all categories

### Clustering Errors
- K > number of POIs → Return individual POI clusters
- Empty POI list → Return empty result
- Convergence failure → Return best result after max iterations

### GA Errors
- Less than 2 POIs → Return as-is (no optimization needed)
- Population convergence → Return best found
- Timeout → Return best found

---

## Configuration Parameters

### NLC
```python
NLC_CONFIG = {
    "tfidf_vocabulary_size": 5000,
    "category_threshold": 0.30,
    "max_categories": 5
}
```

### Popularity
```python
POPULARITY_CONFIG = {
    "alpha": 0.35,  # Review weight
    "beta": 0.25,   # Engagement weight
    "gamma": 0.25,  # Temporal weight
    "delta": 0.15,  # Geographic weight
    "review_sources": ["google", "tripadvisor", "booking"]
}
```

### Clustering
```python
CLUSTERING_CONFIG = {
    "k_equals_days": True,
    "min_pois_per_day": 6,
    "max_pois_per_day": 15,
    "outlier_threshold_km": 30.0,
    "max_iterations": 100,
    "convergence_tolerance": 1e-4,
    "random_seed": 42
}
```

### GA
```python
GA_CONFIG = {
    "population_size": 100,
    "max_generations": 75,
    "crossover_rate": 0.85,
    "mutation_rate": 0.15,
    "tournament_size": 4,
    "elite_count": 2,
    "fitness_weights": {
        "travel_time": 0.25,
        "popularity": 0.25,
        "waiting_time": 0.25,
        "constraints": 0.25
    }
}
```
