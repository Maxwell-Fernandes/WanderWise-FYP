# WANDERWISE ARCHITECTURE & FLOW DIAGRAMS
# Based on Research Paper Analysis
# Date: November 16, 2025

---

## DIAGRAM 1: HIGH-LEVEL SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │   Web App    │  │  Mobile App  │  │  Admin Panel │                  │
│  │   (React)    │  │   (React)    │  │   (React)    │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │ HTTPS/REST API
┌────────────────────────────────┴────────────────────────────────────────┐
│                         API GATEWAY LAYER                                │
│  ┌─────────────────────────────────────────────────────────────┐        │
│  │  Nginx Reverse Proxy + Load Balancer                        │        │
│  │  - Request routing                                           │        │
│  │  - Rate limiting                                             │        │
│  │  - SSL termination                                           │        │
│  └─────────────────────────────────────────────────────────────┘        │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
┌────────────────────────────────┴────────────────────────────────────────┐
│                       APPLICATION LAYER (FastAPI)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │  POI Service │  │ User Service │  │Route Service │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │ Optimization │  │Recommendation│  │  Map Service │                  │
│  │   Service    │  │   Service    │  │              │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │  Distance    │  │   Weather    │  │ Notification │                  │
│  │ Calculator   │  │   Monitor    │  │   Service    │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
┌────────────────────────────────┴────────────────────────────────────────┐
│                          ALGORITHM LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │   Greedy     │  │   Genetic    │  │  Simulated   │                  │
│  │  Algorithm   │  │  Algorithm   │  │  Annealing   │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │ Tabu Search  │  │ Ant Colony   │  │   Integer    │                  │
│  │              │  │ Optimization │  │ Programming  │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
│  ┌──────────────────────────────────────────────────┐                   │
│  │        Algorithm Selector (Adaptive)             │                   │
│  └──────────────────────────────────────────────────┘                   │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
┌────────────────────────────────┴────────────────────────────────────────┐
│                          CACHING LAYER (Redis)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │   L1 Cache   │  │   L2 Cache   │  │   L3 Cache   │                  │
│  │  (Routes)    │  │(POI Metadata)│  │  (Distance   │                  │
│  │   1hr TTL    │  │   24hr TTL   │  │   Matrix)    │                  │
│  └──────────────┘  └──────────────┘  │   7day TTL   │                  │
│                                       └──────────────┘                  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
┌────────────────────────────────┴────────────────────────────────────────┐
│                    DATA LAYER (PostgreSQL + PostGIS)                     │
│  ┌─────────────────────────────────────────────────────────────┐        │
│  │  POI Database     User Profiles    Itineraries              │        │
│  │  Distance Cache   Visit History    Feedback                 │        │
│  └─────────────────────────────────────────────────────────────┘        │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
┌────────────────────────────────┴────────────────────────────────────────┐
│                         EXTERNAL APIs                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │ Google Places│  │ Google Maps  │  │ OpenWeather  │                  │
│  │     API      │  │  Routes API  │  │     API      │                  │
│  └──────────────┘  └──────────────┘  └──────────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## DIAGRAM 2: ITINERARY GENERATION FLOW

```
                              START
                                │
                                ▼
                    ┌───────────────────────┐
                    │   User Input          │
                    │   - Days              │
                    │   - Budget            │
                    │   - Preferences       │
                    │   - Constraints       │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Check Cache          │
                    │  (Similar requests?)  │
                    └───────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
              Cache HIT                Cache MISS
                    │                       │
                    ▼                       ▼
          ┌──────────────────┐   ┌──────────────────┐
          │ Return Cached    │   │  Fetch POIs      │
          │ Itinerary        │   │  from Database   │
          └──────────────────┘   └──────────────────┘
                    │                       │
                    │                       ▼
                    │            ┌──────────────────┐
                    │            │ Apply Filters    │
                    │            │ - Category       │
                    │            │ - Region         │
                    │            │ - Budget         │
                    │            │ - Opening Hours  │
                    │            └──────────────────┘
                    │                       │
                    │                       ▼
                    │            ┌──────────────────┐
                    │            │ Score POIs       │
                    │            │ - User prefs     │
                    │            │ - Popularity     │
                    │            │ - Collaborative  │
                    │            └──────────────────┘
                    │                       │
                    │                       ▼
                    │            ┌──────────────────┐
                    │            │ Select Algorithm │
                    │            │ - Problem size   │
                    │            │ - Constraints    │
                    │            │ - Time limit     │
                    │            └──────────────────┘
                    │                       │
                    │                       ▼
                    │            ┌──────────────────┐
                    │            │ Build Distance   │
                    │            │ Matrix           │
                    │            │ - Check L3 Cache │
                    │            │ - Query DB       │
                    │            │ - Calculate gaps │
                    │            └──────────────────┘
                    │                       │
                    │                       ▼
                    │            ┌──────────────────┐
                    │            │ Run Optimization │
                    │            │ - POI selection  │
                    │            │ - Sequencing     │
                    │            │ - Scheduling     │
                    │            └──────────────────┘
                    │                       │
                    │                       ▼
                    │            ┌──────────────────┐
                    │            │ Validate Route   │
                    │            │ - Constraints OK?│
                    │            │ - Feasible?      │
                    │            └──────────────────┘
                    │                       │
                    │                       ▼
                    │            ┌──────────────────┐
                    │            │ Generate         │
                    │            │ Alternatives     │
                    │            │ (Top 3)          │
                    │            └──────────────────┘
                    │                       │
                    │                       ▼
                    │            ┌──────────────────┐
                    │            │ Enrich Itinerary │
                    │            │ - Map Service    │
                    │            │ - Directions API │
                    │            │ - Route geometry │
                    │            │ - POI photos     │
                    │            └──────────────────┘
                    │                       │
                    │                       ▼
                    │            ┌──────────────────┐
                    │            │ Cache Result     │
                    │            └──────────────────┘
                    │                       │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Return Itinerary     │
                    │  - Main route         │
                    │  - Alternatives       │
                    │  - Statistics         │
                    │  - Map data           │
                    └───────────────────────┘
                                │
                                ▼
                              END
```

---

## DIAGRAM 3: GENETIC ALGORITHM FLOW (Main Optimization)

```
                              START
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Initialize Parameters │
                    │ - Population size     │
                    │ - Generations         │
                    │ - Mutation rate       │
                    │ - Crossover rate      │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Generate Initial      │
                    │ Population            │
                    │ - Random chromosomes  │
                    │ - Greedy seeding      │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Evaluate Fitness      │
                    │ - Calculate scores    │
                    │ - Check constraints   │
                    └───────────────────────┘
                                │
                                ▼
                       ╔════════════════╗
                       ║  GENERATION    ║
                       ║     LOOP       ║
                       ╚════════════════╝
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
          ┌──────────────────┐   ┌──────────────────┐
          │  Selection       │   │  Track Best      │
          │  - Tournament    │   │  Solution        │
          │  - Roulette      │   │                  │
          └──────────────────┘   └──────────────────┘
                    │                       │
                    ▼                       │
          ┌──────────────────┐             │
          │  Crossover       │             │
          │  - Order (OX)    │             │
          │  - PMX           │             │
          └──────────────────┘             │
                    │                       │
                    ▼                       │
          ┌──────────────────┐             │
          │  Mutation        │             │
          │  - Swap          │             │
          │  - Insert        │             │
          │  - Inversion     │             │
          └──────────────────┘             │
                    │                       │
                    ▼                       │
          ┌──────────────────┐             │
          │  Evaluate        │             │
          │  New Population  │             │
          └──────────────────┘             │
                    │                       │
                    ▼                       │
          ┌──────────────────┐             │
          │  Replace         │             │
          │  Population      │             │
          └──────────────────┘             │
                    │                       │
                    ▼                       │
          ┌──────────────────┐             │
          │  Convergence?    │─────NO──────┘
          │  or Max Gens?    │
          └──────────────────┘
                    │
                   YES
                    │
                    ▼
          ┌──────────────────┐
          │  Return Best     │
          │  Itinerary       │
          └──────────────────┘
                    │
                    ▼
                  END
```

---

## DIAGRAM 4: MULTI-DAY ITINERARY OPTIMIZATION

```
                              START
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Input Parameters      │
                    │ - Num days: N         │
                    │ - Daily budget        │
                    │ - Daily time limit    │
                    │ - Hotel location      │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Geographic Clustering │
                    │ - North Goa           │
                    │ - South Goa           │
                    │ - Central Goa         │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Score All POIs        │
                    │ - User preferences    │
                    │ - Popularity          │
                    │ - Seasonality         │
                    └───────────────────────┘
                                │
                                ▼
                 ╔══════════════════════════════╗
                 ║     DAY-BY-DAY LOOP (N)      ║
                 ╚══════════════════════════════╝
                                │
              ┌─────────────────┴─────────────────┐
              │                                   │
              ▼                                   ▼
    ┌──────────────────┐              ┌──────────────────┐
    │ Select Region    │              │ Balance Budget   │
    │ for Day i        │              │ across Days      │
    │ - Minimize       │              └──────────────────┘
    │   inter-region   │
    │   travel         │
    └──────────────────┘
              │
              ▼
    ┌──────────────────┐
    │ Filter POIs      │
    │ - By region      │
    │ - By budget      │
    │ - Not visited    │
    └──────────────────┘
              │
              ▼
    ┌──────────────────┐
    │ Optimize Single  │
    │ Day Route        │
    │ (Use GA/SA/TS)   │
    └──────────────────┘
              │
              ▼
    ┌──────────────────┐
    │ Add to Itinerary │
    │ - Update visited │
    │ - Update budget  │
    └──────────────────┘
              │
              ▼
    ┌──────────────────┐
    │ More Days?       │
    └──────────────────┘
              │
         ┌────┴────┐
        YES       NO
         │         │
         │         ▼
         │   ┌──────────────────┐
         │   │ Inter-day        │
         │   │ Optimization     │
         │   │ - Balance POIs   │
         └───│ - Smooth flow    │
             └──────────────────┘
                     │
                     ▼
             ┌──────────────────┐
             │ Generate Final   │
             │ N-day Itinerary  │
             └──────────────────┘
                     │
                     ▼
                   END
```

---

## DIAGRAM 5: POI SCORING & RECOMMENDATION SYSTEM

```
                         POI SCORING PIPELINE
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Raw POI Data        │
                    │   - Name              │
                    │   - Category          │
                    │   - Location          │
                    │   - Reviews           │
                    │   - Google rating     │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Content-Based         │
                    │ Filtering             │
                    │                       │
                    │ - Category match      │
                    │ - Tag matching        │
                    │ - Text similarity     │
                    │ - User preference fit │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Popularity Score     │
                    │  - Avg rating         │
                    │  - Review count       │
                    │  - Google popularity  │
                    │  - Visit frequency    │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Context Factors      │
                    │  - Time of day        │
                    │  - Season             │
                    │  - Weather            │
                    │  - Day of week        │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Constraint Checking  │
                    │  - Budget             │
                    │  - Time available     │
                    │  - Accessibility      │
                    │  - Age appropriate    │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Weighted Score       │
                    │  = w1*Content         │
                    │  + w2*Popularity      │
                    │  + w3*Context         │
                    │  - Constraint penalty │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Final POI Score      │
                    │  (0.0 - 1.0)          │
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Ranking & Selection  │
                    │  for Optimization     │
                    └───────────────────────┘

NOTE: Collaborative filtering NOT implemented (requires user interaction data).
      Using content-based + popularity-based hybrid approach instead.
```

---

## DIAGRAM 6: REAL-TIME ADAPTATION FLOW

```
                      ADAPTATION TRIGGERS
                                │
            ┌───────────────────┼───────────────────┐
            │                   │                   │
            ▼                   ▼                   ▼
  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
  │   Weather    │    │    User      │    │   Manual     │
  │   Changes    │    │  Feedback    │    │   Trigger    │
  │ (OpenWeather)│    │  (In-app)    │    │  (Button)    │
  └──────────────┘    └──────────────┘    └──────────────┘
            │                   │                   │
            └───────────────────┼───────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Event Detection      │
                    │  - Rain started?      │
                    │  - Too hot/cold?      │
                    │  - User wants change? │
                    │  - Manual re-optimize?│
                    └───────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Severity Assessment  │
                    │  - Minor: Log only    │
                    │  - Major: Adapt route │
                    │  - Critical: Alert    │
                    └───────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                  MINOR                   MAJOR
                    │                       │
                    ▼                       ▼
          ┌──────────────┐      ┌──────────────────┐
          │ Log Event    │      │ Trigger          │
          │ Continue     │      │ Re-optimization  │
          └──────────────┘      └──────────────────┘
                                          │
                                          ▼
                              ┌──────────────────┐
                              │ Generate         │
                              │ Alternatives     │
                              │ - Skip outdoor   │
                              │ - Suggest indoor │
                              │ - Reorder POIs   │
                              └──────────────────┘
                                          │
                                          ▼
                              ┌──────────────────┐
                              │ Notify User      │
                              │ - Show options   │
                              │ - Request choice │
                              └──────────────────┘
                                          │
                                          ▼
                              ┌──────────────────┐
                              │ Update Itinerary │
                              │ - New route      │
                              │ - New timing     │
                              └──────────────────┘

NOTE: Traffic and crowd density monitoring NOT implemented.
      Focus on weather adaptation and user-initiated re-optimization.
```

---

## DIAGRAM 7: DATA FLOW - POI COLLECTION TO OPTIMIZATION

```
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA COLLECTION PHASE                          │
└─────────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
                ▼                               ▼
    ┌────────────────────┐         ┌────────────────────┐
    │  Google Places API │         │ Manual Curation    │
    │  - Basic info      │         │ - Validation       │
    │  - Reviews         │         │ - Enhancements     │
    │  - Photos          │         │ - Local knowledge  │
    └────────────────────┘         └────────────────────┘
                │                               │
                └───────────────┬───────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      DATA PROCESSING PHASE                          │
└─────────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
    ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
    │ Geocoding      │  │ Categorization │  │ Enrichment     │
    │ - Coordinates  │  │ - Tags         │  │ - Duration     │
    │ - Address      │  │ - Themes       │  │ - Best time    │
    └────────────────┘  └────────────────┘  └────────────────┘
                │               │               │
                └───────────────┴───────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         STORAGE PHASE                               │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  PostgreSQL + PostGIS │
                    │  - Spatial indexing   │
                    │  - JSONB fields       │
                    │  - Full-text search   │
                    └───────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PRE-COMPUTATION PHASE                            │
└─────────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
                ▼               ▼               ▼
    ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
    │ Distance       │  │ Travel Time    │  │ POI Clusters   │
    │ Matrix         │  │ Matrix         │  │ - Geographic   │
    │ (N x N)        │  │ (time-dep)     │  │ - Thematic     │
    └────────────────┘  └────────────────┘  └────────────────┘
                │               │               │
                └───────────────┴───────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      OPTIMIZATION PHASE                             │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Algorithm Selection  │
                    │  & Execution          │
                    └───────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      RESULT DELIVERY PHASE                          │
└─────────────────────────────────────────────────────────────────────┘
```

---

## DIAGRAM 8: CONSTRAINT SATISFACTION ARCHITECTURE

```
                     CONSTRAINT SYSTEM
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
   │   HARD       │  │    SOFT      │  │  DYNAMIC     │
   │ CONSTRAINTS  │  │ CONSTRAINTS  │  │ CONSTRAINTS  │
   └──────────────┘  └──────────────┘  └──────────────┘
            │               │               │
            │               │               │
            ▼               ▼               ▼
   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
   │ Time Budget  │  │ Preferences  │  │ Weather      │
   │ Money Budget │  │ POI Quality  │  │ Traffic      │
   │ Opening Hours│  │ Diversity    │  │ Crowds       │
   │ Capacity     │  │ Balance      │  │ Events       │
   └──────────────┘  └──────────────┘  └──────────────┘
            │               │               │
            └───────────────┴───────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │  Constraint Checker   │
                │  - Validates routes   │
                │  - Calculates scores  │
                │  - Reports violations │
                └───────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
             VALID                  INVALID
                │                       │
                ▼                       ▼
      ┌──────────────┐      ┌──────────────┐
      │ Accept Route │      │ Repair or    │
      │              │      │ Reject       │
      └──────────────┘      └──────────────┘
```

---

## DIAGRAM 9: CACHING STRATEGY (3-LEVEL)

```
                      USER REQUEST
                            │
                            ▼
              ┌───────────────────────┐
              │   L1: Route Cache     │
              │   (Redis - In Memory) │
              │   TTL: 1 hour         │
              │   Hit Rate: 40-50%    │
              └───────────────────────┘
                            │
                      ┌─────┴─────┐
                   HIT          MISS
                      │             │
                      ▼             ▼
              ┌──────────┐  ┌───────────────────────┐
              │ Return   │  │   L2: POI Metadata    │
              │ Cached   │  │   (Redis)             │
              │ Route    │  │   TTL: 24 hours       │
              └──────────┘  │   Hit Rate: 30-40%    │
                            └───────────────────────┘
                                        │
                                  ┌─────┴─────┐
                               HIT          MISS
                                  │             │
                                  ▼             ▼
                          ┌──────────┐  ┌───────────────────────┐
                          │ Compute  │  │ L3: Distance Matrix   │
                          │ Route    │  │ (Redis + PostgreSQL)  │
                          │ Using    │  │ TTL: 7 days           │
                          │ Cached   │  │ Hit Rate: 80-90%      │
                          │ POIs     │  └───────────────────────┘
                          └──────────┘              │
                                  │           ┌─────┴─────┐
                                  │        HIT          MISS
                                  │           │             │
                                  │           ▼             ▼
                                  │   ┌──────────┐  ┌──────────┐
                                  │   │ Compute  │  │  Fetch   │
                                  │   │ Using    │  │  from    │
                                  │   │ Cached   │  │  APIs &  │
                                  │   │ Distances│  │  Compute │
                                  │   └──────────┘  └──────────┘
                                  │           │             │
                                  │           └─────┬───────┘
                                  │                 │
                                  └────────┬────────┘
                                           │
                                           ▼
                                  ┌──────────────┐
                                  │ Cache Result │
                                  │ in All Layers│
                                  └──────────────┘
                                           │
                                           ▼
                                  ┌──────────────┐
                                  │ Return to    │
                                  │ User         │
                                  └──────────────┘

CACHE STATISTICS TARGET:
- Overall Hit Rate: >70%
- L1 Response Time: <10ms
- L2 Response Time: <50ms
- L3 Response Time: <100ms
- Cache Miss (Full Compute): <5 seconds
```

---

## DIAGRAM 10: USER PREFERENCE LEARNING SYSTEM

```
                    USER INTERACTIONS
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
   │   Explicit   │  │   Implicit   │  │   Feedback   │
   │   Prefs      │  │   Behavior   │  │   Ratings    │
   │              │  │              │  │              │
   │ - Categories │  │ - Click      │  │ - Stars      │
   │ - Budget     │  │ - Time spent │  │ - Comments   │
   │ - Activity   │  │ - Bookmarks  │  │ - Favorites  │
   └──────────────┘  └──────────────┘  └──────────────┘
            │               │               │
            └───────────────┴───────────────┘
                            │
                            ▼
              ┌───────────────────────┐
              │   Feature Extraction  │
              │   - Category weights  │
              │   - Budget ranges     │
              │   - Activity level    │
              │   - POI attributes    │
              └───────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            │                               │
            ▼                               ▼
   ┌──────────────────┐         ┌──────────────────┐
   │ Short-term Model │         │ Long-term Model  │
   │ (Session-based)  │         │ (Profile-based)  │
   │                  │         │                  │
   │ - Current trip   │         │ - Saved prefs    │
   │ - Real-time adj  │         │ - Demographics   │
   │ - Context-aware  │         │ - History        │
   └──────────────────┘         └──────────────────┘
            │                               │
            └───────────────┬───────────────┘
                            │
                            ▼
              ┌───────────────────────┐
              │  Preference Fusion    │
              │  - Weighted average   │
              │  - Context adaptation │
              │  - Recency weighting  │
              └───────────────────────┘
                            │
                            ▼
              ┌───────────────────────┐
              │  POI Score Adjustment │
              │  - Content matching   │
              │  - Popularity boost   │
              │  - Context factors    │
              └───────────────────────┘
                            │
                            ▼
              ┌───────────────────────┐
              │  Optimization Input   │
              │  (Personalized scores)│
              └───────────────────────┘

NOTE: Uses content-based personalization only (no collaborative filtering).
      User preferences mapped to POI attributes for scoring.
```

---

## DIAGRAM 11: COMPLETE SERVICE INTERACTION MAP

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER REQUEST                                 │
│                     (Generate 3-day itinerary)                       │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
        ┌──────────────────┐      ┌──────────────────┐
        │  Route Service   │      │  User Service    │
        │  - Validate req  │      │  - Get user prefs│
        └──────────────────┘      └──────────────────┘
                    │                         │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
        ┌──────────────────┐      ┌──────────────────┐
        │ Redis L1 Cache   │      │ POI Service      │
        │ Check cached     │      │ Fetch candidates │
        │ route            │      │                  │
        └──────────────────┘      └──────────────────┘
                    │                         │
                   HIT                       ▼
                    │              ┌──────────────────┐
                    │              │ Redis L2 Cache   │
                    │              │ POI Metadata     │
                    │              └──────────────────┘
                    │                         │
                    │                        MISS
                    │                         ▼
                    │              ┌──────────────────┐
                    │              │ PostgreSQL + PG  │
                    │              │ Query goa_places │
                    │              └──────────────────┘
                    │                         │
                    │                         ▼
                    │              ┌──────────────────┐
                    │              │ Recommendation   │
                    │              │ Service          │
                    │              │ - Score POIs     │
                    │              └──────────────────┘
                    │                         │
                    │                         ▼
                    │              ┌──────────────────┐
                    │              │ Distance         │
                    │              │ Calculator       │
                    │              │ - Check L3       │
                    │              │ - Query DB       │
                    │              │ - Haversine      │
                    │              └──────────────────┘
                    │                         │
                    │                         ▼
                    │              ┌──────────────────┐
                    │              │ Redis L3 Cache   │
                    │              │ Distance Matrix  │
                    │              └──────────────────┘
                    │                         │
                    │                         ▼
                    │              ┌──────────────────┐
                    │              │ Optimization     │
                    │              │ Service          │
                    │              │ - Select algo    │
                    │              └──────────────────┘
                    │                         │
                    │                         ▼
                    │              ┌──────────────────┐
                    │              │ Algorithm Layer  │
                    │              │ - GA / SA / TS   │
                    │              └──────────────────┘
                    │                         │
                    │                         ▼
                    │              ┌──────────────────┐
                    │              │ Map Service      │
                    │              │ - Get directions │
                    │              │ - Route geometry │
                    │              └──────────────────┘
                    │                         │
                    │                         │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
        ┌──────────────────┐      ┌──────────────────┐
        │ Save to          │      │ Cache in Redis   │
        │ user_routes      │      │ L1 (1hr TTL)     │
        │ table            │      │                  │
        └──────────────────┘      └──────────────────┘
                    │                         │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌───────────────────────┐
                    │  Return Itinerary     │
                    │  - 3-day route        │
                    │  - Map data           │
                    │  - Statistics         │
                    └───────────────────────┘


EXTERNAL INTEGRATION POINTS:
┌────────────────────────────────────────────────────────────┐
│                                                            │
│  Google Places API ←── POI Service (data collection)      │
│                                                            │
│  Google Maps API ←──── Distance Calculator (fallback)     │
│                   └──── Map Service (directions)           │
│                                                            │
│  OpenWeather API ←──── Weather Monitor (every 30min)      │
│                                                            │
└────────────────────────────────────────────────────────────┘


BACKGROUND PROCESSES:
┌────────────────────────────────────────────────────────────┐
│                                                            │
│  Weather Monitor (polling) → Adaptation Trigger           │
│         ↓                                                  │
│  Notification Service → WebSocket/Push/Email              │
│                                                            │
│  Cache Warmer (on startup) → Redis L1/L2/L3              │
│                                                            │
│  Materialized View Refresh (daily) → PostgreSQL           │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## TECHNICAL SPECIFICATIONS

### Performance Metrics

**Algorithm Performance**:
- Single-day optimization: <5 seconds
- Multi-day optimization (up to 5 days): <30 seconds
- Real-time re-optimization: <3 seconds

**System Performance**:
- API response time: <200ms (95th percentile)
- Database query time: <50ms
- Cache hit rate: >70%
- Concurrent users: 100+

**Quality Metrics**:
- Route feasibility: 100%
- Constraint satisfaction: 100%
- User satisfaction: >4.0/5.0

### Scalability Targets

**Data Scale**:
- POIs in database: 500+
- User profiles: 10,000+
- Cached routes: 50,000+

**Load Capacity**:
- Requests per second: 100+
- Concurrent optimizations: 20+
- Database connections: 50+

### Infrastructure Requirements

**Hardware**:
- CPU: 4+ cores
- RAM: 16GB+
- Storage: 100GB+ SSD
- Network: 100Mbps+

**Software**:
- OS: Ubuntu 24.04 LTS
- Database: PostgreSQL 15+ with PostGIS
- Cache: Redis 7+
- Web Server: Nginx 1.24+
- Runtime: Python 3.11+, Node.js 20+

---

## IMPLEMENTATION NOTES

### Critical Success Factors

1. **Data Quality**: Manual validation of all POI data
2. **Algorithm Tuning**: Proper parameter selection for each algorithm
3. **Caching Strategy**: Multi-level caching for performance
4. **Constraint Handling**: Robust validation and repair mechanisms
5. **User Experience**: Fast, intuitive interface with clear visualizations

### Risk Mitigation

1. **Performance**: Pre-computation, caching, and algorithm timeouts
2. **Data Quality**: Multiple sources, manual curation, user feedback
3. **Scalability**: Database indexing, connection pooling, async processing
4. **Reliability**: Error handling, fallback mechanisms, monitoring

### Testing Strategy

1. **Unit Tests**: Each algorithm component
2. **Integration Tests**: Full optimization pipeline
3. **Performance Tests**: Load testing, stress testing
4. **User Acceptance Tests**: Real user feedback (N=20+)

---

## REFERENCES TO RESEARCH PAPERS

These diagrams synthesize findings from:

1. Paper 1 (Yan 2022): Interest field extraction, greedy algorithm
2. Paper 2 (Cao 2022): Multi-objective optimization, round-trip constraints
3. Paper 3 (Yoon 2023): Real-time adaptation, context-aware recommendations
4. Paper 4 (2020): Genetic algorithm implementation, pairwise relationships
5. Paper 5 (2024): AI algorithm comparison, multi-day planning
6. Paper 6 (2024): Enhanced GA, parameter adaptation
7. Paper 7 (2022): Data integration, behavior pattern mining
8. Paper 8 (2021): Constraint handling, feasibility checking

---

**Document Version**: 2.0
**Last Updated**: November 16, 2025
**Total Diagrams**: 11
**Changes in v2.0**:
- Added Distance Calculator, Weather Monitor, Notification Service to Application Layer
- Updated L3 Cache to show Distance Matrix explicitly with TTL
- Added distance matrix building step to Itinerary Generation Flow
- Updated Enrich Itinerary to show Map Service integration
- Added Diagram 11: Complete Service Interaction Map with all components
