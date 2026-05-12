"""Chat service for WanderWise — grounded Q&A about Goa places."""

from __future__ import annotations

import logging
from typing import Any

from app.services.description_context_service import get_descriptions_for_route
from app.services.groq_client import groq_chat_text

logger = logging.getLogger(__name__)

_MAX_CONTEXT_CHARS = 800
_MAX_HISTORY_TURNS = 10

_SYSTEM_PROMPT = (
    "You are WanderWise, a helpful Goa tourism assistant. "
    "Answer questions about places in Goa using the place data provided below. "
    "Be concise, practical, and engaging. If the user asks about a place not in the data, "
    "say you don't have detailed info for that place but offer general Goa travel advice. "
    "Keep responses under 200 words unless the user asks for detail."
)


def _truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rsplit(" ", 1)[0] + "..."


def _format_place_context(data: dict[str, Any]) -> str:
    parts: list[str] = []
    name = data.get("name", "Unknown")
    category = data.get("category", "")
    header = f"{name} ({category})" if category else name
    parts.append(header)

    desc = data.get("description", "")
    if desc:
        parts.append(f"Description: {_truncate(desc, 350)}")

    accordion = data.get("accordion_sections", [])
    if accordion:
        faq_lines = []
        for item in accordion[:4]:
            q = item.get("title", "")
            a = item.get("content", "")
            if q and a:
                faq_lines.append(f"  Q: {q}\n  A: {_truncate(a, 150)}")
        if faq_lines:
            parts.append("FAQ:\n" + "\n".join(faq_lines))

    guidelines = data.get("guidelines", [])
    if guidelines:
        parts.append(
            "Guidelines: " + "; ".join(g.strip() for g in guidelines[:4] if g.strip())
        )

    timing = data.get("timing_info", "")
    if timing:
        parts.append(f"Best time: {_truncate(timing, 100)}")

    fee = data.get("entry_fee", "")
    if fee and fee not in ("", "Not specified", "None"):
        parts.append(f"Entry fee: {_truncate(fee, 80)}")

    return _truncate("\n".join(parts), _MAX_CONTEXT_CHARS)


def _build_context_block(descriptions: dict[str, dict[str, Any]]) -> str:
    matched = {k: v for k, v in descriptions.items() if v and v.get("matched")}
    if not matched:
        return ""
    lines = ["\n--- Place Data ---"]
    for _name, data in matched.items():
        lines.append(_format_place_context(data))
        lines.append("")
    lines.append("--- End Place Data ---")
    return "\n".join(lines)


def _format_retrieved_chunks(chunks: list[dict[str, Any]]) -> str:
    if not chunks:
        return ""
    lines = ["\n--- Retrieved Place Context ---"]
    for chunk in chunks:
        lines.append(f"[{chunk.get('place_name', '?')}] {chunk.get('text', '')}")
    lines.append("--- End Retrieved Context ---")
    return "\n".join(lines)


def _build_messages(
    user_message: str,
    history: list[dict[str, str]],
    context_block: str,
) -> tuple[str, str]:
    system_parts = [_SYSTEM_PROMPT]
    if context_block:
        system_parts.append(context_block)
    system_prompt = "\n".join(system_parts)

    recent_history = history[-_MAX_HISTORY_TURNS * 2:]
    history_lines: list[str] = []
    for msg in recent_history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            history_lines.append(f"User: {content}")
        elif role == "assistant":
            history_lines.append(f"Assistant: {content}")
    history_lines.append(f"User: {user_message}")
    combined_user_message = "\n".join(history_lines)

    return system_prompt, combined_user_message


def _chat_direct(
    user_message: str,
    history: list[dict[str, str]],
    place_names: list[str],
) -> dict[str, Any]:
    """Mode A: Direct context injection for route places."""
    descriptions: dict[str, dict[str, Any]] = {}
    grounded_places: list[str] = []

    if place_names:
        descriptions = get_descriptions_for_route(place_names)
        grounded_places = [
            n for n, d in descriptions.items() if d and d.get("matched")
        ]

    context_block = _build_context_block(descriptions)
    system_prompt, combined_message = _build_messages(
        user_message, history, context_block
    )

    try:
        reply = groq_chat_text(
            system_prompt, combined_message, timeout=60, max_tokens=500
        )
    except Exception as exc:
        logger.error("Chat Groq call failed: %s", exc)
        reply = "Sorry, I'm having trouble connecting to the AI service right now."

    return {"reply": reply.strip(), "grounded_places": grounded_places}


def _chat_with_embeddings(
    user_message: str,
    history: list[dict[str, str]],
    cluster_poi_names: list[str],
    session_id: str,
    day_key: str,
) -> dict[str, Any]:
    """Mode B: Embeddings-based retrieval from Supabase pgvector."""
    from app.services.embedding_service import search_places

    # Search with cluster filter
    chunks = search_places(
        user_message, place_filter=cluster_poi_names, top_k=5
    )

    if not chunks:
        return _chat_direct(user_message, history, cluster_poi_names[:15])

    retrieved_names = list(
        {c["place_name"] for c in chunks if c.get("place_name")}
    )
    context_block = _format_retrieved_chunks(chunks)
    system_prompt, combined_message = _build_messages(
        user_message, history, context_block
    )

    try:
        reply = groq_chat_text(
            system_prompt, combined_message, timeout=60, max_tokens=500
        )
    except Exception as exc:
        logger.error("Chat Groq call failed: %s", exc)
        reply = "Sorry, I'm having trouble connecting to the AI service right now."

    return {"reply": reply.strip(), "grounded_places": retrieved_names}


def chat_response(
    user_message: str,
    history: list[dict[str, str]],
    place_names: list[str],
    cluster_poi_names: list[str] | None = None,
    session_id: str = "default",
    day_key: str | None = None,
) -> dict[str, Any]:
    """Generate a chat response grounded in place description data.

    Mode A (route places): Direct context injection for small sets.
    Mode B (full cluster): Embeddings-based retrieval for large sets.

    Args:
        user_message: The user's question.
        history: Conversation history as list of {role, content} dicts.
        place_names: Place names from the current route sequence.
        cluster_poi_names: All place names in the day's cluster (for Mode B).
        session_id: Session identifier for caching embeddings.
        day_key: Day key like "day_1" for per-day indexing.

    Returns:
        Dict with 'reply' (str) and 'grounded_places' (list[str]).
    """
    use_embeddings = (
        cluster_poi_names
        and len(cluster_poi_names) > 15
        and day_key is not None
    )

    if use_embeddings:
        return _chat_with_embeddings(
            user_message, history, cluster_poi_names, session_id, day_key
        )
    else:
        effective_names = (
            place_names or (cluster_poi_names[:15] if cluster_poi_names else [])
        )
        return _chat_direct(user_message, history, effective_names)
