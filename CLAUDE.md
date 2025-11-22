# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🎯 Current Repository Status

**⚠️ IMPORTANT: This repository is currently in the PLANNING/DESIGN phase.**

### What EXISTS in this repository:
- ✅ Complete database schema (`database/database_setup.sql`) - Production-ready PostgreSQL + PostGIS
- ✅ Curated dataset (`Wanderwise_datasetnew.csv`) - 100 Goa tourist destinations
- ✅ System architecture diagrams (in `diagrams/`)
- ✅ Database ERD and design documentation
- ✅ Research papers and reference materials
- ✅ Project documentation (README, QUICKSTART, SETUP_SUMMARY)
- ✅ Presentation materials
- ✅ `.gitignore` configuration

### What DOES NOT EXIST (needs implementation):
- ❌ Backend Python code (no `app/` directory structure)
- ❌ FastAPI application
- ❌ SQLAlchemy models
- ❌ Pydantic schemas
- ❌ API route handlers
- ❌ Business logic services
- ❌ Utility functions
- ❌ Tests
- ❌ requirements.txt
- ❌ .env.example
- ❌ Data import scripts

**Current Working Directory:** `/home/user/WanderWise-FYP/`

---

## 📋 Project Overview

**WanderWise+** is an intelligent Goa tourism route planning system developed as a final year project. It combines spatial databases (PostgreSQL + PostGIS), FastAPI backend, and advanced route optimization algorithms to help tourists discover and plan optimal itineraries for exploring Goa.

### Planned Tech Stack

- **Backend:** Python 3.11+, FastAPI 0.109+, SQLAlchemy 2.0+
- **Database:** PostgreSQL 12+ with PostGIS 3.0+ extensions
- **Spatial Libraries:** GeoAlchemy2, Shapely, GeoPy, PyProj
- **Optimization:** Python-TSP, OR-Tools, NetworkX, SciPy
- **Data Source:** Curated CSV dataset with 100+ Goa destinations

### Implementation Phases

📋 **Phase 1 - Database & Data (READY FOR IMPLEMENTATION):**
- Database schema exists and is ready to deploy
- Dataset is cleaned and validated
- Need to: Set up PostgreSQL, run schema, import data

📋 **Phase 2 - Backend Core (NOT STARTED):**
- Need to: Create project structure, FastAPI app, models, basic CRUD

📋 **Phase 3 - Route Optimization (NOT STARTED):**
- Need to: Implement TSP solver, recommendation engine

📋 **Phase 4 - Advanced Features (PLANNED):**
- Caching, testing, authentication, analytics

---

## 📊 Dataset Structure

### Main Data File: `Wanderwise_datasetnew.csv`

The dataset contains **101 entries** (100 destinations + 1 header row) with 29 fields.

**Core Fields:**
- `name` - Destination name
- `category` - Main category (Beach, Temple, Fort, Church, Waterfall, Wildlife, Museum)
- `subcategory` - Specific classification (e.g., "North Goa Beach", "South Goa Beach")
- `latitude`, `longitude` - Geographic coordinates (WGS84 decimal degrees)
- `description` - Detailed destination description (200-500 words)

**Visitor Information:**
- `entry_fee_inr` - Entry fee in Indian Rupees (0 if free)
- `is_free` - Boolean indicating if entry is free
- `opening_time`, `closing_time` - Operating hours (24-hour format HH:MM)
- `best_visit_time` - Recommended visiting time/season (e.g., "Sunset (17:00-18:30)")
- `duration_minutes` - Suggested visit duration in minutes

**Destination Attributes:**
- `popularity_score` - Rating scale 0-10 (most places: 7.0-10.0)
- `difficulty_level` - Access difficulty (Easy, Moderate, Hard)
- `facilities` - Pipe-delimited list (e.g., "Lifeguards|Toilets|Beach Shacks|Water Sports")
- `best_for` - Pipe-delimited target audiences (e.g., "Families|Couples|Adventure Seekers")
- `avoid_when` - Times/conditions to avoid (e.g., "Monsoon (June-September)")
- `tips` - Practical visitor advice (detailed recommendations)

**Discoverability:**
- `instagram_tags` - Pipe-delimited hashtags (e.g., "#CalanguteBeach|#GoaBeaches|#NorthGoa")
- `photo_spots` - Number of notable photography locations (0-15)

**Contact & Access:**
- `address` - Full postal address with pin code
- `taluka` - Administrative subdivision (e.g., Bardez, Salcete, Tiswadi)
- `contact_number` - Phone number (format: +91-XXX-XXX-XXXX, may be "NA")
- `website` - Official website URL (may be empty)
- `parking_available` - Boolean/Yes/No
- `wheelchair_accessible` - Accessibility status (Yes/No/Partial)
- `food_available` - Food options available (Yes/No)

**Metadata:**
- `last_verified_date` - Data verification date (YYYY-MM-DD format, mostly 2024-11-01)
- `RESEARCH_STATUS` - Data collection status (all entries: COMPLETE)

### Data Characteristics

- **Primary focus:** Goa beaches (North Goa, South Goa, City beaches) - approximately 40% of dataset
- **Categories:** Beach, Temple, Fort, Church, Waterfall, Wildlife Sanctuary, Museum, Market
- **Coordinate system:** WGS84 (SRID 4326) - Decimal degrees
- **Geographic bounds:** Goa boundaries (14.8-15.9°N, 73.6-74.4°E)
- **Verification status:** All entries verified as of November 2024
- **Delimiter:** Pipe character (|) for multi-value fields (facilities, tags, best_for)
- **Time format:** 24-hour (HH:MM), "00:00-23:59" indicates 24/7 access
- **Free entry:** Entries with `entry_fee_inr=0` have `is_free=TRUE`

### Data Processing Notes

When implementing CSV import:
- Use pandas or Python csv module for parsing
- Split pipe-delimited fields: `facilities.split('|')` → PostgreSQL TEXT[] array
- Handle "NA" values in contact_number and website (convert to NULL)
- Parse time fields: `datetime.strptime(time_str, '%H:%M').time()`
- Validate coordinates within Goa boundaries before insertion
- Create PostGIS GEOGRAPHY point: `ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)`
- Boolean conversion: "Yes" → True, "No" → False, "Partial" → store as-is for wheelchair_accessible

**Example CSV row (Calangute Beach):**
```csv
Calangute Beach,Beach,North Goa Beach,15.544500,73.755100,"Calangute Beach is one of North Goa's most iconic...",0,TRUE,00:00,23:59,Sunset (17:00-18:30),120,9,Easy,Lifeguards|Toilets|Beach Shacks|Water Sports|Parking|ATM|First Aid,#CalanguteBeach|#GoaBeaches|#NorthGoa|#BeachLife|#GoaTourism,"Calangute Beach Road, Calangute, North Goa, Goa 403516",Bardez,+91-832-227-6745,https://www.goatourism.gov.in,Yes,Partial,Yes,8,Families|Couples|Adventure Seekers|Party Lovers,Monsoon (June-September)|Weekends can be very crowded,"Visit early morning (6-8 AM) for peaceful sunrise walks...",2024-11-01,COMPLETE
```

---

## 🗄️ Database Schema

### File: `database/database_setup.sql`

Complete PostgreSQL + PostGIS schema (500+ lines) ready for deployment.

### Extensions Required

```sql
CREATE EXTENSION IF NOT EXISTS postgis;           -- Spatial operations
CREATE EXTENSION IF NOT EXISTS postgis_topology;  -- Topology support
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";       -- UUID generation
CREATE EXTENSION IF NOT EXISTS pg_trgm;           -- Trigram text search
```

### Custom Types

```sql
-- Difficulty levels for destinations
CREATE TYPE difficulty_level AS ENUM ('Easy', 'Moderate', 'Hard');

-- Research/verification status
CREATE TYPE research_status AS ENUM ('PENDING', 'IN_PROGRESS', 'COMPLETE', 'NEEDS_UPDATE');
```

### Main Tables

#### 1. `goa_places` - Tourist Destinations

**Purpose:** Stores all tourist destinations with spatial and descriptive data

**Key Columns:**
- `id` UUID PRIMARY KEY - UUID v4 identifier
- `name` VARCHAR(255) NOT NULL - Place name
- `category` VARCHAR(100) NOT NULL - Main category
- `subcategory` VARCHAR(100) - Detailed classification
- `location` GEOGRAPHY(POINT, 4326) NOT NULL - PostGIS spatial point
- `latitude` NUMERIC(10, 7) NOT NULL - WGS84 latitude
- `longitude` NUMERIC(10, 7) NOT NULL - WGS84 longitude
- `description` TEXT - Detailed description
- `entry_fee_inr` NUMERIC(10, 2) DEFAULT 0 - Entry fee
- `is_free` BOOLEAN DEFAULT true - Free entry flag
- `opening_time` TIME - Opening hour
- `closing_time` TIME - Closing hour
- `best_visit_time` VARCHAR(255) - Recommended visit time
- `duration_minutes` INTEGER - Suggested visit duration
- `popularity_score` NUMERIC(3, 1) - Rating 0-10
- `difficulty_level` difficulty_level - Ease of access
- `facilities` TEXT[] - Array of available facilities
- `facilities_raw` TEXT - Original pipe-delimited string
- `instagram_tags` TEXT[] - Array of hashtags
- `instagram_tags_raw` TEXT - Original pipe-delimited string
- `photo_spots` INTEGER DEFAULT 0 - Number of photo locations
- `address` TEXT - Full postal address
- `taluka` VARCHAR(100) - Administrative subdivision
- `contact_number` VARCHAR(50) - Phone number
- `website` VARCHAR(500) - Official website URL
- `parking_available` BOOLEAN DEFAULT false - Parking availability
- `wheelchair_accessible` VARCHAR(20) - Accessibility (Yes/No/Partial)
- `food_available` BOOLEAN DEFAULT false - Food options
- `best_for` TEXT[] - Array of target audiences
- `best_for_raw` TEXT - Original pipe-delimited string
- `avoid_when` TEXT - When to avoid visiting
- `tips` TEXT - Travel tips
- `last_verified_date` DATE - Data verification date
- `research_status` research_status DEFAULT 'COMPLETE' - Verification status
- `created_at` TIMESTAMP WITH TIME ZONE - Creation timestamp
- `updated_at` TIMESTAMP WITH TIME ZONE - Last update timestamp

**Constraints:**
- Valid Goa coordinates: `latitude BETWEEN 14.8 AND 15.9`, `longitude BETWEEN 73.6 AND 74.4`
- Positive duration: `duration_minutes > 0`
- Non-negative fee: `entry_fee_inr >= 0`
- Fee consistency: Free places have `entry_fee_inr = 0` (with exceptions for donations)

**Indexes:**
- GIST spatial index on `location` (critical for spatial queries)
- B-tree indexes on `category`, `subcategory`, `popularity_score DESC`, `is_free`
- GIN indexes on array fields: `facilities`, `instagram_tags`, `best_for`
- Trigram index on `name` for fuzzy text search
- GIN index on `description` for full-text search

#### 2. `distance_matrix` - Cached Distances

**Purpose:** Pre-computed distances between places for route optimization performance

**Key Columns:**
- `id` UUID PRIMARY KEY
- `place_id_from` UUID NOT NULL REFERENCES goa_places(id)
- `place_id_to` UUID NOT NULL REFERENCES goa_places(id)
- `distance_meters` NUMERIC(10, 2) NOT NULL - Distance in meters
- `distance_km` NUMERIC(10, 2) GENERATED - Auto-calculated km (stored)
- `estimated_time_minutes` INTEGER - Travel time estimate (40 km/h average)
- `route_geometry` GEOGRAPHY(LINESTRING, 4326) - Optional route line (future)
- `calculated_at` TIMESTAMP WITH TIME ZONE - Calculation timestamp
- `calculation_method` VARCHAR(50) DEFAULT 'haversine' - Method used

**Constraints:**
- Different places: `place_id_from != place_id_to`
- Positive distance: `distance_meters > 0`
- Unique pairs: `UNIQUE (place_id_from, place_id_to)`

**Note:** For 100 places, full matrix = ~10,000 entries (100 × 99 directed pairs)

#### 3. `user_routes` - Saved Routes

**Purpose:** Store saved and optimized routes

**Key Columns:**
- `id` UUID PRIMARY KEY
- `route_name` VARCHAR(255) - User-friendly route name
- `place_ids` UUID[] NOT NULL - Ordered array of place IDs
- `total_distance_km` NUMERIC(10, 2) - Total route distance
- `total_duration_minutes` INTEGER - Total duration including visits
- `estimated_cost_inr` NUMERIC(10, 2) - Estimated trip cost
- `preferences` JSONB - User preferences (flexible JSON storage)
- `created_at` TIMESTAMP WITH TIME ZONE
- `updated_at` TIMESTAMP WITH TIME ZONE

**Constraints:**
- Minimum 2 places: `array_length(place_ids, 1) >= 2`

### Materialized Views

```sql
-- Popular places (popularity_score >= 7.0)
CREATE MATERIALIZED VIEW popular_places AS
SELECT * FROM goa_places
WHERE popularity_score >= 7.0
ORDER BY popularity_score DESC;

-- Goa beaches quick access
CREATE MATERIALIZED VIEW goa_beaches AS
SELECT * FROM goa_places
WHERE category = 'Beach'
ORDER BY popularity_score DESC;
```

**Refresh command:** `REFRESH MATERIALIZED VIEW popular_places;`

### Spatial Functions

```sql
-- Calculate distance between two places (in meters)
CREATE OR REPLACE FUNCTION calculate_distance(place_id_1 UUID, place_id_2 UUID)
RETURNS NUMERIC AS $$
    SELECT ST_Distance(
        (SELECT location FROM goa_places WHERE id = place_id_1),
        (SELECT location FROM goa_places WHERE id = place_id_2)
    );
$$ LANGUAGE SQL;

-- Find nearby places within radius
CREATE OR REPLACE FUNCTION find_nearby_places(lat NUMERIC, lon NUMERIC, radius_km NUMERIC)
RETURNS TABLE(place_id UUID, place_name VARCHAR, distance_km NUMERIC) AS $$
    SELECT
        id,
        name,
        ST_Distance(location, ST_SetSRID(ST_MakePoint(lon, lat), 4326)) / 1000 AS distance_km
    FROM goa_places
    WHERE ST_DWithin(
        location,
        ST_SetSRID(ST_MakePoint(lon, lat), 4326),
        radius_km * 1000
    )
    ORDER BY distance_km;
$$ LANGUAGE SQL;

-- Populate distance matrix for a single place
CREATE OR REPLACE FUNCTION populate_distance_matrix_for_place(target_place_id UUID)
RETURNS INTEGER AS $$
-- Implementation populates distances from target_place_id to all other places
$$ LANGUAGE PLPGSQL;

-- Populate full distance matrix (run once after data import)
CREATE OR REPLACE FUNCTION populate_full_distance_matrix()
RETURNS INTEGER AS $$
-- Implementation populates all pairwise distances
$$ LANGUAGE PLPGSQL;
```

### Database Setup Commands

```bash
# 1. Create database and user
sudo -u postgres psql
CREATE DATABASE wanderwise_db;
CREATE USER wanderwise_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE wanderwise_db TO wanderwise_user;

# 2. Enable extensions
\c wanderwise_db
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
CREATE EXTENSION "uuid-ossp";
CREATE EXTENSION pg_trgm;
\q

# 3. Run setup script
psql -U wanderwise_user -d wanderwise_db -f database/database_setup.sql

# 4. Verify setup
psql -U wanderwise_user -d wanderwise_db
\dt                          -- List tables
\d goa_places                -- Describe main table
SELECT PostGIS_Version();    -- Verify PostGIS
\q
```

---

## 🏗️ Planned Backend Architecture

### Directory Structure (TO BE CREATED)

```
/home/user/WanderWise-FYP/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI application entry point
│   │   ├── config.py                  # Environment configuration
│   │   ├── database.py                # Database connection and session management
│   │   ├── models/                    # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   └── places.py              # Place model with PostGIS types
│   │   ├── schemas/                   # Pydantic validation schemas
│   │   │   ├── __init__.py
│   │   │   ├── places.py              # Place request/response schemas
│   │   │   └── routes.py              # Route schemas
│   │   ├── api/                       # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── places.py              # Place CRUD endpoints
│   │   │   └── routes.py              # Route planning endpoints
│   │   ├── services/                  # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── route_planner.py       # TSP and optimization algorithms
│   │   │   ├── recommender.py         # Recommendation engine
│   │   │   └── distance_calculator.py # Distance computation
│   │   └── utils/                     # Utility functions
│   │       ├── __init__.py
│   │       └── spatial.py             # PostGIS helpers
│   ├── scripts/
│   │   ├── import_csv_data.py         # Import CSV to database
│   │   └── populate_distances.py      # Populate distance matrix
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py                # Pytest configuration
│   │   ├── test_api/
│   │   │   ├── test_places.py
│   │   │   └── test_routes.py
│   │   ├── test_services/
│   │   │   └── test_route_planner.py
│   │   └── test_utils/
│   │       └── test_spatial.py
│   ├── requirements.txt               # Python dependencies
│   ├── .env.example                   # Environment template
│   └── pytest.ini                     # Test configuration
├── database/                          # ✅ EXISTS
│   └── database_setup.sql
├── Wanderwise_datasetnew.csv          # ✅ EXISTS
├── diagrams/                          # ✅ EXISTS
├── docs/                              # ✅ EXISTS
├── Research_papers/                   # ✅ EXISTS
├── presentation/                      # ✅ EXISTS
├── CLAUDE.md                          # ✅ THIS FILE
├── README.md                          # ✅ EXISTS
├── QUICKSTART.md                      # ✅ EXISTS
├── SETUP_SUMMARY.md                   # ✅ EXISTS
├── .gitignore                         # ✅ EXISTS
└── .git/                              # ✅ EXISTS
```

### Design Patterns to Follow

1. **Repository Pattern** - Data access abstraction in models
2. **Service Layer** - Business logic separated from API routes
3. **Schema Validation** - Pydantic schemas for all API I/O
4. **Dependency Injection** - FastAPI dependencies for DB sessions
5. **Spatial First** - PostGIS for all geographic operations (not Python libraries)

### Spatial Data Handling Strategy

- **Coordinates:** Always use WGS84 (SRID 4326) decimal degrees
- **Data Type:** Use `GEOGRAPHY` (not `GEOMETRY`) for accurate spherical distances
- **Distance Calculations:** PostGIS `ST_Distance()` returns meters for GEOGRAPHY
- **Spatial Queries:** Use `ST_DWithin()` for radius searches (more efficient than ST_Distance in WHERE)
- **Indexing:** GIST indexes are mandatory for spatial performance
- **Python Integration:** GeoAlchemy2 for SQLAlchemy ORM, Shapely for geometry manipulation

### Route Optimization Strategy

1. **Distance Matrix:** Pre-compute all pairwise distances (populate once, use many times)
2. **TSP Solver:** Use `python-tsp` library for small problems (≤15 places)
3. **Heuristics:** Nearest neighbor for initial solution, 2-opt for improvement
4. **Advanced:** OR-Tools for larger problems with time window constraints
5. **Caching:** Redis for frequently requested routes (future enhancement)

---

## 📦 Required Dependencies

### Create `backend/requirements.txt`:

```txt
# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
asyncpg==0.29.0
alembic==1.13.1

# Spatial
geoalchemy2==0.14.2
shapely==2.0.2
geopy==2.4.1
pyproj==3.6.1

# Optimization
python-tsp==0.4.1
ortools==9.8.3296
networkx==3.2.1
scipy==1.12.0
numpy==1.26.3

# Validation & Config
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0

# Data Processing
pandas==2.2.0

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
httpx==0.26.0

# Code Quality
black==24.1.1
isort==5.13.2
flake8==7.0.0
```

### Create `backend/.env.example`:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=wanderwise_db
DB_USER=wanderwise_user
DB_PASSWORD=your_secure_password

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Environment
ENVIRONMENT=development

# Spatial Configuration
DEFAULT_SRID=4326
AVERAGE_SPEED_KMH=30

# Optional (Future)
REDIS_HOST=localhost
REDIS_PORT=6379
SECRET_KEY=your-secret-key-here
```

---

## 🔧 Development Workflow

### 1. Initial Setup (First Time)

```bash
# Navigate to project
cd /home/user/WanderWise-FYP

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create backend structure
mkdir -p backend/app/{models,schemas,api,services,utils}
mkdir -p backend/scripts
mkdir -p backend/tests/{test_api,test_services,test_utils}

# Create __init__.py files
touch backend/app/__init__.py
touch backend/app/models/__init__.py
touch backend/app/schemas/__init__.py
touch backend/app/api/__init__.py
touch backend/app/services/__init__.py
touch backend/app/utils/__init__.py
touch backend/tests/__init__.py

# Install dependencies (after creating requirements.txt)
cd backend
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Set up PostgreSQL (if not already running)
sudo systemctl start postgresql

# Create database (first time only)
sudo -u postgres psql -c "CREATE DATABASE wanderwise_db;"
sudo -u postgres psql -c "CREATE USER wanderwise_user WITH ENCRYPTED PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE wanderwise_db TO wanderwise_user;"

# Run schema setup
psql -U wanderwise_user -d wanderwise_db -f database/database_setup.sql

# Verify setup
psql -U wanderwise_user -d wanderwise_db -c "\dt"
psql -U wanderwise_user -d wanderwise_db -c "SELECT PostGIS_Version();"
```

### 3. Data Import (After creating import script)

```bash
cd backend
python scripts/import_csv_data.py

# Verify import
psql -U wanderwise_user -d wanderwise_db -c "SELECT COUNT(*) FROM goa_places;"
# Expected: 100 rows

# Populate distance matrix
psql -U wanderwise_user -d wanderwise_db -c "SELECT populate_full_distance_matrix();"
# Expected: ~10,000 distance pairs created

# Refresh materialized views
psql -U wanderwise_user -d wanderwise_db -c "REFRESH MATERIALIZED VIEW popular_places;"
psql -U wanderwise_user -d wanderwise_db -c "REFRESH MATERIALIZED VIEW goa_beaches;"
```

### 4. Development Server

```bash
cd backend
source ../venv/bin/activate  # if not already activated

# Run development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Server will be available at:
# - API: http://localhost:8000
# - Interactive docs: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

### 5. Testing

```bash
cd backend

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api/test_places.py -v

# Run specific test
pytest tests/test_api/test_places.py::test_get_all_places -v
```

### 6. Code Quality

```bash
cd backend

# Format code with Black (88 char line length)
black app/ --line-length 88

# Sort imports with isort
isort app/ --profile black

# Lint with flake8
flake8 app/ --max-line-length=88 --extend-ignore=E203,W503
```

---

## 🎯 Implementation Roadmap

### Phase 1: Database & Infrastructure (CURRENT PHASE)

**Status:** Database schema ready, needs deployment and data import

**Tasks:**
1. ✅ Database schema designed (`database/database_setup.sql`)
2. ✅ Dataset prepared (`Wanderwise_datasetnew.csv`)
3. ⬜ Set up PostgreSQL + PostGIS on target environment
4. ⬜ Run database setup script
5. ⬜ Create Python import script (`backend/scripts/import_csv_data.py`)
6. ⬜ Import CSV data to database
7. ⬜ Populate distance matrix (initial population)
8. ⬜ Verify data integrity and spatial indexes

**Success Criteria:**
- PostgreSQL running with PostGIS extensions
- 100 places imported correctly
- ~10,000 distance pairs computed
- Spatial queries working (`ST_Distance`, `ST_DWithin`)

---

### Phase 2: Backend Core (NEXT PHASE)

**Status:** Not started - no code exists yet

**Tasks:**

1. **Project Structure**
   - ⬜ Create `backend/app/` directory structure
   - ⬜ Create `requirements.txt` with dependencies
   - ⬜ Create `.env.example` template
   - ⬜ Set up virtual environment

2. **Configuration & Database Connection**
   - ⬜ Implement `backend/app/config.py` - Pydantic settings
   - ⬜ Implement `backend/app/database.py` - SQLAlchemy engine & session

3. **Data Models**
   - ⬜ Implement `backend/app/models/places.py` - SQLAlchemy ORM models
     - `GoaPlace` model with GeoAlchemy2 GEOGRAPHY type
     - `DistanceMatrix` model
     - `UserRoute` model
   - ⬜ Add proper type hints (`Mapped[Type]`)
   - ⬜ Configure relationships

4. **Pydantic Schemas**
   - ⬜ Implement `backend/app/schemas/places.py`
     - `PlaceBase`, `PlaceCreate`, `PlaceUpdate`, `PlaceResponse`
     - `PlaceListResponse` with pagination
     - `NearbySearchParams`
   - ⬜ Add field validation (min/max, formats)

5. **API Endpoints - Places**
   - ⬜ Implement `backend/app/api/places.py`
     - `GET /api/v1/places` - List with pagination & filters
     - `GET /api/v1/places/{id}` - Get place details
     - `GET /api/v1/places/search` - Text search
     - `GET /api/v1/places/nearby` - Spatial search (ST_DWithin)
     - `GET /api/v1/places/category/{category}` - Filter by category
   - ⬜ Add proper error handling (404, 422, 500)

6. **FastAPI Application**
   - ⬜ Implement `backend/app/main.py`
     - Initialize FastAPI app
     - Configure CORS
     - Include routers
     - Add exception handlers
     - Create health check endpoint

**Success Criteria:**
- Server runs successfully: `uvicorn app.main:app --reload`
- Interactive docs accessible at `/docs`
- All 5+ place endpoints working
- Database queries optimized with proper indexes
- Proper error handling and validation

---

### Phase 3: Route Optimization

**Status:** Planned - requires Phase 2 completion

**Tasks:**

1. **Spatial Utilities**
   - ⬜ Implement `backend/app/utils/spatial.py`
     - `get_distance_between_places()` - Fetch from matrix
     - `get_distance_matrix_for_places()` - Build NumPy matrix
     - `calculate_haversine_distance()` - Fallback calculation
     - `estimate_travel_time()` - Distance to minutes
     - `validate_coordinates()` - Goa boundary check

2. **Route Planner Service**
   - ⬜ Implement `backend/app/services/route_planner.py`
     - `optimize_route()` - Core TSP solver (python-tsp)
     - `create_time_constrained_route()` - Time budget optimization
     - `recommend_route_by_preferences()` - Preference filtering
     - `_build_distance_matrix()` - Convert to NumPy array
     - `_optimize_tsp()` - TSP algorithm (exact or heuristic)
     - `_calculate_schedule()` - Generate arrival/departure times

3. **Route Schemas**
   - ⬜ Implement `backend/app/schemas/routes.py`
     - `RouteOptimizeRequest/Response`
     - `TimeConstrainedRouteRequest/Response`
     - `RouteRecommendRequest/Response`
     - `ScheduleStop` - Individual stop details

4. **Route Endpoints**
   - ⬜ Implement `backend/app/api/routes.py`
     - `POST /api/v1/routes/optimize` - TSP optimization
     - `POST /api/v1/routes/recommend` - Preference-based
     - `POST /api/v1/routes/time-constrained` - Time budget
     - `POST /api/v1/routes/distance` - Calculate distance
     - `GET /api/v1/routes/places/{id}/nearby-routes` - Nearby suggestions

**Algorithms:**
- **Exact TSP:** Dynamic programming (≤10 places)
- **Heuristic TSP:** Simulated annealing (>10 places)
- **2-Opt:** Local search improvement
- **Greedy:** Preference filtering and trimming

**Success Criteria:**
- TSP optimization working for 2-20 places
- Route optimization < 1 second for 10 places
- Time constraint handling with auto-trimming
- Fixed start/end point support
- Schedule generation with accurate timing

---

### Phase 4: Testing & Quality

**Status:** Future phase

**Tasks:**

1. **Unit Tests**
   - `tests/test_models.py` - Model validation
   - `tests/test_schemas.py` - Pydantic validation
   - `tests/test_services/test_route_planner.py` - Algorithm accuracy
   - `tests/test_utils/test_spatial.py` - Distance calculations

2. **Integration Tests**
   - `tests/test_api/test_places.py` - Place endpoints
   - `tests/test_api/test_routes.py` - Route endpoints
   - `tests/test_database.py` - Database operations

3. **Test Configuration**
   - `tests/conftest.py` - Pytest fixtures
   - `pytest.ini` - Test configuration
   - Test database setup/teardown

**Coverage Goal:** 80%+ code coverage

---

### Phase 5: Advanced Features (Future)

**Planned Enhancements:**

1. **Caching (Redis)**
   - Cache distance lookups (TTL: 1 week)
   - Cache popular routes (TTL: 1 day)
   - Cache search results (TTL: 1 hour)

2. **Authentication**
   - JWT token-based auth
   - User registration/login
   - Protected endpoints for saving routes

3. **Enhanced Recommendations**
   - Collaborative filtering (users who visited X also visited Y)
   - Contextual recommendations (time of day, weather, season)
   - Diversity optimization in routes

4. **Analytics**
   - Track popular routes
   - Most visited places
   - Usage statistics

---

## 💻 Code Conventions

### Python Style

- **Formatting:** Black with 88 character line length
- **Imports:** isort with "black" profile
- **Type Hints:** Use throughout (PEP 484)
- **Docstrings:** Google style for all public functions
- **Naming:**
  - `snake_case` for functions, variables, modules
  - `PascalCase` for classes
  - `UPPER_CASE` for constants

### Database Conventions

- **Primary Keys:** UUIDs for all tables (use `uuid_generate_v4()`)
- **Timestamps:** Always `TIMESTAMP WITH TIME ZONE`, auto-update via triggers
- **Arrays:** PostgreSQL arrays for multi-valued attributes
- **JSONB:** Use for flexible/schema-less data (preferences, metadata)
- **Constraints:** Always validate at database level (NOT NULL, CHECK, etc.)
- **Naming:** `idx_table_column` for indexes, `fk_table_column` for foreign keys

### API Design

- **Versioning:** `/api/v1/` prefix for all endpoints
- **Pagination:** Default limit 50, max 100
- **Filtering:** Query parameters (`?category=Beach&min_popularity=7`)
- **Sorting:** Query parameter (`?sort=popularity_score:desc`)
- **Search:** Query parameter (`?q=search_term`)
- **Spatial:** Query parameters (`?lat=X&lon=Y&radius=Z`)
- **HTTP Methods:** GET (read), POST (create/complex), PUT (full update), PATCH (partial), DELETE
- **Status Codes:** 200 (OK), 201 (Created), 400 (Bad Request), 404 (Not Found), 422 (Validation Error), 500 (Server Error)

### Spatial Data

- **Coordinate Order:** Longitude, Latitude in PostGIS (reversed from common usage!)
  - `ST_MakePoint(longitude, latitude)` ← CORRECT
  - Common mistake: `ST_MakePoint(latitude, longitude)` ← WRONG
- **SRID:** Always explicitly set to 4326 for WGS84
- **Geography vs Geometry:** Use `GEOGRAPHY` for accuracy, `GEOMETRY` for speed
- **Distance Units:** `ST_Distance()` with GEOGRAPHY returns meters
- **Radius Searches:** Always use `ST_DWithin()`, not `ST_Distance() < threshold`

### Error Handling

- **Database Errors:** Catch and convert to HTTPException with appropriate status
- **Validation Errors:** Let Pydantic handle, return 422 Unprocessable Entity
- **Not Found:** Return 404 with clear message
- **Server Errors:** Log full traceback, return 500 with generic message (production)

---

## 🔍 Common Tasks & Examples

### Task 1: Adding a New Place Field

**Example:** Add `average_crowd_level` field (Low/Medium/High)

1. **Update Database Schema**
   ```sql
   -- Add ENUM type
   CREATE TYPE crowd_level AS ENUM ('Low', 'Medium', 'High');

   -- Add column
   ALTER TABLE goa_places
   ADD COLUMN average_crowd_level crowd_level DEFAULT 'Medium';
   ```

2. **Update SQLAlchemy Model** (`backend/app/models/places.py`)
   ```python
   from sqlalchemy import Enum

   class GoaPlace(Base):
       # ... existing fields ...
       average_crowd_level: Mapped[str] = mapped_column(
           Enum('Low', 'Medium', 'High', name='crowd_level'),
           default='Medium'
       )
   ```

3. **Update Pydantic Schema** (`backend/app/schemas/places.py`)
   ```python
   from pydantic import BaseModel
   from typing import Literal

   class PlaceBase(BaseModel):
       # ... existing fields ...
       average_crowd_level: Literal['Low', 'Medium', 'High'] = 'Medium'
   ```

4. **Update CSV Import** (if field exists in CSV)
   ```python
   # In import_csv_data.py
   place = GoaPlace(
       # ... existing fields ...
       average_crowd_level=row['average_crowd_level']
   )
   ```

### Task 2: Creating a New API Endpoint

**Example:** Get top N places by popularity

1. **Define Schema** (`backend/app/schemas/places.py`)
   ```python
   class TopPlacesRequest(BaseModel):
       limit: int = Field(default=10, ge=1, le=50)
       category: Optional[str] = None
   ```

2. **Add Route Handler** (`backend/app/api/places.py`)
   ```python
   @router.get("/top", response_model=List[PlaceResponse])
   async def get_top_places(
       limit: int = Query(default=10, ge=1, le=50),
       category: Optional[str] = None,
       db: Session = Depends(get_db)
   ):
       """Get top N places by popularity score."""
       query = db.query(GoaPlace).order_by(GoaPlace.popularity_score.desc())

       if category:
           query = query.filter(GoaPlace.category == category)

       places = query.limit(limit).all()
       return places
   ```

3. **Test Endpoint**
   ```bash
   curl "http://localhost:8000/api/v1/places/top?limit=5&category=Beach"
   ```

### Task 3: Optimizing a Spatial Query

**Example:** Find all beaches within 10km of a point

**❌ Inefficient (doesn't use spatial index):**
```python
# BAD: Computes distance for every row
places = db.query(GoaPlace).filter(
    func.ST_Distance(GoaPlace.location, point) < 10000
).all()
```

**✅ Efficient (uses GIST index):**
```python
# GOOD: Uses ST_DWithin with spatial index
from geoalchemy2 import WKTElement

point = WKTElement(f'POINT({lon} {lat})', srid=4326)

places = db.query(GoaPlace).filter(
    GoaPlace.category == 'Beach',
    func.ST_DWithin(GoaPlace.location, point, 10000)  # 10km in meters
).order_by(
    func.ST_Distance(GoaPlace.location, point)  # Sort by distance
).all()
```

### Task 4: Handling Pipe-Delimited Fields

**Example:** Query places with specific facilities

```python
# In models/places.py - facilities is TEXT[] array

# Query places with parking
places = db.query(GoaPlace).filter(
    GoaPlace.facilities.any('Parking')
).all()

# Query places with multiple facilities (AND)
places = db.query(GoaPlace).filter(
    GoaPlace.facilities.contains(['Parking', 'Toilets'])
).all()

# Query places with any facility (OR)
from sqlalchemy import or_
places = db.query(GoaPlace).filter(
    or_(
        GoaPlace.facilities.any('Parking'),
        GoaPlace.facilities.any('Food')
    )
).all()
```

---

## 🚨 Troubleshooting

### Problem: PostGIS extension not found

```bash
# Install PostGIS
sudo apt install postgresql-12-postgis-3  # Ubuntu/Debian
brew install postgis                      # macOS

# Enable in database
psql -U wanderwise_user -d wanderwise_db
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
```

### Problem: Import errors with GeoAlchemy2

```python
# Correct imports for GeoAlchemy2
from geoalchemy2 import Geography, Geometry
from geoalchemy2.elements import WKTElement
from geoalchemy2.functions import ST_Distance, ST_DWithin, ST_MakePoint

# NOT: from geoalchemy2.types import Geography  # Old syntax
```

### Problem: Database connection refused

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check connection parameters
psql -U wanderwise_user -d wanderwise_db -h localhost -p 5432

# Check .env file has correct credentials
cat backend/.env
```

### Problem: Slow spatial queries

```sql
-- Check if spatial index exists
\d+ goa_places

-- Should see: idx_goa_places_location | gist | location

-- If missing, create it:
CREATE INDEX idx_goa_places_location ON goa_places USING GIST(location);

-- Verify query plan uses index
EXPLAIN ANALYZE
SELECT * FROM goa_places
WHERE ST_DWithin(location, ST_SetSRID(ST_MakePoint(73.8, 15.5), 4326), 10000);
```

### Problem: Coordinate order confusion

```python
# PostGIS uses (longitude, latitude) - opposite of common usage!

# ✅ CORRECT
point = WKTElement(f'POINT({longitude} {latitude})', srid=4326)

# ❌ WRONG
point = WKTElement(f'POINT({latitude} {longitude})', srid=4326)

# Easy way to remember: X comes before Y, Longitude is X, Latitude is Y
```

---

## 📚 Important References

### PostGIS Documentation

- [PostGIS Reference](https://postgis.net/docs/reference.html)
- [ST_Distance](https://postgis.net/docs/ST_Distance.html) - Calculate distance
- [ST_DWithin](https://postgis.net/docs/ST_DWithin.html) - Radius search (indexed!)
- [ST_MakePoint](https://postgis.net/docs/ST_MakePoint.html) - Create point geometry
- [Geography vs Geometry](https://postgis.net/workshops/postgis-intro/geography.html)

### FastAPI Documentation

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy with FastAPI](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)

### SQLAlchemy 2.0

- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/en/20/)
- [ORM Mapped Column](https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html)
- [GeoAlchemy2](https://geoalchemy-2.readthedocs.io/)

### Route Optimization

- [python-tsp](https://github.com/fillipe-gsm/python-tsp) - TSP solver
- [OR-Tools](https://developers.google.com/optimization) - Google's optimization tools
- [TSP Algorithms](https://en.wikipedia.org/wiki/Travelling_salesman_problem)

---

## 📝 Development Notes

### Current Status Summary

**Repository Path:** `/home/user/WanderWise-FYP/`

**What Works:**
- ✅ Database schema is production-ready
- ✅ Dataset is clean and validated (100 destinations)
- ✅ Documentation is comprehensive
- ✅ Architecture is well-designed

**What Needs Work:**
- ❌ No backend code implemented yet
- ❌ No API endpoints
- ❌ No data import scripts
- ❌ No tests
- ❌ No dependencies installed

**Next Immediate Steps:**
1. Set up PostgreSQL + PostGIS
2. Run `database/database_setup.sql`
3. Create `backend/requirements.txt`
4. Create `backend/app/` directory structure
5. Implement data import script
6. Import CSV data
7. Start implementing FastAPI application

---

## 🎓 Learning Resources

### For Spatial Databases
- [PostGIS Tutorial](https://postgis.net/workshops/postgis-intro/)
- [Introduction to GIS](https://www.gislounge.com/what-is-gis/)
- [WGS84 Coordinate System](https://en.wikipedia.org/wiki/World_Geodetic_System)

### For Route Optimization
- [Traveling Salesman Problem](https://en.wikipedia.org/wiki/Travelling_salesman_problem)
- [2-Opt Algorithm](https://en.wikipedia.org/wiki/2-opt)
- [Simulated Annealing](https://en.wikipedia.org/wiki/Simulated_annealing)

### For FastAPI Development
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Pydantic v2 Migration](https://docs.pydantic.dev/latest/migration/)
- [SQLAlchemy 2.0 Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)

---

## 👥 Contributing

When implementing features:

1. **Read this guide first** - Understand the architecture
2. **Follow conventions** - Code style, naming, patterns
3. **Test thoroughly** - Write tests for new features
4. **Document as you go** - Update this file with learnings
5. **Commit meaningful changes** - Clear commit messages

---

## 📧 Support & Contact

For questions about this project:
- Check this CLAUDE.md file first
- Review README.md and QUICKSTART.md
- Check database schema in `database/database_setup.sql`
- Review system diagrams in `diagrams/`

---

**Last Updated:** November 22, 2025
**Repository:** /home/user/WanderWise-FYP/
**Status:** Planning Phase - Ready for Implementation
