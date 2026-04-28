"""Shared Groq OpenAI-compatible chat completion for JSON responses."""

from __future__ import annotations

from typing import Any

import requests

from app.config import GROQ_API_BASE, GROQ_API_KEY, GROQ_MODEL


def _resolve_chat_completions_url(raw_base: str) -> str:
    """Normalize Groq base URL to OpenAI-compatible chat completions endpoint."""
    base = (raw_base or "").strip().rstrip("/")
    if not base:
        base = "https://api.groq.com/openai/v1"

    # Accept users pasting the console host and normalize to API host.
    if "console.groq.com" in base:
        base = base.replace("console.groq.com", "api.groq.com")

    # If user already provided a full chat completions URL, keep it as-is.
    if base.endswith("/openai/v1/chat/completions") or base.endswith("/chat/completions"):
        return base

    # If only host is provided, assume OpenAI-compatible path.
    if base.endswith("api.groq.com"):
        base = f"{base}/openai/v1"

    # If someone provided /openai without version, complete it.
    if base.endswith("/openai"):
        base = f"{base}/v1"

    return f"{base}/chat/completions"


def groq_chat_json(system_prompt: str, user_message: str, *, timeout: int = 45) -> str:
    """POST chat/completions; prefer JSON mode; retry once without response_format on 400."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set")
    url = _resolve_chat_completions_url(GROQ_API_BASE)
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    body: dict[str, Any] = {
        "model": GROQ_MODEL,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "response_format": {"type": "json_object"},
    }
    res = requests.post(url, headers=headers, json=body, timeout=timeout)
    if res.status_code == 400:
        body.pop("response_format", None)
        res = requests.post(url, headers=headers, json=body, timeout=timeout)
    res.raise_for_status()
    payload = res.json()
    choices = payload.get("choices") or []
    if not choices:
        raise ValueError("Groq returned no choices")
    message = choices[0].get("message") or {}
    content = message.get("content") or ""
    if not content.strip():
        raise ValueError("Empty Groq message content")
    return content
