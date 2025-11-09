# WanderWise+ 🗺️

> An intelligent Goa tourism route planning system powered by spatial databases and optimization algorithms.

WanderWise+ is a comprehensive tourism route planning application designed specifically for Goa, India. It leverages PostGIS spatial databases, FastAPI backend, and advanced route optimization algorithms to help tourists discover and plan their perfect Goa itinerary.

## 🎯 Project Overview

**Project Type:** Final Year Project
**Tech Stack:** Python FastAPI + PostgreSQL + PostGIS + React
**Domain:** Tourism, Geospatial Systems, Route Optimization

### Key Features

- 📍 **Spatial Search**: Find tourist destinations within a specified radius
- 🗺️ **Route Optimization**: Generate optimal routes using TSP algorithms
- 🏖️ **Smart Recommendations**: Personalized suggestions based on preferences
- 📊 **Distance Matrix Caching**: Fast distance calculations between destinations
- 🎫 **Cost Estimation**: Calculate trip costs including entry fees
- ♿ **Accessibility Filters**: Filter by wheelchair accessibility and difficulty
- 🕒 **Time Planning**: Optimal visiting times and duration estimates

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Frontend  │ ←───→   │    FastAPI   │ ←───→   │ PostgreSQL  │
│   (React)   │  REST   │   Backend    │  SQL    │  + PostGIS  │
└─────────────┘         └──────────────┘         └─────────────┘
                              │
                              ↓
                        ┌──────────────┐
                        │  Route       │
                        │  Optimizer   │
                        └──────────────┘
```

### Technology Stack

**Backend:**
- FastAPI 0.109+ - Modern, fast web framework
- SQLAlchemy 2.0+ - ORM with spatial support
- GeoAlchemy2 - PostGIS integration
- Pydantic - Data validation
- Python-TSP - Route optimization
- OR-Tools - Advanced optimization

**Database:**
- PostgreSQL 12+ - Relational database
- PostGIS 3.0+ - Spatial extensions
- Geographic data types for accurate distance calculations
- Spatial indexes (GIST) for performance

**Spatial Libraries:**
- Shapely - Geometric operations
- GeoPy - Geocoding and distance calculations
- PyProj - Coordinate transformations

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **PostgreSQL 12+** - [Download](https://www.postgresql.org/download/)
- **PostGIS 3.0+** - [Installation Guide](https://postgis.net/install/)
- **pip** - Python package manager
- **Git** - Version control

### System Requirements

- OS: Linux, macOS, or Windows with WSL2
- RAM: 4GB minimum, 8GB recommended
- Storage: 2GB free space

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd WanderWise
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL Database

#### Create Database and User

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# In PostgreSQL shell:
CREATE DATABASE wanderwise_db;
CREATE USER wanderwise_user WITH ENCRYPTED PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE wanderwise_db TO wanderwise_user;

# Enable PostGIS extension
\c wanderwise_db
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;

# Exit PostgreSQL shell
\q
```

#### Run Database Setup Script

```bash
# From the project root
psql -U wanderwise_user -d wanderwise_db -f database/database_setup.sql
```

### 5. Configure Environment Variables

```bash
# Copy example environment file
cp backend/.env.example backend/.env

# Edit .env file with your database credentials
nano backend/.env  # or use your preferred editor
```

Update the following in `.env`:
```
DB_HOST="localhost"
DB_PORT=5432
DB_NAME="wanderwise_db"
DB_USER="wanderwise_user"
DB_PASSWORD="your_secure_password"
```

### 6. Import Tourism Data

```bash
# Create the import script first (see next section)
cd backend
python scripts/import_csv_data.py
```

### 7. Populate Distance Matrix (Optional but Recommended)

```bash
# Connect to database
psql -U wanderwise_user -d wanderwise_db

# Run the population function (may take a few minutes)
SELECT populate_full_distance_matrix();

# Refresh materialized views
REFRESH MATERIALIZED VIEW popular_places;
REFRESH MATERIALIZED VIEW goa_beaches;

# Exit
\q
```

### 8. Start the Backend Server

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

## 📁 Project Structure

```
WanderWise/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── config.py               # Configuration management
│   │   ├── database.py             # Database connection and session
│   │   ├── models/                 # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   └── places.py           # Place model with PostGIS
│   │   ├── schemas/                # Pydantic schemas for validation
│   │   │   ├── __init__.py
│   │   │   └── places.py           # Place schemas
│   │   ├── api/                    # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── places.py           # Place endpoints
│   │   │   └── routes.py           # Route planning endpoints
│   │   ├── services/               # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── route_planner.py    # Route optimization logic
│   │   │   └── distance_calculator.py
│   │   └── utils/                  # Utility functions
│   │       ├── __init__.py
│   │       └── spatial.py          # Spatial calculations
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_places.py
│   ├── scripts/
│   │   ├── import_csv_data.py      # Import CSV to database
│   │   └── seed_database.py        # Seed with sample data
│   ├── requirements.txt
│   └── .env.example
├── database/
│   ├── database_setup.sql          # Complete DB schema
│   ├── migrations/                 # Alembic migrations (future)
│   └── seeds/                      # Seed data files
├── docs/
│   ├── api.md                      # API documentation
│   ├── architecture.md             # System architecture
│   └── database.md                 # Database schema docs
├── tests/
│   └── integration/                # Integration tests
├── Wanderwise_datasetnew.csv       # Source data (100 places)
├── CLAUDE.md                       # Claude Code guidance
├── .gitignore
└── README.md
```

## 🔧 Development

### Running Tests

```bash
cd backend
pytest tests/ -v
```

### Code Formatting

```bash
# Format code with Black
black backend/app/

# Sort imports
isort backend/app/

# Lint with flake8
flake8 backend/app/
```

### Database Migrations (with Alembic)

```bash
# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 📊 Database Schema

### Main Tables

#### `goa_places`
Stores all tourist destinations with spatial data.

**Key Columns:**
- `id` (UUID) - Primary key
- `name` (VARCHAR) - Place name
- `category` (VARCHAR) - Beach, Temple, Fort, etc.
- `location` (GEOGRAPHY) - PostGIS point for spatial queries
- `latitude`, `longitude` (NUMERIC) - Coordinates
- `popularity_score` (NUMERIC) - Rating 0-10
- `facilities` (TEXT[]) - Array of available facilities
- `entry_fee_inr` (NUMERIC) - Entry fee
- `duration_minutes` (INTEGER) - Suggested visit duration

#### `distance_matrix`
Caches calculated distances between places.

**Key Columns:**
- `place_id_from`, `place_id_to` (UUID) - Foreign keys
- `distance_meters` (NUMERIC) - Distance in meters
- `distance_km` (NUMERIC) - Distance in kilometers
- `estimated_time_minutes` (INTEGER) - Travel time estimate

#### `user_routes`
Stores saved and optimized routes.

**Key Columns:**
- `id` (UUID) - Primary key
- `route_name` (VARCHAR) - Route name
- `place_ids` (UUID[]) - Ordered array of place IDs
- `total_distance_km` (NUMERIC) - Total route distance
- `preferences` (JSONB) - User preferences

### Spatial Indexes

- GIST index on `goa_places.location` for spatial queries
- GIN indexes on array fields for fast containment queries
- B-tree indexes on frequently filtered columns

## 🛠️ API Endpoints (Planned)

### Places

- `GET /api/places` - List all places with filters
- `GET /api/places/{id}` - Get place details
- `GET /api/places/nearby` - Find nearby places
- `GET /api/places/search` - Full-text search

### Routes

- `POST /api/routes/optimize` - Generate optimized route
- `GET /api/routes/{id}` - Get saved route
- `POST /api/routes/save` - Save a route

### Recommendations

- `GET /api/recommendations` - Get personalized recommendations
- `POST /api/recommendations/preferences` - Update preferences

## 🔍 Key Algorithms

### Route Optimization

The system uses multiple algorithms for route planning:

1. **Nearest Neighbor** - Fast heuristic for initial solution
2. **2-opt Improvement** - Local search optimization
3. **Simulated Annealing** - Escape local optima
4. **OR-Tools** - Google's optimization library for complex constraints

### Distance Calculation

- **Haversine Formula** - Great-circle distance
- **PostGIS ST_Distance** - Accurate geodesic distance
- **OSRM/Google Maps** - Actual road distances (future)

## 📝 Data Source

The project uses a curated dataset of 100+ Goa tourist destinations including:

- 25+ Beaches (North Goa, South Goa, City beaches)
- Temples and Churches
- Forts and Historical sites
- Waterfalls and Natural attractions
- Markets and Shopping areas

**Data Fields:** Name, Category, Coordinates, Description, Entry Fee, Facilities, Opening Hours, Best Visit Time, Tips, and more.

## 🤝 Contributing

This is a final year project, but suggestions and feedback are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is developed as an academic final year project.

## 👨‍💻 Author

**Your Name**
Final Year Project - [University Name]

## 🙏 Acknowledgments

- PostGIS for spatial database capabilities
- FastAPI for the excellent web framework
- OpenStreetMap for geographic data
- Goa Tourism for destination information

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Contact: your.email@example.com

---

**Note:** This is an active development project for academic purposes. Some features may be in progress.
