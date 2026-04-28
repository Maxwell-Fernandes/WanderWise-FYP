"""One-shot Groq LLM resolution of fitness weights and tag preferences (not per GA evaluation)."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from app.config import GROQ_API_KEY
from app.services.groq_client import groq_chat_json
from app.services.module4_service import (
    FitnessWeights,
    get_default_tag_adjustments,
    get_fitness_weights,
)

logger = logging.getLogger(__name__)

# Keys must match tags producible by module4 POI classification / balance tags.
ALLOWED_TAG_KEYS = frozenset(
    {
        "waterfall",
        "strenuous",
        "beach",
        "water_sports",
        "park",
        "religious",
        "nature",
        "historical",
        "fort",
        "sanctuary",
        "scenic",
        "peaceful",
        "relaxation",
        "photography",
        "temple",
        "church",
        "shopping",
        "viewpoint",
    }
)

WEIGHT_DELTA_MIN = -0.5
WEIGHT_DELTA_MAX = 0.5
TAG_PREF_MIN = -1.0
TAG_PREF_MAX = 1.0
MERGED_WEIGHT_MIN = 0.25
MERGED_WEIGHT_MAX = 4.0

SYSTEM_PROMPT = """You configure a route optimizer for Goa, India. Reply with ONE JSON object only (no markdown, no text outside JSON).

## What the numbers do
- weight_deltas: each field is a *small* tweak to the travel-type baseline. Formula: final_multiplier = baseline * (1 + delta). Deltas must stay in [-0.5, 0.5]. Use 0.0 or omit a key when you do not want to change that dimension.
  - distance: higher delta = penalize long drives more.
  - overtime / undertime: stricter schedule vs more flexible day.
  - wrong_time: visiting POIs at awkward times of day.
  - waterfall: extra penalty when the route includes *multiple* waterfall-style stops (not the first one only).
  - fatigue: penalty for many strenuous segments (treks, forts, hills).
  - type_coverage: penalty for missing variety of place categories.
  - beach_dominance: penalty if the day is too beach-heavy.
- tag_preference: values in [-1, 1]. Negative = discourage routes containing POIs with that tag (matched from names/types). Positive = reward. Allowed keys only: waterfall, strenuous, beach, water_sports, park, religious, nature, historical, fort, sanctuary, scenic, peaceful, relaxation, photography, temple, church, shopping, viewpoint.

## Critical merge rule (tag_preference)
The API already applies **server defaults** for this travel_type. Your tag_preference object is **merged on top**: if you output a key, your value **replaces** the server default for that tag. To keep the server default, **omit** that key entirely. Do not output weak values that accidentally undo strong safety defaults (e.g. family + easy day → do not output waterfall: -0.2 unless you intend to replace a stronger default).

Prefer **sparse** output: only weight_deltas and tag_preference keys that the user text clearly justifies.

## Conflict resolution
If user text asks for risky or strenuous activities but travel_type is family (or similar), favor safer weights and negative strenuous/waterfall tags unless the user clearly insists on adventure.

## Examples (format only; values illustrative)

User wants relaxed heritage, no hiking:
{"weight_deltas":{"fatigue":0.15,"waterfall":0.1,"distance":0.05},"tag_preference":{"strenuous":-0.6,"historical":0.5}}

User wants beaches and sunset spots, couple:
{"weight_deltas":{"beach_dominance":-0.1},"tag_preference":{"beach":0.5,"viewpoint":0.4}}

Minimal change (trust server defaults):
{"weight_deltas":{},"tag_preference":{}}"""


@dataclass
class ResolvedFitnessProfile:
    """Resolved GA objective: merged penalty weights plus per-tag route preferences."""

    weights: FitnessWeights
    tag_adjustments: dict[str, float]
    source: str = "baseline"


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def merge_fitness_weights(
    base: FitnessWeights, deltas: dict[str, Any] | None
) -> FitnessWeights:
    """Apply LLM deltas: merged[field] = clamp(base[field] * (1 + delta))."""
    if not deltas:
        return base
    kwargs: dict[str, float] = {}
    for name in (
        "distance",
        "hard_violation",
        "undertime",
        "overtime",
        "wrong_time",
        "waterfall",
        "fatigue",
        "type_coverage",
        "beach_dominance",
    ):
        raw = deltas.get(name, 0.0)
        try:
            d = _clamp(float(raw), WEIGHT_DELTA_MIN, WEIGHT_DELTA_MAX)
        except (TypeError, ValueError):
            d = 0.0
        v = float(getattr(base, name)) * (1.0 + d)
        kwargs[name] = _clamp(v, MERGED_WEIGHT_MIN, MERGED_WEIGHT_MAX)
    return FitnessWeights(**kwargs)


def _sanitize_tag_preferences(raw: Any) -> dict[str, float]:
    if not isinstance(raw, dict):
        return {}
    out: dict[str, float] = {}
    for k, v in raw.items():
        if k not in ALLOWED_TAG_KEYS:
            continue
        try:
            out[k] = _clamp(float(v), TAG_PREF_MIN, TAG_PREF_MAX)
        except (TypeError, ValueError):
            continue
    return out


def _parse_llm_content(content: str) -> tuple[dict[str, Any], dict[str, float]]:
    data = json.loads(content.strip())
    if not isinstance(data, dict):
        return {}, {}
    wd = data.get("weight_deltas") or {}
    tp = _sanitize_tag_preferences(data.get("tag_preference"))
    if not isinstance(wd, dict):
        wd = {}
    return wd, tp


def resolve_fitness_profile(
    travel_type: str | None,
    user_preference: str,
    *,
    use_llm: bool = False,
    module1_context: str | None = None,
) -> ResolvedFitnessProfile:
    """
    Resolve fitness weights and tag preferences for one Module 4 run.

    Travel-type defaults (e.g. family avoids waterfalls) always apply; Groq can override
    or refine the same keys when use_llm is True and GROQ_API_KEY is set.
    """
    base = get_fitness_weights(travel_type)
    defaults = get_default_tag_adjustments(travel_type)
    if not use_llm or not GROQ_API_KEY:
        return ResolvedFitnessProfile(
            weights=base,
            tag_adjustments=defaults,
            source="baseline",
        )

    defaults_json = json.dumps(defaults, ensure_ascii=False, sort_keys=True)
    user_block = (
        f"travel_type: {travel_type or 'solo'}\n"
        f"server_default_tag_preferences (omit a tag in your output to keep these; your tag_preference replaces per key): "
        f"{defaults_json}\n"
        f"user_preference: {user_preference.strip() or '(none)'}\n"
    )
    if module1_context and module1_context.strip():
        user_block += f"module1_structured_extraction (from Groq interest pass; honor themes and constraints):\n{module1_context.strip()}\n"
    try:
        content = groq_chat_json(SYSTEM_PROMPT, user_block)
        wd, tp = _parse_llm_content(content)
        merged = merge_fitness_weights(base, wd)
        merged_tags = {**defaults, **tp}
        return ResolvedFitnessProfile(
            weights=merged,
            tag_adjustments=merged_tags,
            source="groq",
        )
    except Exception as exc:
        logger.warning("Groq fitness profile failed, using baseline: %s", exc)
        return ResolvedFitnessProfile(
            weights=base,
            tag_adjustments=defaults,
            source="fallback",
        )
