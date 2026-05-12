"""Groq: post-check rank-1 daily itinerary against Goa context and timing rules."""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

from app.config import GROQ_API_KEY
from app.services.groq_client import groq_chat_json

logger = logging.getLogger(__name__)

# In-memory cache for itinerary QA results (keyed by route hash)
_QA_CACHE: dict[str, dict[str, Any]] = {}

SYSTEM_PROMPT = """You are a travel QA reviewer for Goa, India. You receive a single-day itinerary with stops in chronological visit order (1 to N). Your job is to check whether the route is feasible, well-ordered, and avoids common pitfalls.

Output exactly ONE JSON object. No markdown, no commentary, no text outside the JSON.

## Output schema

{
  "ok": true | false,
  "issues": ["short description with sequence number", ...],
  "summary": "one sentence overall assessment",
  "problematic_places": [{"name": "place name", "reason": "brief explanation"}, ...]
}

---

## Review rules (in priority order)

### 1. Timing feasibility (HARD)
- Visit windows must be in strictly increasing order (no overlapping start/end times).
- Each stop must have enough time between it and the previous stop for travel.
- Flag as impossible if two consecutive stops are more than 60 km apart with less than 1 hour gap.
- If windows overlap or go backwards, set ok=false.

### 2. Beach time-of-day rule (HARD)
- Beach stops must NOT have visit windows that overlap with 12:00-16:00.
- Rationale: Goa beaches are scorching during midday; this is a health/comfort concern.
- A beach stop starting at 11:30 and ending at 12:01 partially overlaps 12:00-16:00 -- flag it.
- A beach stop from 16:00-18:00 is fine -- it starts after the danger window.
- If this rule is violated, set ok=false.

### 3. Route order (ping-pong check)
- Flag if the route goes deep south, then far north, then back south (or vice versa).
- A small backtrack of 5-10 km to visit a nearby attraction is acceptable.
- A 30+ km backtrack that doubles back across the map is NOT acceptable.
- If ping-ponging is detected, set ok=false.

### 4. Activity sequencing
- Flag strenuous activities (forts, treks, hill climbs) scheduled after 15:00.
- Flag early-morning activities that realistically need more sleep time than the previous stop's end time allows (e.g. previous stop ends at 23:00, next starts at 06:00).
- If sequencing is unreasonable, set ok=false.

### 5. Repetition / variety
- Flag ONLY if there are 3+ stops of the same type with no cultural/food break between them.
- Two beaches in a row is fine if they have different vibes.
- Three beaches in a row with no break is NOT fine.
- If repetition is detected, set ok=false.

### 6. Reasonableness threshold
- Do NOT nitpick minor imperfections like a 5-minute gap or a slightly tight lunch.
- If the route is plausible and the HARD rules (timing + beach) are satisfied, set ok=true.
- A few minor issues are acceptable -- note them in issues but keep ok=true.

---

## Issue formatting
- Each issue string should be short (under 80 chars).
- Include the sequence number of the problematic stop (e.g. "Stop 3: beach at noon").
- List issues in order of severity (hardest violation first).

## Replanning guidance
When ok=false, the problematic_places array should list concrete stops to remove or reschedule:
- Name the actual POI from the stop list.
- Give a brief reason (e.g. "beach at noon violates sun rule", "backtrack to north after south").
- This array is used by the system to auto-remove stops and re-plan, so be specific.

---

## Examples

Example 1 -- Good itinerary:
{"ok": true, "issues": ["Stop 5: slightly tight 20min transfer from Fort Aguada"], "summary": "Well-paced heritage morning, beach afternoon after 16:00.", "problematic_places": []}

Example 2 -- Beach at noon:
{"ok": false, "issues": ["Stop 3: Baga Beach visit 12:30-14:00 overlaps 12-16 sun window", "Stop 5: Calangute Beach visit 13:00-14:30 overlaps 12-16 sun window"], "summary": "Two beach stops scheduled during peak sun hours.", "problematic_places": [{"name": "Baga Beach", "reason": "visit window 12:30-14:00 overlaps 12:00-16:00 sun danger zone"}, {"name": "Calangute Beach", "reason": "visit window 13:00-14:30 overlaps 12:00-16:00 sun danger zone"}]}

Example 3 -- Ping-pong routing:
{"ok": false, "issues": ["Stop 4: 35km backtrack from south to north Goa after visiting south"], "summary": "Route ping-pongs between north and south Goa.", "problematic_places": [{"name": "Fort Aguada", "reason": "35km backtrack from south Goa to north Goa"}]}"""


def evaluate_itinerary_qa(
    route_stops: list[dict[str, Any]],
    day_num: int,
) -> dict[str, Any]:
    """
    Call Groq once to sanity-check the recommended route.

    Returns a dict with keys: ok, issues, summary, source, and problematic_places (list).
    Results are cached by route content (name, visit times) to avoid redundant API calls.
    """
    if not GROQ_API_KEY:
        return {
            "ok": True,
            "issues": [],
            "summary": "Skipped: GROQ_API_KEY not set",
            "source": "skipped",
            "problematic_places": [],
        }

    # Build cache key from route stops (name and timing, which define the route)
    cache_key_data = [
        (s.get("name"), s.get("visit_start"), s.get("visit_end"))
        for s in route_stops
    ]
    cache_key = hashlib.sha256(
        json.dumps(cache_key_data, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()

    # Return cached result if available
    if cache_key in _QA_CACHE:
        cached = _QA_CACHE[cache_key].copy()
        cached["source"] = "cache"  # Mark as from cache
        return cached

    slim = []
    for i, s in enumerate(route_stops, start=1):
        slim.append(
            {
                "sequence": i,
                "name": s.get("name"),
                "visit_start": s.get("visit_start"),
                "visit_end": s.get("visit_end"),
                "visit_duration_min": s.get("visit_duration_min"),
            }
        )
    user = json.dumps(
        {
            "day": day_num,
            "instruction": "Stops are in chronological visit order; assess the full sequence.",
            "stops": slim,
        },
        ensure_ascii=False,
        indent=2,
    )
    try:
        raw = groq_chat_json(SYSTEM_PROMPT, user, max_tokens=500)
        data = json.loads(raw)
        ok = bool(data.get("ok", False))
        issues = data.get("issues") or []
        if not isinstance(issues, list):
            issues = [str(issues)]
        summary = str(data.get("summary", "")).strip() or "No summary"
        raw_pp = data.get("problematic_places") or []
        if not isinstance(raw_pp, list):
            raw_pp = []
        result = {
            "ok": ok,
            "issues": [str(x) for x in issues],
            "summary": summary,
            "source": "groq",
            "problematic_places": raw_pp,
        }
        # Cache the result
        _QA_CACHE[cache_key] = result.copy()
        return result
    except Exception as exc:
        logger.warning("Itinerary QA Groq failed: %s", exc)
        return {
            "ok": True,
            "issues": [],
            "summary": f"QA error: {exc}",
            "source": "error",
            "problematic_places": [],
        }
