"""Shared Groq chat completion via LangChain for JSON responses."""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from app.config import GROQ_API_BASE, GROQ_API_KEY, GROQ_MODEL

logger = logging.getLogger(__name__)


def _build_llm(
    *, json_mode: bool = False, max_tokens: int = 500, timeout: int = 45
) -> ChatGroq:
    """Build a ChatGroq instance with optional JSON response format."""
    kwargs: dict[str, Any] = {
        "model": GROQ_MODEL,
        "temperature": 0.2,
        "api_key": GROQ_API_KEY,
        "max_tokens": max_tokens,
        "timeout": timeout,
    }
    # ChatGroq defaults to https://api.groq.com — only override if configured differently.
    if GROQ_API_BASE:
        base = GROQ_API_BASE.rstrip("/")
        if "console.groq.com" in base:
            base = base.replace("console.groq.com", "api.groq.com")
        for suffix in ("/openai/v1", "/openai", "/v1"):
            if base.endswith(suffix):
                base = base[: -len(suffix)]
                break
        if base and base != "https://api.groq.com":
            kwargs["base_url"] = base
    if json_mode:
        kwargs["model_kwargs"] = {"response_format": {"type": "json_object"}}
    return ChatGroq(**kwargs)


def _extract_content(response: Any) -> str:
    """Extract text content from a LangChain AIMessage response."""
    content = response.content
    if isinstance(content, str):
        return content
    # LangChain may return a list of content blocks
    if isinstance(content, list):
        return "".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )
    return str(content)


def groq_chat_text(
    system_prompt: str,
    user_message: str,
    *,
    timeout: int = 45,
    max_tokens: int = 600,
) -> str:
    """Call Groq via LangChain for plain text responses (no JSON mode).

    Args:
        system_prompt: System instruction for the LLM
        user_message: User input/data to process
        timeout: Request timeout in seconds (default 45)
        max_tokens: Max output tokens (default 600 for prose)
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set")

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ]
    llm = _build_llm(json_mode=False, max_tokens=max_tokens, timeout=timeout)
    response = llm.invoke(messages)
    content = _extract_content(response)
    if not content.strip():
        raise ValueError("Empty Groq message content")
    return content


def groq_chat_json(
    system_prompt: str,
    user_message: str,
    *,
    timeout: int = 45,
    max_tokens: int = 500,
) -> str:
    """Call Groq via LangChain; prefer JSON mode; retry once without response_format on 400.

    Args:
        system_prompt: System instruction for the LLM
        user_message: User input/data to process
        timeout: Request timeout in seconds (default 45)
        max_tokens: Max output tokens (default 500 for JSON responses)
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set")

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message),
    ]

    # First attempt with JSON mode
    try:
        llm = _build_llm(json_mode=True, max_tokens=max_tokens, timeout=timeout)
        response = llm.invoke(messages)
        content = _extract_content(response)
        if content.strip():
            return content
    except Exception as exc:
        logger.debug("Groq JSON mode attempt failed, retrying without: %s", exc)

    # Retry without JSON mode
    llm = _build_llm(json_mode=False, max_tokens=max_tokens, timeout=timeout)
    response = llm.invoke(messages)
    content = _extract_content(response)
    if not content.strip():
        raise ValueError("Empty Groq message content")
    return content
