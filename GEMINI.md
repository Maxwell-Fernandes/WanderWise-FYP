# WanderWise+ Project Overview

This document provides a comprehensive overview of the WanderWise+ project, an intelligent tourism route planning system for Goa, India.

## Project Overview

WanderWise+ is a Python-based web application that leverages a FastAPI backend, a PostgreSQL database with PostGIS for spatial data, and a React frontend (currently not implemented). The application is designed to help tourists plan their trips to Goa by providing optimized routes, smart recommendations, and detailed information about tourist destinations.

**Key Technologies:**

*   **Backend:** Python, FastAPI, SQLAlchemy, GeoAlchemy2, `python-tsp`
*   **Database:** PostgreSQL, PostGIS
*   **Frontend:** React (not yet implemented)
*   **Development Tools:** `pytest`, `black`, `isort`, `flake8`

## Building and Running

### Backend

1.  **Set up the environment:**
    *   Install Python 3.11+ and PostgreSQL 12+ with PostGIS 3.0+.
    *   Create a Python virtual environment.
    *   Install the required Python packages:
        ```bash
        pip install -r backend/requirements.txt
        ```

2.  **Set up the database:**
    *   Create a PostgreSQL database and user.
    *   Enable the PostGIS extension.
    *   Run the database setup script:
        ```bash
        psql -U <user> -d <database> -f database/database_setup.sql
        ```

3.  **Configure the application:**
    *   Copy the `.env.example` file to `.env` in the `backend` directory.
    *   Update the `.env` file with your database credentials.

4.  **Run the application:**
    *   Start the FastAPI server:
        ```bash
        uvicorn app.main:app --reload
        ```
    *   The API will be available at `http://localhost:8000/docs`.

### Frontend

The frontend is not yet implemented.

## Development Conventions

The project follows standard Python development conventions.

*   **Code Style:** The project uses `black` for code formatting and `isort` for import sorting.
*   **Linting:** `flake8` is used for linting.
*   **Testing:** `pytest` is used for testing.

To run the linter and code formatter:

```bash
black backend/app/
isort backend/app/
flake8 backend/app/
```

To run the tests:

```bash
pytest backend/tests/
```

## Database Schema

The database schema is defined in `database/database_setup.sql` and includes the following main tables:

*   **`goa_places`**: Stores all tourist destinations with spatial data.
    *   `id`: UUID, Primary Key
    *   `name`: VARCHAR, Name of the place
    *   `category`: VARCHAR, Category of the place (e.g., "Beach", "Temple")
    *   `location`: GEOGRAPHY(POINT, 4326), PostGIS point for spatial queries
    *   `latitude`, `longitude`: NUMERIC, Coordinates
    *   `description`: TEXT, Description of the place
    *   `entry_fee_inr`: NUMERIC, Entry fee in Indian Rupees
    *   `is_free`: BOOLEAN, True if the entry is free
    *   `opening_time`, `closing_time`: TIME, Opening and closing times
    *   `popularity_score`: NUMERIC, Popularity score from 0 to 10
    *   `facilities`: TEXT[], Array of available facilities

*   **`distance_matrix`**: Caches calculated distances between places for performance.
    *   `id`: UUID, Primary Key
    *   `place_id_from`, `place_id_to`: UUID, Foreign keys to `goa_places`
    *   `distance_meters`: NUMERIC, Distance in meters
    *   `distance_km`: NUMERIC, Distance in kilometers
    *   `estimated_time_minutes`: INTEGER, Estimated travel time in minutes

*   **`user_routes`**: Stores saved and optimized routes.
    *   `id`: UUID, Primary Key
    *   `route_name`: VARCHAR, Name of the route
    *   `place_ids`: UUID[], Ordered array of place IDs in the route
    *   `total_distance_km`: NUMERIC, Total distance of the route in kilometers
    *   `total_duration_minutes`: INTEGER, Total duration of the route in minutes
    *   `preferences`: JSONB, User preferences for the route
