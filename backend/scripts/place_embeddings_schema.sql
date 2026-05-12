-- place_embeddings schema for pgvector semantic search
-- Run this on Supabase SQL editor or via: supabase db query -f backend/scripts/place_embeddings_schema.sql

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS place_embeddings (
  id BIGSERIAL PRIMARY KEY,
  place_name TEXT NOT NULL,
  category TEXT,
  chunk_type TEXT,
  chunk_text TEXT NOT NULL,
  embedding vector(384),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Cosine similarity index (ivfflat)
CREATE INDEX IF NOT EXISTS place_embeddings_embedding_idx
  ON place_embeddings
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 10);

-- Index for filtering by place name
CREATE INDEX IF NOT EXISTS place_embeddings_place_name_idx
  ON place_embeddings (place_name);

-- Index for filtering by category
CREATE INDEX IF NOT EXISTS place_embeddings_category_idx
  ON place_embeddings (category);
