"""Embedding service — Supabase pgvector backend.

Provides semantic search over pre-computed place description embeddings
stored in Supabase. Embeddings are generated via Modal (sentence-transformers)
and queried by cosine similarity using pgvector.

The _chunk_place() function is kept here for reuse by the pre-computation script.
"""

from __future__ import annotations

import logging
from typing import Any

from app.services.supabase_embedding_store import (
    search_embeddings,
    search_embeddings_by_category,
)
from app.services.modal_embedding_client import embed_query

logger = logging.getLogger(__name__)

_MAX_CHUNK_CHARS = 500


def _truncate(text: str, max_len: int = _MAX_CHUNK_CHARS) -> str:
    """Truncate text to max_len, appending ellipsis if needed."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rsplit(" ", 1)[0] + "..."


def _chunk_place(
    place_name: str, data: dict[str, Any]
) -> list[tuple[str, str, str]]:
    """Split a place description into semantic chunks.

    Args:
        place_name: Display name of the place.
        data: Full description JSON data.

    Returns:
        List of (chunk_text, chunk_id, chunk_type) tuples.
    """
    chunks: list[tuple[str, str, str]] = []
    safe_name = place_name.replace(" ", "_")[:40]

    desc = data.get("description", "")
    if desc:
        chunks.append(
            (
                f"{place_name}: {_truncate(desc, 400)}",
                f"{safe_name}_desc",
                "description",
            )
        )

    accordion = data.get("accordion_sections", [])
    if accordion:
        faq_parts = []
        for item in accordion[:3]:
            q = item.get("title", "")
            a = item.get("content", "")
            if q and a:
                faq_parts.append(f"Q: {q} A: {_truncate(a, 150)}")
        if faq_parts:
            chunks.append(
                (
                    f"{place_name} FAQ: " + " | ".join(faq_parts),
                    f"{safe_name}_faq",
                    "faq",
                )
            )

    guidelines = data.get("guidelines", [])
    timing = data.get("timing_info", "")
    fee = data.get("entry_fee", "")
    meta_parts = []
    if guidelines:
        meta_parts.append(
            "Guidelines: "
            + "; ".join(g.strip() for g in guidelines[:3] if g.strip())
        )
    if timing:
        meta_parts.append(f"Best time: {_truncate(timing, 80)}")
    if fee and fee not in ("", "Not specified", "None"):
        meta_parts.append(f"Entry fee: {_truncate(fee, 60)}")
    if meta_parts:
        chunks.append(
            (
                f"{place_name} info: " + " | ".join(meta_parts),
                f"{safe_name}_meta",
                "meta",
            )
        )

    return chunks


def search_places(
    question: str,
    place_filter: list[str] | None = None,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Search pre-computed embeddings for relevant place chunks.

    Args:
        question: User's question.
        place_filter: Optional place names to restrict search (e.g., cluster POIs).
        top_k: Number of results to return.

    Returns:
        List of dicts with place_name, text, chunk_type, score.
    """
    try:
        embedding = embed_query(question)
    except Exception as exc:
        logger.error("Modal embed_query failed: %s", exc)
        return []

    return search_embeddings(embedding, top_k=top_k, place_filter=place_filter)


def search_places_by_category(
    question: str,
    category: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Search within a specific category.

    Args:
        question: User's question.
        category: Category filter (e.g., "Beaches", "Forts").
        top_k: Number of results.

    Returns:
        List of dicts with place_name, text, chunk_type, score.
    """
    try:
        embedding = embed_query(question)
    except Exception as exc:
        logger.error("Modal embed_query failed: %s", exc)
        return []

    return search_embeddings_by_category(embedding, category=category, top_k=top_k)
