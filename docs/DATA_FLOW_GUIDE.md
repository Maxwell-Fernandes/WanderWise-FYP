# WANDERWISE DATA FLOW IMPLEMENTATION GUIDE
**Date**: November 16, 2025
**Purpose**: Practical guide for implementing data flows using the architecture
**Audience**: Development team (4 members)

---

## DOCUMENT OVERVIEW

This document explains **HOW data flows** through WanderWise and **WHICH diagrams to reference** during implementation. Think of this as your implementation roadmap.

### How to Use This Document

1. **Before coding a feature**: Read the corresponding data flow section
2. **During implementation**: Reference the diagram number provided
3. **During debugging**: Trace the data flow path to find bottlenecks
4. **During code review**: Verify implementation matches documented flow

### Quick Navigation

| Feature | Section | Diagram Reference |
|---------|---------|-------------------|
| Generate itinerary | [Flow 1](#flow-1) | Diagram 2, 11 |
| Real-time adaptation | [Flow 2](#flow-2) | Diagram 6 |
| POI recommendation | [Flow 3](#flow-3) | Diagram 5, 10 |
| Distance calculation | [Flow 4](#flow-4) | Diagram 11 |
| Multi-day planning | [Flow 5](#flow-5) | Diagram 4 |
| Weather monitoring | [Flow 6](#flow-6) | Diagram 6 |
| User preferences | [Flow 7](#flow-7) | Diagram 10 |
| System initialization | [Flow 8](#flow-8) | Diagram 7 |

---

## UNDERSTANDING THE ARCHITECTURE (Quick Primer)

### The 7 Layers (Diagram 1)

```
User Interface ←→ API Gateway ←→ Application Layer ←→ Algorithm Layer
                                        ↕                    ↕
                                   Caching Layer ←→ Data Layer
                                        ↕
                                  External APIs
```

**Data Always Flows**:
1. **Downward**: UI → Gateway → Application → Algorithm/Cache/Data
2. **Upward**: Data/Cache/Algorithm → Application → Gateway → UI
3. **Horizontally**: Application ↔ Cache ↔ Database (cache-aside pattern)

### The 9 Services (Diagram 1)

| Service | Responsibility | Data In | Data Out |
|---------|---------------|---------|----------|
| **POI Service** | Manage POI data | POI IDs, filters | POI objects |
| **User Service** | Manage user data | User ID, prefs | User profile |
| **Route Service** | Orchestrate routes | Route request | Complete itinerary |
| **Optimization Service** | Run algorithms | POIs + constraints | Optimized route |
| **Recommendation Service** | Score POIs | User prefs + POIs | Scored POI list |
| **Distance Calculator** | Calculate distances | 2 POI IDs | Distance (km) |
| **Map Service** | Get directions | Route POIs | Map data, polylines |
| **Weather Monitor** | Track weather | Location | Weather updates |
| **Notification Service** | Send alerts | Event + user | Notification sent |

---

## FLOW 1: GENERATE NEW ITINERARY

**Use Case**: User wants a 3-day beach vacation in Goa with ₹15,000 budget

**Reference Diagrams**:
- Diagram 2 (Itinerary Generation Flow) - Complete workflow
- Diagram 11 (Service Interaction Map) - Service-level details

### Step-by-Step Data Flow

#### STEP 1: User Input → UI Layer

**What Happens**: User fills form in React app

**Data Format**:
```javascript
// Frontend (React)
const userInput = {
  days: 3,
  budget: 15000,
  preferences: {
    categories: ["Beach", "Heritage"],
    difficulty: "Easy",
    accessibility: "wheelchair"
  },
  constraints: {
    max_daily_duration_minutes: 480,
    start_time: "09:00",
    hotel_location: {
      latitude: 15.2993,
      longitude: 74.1240,
      name: "Calangute Hotel"
    }
  },
  user_id: "user_abc123"  // From auth token
};
```

**UI Action**:
```javascript
// src/services/api.js
const response = await fetch('/api/v1/itinerary/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${authToken}`
  },
  body: JSON.stringify(userInput)
});
```

**Data Flows To**: API Gateway (Nginx)

---

#### STEP 2: API Gateway → Application Layer

**What Happens**: Nginx routes request to FastAPI backend

**Nginx Config** (`nginx.conf`):
```nginx
location /api/ {
    proxy_pass http://backend:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;

    # Rate limiting (100 req/min per IP)
    limit_req zone=api burst=10;
}
```

**Data Transformation**: None (pass-through)

**Data Flows To**: Route Service

---

#### STEP 3: Route Service → Validation

**What Happens**: FastAPI validates request with Pydantic

**Implementation** (`app/api/routes.py`):
```python
from pydantic import BaseModel, Field, validator

class ItineraryRequest(BaseModel):
    days: int = Field(ge=1, le=7, description="Number of days")
    budget: float = Field(ge=0, description="Total budget in INR")
    preferences: PreferenceSchema
    constraints: ConstraintSchema
    user_id: str

    @validator('days')
    def validate_days(cls, v):
        if v > 7:
            raise ValueError("Maximum 7 days supported")
        return v

@router.post("/itinerary/generate")
async def generate_itinerary(
    request: ItineraryRequest,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    # Validation happens automatically
    logger.info(f"Generating itinerary for user {request.user_id}")

    # Step 4: Check cache
    cache_key = generate_cache_key(request)
    cached = await redis.get(cache_key)

    if cached:
        logger.info("Cache HIT - returning cached itinerary")
        return JSONResponse(content=json.loads(cached))
```

**Data After Validation**:
```python
# Pydantic model instance
request = ItineraryRequest(
    days=3,
    budget=15000.0,
    preferences=PreferenceSchema(...),
    constraints=ConstraintSchema(...),
    user_id="user_abc123"
)
```

**Data Flows To**: Redis L1 Cache (check)

---

#### STEP 4: Redis L1 Cache Check

**What Happens**: Check if similar request was cached

**Implementation**:
```python
# app/services/cache_service.py
class CacheService:
    def __init__(self, redis_client):
        self.redis = redis_client

    def generate_cache_key(self, request: ItineraryRequest) -> str:
        """Generate deterministic cache key"""
        key_data = {
            'days': request.days,
            'budget': request.budget,
            'categories': sorted(request.preferences.categories),
            'difficulty': request.preferences.difficulty,
            # Don't include user_id - cache is shared
        }
        key_string = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        return f"itinerary:v1:{key_hash}"

    async def get_cached_itinerary(self, cache_key: str):
        """Get from L1 cache"""
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        return None
```

**Cache Key Example**: `itinerary:v1:a1b2c3d4e5f6...`

**Possible Outcomes**:
- **HIT**: Return cached itinerary (skip to Step 19)
- **MISS**: Continue to Step 5

**Data Flows To**: User Service + POI Service (parallel)

---

#### STEP 5: Get User Preferences

**What Happens**: Fetch user profile and preferences

**Implementation** (`app/services/user_service.py`):
```python
class UserService:
    async def get_user_preferences(self, user_id: str):
        """Fetch user profile from database"""
        # Check L2 cache first
        cache_key = f"user:prefs:{user_id}"
        cached = await self.redis.get(cache_key)

        if cached:
            return json.loads(cached)

        # Query database
        user = db.query(UserProfile).filter_by(id=user_id).first()

        if not user:
            # Create default preferences
            user_prefs = self._default_preferences()
        else:
            user_prefs = {
                'favorite_categories': user.favorite_categories,
                'budget_range': user.budget_range,
                'difficulty_preference': user.difficulty_preference,
                'accessibility_needs': user.accessibility_needs,
                'past_visits': user.visited_poi_ids
            }

        # Cache for 24 hours
        await self.redis.setex(cache_key, 86400, json.dumps(user_prefs))

        return user_prefs
```

**Data Output**:
```python
user_prefs = {
    'favorite_categories': ['Beach', 'Temple', 'Heritage'],
    'budget_range': 'medium',  # low/medium/high
    'difficulty_preference': 'Easy',
    'accessibility_needs': ['wheelchair'],
    'past_visits': ['poi_123', 'poi_456']  # For diversity
}
```

**Data Flows To**: Recommendation Service

---

#### STEP 6: Fetch POI Candidates

**What Happens**: Get POIs matching user criteria

**Implementation** (`app/services/poi_service.py`):
```python
class POIService:
    async def fetch_candidate_pois(
        self,
        categories: List[str],
        filters: Dict
    ) -> List[POI]:
        """Fetch POIs from database with filters"""

        # Build query
        query = db.query(GoaPlace)

        # Category filter
        if categories:
            query = query.filter(GoaPlace.category.in_(categories))

        # Budget filter (daily budget = total / days)
        daily_budget = filters['budget'] / filters['days']
        query = query.filter(GoaPlace.entry_fee_inr <= daily_budget * 0.3)

        # Difficulty filter
        if filters.get('difficulty'):
            query = query.filter(
                GoaPlace.difficulty_level == filters['difficulty']
            )

        # Accessibility filter
        if filters.get('accessibility'):
            if 'wheelchair' in filters['accessibility']:
                query = query.filter(
                    GoaPlace.wheelchair_accessible.in_(['Yes', 'Partial'])
                )

        # Order by popularity
        query = query.order_by(GoaPlace.popularity_score.desc())

        # Limit to top 50 candidates
        pois = query.limit(50).all()

        logger.info(f"Found {len(pois)} candidate POIs")
        return pois
```

**SQL Query Example**:
```sql
SELECT * FROM goa_places
WHERE category IN ('Beach', 'Heritage')
  AND entry_fee_inr <= 1500  -- (15000/3)*0.3
  AND difficulty_level = 'Easy'
  AND wheelchair_accessible IN ('Yes', 'Partial')
ORDER BY popularity_score DESC
LIMIT 50;
```

**Data Output**:
```python
pois = [
    POI(id='poi_001', name='Calangute Beach', category='Beach', ...),
    POI(id='poi_002', name='Baga Beach', category='Beach', ...),
    POI(id='poi_003', name='Basilica of Bom Jesus', category='Heritage', ...),
    # ... 47 more
]
```

**Data Flows To**: Recommendation Service

---

#### STEP 7: Score POIs (Diagram 5)

**What Happens**: Apply content-based + popularity scoring

**Reference**: Diagram 5 (POI Scoring & Recommendation System)

**Implementation** (`app/services/recommendation_service.py`):
```python
class RecommendationService:
    def score_pois(
        self,
        pois: List[POI],
        user_prefs: Dict,
        context: Dict
    ) -> List[ScoredPOI]:
        """
        Score POIs using hybrid approach:
        - Content-based filtering (40%)
        - Popularity score (30%)
        - Context factors (30%)
        """
        scored_pois = []

        for poi in pois:
            # 1. Content-based score (Diagram 5, Step 1)
            content_score = self._content_based_score(poi, user_prefs)

            # 2. Popularity score (Diagram 5, Step 2)
            popularity_score = poi.popularity_score / 10.0  # Normalize to 0-1

            # 3. Context factors (Diagram 5, Step 3)
            context_score = self._context_score(poi, context)

            # 4. Constraint checking (Diagram 5, Step 4)
            constraint_penalty = self._check_constraints(poi, context)

            # 5. Weighted combination (Diagram 5, Step 5)
            final_score = (
                0.40 * content_score +
                0.30 * popularity_score +
                0.30 * context_score
            ) - constraint_penalty

            scored_pois.append(ScoredPOI(
                poi=poi,
                score=final_score,
                breakdown={
                    'content': content_score,
                    'popularity': popularity_score,
                    'context': context_score,
                    'penalty': constraint_penalty
                }
            ))

        # Sort by score and return top 20
        scored_pois.sort(key=lambda x: x.score, reverse=True)
        return scored_pois[:20]

    def _content_based_score(self, poi: POI, user_prefs: Dict) -> float:
        """Calculate content-based similarity"""
        score = 0.0

        # Category match (50% of content score)
        if poi.category in user_prefs['favorite_categories']:
            score += 0.5

        # Tag matching (30% of content score)
        user_tags = set(user_prefs.get('preferred_tags', []))
        poi_tags = set(poi.instagram_tags or [])
        if user_tags and poi_tags:
            jaccard = len(user_tags & poi_tags) / len(user_tags | poi_tags)
            score += 0.3 * jaccard

        # Accessibility match (20% of content score)
        if 'wheelchair' in user_prefs.get('accessibility_needs', []):
            if poi.wheelchair_accessible == 'Yes':
                score += 0.2
            elif poi.wheelchair_accessible == 'Partial':
                score += 0.1

        return min(score, 1.0)

    def _context_score(self, poi: POI, context: Dict) -> float:
        """Calculate context-based score"""
        score = 0.5  # Base score

        # Time of day (if POI has best_visit_time)
        if poi.best_visit_time and context.get('start_time'):
            if self._time_matches(poi.best_visit_time, context['start_time']):
                score += 0.3

        # Season (if summer, boost water activities)
        if context.get('season') == 'summer' and poi.category == 'Beach':
            score += 0.2

        return min(score, 1.0)

    def _check_constraints(self, poi: POI, context: Dict) -> float:
        """Calculate constraint violations (penalties)"""
        penalty = 0.0

        # Budget violation
        if poi.entry_fee_inr > context.get('max_poi_cost', float('inf')):
            penalty += 0.5

        # Time violation (opening hours)
        if not self._is_open_during(poi, context.get('start_time')):
            penalty += 0.3

        # Already visited
        if poi.id in context.get('visited_pois', []):
            penalty += 0.7  # Heavy penalty for diversity

        return penalty
```

**Data After Scoring**:
```python
scored_pois = [
    ScoredPOI(
        poi=POI(id='poi_001', name='Calangute Beach'),
        score=0.89,
        breakdown={'content': 0.9, 'popularity': 0.9, 'context': 0.8, 'penalty': 0.0}
    ),
    ScoredPOI(
        poi=POI(id='poi_003', name='Basilica'),
        score=0.85,
        breakdown={'content': 0.8, 'popularity': 1.0, 'context': 0.7, 'penalty': 0.0}
    ),
    # ... 18 more
]
```

**Data Flows To**: Optimization Service

---

#### STEP 8: Select Algorithm (Diagram 2, Step 6)

**What Happens**: Algorithm Selector chooses best algorithm

**Implementation** (`app/services/optimization_service.py`):
```python
class OptimizationService:
    def select_algorithm(
        self,
        num_pois: int,
        days: int,
        constraints: Dict
    ) -> str:
        """
        Select optimization algorithm based on problem characteristics
        Reference: Diagram 2, "Select Algorithm" step
        """
        # Small problem (<10 POIs) - use exact method
        if num_pois <= 10:
            return "integer_programming"  # Optimal solution guaranteed

        # Medium problem (10-20 POIs) - use GA
        elif num_pois <= 20:
            return "genetic_algorithm"  # Good balance

        # Large problem (>20 POIs) - use heuristics
        elif num_pois > 20:
            # If multi-day, use Simulated Annealing
            if days > 1:
                return "simulated_annealing"
            # If single day, use Greedy
            else:
                return "greedy"

        # If many constraints, use Tabu Search
        elif len(constraints) > 5:
            return "tabu_search"

        # Default: Genetic Algorithm
        return "genetic_algorithm"
```

**Decision Example**:
```python
# Input: 20 POIs, 3 days, 4 constraints
selected_algorithm = "genetic_algorithm"
```

**Data Flows To**: Distance Calculator

---

#### STEP 9: Build Distance Matrix (Diagram 2, NEW STEP)

**What Happens**: Get all pairwise distances for optimization

**Reference**: Diagram 11, Distance Calculator service

**Implementation** (`app/services/distance_calculator.py`):
```python
class DistanceCalculator:
    def __init__(self, db, redis, google_api_key=None):
        self.db = db
        self.redis = redis
        self.google_api_key = google_api_key

    async def build_distance_matrix(
        self,
        poi_ids: List[str]
    ) -> np.ndarray:
        """
        Build complete distance matrix for POIs
        Returns: NxN matrix where matrix[i][j] = distance(poi_i, poi_j)
        """
        n = len(poi_ids)
        matrix = np.zeros((n, n))

        missing_pairs = []

        # Fill matrix
        for i in range(n):
            for j in range(i+1, n):  # Upper triangle only
                distance = await self.get_distance(poi_ids[i], poi_ids[j])

                if distance is None:
                    missing_pairs.append((poi_ids[i], poi_ids[j]))
                else:
                    matrix[i][j] = distance
                    matrix[j][i] = distance  # Symmetric

        # Calculate missing distances
        if missing_pairs:
            logger.warning(f"Calculating {len(missing_pairs)} missing distances")
            await self._calculate_missing_distances(missing_pairs, matrix, poi_ids)

        return matrix

    async def get_distance(
        self,
        poi_id_1: str,
        poi_id_2: str
    ) -> Optional[float]:
        """
        Get distance between two POIs
        Flow: L3 Cache → Database → Haversine → Google Maps (fallback)
        """
        # Step 1: Check Redis L3 Cache
        cache_key = f"distance:{poi_id_1}:{poi_id_2}"
        cached = await self.redis.get(cache_key)

        if cached:
            logger.debug(f"L3 Cache HIT: {poi_id_1} → {poi_id_2}")
            return float(cached)

        # Step 2: Check distance_matrix table
        db_result = self.db.query(DistanceMatrix).filter(
            or_(
                and_(
                    DistanceMatrix.place_id_from == poi_id_1,
                    DistanceMatrix.place_id_to == poi_id_2
                ),
                and_(
                    DistanceMatrix.place_id_from == poi_id_2,
                    DistanceMatrix.place_id_to == poi_id_1
                )
            )
        ).first()

        if db_result:
            logger.debug(f"Database HIT: {poi_id_1} → {poi_id_2}")
            distance = float(db_result.distance_km)

            # Cache in L3 for 7 days
            await self.redis.setex(cache_key, 604800, str(distance))
            return distance

        # Step 3: Calculate with Haversine (fallback)
        logger.debug(f"MISS: Calculating {poi_id_1} → {poi_id_2}")
        distance = await self._calculate_haversine(poi_id_1, poi_id_2)

        # Store in database
        await self._store_distance(poi_id_1, poi_id_2, distance)

        # Cache in L3
        await self.redis.setex(cache_key, 604800, str(distance))

        return distance

    async def _calculate_haversine(
        self,
        poi_id_1: str,
        poi_id_2: str
    ) -> float:
        """Calculate distance using Haversine formula"""
        # Get POI coordinates
        poi1 = self.db.query(GoaPlace).filter_by(id=poi_id_1).first()
        poi2 = self.db.query(GoaPlace).filter_by(id=poi_id_2).first()

        lat1, lon1 = poi1.latitude, poi1.longitude
        lat2, lon2 = poi2.latitude, poi2.longitude

        # Haversine formula
        R = 6371  # Earth radius in km

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = (math.sin(dlat/2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon/2) ** 2)

        c = 2 * math.asin(math.sqrt(a))
        distance = R * c

        return round(distance, 2)
```

**Data After Distance Calculation**:
```python
# 20x20 distance matrix (km)
distance_matrix = np.array([
    [0.0,  5.2,  12.3, ...],  # Calangute Beach to others
    [5.2,  0.0,  8.1,  ...],  # Baga Beach to others
    [12.3, 8.1,  0.0,  ...],  # Basilica to others
    # ...
])

# Cache status
cache_hits_l3 = 168  # 84% hit rate
database_hits = 22   # 11% hit rate
calculated = 10      # 5% miss rate (Haversine)
```

**Data Flows To**: Algorithm Layer

---

#### STEP 10: Run Optimization - Genetic Algorithm (Diagram 3)

**What Happens**: GA optimizes POI selection and sequencing

**Reference**: Diagram 3 (Genetic Algorithm Flow)

**Implementation** (`app/algorithms/genetic_algorithm.py`):
```python
class GeneticAlgorithm:
    def __init__(self, distance_matrix, pois, constraints):
        self.distance_matrix = distance_matrix
        self.pois = pois
        self.constraints = constraints

        # GA Parameters (Diagram 3, Step 1)
        self.population_size = 50
        self.generations = 100
        self.mutation_rate = 0.2
        self.crossover_rate = 0.8
        self.elite_size = 2

    def optimize(self) -> Tuple[List[int], float]:
        """
        Run genetic algorithm optimization
        Returns: (route_indices, fitness_score)
        """
        # Step 1: Generate initial population (Diagram 3, Step 2)
        population = self._generate_initial_population()

        best_solution = None
        best_fitness = float('-inf')

        # Generation loop (Diagram 3, main loop)
        for generation in range(self.generations):
            # Step 2: Evaluate fitness (Diagram 3, Step 3)
            fitness_scores = [
                self._evaluate_fitness(chromosome)
                for chromosome in population
            ]

            # Track best solution (Diagram 3, "Track Best")
            gen_best_idx = np.argmax(fitness_scores)
            if fitness_scores[gen_best_idx] > best_fitness:
                best_fitness = fitness_scores[gen_best_idx]
                best_solution = population[gen_best_idx].copy()

            # Check convergence
            if self._has_converged(fitness_scores, generation):
                logger.info(f"Converged at generation {generation}")
                break

            # Step 3: Selection (Diagram 3, Selection step)
            parents = self._tournament_selection(population, fitness_scores)

            # Step 4: Crossover (Diagram 3, Crossover step)
            offspring = self._crossover(parents)

            # Step 5: Mutation (Diagram 3, Mutation step)
            offspring = self._mutate(offspring)

            # Step 6: Replace population (Diagram 3, Replace step)
            population = self._elitism(population, offspring, fitness_scores)

        return best_solution, best_fitness

    def _generate_initial_population(self) -> List[List[int]]:
        """Generate initial population with greedy seeding"""
        population = []

        # 20% greedy-seeded (smart start)
        for _ in range(int(self.population_size * 0.2)):
            chromosome = self._greedy_chromosome()
            population.append(chromosome)

        # 80% random
        for _ in range(self.population_size - len(population)):
            chromosome = self._random_chromosome()
            population.append(chromosome)

        return population

    def _evaluate_fitness(self, chromosome: List[int]) -> float:
        """
        Fitness function (multi-objective)
        Higher is better
        """
        # Decode chromosome to route
        route = [i for i, gene in enumerate(chromosome) if gene == 1]

        if len(route) == 0:
            return -1000  # Invalid

        # Calculate objectives
        satisfaction = sum(self.pois[i].score for i in route) / len(route)

        # Calculate total distance
        total_distance = 0
        for i in range(len(route) - 1):
            total_distance += self.distance_matrix[route[i]][route[i+1]]

        # Calculate total time
        total_time = sum(self.pois[i].duration_minutes for i in route)
        total_time += total_distance * 2  # Travel time (30 km/h = 2 min/km)

        # Calculate total cost
        total_cost = sum(self.pois[i].entry_fee_inr for i in route)

        # Fitness = weighted sum
        fitness = (
            0.50 * satisfaction +
            0.20 * (1 - total_distance / 200) +  # Minimize distance
            0.15 * (1 - total_time / self.constraints['max_time']) +
            0.15 * (1 - total_cost / self.constraints['budget'])
        )

        # Constraint penalties
        if total_time > self.constraints['max_time']:
            fitness *= 0.5
        if total_cost > self.constraints['budget']:
            fitness *= 0.5

        return fitness

    def _crossover(self, parents: List[List[int]]) -> List[List[int]]:
        """Order crossover (OX) for route optimization"""
        offspring = []

        for i in range(0, len(parents), 2):
            if i + 1 < len(parents):
                if random.random() < self.crossover_rate:
                    child1, child2 = self._order_crossover(
                        parents[i],
                        parents[i+1]
                    )
                    offspring.extend([child1, child2])
                else:
                    offspring.extend([parents[i], parents[i+1]])

        return offspring

    def _mutate(self, offspring: List[List[int]]) -> List[List[int]]:
        """Swap mutation"""
        for chromosome in offspring:
            if random.random() < self.mutation_rate:
                # Swap two genes
                idx1, idx2 = random.sample(range(len(chromosome)), 2)
                chromosome[idx1], chromosome[idx2] = (
                    chromosome[idx2],
                    chromosome[idx1]
                )
        return offspring
```

**GA Evolution Example**:
```python
# Generation 0 (random)
best_fitness = 0.45
best_route = [0, 5, 12, 8, 15]  # Random sequence

# Generation 25
best_fitness = 0.68  # Improving
best_route = [0, 2, 5, 8, 12, 15]  # Better sequence

# Generation 50
best_fitness = 0.82  # Good
best_route = [0, 2, 5, 8, 12, 15, 18]  # Optimal?

# Generation 75 - CONVERGED
best_fitness = 0.89  # Excellent
best_route = [0, 1, 3, 5, 8, 10, 12, 15, 18, 19]  # Final
```

**Data After Optimization**:
```python
optimized_result = {
    'poi_indices': [0, 1, 3, 5, 8, 10, 12, 15, 18, 19],  # 10 POIs selected
    'fitness_score': 0.89,
    'total_distance_km': 87.5,
    'total_duration_minutes': 425,
    'total_cost_inr': 1200,
    'generations_run': 75,
    'converged': True
}
```

**Data Flows To**: Optimization Service (Multi-Day Planning)

---

#### STEP 11: Multi-Day Planning (Diagram 4)

**What Happens**: Split optimized POIs across 3 days

**Reference**: Diagram 4 (Multi-Day Itinerary Optimization)

**Implementation**:
```python
class MultiDayPlanner:
    def split_into_days(
        self,
        poi_route: List[POI],
        days: int,
        constraints: Dict
    ) -> List[DayItinerary]:
        """
        Split route into multi-day itinerary
        Reference: Diagram 4
        """
        # Step 1: Geographic clustering (Diagram 4, Step 2)
        clusters = self._geographic_clustering(poi_route)
        # Clusters: {'North': [POI1, POI2], 'South': [POI8, POI9], ...}

        # Step 2: Allocate clusters to days
        day_itineraries = []
        daily_budget = constraints['budget'] / days
        daily_time = constraints['max_daily_duration_minutes']

        for day_num in range(1, days + 1):
            # Select region for this day (minimize inter-region travel)
            region = self._select_region_for_day(
                clusters,
                day_num,
                used_regions=[d.region for d in day_itineraries]
            )

            # Get POIs for this region
            day_pois = clusters[region]

            # Optimize single day (Diagram 4, Step 5)
            day_route = self._optimize_single_day(
                day_pois,
                daily_budget,
                daily_time
            )

            # Create day itinerary
            day_itineraries.append(DayItinerary(
                day=day_num,
                region=region,
                pois=day_route,
                total_distance=self._calc_distance(day_route),
                total_duration=self._calc_duration(day_route),
                total_cost=sum(poi.entry_fee_inr for poi in day_route)
            ))

        return day_itineraries

    def _geographic_clustering(self, pois: List[POI]) -> Dict[str, List[POI]]:
        """Cluster POIs by geographic region"""
        clusters = {'North': [], 'South': [], 'Central': []}

        for poi in pois:
            if poi.latitude > 15.45:  # North Goa
                clusters['North'].append(poi)
            elif poi.latitude < 15.15:  # South Goa
                clusters['South'].append(poi)
            else:  # Central Goa
                clusters['Central'].append(poi)

        return {k: v for k, v in clusters.items() if v}  # Remove empty
```

**Data After Multi-Day Split**:
```python
multi_day_itinerary = [
    DayItinerary(
        day=1,
        region='North',
        pois=[
            POI(name='Calangute Beach', arrival='09:00', departure='11:00'),
            POI(name='Baga Beach', arrival='11:15', departure='13:15'),
            POI(name='Anjuna Flea Market', arrival='14:00', departure='16:00'),
        ],
        total_distance_km=28.5,
        total_duration_minutes=420,
        total_cost_inr=500
    ),
    DayItinerary(
        day=2,
        region='Central',
        pois=[
            POI(name='Basilica of Bom Jesus', arrival='09:00', departure='10:30'),
            POI(name='Se Cathedral', arrival='10:45', departure='12:00'),
            POI(name='Fort Aguada', arrival='14:00', departure='16:00'),
        ],
        total_distance_km=35.2,
        total_duration_minutes=405,
        total_cost_inr=200
    ),
    DayItinerary(
        day=3,
        region='South',
        pois=[
            POI(name='Palolem Beach', arrival='09:30', departure='12:30'),
            POI(name='Cabo de Rama Fort', arrival='13:30', departure='15:00'),
            POI(name='Butterfly Beach', arrival='15:30', departure='17:00'),
        ],
        total_distance_km=42.8,
        total_duration_minutes=450,
        total_cost_inr=300
    )
]
```

**Data Flows To**: Map Service

---

#### STEP 12: Enrich with Map Data (Diagram 2, Updated Step)

**What Happens**: Get directions and route geometry from Google Maps

**Implementation** (`app/services/map_service.py`):
```python
class MapService:
    def __init__(self, google_api_key):
        self.api_key = google_api_key
        self.base_url = "https://maps.googleapis.com/maps/api"

    async def enrich_itinerary(
        self,
        day_itineraries: List[DayItinerary]
    ) -> List[EnrichedDayItinerary]:
        """
        Get map data for each day's route
        Reference: Diagram 2, "Enrich Itinerary" step
        """
        enriched = []

        for day in day_itineraries:
            # Build waypoints
            waypoints = [
                {'lat': poi.latitude, 'lng': poi.longitude}
                for poi in day.pois
            ]

            # Get directions from Google Maps
            directions = await self._get_directions(waypoints)

            # Get route geometry (polyline)
            polyline = directions['routes'][0]['overview_polyline']['points']

            # Get turn-by-turn steps
            steps = self._extract_steps(directions)

            # Get POI photos
            photos = await self._get_poi_photos(day.pois)

            enriched.append(EnrichedDayItinerary(
                day=day.day,
                pois=day.pois,
                polyline=polyline,  # For map rendering
                steps=steps,  # Turn-by-turn
                photos=photos,
                total_distance_km=day.total_distance_km,
                total_duration_minutes=day.total_duration_minutes,
                total_cost_inr=day.total_cost_inr
            ))

        return enriched

    async def _get_directions(self, waypoints: List[Dict]) -> Dict:
        """Call Google Maps Directions API"""
        # Build request
        origin = f"{waypoints[0]['lat']},{waypoints[0]['lng']}"
        destination = f"{waypoints[-1]['lat']},{waypoints[-1]['lng']}"

        # Middle waypoints
        waypoints_str = "|".join([
            f"{wp['lat']},{wp['lng']}"
            for wp in waypoints[1:-1]
        ])

        url = (
            f"{self.base_url}/directions/json"
            f"?origin={origin}"
            f"&destination={destination}"
            f"&waypoints=optimize:true|{waypoints_str}"
            f"&key={self.api_key}"
        )

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()
```

**Data After Enrichment**:
```python
enriched_itinerary = [
    EnrichedDayItinerary(
        day=1,
        pois=[...],
        polyline="a~l~Fjk~uOnqC...",  # Encoded polyline
        steps=[
            {
                'instruction': 'Head north on NH66',
                'distance': '5.2 km',
                'duration': '8 mins',
                'polyline': '...'
            },
            # ... more steps
        ],
        photos={
            'poi_001': [
                'https://maps.googleapis.com/maps/api/place/photo?photoreference=...',
                # ... more photos
            ]
        },
        total_distance_km=28.5,
        total_duration_minutes=420,
        total_cost_inr=500
    ),
    # Day 2, Day 3...
]
```

**Data Flows To**: Route Service (final assembly)

---

#### STEP 13: Save to Database

**What Happens**: Store complete itinerary in user_routes table

**Implementation**:
```python
# Save to database
new_route = UserRoute(
    id=uuid.uuid4(),
    user_id=request.user_id,
    route_name=f"3-Day Goa Trip - {datetime.now().strftime('%b %d')}",
    place_ids=[poi.id for day in enriched_itinerary for poi in day.pois],
    total_distance_km=sum(day.total_distance_km for day in enriched_itinerary),
    total_duration_minutes=sum(day.total_duration_minutes for day in enriched_itinerary),
    estimated_cost_inr=sum(day.total_cost_inr for day in enriched_itinerary),
    preferences=request.preferences.dict(),  # Store as JSONB
    multi_day_data=json.dumps([day.dict() for day in enriched_itinerary]),
    created_at=datetime.utcnow()
)

db.add(new_route)
db.commit()
```

**Data Flows To**: Redis L1 Cache

---

#### STEP 14: Cache Result

**What Happens**: Store in L1 cache for future requests

**Implementation**:
```python
# Cache complete response for 1 hour
cache_key = cache_service.generate_cache_key(request)

final_response = {
    'route_id': str(new_route.id),
    'user_id': request.user_id,
    'created_at': new_route.created_at.isoformat(),
    'days': enriched_itinerary,
    'summary': {
        'total_pois': len(new_route.place_ids),
        'total_distance_km': new_route.total_distance_km,
        'total_duration_minutes': new_route.total_duration_minutes,
        'estimated_cost_inr': new_route.estimated_cost_inr
    }
}

await redis.setex(
    cache_key,
    3600,  # 1 hour TTL
    json.dumps(final_response)
)
```

**Data Flows To**: API Response

---

#### STEP 15: Return to User

**What Happens**: Send JSON response through API Gateway to UI

**Response Format**:
```json
{
  "status": "success",
  "route_id": "route_xyz789",
  "user_id": "user_abc123",
  "created_at": "2025-11-16T14:30:00Z",
  "days": [
    {
      "day": 1,
      "region": "North",
      "date": "2025-12-01",
      "pois": [
        {
          "id": "poi_001",
          "name": "Calangute Beach",
          "category": "Beach",
          "arrival_time": "09:00",
          "departure_time": "11:00",
          "duration_minutes": 120,
          "entry_fee_inr": 0,
          "location": {
            "latitude": 15.5467,
            "longitude": 73.7634
          },
          "photos": [
            "https://maps.googleapis.com/maps/api/place/photo?..."
          ]
        }
        // ... more POIs for Day 1
      ],
      "route": {
        "polyline": "a~l~Fjk~uOnqC...",
        "total_distance_km": 28.5,
        "total_duration_minutes": 420,
        "total_cost_inr": 500,
        "steps": [
          {
            "instruction": "Head north on NH66",
            "distance": "5.2 km",
            "duration": "8 mins"
          }
          // ... more navigation steps
        ]
      }
    }
    // Day 2, Day 3...
  ],
  "summary": {
    "total_pois": 10,
    "total_distance_km": 106.5,
    "total_duration_minutes": 1275,
    "estimated_cost_inr": 1000,
    "avg_popularity_score": 8.7
  },
  "alternatives": [
    // Alternative route 1
    // Alternative route 2
  ]
}
```

**UI Rendering** (`src/components/Itinerary.jsx`):
```javascript
function ItineraryView({ itinerary }) {
  return (
    <div className="itinerary-container">
      {/* Summary Card */}
      <Summary data={itinerary.summary} />

      {/* Map View */}
      <MapView
        polyline={itinerary.days[0].route.polyline}
        pois={itinerary.days[0].pois}
      />

      {/* Day-by-Day Timeline */}
      {itinerary.days.map(day => (
        <DayCard key={day.day} day={day} />
      ))}

      {/* Alternatives */}
      <Alternatives routes={itinerary.alternatives} />
    </div>
  );
}
```

---

### Data Flow Summary for Flow 1

**Total Steps**: 15
**Total Time** (cold cache): 8-12 seconds
**Total Time** (warm cache): 200-500ms

**Data Transformations**:
```
User Input (JSON)
  ↓ Pydantic validation
Validated Request Object
  ↓ POI Service
List of POI Objects
  ↓ Recommendation Service
Scored POI List
  ↓ Distance Calculator
Distance Matrix (NumPy array)
  ↓ Genetic Algorithm
Optimized Route (POI indices)
  ↓ Multi-Day Planner
3 Day Itineraries
  ↓ Map Service
Enriched Itineraries (with directions)
  ↓ JSON serialization
Final Response (JSON)
```

**Services Used**: 9/9
- ✅ Route Service (orchestration)
- ✅ User Service (preferences)
- ✅ POI Service (fetch candidates)
- ✅ Recommendation Service (scoring)
- ✅ Distance Calculator (matrix building)
- ✅ Optimization Service (GA + multi-day)
- ✅ Map Service (directions)
- ✅ Redis (L1, L2, L3 caching)
- ✅ PostgreSQL (data storage)

**Cache Hit Rates**:
- L1 (Routes): ~45% hit rate
- L2 (POIs): ~85% hit rate
- L3 (Distances): ~84% hit rate

---

## FLOW 2: REAL-TIME WEATHER ADAPTATION

**Use Case**: Rain starts in North Goa, user has active itinerary

**Reference**: Diagram 6 (Real-Time Adaptation Flow)

### Detailed Flow

#### STEP 1: Weather Polling (Background Process)

**What Happens**: Weather Monitor polls OpenWeather API every 30 minutes

**Implementation** (`app/services/weather_monitor.py`):
```python
import asyncio
from datetime import datetime, timedelta

class WeatherMonitor:
    def __init__(self, openweather_api_key, redis, db):
        self.api_key = openweather_api_key
        self.redis = redis
        self.db = db
        self.base_url = "https://api.openweathermap.org/data/2.5"

        # Goa regions to monitor
        self.regions = {
            'north': {'lat': 15.55, 'lon': 73.76, 'name': 'North Goa'},
            'central': {'lat': 15.30, 'lon': 74.00, 'name': 'Central Goa'},
            'south': {'lat': 15.00, 'lon': 73.93, 'name': 'South Goa'}
        }

    async def start_monitoring(self):
        """Start background monitoring (runs forever)"""
        logger.info("Starting weather monitoring...")

        while True:
            try:
                await self._check_all_regions()
                await asyncio.sleep(1800)  # 30 minutes
            except Exception as e:
                logger.error(f"Weather monitoring error: {e}")
                await asyncio.sleep(60)  # Retry after 1 min

    async def _check_all_regions(self):
        """Check weather for all Goa regions"""
        for region_id, region_data in self.regions.items():
            current_weather = await self._fetch_weather(
                region_data['lat'],
                region_data['lon']
            )

            # Get cached previous weather
            cache_key = f"weather:{region_id}:current"
            cached_weather = await self.redis.get(cache_key)

            if cached_weather:
                previous_weather = json.loads(cached_weather)

                # Detect significant changes
                if self._is_significant_change(previous_weather, current_weather):
                    logger.warning(
                        f"Significant weather change in {region_data['name']}: "
                        f"{previous_weather['condition']} → {current_weather['condition']}"
                    )

                    # Trigger adaptation for affected routes
                    await self._trigger_adaptation(region_id, current_weather)

            # Update cache
            await self.redis.setex(
                cache_key,
                7200,  # 2 hours
                json.dumps(current_weather)
            )

    async def _fetch_weather(self, lat: float, lon: float) -> Dict:
        """Fetch current weather from OpenWeather API"""
        url = (
            f"{self.base_url}/weather"
            f"?lat={lat}&lon={lon}"
            f"&appid={self.api_key}"
            f"&units=metric"
        )

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()

        return {
            'condition': data['weather'][0]['main'].lower(),  # 'clear', 'rain', 'clouds'
            'description': data['weather'][0]['description'],
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'timestamp': datetime.utcnow().isoformat()
        }

    def _is_significant_change(self, old: Dict, new: Dict) -> bool:
        """
        Detect significant weather changes that require route adaptation
        Reference: Diagram 6, "Event Detection" step
        """
        # Clear to Rain (major change)
        if old['condition'] == 'clear' and new['condition'] == 'rain':
            return True

        # Rain to Clear (major change)
        if old['condition'] == 'rain' and new['condition'] == 'clear':
            return True

        # Temperature change > 10°C
        if abs(old['temperature'] - new['temperature']) > 10:
            return True

        # Extreme heat (> 35°C)
        if new['temperature'] > 35 and old['temperature'] <= 35:
            return True

        return False

    async def _trigger_adaptation(self, region_id: str, new_weather: Dict):
        """
        Trigger route adaptation for affected users
        Reference: Diagram 6, "Trigger Re-optimization" step
        """
        # Find active routes in this region
        affected_routes = await self._find_affected_routes(region_id)

        logger.info(f"Found {len(affected_routes)} affected routes")

        for route in affected_routes:
            # Assess severity
            severity = self._assess_severity(new_weather)

            if severity == 'minor':
                # Just log, don't notify
                logger.info(f"Minor weather change for route {route.id}")
                continue

            elif severity in ['major', 'critical']:
                # Generate alternative route
                alternatives = await self._generate_alternatives(
                    route,
                    new_weather
                )

                # Notify user
                await self._notify_user(route, new_weather, alternatives)
```

**Data Flow**: OpenWeather API → Weather Monitor → Redis → Adaptation Trigger

---

#### STEP 2: Find Affected Routes

**Implementation**:
```python
async def _find_affected_routes(self, region_id: str) -> List[UserRoute]:
    """Find active routes with POIs in affected region"""
    # Define region boundaries
    if region_id == 'north':
        lat_min, lat_max = 15.45, 15.65
    elif region_id == 'central':
        lat_min, lat_max = 15.15, 15.45
    else:  # south
        lat_min, lat_max = 14.90, 15.15

    # Get active routes (started but not completed)
    now = datetime.utcnow()
    active_routes = self.db.query(UserRoute).filter(
        UserRoute.status == 'active',
        UserRoute.start_date <= now,
        UserRoute.end_date >= now
    ).all()

    affected = []
    for route in active_routes:
        # Check if any POI in route is in affected region
        for poi_id in route.place_ids:
            poi = self.db.query(GoaPlace).filter_by(id=poi_id).first()
            if lat_min <= poi.latitude <= lat_max:
                affected.append(route)
                break

    return affected
```

**Data Output**:
```python
affected_routes = [
    UserRoute(
        id='route_abc123',
        user_id='user_xyz',
        current_poi_index=2,  # Currently at POI 2 of 8
        place_ids=['poi_001', 'poi_002', 'poi_003', ...],
        status='active'
    )
]
```

---

#### STEP 3: Generate Alternatives (Diagram 6, "Generate Alternatives")

**Implementation**:
```python
async def _generate_alternatives(
    self,
    route: UserRoute,
    new_weather: Dict
) -> List[AlternativeRoute]:
    """
    Generate alternative routes based on weather
    Reference: Diagram 6, "Generate Alternatives" step
    """
    alternatives = []

    if new_weather['condition'] == 'rain':
        # Option 1: Skip outdoor POIs, add indoor alternatives
        indoor_route = await self._create_indoor_route(route)
        alternatives.append(indoor_route)

        # Option 2: Postpone outdoor POIs to later in the day
        postponed_route = await self._postpone_outdoor(route)
        alternatives.append(postponed_route)

        # Option 3: Continue current route (for reference)
        alternatives.append({
            'type': 'continue',
            'description': 'Continue with current route',
            'changes': []
        })

    return alternatives

async def _create_indoor_route(self, route: UserRoute) -> Dict:
    """Create alternative with indoor POIs"""
    # Get remaining POIs from current position
    remaining_poi_ids = route.place_ids[route.current_poi_index:]
    remaining_pois = [
        self.db.query(GoaPlace).filter_by(id=pid).first()
        for pid in remaining_poi_ids
    ]

    # Separate indoor and outdoor
    indoor = [poi for poi in remaining_pois if poi.category in ['Museum', 'Temple', 'Church']]
    outdoor = [poi for poi in remaining_pois if poi.category in ['Beach', 'Fort']]

    # Find additional indoor POIs nearby
    current_poi = remaining_pois[0] if remaining_pois else None
    if current_poi:
        nearby_indoor = self.db.query(GoaPlace).filter(
            GoaPlace.category.in_(['Museum', 'Temple', 'Church']),
            GoaPlace.id.notin_(route.place_ids),
            func.ST_DWithin(
                GoaPlace.location,
                current_poi.location,
                10000  # Within 10km
            )
        ).limit(3).all()

        indoor.extend(nearby_indoor)

    # Re-optimize indoor route
    optimized = await self._quick_optimize(indoor)

    return {
        'type': 'indoor',
        'description': 'Rain-friendly route with indoor attractions',
        'pois': optimized,
        'skipped_pois': [poi.id for poi in outdoor],
        'added_pois': [poi.id for poi in nearby_indoor]
    }
```

**Data Output**:
```python
alternatives = [
    {
        'type': 'indoor',
        'description': 'Rain-friendly route with indoor attractions',
        'pois': [
            POI(name='Basilica of Bom Jesus', category='Church'),
            POI(name='Goa State Museum', category='Museum'),
            POI(name='Shantadurga Temple', category='Temple')
        ],
        'skipped_pois': ['poi_001', 'poi_005'],  # Beaches
        'added_pois': ['poi_012', 'poi_015'],  # Museums
        'estimated_time_saved': 45,  # minutes
        'updated_cost': 300  # INR
    },
    {
        'type': 'postpone',
        'description': 'Postpone beach visits to evening',
        'changes': [
            {'poi': 'Calangute Beach', 'new_time': '16:00 (was 11:00)'},
            {'poi': 'Baga Beach', 'new_time': '17:30 (was 13:00)'}
        ]
    },
    {
        'type': 'continue',
        'description': 'Continue with current route (bring umbrella!)',
        'changes': []
    }
]
```

---

#### STEP 4: Notify User (Diagram 6, "Notify User")

**What Happens**: Send notification via WebSocket, Push, or Email

**Implementation** (`app/services/notification_service.py`):
```python
class NotificationService:
    def __init__(self, redis, websocket_manager, push_service, email_service):
        self.redis = redis
        self.websocket = websocket_manager
        self.push = push_service
        self.email = email_service

    async def notify_route_change(
        self,
        route: UserRoute,
        reason: str,
        alternatives: List[Dict]
    ):
        """
        Send multi-channel notification
        Reference: Diagram 6, "Notify User" step
        """
        user_id = route.user_id

        # Build notification payload
        notification = {
            'type': 'route_update',
            'route_id': str(route.id),
            'reason': reason,
            'severity': 'major',
            'alternatives': alternatives,
            'timestamp': datetime.utcnow().isoformat()
        }

        # 1. WebSocket (real-time, if user online)
        if await self._is_user_online(user_id):
            await self.websocket.send_to_user(user_id, notification)
            logger.info(f"WebSocket notification sent to {user_id}")

        # 2. Push Notification (mobile app)
        push_token = await self._get_push_token(user_id)
        if push_token:
            await self.push.send({
                'to': push_token,
                'title': 'Weather Alert',
                'body': f'{reason}. Tap to see alternative routes.',
                'data': notification
            })
            logger.info(f"Push notification sent to {user_id}")

        # 3. Email (fallback, or if user prefers)
        user_email = await self._get_user_email(user_id)
        if user_email:
            await self.email.send({
                'to': user_email,
                'subject': 'Your WanderWise Route Updated',
                'template': 'route_update.html',
                'context': {
                    'reason': reason,
                    'alternatives': alternatives,
                    'route_name': route.route_name
                }
            })
            logger.info(f"Email sent to {user_email}")

    async def _is_user_online(self, user_id: str) -> bool:
        """Check if user has active WebSocket connection"""
        connection_key = f"ws:connection:{user_id}"
        return await self.redis.exists(connection_key)
```

**WebSocket Payload**:
```json
{
  "type": "route_update",
  "route_id": "route_abc123",
  "reason": "Rain started in North Goa",
  "severity": "major",
  "alternatives": [
    {
      "type": "indoor",
      "description": "Rain-friendly route with indoor attractions",
      "pois": [...]
    }
  ],
  "timestamp": "2025-11-16T11:45:00Z"
}
```

**UI Handling** (`src/components/RouteUpdateModal.jsx`):
```javascript
useEffect(() => {
  const ws = new WebSocket('ws://api.wanderwise.com/ws');

  ws.onmessage = (event) => {
    const notification = JSON.parse(event.data);

    if (notification.type === 'route_update') {
      // Show modal with alternatives
      setShowAlternativesModal(true);
      setAlternatives(notification.alternatives);
    }
  };
}, []);
```

---

#### STEP 5: User Response

**What Happens**: User selects alternative from UI

**UI Action**:
```javascript
async function handleAlternativeSelection(alternative) {
  const response = await fetch(`/api/v1/routes/${routeId}/update`, {
    method: 'PATCH',
    body: JSON.stringify({
      alternative_type: alternative.type,
      updated_pois: alternative.pois.map(p => p.id)
    })
  });

  if (response.ok) {
    // Update local state
    setCurrentRoute(await response.json());
    setShowAlternativesModal(false);
  }
}
```

---

#### STEP 6: Update Route (Diagram 6, "Update Itinerary")

**Implementation**:
```python
@router.patch("/routes/{route_id}/update")
async def update_route(
    route_id: str,
    update: RouteUpdateRequest,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    """Update route with user-selected alternative"""
    # Get route
    route = db.query(UserRoute).filter_by(id=route_id).first()

    # Update POIs
    route.place_ids = update.updated_pois

    # Recalculate metadata
    route.total_distance_km = calculate_total_distance(update.updated_pois)
    route.total_duration_minutes = calculate_total_duration(update.updated_pois)
    route.total_cost_inr = calculate_total_cost(update.updated_pois)

    # Mark as modified
    route.updated_at = datetime.utcnow()
    route.adaptation_count = route.adaptation_count + 1

    db.commit()

    # Invalidate L1 cache
    cache_key = f"route:{route_id}"
    await redis.delete(cache_key)

    return {'status': 'success', 'route': route.to_dict()}
```

---

### Flow 2 Summary

**Total Time**: 3-5 seconds (from weather change to user notification)

**Data Flow**:
```
OpenWeather API (poll every 30min)
  ↓
Weather Monitor (detect change)
  ↓
Find Affected Routes (database query)
  ↓
Generate Alternatives (re-optimization)
  ↓
Notification Service (WebSocket/Push/Email)
  ↓
User Response (UI selection)
  ↓
Update Route (database + cache invalidation)
```

---

## FLOW 3: POI RECOMMENDATION & SCORING

**Use Case**: Score POIs based on user preferences

**Reference**: Diagram 5 (POI Scoring & Recommendation System), Diagram 10 (User Preference Learning)

[Continue with detailed implementation for remaining flows...]

---

## QUICK REFERENCE TABLE

### Which Diagram to Use When

| Scenario | Use This Diagram | Why |
|----------|------------------|-----|
| Building itinerary generation endpoint | Diagram 2, 11 | Complete workflow + service interactions |
| Implementing Genetic Algorithm | Diagram 3 | Step-by-step GA flow |
| Multi-day route splitting | Diagram 4 | Day-by-day optimization logic |
| POI scoring logic | Diagram 5 | Hybrid scoring approach |
| Weather-triggered updates | Diagram 6 | Real-time adaptation flow |
| Data import/ETL | Diagram 7 | Data collection to storage |
| Constraint validation | Diagram 8 | Hard/soft constraint checking |
| Implementing Redis caching | Diagram 9 | 3-level cache strategy |
| User preference modeling | Diagram 10 | Preference fusion approach |
| Debugging data flow | Diagram 11 | Complete service interaction map |

### Service Communication Patterns

```
Request Pattern: Client → Nginx → Service
Response Pattern: Service → Nginx → Client
Cache Pattern: Service → Redis → Database
Async Pattern: Service → Queue → Background Worker
Event Pattern: Monitor → Event → Notification
```

---

**Document Version**: 1.0
**Last Updated**: November 16, 2025
**Total Flows Documented**: 2/8 (Comprehensive)
**Ready for**: Implementation Phase

**Next**: Continue documenting Flows 3-8 for complete coverage
