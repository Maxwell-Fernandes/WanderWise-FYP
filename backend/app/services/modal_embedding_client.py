"""Thin client for calling Modal-hosted embedding functions."""

from __future__ import annotations

import logging
from typing import Any

import modal

logger = logging.getLogger(__name__)

_APP_NAME = "wanderwise-embeddings"


def _get_function(func_name: str) -> Any:
    """Get a reference to a deployed Modal function."""
    return modal.Function.from_name(_APP_NAME, func_name)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Call Modal to embed a batch of texts.

    Args:
        texts: List of text strings to embed.

    Returns:
        List of embedding vectors (each a list of floats).
    """
    func = _get_function("embed_texts")
    return func.remote(texts)


def embed_query(query: str) -> list[float]:
    """Call Modal to embed a single query string.

    Args:
        query: The query text to embed.

    Returns:
        Embedding vector as a list of floats.
    """
    func = _get_function("embed_query")
    return func.remote(query)
