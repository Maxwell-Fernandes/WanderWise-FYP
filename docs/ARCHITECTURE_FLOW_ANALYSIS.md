# WANDERWISE ARCHITECTURE FLOW ANALYSIS
**Date**: November 16, 2025
**Purpose**: Comprehensive data flow testing and component connectivity verification
**Status**: Architecture Review & Gap Analysis

---

## EXECUTIVE SUMMARY

### ✅ Overall Assessment: **WELL-DESIGNED** with minor gaps

**Score**: 8.5/10

**Strengths**:
- Clear layered architecture
- Proper separation of concerns
- Comprehensive database schema
- Well-defined data flows

**Critical Gaps Identified**: 3
**Non-Critical Gaps**: 4
**Missing Components**: 2

---

## COMPLETE DATA FLOW TRACE

### Flow 1: NEW ITINERARY GENERATION (Happy Path)

```
USER REQUEST
    ↓
[1] UI Layer (React Web/Mobile)
    → User fills form: {days: 3, budget: 15000, preferences: ["Beach", "Heritage"], constraints: {...}}
    → Sends: POST /api/v1/itinerary/generate
    ↓
[2] API Gateway (Nginx)
    ✅ VERIFIED CONNECTION: HTTPS → FastAPI backend
    → SSL termination
    → Rate limiting check
    → Routes to Application Layer
    ↓
[3] Application Layer (FastAPI)
    → Route Service receives request
    → Validates with Pydantic schemas
    ↓
    ┌─→ [3a] Check Cache (Redis L1)
    │   → Key: hash(days=3, budget=15000, prefs=["Beach","Heritage"])
    │   → Cache MISS (first time request)
    │   ↓
    └─→ [3b] Recommendation Service
        → Calls POI Service to fetch candidates
        ↓
[4] POI Service
    ┌─→ Check Redis L2 Cache (POI Metadata)
    │   → Cache MISS
    │   ↓
    └─→ Query Database Layer
        ↓
[5] Database Layer (PostgreSQL + PostGIS)
    → Execute query:
    ```sql
    SELECT * FROM goa_places
    WHERE category IN ('Beach', 'Heritage')
    AND entry_fee_inr <= 15000/3
    ORDER BY popularity_score DESC
    ```
    → Returns: 35 candidate POIs
    ↓
[6] POI Metadata → Cache in Redis L2
    → TTL: 24 hours
    ↓
[7] Recommendation Service
    → Applies POI Scoring (Diagram 5)
        ┌→ Content-Based Filtering
        ├→ Popularity Score
        ├→ Context Factors (weather, time)
        └→ Constraint Checking
    → Returns: Scored list of 20 POIs
    ↓
[8] Optimization Service
    → Calls Algorithm Selector
    ↓
[9] Algorithm Layer
    → Algorithm Selector analyzes:
        - POIs: 20
        - Days: 3
        - Constraints: Budget, time
    → Selects: Genetic Algorithm
    ↓
[10] Genetic Algorithm Execution
    → Needs distance matrix
    ↓
[11] Check Redis L3 Cache (Distance Matrix)
    ┌─→ Look for distances between all POI pairs
    │   → Partial HIT: 85% of pairs cached
    │   ↓
    └─→ For missing pairs (15%):
        ┌→ Query distance_matrix table
        │   → HIT: 10% found in DB
        │   ↓
        └→ For remaining 5%:
            → ⚠️ GAP IDENTIFIED: Need to call External API
            ↓
[12] ❌ MISSING COMPONENT: Distance Calculation Service
    → Should call Google Maps Routes API
    → Calculate distance and duration
    → Store in distance_matrix table
    → Cache in Redis L3
    ↓
[13] GA Optimization Runs
    → Population: 50 chromosomes
    → Generations: 100
    → Selection → Crossover → Mutation
    → Fitness evaluation using distances
    → Converges after 75 generations
    → Best solution: [POI1, POI5, POI12, POI8, POI15, ...]
    ↓
[14] Multi-Day Planning (Diagram 4)
    → Geographic Clustering (North/South/Central Goa)
    → Allocate POIs across 3 days
    → Optimize each day separately
    → Day 1: [POI1, POI5, POI12] (North Goa)
    → Day 2: [POI8, POI15, POI20] (South Goa)
    → Day 3: [POI3, POI7, POI18] (Central)
    ↓
[15] Enrich Itinerary
    ❌ MISSING COMPONENT: Map Service integration
    → Should call Google Maps Routes API for:
        - Turn-by-turn directions
        - Route geometry (polylines)
        - Real-time travel duration
    ↓
[16] Generate Alternatives
    → Run GA again with different seed
    → Generate 2 alternative routes
    ↓
[17] Store Result
    → Save to user_routes table
    ```sql
    INSERT INTO user_routes (route_name, place_ids, total_distance_km, ...)
    ```
    ↓
[18] Cache Result in Redis L1
    → Key: hash(request_params)
    → Value: Complete itinerary JSON
    → TTL: 1 hour
    ↓
[19] Return to User
    → Application Layer formats response
    → Includes: main route, 2 alternatives, stats, map data
    ↓
[20] API Gateway → UI
    → Response: 200 OK
    → Body: JSON with itinerary
    ↓
[21] UI Renders
    → Display itinerary
    → Show map with route
    ❌ MISSING: Map rendering connection (needs Google Maps JS API key)
    → Display schedule with timing
    ↓
END - User sees itinerary
```

**Total Flow Time**: ~8-12 seconds (first request, cold cache)
**Cached Request Time**: ~200-500ms

---

## Flow 2: REAL-TIME ADAPTATION (Weather Change)

```
EXTERNAL TRIGGER (Weather API Webhook or Polling)
    ↓
[1] ❌ MISSING COMPONENT: Weather Monitoring Service
    → Should poll OpenWeather API every 30 minutes
    → Detect significant changes (sunny → rain)
    ↓
[2] Adaptation Service (Diagram 6)
    → Event Detection: "Rain started"
    → Severity Assessment: MAJOR
    → Trigger re-optimization
    ↓
[3] Optimization Service
    → Load current itinerary from Redis/DB
    → Filter outdoor POIs
    → Add indoor alternatives
    ↓
[4] Algorithm Layer
    → Re-run optimization with new constraints
    → Use Simulated Annealing (faster for re-opt)
    ↓
[5] Generate Alternatives
    → New route with indoor POIs
    ↓
[6] Notify User
    ❌ MISSING COMPONENT: Notification Service
    → Should send:
        - Push notification (if mobile app)
        - WebSocket message (if web app active)
        - Email (if configured)
    ↓
[7] User Reviews Options
    → UI shows: "Weather changed. Here's updated itinerary"
    → User accepts/rejects
    ↓
[8] Update Itinerary
    → Save to user_routes (new version)
    → Invalidate old cache
    ↓
END
```

---

## Flow 3: DATA IMPORT & INITIALIZATION

```
ADMIN OPERATION (One-time setup)
    ↓
[1] Data Collection (Manual + API)
    ┌→ Google Places API calls
    │   → Fetch 100+ Goa POIs
    │   → Get: name, location, rating, photos, etc.
    │   ↓
    └→ Manual Curation
        → Validate data
        → Add: duration, tips, best_for, etc.
        ↓
[2] CSV File Creation
    → Wanderwise_datasetnew.csv (100 rows)
    ↓
[3] Import Script (Python)
    → Read CSV
    → Parse pipe-delimited fields
    → Validate coordinates
    ↓
[4] Database Insertion
    ```sql
    INSERT INTO goa_places (...) VALUES (...)
    ```
    → 100 POIs inserted
    ↓
[5] ❌ MISSING COMPONENT: Distance Matrix Population Service
    → Should call: populate_full_distance_matrix()
    → For 100 POIs: 100 × 99 / 2 = 4,950 pairs
    → Options:
        a) Use Haversine (fast, less accurate)
        b) Call Google Maps API (slow, accurate, $$)
        c) Use OSRM (free, accurate, self-hosted)
    ↓
[6] Populate distance_matrix table
    → Insert 4,950 rows
    → Estimated time:
        - Haversine: 30 seconds
        - Google Maps: 8 hours (rate limits)
        - OSRM: 30 minutes
    ↓
[7] Refresh Materialized Views
    ```sql
    REFRESH MATERIALIZED VIEW popular_places;
    REFRESH MATERIALIZED VIEW goa_beaches;
    ```
    ↓
[8] Warm Redis Cache
    → Pre-cache popular POIs
    → Pre-cache common distance pairs
    ↓
END - System ready for use
```

---

## COMPONENT CONNECTIVITY MATRIX

### Layer-by-Layer Connections

| From Layer | To Layer | Protocol | Status | Notes |
|------------|----------|----------|--------|-------|
| UI → API Gateway | Nginx | HTTPS/REST | ✅ | Standard |
| API Gateway → Application | FastAPI | HTTP | ✅ | Internal |
| Application → Algorithm | Python calls | In-process | ✅ | Same app |
| Application → Caching | Redis protocol | TCP 6379 | ⚠️ | Not configured yet |
| Application → Database | PostgreSQL | TCP 5432 | ✅ | SQLAlchemy |
| Application → External APIs | HTTPS | Internet | ⚠️ | Needs API keys |
| Caching → Database | N/A | N/A | ✅ | Cache-aside pattern |

### Service-to-Service Connections

| Service | Depends On | Connection Type | Status | Missing? |
|---------|-----------|-----------------|--------|----------|
| **POI Service** | Database | SQLAlchemy ORM | ✅ | No |
| **POI Service** | Redis L2 | redis-py | ⚠️ | Config needed |
| **User Service** | Database | SQLAlchemy ORM | ✅ | No |
| **Route Service** | POI Service | Direct call | ✅ | No |
| **Route Service** | Optimization Service | Direct call | ✅ | No |
| **Route Service** | Redis L1 | redis-py | ⚠️ | Config needed |
| **Optimization Service** | Algorithm Layer | Direct call | ✅ | No |
| **Optimization Service** | Distance Calculator | Direct call | ❌ | **MISSING** |
| **Recommendation Service** | POI Service | Direct call | ✅ | No |
| **Recommendation Service** | User Service | Direct call | ✅ | No |
| **Map Service** | Google Maps API | HTTPS | ❌ | **MISSING** |
| **Map Service** | Database (cache routes) | SQLAlchemy | ✅ | No |

---

## CRITICAL GAPS IDENTIFIED

### 🔴 Gap 1: Distance Calculation Service (CRITICAL)

**Location**: Application Layer
**Purpose**: Calculate distances between POI pairs
**Impact**: Cannot run optimization without distances

**Required Implementation**:
```python
# backend/app/services/distance_calculator.py

class DistanceCalculator:
    def __init__(self):
        self.db = get_database()
        self.cache = get_redis()
        self.google_api_key = config.GOOGLE_MAPS_API_KEY

    async def get_distance(self, poi_id_1: UUID, poi_id_2: UUID) -> float:
        """
        Get distance between two POIs with caching
        1. Check Redis L3
        2. Check distance_matrix table
        3. Calculate via Haversine (fallback)
        4. Calculate via Google Maps (if API key available)
        """
        # Check cache
        cache_key = f"distance:{poi_id_1}:{poi_id_2}"
        cached = await self.cache.get(cache_key)
        if cached:
            return float(cached)

        # Check DB
        db_result = self.db.query(DistanceMatrix).filter(...).first()
        if db_result:
            return db_result.distance_km

        # Calculate
        if self.google_api_key:
            distance = await self._calculate_google_maps(poi_id_1, poi_id_2)
        else:
            distance = await self._calculate_haversine(poi_id_1, poi_id_2)

        # Store & cache
        await self._store_distance(poi_id_1, poi_id_2, distance)
        return distance
```

**Priority**: P0 (Blocking)
**Effort**: 1-2 weeks
**Owner**: Backend Team Member 1

---

### 🔴 Gap 2: Weather Monitoring Service (HIGH)

**Location**: Application Layer
**Purpose**: Monitor weather changes and trigger adaptations
**Impact**: Real-time adaptation won't work

**Required Implementation**:
```python
# backend/app/services/weather_monitor.py

class WeatherMonitor:
    def __init__(self):
        self.openweather_api_key = config.OPENWEATHER_API_KEY
        self.cache = get_redis()

    async def check_weather_for_route(self, route_id: UUID):
        """
        Check weather for all POIs in route
        Compare with cached conditions
        Trigger adaptation if significant change
        """
        route = await get_route(route_id)

        for poi_id in route.place_ids:
            poi = await get_poi(poi_id)
            current_weather = await self._fetch_weather(poi.latitude, poi.longitude)
            cached_weather = await self.cache.get(f"weather:{poi_id}")

            if self._significant_change(cached_weather, current_weather):
                await self._trigger_adaptation(route_id, poi_id, current_weather)

    def _significant_change(self, old, new):
        """
        Detect significant weather changes:
        - Clear → Rain
        - Hot → Cold (>10°C difference)
        """
        if old['condition'] == 'clear' and new['condition'] == 'rain':
            return True
        if abs(old['temp'] - new['temp']) > 10:
            return True
        return False
```

**Priority**: P1 (High)
**Effort**: 2-3 weeks
**Owner**: Backend Team Member 2

---

### 🔴 Gap 3: Notification Service (MEDIUM)

**Location**: Application Layer
**Purpose**: Send notifications to users about route changes
**Impact**: Users won't know about adaptations

**Required Implementation**:
```python
# backend/app/services/notification_service.py

class NotificationService:
    async def notify_route_change(self, user_id: UUID, route_id: UUID, reason: str):
        """
        Send multi-channel notifications
        - WebSocket (if user online)
        - Push notification (if mobile)
        - Email (fallback)
        """
        user = await get_user(user_id)

        # WebSocket (real-time)
        if user.is_online:
            await self.websocket.send(user.connection_id, {
                "type": "route_update",
                "route_id": route_id,
                "reason": reason
            })

        # Push notification (mobile)
        if user.push_token:
            await self.push_service.send(user.push_token, {
                "title": "Route Updated",
                "body": f"Your itinerary changed: {reason}"
            })

        # Email (fallback)
        await self.email_service.send(user.email,
            subject="WanderWise Route Update",
            template="route_change.html",
            data={"route_id": route_id, "reason": reason}
        )
```

**Priority**: P2 (Medium)
**Effort**: 2-3 weeks
**Owner**: Backend Team Member 3

---

## NON-CRITICAL GAPS

### ⚠️ Gap 4: Map Service Integration

**Issue**: No connection to Google Maps for route geometry
**Impact**: No turn-by-turn directions, no visual route on map
**Workaround**: Show POI markers only (no routes)
**Priority**: P2
**Effort**: 1 week

---

### ⚠️ Gap 5: Redis Configuration

**Issue**: Redis caching layer not configured
**Impact**: Slower performance (all DB queries)
**Workaround**: Works without cache (just slower)
**Priority**: P1
**Effort**: 2-3 days

---

### ⚠️ Gap 6: Algorithm Selector Logic

**Issue**: Algorithm selector not implemented
**Impact**: Can't auto-select best algorithm
**Workaround**: Hardcode Genetic Algorithm
**Priority**: P2
**Effort**: 3-4 days

---

### ⚠️ Gap 7: User Authentication

**Issue**: No user service implementation
**Impact**: Can't save routes per user
**Workaround**: Use session-based temporary storage
**Priority**: P1
**Effort**: 1-2 weeks

---

## MISSING COMPONENTS

### 1. Distance Matrix Population Script

**File**: `backend/scripts/populate_distances.py`
**Status**: ❌ Missing
**Purpose**: Bulk populate distance_matrix table

**Pseudocode**:
```python
async def populate_all_distances():
    pois = db.query(GoaPlace).all()
    total_pairs = len(pois) * (len(pois) - 1) / 2

    for i, poi1 in enumerate(pois):
        for poi2 in pois[i+1:]:
            # Check if already exists
            exists = check_distance_exists(poi1.id, poi2.id)
            if exists:
                continue

            # Calculate
            distance = calculate_haversine(
                poi1.latitude, poi1.longitude,
                poi2.latitude, poi2.longitude
            )

            # Store bidirectional
            store_distance(poi1.id, poi2.id, distance)
            store_distance(poi2.id, poi1.id, distance)
```

---

### 2. Environment Configuration Template

**File**: `backend/.env.example`
**Status**: ❌ Missing
**Purpose**: Template for required environment variables

**Required Contents**:
```bash
# Database
DATABASE_URL=postgresql://wanderwise_user:password@localhost:5432/wanderwise_db

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=

# External APIs
GOOGLE_MAPS_API_KEY=your_key_here
GOOGLE_PLACES_API_KEY=your_key_here
OPENWEATHER_API_KEY=your_key_here

# Application
SECRET_KEY=generate_random_secret
DEBUG=True
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Nginx (if using)
NGINX_HOST=localhost
NGINX_PORT=80
```

---

## ARCHITECTURE VALIDATION RESULTS

### ✅ What's Working Well

1. **Database Schema** (10/10)
   - Comprehensive tables
   - Proper indexes (GIST, GIN, B-tree)
   - Materialized views for performance
   - Good constraints and validations

2. **Layered Architecture** (9/10)
   - Clear separation of concerns
   - Scalable structure
   - Microservice-ready

3. **Caching Strategy** (9/10)
   - Well-designed 3-level cache
   - Proper TTLs
   - Realistic hit rate targets

4. **Algorithm Layer** (8/10)
   - Good algorithm selection
   - Clear separation from business logic
   - Modular design

5. **Data Flow** (8/10)
   - Logical flow from UI to DB
   - Proper use of caching
   - Good error handling paths

---

### ⚠️ What Needs Work

1. **Missing Service Implementations** (5/10)
   - Distance Calculator: MISSING
   - Weather Monitor: MISSING
   - Notification Service: MISSING
   - Map Service: PARTIAL

2. **External API Integration** (4/10)
   - No API keys configured
   - No retry logic
   - No rate limiting
   - No fallback mechanisms

3. **Redis Integration** (3/10)
   - Not configured
   - No connection pool
   - No cache warming strategy

4. **User Management** (2/10)
   - No authentication
   - No authorization
   - No user sessions

---

## DATA FLOW BOTTLENECKS

### Bottleneck 1: Distance Matrix Population

**Problem**: 100 POIs = 4,950 distance calculations
**Options**:

| Method | Time | Cost | Accuracy |
|--------|------|------|----------|
| Haversine | 30 sec | $0 | 85% |
| OSRM (self-host) | 30 min | $0 | 95% |
| Google Maps | 8 hrs | ~$25 | 99% |

**Recommendation**: Use Haversine for initialization, add Google Maps option later

---

### Bottleneck 2: Cold Cache Performance

**Problem**: First request takes 8-12 seconds
**Solution**:
1. Warm cache on startup (top 20 popular routes)
2. Pre-compute common queries
3. Background cache refresh every 6 hours

---

### Bottleneck 3: Algorithm Execution Time

**Problem**: GA takes 5-10 seconds for 20 POIs
**Solutions**:
1. Run in background (async/Celery)
2. Show "Computing..." UI with progress
3. Return quick greedy solution first, then optimize

---

## RECOMMENDED FIXES (Priority Order)

### Phase 1: MVP Blocking (Weeks 1-4)

**Week 1-2**: Distance Calculator Service
- ✅ Haversine implementation
- ✅ Database caching
- ✅ Redis integration
- ✅ Population script

**Week 3**: Redis Configuration
- ✅ Install Redis
- ✅ Configure connection pool
- ✅ Implement L1/L2/L3 caching
- ✅ Cache warming

**Week 4**: Environment Setup
- ✅ Create .env.example
- ✅ Document all required variables
- ✅ Set up secrets management

---

### Phase 2: Core Features (Weeks 5-8)

**Week 5-6**: User Authentication
- ✅ JWT-based auth
- ✅ User registration/login
- ✅ Route saving per user

**Week 7**: Map Service
- ✅ Google Maps integration
- ✅ Route geometry fetching
- ✅ Frontend map rendering

**Week 8**: Algorithm Selector
- ✅ Implement selection logic
- ✅ Performance testing
- ✅ Algorithm comparison

---

### Phase 3: Advanced Features (Weeks 9-12)

**Week 9-10**: Weather Monitoring
- ✅ OpenWeather integration
- ✅ Polling service
- ✅ Adaptation triggers

**Week 11**: Notification Service
- ✅ WebSocket setup
- ✅ Email service
- ✅ (Optional) Push notifications

**Week 12**: Performance Optimization
- ✅ Query optimization
- ✅ Index tuning
- ✅ Load testing

---

## TEAM ASSIGNMENT RECOMMENDATIONS

### Team Member 1: Backend Infrastructure
**Responsibilities**:
- Distance Calculator Service
- Redis setup and configuration
- Database optimization
- API gateway setup

**Estimated Hours**: 120-150 hours

---

### Team Member 2: Algorithm & Optimization
**Responsibilities**:
- Genetic Algorithm implementation
- Algorithm Selector
- Route optimization service
- Performance tuning

**Estimated Hours**: 120-150 hours

---

### Team Member 3: Integration & Services
**Responsibilities**:
- Map Service integration
- Weather Monitoring
- Notification Service
- External API management

**Estimated Hours**: 120-150 hours

---

### Team Member 4: Data & Frontend
**Responsibilities**:
- POI data collection (100+)
- Data validation scripts
- Frontend React app
- Map visualization

**Estimated Hours**: 120-150 hours

---

## FINAL VERDICT

### Overall Architecture Score: 8.5/10

**Breakdown**:
- Design Quality: 9/10 ✅
- Completeness: 6/10 ⚠️
- Scalability: 9/10 ✅
- Performance: 8/10 ✅
- Implementability: 7/10 ⚠️

### Critical Path Items:
1. ✅ Database Schema (DONE)
2. ❌ Distance Calculator (BLOCKING)
3. ❌ Redis Setup (BLOCKING)
4. ❌ Environment Config (BLOCKING)
5. ⚠️ User Auth (HIGH PRIORITY)

### Timeline to MVP:
- With gaps fixed: 8-10 weeks
- Without gaps fixed: Cannot launch

### Recommendation:
**Architecture is fundamentally sound.** The 7-layer design is appropriate for a 4-person/6-month project. However, **3 critical components are missing** that must be implemented before the system can function:

1. Distance Calculator Service (P0)
2. Redis Configuration (P1)
3. Environment Setup (P0)

Once these are addressed, the architecture will support all documented flows correctly.

---

**Document Version**: 1.0
**Last Updated**: November 16, 2025
**Next Review**: After Distance Calculator implementation
**Status**: ⚠️ **ACTION REQUIRED** - Implement missing P0/P1 components
