# 04 K-Means Algorithm Details for Geographic Clustering

## 1. Complete K-Means Algorithm Step-by-Step

The K-means algorithm for geographic clustering proceeds through a systematic sequence of steps that transform an initial centroid configuration into optimal geographic clusters. This section provides a detailed walkthrough of each step, explaining both the algorithmic mechanics and the geographic interpretation relevant to WanderWise+ tour planning.

**Initialization Phase**: The algorithm begins with K-means++ initialization, selecting K initial centroids as described in the previous document. For a 5-day tour with 50 POIs, this phase produces 5 initial centroid locations, spread across the geographic distribution of POIs. The initial centroids may not correspond to actual POI locations—they are geographic points calculated as weighted combinations of existing POIs.

**Iteration Loop**: The algorithm enters an iterative process that continues until convergence criteria are met. Each iteration consists of an assignment step followed by an update step.

**Assignment Step**: Each POI is assigned to the cluster with the nearest centroid. The assignment uses Haversine distance for geographic accuracy. For each POI, the algorithm computes the distance to all K centroids and assigns the POI to the cluster with minimum distance. The result is a partition of the POI set into K mutually exclusive clusters. Geographically, this means each POI goes to the day whose cluster center is closest to its location.

**Update Step**: After all POIs are assigned, each centroid is repositioned to the geographic center (mean latitude and mean longitude) of its assigned POIs. This recalculation reflects the geographic principle that the best representative point for a set of locations is their centroid. If a cluster contains POIs at Palolem Beach, Cola Beach, and Agonda Beach, the new centroid will be somewhere in the middle of these three points.

**Convergence Check**: After the update step, the algorithm checks whether convergence has been achieved. Convergence is typically defined as no change in cluster assignments (all POIs remain in their current clusters) or minimal improvement in the objective function (within-cluster sum of squares decreases by less than a threshold). If not converged, the algorithm returns to the assignment step using the new centroids.

**Termination**: The algorithm terminates when convergence is achieved or when a maximum iteration count is reached. Upon termination, the final clusters represent the geographic grouping of POIs for the multi-day tour.

The following pseudocode provides the complete algorithm:

```python
from typing import List, Tuple, Dict
from dataclasses import dataclass
import math

@dataclass
class POI:
    id: str
    name: str
    latitude: float
    longitude: float

@dataclass
class ClusteringResult:
    clusters: Dict[int, List[POI]]
    centroids: List[Tuple[float, float]]
    iterations: int
    converged: bool
    wcss: float

class GeographicKMeans:
    def __init__(self, k: int = 3, max_iterations: int = 100,
                 tolerance: float = 1e-4, random_seed: int = 42):
        self.k = k
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.random_seed = random_seed
        self.centroids = None
        self.clusters = None
    
    def _haversine_distance(self, lat1: float, lon1: float,
                           lat2: float, lon2: float) -> float:
        r_lat1 = math.radians(lat1)
        r_lon1 = math.radians(lon1)
        r_lat2 = math.radians(lat2)
        r_lon2 = math.radians(lon2)
        
        d_lat = r_lat2 - r_lat1
        d_lon = r_lon2 - r_lon1
        
        a = (math.sin(d_lat / 2) ** 2 +
             math.cos(r_lat1) * math.cos(r_lat2) * math.sin(d_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return 6371.0 * c
    
    def _initialize_centroids(self, pois: List[POI]) -> List[Tuple[float, float]]:
        import random
        random.seed(self.random_seed)
        n = len(pois)
        
        centroids = []
        first_idx = random.randint(0, n - 1)
        first_poi = pois[first_idx]
        centroids.append((first_poi.latitude, first_poi.longitude))
        
        distances = [float('inf')] * n
        
        for _ in range(1, self.k):
            total_weight = 0.0
            for i, poi in enumerate(pois):
                d = self._haversine_distance(
                    poi.latitude, poi.longitude,
                    centroids[-1][0], centroids[-1][1]
                )
                distances[i] = min(distances[i], d)
                total_weight += distances[i] ** 2
            
            threshold = random.uniform(0, total_weight)
            cumulative = 0.0
            for i, poi in enumerate(pois):
                cumulative += distances[i] ** 2
                if cumulative >= threshold:
                    centroids.append((poi.latitude, poi.longitude))
                    break
        
        return centroids
    
    def _assign_clusters(self, pois: List[POI]) -> Dict[int, List[POI]]:
        clusters = {i: [] for i in range(self.k)}
        
        for poi in pois:
            min_distance = float('inf')
            closest_cluster = 0
            
            for cluster_idx, (cent_lat, cent_lon) in enumerate(self.centroids):
                distance = self._haversine_distance(
                    poi.latitude, poi.longitude,
                    cent_lat, cent_lon
                )
                if distance < min_distance:
                    min_distance = distance
                    closest_cluster = cluster_idx
            
            clusters[closest_cluster].append(poi)
        
        return clusters
    
    def _update_centroids(self, clusters: Dict[int, List[POI]]) -> List[Tuple[float, float]]:
        new_centroids = []
        
        for cluster_idx, cluster_pois in clusters.items():
            if len(cluster_pois) == 0:
                new_centroids.append(self.centroids[cluster_idx])
                continue
            
            avg_lat = sum(p.latitude for p in cluster_pois) / len(cluster_pois)
            avg_lon = sum(p.longitude for p in cluster_pois) / len(cluster_pois)
            new_centroids.append((avg_lat, avg_lon))
        
        return new_centroids
    
    def _compute_wcss(self, clusters: Dict[int, List[POI]]) -> float:
        wcss = 0.0
        
        for cluster_idx, cluster_pois in clusters.items():
            cent_lat, cent_lon = self.centroids[cluster_idx]
            for poi in cluster_pois:
                d = self._haversine_distance(
                    poi.latitude, poi.longitude,
                    cent_lat, cent_lon
                )
                wcss += d ** 2
        
        return wcss
    
    def fit(self, pois: List[POI]) -> ClusteringResult:
        if len(pois) < self.k:
            raise ValueError(f"Number of POIs ({len(pois)}) must be >= k ({self.k})")
        
        self.centroids = self._initialize_centroids(pois)
        
        prev_wcss = float('inf')
        
        for iteration in range(self.max_iterations):
            self.clusters = self._assign_clusters(pois)
            
            empty_clusters = [i for i, c in self.clusters.items() if len(c) == 0]
            for empty_idx in empty_clusters:
                remaining_pois = [p for c in self.clusters.values() 
                                 for p in c 
                                 if (p.latitude, p.longitude) not in self.centroids]
                if remaining_pois:
                    import random
                    random_poi = random.choice(remaining_pois)
                    self.centroids[empty_idx] = (random_poi.latitude, random_poi.longitude)
            
            new_centroids = self._update_centroids(self.clusters)
            
            current_wcss = self._compute_wcss(self.clusters)
            
            if abs(prev_wcss - current_wcss) < self.tolerance:
                return ClusteringResult(
                    clusters=self.clusters,
                    centroids=self.centroids,
                    iterations=iteration + 1,
                    converged=True,
                    wcss=current_wcss
                )
            
            self.centroids = new_centroids
            prev_wcss = current_wcss
        
        return ClusteringResult(
            clusters=self.clusters,
            centroids=self.centroids,
            iterations=self.max_iterations,
            converged=False,
            wcss=self._compute_wcss(self.clusters)
        )
```

## 2. Assignment Step: POI to Cluster Mapping

The assignment step is the computational core of each K-means iteration. For each POI, the algorithm computes distances to all K centroids and assigns the POI to the nearest centroid. This step determines the geographic grouping that defines each day's itinerary.

The assignment process for geographic data uses the Haversine formula to compute great-circle distances between POI coordinates and cluster centroids. The algorithm maintains O(K) distance calculations per POI, where K is the number of clusters (days in the tour). For a typical tour with 50 POIs and K=5, each iteration requires 250 distance calculations.

The assignment step can be optimized through precomputation. The WanderWise+ database maintains a distance_matrix table containing pairwise distances between all POIs. During assignment, the algorithm looks up distances rather than computing them, reducing computational overhead. However, centroid positions may not correspond to actual POIs, requiring on-the-fly distance computation for centroid-to-POI distances.

Assignment results are stored as cluster membership lists. Each cluster maintains a list of assigned POIs, enabling efficient iteration during the update step. The assignment also tracks whether any POIs changed clusters since the previous iteration, providing an early convergence signal.

## 3. Update Step: Centroid Recalculation

The update step repositions each cluster centroid to the geographic center of its assigned POIs. This recalculation reflects the principle that the optimal representative point for a set of geographic locations is their mean latitude and mean longitude.

For a cluster containing POIs at coordinates (lat1, lon1), (lat2, lon2), ..., (latn, lonn), the new centroid position is:

$$centroid\_lat = \frac{lat_1 + lat_2 + ... + lat_n}{n}$$

$$centroid\_lon = \frac{lon_1 + lon_2 + ... + lon_n}{n}$$

This simple averaging works well for geographic data because it produces the point that minimizes the sum of squared distances to all cluster members—the same objective that K-means optimizes.

The update step also handles empty clusters, which can occur when initialization places centroids in sparse regions or when cluster reassignment during iterations leaves some centroids without assigned POIs. The implementation uses a reinitialization strategy that moves empty cluster centroids to the location of a random unassigned POI, preserving the number of clusters K.

## 4. Haversine Distance Implementation

The Haversine formula implementation in the WanderWise+ clustering module requires careful attention to coordinate handling and angle conversion. The following implementation provides production-ready distance calculation:

```python
import math

def haversine_distance(lat1: float, lon1: float, 
                      lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points 
    on Earth using the Haversine formula.
    
    Args:
        lat1, lon1: Latitude and longitude of point 1 in degrees
        lat2, lon2: Latitude and longitude of point 2 in degrees
    
    Returns:
        Distance in kilometers
    """
    EARTH_RADIUS_KM = 6371.0
    
    r_lat1 = math.radians(lat1)
    r_lon1 = math.radians(lon1)
    r_lat2 = math.radians(lat2)
    r_lon2 = math.radians(lon2)
    
    d_lat = r_lat2 - r_lat1
    d_lon = r_lon2 - r_lon1
    
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(r_lat1) * math.cos(r_lat2) * 
         math.sin(d_lon / 2) ** 2)
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return EARTH_RADIUS_KM * c
```

The implementation uses the standard Haversine formula with Earth radius 6371 kilometers. All trigonometric functions in Python's math library operate on radians, requiring explicit conversion from degrees. The formula produces distances in kilometers, appropriate for the geographic scale of Goa tourism.

## 5. Convergence Criteria

Convergence criteria determine when the K-means algorithm terminates. The implementation uses two criteria: objective function improvement threshold and maximum iteration count.

The objective function improvement criterion uses the within-cluster sum of squares (WCSS). After each update step, the algorithm computes WCSS by summing squared distances from each POI to its cluster centroid. If the improvement from the previous WCSS is less than the tolerance (1e-4), the algorithm considers itself converged. This criterion ensures that further iterations would produce negligible improvement in cluster quality.

The maximum iteration count provides a hard limit on computation time. Even if the algorithm is slowly converging, it will terminate after the specified maximum iterations. This prevents infinite loops in pathological cases and ensures predictable performance.

For geographic clustering of tourism POIs, convergence typically occurs within 10-15 iterations with K-means++ initialization. The tolerance-based criterion is usually reached first, indicating that the cluster configuration has stabilized.

## 6. Edge Cases: Empty Clusters and Single POI Clusters

Two edge cases require special handling in geographic K-means clustering: empty clusters and clusters containing only a single POI.

Empty clusters occur when initialization places a centroid in a sparse region or when cluster reassignment during iterations leaves a centroid without any assigned POIs. The implementation handles empty clusters by reinitializing the centroid to the location of a randomly selected unassigned POI. This maintains the total number of clusters K while ensuring all centroids have at least one assigned POI.

Single-POI clusters occur when geographic distribution naturally isolates one POI from the main clusters. This is common for outlier POIs like Dudhsagar Waterfalls, which is located inland from the coastal concentration of other POIs. The algorithm handles single-POI clusters by maintaining the centroid at the POI's location. This is mathematically correct—the centroid of a single point is that point itself.

Post-clustering validation checks whether all clusters contain a minimum number of POIs (e.g., 5). Clusters below this threshold may be merged with neighboring clusters to ensure each day of the tour has sufficient activities.

---

## References

1. MacQueen, J. (1967). Some methods for classification and analysis of multivariate observations. Proceedings of the Fifth Berkeley Symposium on Mathematical Statistics and Probability, 1, 281-297.

2. Lloyd, S. P. (1982). Least squares quantization in PCM. IEEE Transactions on Information Theory, 28(2), 129-137.

3. Sinnott, R. W. (1984). Virtues of the Haversine. Sky and Telescope, 68(2), 159.

4. Jain, A. K., & Dubes, R. C. (1988). Algorithms for Clustering Data. Prentice-Hall.
