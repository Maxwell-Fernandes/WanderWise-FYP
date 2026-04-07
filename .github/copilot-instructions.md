# GitHub Copilot Instructions - WanderWise+

WanderWise+ is an intelligent tourism route planning system for Goa, India. It uses AI to personalize multi-day itineraries with optimal route planning.

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0+, GeoAlchemy2
- **Database**: PostgreSQL 12+ with PostGIS 3.0+
- **Frontend**: React 19+, Vite, TailwindCSS 4+, React Router 7+
- **Route Optimization**: python-tsp, OR-Tools, SciPy, NetworkX
- **Spatial**: Shapely, GeoPy, PyProj

## Build, Run, and Test Commands

### Backend

```bash
# Setup (first time)
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run development server
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# API docs at http://localhost:8000/docs

# Run tests
cd backend
pytest tests/ -v                                      # All tests
pytest tests/test_places.py -v                        # Specific file
pytest tests/test_places.py::test_function_name -v    # Single test
pytest -k "test_nearby" -v                            # Match by keyword
pytest --lf -v                                        # Failed tests only
pytest tests/ -v --cov=app --cov-report=html         # With coverage

# Code quality
black app/                    # Format code
isort app/                    # Sort imports
black app/ && isort app/      # Both together
flake8 app/                   # Style violations
pylint app/                   # Comprehensive linting
mypy app/                     # Type checking
```

### Frontend

```bash
# Setup (first time)
cd frontend
npm install

# Run development server
npm run dev              # Starts at http://localhost:5173

# Build for production
npm run build

# Preview production build
npm run preview

# Linting
npm run lint             # ESLint
npm run lint -- --fix    # Auto-fix
```

### Database

```bash
# Connect to database
export PGPASSWORD="WanderWise2024!Secure"
psql -U wanderwise_user -d wanderwise_db

# Setup schema
psql -U wanderwise_user -d wanderwise_db -f database/database_setup.sql

# Import CSV data
cd backend
python scripts/import_csv_data.py

# Populate distance matrix (slow operation - run once)
psql -U wanderwise_user -d wanderwise_db -c "SELECT populate_full_distance_matrix();"
```

## High-Level Architecture

### System Overview
WanderWise+ consists of 4 main modules:
1. **Module I (NLC)**: Natural language classification of user interests using TF-IDF + Logistic Regression
2. **Module II**: POI popularity scoring using Google popularity metrics
3. **Module III**: K-Means geographic clustering to group POIs by day (K = number of days)
4. **Module IV**: Genetic Algorithm for optimal daily route planning (TTDP/OPTW problem)

### Backend Structure
```
backend/app/
├── api/          # FastAPI route handlers
├── models/       # SQLAlchemy ORM models
├── schemas/      # Pydantic validation schemas
├── services/     # Business logic (route planning, clustering)
├── utils/        # Helper functions (spatial calculations)
├── config.py     # Application configuration
├── database.py   # Database connection
└── main.py       # FastAPI app entry point
```

### Data Flow
1. User inputs preferences in natural language → Module I classifies interests
2. System queries POIs matching interests → Module II filters by popularity
3. POIs grouped by day using K-Means clustering → Module III
4. Each day's route optimized with GA → Module IV
5. Complete itinerary returned with timeline and map

## Key Conventions and Patterns

### Python Code Style

**Required Type Hints**
```python
# All function signatures MUST have type hints
def get_places(db: Session, limit: int = 10) -> list[Place]:
    return db.query(Place).limit(limit).all()
```

**Import Order**
```python
# Standard library
from datetime import datetime
from typing import List, Optional

# Third-party
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session

# Local application
from app.models.places import Place
from app.schemas.places import PlaceResponse
```

**Naming Conventions**
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private methods: `_leading_underscore`
- Database models: Singular (e.g., `Place` not `Places`)
- Pydantic schemas: Match model name or add suffix (e.g., `PlaceResponse`, `PlaceCreate`)

**Error Handling**
```python
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

try:
    place = db.query(Place).filter(Place.id == place_id).first()
    if not place:
        raise HTTPException(status_code=404, detail=f"Place {place_id} not found")
except Exception as e:
    logger.error(f"Error fetching place {place_id}: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

**Docstrings**
Use Google-style docstrings for all public functions:
```python
def optimize_route(place_ids: list[str], method: str = "auto") -> tuple[list[str], float]:
    """
    Optimize route through multiple places using TSP.

    Args:
        place_ids: List of place UUIDs to visit
        method: Optimization method ("exact", "heuristic", "auto")

    Returns:
        Tuple of (optimized_place_ids, total_distance_km)

    Raises:
        ValueError: If less than 2 places provided
        HTTPException: If places not found in database
    """
    pass
```

### React/Frontend Conventions

**Component Structure**
```jsx
// Functional components with hooks only
export default function InterestInputPage() {
  const [interests, setInterests] = useState([]);
  // Component logic
}
```

**Styling**
```jsx
import { cn } from '@/lib/utils';

// Use Tailwind CSS classes, avoid inline styles
<button className={cn(
  "px-4 py-2 rounded",
  isActive && "bg-blue-500",
  isDisabled && "opacity-50"
)}>
  Click me
</button>
```

## Critical Architecture Rules

### Spatial Data Handling
- **Always use PostGIS GEOGRAPHY type (SRID 4326)** for coordinates
- Goa bounds: Latitude 14.8-15.9, Longitude 73.6-74.4
- All distance values must be non-negative
- Place IDs are UUIDs, not integers

```python
from geoalchemy2 import Geography
from geoalchemy2.functions import ST_Distance

# Define spatial column
location = Column(Geography(geometry_type='POINT', srid=4326))

# Query nearby places
nearby = db.query(Place).filter(
    ST_Distance(Place.location, poi_location) < radius_meters
).all()
```

### Distance Calculations
**CRITICAL**: Use pre-cached `distance_matrix` table, NOT real-time PostGIS queries for route optimization.

```python
# ❌ NEVER do this in route optimization
distance = ST_Distance(place1.location, place2.location)

# ✅ ALWAYS use distance_matrix table
distance = db.query(DistanceMatrix.distance_km).filter(
    DistanceMatrix.from_place_id == place1_id,
    DistanceMatrix.to_place_id == place2_id
).scalar()
```

### Route Optimization Algorithm Selection
Choose algorithm based on number of places:
- **≤10 places**: Use exact TSP (dynamic programming via `python-tsp`)
- **>10 places**: Use heuristic TSP (simulated annealing or genetic algorithm)

```python
def optimize_route(places: list[Place]) -> list[Place]:
    if len(places) <= 10:
        # Use exact solver for small problems
        return solve_tsp_exact(places)
    else:
        # Use heuristic for larger problems
        return solve_tsp_genetic_algorithm(places)
```

### Database Access
- **Always use SQLAlchemy ORM**, never raw SQL in application code
- Database migrations: Use Alembic
- All API responses must use Pydantic schemas for validation

### Adding New API Endpoints
1. Create Pydantic schema in `app/schemas/`
2. Add route handler in `app/api/routes.py`
3. Use dependency injection: `db: Session = Depends(get_db)`
4. Return Pydantic schema instances

### Adding Database Models
1. Define SQLAlchemy model in `app/models/`
2. Create migration: `alembic revision --autogenerate -m "description"`
3. Review migration file
4. Apply: `alembic upgrade head`

## Important Files

- `AGENTS.md`: Comprehensive development guide for AI coding agents
- `QUICKSTART.md`: Quick setup guide
- `backend/.env`: Environment variables (DB credentials - never commit!)
- `backend/app/config.py`: Application settings
- `database/database_setup.sql`: Database schema and PostGIS functions
- `Wanderwise_datasetnew.csv`: POI dataset (100+ Goa tourist attractions)

## What NOT to Do

- ❌ Never commit `.env` files or hardcode database passwords
- ❌ Never use `SELECT *` in production code
- ❌ Never calculate distances in Python for route optimization (use `distance_matrix` table)
- ❌ Never use `print()` for logging (use `logging` module)
- ❌ Never modify `database_setup.sql` without testing in development first
- ❌ Never use class components in React (functional components only)

## Environment Setup

Database credentials are in `backend/.env`:
```env
DB_USER=wanderwise_user
DB_PASSWORD=WanderWise2024!Secure
DB_NAME=wanderwise_db
DB_HOST=localhost
DB_PORT=5432
```

Frontend API URL in `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
```

## Genetic Algorithm Parameters

When implementing or tuning the GA for route optimization:
```python
GA_PARAMS = {
    "population_size": 100,
    "max_generations": 50,
    "crossover_rate": 0.8,
    "mutation_rate": 0.2,
    "tournament_size": 5,
    "elite_count": 2,
}

FITNESS_WEIGHTS = {
    "alpha": 0.1,   # Travel time penalty
    "beta": 1.0,    # Constraint penalty
}

PENALTIES = {
    "closed_poi": 30.0,
    "lunch_invasion": 20.0,
    "overtime_per_min": 0.5,
}
```

## Common Tasks

### Run full development stack
```bash
# Terminal 1: Database (should already be running)
# If not: sudo systemctl start postgresql

# Terminal 2: Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 3: Frontend
cd frontend
npm run dev
```

### Verify database setup
```bash
psql -U wanderwise_user -d wanderwise_db -c "SELECT COUNT(*) FROM goa_places;"
# Expected: 100

psql -U wanderwise_user -d wanderwise_db -c "SELECT COUNT(*) FROM distance_matrix;"
# Expected: ~9,900 (if populated)
```

### Format code before committing
```bash
# Backend
cd backend
black app/ && isort app/

# Frontend
cd frontend
npm run lint -- --fix
```
