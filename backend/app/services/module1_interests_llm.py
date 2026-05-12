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

SYSTEM_PROMPT = """You are a travel preference analyst for Goa, India. Your job is to read a short user message about their travel wishes and extract structured preference data.

Output exactly ONE JSON object. No markdown, no commentary, no text outside the JSON.

## Output schema

{
  "positive_interests": ["category", ...],
  "negative_interests": ["category", ...],
  "themes_keywords": ["specific term", ...],
  "mentioned_places": ["place name fragment", ...],
  "constraints": {
    "pace": "relaxed" | "moderate" | "packed",
    "avoid_strenuous": true | false,
    "kid_friendly": true | false
  },
  "preference_summary": "one sentence, max 240 chars"
}

## Allowed categories (use these exact strings, nothing else)

adventure, beaches, food, fort, historical, nature, nightlife, peaceful,
photography, relaxation, religious, scenic, shopping, water sports

## Field rules

1. **positive_interests** — Categories the user wants or sounds enthusiastic about.
2. **negative_interests** — Categories the user explicitly wants to avoid.
3. **themes_keywords** — Up to 12 short tokens (max 32 chars each). These are specific words from the user's text or strongly implied topics (e.g. "dudhsagar", "sunset", "spice plantation"). They must NOT be category names — they are finer-grained tags.
4. **mentioned_places** — Up to 8 place name fragments the user named or clearly referenced (e.g. "old goa", "baga beach").
5. **constraints.pace** — Infer from tone: "relaxed" for chill/easy/rest, "moderate" for balanced/normal, "packed" for see-everything/rush. Default to "moderate" if unclear.
6. **constraints.avoid_strenuous** — true if user mentions avoiding hard treks, steep climbs,体力 work, or says they want easy/relaxed. false otherwise.
7. **constraints.kid_friendly** — true only if user mentions kids, children, or family with young children.
8. **preference_summary** — A concise natural-language sentence summarizing the user's overall travel wish.

## Handling edge cases

- If the input is empty or unintelligible: output empty arrays, default constraints (pace: moderate, avoid_strenuous: false, kid_friendly: false), and summary: "No clear preference stated."
- If the user only mentions dislikes (no positives): positive_interests can be [].
- Slang and informal language: map to the closest category. "chill vibes" → peaceful/relaxation. "party" → nightlife. "photo spots" → photography.
- Ambiguous input: prefer the most likely interpretation. "goa" alone is too vague — treat as no clear preference.

## Example

Input: "forts and churches, no clubs"
Output: {"positive_interests":["historical","religious"],"negative_interests":["nightlife"],"themes_keywords":["basilica","fort"],"mentioned_places":[],"constraints":{"pace":"relaxed","avoid_strenuous":true},"preference_summary":"Heritage and churches; easy pace; no nightlife."}"""


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
