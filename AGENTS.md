# AGENTS.md — WanderWise

Multi-app project for AI-assisted tourism routing in Goa, India. Not a monorepo — each directory is independent.

## Project Layout

```
backend/              # Primary FastAPI backend (notebook simulator, GA routing)
frontend/             # Web frontend (Vite + React, minimal)
wanderwise-mobile/    # Mobile app (separate git root)
  frontend/           # Expo/React Native (TypeScript)
  backend/            # Production backend (SQLAlchemy + PostgreSQL)
```

The two backends share business logic patterns but are **separate codebases** with separate requirements. The mobile backend connects to a real database; the primary backend uses in-memory data.

## Commands

### Primary Backend (`backend/`)
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pytest tests/ -v
```

### Web Frontend (`frontend/`)
```bash
cd frontend
npm install
npm run dev     # Vite dev server (port 5173)
npm run build   # Production build
# Lint is a no-op: `echo 'No lint config yet'`
```

### Mobile Frontend (`wanderwise-mobile/frontend/`)
```bash
cd wanderwise-mobile/frontend
npm install
npm start       # expo start
npm run android # expo run:android
npm run ios     # expo run:ios
```

### Mobile Backend (`wanderwise-mobile/backend/`)
```bash
cd wanderwise-mobile/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pytest tests/ -v
```

## Critical Infrastructure

- **OSRM** required on `localhost:5000` for routing distance/duration matrices
- **PostgreSQL + PostGIS** required for mobile backend (SQLAlchemy models, GEOGRAPHY columns)
- **Groq API** (llama-3.3-70b-versatile) for LLM features — set `GROQ_API_KEY` in `backend/.env`
- **Modal** for remote compute (see `get_started.py`)

## Conventions

### Python
- Type hints required on all function signatures
- Google-style docstrings for public functions
- Import order: stdlib → third-party → local app modules
- Always use SQLAlchemy ORM (no raw SQL); use Alembic for migrations
- Return Pydantic schema instances from API endpoints
- Use `logging`, never `print()`

### Spatial Data
- PostGIS GEOGRAPHY type only, SRID 4326
- Goa bounds: lat 14.8–15.9, lon 73.6–74.4
- Never compute distances ad-hoc — use pre-cached `distance_matrix` table
- Place IDs are UUIDs, not integers

### Frontend (Mobile)
- React function components only (Expo / React Native)
- State management: zustand with AsyncStorage persistence
- API client auto-resolves backend URL via Expo host discovery (`src/config/apiConfig.ts`)
- Mobile API hits backend on port 8000; URL fallback chain: Expo host → Android emulator `10.0.2.2` → localhost

### Frontend (Web)
- React 19 + Vite 6 + React Router 7
- No linting or typechecking configured

## Architecture (4 Modules)

1. **Module I — NLC:** DistilBERT interest classification from user text
2. **Module II — Popularity:** POI popularity scoring with K-Means clustering
3. **Module III — Clustering:** Spatial K-Means for day-wise POI grouping
4. **Module IV — GA Routing:** Genetic algorithm route optimization with LLM-powered fitness

Entry point for Module IV simulation: `backend/app/api/routes_simulation.py` → `backend/app/services/module4_service.py`

## Gotchas

- **No CI/CD, no lint, no typecheck, no pre-commit hooks** — verification is manual
- `frontend/` lint script is a placeholder (`echo 'No lint config yet'`)
- `backend/requirements.txt` is unpinned; `wanderwise-mobile/backend/requirements.txt` pins core deps
- Mobile backend has SQLAlchemy + psycopg2-binary (Postgres), primary backend does not
- `.env` files exist in both `backend/` and `frontend/` — never commit secrets
- `wanderwise-mobile/` has its own `.git/` — treat as a separate repo when committing
