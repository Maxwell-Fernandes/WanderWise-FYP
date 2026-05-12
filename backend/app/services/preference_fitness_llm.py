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

SYSTEM_PROMPT = """You are a route optimizer configurator for Goa, India. Given a travel type and user preference text, output ONE JSON object that tunes the optimizer's fitness function.

Output exactly ONE JSON object. No markdown, no commentary, no text outside the JSON.

## Output schema

{
  "weight_deltas": { "field": float, ... },
  "tag_preference": { "tag": float, ... }
}

---

## weight_deltas

Each field is a small multiplier tweak to the travel-type baseline. The formula is:
    final_weight = baseline x (1 + delta)

Deltas MUST stay in [-0.5, 0.5]. Omit a key or set it to 0.0 to keep the baseline unchanged.

| Key               | What it controls                                        |
|-------------------|---------------------------------------------------------|
| distance          | Penalty for long drives between stops                   |
| overtime          | Penalty for exceeding planned day length                |
| undertime         | Penalty for days that end too early                     |
| wrong_time        | Penalty for visiting POIs at bad times of day           |
| waterfall         | Extra penalty when route includes multiple waterfalls   |
| fatigue           | Penalty for strenuous segments (treks, forts, hills)    |
| type_coverage     | Penalty for lacking variety in place categories         |
| beach_dominance   | Penalty if the day is too beach-heavy                   |

Use positive deltas to increase that penalty (discourage the behavior).
Use negative deltas to decrease that penalty (allow more of it).

## tag_preference

Per-tag route scoring. Values in [-1, 1]:
- Positive = reward routes containing POIs with this tag
- Negative = penalize routes containing POIs with this tag

Allowed keys (use these exact strings):

waterfall, strenuous, beach, water_sports, park, religious, nature,
historical, fort, sanctuary, scenic, peaceful, relaxation, photography,
temple, church, shopping, viewpoint

---

## CRITICAL: Merge rule for tag_preference

The server already applies default tag preferences for the given travel_type.
Your tag_preference object is merged on top:

- If you output a tag key, your value REPLACES the server default for that tag.
- If you omit a tag key, the server default is kept.

This means:
- Do NOT output a tag with a weak value (e.g. -0.1) if the server already has a
  strong default (e.g. -0.8) -- you would accidentally weaken it.
- Only output a tag when you want to CHANGE the default or when no default exists.
- When in doubt, output fewer tags. Sparse output is better than noisy output.

## Sparsity guideline

Only include weight_deltas and tag_preference keys that are clearly justified by the
user text. Empty objects are valid:

    {"weight_deltas": {}, "tag_preference": {}}

means "trust the server defaults completely."

---

## Conflict resolution

If the user text requests risky/strenuous activities but the travel_type is "family"
(or similar safe type), prioritize safety:
- Increase fatigue and waterfall penalties (positive deltas).
- Set strenuous tag to negative.
- Only override to positive strenuous/waterfall if the user explicitly and clearly
  insists (e.g. "I specifically want hard treks even with kids").

## Travel-type context

The user message includes a travel_type field. Common types and their typical defaults:
- solo: balanced, moderate penalties, flexible.
- couple: similar to solo, slight romantic/scenic bias.
- family: lower fatigue tolerance, waterfall avoidance, kid-friendly bias.
- friends: flexible, can handle more variety.
- adventure: lower fatigue penalty, higher strenuous reward.

Use this context to calibrate your output. The user_preference field is what matters
most -- the travel_type sets the baseline, your output fine-tunes it.

---

## Examples

Example 1 -- Solo traveler wants relaxed heritage, no hiking:
{"weight_deltas":{"fatigue":0.15,"waterfall":0.1,"distance":0.05},"tag_preference":{"strenuous":-0.6,"historical":0.5}}

Example 2 -- Couple wants beaches and sunset spots:
{"weight_deltas":{"beach_dominance":-0.1},"tag_preference":{"beach":0.5,"viewpoint":0.4}}

Example 3 -- Family with young kids, no preference text:
{"weight_deltas":{"fatigue":0.2},"tag_preference":{"strenuous":-0.5,"waterfall":-0.3}}

Example 4 -- Adventure traveler wants trekking and waterfalls:
{"weight_deltas":{"fatigue":-0.2,"waterfall":-0.1},"tag_preference":{"strenuous":0.6,"waterfall":0.5,"nature":0.3}}

Example 5 -- Minimal change (no clear user preference):
{"weight_deltas":{},"tag_preference":{}}}"""


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
        content = groq_chat_json(SYSTEM_PROMPT, user_block, max_tokens=400)
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
