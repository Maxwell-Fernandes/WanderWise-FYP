"""Groq: post-check rank-1 daily itinerary against Goa context and timing rules."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.config import GROQ_API_KEY
from app.services.groq_client import groq_chat_json

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a travel QA reviewing a single-day Goa itinerary. Stops are in visit order (1→N).

Rules:
1. **Order** — Flag ping-pong (deep south→far north→south) or heavy treks after beach afternoons.
2. **Timing** — Windows must advance; flag overlaps or impossible travel.
3. **Beach rule (HARD)** — Beaches must NOT overlap 12:00–16:00 (scorching sun).
4. **Variety** — Flag only stark repetition (3+ similar beaches with no cultural break).
5. **Reasonableness** — Don't nitpick minor imperfections. If plausible + beach rule holds → ok=true.
6. **Replanning** — When ok=false, name concrete redundant/problematic stops.

JSON only:
{
  "ok": bool,
  "issues": ["short strings with seq#"],
  "summary": "one sentence",
  "problematic_places": [{"name": "...", "reason": "brief"}]
}"""


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
