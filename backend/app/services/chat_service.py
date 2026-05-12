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
    """Truncate text to max_len, appending ellipsis if needed."""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rsplit(" ", 1)[0] + "..."


def _format_place_context(data: dict[str, Any]) -> str:
    """Format a single place's key fields into a compact context string."""
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
        parts.append("Guidelines: " + "; ".join(g.strip() for g in guidelines[:4] if g.strip()))

    timing = data.get("timing_info", "")
    if timing:
        parts.append(f"Best time: {_truncate(timing, 100)}")

    fee = data.get("entry_fee", "")
    if fee and fee != "Not specified":
        parts.append(f"Entry fee: {_truncate(fee, 80)}")

    full_text = "\n".join(parts)
    return _truncate(full_text, _MAX_CONTEXT_CHARS)


def _build_context_block(descriptions: dict[str, dict[str, Any]]) -> str:
    """Build the full place context block for the system prompt."""
    matched = {k: v for k, v in descriptions.items() if v and v.get("matched")}
    if not matched:
        return ""

    lines = ["\n--- Place Data ---"]
    for name, data in matched.items():
        lines.append(_format_place_context(data))
        lines.append("")
    lines.append("--- End Place Data ---")
    return "\n".join(lines)


def _build_messages(
    user_message: str,
    history: list[dict[str, str]],
    context_block: str,
) -> tuple[str, str]:
    """Build system prompt and user message with conversation history.

    Returns:
        Tuple of (system_prompt, user_message_with_history).
    """
    system_parts = [_SYSTEM_PROMPT]
    if context_block:
        system_parts.append(context_block)
    system_prompt = "\n".join(system_parts)

    # Build conversation history
    recent_history = history[-_MAX_HISTORY_TURNS * 2 :]
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


def chat_response(
    user_message: str,
    history: list[dict[str, str]],
    place_names: list[str],
) -> dict[str, Any]:
    """Generate a chat response grounded in place description data.

    Args:
        user_message: The user's question.
        history: Conversation history as list of {role, content} dicts.
        place_names: Place names from the current route sequence for grounding.

    Returns:
        Dict with 'reply' (str) and 'grounded_places' (list[str]).
    """
    descriptions: dict[str, dict[str, Any]] = {}
    grounded_places: list[str] = []

    if place_names:
        descriptions = get_descriptions_for_route(place_names)
        grounded_places = [
            name for name, data in descriptions.items() if data and data.get("matched")
        ]

    context_block = _build_context_block(descriptions)
    system_prompt, combined_message = _build_messages(user_message, history, context_block)

    try:
        reply = groq_chat_text(
            system_prompt,
            combined_message,
            timeout=60,
            max_tokens=500,
        )
    except Exception as exc:
        logger.error("Chat Groq call failed: %s", exc)
        reply = (
            "Sorry, I'm having trouble connecting to the AI service right now. "
            "Please try again in a moment."
        )

    return {
        "reply": reply.strip(),
        "grounded_places": grounded_places,
    }
