# 02 K Selection Strategy for Multi-Day Tour Clustering

## 1. Determining the Number of Clusters

The selection of K, the number of clusters in K-means clustering, directly determines the structure of multi-day tour itineraries in WanderWise+. Unlike many clustering applications where the optimal K must be discovered through algorithmic methods, the tourism routing domain provides a natural interpretation for K: it represents the number of days in the user's planned trip. This correspondence simplifies the K selection problem considerably while introducing domain-specific considerations for balancing cluster sizes and geographic coherence.

In the WanderWise+ system, K is not a parameter to be optimized through traditional methods like the Elbow method or Silhouette analysis. Instead, K is directly specified by the user through their trip duration selection. When a user indicates they are planning a 5-day trip to Goa, the clustering module sets K=5, dividing the relevant POIs into 5 geographic clusters corresponding to each day. This user-driven K selection ensures that the output naturally matches user expectations—no post-processing is required to determine how many days the itinerary should span.

The K selection process begins when the user completes the interest selection phase of the WanderWise+ application. The frontend presents a trip duration selector, typically offering options ranging from 2-day weekend trips to 10-day extended vacations. The selected value is transmitted to the backend along with the classified interest categories. The clustering service then uses this K value to partition the filtered POI set into the appropriate number of daily clusters.

The relationship between trip duration and clustering structure is straightforward but requires careful handling of edge cases. Very short trips (2 days) pose challenges because dividing POIs into only 2 clusters may result in geographically scattered clusters covering large areas. A 2-day trip covering all of Goa would require approximately 55 kilometers of travel from one extreme to the other, potentially exceeding reasonable daily travel time. The clustering module addresses this through geographic constraints that may reduce effective K for very short trips or suggest trip extensions to users. Conversely, very long trips (10+ days) may result in clusters with very few POIs each, as the POI set must be divided into many small groups. The system handles this through minimum POI-per-day constraints.

## 2. WanderWise Approach: K Equals Days

The WanderWise+ implementation adopts a direct mapping between K and trip duration, where each cluster represents one day's itinerary. This approach aligns with user mental models—when users plan a 3-day trip, they expect three distinct daily plans, not two days with double the activities and one rest day. The K=days approach also simplifies system architecture by eliminating the need for K selection algorithms and their associated hyperparameter tuning.

The implementation stores trip duration as a user preference, typically selected during the initial trip planning phase. The preference is stored in the user session or database and passed to the clustering service when generating itineraries. The clustering service validates that the requested K is feasible given the number of available POIs in the selected categories. If a user requests a 7-day beach itinerary but only 20 beach POIs match their interests, the system may suggest limiting to 5 days or expanding interest categories to include nearby historical or nature sites that would enrich the itinerary.

The K=days approach enables several user experience features that would be difficult with algorithmic K selection. Users can explicitly control their trip duration, comparing the differences between 3-day and 5-day itineraries for the same interest profile. This transparency builds trust in the system—users understand why they receive a particular number of daily plans and can adjust their trip parameters if needed. The system can also provide duration recommendations based on the available POIs, suggesting minimum and maximum feasible trip lengths for each interest combination.

The technical implementation of K=days is straightforward. The clustering service accepts K as a required parameter alongside the POI list and interest categories. The K-means algorithm is configured with exactly K clusters, and the output is formatted as a list of K clusters, one for each day. No elbow analysis, silhouette calculation, or other K selection method is invoked because the optimal K is known a priori from user input.

## 3. Alternative Methods for K Selection

While the K=days approach simplifies K selection for WanderWise+, understanding alternative methods provides context for system design decisions and potential future enhancements. Alternative K selection methods remain relevant for exploratory analysis, such as determining whether a user's interest profile might naturally cluster into fewer or more groups than the requested trip duration would suggest.

The Elbow method evaluates cluster quality for different values of K by plotting the within-cluster sum of squares (WCSS) against K. As K increases, WCSS decreases because additional clusters can better fit the data. The "elbow" point—where the rate of decrease sharply slows—indicates the natural number of clusters in the data. For geographic POI data, the elbow plot typically shows a gradual decrease without a sharp elbow, reflecting the continuous geographic distribution of POIs rather than discrete natural groupings. This behavior confirms that geographic clustering lacks strong natural boundaries, supporting the K=days approach where external factors (trip duration) determine K rather than data-driven discovery.

The Silhouette score provides a measure of cluster cohesion and separation, ranging from -1 to 1. Higher scores indicate better-defined clusters. For each K, the silhouette score is calculated as the average across all data points. The optimal K maximizes the silhouette score. For Goa POI data, silhouette analysis typically shows gradual increases in score with additional clusters, plateauing at K values around the natural geographic regions (North, Central, South). This suggests that while geographic regions provide some clustering structure, the choice of K=days (3-7 typically) falls well within reasonable bounds where cluster quality remains relatively stable.

The Gap statistic compares the total within-cluster variation for different values of K to their expected values under a null reference distribution of the data. The gap statistic identifies the K where the observed clustering shows the largest gap from the null distribution. This method is computationally expensive but provides statistically principled K selection. For WanderWise+, gap statistic analysis of Goa POI data would likely show optimal K values in the 3-5 range for general interest combinations, again aligning well with typical trip durations.

Hierarchical clustering with dendrogram analysis provides visual insight into natural data groupings. Cutting the dendrogram at different heights produces different numbers of clusters. For Goa POI data, the dendrogram typically shows three main branches corresponding to North, Central, and South Goa, with further subdivisions within each region. This hierarchical structure supports both the K=days approach (where K is user-specified) and potential enhancements where the system might suggest K values based on natural geographic divisions.

## 4. Geographic Constraints for Goa Tourism

Goa's distinctive geography imposes constraints on K selection that supplement the K=days approach. The state's approximately 110-kilometer north-south extent, combined with its relatively narrow width (25-65 kilometers), creates natural limits on daily travel distance. Geographic constraints ensure that clusters remain spatially coherent and that daily travel times remain reasonable.

The Northern region of Goa, spanning from Pernem to the Mapusa River, concentrates the highest density of tourist POIs. A full-day itinerary in North Goa can comfortably cover 8-12 beach and nightlife POIs with total travel distance under 30 kilometers. The Central region, centered on Panaji, offers a more compact set of POIs suitable for 6-10 daily visits with under 20 kilometers of travel. The Southern region, featuring dispersed beach and nature POIs, may support only 6-8 daily visits due to longer distances between locations.

These geographic constraints inform the clustering algorithm through minimum and maximum POI constraints per cluster. A cluster with fewer than 6 POIs may not provide a full day's activities, while a cluster with more than 15 POIs may exceed reasonable daily capacity. The clustering service enforces these constraints through post-processing: clusters below the minimum threshold are merged with neighboring clusters, while clusters above the maximum threshold are split and redistributed.

The geographic constraints also influence initialization strategy for K-means. Initial centroids should be placed in areas with sufficient POI density to form viable clusters. Random initialization may place centroids in sparse regions, leading to imbalanced clusters with some very small and some very large. The K-means++ initialization method (detailed in the next document) addresses this by probabilistically favoring initial centroids near existing POIs, but additional constraints may be needed for very sparse regions like South Goa interior.

For multi-day tours spanning different geographic regions, the system applies sequential clustering that respects travel constraints between days. A 5-day tour might allocate Days 1-2 to North Goa, Days 3-4 to Central Goa, and Day 5 to South Goa, ensuring that travel between cluster centroids follows a logical geographic progression. This sequential constraint prevents the algorithm from arbitrarily assigning geographically distant regions to adjacent days.

## 5. Balancing Cluster Sizes

The balance of cluster sizes—measured in terms of POI count, total sightseeing time, and geographic spread—significantly impacts user experience with generated itineraries. Unbalanced clusters result in some days feeling rushed while others feel sparse, creating an inconsistent travel experience. The WanderWise+ clustering module implements several strategies to achieve balanced clusters.

POI count balancing ensures each day includes a similar number of attractions. The initial K-means clustering produces clusters based purely on geographic proximity, which may result in imbalanced counts due to non-uniform POI density. North Goa, with its high POI density, might absorb 40% of POIs into a single cluster, while South Goa, with lower density, produces smaller clusters. Post-clustering rebalancing redistributes POIs from oversized to undersized clusters, maintaining geographic coherence while achieving count balance.

Time-based balancing considers the average time required to visit each POI, accounting for both sightseeing duration and travel time between locations. A cluster containing several major attractions (each requiring 1-2 hours) plus several minor attractions (requiring 15-30 minutes) may have similar POI counts to a cluster of quick-visit spots but require significantly more total time. The clustering service maintains time estimates for each POI category and balances total daily time rather than just POI counts.

Geographic spread balancing limits the diameter of each cluster, measured as the maximum distance between any two POIs within the cluster. A geographically compact cluster reduces daily travel time, while a spread-out cluster requires more transit. The clustering algorithm monitors cluster diameter during formation and rejects assignments that would create clusters exceeding the maximum spread threshold.

The implementation uses iterative rebalancing to achieve multiple balance criteria simultaneously. Starting from the initial geographic clustering, the algorithm evaluates cluster sizes against target ranges. POIs in oversized clusters are evaluated for potential reassignment to undersized clusters based on marginal increase in objective function. Reassignments that improve balance without significantly degrading geographic coherence are accepted. The process iterates until all clusters fall within acceptable size ranges.

## 6. Real Examples: 3-Day, 5-Day, and 7-Day Tours

Examining how K selection affects actual tour generation demonstrates the practical application of clustering strategies in WanderWise+. Each tour duration produces a distinct itinerary structure reflecting the interplay between geographic constraints and user interests.

A 3-day beach-focused tour illustrates K=3 clustering for a popular trip type. After filtering for beach-related POIs, the system retrieves approximately 25-30 relevant locations. Geographic analysis reveals natural concentration in North Goa (Baga, Calangute, Anjuna, Vagator), Central Goa (Miramar, Dona Paula, Coco Beach), and South Goa (Palolem, Agonda, Patnem, Cola Beach). K-means clustering with K=3 produces clusters closely matching these regional divisions, with Day 1 covering North Goa beaches, Day 2 covering Central Goa beaches, and Day 3 covering South Goa beaches. Each cluster contains 8-10 POIs, providing full-day itineraries with reasonable geographic spread.

A 5-day mixed-interest tour (beaches, historical sites, and nature) demonstrates clustering with expanded POI set. The system retrieves 50-60 POIs across three categories, creating a more complex clustering problem. K=5 clustering divides the POIs into five geographic clusters: North Coast (beaches), North Interior (markets, villages), Central Panaji (historical sites, government buildings), South Beaches (nature-focused coastal POIs), and Interior Nature (spice plantations, wildlife areas). The resulting itinerary alternates between coastal and interior regions, providing variety while maintaining geographic coherence.

A 7-day comprehensive tour represents the maximum recommended trip duration for thorough Goa exploration. With K=7, the clustering algorithm must divide POIs into finer-grained groups. The North Coast cluster splits into two (Baga/Calangute and Anjuna/Vagator), the Central cluster maintains cohesion, and South Goa splits into three (Palolem area, Agonda area, and interior nature). Day 7 might focus on a specific interest not fully covered in previous days—perhaps a dedicated food and nightlife day in North Goa or a repeat visit to favorite beaches. The additional K value provides flexibility for itinerary customization.

The comparison across tour durations reveals the value of K=days selection. A 3-day tour requires efficient use of limited time, prioritizing high-density regions. A 5-day tour can balance density with variety. A 7-day tour can explore peripheral areas and provide specialized interest days. Users intuitively understand these trade-offs, making the K=days approach transparent and controllable.

---

## References

1. Tibshirani, R., Walther, G., & Hastie, T. (2001). Estimating the number of clusters in a data set via the gap statistic. Journal of the Royal Statistical Society: Series B (Statistical Methodology), 63(2), 411-423.

2. Rousseeuw, P. J. (1987). Silhouettes: A graphical aid to the interpretation and validation of cluster analysis. Journal of Computational and Applied Mathematics, 20, 53-65.

3. Kodinariya, T. M., & Makwana, P. R. (2013). Review on determining number of Cluster in K-Means Clustering. International Journal, 1(6), 90-95.

4. Sugar, C. A., & James, G. M. (2003). Finding the number of clusters in a dataset: An information-theoretic approach. Journal of the American Statistical Association, 98(463), 750-763.
