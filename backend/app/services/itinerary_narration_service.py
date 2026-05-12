from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

import requests

from app.config import MODAL_NARRATION_URL
from app.services.description_context_service import (
    get_descriptions_for_route,
    get_many_place_contexts,
)
from app.services.groq_client import groq_chat_text

_NARRATION_CACHE: dict[str, dict[str, Any]] = {}


def _cache_key(payload: dict[str, Any]) -> str:
    route = payload.get("route", [])
    route_signature = [
        {
            "sequence": p.get("sequence"),
            "name": p.get("name"),
            "arrival_time": p.get("arrival_time"),
            "visit_start": p.get("visit_start"),
            "visit_end": p.get("visit_end"),
        }
        for p in route
    ]
    raw = json.dumps(
        {
            "day": payload.get("day"),
            "rank": payload.get("rank"),
            "user_preference": payload.get("user_preference", ""),
            "route": route_signature,
        },
        sort_keys=True,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _clean_text(text: str, max_len: int) -> str:
    import re

    text = re.sub(r"\s+", " ", (text or "")).strip()
    return text[:max_len].rstrip()


def _build_prompt(payload: dict[str, Any], contexts: list[dict[str, Any]]) -> str:
    day = payload.get("day")
    rank = payload.get("rank", 1)
    pref = payload.get("user_preference", "")
    route = payload.get("route", [])
    lines = [
        "You are a travel narrator for Goa itineraries.",
        f"Write a day-{day} itinerary narration for route rank {rank}.",
        "Tone: engaging, practical, concise. Keep it around 180-260 words.",
        "Use route order exactly and mention start + middle + end pacing.",
        "Mention timing naturally from visit slots.",
        "Avoid nightlife/shopping if user preference discourages them.",
        f"User preference: {pref}",
        "",
        "Ordered route:",
    ]
    for stop in route:
        lines.append(
            f"- {stop.get('sequence')}. {stop.get('name')} "
            f"({stop.get('visit_start')} to {stop.get('visit_end')})"
        )
    lines.append("")
    lines.append("Grounded place context:")
    for i, ctx in enumerate(contexts, start=1):
        if not ctx.get("matched"):
            continue
        place_lines = [f"- {i}. {ctx.get('name')}:"]
        desc = ctx.get("description", ctx.get("summary", ""))
        if desc:
            place_lines.append(f"  Description: {desc[:300]}")
        faq = ctx.get("accordion_sections", [])
        if faq:
            top_qa = faq[:2]
            for qa in top_qa:
                place_lines.append(
                    f"  FAQ: {qa.get('title', '')} — {_clean_text(qa.get('content', ''), 100)}"
                )
        guidelines = ctx.get("guidelines", [])
        if guidelines:
            place_lines.append(
                f"  Tips: {'; '.join(g.strip() for g in guidelines[:2] if g.strip())}"
            )
        timing = ctx.get("timing_info", ctx.get("best_time_hint", ""))
        if timing:
            place_lines.append(f"  Best time: {timing[:80]}")
        lines.append("\n".join(place_lines))
    lines.append("")
    lines.append("Return only narration text.")
    return "\n".join(lines)


def _fallback_narration(payload: dict[str, Any], contexts: list[dict[str, Any]]) -> str:
    day = payload.get("day")
    route = payload.get("route", [])
    if not route:
        return f"Day {day} has no selected places yet. Try another ranked route."
    first = route[0]
    last = route[-1]
    parts = [
        f"Start day {day} with {first.get('name')} around {first.get('visit_start')}, easing into the itinerary with a comfortable first stop.",
    ]
    for idx, stop in enumerate(route[1:-1], start=2):
        parts.append(
            f"Then continue to {stop.get('name')} ({stop.get('visit_start')} to {stop.get('visit_end')}) to keep the day flowing without long idle gaps."
        )
        if idx >= 4:
            break
    parts.append(
        f"Wrap up at {last.get('name')} by {last.get('visit_end')} for a balanced finish to the day."
    )
    matched = [c for c in contexts if c.get("matched")]
    if matched:
        hint = matched[0].get("best_time_hint")
        if hint:
            parts.append(f"Tip: {hint}")
    return " ".join(parts)


def _call_modal_narration(prompt: str) -> str | None:
    if not MODAL_NARRATION_URL:
        return None
    try:
        res = requests.post(
            MODAL_NARRATION_URL,
            json={"prompt": prompt},
            timeout=25,
        )
        res.raise_for_status()
        data = res.json()
        text = data.get("narration") or data.get("text") or data.get("output")
        if isinstance(text, str) and text.strip():
            return text.strip()
    except Exception:
        return None
    return None


def _call_groq_narration(prompt: str) -> str | None:
    try:
        text = groq_chat_text(
            system_prompt="You are a travel narrator for Goa itineraries. Return only narration text, no markdown or formatting.",
            user_message=prompt,
            max_tokens=600,
            timeout=30,
        )
        if text.strip():
            return text.strip()
    except Exception:
        return None
    return None


def generate_day_narration(payload: dict[str, Any]) -> dict[str, Any]:
    key = _cache_key(payload)
    if key in _NARRATION_CACHE:
        return _NARRATION_CACHE[key]

    route = payload.get("route", [])
    route_names = [stop.get("name", "") for stop in route]
    full_descriptions = get_descriptions_for_route(route_names)

    # Convert to list format matching get_many_place_contexts output
    contexts: list[dict[str, Any]] = []
    for name in route_names:
        ctx = full_descriptions.get(name)
        if ctx:
            contexts.append(ctx)
        else:
            contexts.append({"matched": False, "name": name})

    prompt = _build_prompt(payload, contexts)

    modal_text = _call_modal_narration(prompt)
    if modal_text:
        provider = "modal"
        narration_text = modal_text
    else:
        groq_text = _call_groq_narration(prompt)
        if groq_text:
            provider = "groq"
            narration_text = groq_text
        else:
            provider = "fallback"
            narration_text = _fallback_narration(payload, contexts)

    result = {
        "day": payload.get("day"),
        "rank": payload.get("rank", 1),
        "provider": provider,
        "narration_text": narration_text,
        "grounded_places": [c for c in contexts if c.get("matched")],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    _NARRATION_CACHE[key] = result
    return result
