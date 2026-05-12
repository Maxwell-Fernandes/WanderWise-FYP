"""Supabase pgvector-backed embedding store for place descriptions."""

from __future__ import annotations

import logging
from typing import Any

import psycopg2

from app.config import SUPABASE_DB_URL

logger = logging.getLogger(__name__)


def _get_connection() -> psycopg2.extensions.connection:
    """Get a connection to the Supabase database."""
    if not SUPABASE_DB_URL:
        raise ValueError("SUPABASE_DB_URL is not set in config")
    return psycopg2.connect(SUPABASE_DB_URL)


def search_embeddings(
    query_embedding: list[float],
    top_k: int = 5,
    place_filter: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Search place_embeddings by cosine similarity.

    Args:
        query_embedding: 384-dim vector from embed_query.
        top_k: Number of results to return.
        place_filter: Optional list of place names to restrict search.

    Returns:
        List of dicts with place_name, text, chunk_type, score.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        emb_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

        if place_filter:
            # Use ANY for array matching
            sql = """
                SELECT place_name, chunk_text, chunk_type,
                       1 - (embedding <=> %s::vector) AS score
                FROM place_embeddings
                WHERE place_name = ANY(%s)
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """
            params = [emb_str, place_filter, emb_str, top_k]
        else:
            sql = """
                SELECT place_name, chunk_text, chunk_type,
                       1 - (embedding <=> %s::vector) AS score
                FROM place_embeddings
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """
            params = [emb_str, emb_str, top_k]

        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close()

        return [
            {
                "place_name": r[0],
                "text": r[1],
                "chunk_type": r[2],
                "score": round(float(r[3]), 4),
            }
            for r in rows
        ]
    finally:
        conn.close()


def search_embeddings_by_category(
    query_embedding: list[float],
    category: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Search within a specific category.

    Args:
        query_embedding: 384-dim vector.
        category: Category to filter by (e.g., "Beaches", "Forts").
        top_k: Number of results.

    Returns:
        List of dicts with place_name, text, chunk_type, score.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        emb_str = "[" + ",".join(str(x) for x in query_embedding) + "]"

        sql = """
            SELECT place_name, chunk_text, chunk_type,
                   1 - (embedding <=> %s::vector) AS score
            FROM place_embeddings
            WHERE category = %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """
        cur.execute(sql, [emb_str, category, emb_str, top_k])
        rows = cur.fetchall()
        cur.close()

        return [
            {
                "place_name": r[0],
                "text": r[1],
                "chunk_type": r[2],
                "score": round(float(r[3]), 4),
            }
            for r in rows
        ]
    finally:
        conn.close()


def get_embedding_count() -> int:
    """Get total number of embeddings in the table."""
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM place_embeddings")
        count = cur.fetchone()[0]
        cur.close()
        return count
    finally:
        conn.close()


def get_categories() -> list[str]:
    """Get distinct categories in the embeddings table."""
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT DISTINCT category FROM place_embeddings ORDER BY category"
        )
        rows = cur.fetchall()
        cur.close()
        return [r[0] for r in rows if r[0]]
    finally:
        conn.close()


def get_existing_place_names() -> list[str]:
    """Get all place_name values currently in the embeddings table."""
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT place_name FROM place_embeddings")
        names = [r[0] for r in cur.fetchall()]
        cur.close()
        return names
    finally:
        conn.close()


def upsert_place_embeddings(
    place_name: str,
    category: str,
    chunks: list[tuple[str, str]],
    embeddings: list[list[float]],
) -> int:
    """Insert or replace all embeddings for a single place.

    Deletes existing embeddings for this place_name, then inserts the new ones.

    Args:
        place_name: Display name of the place.
        category: Category (e.g., "beaches", "Forts").
        chunks: List of (chunk_text, chunk_type) tuples.
        embeddings: Matching list of 384-dim embedding vectors.

    Returns:
        Number of chunks inserted.
    """
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM place_embeddings WHERE place_name = %s", (place_name,)
        )

        insert_sql = (
            "INSERT INTO place_embeddings "
            "(place_name, category, chunk_type, chunk_text, embedding) "
            "VALUES (%s, %s, %s, %s, %s)"
        )
        for (text, ctype), emb in zip(chunks, embeddings):
            emb_str = "[" + ",".join(str(x) for x in emb) + "]"
            cur.execute(insert_sql, (place_name, category, ctype, text, emb_str))

        count = len(chunks)
        conn.commit()
        cur.close()
        return count
    finally:
        conn.close()


def delete_place_embeddings(place_name: str) -> int:
    """Delete all embeddings for a place. Returns count deleted."""
    conn = _get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM place_embeddings WHERE place_name = %s", (place_name,)
        )
        deleted = cur.rowcount
        conn.commit()
        cur.close()
        return deleted
    finally:
        conn.close()
