# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WanderWise+ is an intelligent tourism route planning system for Goa, India. It uses PostGIS spatial databases, FastAPI backend, and route optimization algorithms to help tourists plan optimal itineraries.

**Tech Stack:**
- Backend: Python 3.11+, FastAPI, SQLAlchemy 2.0+, GeoAlchemy2
- Database: PostgreSQL 12+ with PostGIS 3.0+
- Route Optimization: python-tsp, OR-Tools, SciPy, NetworkX
- Spatial: Shapely, GeoPy, PyProj

## Database Connection

The application connects to PostgreSQL using credentials from `backend/.env`. The database password is stored in the environment:
- DB_PASSWORD="WanderWise2024!Secure"
- Database: wanderwise_db
- User: wanderwise_user

To connect to the database directly:
```bash
export PGPASSWORD="WanderWise2024!Secure"
psql -U wanderwise_user -d wanderwise_db
```

## Development Commands

### Running the Backend
```bash
# From backend directory
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API Documentation available at:
# http://localhost:8000/docs
```

### Database Operations
```bash
# Setup database schema
psql -U wanderwise_user -d wanderwise_db -f database/database_setup.sql

# Import CSV data
cd backend
python scripts/import_csv_data.py

# Populate distance matrix (can be slow, run in psql)
psql -U wanderwise_user -d wanderwise_db
SELECT populate_full_distance_matrix();

# Refresh materialized views
REFRESH MATERIALIZED VIEW popular_places;
REFRESH MATERIALIZED VIEW goa_beaches;
```

### Testing
```bash
cd backend
pytest tests/ -v                    # Run all tests
pytest tests/test_places.py -v     # Run specific test file
pytest tests/ -v --cov=app         # Run with coverage
```

### Code Quality
```bash
cd backend
black app/                          # Format code
isort app/                          # Sort imports
flake8 app/                         # Lint code
mypy app/                           # Type checking
```

## Architecture

### Core Components

**1. Spatial Database Layer** (database/database_setup.sql)
- `goa_places`: Main table with PostGIS GEOGRAPHY points for destinations
- `distance_matrix`: Cached distances between place pairs for performance
- `user_routes`: Saved optimized routes
- PostGIS functions: `find_nearby_places()`, `calculate_distance()`, `populate_distance_matrix_for_place()`
- Materialized views: `popular_places`, `goa_beaches`

**2. Models Layer** (app/models/places.py)
- SQLAlchemy models with GeoAlchemy2 for spatial types
- `Place`: Tourist destinations with spatial data (location as GEOGRAPHY type)
- `DistanceMatrix`: Cached distances with bidirectional relationships
- `UserRoute`: Saved routes with JSONB preferences

**3. Services Layer** (app/services/route_planner.py)
- `RoutePlanner`: Core route optimization class
  - `optimize_route()`: TSP optimization using dynamic programming (≤10 places) or simulated annealing (>10 places)
  - `create_time_constrained_route()`: Routes with max duration constraints
  - `recommend_route_by_preferences()`: Generate routes based on user preferences
  - `_trim_route_by_time()`: Remove lower-priority places to fit time budget

**4. Spatial Utilities** (app/utils/spatial.py)
- Distance calculations using distance_matrix table (not direct PostGIS queries)
- Haversine formula fallback when distances not cached
- Travel time estimation (default: 30 km/h for Goa roads)
- Coordinate validation for Goa boundaries (14.9-15.8 lat, 73.7-74.3 lon)

**5. API Layer** (app/api/routes.py, app/main.py)
- Route optimization endpoints: `/api/v1/routes/optimize`, `/api/v1/routes/recommend`
- Places endpoints: `/api/places`, `/api/places/{id}`, `/api/places/search/nearby`
- Time-constrained routing: `/api/v1/routes/time-constrained`

### Key Architecture Decisions

1. **Distance Matrix Caching**: Distances are pre-calculated and stored in `distance_matrix` table rather than computed on-demand with PostGIS. This trades storage for query speed in route optimization.

2. **TSP Algorithm Selection**:
   - ≤10 places: Exact solution via dynamic programming
   - >10 places: Simulated annealing + local search (2-opt)
   - Method can be overridden with `method` parameter

3. **Spatial Data Storage**: Uses PostGIS GEOGRAPHY type (not GEOMETRY) for accurate real-world distance calculations on Earth's surface (WGS84).

4. **Configuration Management**: Settings loaded from environment variables via pydantic-settings (app/config.py). Database URL constructed from components.

## Important Spatial Concepts

### PostGIS vs Application Layer
- **Never compute distances directly in API**: Always use `distance_matrix` table first
- **Fallback to Haversine**: Only calculate distance on-the-fly if not in cache
- **Spatial indexes**: GIST indexes on `location` columns enable fast nearby searches
- **Triggers**: `sync_location_with_coordinates()` trigger automatically updates GEOGRAPHY point when lat/lon changes

### Distance Matrix Population
The distance matrix must be populated after importing place data:
```sql
-- Populate for all places (slow for large datasets)
SELECT populate_full_distance_matrix();

-- Or populate for specific place
SELECT populate_distance_matrix_for_place('<place_uuid>');
```

### Coordinate System
- SRID 4326 (WGS84) for all spatial data
- Latitude: 14.8 to 15.9 (Goa boundaries with buffer)
- Longitude: 73.6 to 74.4 (Goa boundaries with buffer)

## Data Import Pipeline

1. CSV data is in `Wanderwise_datasetnew.csv` (100+ places)
2. Import script: `backend/scripts/import_csv_data.py`
   - Parses pipe-delimited arrays (facilities, best_for, instagram_tags)
   - Converts times, dates, booleans, numerics
   - Validates coordinates against Goa boundaries
   - Handles ENUM types (difficulty_level, research_status)
3. After import: populate distance matrix and refresh materialized views

## Route Optimization Flow

1. User provides list of place IDs (or preferences for recommendations)
2. System builds NxN distance matrix from `distance_matrix` table
3. TSP algorithm optimizes order:
   - Dynamic programming for exact solution (small N)
   - Simulated annealing + local search (large N)
4. Optional: Apply time constraints (trim route to fit duration)
5. Generate schedule with arrival/departure times for each place

## Configuration

### Environment Variables (backend/.env)
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=wanderwise_db
DB_USER=wanderwise_user
DB_PASSWORD=WanderWise2024!Secure
SECRET_KEY=<your-secret-key>

# Routing parameters
DEFAULT_TRAVEL_SPEED_KMH=40
MAX_OPTIMIZATION_TIME_SECONDS=30
MAX_ROUTE_PLACES=15
DEFAULT_SEARCH_RADIUS_KM=50

# CORS origins for frontend
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Connection Pooling
- Pool size: 5 connections
- Max overflow: 10
- Pool timeout: 30s
- Pool recycle: 3600s (1 hour)

## Common Operations

### Adding New Places
When adding places programmatically:
1. Insert into `goa_places` table (trigger auto-updates GEOGRAPHY point)
2. Run `populate_distance_matrix_for_place(new_place_id)` to cache distances
3. Refresh materialized views if needed

### Modifying Route Algorithms
Route optimization logic is in `app/services/route_planner.py`:
- `_optimize_tsp()`: Core TSP solver
- `_optimize_with_fixed_points()`: Handle fixed start/end
- Adjust algorithm thresholds in `optimize_route()` method

### Adding New Filters
To add place filters:
1. Ensure database column exists with appropriate index
2. Add filter parameter to `app/main.py` endpoint
3. Add SQLAlchemy filter to query in endpoint handler
4. Update Pydantic schema in `app/schemas/places.py`

## Testing Database Queries

Useful queries for debugging:
```sql
-- Check distance matrix coverage
SELECT COUNT(*) FROM distance_matrix;
SELECT COUNT(*) * (COUNT(*) - 1) as expected_distances FROM goa_places;

-- Find places without cached distances
SELECT p.id, p.name, COUNT(dm.id) as cached_count
FROM goa_places p
LEFT JOIN distance_matrix dm ON p.id = dm.place_id_from
GROUP BY p.id, p.name
HAVING COUNT(dm.id) = 0;

-- Test spatial search
SELECT * FROM find_nearby_places(15.5444, 73.7551, 10);

-- Check data quality
SELECT * FROM data_quality_check;

-- View route statistics
SELECT * FROM places_with_distance_stats ORDER BY popularity_score DESC LIMIT 10;
```

## Known Limitations

1. Distance matrix is directional (A→B may differ from B→A if roads are one-way), but current implementation treats as symmetric
2. Travel time estimates use fixed average speed (30-40 km/h), doesn't account for traffic or road conditions
3. Route optimization assumes all places are visitable (doesn't check opening hours against schedule)
4. No integration with real-time routing APIs (OSRM, Google Maps) - uses straight-line distances

## Dependencies Note

Key Python packages and their purposes:
- `geoalchemy2`: SQLAlchemy integration for PostGIS
- `python-tsp`: TSP algorithms (dynamic programming, simulated annealing)
- `ortools`: Google's optimization library for advanced constraints
- `shapely`: Geometric operations
- `geopy`: Geocoding and distance calculations
- `psycopg2-binary`: PostgreSQL adapter

## Frontend (Not Yet Implemented)

Frontend directory exists but is not yet developed. When implementing:
- Use React or similar SPA framework
- Connect to FastAPI backend at `http://localhost:8000`
- Interactive map for place selection and route visualization
- Use Leaflet or Mapbox for mapping
