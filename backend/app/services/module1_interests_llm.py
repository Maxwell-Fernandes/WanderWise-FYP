"""Groq: map free-text user preference to Module 1 categories plus structured extraction."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from app.services.groq_client import groq_chat_json
from app.services.module1_service import CATEGORY_KEYWORDS

ALLOWED_CATEGORIES = frozenset(CATEGORY_KEYWORDS.keys())
ALLOWED_PACE = frozenset({"relaxed", "moderate", "packed"})

MAX_THEMES = 12
MAX_THEME_LEN = 32
MAX_MENTIONED_PLACES = 8
MAX_PLACE_FRAG_LEN = 48
MAX_SUMMARY_LEN = 240

SYSTEM_PROMPT = """Goa travel planner. Output ONE JSON object only.

Categories: adventure|beaches|food|fort|historical|nature|nightlife|peaceful|photography|relaxation|religious|scenic|shopping|water sports

Schema:
{"positive_interests":[cats],"negative_interests":[cats],"themes_keywords":["short tokens, max 12, ≤32 chars"],"mentioned_places":["name fragments, max 8"],"constraints":{"pace":"relaxed|moderate|packed","avoid_strenuous":bool,"kid_friendly":bool},"preference_summary":"≤240 chars"}

Rules: Map to categories only. themes_keywords = specific words (dudhsagar, sunset), not new categories. If user only dislikes things, positive_interests can be [].
Example: {"positive_interests":["historical","religious"],"negative_interests":["nightlife"],"themes_keywords":["basilica","fort"],"mentioned_places":[],"constraints":{"pace":"relaxed","avoid_strenuous":true},"preference_summary":"Heritage and churches; easy pace; no nightlife."}"""


def _sanitize_categories(raw: Any) -> list[str]:
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    for x in raw:
        if isinstance(x, str) and x in ALLOWED_CATEGORIES and x not in out:
            out.append(x)
    return out


def _sanitize_string_list(
    raw: Any, *, max_items: int, max_item_len: int
) -> list[str]:
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    for x in raw:
        if not isinstance(x, str):
            continue
        s = re.sub(r"\s+", " ", x.strip().lower())[:max_item_len]
        if s and s not in out:
            out.append(s)
        if len(out) >= max_items:
            break
    return out


def _sanitize_summary(raw: Any) -> str:
    if not isinstance(raw, str):
        return ""
    s = re.sub(r"\s+", " ", raw.strip())
    return s[:MAX_SUMMARY_LEN]


def _sanitize_constraints(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        return {}
    out: dict[str, Any] = {}
    pace = raw.get("pace")
    if isinstance(pace, str) and pace.lower() in ALLOWED_PACE:
        out["pace"] = pace.lower()
    for key in ("avoid_strenuous", "kid_friendly"):
        if key in raw and isinstance(raw[key], bool):
            out[key] = raw[key]
    return out


def _build_extraction_from_parsed(data: dict[str, Any]) -> dict[str, Any]:
    themes = _sanitize_string_list(
        data.get("themes_keywords"), max_items=MAX_THEMES, max_item_len=MAX_THEME_LEN
    )
    places = _sanitize_string_list(
        data.get("mentioned_places"),
        max_items=MAX_MENTIONED_PLACES,
        max_item_len=MAX_PLACE_FRAG_LEN,
    )
    constraints = _sanitize_constraints(data.get("constraints"))
    summary = _sanitize_summary(data.get("preference_summary"))
    extraction: dict[str, Any] = {}
    if themes:
        extraction["themes_keywords"] = themes
    if places:
        extraction["mentioned_places"] = places
    if constraints:
        extraction["constraints"] = constraints
    if summary:
        extraction["preference_summary"] = summary
    return extraction


@dataclass
class Module1LlmResult:
    """Outcome of Groq interest + extraction call."""

    positive_interests: list[str]
    negative_interests: list[str]
    preference_extraction: dict[str, Any] = field(default_factory=dict)


def resolve_module1_interests_llm(user_preference: str) -> Module1LlmResult:
    """
    Call Groq for categories plus themes, places, constraints, summary.

    Raises:
        Exception on HTTP/parse errors (caller falls back to keyword classifier).
    """
    text = groq_chat_json(
        SYSTEM_PROMPT,
        f"user_preference:\n{(user_preference or '').strip() or '(none)'}",
        max_tokens=300,
    )
    data = json.loads(text.strip())
    if not isinstance(data, dict):
        raise ValueError("LLM response is not a JSON object")
    pos = _sanitize_categories(data.get("positive_interests"))
    neg = _sanitize_categories(data.get("negative_interests"))
    neg = [c for c in neg if c not in pos]
    extraction = _build_extraction_from_parsed(data)
    return Module1LlmResult(
        positive_interests=pos,
        negative_interests=neg,
        preference_extraction=extraction,
    )


def interests_lists_to_dict(positive: list[str], negative: list[str]) -> dict[str, bool]:
    """Build user_interests map for API responses (True=want, False=avoid)."""
    out: dict[str, bool] = {}
    for p in positive:
        out[p] = True
    for n in negative:
        if n not in out:
            out[n] = False
    return out
