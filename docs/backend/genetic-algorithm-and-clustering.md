# Genetic Algorithm and Clustering Documentation

## Scope
This document describes the production clustering pipeline (Module 2) and the GA-based route optimizer (Module 4). It lists all parameters currently used in code, their defaults, and how the fitness function is computed, including penalties and rewards.

---

## Module 2: Clustering (K-Means + Popularity Normalization)



### Inputs
- `num_days` (int): number of clusters (days)
- `min_reviews` (int, default 1): Bayesian smoothing threshold
- `random_state` (int, default 42): KMeans RNG seed
- `input_places` (optional list): if provided, bypass dataset loading
- `travel_distance` ("less" or "more"): optional radius filter
- `hotel_location`, `region`, `hotel_lat`, `hotel_lon`, `hotel_address`: anchor inputs
- `user_preference`, `positive_interests`: used for interest derivation and metadata

### Preprocessing
- Loads dataset and filters to Goa bounds: latitude 14.8-15.9, longitude 73.6-74.4.
- Ensures `categories` exists (via `parse_categories()` or `classify_place()`).
- Coerces coordinates to numeric and drops invalid rows.

### Anchor Resolution
If the user provides hotel coordinates or a location/region:
1. `hotel_lat`/`hotel_lon` takes priority if within Goa bounds.
2. `hotel_location` is matched against `HOTEL_LOCATION_TERMS` in address/name text.
3. `region` is matched against `REGION_TERMS` in address/name text.
4. Fallback to dataset mean coordinates.

### Travel Distance Filter ("less")
Enabled when `travel_distance == "less"` and there is enough data.

Parameters:
- `TRAVEL_LESS_BASE_RADIUS_KM = 20.0`
- `TRAVEL_LESS_STEP_KM = 5.0`
- `TRAVEL_LESS_MAX_RADIUS_KM = 60.0`
- `TRAVEL_LESS_EXCEPTION_PER_DAY = 2`
- `FIRST_STOP_RADIUS_BUFFER_KM = 0.0`

Logic:
- Radius starts at base and expands by step up to max until minimum POI counts are satisfied.
- Minimum count target: `min_count = max(num_days * MIN_POIS_PER_ROUTE, num_days)`.
- Metadata includes `exception_cap` and `fallback_reason`, but exception adding is currently disabled (`exception_policy = "none"`).

### Clustering Features
- Base features: latitude and longitude.
- Optional third feature: distance from anchor (km) scaled by `HOTEL_DISTANCE_FEATURE_WEIGHT = 0.05`.

### KMeans Configuration
`perform_kmeans_clustering()`:
- `n_clusters = min(num_days, len(df))`
- `random_state = random_state`
- `n_init = 10`
- `max_iter = 300`

Day assignment:
- `cluster` is KMeans label (0-based)
- `day = cluster + 1`

### Popularity Scoring
Computed per cluster with Bayesian smoothing and normalization.

Definitions:
- $r$ = normalized Google rating, $r = (rating - 1) / 4$
- $v$ = review count
- $m$ = `min_reviews`
- $c$ = global mean normalized rating

Weighted rating:
$$
weighted = \frac{v}{v + m} r + \frac{m}{v + m} c
$$

Quantity factor:
$$
quantity = \frac{\log(1 + v)}{\log(1 + max\_reviews\_in\_cluster)}
$$

Popularity score:
$$
score = QUALITY\_WEIGHT \cdot weighted + QUANTITY\_WEIGHT \cdot quantity
$$

Normalization within cluster:
$$
normalized\_popularity = \frac{score}{max\_score\_in\_cluster}
$$

Parameters:
- `QUALITY_WEIGHT = 0.6`
- `QUANTITY_WEIGHT = 0.4`

### First-Stop Ordering (optional)
When a travel radius is used, `FIRST_STOP_RADIUS_BUFFER_KM` is applied to find a first POI near the anchor. The day is then ordered so this POI appears early. Metadata records per-day first-stop selection.

---

## Module 4: Genetic Algorithm (GA) Route Optimization

### GA Defaults (ga_config)
- `POPULATION_SIZE = 120`
- `MAX_GENERATIONS = 90`
- `CROSSOVER_RATE = 0.7`
- `MUTATION_RATE = 0.2`
- `TOURNAMENT_SIZE = 2`
- `ELITE_COUNT = 3`
- `EARLY_STOPPING_THRESHOLD = 40`

Chromosome limits:
- `INITIAL_CHROMOSOME_LENGTH = 6`
- `MIN_POIS_PER_ROUTE = 4`
- `MAX_POIS_PER_ROUTE = 15`

Time windows:
- `TOUR_START_TIME = "09:00"`
- `TOUR_END_TIME = "18:00"`
- `LUNCH_START_TIME = "12:30"`
- `LUNCH_END_TIME = "13:30"`
- `DAILY_TIME_BUDGET_HOURS = 9`

Defaults:
- `DEFAULT_VISIT_DURATION_MIN = 60`
- `DEFAULT_OPENING_TIME = "09:00"`
- `DEFAULT_CLOSING_TIME = "17:00"`
- `AVERAGE_SPEED_KM_H = 30`

### Runtime Overrides (payload)
The payload can override:
- `population_size`, `max_generations`, `mutation_rate`, `crossover_rate`, `early_stopping_patience`

### Core GA Operations
- **Initialization**: `initialize_population()` builds random routes with a bias toward higher popularity POIs.
- **Selection**: `tournament_selection()` with `TOURNAMENT_SIZE`.
- **Crossover**: `single_point_crossover()` maintains unique POIs and minimum length.
- **Mutation**: `swap_mutation()` swaps two POIs with probability `MUTATION_RATE`.
- **Early stopping**: stops after `EARLY_STOPPING_THRESHOLD` generations without improvement.
- **Diversity**: final top routes are filtered by minimum Jaccard distance between POI sets.

### Distance and Duration Matrices
`prepare_day_matrices()` builds matrices per day:
- Primary: OSRM Table API
- Fallback: Haversine + average speed

### Itinerary QA Retry (end-to-end)
When `use_llm_itinerary_qa` is enabled, the primary day route is evaluated by `evaluate_itinerary_qa()`.
If `use_llm_itinerary_retry` is also enabled and the result is `ok == false` with `source == "groq"`, the retry flow runs:
1. Map `problematic_places` to POI IDs via `resolve_qa_flagged_place_ids()`.
2. Choose a retry strategy:
	- `excluded_from_pool`: remove flagged POIs if the remaining pool stays >= `MIN_POIS_PER_ROUTE`.
	- `penalty_only`: keep pool, but pass `penalty_place_ids` so flagged POIs incur `ITINERARY_QA_FLAGGED_POI_PENALTY`.
	- `weights_only`: if no POIs could be matched, only adjust weights.
3. Increase `wrong_time` weight by 20% (capped at 3.0) for the retry run.
4. Re-run `optimize_route_ga()` on the chosen pool with optional penalty IDs.
5. Rebuild the day JSON and re-run QA on the new recommended itinerary.
6. Persist `itinerary_retry_attempted` and `itinerary_retry_details` in the response.

### Travel-Type Weights and Tag Defaults
- `FitnessWeights` multipliers scale penalty groups.
- `get_fitness_weights(travel_type)` returns travel-type defaults.
- `get_default_tag_adjustments(travel_type)` provides baseline tag rewards/penalties (e.g., family penalizes strenuous waterfalls).

FitnessWeights fields:
- `distance`, `hard_violation`, `undertime`, `overtime`, `wrong_time`, `trek`, `fatigue`, `type_coverage`, `beach_dominance`

Per-travel-type weight defaults (values not listed are 1.0):

| travel_type | distance | hard_violation | undertime | overtime | wrong_time | trek | fatigue | type_coverage | beach_dominance |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| solo | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| family | 1.1 | 1.15 | 1.0 | 1.25 | 0.95 | 1.15 | 1.45 | 1.05 | 0.9 |
| duo | 0.98 | 1.0 | 1.0 | 1.08 | 1.0 | 1.0 | 0.95 | 1.0 | 1.0 |
| friends | 0.92 | 1.0 | 1.0 | 1.05 | 0.92 | 1.0 | 0.9 | 1.0 | 1.0 |
| couple | 0.96 | 1.0 | 1.0 | 1.05 | 0.98 | 1.0 | 0.96 | 1.0 | 1.0 |
| group | 0.88 | 1.0 | 1.0 | 1.1 | 0.9 | 1.0 | 0.85 | 1.03 | 1.0 |

Hard-violation scaling (applies to `LUNCH_INVASION_PENALTY` and closed-POI penalties):
- solo: 1.0
- family: 1.15
- duo: 1.0
- friends: 1.0
- couple: 1.0
- group: 1.0

Per-travel-type tag defaults (values are per-tag reward/penalty multipliers):
- solo: `{}`
- family: `{waterfall: -0.78, strenuous: -0.68, park: 0.42, sanctuary: 0.52, beach: 0.58}`
- duo: `{beach: 0.22, historical: 0.18, religious: 0.1}`
- couple: `{beach: 0.58, historical: 0.2, viewpoint: 0.45, religious: 0.15, park: 0.12}`
- friends: `{beach: 0.2, park: 0.15, historical: 0.1}`
- group: `{beach: 0.15, park: 0.2, religious: 0.12, shopping: 0.12}`

Optional LLM adjustments are provided by `preference_fitness_llm.py`:
- `weight_deltas` clamped to [-0.5, 0.5]
- Final weights clamped to [0.25, 4.0]
- Tag preferences override per-tag defaults when provided

LLM prompt logic (preference_fitness_llm.py):
- System prompt requires a single JSON object only (no markdown).
- Output schema:
	- `weight_deltas`: per-weight deltas applied as `final = base * (1 + delta)`.
	- `tag_preference`: per-tag adjustments in [-1, 1].
- Allowed tag keys: waterfall, strenuous, beach, park, religious, nature, historical, sanctuary, temple, church, shopping, viewpoint.
- Merge rule: `tag_preference` replaces server defaults only for keys present in the LLM output; omitted keys keep defaults.
- Conflict handling: if user preference conflicts with safer travel types (e.g., family), the prompt instructs safer weights unless user insists.
- Input context: travel_type, server defaults, raw user_preference text, and optional module1 structured extraction.

---

## Fitness Function (Detailed)

### Formula
$$
fitness = \frac{total\_reward}{1 + \Delta}
$$

Where:
$$
\Delta = w_d D + w_h H + w_u U + w_o O + w_t T + w_w W + w_f F + w_c C + w_b B + P_{tag}
$$

- $D$ distance penalty
- $H$ hard violation penalty
- $U$ undertime penalty
- $O$ overtime penalty
- $T$ wrong-time penalty
- $W$ trek penalty
- $F$ fatigue penalty
- $C$ type coverage penalty
- $B$ beach dominance penalty
- $P_{tag}$ negative tag-preference penalty

Weights $w_*$ come from `FitnessWeights`.

### Rewards (added to total_reward)
- **POI value sum**: sum of normalized popularity for POIs in route.
- **Time utilization bonus**: proportional to fraction of daily time budget used.
- **Route length bonus**: favors a target route length (8 if budget >= 8h, else 6).
- **Must-see reward**: `MUST_SEE_REWARD` per must-see POI (WPI >= 0.85).
- **Neighbour reward**: `MUST_SEE_NEIGHBOUR_REWARD` per POI within 5 km of must-see POIs.
- **Correct time reward**: rewards for time-appropriate visits (waterfalls early, beaches outside scorch window, parks in 10:00-16:00).
- **Type coverage bonus**: `DAY_TYPE_COVERAGE_BONUS` for each distinct category covered.
- **Tag preference reward**: positive average tag adjustment scaled by `TAG_PREFERENCE_SCALE`.

### Penalties (detailed)

#### 1) Distance penalty
For each segment distance $d$ (km):
$$
D += DISTANCE\_PENALTY\_WEIGHT \cdot d + DISTANCE\_QUADRATIC\_WEIGHT \cdot d^2
$$

#### 2) Hard violation penalty
- Lunch invasion: `LUNCH_INVASION_PENALTY`
- Closed POI: `HARD_VIOLATION_PENALTY`
- Partial close overlap: `0.5 * HARD_VIOLATION_PENALTY`

#### 3) Overtime penalty
- Base: `OVERTIME_PENALTY_PER_MIN * overtime_minutes`
- If overtime exceeds `OVERTIME_HARD_THRESHOLD_MIN`, multiply by `OVERTIME_STEEP_MULTIPLIER`

#### 4) Undertime penalty
If finishing early beyond 45 minutes buffer:
$$
U = UNDERTIME\_PENALTY\_PER\_MIN \cdot undertime\_minutes
$$

#### 5) Wrong-time penalty
Accumulated from:
- Waterfall visited after `AFTERNOON_END_MIN`: `WRONG_TIME_PENALTY`
- Beach scorch overlap: `BEACH_SCORCH_PENALTY_PER_MIN * overlap_minutes`
- Beach streak (3 beaches in a row): `BEACH_STREAK_PENALTY`
- Park visited outside 10:00-16:00: `PARK_WRONG_TIME_PENALTY`
- Backtrack penalty: `BACKTRACK_PENALTY_WEIGHT * sum(peaks over avg segment distance)`
- Nearby duplicate POIs within `NEARBY_DEDUP_KM`: `NEARBY_DUPLICATE_PENALTY`
- Itinerary QA retry penalty (flagged POIs): `ITINERARY_QA_FLAGGED_POI_PENALTY`

#### 6) Waterfall penalty
If more than one waterfall:
$$
W = (waterfall\_count - 1) \cdot EXTRA\_WATERFALL\_PENALTY
$$

#### 7) Fatigue penalty
If more than two strenuous POIs:
$$
F = (strenuous\_count - 2) \cdot PHYSICAL\_FATIGUE\_PENALTY
$$

#### 8) Type coverage penalty
If route misses categories (historical, religious, nature, beach, waterfall, park):
$$
C = missing\_types \cdot DAY\_MISSING\_TYPE\_PENALTY
$$

#### 9) Beach dominance penalty
If beach ratio exceeds `BEACH_DOMINANCE_THRESHOLD`:
$$
B = (ratio - BEACH\_DOMINANCE\_THRESHOLD) \cdot BEACH\_DOMINANCE\_PENALTY\_SCALE
$$

#### 10) Tag preference penalty
Negative average tag adjustment scaled by:
- `TAG_PREFERENCE_SCALE = 0.2`

### Penalty and Reward Constants (Module 4)
- `MUST_SEE_WPI_THRESHOLD = 0.85`
- `DISTANCE_PENALTY_WEIGHT = 0.5`
- `DISTANCE_QUADRATIC_WEIGHT = 0.08`
- `LUNCH_INVASION_PENALTY = 10.0`
- `UNDERTIME_PENALTY_PER_MIN = 0.15`
- `OVERTIME_PENALTY_PER_MIN = 0.20`
- `OVERTIME_HARD_THRESHOLD_MIN = 45`
- `OVERTIME_STEEP_MULTIPLIER = 1.8`
- `WRONG_TIME_PENALTY = 8.0`
- `EXTRA_WATERFALL_PENALTY = 30.0`
- `PHYSICAL_FATIGUE_PENALTY = 5.0`
- `BACKTRACK_PENALTY_WEIGHT = 0.5`
- `BEACH_STREAK_PENALTY = 20.0`
- `BEACH_SCORCH_START = "12:00"`
- `BEACH_SCORCH_END = "16:00"`
- `BEACH_SCORCH_PENALTY_PER_MIN = 0.35`
- `ITINERARY_QA_FLAGGED_POI_PENALTY = 18.0`
- `DAY_TYPE_COVERAGE_BONUS = 0.12`
- `DAY_MISSING_TYPE_PENALTY = 2.0`
- `BEACH_DOMINANCE_THRESHOLD = 0.45`
- `BEACH_DOMINANCE_PENALTY_SCALE = 16.0`
- `PARK_WRONG_TIME_PENALTY = 6.0`
- `PARK_CORRECT_TIME_REWARD = 0.08`
- `NEARBY_DEDUP_KM = 0.5`
- `NEARBY_REWARD_RADIUS_KM = 0.7`
- `NEARBY_DUPLICATE_PENALTY = 4.0`
- `NEARBY_SUGGESTION_RADIUS_KM = 2.0`
- `NEARBY_SUGGESTIONS_PER_STOP = 3`
- `TIME_UTILIZATION_WEIGHT = 2.0`
- `ROUTE_LENGTH_BONUS_PER_POI = 0.05` (used in earlier versions; current route length bonus uses a fixed curve)
- `MUST_SEE_REWARD = 0.3`
- `MUST_SEE_NEIGHBOUR_REWARD = 0.15`
- `CORRECT_TIME_REWARD = 0.1`

### Fitness Breakdown Output
`build_day_json()` embeds a structured breakdown with:
- Fitness score and formula
- Penalty components
- Reward components
- Weight multipliers
- Nearby alternatives and suggestions


