# AGENTS.md - WanderWise+ Development Guide for AI Coding Agents

This guide provides essential information for AI coding agents (Claude, Cursor, Copilot, etc.) working on WanderWise+, an intelligent tourism route planning system for Goa, India.

## Tech Stack Overview

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0+, GeoAlchemy2
- **Database**: PostgreSQL 12+ with PostGIS 3.0+
- **Frontend**: React 19+, Vite, TailwindCSS 4+, React Router 7+
- **Route Optimization**: python-tsp, OR-Tools, SciPy, NetworkX
- **Spatial**: Shapely, GeoPy, PyProj

## Build/Run Commands

### Backend

```bash
# Setup (first time)
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run development server
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API docs available at http://localhost:8000/docs
```

### Frontend

```bash
# Setup (first time)
cd frontend
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
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

# Populate distance matrix (slow operation)
psql -U wanderwise_user -d wanderwise_db -c "SELECT populate_full_distance_matrix();"
```

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_places.py -v

# Run single test function
pytest tests/test_places.py::test_function_name -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html

# Run specific test with keyword match
pytest -k "test_nearby" -v

# Run failed tests only
pytest --lf -v
```

### Frontend Tests

```bash
cd frontend

# Lint JavaScript/TypeScript
npm run lint

# Lint with auto-fix
npm run lint -- --fix
```

## Code Style Guidelines

### Python (Backend)

#### Imports
- Standard library imports first
- Third-party imports second
- Local application imports last
- Use absolute imports: `from app.models.places import Place`
- Sort imports with `isort app/`

```python
# Standard library
from datetime import datetime
from typing import List, Optional

# Third-party
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session

# Local
from app.models.places import Place
from app.schemas.places import PlaceResponse
```

#### Formatting
- **Formatter**: Black (line length: 88 characters)
- **Import sorter**: isort
- Run before committing: `black app/ && isort app/`

```bash
# Format code
black app/

# Sort imports
isort app/

# Both in one command
black app/ && isort app/
```

#### Type Hints
- **REQUIRED**: All function signatures must have type hints
- Use Python 3.10+ syntax: `list[str]` instead of `List[str]` where possible
- Type check with: `mypy app/`

```python
# Good
def get_places(db: Session, limit: int = 10) -> list[Place]:
    return db.query(Place).limit(limit).all()

# Bad
def get_places(db, limit=10):
    return db.query(Place).limit(limit).all()
```

#### Naming Conventions
- **Functions/variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`
- **Database models**: Singular (e.g., `Place` not `Places`)
- **Pydantic schemas**: Match model name or add suffix (e.g., `PlaceResponse`, `PlaceCreate`)

```python
# Models
class Place(Base):
    __tablename__ = "goa_places"
    
# Constants
MAX_ROUTE_PLACES = 15
DEFAULT_SEARCH_RADIUS_KM = 50

# Functions
def calculate_route_distance(places: list[Place]) -> float:
    pass
```

#### Error Handling
- Use FastAPI's `HTTPException` for API errors
- Include descriptive error messages
- Log errors with appropriate levels

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

#### Docstrings
- Use Google-style docstrings for all public functions/classes
- Include Args, Returns, Raises sections

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

### JavaScript/TypeScript (Frontend)

#### React Components
- Functional components with hooks only
- Component names: `PascalCase`
- File names: `PascalCase.jsx` or `kebab-case.jsx`

```jsx
// Good
export default function InterestInputPage() {
  const [interests, setInterests] = useState([]);
  // ...
}
```

#### Styling
- Use Tailwind CSS classes
- Avoid inline styles unless dynamic
- Use `clsx` or `cn` for conditional classes

```jsx
import { cn } from '@/lib/utils';

<button className={cn(
  "px-4 py-2 rounded",
  isActive && "bg-blue-500",
  isDisabled && "opacity-50"
)}>
  Click me
</button>
```

## Architecture Patterns

### Backend Structure

```
backend/app/
├── api/          # API route handlers
├── models/       # SQLAlchemy ORM models
├── schemas/      # Pydantic validation schemas
├── services/     # Business logic (route planning, etc.)
├── utils/        # Helper functions (spatial calculations)
├── config.py     # App configuration
├── database.py   # Database connection
└── main.py       # FastAPI app entry point
```

### Key Architectural Rules

1. **Spatial Data**: Always use PostGIS GEOGRAPHY type (SRID 4326) for coordinates
2. **Distance Calculations**: Use pre-cached `distance_matrix` table, NOT real-time PostGIS queries
3. **Route Optimization**: 
   - ≤10 places: Use exact TSP (dynamic programming)
   - >10 places: Use heuristic TSP (simulated annealing)
4. **Database Access**: Always use SQLAlchemy ORM, never raw SQL in application code
5. **API Responses**: Always use Pydantic schemas for validation

### Database Constraints

- Goa coordinates: Latitude 14.8-15.9, Longitude 73.6-74.4
- All distance values must be non-negative
- Place IDs are UUIDs, not integers

## Common Tasks

### Adding a New API Endpoint

1. Create Pydantic schema in `app/schemas/`
2. Add route handler in `app/api/routes.py`
3. Use dependency injection for database: `db: Session = Depends(get_db)`
4. Return Pydantic schema instances

### Adding a New Database Model

1. Define SQLAlchemy model in `app/models/`
2. Create migration: `alembic revision --autogenerate -m "description"`
3. Review migration file
4. Apply: `alembic upgrade head`

### Working with Spatial Data

```python
from geoalchemy2 import Geography
from geoalchemy2.functions import ST_Distance

# Define spatial column
location = Column(Geography(geometry_type='POINT', srid=4326))

# Query nearby places (use database functions, not application logic)
nearby = db.query(Place).filter(
    ST_Distance(Place.location, poi_location) < radius_meters
).all()

# Always use distance_matrix table for route optimization
```

## Linting

```bash
# Backend
cd backend
flake8 app/              # Check style violations
pylint app/              # Comprehensive linting
mypy app/                # Type checking

# Frontend
cd frontend
npm run lint             # ESLint
```

## Important Files

- `CLAUDE.md`: Project overview and architecture details
- `backend/.env`: Environment variables (DB credentials)
- `backend/app/config.py`: Application settings
- `database/database_setup.sql`: Database schema and functions
- `Wanderwise_datasetnew.csv`: POI data (100+ places)

## Never Do This

- ❌ Never commit `.env` files
- ❌ Never use `SELECT *` in production code
- ❌ Never calculate distances in Python (use database distance_matrix)
- ❌ Never hardcode database passwords
- ❌ Never use `print()` for logging (use `logging` module)
- ❌ Never modify `database_setup.sql` without testing in development first

## Database Password

Database password is in `backend/.env`: `WanderWise2024!Secure`
Never commit this to version control.
