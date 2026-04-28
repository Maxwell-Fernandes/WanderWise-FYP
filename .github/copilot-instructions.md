# Project Guidelines

WanderWise+ is an AI-assisted, multi-day tourism route planner for Goa, India.

## Build and Test

See [QUICKSTART.md](../QUICKSTART.md) for full setup (database, env, data import).

Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pytest tests/ -v
```

Frontend:
```bash
cd frontend
npm install
npm run dev
npm run lint
```

## Architecture

System modules: NLC (Module I), popularity scoring (Module II), K-Means clustering (Module III), GA routing (Module IV). See [docs/backend/genetic-algorithm-and-clustering.md](../docs/backend/genetic-algorithm-and-clustering.md) and [docs/backend/module4-ga-preference-fitness.md](../docs/backend/module4-ga-preference-fitness.md) for detailed GA and fitness behavior.

Backend layout:

```
backend/app/
  api/      # FastAPI route handlers
  models/   # SQLAlchemy ORM models
  schemas/  # Pydantic validation schemas
  services/ # Business logic (routing, clustering)
  utils/    # Helper functions (spatial calculations)
```

## Conventions

- Python: type hints required on all function signatures; use Google-style docstrings for public functions.
- Imports: standard library, third-party, then local app modules.
- Database: always use SQLAlchemy ORM (no raw SQL); use Alembic for migrations.
- API responses: always return Pydantic schema instances.
- Spatial: PostGIS GEOGRAPHY (SRID 4326) only; Goa bounds lat 14.8-15.9, lon 73.6-74.4.
- Routing: never compute distances ad-hoc; use the pre-cached `distance_matrix` table.
- Logging: use `logging`, not `print()`.
- Frontend: React function components only; Tailwind classes with `cn`/`clsx` helpers (avoid inline styles).

## Data Constraints

- Place IDs are UUIDs (not integers).
- Distances must be non-negative.
