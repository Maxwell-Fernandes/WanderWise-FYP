# 05 Edge Cases Handling in Geographic Clustering

## 1. Common Edge Cases in Tourism Clustering

Geographic clustering for tourism routing encounters several edge cases that require specialized handling beyond the standard K-means algorithm. These edge cases arise from the unique characteristics of tourism POI distribution, user preference combinations, and the requirement for balanced daily itineraries. The WanderWise+ clustering module implements specific strategies to address each edge case, ensuring robust cluster quality across diverse tour configurations.

The primary edge cases include imbalanced clusters (where POIs are distributed unevenly across days), empty clusters (where some cluster centroids receive no POI assignments), outlier POIs (that fall far from any natural cluster), and minimum POI constraints (ensuring each day has sufficient activities). Additional edge cases arise from the geographic peculiarities of Goa, including coastal concentration, interior sparsity, and the presence of distant attractions like Dudhsagar Waterfalls.

Understanding these edge cases is essential for production deployment. Without proper handling, edge cases can produce unusable itineraries—days with too few activities, days requiring excessive travel, or tours that exclude popular POIs due to algorithmic quirks. The following sections detail each edge case and the WanderWise+ implementation's response.

## 2. Imbalanced Clusters

Imbalanced clusters occur when POIs are distributed unevenly across the K clusters, resulting in some days with significantly more activities than others. This situation commonly arises when user interests favor POIs concentrated in one geographic region. For example, a user interested primarily in nightlife might select POIs concentrated almost entirely in North Goa (Baga, Calangute, Anjuna), leaving Central and South Goa with few relevant POIs.

The impact of imbalanced clusters on user experience is significant. A tour with 25 POIs in Day 1 and only 3 POIs in Day 2 creates an inconsistent travel experience—users would feel rushed on the first day and bored on the second. Additionally, the dense cluster may require excessive travel time to visit all POIs, while the sparse cluster may not fill a full day of activities.

The WanderWise+ implementation addresses imbalanced clusters through post-clustering rebalancing. After the K-means algorithm converges, the algorithm evaluates cluster sizes against minimum and maximum thresholds (typically 6 and 15 POIs per cluster). If clusters fall outside these bounds, rebalancing proceeds by identifying oversized clusters and attempting to reassign peripheral POIs to undersized clusters.

Rebalancing maintains geographic coherence by only considering POIs near cluster boundaries. A POI on the edge of the North Goa cluster that is closer to the Central Goa cluster centroid might be reassigned to Central, improving balance with minimal geographic penalty. The algorithm evaluates each boundary POI for potential reassignment, accepting changes that improve balance without excessive increase in within-cluster sum of squares.

```python
def rebalance_clusters(clusters: Dict[int, List[POI]], 
                       centroids: List[Tuple[float, float]],
                       min_pois: int = 6, 
                       max_pois: int = 15) -> Dict[int, List[POI]]:
    """
    Rebalance clusters to ensure each has sufficient POIs.
    
    Args:
        clusters: Initial clustering result
        centroids: Cluster centroids
        min_pois: Minimum POIs per cluster
        max_pois: Maximum POIs per cluster
    
    Returns:
        Rebalanced clusters
    """
    MIN_POI_COUNT = min_pois
    MAX_POI_COUNT = max_pois
    
    def compute_cluster_stats(cluster_idx: int) -> Dict:
        cluster_pois = clusters[cluster_idx]
        cent_lat, cent_lon = centroids[cluster_idx]
        
        max_dist = 0.0
        for poi in cluster_pois:
            d = haversine_distance(poi.latitude, poi.longitude, cent_lat, cent_lon)
            max_dist = max(max_dist, d)
        
        return {
            'count': len(cluster_pois),
            'centroid': (cent_lat, cent_lon),
            'max_distance': max_dist
        }
    
    stats = {i: compute_cluster_stats(i) for i in clusters.keys()}
    
    undersized = [i for i, s in stats.items() if s['count'] < MIN_POI_COUNT]
    oversized = [i for i, s in stats.items() if s['count'] > MAX_POI_COUNT]
    
    for under_idx in undersized:
        for over_idx in oversized:
            if len(clusters[over_idx]) <= MIN_POI_COUNT + 1:
                continue
            
            over_cent = stats[over_idx]['centroid']
            under_cent = stats[under_idx]['centroid']
            
            candidates = []
            for poi in clusters[over_idx]:
                dist_from_over = haversine_distance(
                    poi.latitude, poi.longitude, over_cent[0], over_cent[1]
                )
                dist_from_under = haversine_distance(
                    poi.latitude, poi.longitude, under_cent[0], under_cent[1]
                )
                
                if dist_from_under < dist_from_over:
                    candidates.append((poi, dist_from_over - dist_from_under))
            
            if not candidates:
                continue
            
            candidates.sort(key=lambda x: x[1], reverse=True)
            best_poi, _ = candidates[0]
            
            clusters[over_idx].remove(best_poi)
            clusters[under_idx].append(best_poi)
            
            if len(clusters[under_idx]) >= MIN_POI_COUNT:
                break
    
    return clusters
```

## 3. Empty Clusters

Empty clusters occur when K-means initialization places a centroid in a sparse region of the POI distribution, or when cluster reassignment during iterations leaves a centroid without any assigned POIs. This edge case is particularly common when clustering POIs for niche interest combinations that concentrate in specific geographic areas.

The standard K-means algorithm fails with empty clusters because the centroid update step requires computing the mean of assigned POIs—with no assigned POIs, the mean is undefined. Naive approaches like skipping the update or maintaining the previous position can destabilize the algorithm.

The WanderWise+ implementation handles empty clusters through proactive detection and reinitialization. After each assignment step, the algorithm checks for empty clusters. If empty clusters are detected, the implementation reinitializes each empty centroid to the location of a randomly selected POI from an oversized cluster. This approach maintains the total number of clusters K while redistributing cluster membership.

```python
def handle_empty_clusters(clusters: Dict[int, List[POI]], 
                          centroids: List[Tuple[float, float]],
                          pois: List[POI]) -> Tuple[Dict[int, List[POI]], 
                                                    List[Tuple[float, float]]]:
    """
    Handle empty clusters by reinitializing centroids.
    
    Args:
        clusters: Current cluster assignments
        centroids: Current centroids
        pois: All POIs
    
    Returns:
        Updated clusters and centroids
    """
    empty_clusters = [i for i, c in clusters.items() if len(c) == 0]
    
    if not empty_clusters:
        return clusters, centroids
    
    non_empty_clusters = [i for i, c in clusters.items() if len(c) > 0]
    
    for empty_idx in empty_clusters:
        source_cluster = random.choice(non_empty_clusters)
        
        candidate_pois = [p for p in clusters[source_cluster] 
                         if p not in [poi for c in clusters.values() 
                                     for poi in c if (p.latitude, p.longitude) 
                                     not in centroids]]
        
        if candidate_pois:
            random_poi = random.choice(candidate_pois)
            new_centroid = (random_poi.latitude, random_poi.longitude)
        else:
            random_poi = random.choice(pois)
            new_centroid = (random_poi.latitude, random_poi.longitude)
        
        centroids[empty_idx] = new_centroid
    
    return clusters, centroids
```

## 4. Outlier POIs in Goa Tourism

Outlier POIs present a unique challenge in geographic clustering because they cannot be meaningfully assigned to any cluster without creating geographic incoherence. In the Goa context, Dudhsagar Waterfalls is the primary outlier—located approximately 40 kilometers inland from the coastal concentration of most other POIs.

The geographic distribution of Goa POIs creates natural clustering around the coastal regions. Most beaches, nightlife venues, and historical sites are located within 10-15 kilometers of the coastline. Dudhsagar Waterfalls, situated in the Bhagwan Mahavir Wildlife Sanctuary near the Karnataka border, lies approximately 40 kilometers from the nearest major beach destination. For a user interested in both beaches and nature, including Dudhsagar in any coastal cluster would dramatically increase cluster diameter and daily travel time.

The WanderWise+ implementation handles outliers through detection and either special clustering or user notification. Outlier detection uses a distance threshold—POIs more than 30 kilometers from the geographic center of the POI distribution are flagged as potential outliers. These outliers are then either assigned to the nearest cluster (with user notification about increased travel time) or suggested as an optional add-on that would require dedicated day planning.

```python
def detect_outliers(pois: List[POI], 
                   distance_threshold_km: float = 30.0) -> List[POI]:
    """
    Detect POIs that are geographic outliers.
    
    Args:
        pois: List of POIs to analyze
        distance_threshold_km: Maximum distance from center to be non-outlier
    
    Returns:
        List of outlier POIs
    """
    if len(pois) < 2:
        return []
    
    center_lat = sum(p.latitude for p in pois) / len(pois)
    center_lon = sum(p.longitude for p in pois) / len(pois)
    
    outliers = []
    for poi in pois:
        d = haversine_distance(poi.latitude, poi.longitude, center_lat, center_lon)
        if d > distance_threshold_km:
            outliers.append(poi)
    
    return outliers

def cluster_with_outlier_handling(pois: List[POI], k: int) -> Dict[int, List[POI]]:
    """
    Perform clustering with special handling for outliers.
    
    Args:
        pois: POIs to cluster
        k: Number of clusters (days)
    
    Returns:
        Cluster assignments with outlier handling
    """
    outliers = detect_outliers(pois)
    core_pois = [p for p in pois if p not in outliers]
    
    if len(core_pois) < k:
        return {i: [pois[i]] if i < len(pois) else [] for i in range(k)}
    
    kmeans = GeographicKMeans(k=k)
    result = kmeans.fit(core_pois)
    
    clusters = result.clusters
    
    for outlier in outliers:
        min_distance = float('inf')
        closest_cluster = 0
        for cluster_idx, centroid in enumerate(result.centroids):
            d = haversine_distance(
                outlier.latitude, outlier.longitude,
                centroid[0], centroid[1]
            )
            if d < min_distance:
                min_distance = d
                closest_cluster = cluster_idx
        clusters[closest_cluster].append(outlier)
    
    return clusters
```

## 5. Minimum POIs Per Day Constraint

The minimum POIs per day constraint ensures that each day of the tour has sufficient activities to constitute a meaningful itinerary. The WanderWise+ implementation enforces a minimum threshold (typically 6 POIs per day) to prevent days with only 1-2 activities that would leave users with excessive free time.

Minimum constraint violations occur when user interest selection yields few POIs overall, or when geographic distribution naturally creates sparse clusters. The implementation addresses minimum constraints through three mechanisms: minimum constraint violation detection, cluster merging, and user notification.

When minimum constraint violations are detected, the algorithm first attempts cluster merging—combining undersized clusters with neighboring clusters to achieve minimum size. If merging all undersized clusters still results in violations (indicating insufficient total POIs), the system notifies the user that their selected interests yield limited options and suggests expanding interest categories or reducing trip duration.

```python
def enforce_minimum_pois(clusters: Dict[int, List[POI]], 
                        centroids: List[Tuple[float, float]],
                        pois: List[POI],
                        min_pois: int = 6) -> Dict[int, List[POI]]:
    """
    Ensure each cluster has minimum number of POIs.
    
    Args:
        clusters: Current cluster assignments
        centroids: Cluster centroids
        pois: All POIs (for reassignment options)
        min_pois: Minimum POIs per cluster
    
    Returns:
        Clusters meeting minimum constraint
    """
    MIN_POI_PER_DAY = min_pois
    
    def get_cluster_stats():
        return {
            i: {
                'count': len(c),
                'centroid': centroids[i],
                'pois': c
            }
            for i, c in clusters.items()
        }
    
    stats = get_cluster_stats()
    undersized = [i for i, s in stats.items() if s['count'] < MIN_POI_PER_DAY]
    
    while undersized:
        smallest = min(undersized, key=lambda i: stats[i]['count'])
        
        candidates = []
        for i, s in stats.items():
            if i == smallest or s['count'] <= MIN_POI_PER_DAY:
                continue
            
            for poi in s['pois']:
                d = haversine_distance(
                    poi.latitude, poi.longitude,
                    stats[smallest]['centroid'][0],
                    stats[smallest]['centroid'][1]
                )
                candidates.append((i, poi, d))
        
        if not candidates:
            break
        
        candidates.sort(key=lambda x: x[2])
        source_cluster, reassign_poi, _ = candidates[0]
        
        clusters[source_cluster].remove(reassign_poi)
        clusters[smallest].append(reassign_poi)
        
        stats = get_cluster_stats()
        undersized = [i for i, s in stats.items() if s['count'] < MIN_POI_PER_DAY]
    
    return clusters
```

## 6. Real Goa Examples

The practical application of edge case handling to Goa tourism demonstrates how the WanderWise+ clustering module manages real-world complexity.

**Example 1: Beach-Focused 5-Day Tour with 25 POIs**

After filtering for beach-related POIs, the system retrieves 25 locations distributed across North, Central, and South Goa. K-means clustering with K=5 initially produces clusters with sizes [8, 7, 6, 3, 1]. The undersized clusters (3 and 1 POIs) trigger rebalancing. The algorithm reassigns boundary POIs from oversized clusters, achieving final sizes [7, 7, 6, 6, 5]—all meeting the minimum of 6.

**Example 2: Nightlife-Focused 3-Day Tour with 12 POIs**

Nightlife POIs concentrate heavily in North Goa (Baga, Calangute, Anjuna). After filtering, only 12 POIs match, all in the North region. K-means produces clusters with sizes [10, 1, 1]. Rebalancing merges the undersized clusters into a single cluster of size 2, resulting in [10, 2]. The remaining undersized cluster triggers user notification: "Your selected interests yield limited POIs in Central and South Goa. Consider adding beach or historical interests for more balanced itineraries."

**Example 3: Nature-Focused Tour with Dudhsagar**

A user interested in nature selects Dudhsagar Waterfalls, Bhagwan Mahavir Sanctuary, Salim Ali Bird Sanctuary, and several spice plantations. The outlier detection identifies Dudhsagar as an outlier (40km from the center of other nature POIs). The system assigns Dudhsagar to the nearest cluster but adds a notification: "Dudhsagar Waterfalls is distant from other nature POIs. Including this attraction will increase daily travel time."

---

## References

1. Jain, A. K. (2010). Data clustering: 50 years beyond K-means. Pattern Recognition Letters, 31(8), 651-666.

2. Celebi, M. E., Kingravi, H. A., & Vela, P. A. (2013). A comparative study of efficient initialization methods for the k-means clustering algorithm. Expert Systems with Applications, 40(1), 200-210.

3. Bradley, P. S., & Fayyad, U. M. (1998). Refining initial points for k-means clustering. Proceedings of the Fifteenth International Conference on Machine Learning, 91-99.
