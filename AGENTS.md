# AGENTS.md — WanderWise

Multi-app project for AI-assisted tourism routing in Goa, India. Not a monorepo — each directory is independent.

## Project Layout

```
backend/              # Primary FastAPI backend (notebook simulator, GA routing)
frontend/             # Web frontend (Vite + React, minimal)
wanderwise-mobile/    # Mobile app (separate git root)
  frontend/           # Expo SDK 54 / React Native 0.81 (TypeScript)
  backend/            # Production backend (SQLAlchemy + PostgreSQL)
goadataset.csv        # POI dataset (loaded at runtime, not in git)
goa.geojson           # Goa boundary polygon for spatial filtering
Description_data/     # Place description JSONs (loaded by description_context_service)
.agents/skills/       # Agent skill definitions (see Agent Skills section)
get_started.py        # Modal remote compute setup
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
- **Geoapify API** for geocoding/autocomplete (hotel search) — set `VITE_GEOAPIFY_API_KEY` (web) or `EXPO_PUBLIC_GEOAPIFY_API_KEY` (mobile) in respective `.env` files
- **Modal** for remote compute (see `get_started.py`)

## Conventions

### Python
- Type hints required on all function signatures
- Google-style docstrings for public functions
- Import order: stdlib → third-party → local app modules
- Always use SQLAlchemy ORM (no raw SQL); use Alembic for migrations (primary backend) or manual migration scripts (mobile backend)
- Return Pydantic schema instances from API endpoints
- Use `logging`, never `print()`

### Spatial Data
- PostGIS GEOGRAPHY type only, SRID 4326
- Goa bounds: lat 14.8–15.9, lon 73.6–74.4
- Never compute distances ad-hoc — use pre-cached `distance_matrix` table
- Place IDs are UUIDs, not integers

### Frontend (Mobile)
- React function components only (Expo SDK 54 / React Native 0.81, New Architecture enabled)
- **No Expo Router** — navigation is a custom state-machine in `App.tsx` (manual screen stack with `screenHistory` array)
- State management: zustand with AsyncStorage persistence (`sessionStore`, `onboardingStore`)
- API client auto-resolves backend URL via Expo host discovery (`src/config/apiConfig.ts`)
- Mobile API hits backend on port 8000; URL fallback chain: Expo host → Android emulator `10.0.2.2` → localhost

### Frontend (Web)
- React 19 + Vite 6 + React Router 7
- No linting or typechecking configured

## Agent Skills (`.agents/skills/`)

Load relevant skills when working on specific tasks. Use the `skill` tool to inject skill instructions into context. **Always load the relevant skill before starting a matching task.**

| Skill | When to use |
|---|---|
| `building-native-ui` | Building Expo Router screens, components, navigation, animations, styling |
| `expo-api-routes` | Creating API routes in Expo Router with EAS Hosting |
| `expo-tailwind-setup` | Setting up Tailwind CSS v4 / NativeWind v5 in Expo |
| `vercel-react-native-skills` | React Native performance optimization, list virtualization, Reanimated patterns |
| `frontend-design` | Building web components, pages, dashboards, or styling any web UI with high design quality |
| `web-design-guidelines` | Reviewing UI code for Web Interface Guidelines compliance, accessibility, UX audits |
| `grill-me` | Stress-testing a plan or design — interview the user to resolve decision branches |
| `find-skills` | Discovering and installing additional agent skills |
| `supabase` | Any Supabase task: DB, Auth, Edge Functions, RLS, migrations, CLI, client libraries |
| `supabase-postgres-best-practices` | Postgres performance optimization, schema design, and query tuning |
| `langchain-fundamentals` | Creating LangChain agents, defining tools, middleware for human-in-the-loop |
| `langgraph-docs` | Building stateful agents, multi-agent workflows, human-in-the-loop with LangGraph |
| `langgraph-human-in-the-loop` | Implementing interrupt/resume, approval workflows, error handling in LangGraph |
| `langgraph-persistence` | Persisting LangGraph state, checkpointers, time travel, thread management |

## Architecture (4 Modules)

1. **Module I — NLC:** DistilBERT interest classification from user text (keyword-based + optional Groq LLM enrichment)
2. **Module II — Popularity:** POI popularity scoring with Bayesian weighting + K-Means spatial clustering (also handles Module III clustering inline)
3. **Module IV — GA Routing:** Genetic algorithm route optimization with LLM-powered fitness — the core orchestrator (~2870 lines in `module4_service.py`) that chains M1→M2→M4 per day, runs itinerary QA via Groq, generates alternative itineraries, and produces Folium maps

Module IV entry point: `backend/app/api/routes_simulation.py` → `backend/app/services/module4_service.py`

### Key services
- `groq_client.py` — Shared Groq HTTP client (JSON mode, retry on 400)
- `preference_fitness_llm.py` — LLM-based fitness weight resolution per travel type
- `itinerary_qa_llm.py` — Post-optimization route sanity checking via Groq
- `itinerary_narration_service.py` — Day narration (Modal remote or fallback template)
- `description_context_service.py` — Fuzzy place description lookup from `Description_data/`
- `preference_service.py` — DB-backed preference merging (mobile backend only)
- `itinerary_persistence.py` — Save/read/delete itineraries (mobile backend only)

## Gotchas

- **No CI/CD, no lint, no typecheck, no pre-commit hooks** — verification is manual
- `frontend/` lint script is a placeholder (`echo 'No lint config yet'`)
- `backend/requirements.txt` is unpinned; `wanderwise-mobile/backend/requirements.txt` pins core deps
- Mobile backend has SQLAlchemy + psycopg2-binary (Postgres), primary backend does not
- `.env` files exist in both `backend/` and `frontend/` — never commit secrets (includes Geoapify API key)
- `wanderwise-mobile/` has its own `.git/` — treat as a separate repo when committing
- `wanderwise-mobile/frontend` does **not** use Expo Router — it's a custom state-machine, not file-based routing
- `Description_data/` and `goadataset.csv` are loaded at runtime from the project root — not bundled in either backend
- Mobile backend uses **manual migration scripts** (standalone `.py` files), not Alembic
- Module 4 request supports `mobile_only: bool` which strips the response to one alternative per day
