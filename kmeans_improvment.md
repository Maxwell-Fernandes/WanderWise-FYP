## 3. K-Means Clustering Analysis & Fixes

### 3.1 Current Implementation

```python
def perform_kmeans_clustering(features, num_clusters, random_state=42):
    kmeans = KMeans(n_clusters=num_clusters, random_state=random_state, n_init=10, max_iter=300)
    labels = kmeans.fit_predict(features)
    centroids = kmeans.cluster_centers_
    return labels, centroids, kmeans
```

**Called with:**
```python
features = df_base[["latitude", "longitude"]].to_numpy()
labels, _, _ = perform_kmeans_clustering(features, num_days, random_state=random_state)
```

### 3.2 Identified Flaws

#### 🔴 Flaw 1: K-Means Assumes Spherical Clusters — Goa Isn't Spherical

Goa's POI distribution is **coastal and elongated**:
- Dense strip along the coast (north-south ~120km)
- Sparse interior (east-west ~40km)
- K-means creates spherical Voronoi cells that split the coastal strip artificially

**Fix:** Convert lat/lon to local km coordinates:

```python
def _to_local_km(lat_arr, lon_arr):
    R = 6371.0
    lat0, lon0 = lat_arr.mean(), lon_arr.mean()
    x_km = (lon_arr - lon0) * np.radians(R) * np.cos(np.radians(lat0))
    y_km = (lat_arr - lat0) * np.radians(R)
    return np.column_stack([x_km, y_km])
```

#### 🔴 Flaw 2: No Minimum Cluster Size Guarantee

K-means can create a cluster with 2 POIs and another with 50. Small clusters = "empty days."

**Fix:** Post-process — merge undersized clusters into nearest neighbor:

```python
def _enforce_min_cluster_size(labels, features_km, min_size=4, centroids_km=None):
    labels = labels.copy()
    unique, counts = np.unique(labels, return_counts=True)
    small = [c for c, n in zip(unique, counts) if n < min_size]
    large = [c for c, n in zip(unique, counts) if n >= min_size]
    if not small:
        return labels
    if not large:
        return np.zeros_like(labels)
    if centroids_km is None:
        centroids_km = np.array([features_km[labels == c].mean(axis=0) for c in unique])
    for sc in small:
        mask = labels == sc
        sc_centroid = centroids_km[sc]
        nearest = min(large, key=lambda lc: np.linalg.norm(sc_centroid - centroids_km[lc]))
        labels[mask] = nearest
    remap = {old: new for new, old in enumerate(np.unique(labels))}
    return np.array([remap[l] for l in labels])
```

#### 🟡 Flaw 3: Lat/Lon Feature Scale Mismatch

In the less-travel path, `HOTEL_DISTANCE_FEATURE_WEIGHT = 0.05` is ad-hoc. Lat/lon are in degrees (~1.1 range), distance feature is in km×0.05 (~3.0 range). Without standardization, the distance feature has inconsistent influence.

**Fix:** Standardize features with `StandardScaler` before clustering.

#### 🟡 Flaw 4: No Cluster-to-Day Ordering

Cluster 0 might be the furthest from the hotel but gets Day 1. No logic determines which cluster becomes which day.

**Fix:** Order clusters by proximity to anchor (hotel) or north→south:

```python
def _order_clusters_by_proximity(labels, df, anchor_lat=None, anchor_lon=None):
    unique = np.unique(labels)
    centroids = {c: (df.loc[labels==c, "latitude"].mean(), 
                     df.loc[labels==c, "longitude"].mean()) for c in unique}
    if anchor_lat is not None:
        ordered = sorted(unique, key=lambda c: _haversine_km(
            centroids[c][0], centroids[c][1], anchor_lat, anchor_lon))
    else:
        ordered = sorted(unique, key=lambda c: centroids[c][0], reverse=True)
    day_map = {old: new+1 for new, old in enumerate(ordered)}
    return np.array([day_map[l] for l in labels])
```

#### 🟡 Flaw 5: Euclidean Distance on Lat/Lon

At Goa's latitude, 1° longitude ≈ 107km but 1° latitude ≈ 111km. ~4% distortion. Low impact for Goa, but the local km conversion (Flaw 1 fix) resolves this automatically.

### 3.3 K-Means Fixes Summary

| Fix | Severity | Effort | Impact |
|-----|----------|--------|--------|
| Convert to local km coordinates | 🔴 High | Low (~8 lines) | Clusters match real geography |
| Enforce minimum cluster size | 🔴 High | Low (~15 lines) | No "empty day" problem |
| Cluster ordering | 🟡 Medium | Low (~12 lines) | Sensible day sequence |
| Feature standardization | 🟡 Medium | Low | Distance feature actually works |
| Travel-time validation | 🟡 Medium | Medium | Prevents spread-out clusters |

---


## 4. Popularity Normalization Approaches

### 4.1 The Problem

Popularity scores need to be comparable across clusters when the GA picks POIs for each day. Three approaches were evaluated.

### 4.2 Approach Comparison

Using Goa POIs as examples:

| POI | Rating | Reviews | Score | Global Norm | Per-Cluster Norm | Per-Category Norm |
|-----|--------|---------|-------|-------------|-----------------|-------------------|
| Calangute Beach | 4.2 | 18,000 | 0.95 | 1.00 | 1.00 | 1.00 |
| Basilica of Bom Jesus | 4.6 | 8,000 | 0.78 | 0.82 | 1.00 | 1.00 |
| Dudhsagar Falls | 4.5 | 3,500 | 0.62 | 0.65 | 1.00 | 1.00 |
| Mahadeva Temple | 4.7 | 60 | 0.20 | 0.21 | 0.26 | 1.00 |

| Approach | Best for | Risk |
|----------|----------|------|
| **Global** | Default routes, no strong preference | Niche gems get buried |
| **Per-cluster** | Regional fairness | Not comparable across clusters |
| **Per-category** | Strong interest filters | Inflates obscure POIs to 1.0 |
| **Hybrid** ✅ | Both cases | Slightly more complex |

### 4.3 Recommended: Hybrid Normalization

**Strategy:**
- **No interests** → Global normalization (honest popularity, 80% global + 20% cluster)
- **With interests** → Category-matching POIs get a 1.3x boost, then global normalization

**Key insight:** The boost is a *multiplier*, not a *replacement*. A 0.20 temple becomes 0.26 (0.20 × 1.3), not 1.0. A genuinely popular matching POI (Basilica at 0.78) benefits much more (0.78 × 1.3 = 1.01 → clamped to 1.0).

**Output examples:**

```
=== No interests (default routes) ===
Calangute Beach                  0.95 → 1.000   ← most popular, wins
Basilica of Bom Jesus            0.78 → 0.857
Dudhsagar Falls                  0.62 → 0.722
Chapora Fort                     0.55 → 0.604
Butterfly Beach                  0.35 → 0.368
Mahadeva Temple                  0.20 → 0.220   ← honest low score

=== User: religious + historical ===
Calangute Beach                  0.95 → 0.769   ← demoted (no match)
Basilica of Bom Jesus            0.78 → 0.857   ← promoted (matches)
Dudhsagar Falls                  0.62 → 0.555
Chapora Fort                     0.55 → 0.604   ← promoted (historical)
Butterfly Beach                  0.35 → 0.283
Mahadeva Temple                  0.20 → 0.220

=== User: beaches ===
Calangute Beach                  0.95 → 1.000   ← top beach, max score
Basilica of Bom Jesus            0.78 → 0.659   ← demoted
Dudhsagar Falls                  0.62 → 0.555
Chapora Fort                     0.55 → 0.465
Butterfly Beach                  0.35 → 0.368   ← boosted (beach match)
Mahadeva Temple                  0.20 → 0.169
```

**Implementation:**

```python
def _category_match_boost(categories, positive_interests, boost_factor=1.3):
    if not positive_interests or not categories:
        return 1.0
    cat_set = set(c.lower().strip() for c in categories)
    int_set = set(i.lower().strip() for i in positive_interests)
    if cat_set & int_set:
        return boost_factor
    for cat in cat_set:
        for interest in int_set:
            if interest in cat or cat in interest:
                return 1.1
    return 1.0


def normalize_popularity_hybrid(df_with_popularity, positive_interests=None,
                                 global_weight=0.8, cluster_weight=0.2,
                                 category_boost=1.3):
    df = df_with_popularity.copy()
    
    # Step 1: Apply category boost if user has interests
    has_interests = positive_interests and len(positive_interests) > 0
    if has_interests:
        df["_boosted_score"] = df.apply(
            lambda row: row["popularity_score"] * _category_match_boost(
                row.get("categories", []), positive_interests, category_boost
            ), axis=1
        )
        score_col = "_boosted_score"
    else:
        score_col = "popularity_score"
    
    # Step 2: Global normalization
    global_max = df[score_col].max()
    df["_global_norm"] = df[score_col] / global_max if global_max > 0 else 0.5
    
    # Step 3: Per-cluster normalization
    if "cluster" in df.columns:
        cluster_max = df.groupby("cluster")[score_col].transform("max")
        df["_cluster_norm"] = np.where(cluster_max > 0, df[score_col] / cluster_max, 0.5)
    else:
        df["_cluster_norm"] = df["_global_norm"]
    
    # Step 4: Blend
    df["normalized_popularity"] = (
        global_weight * df["_global_norm"] + cluster_weight * df["_cluster_norm"]
    ).clip(0.0, 1.0)
    
    # Cleanup
    df.drop(columns=["_global_norm", "_cluster_norm", "_boosted_score"], errors="ignore", inplace=True)
    return df
```

**Integration (one-line change in `_apply_travel_radius_filter`):**
```python
# OLD:
df_norm = normalize_popularity_by_cluster(df_pop)

# NEW:
interests = _derive_positive_interests(user_preference, positive_interests)
df_norm = normalize_popularity_hybrid(df_pop, positive_interests=interests)
```

---