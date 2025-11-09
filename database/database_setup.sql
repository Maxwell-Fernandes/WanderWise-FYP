-- WanderWise+ Database Setup Script
-- PostgreSQL 12+ with PostGIS 3.0+
-- Purpose: Set up spatial database for Goa tourism route planning

-- ============================================================================
-- EXTENSIONS
-- ============================================================================

-- Enable PostGIS for spatial operations
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable text search capabilities
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ============================================================================
-- CUSTOM TYPES
-- ============================================================================

-- Difficulty levels for destinations
CREATE TYPE difficulty_level AS ENUM ('Easy', 'Moderate', 'Hard');

-- Research/verification status
CREATE TYPE research_status AS ENUM ('PENDING', 'IN_PROGRESS', 'COMPLETE', 'NEEDS_UPDATE');

-- ============================================================================
-- MAIN TABLES
-- ============================================================================

-- Table: goa_places
-- Stores all tourist destinations in Goa with spatial data
CREATE TABLE goa_places (
    -- Primary identification
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,

    -- Categorization
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),

    -- Spatial data (using GEOGRAPHY for accurate real-world distances)
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    latitude NUMERIC(10, 7) NOT NULL,
    longitude NUMERIC(10, 7) NOT NULL,

    -- Descriptive information
    description TEXT,

    -- Visitor information
    entry_fee_inr NUMERIC(10, 2) DEFAULT 0,
    is_free BOOLEAN DEFAULT true,
    opening_time TIME,
    closing_time TIME,
    best_visit_time VARCHAR(255),
    duration_minutes INTEGER,

    -- Ratings and difficulty
    popularity_score NUMERIC(3, 1) CHECK (popularity_score >= 0 AND popularity_score <= 10),
    difficulty_level difficulty_level DEFAULT 'Easy',

    -- Facilities and amenities (stored as array for easy querying)
    facilities TEXT[],
    facilities_raw TEXT, -- Original pipe-delimited string

    -- Social media and discoverability
    instagram_tags TEXT[],
    instagram_tags_raw TEXT,
    photo_spots INTEGER DEFAULT 0,

    -- Contact and location details
    address TEXT,
    taluka VARCHAR(100),
    contact_number VARCHAR(50),
    website VARCHAR(500),

    -- Accessibility and amenities
    parking_available BOOLEAN DEFAULT false,
    wheelchair_accessible VARCHAR(20), -- 'Yes', 'No', 'Partial'
    food_available BOOLEAN DEFAULT false,

    -- Target audience (stored as array)
    best_for TEXT[],
    best_for_raw TEXT,

    -- Travel tips
    avoid_when TEXT,
    tips TEXT,

    -- Metadata
    last_verified_date DATE,
    research_status research_status DEFAULT 'COMPLETE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT valid_coordinates CHECK (
        latitude BETWEEN 14.8 AND 15.9 AND
        longitude BETWEEN 73.6 AND 74.4
    ),
    CONSTRAINT valid_duration CHECK (duration_minutes > 0),
    CONSTRAINT valid_fee CHECK (entry_fee_inr >= 0),
    CONSTRAINT free_fee_consistency CHECK (
        (is_free = true AND entry_fee_inr = 0) OR
        (is_free = false AND entry_fee_inr > 0) OR
        (is_free = true AND entry_fee_inr > 0) -- Some places are free but accept donations
    )
);

-- Add comment to table
COMMENT ON TABLE goa_places IS 'Master table storing all tourist destinations in Goa with spatial and descriptive data';
COMMENT ON COLUMN goa_places.location IS 'PostGIS GEOGRAPHY point for accurate distance calculations (WGS84)';
COMMENT ON COLUMN goa_places.facilities IS 'Array of facilities available at the location';
COMMENT ON COLUMN goa_places.popularity_score IS 'Popularity rating from 0-10 based on visitor data';


-- Table: distance_matrix
-- Caches calculated distances between places for performance
CREATE TABLE distance_matrix (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    place_id_from UUID NOT NULL REFERENCES goa_places(id) ON DELETE CASCADE,
    place_id_to UUID NOT NULL REFERENCES goa_places(id) ON DELETE CASCADE,

    -- Distance metrics
    distance_meters NUMERIC(10, 2) NOT NULL,
    distance_km NUMERIC(10, 2) GENERATED ALWAYS AS (distance_meters / 1000) STORED,

    -- Estimated travel time (in minutes, assuming average travel speed)
    estimated_time_minutes INTEGER,

    -- Route information (optional, for future integration with routing APIs)
    route_geometry GEOGRAPHY(LINESTRING, 4326),

    -- Metadata
    calculated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    calculation_method VARCHAR(50) DEFAULT 'haversine', -- 'haversine', 'osrm', 'google_maps', etc.

    -- Constraints
    CONSTRAINT different_places CHECK (place_id_from != place_id_to),
    CONSTRAINT valid_distance CHECK (distance_meters > 0),
    CONSTRAINT unique_place_pair UNIQUE (place_id_from, place_id_to)
);

COMMENT ON TABLE distance_matrix IS 'Cached distances between places for route optimization performance';
COMMENT ON COLUMN distance_matrix.estimated_time_minutes IS 'Estimated travel time assuming 40 km/h average speed in Goa';


-- Table: user_routes (optional - for saving and sharing routes)
CREATE TABLE user_routes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    route_name VARCHAR(255),

    -- Ordered list of place IDs in the route
    place_ids UUID[] NOT NULL,

    -- Route metadata
    total_distance_km NUMERIC(10, 2),
    total_duration_minutes INTEGER,
    estimated_cost_inr NUMERIC(10, 2),

    -- Route preferences
    preferences JSONB, -- Store user preferences like "prefer beaches", "avoid crowds", etc.

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT at_least_two_places CHECK (array_length(place_ids, 1) >= 2)
);

COMMENT ON TABLE user_routes IS 'Saved and optimized routes created by users or the system';


-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Spatial indexes (GIST for GEOGRAPHY types)
CREATE INDEX idx_goa_places_location
    ON goa_places USING GIST(location);

CREATE INDEX idx_distance_matrix_route_geometry
    ON distance_matrix USING GIST(route_geometry);

-- Category and filtering indexes
CREATE INDEX idx_goa_places_category
    ON goa_places(category);

CREATE INDEX idx_goa_places_subcategory
    ON goa_places(subcategory);

CREATE INDEX idx_goa_places_popularity
    ON goa_places(popularity_score DESC);

CREATE INDEX idx_goa_places_is_free
    ON goa_places(is_free);

CREATE INDEX idx_goa_places_difficulty
    ON goa_places(difficulty_level);

-- Array indexes for facilities and tags (GIN indexes for array containment)
CREATE INDEX idx_goa_places_facilities
    ON goa_places USING GIN(facilities);

CREATE INDEX idx_goa_places_instagram_tags
    ON goa_places USING GIN(instagram_tags);

CREATE INDEX idx_goa_places_best_for
    ON goa_places USING GIN(best_for);

-- Text search indexes
CREATE INDEX idx_goa_places_name_trgm
    ON goa_places USING GIN(name gin_trgm_ops);

CREATE INDEX idx_goa_places_description_trgm
    ON goa_places USING GIN(description gin_trgm_ops);

-- Distance matrix indexes
CREATE INDEX idx_distance_matrix_from
    ON distance_matrix(place_id_from);

CREATE INDEX idx_distance_matrix_to
    ON distance_matrix(place_id_to);

CREATE INDEX idx_distance_matrix_distance
    ON distance_matrix(distance_km);

-- Composite index for route optimization queries
CREATE INDEX idx_distance_matrix_pair_distance
    ON distance_matrix(place_id_from, place_id_to, distance_km);

-- User routes indexes
CREATE INDEX idx_user_routes_place_ids
    ON user_routes USING GIN(place_ids);

CREATE INDEX idx_user_routes_created
    ON user_routes(created_at DESC);


-- ============================================================================
-- MATERIALIZED VIEWS
-- ============================================================================

-- Popular places view for quick recommendations
CREATE MATERIALIZED VIEW popular_places AS
SELECT
    id,
    name,
    category,
    subcategory,
    location,
    latitude,
    longitude,
    popularity_score,
    duration_minutes,
    is_free,
    entry_fee_inr,
    facilities,
    best_for,
    photo_spots
FROM goa_places
WHERE popularity_score >= 7.0
ORDER BY popularity_score DESC, photo_spots DESC;

CREATE INDEX idx_popular_places_location
    ON popular_places USING GIST(location);

COMMENT ON MATERIALIZED VIEW popular_places IS 'Quick access to high-rated destinations for recommendations';


-- Beach-specific view
CREATE MATERIALIZED VIEW goa_beaches AS
SELECT
    id,
    name,
    subcategory,
    location,
    latitude,
    longitude,
    popularity_score,
    is_free,
    facilities,
    best_for,
    photo_spots,
    tips
FROM goa_places
WHERE category = 'Beach'
ORDER BY popularity_score DESC;

CREATE INDEX idx_goa_beaches_location
    ON goa_beaches USING GIST(location);

COMMENT ON MATERIALIZED VIEW goa_beaches IS 'Quick access to all beach destinations';


-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate distance between two places (returns meters)
CREATE OR REPLACE FUNCTION calculate_distance(
    place_id_1 UUID,
    place_id_2 UUID
)
RETURNS NUMERIC AS $$
DECLARE
    distance_val NUMERIC;
BEGIN
    SELECT ST_Distance(
        (SELECT location FROM goa_places WHERE id = place_id_1),
        (SELECT location FROM goa_places WHERE id = place_id_2)
    ) INTO distance_val;

    RETURN distance_val;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION calculate_distance IS 'Calculate distance in meters between two places using PostGIS';


-- Function to find nearby places within a radius
CREATE OR REPLACE FUNCTION find_nearby_places(
    center_lat NUMERIC,
    center_lon NUMERIC,
    radius_km NUMERIC DEFAULT 10
)
RETURNS TABLE(
    id UUID,
    name VARCHAR,
    category VARCHAR,
    distance_km NUMERIC,
    popularity_score NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.id,
        p.name,
        p.category,
        ROUND((ST_Distance(
            p.location,
            ST_SetSRID(ST_MakePoint(center_lon, center_lat), 4326)::geography
        ) / 1000)::numeric, 2) AS distance_km,
        p.popularity_score
    FROM goa_places p
    WHERE ST_DWithin(
        p.location,
        ST_SetSRID(ST_MakePoint(center_lon, center_lat), 4326)::geography,
        radius_km * 1000
    )
    ORDER BY distance_km ASC, p.popularity_score DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION find_nearby_places IS 'Find all places within specified radius of given coordinates';


-- Function to populate distance matrix for a specific place
CREATE OR REPLACE FUNCTION populate_distance_matrix_for_place(p_place_id UUID)
RETURNS INTEGER AS $$
DECLARE
    rows_inserted INTEGER := 0;
BEGIN
    INSERT INTO distance_matrix (place_id_from, place_id_to, distance_meters, estimated_time_minutes)
    SELECT
        p_place_id,
        p2.id,
        ST_Distance(p1.location, p2.location),
        CEIL((ST_Distance(p1.location, p2.location) / 1000) / 40 * 60)::INTEGER -- Assuming 40 km/h avg speed
    FROM goa_places p1
    CROSS JOIN goa_places p2
    WHERE p1.id = p_place_id
        AND p2.id != p_place_id
        AND NOT EXISTS (
            SELECT 1 FROM distance_matrix
            WHERE place_id_from = p_place_id AND place_id_to = p2.id
        );

    GET DIAGNOSTICS rows_inserted = ROW_COUNT;
    RETURN rows_inserted;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION populate_distance_matrix_for_place IS 'Populate distance matrix for all connections from a specific place';


-- Function to populate entire distance matrix
CREATE OR REPLACE FUNCTION populate_full_distance_matrix()
RETURNS INTEGER AS $$
DECLARE
    total_rows INTEGER := 0;
    place_record RECORD;
BEGIN
    FOR place_record IN SELECT id FROM goa_places
    LOOP
        total_rows := total_rows + populate_distance_matrix_for_place(place_record.id);
    END LOOP;

    RETURN total_rows;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION populate_full_distance_matrix IS 'Populate distance matrix for all place pairs (can be slow for large datasets)';


-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger to update updated_at on goa_places
CREATE TRIGGER update_goa_places_updated_at
    BEFORE UPDATE ON goa_places
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger to update updated_at on user_routes
CREATE TRIGGER update_user_routes_updated_at
    BEFORE UPDATE ON user_routes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger to sync location with lat/lon
CREATE OR REPLACE FUNCTION sync_location_with_coordinates()
RETURNS TRIGGER AS $$
BEGIN
    -- Update GEOGRAPHY point when lat/lon changes
    IF NEW.latitude IS NOT NULL AND NEW.longitude IS NOT NULL THEN
        NEW.location := ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326)::geography;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sync_goa_places_location
    BEFORE INSERT OR UPDATE OF latitude, longitude ON goa_places
    FOR EACH ROW
    EXECUTE FUNCTION sync_location_with_coordinates();


-- ============================================================================
-- HELPER VIEWS
-- ============================================================================

-- View: places_with_distance_stats
-- Shows each place with statistics about its distances to other places
CREATE VIEW places_with_distance_stats AS
SELECT
    p.id,
    p.name,
    p.category,
    p.popularity_score,
    COUNT(dm.id) AS cached_distances_count,
    ROUND(AVG(dm.distance_km)::numeric, 2) AS avg_distance_to_others_km,
    ROUND(MIN(dm.distance_km)::numeric, 2) AS min_distance_to_another_km,
    ROUND(MAX(dm.distance_km)::numeric, 2) AS max_distance_to_another_km
FROM goa_places p
LEFT JOIN distance_matrix dm ON p.id = dm.place_id_from
GROUP BY p.id, p.name, p.category, p.popularity_score
ORDER BY p.popularity_score DESC;


-- ============================================================================
-- DATA VALIDATION
-- ============================================================================

-- View to check data quality issues
CREATE VIEW data_quality_check AS
SELECT
    'Missing Description' AS issue_type,
    COUNT(*) AS count
FROM goa_places
WHERE description IS NULL OR description = ''
UNION ALL
SELECT
    'Missing Opening Hours',
    COUNT(*)
FROM goa_places
WHERE opening_time IS NULL OR closing_time IS NULL
UNION ALL
SELECT
    'Old Verification Date',
    COUNT(*)
FROM goa_places
WHERE last_verified_date < CURRENT_DATE - INTERVAL '6 months'
UNION ALL
SELECT
    'Missing Contact Info',
    COUNT(*)
FROM goa_places
WHERE (contact_number IS NULL OR contact_number = 'NA')
    AND (website IS NULL OR website = 'NA');


-- ============================================================================
-- REFRESH COMMANDS FOR MATERIALIZED VIEWS
-- ============================================================================

-- Run these periodically or after bulk updates
-- REFRESH MATERIALIZED VIEW CONCURRENTLY popular_places;
-- REFRESH MATERIALIZED VIEW CONCURRENTLY goa_beaches;


-- ============================================================================
-- SAMPLE QUERIES (for reference)
-- ============================================================================

/*
-- Find all beaches within 10km of a point
SELECT * FROM find_nearby_places(15.5444, 73.7551, 10) WHERE category = 'Beach';

-- Get top 10 most popular free places
SELECT name, category, popularity_score
FROM goa_places
WHERE is_free = true
ORDER BY popularity_score DESC
LIMIT 10;

-- Find places with specific facilities
SELECT name, category, facilities
FROM goa_places
WHERE facilities @> ARRAY['Parking', 'Toilets'];

-- Calculate distance between two specific places
SELECT calculate_distance(
    (SELECT id FROM goa_places WHERE name = 'Calangute Beach'),
    (SELECT id FROM goa_places WHERE name = 'Baga Beach')
) / 1000 AS distance_km;

-- Get distance matrix for route optimization
SELECT
    p1.name AS from_place,
    p2.name AS to_place,
    dm.distance_km,
    dm.estimated_time_minutes
FROM distance_matrix dm
JOIN goa_places p1 ON dm.place_id_from = p1.id
JOIN goa_places p2 ON dm.place_id_to = p2.id
WHERE p1.category = 'Beach'
ORDER BY dm.distance_km;
*/


-- ============================================================================
-- COMPLETION MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'WanderWise+ Database Setup Complete!';
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'Created:';
    RAISE NOTICE '  - Tables: goa_places, distance_matrix, user_routes';
    RAISE NOTICE '  - Indexes: Spatial (GIST), Text search (GIN), Performance (B-tree)';
    RAISE NOTICE '  - Views: popular_places, goa_beaches, data_quality_check';
    RAISE NOTICE '  - Functions: distance calculation, nearby search, matrix population';
    RAISE NOTICE '  - Triggers: Auto-update timestamps, sync coordinates';
    RAISE NOTICE '';
    RAISE NOTICE 'Next Steps:';
    RAISE NOTICE '  1. Import CSV data using: python backend/scripts/import_csv_data.py';
    RAISE NOTICE '  2. Populate distance matrix: SELECT populate_full_distance_matrix();';
    RAISE NOTICE '  3. Refresh materialized views: REFRESH MATERIALIZED VIEW popular_places;';
    RAISE NOTICE '=================================================================';
END $$;
