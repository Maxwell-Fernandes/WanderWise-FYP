"""Groq: post-check rank-1 daily itinerary against Goa context and timing rules."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.config import GROQ_API_KEY
from app.services.groq_client import groq_chat_json

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a smart travel assistant reviewing a single-day Goa (India) itinerary. Stops are given in visit order (sequence 1 → N). Use names and times only; infer place types from names (beach, fort, church, temple, waterfall, spice plantation, wildlife, market, viewpoint, etc.).

Geographic context:
- North coast: Calangute, Baga, Anjuna, Vagator, Arambol — busy roads, strong midday sun on sand.
- South coast: Colva, Benaulim, Palolem, Agonda — often quieter; same midday beach heat.
- Central / inland: Old Goa churches, Panaji, spice farms; east: Western Ghats (Dudhsagar-area waterfalls, treks) — often better in cooler morning; long drives from far north to far south same day are taxing.

Evaluate the whole day and the sequence (not just one stop):

1) **Order & flow** — Does the order make sense for a tourist day? Flag jarring ping-pong (e.g. deep south → far north → south again without reason), or putting a heavy trek/waterfall after a full beach afternoon when energy/sun exposure is already high, or clustering incompatible moods (e.g. many sacred sites back-to-back with loud party beaches) if it feels obviously poor.

2) **Timing & pacing** — Visit windows should advance through the day (no backward time travel). Flag overlapping visit windows between consecutive or nearby stops if times imply impossible travel. Flag cramming too many long outdoor blocks in peak heat without shade breaks.

3) **Beach rule (hard product rule)** — Any stop that is clearly a beach must NOT have visit time overlapping 12:00–16:00 (scorching sun). Prefer morning or late afternoon/evening for beaches.

4) **Variety** — Flag only clear problems: same narrow activity repeated unreasonably (e.g. three similar beaches in a row with no cultural/nature break) or a day that ignores obvious opportunities implied by the mix (optional, only if stark).

5) **Reasonableness** — You do not know exact drive minutes; use Goa common sense only. Do not nitpick minor imperfections. If the sequence is plausible and the beach rule holds, ok=true.

6) **Replanning hints (when ok is false)** — List concrete stops that are redundant, harmful to the sequence, or violate rules. Use names that match or closely match the provided stop names (sequence field). The planner may remove them from the day or penalize them.

Respond with a single JSON object only:
{
  "ok": true|false,
  "issues": ["short strings; cite sequence numbers when useful"],
  "summary": "one sentence",
  "problematic_places": [
    {"name": "string matching a stop name", "reason": "brief"},
    ...
  ]
}

When ok=true, use problematic_places: []. When ok=false, include every stop you recommend dropping or fixing (can be empty only if problems are purely ordering with no specific culprit)."""


def evaluate_itinerary_qa(
    route_stops: list[dict[str, Any]],
    day_num: int,
) -> dict[str, Any]:
    """
    Call Groq once to sanity-check the recommended route.

    Returns a dict with keys: ok, issues, summary, source, and problematic_places (list).
    """
    if not GROQ_API_KEY:
        return {
            "ok": True,
            "issues": [],
            "summary": "Skipped: GROQ_API_KEY not set",
            "source": "skipped",
            "problematic_places": [],
        }

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
        raw = groq_chat_json(SYSTEM_PROMPT, user)
        data = json.loads(raw)
        ok = bool(data.get("ok", False))
        issues = data.get("issues") or []
        if not isinstance(issues, list):
            issues = [str(issues)]
        summary = str(data.get("summary", "")).strip() or "No summary"
        raw_pp = data.get("problematic_places") or []
        if not isinstance(raw_pp, list):
            raw_pp = []
        return {
            "ok": ok,
            "issues": [str(x) for x in issues],
            "summary": summary,
            "source": "groq",
            "problematic_places": raw_pp,
        }
    except Exception as exc:
        logger.warning("Itinerary QA Groq failed: %s", exc)
        return {
            "ok": True,
            "issues": [],
            "summary": f"QA error: {exc}",
            "source": "error",
            "problematic_places": [],
        }
