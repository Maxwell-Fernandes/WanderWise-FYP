# WanderWise Implementation Roadmap
## Senior Software Engineer's Perspective

**Project Status:** Design Complete → Ready for Implementation
**Starting Point:** Production-ready database schema + High-quality dataset
**Goal:** Build working MVP incrementally

---

## Phase 1: Foundation (Week 1-2) - CRITICAL PATH

### 1.1 Database Setup & Data Import ⭐ START HERE

**Priority:** CRITICAL
**Effort:** 2-3 days
**Dependencies:** None

#### Tasks:
```bash
✅ Set up PostgreSQL 12+ with PostGIS
✅ Run database_setup.sql
✅ Import CSV data (100 destinations)
✅ Verify spatial queries work
✅ Populate distance matrix
✅ Test stored functions
```

#### Deliverables:
- Working database with 100 destinations
- Pre-computed distance matrix (~10,000 entries)
- Verified spatial indexes

#### Implementation:
```python
# scripts/import_csv_data.py (NEW FILE TO CREATE)
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

def import_places():
    """Import CSV data into goa_places table"""
    df = pd.read_csv('Wanderwise_datasetnew.csv')

    # Convert pipe-delimited strings to arrays
    df['facilities_array'] = df['facilities'].str.split('|')
    df['instagram_tags_array'] = df['instagram_tags'].str.split('|')
    df['best_for_array'] = df['best_for'].str.split('|')

    # Insert into database
    # ... (full implementation)

    print(f"✅ Imported {len(df)} destinations")
```

**Success Criteria:**
- ✅ Query: `SELECT COUNT(*) FROM goa_places;` returns 100
- ✅ Spatial search works: `SELECT * FROM find_nearby_places(15.5, 73.8, 10);`
- ✅ Distance matrix populated: `SELECT COUNT(*) FROM distance_matrix;`

---

### 1.2 Basic Backend API (FastAPI) ⭐ MVP

**Priority:** CRITICAL
**Effort:** 3-4 days
**Dependencies:** Database setup

#### Tasks:
```bash
✅ Create FastAPI project structure
✅ Database connection with SQLAlchemy + GeoAlchemy2
✅ Implement 5 core endpoints
✅ Basic error handling
✅ CORS configuration
```

#### File Structure to Create:
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app
│   ├── config.py              # Settings
│   ├── database.py            # DB connection
│   ├── models/
│   │   ├── __init__.py
│   │   └── places.py          # SQLAlchemy models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── places.py          # Pydantic schemas
│   └── api/
│       ├── __init__.py
│       └── places.py          # Endpoints
├── scripts/
│   └── import_csv_data.py     # CSV import
├── requirements.txt
├── .env.example
└── README.md
```

#### Core Endpoints (MVP):
```python
# 1. Health check
GET /
Response: {"status": "ok", "message": "WanderWise API"}

# 2. List all places (paginated)
GET /api/v1/places?limit=20&offset=0&category=Beach
Response: {
    "total": 100,
    "items": [...],
    "limit": 20,
    "offset": 0
}

# 3. Get place by ID
GET /api/v1/places/{place_id}
Response: {
    "id": "uuid",
    "name": "Calangute Beach",
    "category": "Beach",
    "latitude": 15.5445,
    "longitude": 73.7551,
    ...
}

# 4. Search places (full-text)
GET /api/v1/places/search?q=beach&limit=10
Response: {
    "results": [...],
    "query": "beach",
    "count": 25
}

# 5. Find nearby places
GET /api/v1/places/nearby?lat=15.5&lon=73.8&radius=10
Response: {
    "center": {"lat": 15.5, "lon": 73.8},
    "radius_km": 10,
    "places": [...]
}
```

#### Dependencies (requirements.txt):
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
geoalchemy2==0.14.3
psycopg2-binary==2.9.9
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0
```

**Success Criteria:**
- ✅ API runs: `uvicorn app.main:app --reload`
- ✅ Health check works: `curl http://localhost:8000/`
- ✅ Can retrieve all beaches: `GET /api/v1/places?category=Beach`
- ✅ Spatial search works: `GET /api/v1/places/nearby?lat=15.5&lon=73.8&radius=10`

---

### 1.3 Basic Testing ⭐ QUALITY GATE

**Priority:** HIGH
**Effort:** 2 days
**Dependencies:** Backend API

#### Tasks:
```bash
✅ Set up pytest
✅ Write database tests
✅ Write API endpoint tests
✅ Test spatial queries
```

#### Test Files to Create:
```
backend/
└── tests/
    ├── __init__.py
    ├── conftest.py            # Fixtures
    ├── test_database.py       # DB tests
    └── test_api_places.py     # API tests
```

#### Sample Tests:
```python
# test_api_places.py
def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_list_places(client):
    response = client.get("/api/v1/places?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 100
    assert len(data["items"]) == 10

def test_nearby_search(client):
    response = client.get("/api/v1/places/nearby?lat=15.5&lon=73.8&radius=10")
    assert response.status_code == 200
    data = response.json()
    assert "places" in data
    assert all(p["distance_km"] <= 10 for p in data["places"])
```

**Success Criteria:**
- ✅ All tests pass: `pytest -v`
- ✅ Coverage > 80%: `pytest --cov=app`

---

## Phase 2: Route Optimization (Week 3-4) - CORE VALUE

### 2.1 Simple TSP Solver ⭐ KEY FEATURE

**Priority:** HIGH
**Effort:** 4-5 days
**Dependencies:** Backend API

#### Tasks:
```bash
✅ Install python-tsp library
✅ Implement basic TSP solver
✅ Create route optimization endpoint
✅ Add distance matrix lookup
✅ Handle time constraints
```

#### New Files:
```
backend/app/
├── services/
│   ├── __init__.py
│   └── route_optimizer.py     # TSP implementation
└── api/
    └── routes.py              # Route endpoints
```

#### Implementation Strategy:
```python
# services/route_optimizer.py
from python_tsp.exact import solve_tsp_dynamic_programming
from python_tsp.heuristics import solve_tsp_simulated_annealing

class RouteOptimizer:
    def optimize_route(self, place_ids: List[str]) -> Dict:
        """
        Optimize route using TSP solver

        Strategy:
        - If <= 10 places: Use exact DP solution
        - If > 10 places: Use simulated annealing (heuristic)
        """
        # 1. Get distance matrix from database
        distance_matrix = self.get_distance_matrix(place_ids)

        # 2. Choose solver based on size
        if len(place_ids) <= 10:
            permutation, distance = solve_tsp_dynamic_programming(distance_matrix)
        else:
            permutation, distance = solve_tsp_simulated_annealing(distance_matrix)

        # 3. Reorder places based on optimal route
        optimized_places = [place_ids[i] for i in permutation]

        return {
            "original_order": place_ids,
            "optimized_order": optimized_places,
            "total_distance_km": distance / 1000,
            "estimated_time_hours": distance / 40000,  # 40 km/h avg
            "algorithm": "exact" if len(place_ids) <= 10 else "heuristic"
        }
```

#### New Endpoint:
```python
POST /api/v1/routes/optimize
Request Body:
{
    "place_ids": ["uuid1", "uuid2", "uuid3", ...],
    "start_location": "uuid1",  # optional
    "end_location": "uuid5",    # optional
    "max_time_hours": 8         # optional
}

Response:
{
    "route": [
        {
            "place_id": "uuid",
            "name": "Calangute Beach",
            "sequence": 1,
            "distance_from_previous_km": 0,
            "arrival_time": "09:00",
            "departure_time": "11:00"
        },
        ...
    ],
    "total_distance_km": 45.2,
    "total_time_hours": 6.5,
    "algorithm_used": "exact",
    "optimization_time_ms": 234
}
```

**Success Criteria:**
- ✅ Optimize 5 places in < 1 second
- ✅ Optimize 15 places in < 5 seconds
- ✅ Returns valid route (visits all places once)
- ✅ Respects time constraints

---

### 2.2 K-Means Clustering (Multi-Day Trips)

**Priority:** MEDIUM
**Effort:** 3 days
**Dependencies:** Route optimizer

#### Tasks:
```bash
✅ Implement K-Means for geographical clustering
✅ Group POIs by day based on proximity
✅ Create multi-day itinerary endpoint
```

#### Implementation:
```python
# services/clustering.py
from sklearn.cluster import KMeans
import numpy as np

class GeographicalClusterer:
    def cluster_by_days(self, place_ids: List[str], num_days: int) -> Dict:
        """
        Cluster places into daily groups using K-Means
        """
        # 1. Get coordinates for all places
        places = self.db.query(Place).filter(Place.id.in_(place_ids)).all()
        coords = np.array([[p.latitude, p.longitude] for p in places])

        # 2. Apply K-Means clustering
        kmeans = KMeans(n_clusters=num_days, random_state=42)
        labels = kmeans.fit_predict(coords)

        # 3. Group places by cluster
        daily_groups = {}
        for i, label in enumerate(labels):
            day = f"Day {label + 1}"
            if day not in daily_groups:
                daily_groups[day] = []
            daily_groups[day].append(places[i])

        return {
            "num_days": num_days,
            "daily_groups": daily_groups,
            "cluster_centers": kmeans.cluster_centers_.tolist()
        }
```

#### New Endpoint:
```python
POST /api/v1/routes/multi-day
Request:
{
    "place_ids": ["uuid1", ..., "uuid20"],
    "num_days": 3,
    "start_time": "09:00",
    "max_hours_per_day": 8
}

Response:
{
    "itinerary": [
        {
            "day": 1,
            "places": [...],
            "route": [...],
            "total_distance_km": 25.3,
            "total_time_hours": 6.5
        },
        {
            "day": 2,
            "places": [...],
            ...
        }
    ]
}
```

**Success Criteria:**
- ✅ Clusters 30 places into 3 days effectively
- ✅ Minimizes inter-cluster distances
- ✅ Each day's group is geographically coherent

---

## Phase 3: Smart Recommendations (Week 5-6)

### 3.1 Preference-Based Filtering

**Priority:** MEDIUM
**Effort:** 3 days

#### Implementation:
```python
POST /api/v1/recommendations/generate
Request:
{
    "preferences": {
        "categories": ["Beach", "Church"],
        "min_popularity": 7,
        "difficulty_levels": ["Easy", "Moderate"],
        "free_only": false,
        "max_entry_fee": 500,
        "facilities_required": ["Parking", "Toilets"],
        "wheelchair_accessible": true
    },
    "constraints": {
        "max_distance_from_base_km": 50,
        "base_location": {"lat": 15.5, "lon": 73.8},
        "max_places": 10
    }
}

Response:
{
    "recommendations": [
        {
            "place": {...},
            "match_score": 0.95,
            "reason": "Matches all preferences: Beach, Easy, High popularity (9/10), Free entry"
        },
        ...
    ],
    "total_matches": 15,
    "filters_applied": {...}
}
```

#### Features:
- ✅ Filter by category, popularity, difficulty
- ✅ Filter by facilities and accessibility
- ✅ Distance-based filtering
- ✅ Budget constraints
- ✅ Ranking by match score

---

### 3.2 Smart Itinerary Builder

**Priority:** MEDIUM
**Effort:** 4 days

#### Combine:
1. Preference filtering
2. K-Means clustering (for multi-day)
3. TSP optimization (for each day)
4. Time constraint handling

#### Endpoint:
```python
POST /api/v1/itinerary/smart-build
Request:
{
    "trip_duration_days": 3,
    "preferences": {...},
    "constraints": {
        "start_time": "09:00",
        "end_time": "18:00",
        "lunch_break_duration_minutes": 60,
        "visit_duration_buffer_minutes": 30
    }
}

Response:
{
    "itinerary": [
        {
            "day": 1,
            "date": "2025-12-01",
            "schedule": [
                {
                    "time": "09:00",
                    "activity": "Start",
                    "place": "Hotel"
                },
                {
                    "time": "09:30",
                    "activity": "Visit",
                    "place": "Calangute Beach",
                    "duration_minutes": 120,
                    "arrival_time": "09:30",
                    "departure_time": "11:30"
                },
                ...
            ],
            "stats": {
                "total_distance_km": 35,
                "driving_time_hours": 1.5,
                "visit_time_hours": 5,
                "total_time_hours": 6.5
            }
        },
        ...
    ],
    "summary": {
        "total_places": 15,
        "total_distance_km": 105,
        "total_cost_inr": 2500,
        "difficulty": "Easy"
    }
}
```

---

## Phase 4: Advanced Features (Week 7-10)

### 4.1 Genetic Algorithm (OPTIONAL - Advanced Optimization)

**Priority:** LOW (TSP solver is sufficient for MVP)
**Effort:** 5-7 days

#### When to implement:
- After TSP solver proves insufficient
- For very large route problems (>20 places)
- For multi-objective optimization (time + cost + preferences)

#### Implementation:
```python
# services/genetic_algorithm.py
class GeneticAlgorithmOptimizer:
    def __init__(self, population_size=50, generations=100):
        self.population_size = population_size
        self.generations = generations

    def optimize(self, places, objectives):
        """
        Multi-objective optimization using GA

        Objectives:
        - Minimize total distance
        - Maximize popularity scores
        - Respect time windows
        - Match user preferences
        """
        # Initialize population
        population = self.initialize_population(places)

        for generation in range(self.generations):
            # Calculate fitness
            fitness_scores = [self.fitness(route, objectives) for route in population]

            # Selection
            parents = self.select_parents(population, fitness_scores)

            # Crossover
            offspring = self.crossover(parents)

            # Mutation
            offspring = self.mutate(offspring)

            # Replace population
            population = offspring

        # Return best solution
        best_route = max(population, key=lambda r: self.fitness(r, objectives))
        return best_route
```

**Note:** Only implement if TSP solver has limitations. For 100 places with typical routes of 5-15 destinations, TSP is sufficient.

---

### 4.2 User Management & Authentication

**Priority:** MEDIUM
**Effort:** 3-4 days

#### Features:
```python
# New endpoints
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/logout
GET /api/v1/auth/me

# User preferences
PUT /api/v1/users/me/preferences
GET /api/v1/users/me/preferences

# Saved routes
POST /api/v1/users/me/routes
GET /api/v1/users/me/routes
GET /api/v1/users/me/routes/{route_id}
DELETE /api/v1/users/me/routes/{route_id}
```

#### Tech Stack:
- JWT tokens for authentication
- Password hashing with bcrypt
- Refresh token mechanism

---

### 4.3 Caching Layer (Redis)

**Priority:** MEDIUM
**Effort:** 2 days

#### Cache Strategy:
```python
# Cache popular queries
- Distance matrix lookups (1 week TTL)
- Popular routes (1 day TTL)
- Search results (1 hour TTL)
- Place details (1 day TTL)

# Implementation
from redis import Redis
from functools import wraps

def cache_result(ttl=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{args}:{kwargs}"

            # Check cache
            cached = redis.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            redis.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

---

## Phase 5: Frontend (Week 11-16)

### 5.1 Basic Web UI (React)

**Priority:** HIGH
**Effort:** 6-8 weeks

#### Pages:
1. **Home Page**
   - Search destinations
   - Category filters
   - Popular destinations grid

2. **Map View**
   - Interactive map (Leaflet or Google Maps)
   - Place markers
   - Route visualization

3. **Trip Planner**
   - Select destinations
   - Configure preferences
   - Generate optimized route
   - View itinerary

4. **Place Details**
   - Photos, description
   - Visitor information
   - Reviews and ratings
   - Nearby places

#### Tech Stack:
```json
{
  "framework": "React 18+",
  "mapping": "Leaflet.js (free) or Google Maps API",
  "state": "React Query + Zustand",
  "styling": "Tailwind CSS",
  "routing": "React Router v6"
}
```

#### Component Structure:
```
frontend/
├── src/
│   ├── components/
│   │   ├── Map/
│   │   │   ├── MapView.jsx
│   │   │   ├── PlaceMarker.jsx
│   │   │   └── RoutePolyline.jsx
│   │   ├── PlaceCard/
│   │   ├── SearchBar/
│   │   ├── TripPlanner/
│   │   └── ItineraryView/
│   ├── pages/
│   │   ├── Home.jsx
│   │   ├── MapPage.jsx
│   │   ├── PlaceDetails.jsx
│   │   └── TripPlanner.jsx
│   ├── hooks/
│   │   ├── usePlaces.js
│   │   ├── useRouteOptimizer.js
│   │   └── useMap.js
│   └── api/
│       └── client.js
```

---

## Effort Estimation Summary

| Phase | Features | Effort | Team Size | Duration |
|-------|----------|--------|-----------|----------|
| **Phase 1** | Database + Basic API + Tests | 7-9 days | 1 backend dev | 2 weeks |
| **Phase 2** | TSP + K-Means + Optimization | 7-8 days | 1 backend dev | 2 weeks |
| **Phase 3** | Recommendations + Smart Itinerary | 7 days | 1 backend dev | 1.5 weeks |
| **Phase 4** | Auth + Caching + Advanced | 5-7 days | 1 backend dev | 1.5 weeks |
| **Phase 5** | Frontend (Basic) | 30-40 days | 1 frontend dev | 6-8 weeks |

**Total Estimated Effort:**
- Backend: 26-31 days (5-6 weeks)
- Frontend: 30-40 days (6-8 weeks)
- **Total with 1 developer:** 12-14 weeks (3-3.5 months)
- **Total with 2 developers (1 BE + 1 FE):** 8-10 weeks (2-2.5 months)

---

## MVP Definition (Minimum Viable Product)

**Goal:** Working system in 4 weeks

### Included:
1. ✅ Database with 100 destinations
2. ✅ 5 core API endpoints (list, search, nearby, details, optimize)
3. ✅ TSP route optimization
4. ✅ Basic tests
5. ✅ Simple React UI with map
6. ✅ Trip planning workflow

### Excluded (Post-MVP):
- ❌ Genetic Algorithm (use TSP)
- ❌ User authentication (add later)
- ❌ Redis caching (add later)
- ❌ Mobile app (add later)
- ❌ Advanced recommendations (add later)

---

## Technology Stack Recommendations

### Backend:
```txt
Language: Python 3.11+
Framework: FastAPI 0.109+
Database: PostgreSQL 12+ + PostGIS 3.0+
ORM: SQLAlchemy 2.0 + GeoAlchemy2
Validation: Pydantic 2.5+
Testing: Pytest + pytest-asyncio
Optimization: python-tsp
Clustering: scikit-learn (K-Means)
```

### Frontend:
```txt
Framework: React 18+ with Vite
Mapping: Leaflet.js (free, open-source)
State: React Query + Zustand
Styling: Tailwind CSS
HTTP: Axios
Routing: React Router v6
```

### DevOps:
```txt
Containerization: Docker + Docker Compose
CI/CD: GitHub Actions
Hosting: Railway / Render / DigitalOcean
Monitoring: Sentry (errors) + LogRocket (sessions)
```

---

## Risk Mitigation

### Technical Risks:

| Risk | Impact | Mitigation |
|------|--------|------------|
| TSP solver too slow for large routes | Medium | Implement timeout, fallback to greedy algorithm |
| Database performance at scale | Low | Already optimized with indexes, distance matrix |
| Google Maps API costs | Medium | Use Leaflet.js (free), cache results |
| Complex GA implementation | High | Skip GA for MVP, TSP is sufficient |

### Timeline Risks:

| Risk | Impact | Mitigation |
|------|--------|------------|
| Scope creep | High | Stick to MVP, defer advanced features |
| Underestimated effort | Medium | Add 20% buffer to estimates |
| Team availability | Medium | Prioritize critical path features |

---

## Success Metrics

### Technical Metrics:
- ✅ API response time < 200ms (95th percentile)
- ✅ Route optimization < 2 seconds for 10 places
- ✅ Database query time < 50ms (spatial searches)
- ✅ Test coverage > 80%
- ✅ Zero critical security vulnerabilities

### Business Metrics:
- ✅ Can generate itinerary for any 5-15 destinations
- ✅ Routes are 15-30% shorter than manual planning
- ✅ User can plan 3-day trip in < 5 minutes
- ✅ 100% of Goa destinations searchable

---

## What NOT to Build (At Least Initially)

### ❌ Over-Engineering Traps:

1. **Genetic Algorithm** - TSP solver is sufficient for <20 places
2. **Real-time traffic** - Adds complexity, use static estimates
3. **Social features** - Defer sharing/reviews to post-MVP
4. **Mobile app** - Mobile-responsive web is enough initially
5. **Admin dashboard** - Manual database updates are fine for 100 places
6. **Machine learning recommendations** - Rule-based filtering works fine
7. **Multi-language support** - English only for MVP
8. **Offline mode** - Requires significant PWA effort
9. **Payment integration** - No booking features in MVP
10. **Weather integration** - Nice-to-have, not critical

---

## Recommended Implementation Order

### Sprint 1 (Week 1-2): Database + Basic API
```bash
Day 1-2:   Set up PostgreSQL + PostGIS + import data
Day 3-5:   Create FastAPI project + 5 core endpoints
Day 6-7:   Write tests
Day 8-10:  Documentation + Docker setup
```

### Sprint 2 (Week 3-4): Route Optimization
```bash
Day 11-13: Implement TSP route optimizer
Day 14-15: Add K-Means clustering
Day 16-17: Create route optimization endpoints
Day 18-20: Test optimization with real data
```

### Sprint 3 (Week 5-6): Smart Features
```bash
Day 21-23: Preference-based filtering
Day 24-26: Smart itinerary builder
Day 27-30: Integration testing + bug fixes
```

### Sprint 4 (Week 7-10): Frontend
```bash
Day 31-35: React setup + basic pages
Day 36-40: Map integration + place cards
Day 41-45: Trip planner UI
Day 46-50: Itinerary display + polish
```

---

## Final Recommendations

### Start With:
1. ✅ Database setup + CSV import (2 days)
2. ✅ Basic API with 5 endpoints (3 days)
3. ✅ TSP route optimizer (3 days)
4. ✅ Simple React UI (5 days)

**Total MVP:** 13 days of focused work

### Add Later:
- User authentication
- Caching layer
- Advanced recommendations
- Genetic algorithm
- Mobile app

### Never Build:
- Over-complex ML models (dataset too small)
- Real-time features (premature optimization)
- Social network features (scope creep)

---

**Remember:**
> "Make it work, make it right, make it fast" - Kent Beck

Start simple, validate with users, iterate based on feedback.

---

**Next Steps:**
1. Set up local development environment
2. Create `backend/` folder structure
3. Install dependencies
4. Run database setup script
5. Import CSV data
6. Build first endpoint
7. Test it works
8. Repeat

**Good luck! 🚀**
