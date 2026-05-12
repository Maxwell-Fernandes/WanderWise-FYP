from pathlib import Path
from typing import Any

import numpy as np

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import MAPS_DIR
from app.schemas.simulation import (
    ChatRequest,
    Module1Request,
    Module2Request,
    Module4NarrationRequest,
    Module4Request,
)
from app.services.chat_service import chat_response
from app.services.itinerary_narration_service import generate_day_narration
from app.services.module1_service import run_module1_simulation
from app.services.module2_service import run_module2_simulation
from app.services.module4_service import run_module4_simulation

router = APIRouter()


def _json_safe(value: Any) -> Any:
    """Recursively convert numpy/pandas values to JSON-safe types."""
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [_json_safe(v) for v in value]
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        value = float(value)
    if isinstance(value, float):
        if np.isnan(value) or np.isinf(value):
            return None
        return value
    return value


def _sanitize_mobile_stop(stop: dict[str, Any]) -> dict[str, Any]:
    """Keep only stop fields needed by mobile itinerary/map UI."""
    raw_nearby = stop.get("nearby_suggestions") or []
    safe_nearby: list[dict[str, Any]] = []
    if isinstance(raw_nearby, list):
        for suggestion in raw_nearby:
            if not isinstance(suggestion, dict):
                continue
            safe_nearby.append(
                {
                    "poi_id": suggestion.get("poi_id"),
                    "name": suggestion.get("name"),
                    "latitude": suggestion.get("latitude"),
                    "longitude": suggestion.get("longitude"),
                    "distance_km": suggestion.get("distance_km"),
                    "wpi": suggestion.get("wpi"),
                }
            )

    enriched_fields = {}
    for key in ("description", "best_time_hint", "entry_fee", "category", "source_url"):
        val = stop.get(key)
        if val:
            enriched_fields[key] = val

    return {
        "sequence": stop.get("sequence"),
        "poi_id": stop.get("poi_id"),
        "name": stop.get("name"),
        "latitude": stop.get("latitude"),
        "longitude": stop.get("longitude"),
        "arrival_time": stop.get("arrival_time"),
        "visit_start": stop.get("visit_start"),
        "visit_end": stop.get("visit_end"),
        "visit_duration_min": stop.get("visit_duration_min"),
        "nearby_suggestions": safe_nearby,
        **enriched_fields,
    }


def _sanitize_mobile_alternative(alternative: dict[str, Any]) -> dict[str, Any]:
    """Reduce an alternative route to mobile-friendly fields only."""
    raw_route = alternative.get("route") or []
    safe_route: list[dict[str, Any]] = []
    for stop in raw_route:
        if isinstance(stop, dict):
            safe_route.append(_sanitize_mobile_stop(stop))

    return {
        "day": alternative.get("day"),
        "map": alternative.get("map"),
        "route": safe_route,
        "total_distance_km": alternative.get("total_distance_km"),
        "total_travel_time_min": alternative.get("total_travel_time_min"),
        "total_time_min": alternative.get("total_time_min"),
    }


def _build_mobile_module4_response(result: dict[str, Any]) -> dict[str, Any]:
    """Return first-itinerary-only data without rank/fitness/testing fields."""
    routes = result.get("routes") if isinstance(result.get("routes"), dict) else {}

    for day_key, day_data in routes.items():
        if not isinstance(day_data, dict):
            routes[day_key] = {"alternatives": [], "recommended_route": None}
            continue

        alternatives = day_data.get("alternatives")
        first_alternative: dict[str, Any] | None = None

        if isinstance(alternatives, list) and alternatives:
            candidate = alternatives[0]
            if isinstance(candidate, dict):
                first_alternative = candidate
        elif isinstance(day_data.get("recommended_route"), dict):
            first_alternative = day_data["recommended_route"]

        if first_alternative:
            sanitized = _sanitize_mobile_alternative(first_alternative)
            day_data["alternatives"] = [sanitized]
            day_data["recommended_route"] = sanitized
        else:
            day_data["alternatives"] = []
            day_data["recommended_route"] = None

        # Remove non-mobile/testing fields from day-level response.
        day_data.pop("secondary_itinerary", None)
        day_data.pop("itinerary_qa", None)
        day_data.pop("itinerary_retry_attempted", None)
        day_data.pop("itinerary_retry_details", None)

    mobile_result: dict[str, Any] = {
        "num_days": result.get("num_days"),
        "travel_type": result.get("travel_type"),
        "travel_distance": result.get("travel_distance"),
        "hotel_location": result.get("hotel_location"),
        "hotel_address": result.get("hotel_address"),
        "hotel_lat": result.get("hotel_lat"),
        "hotel_lon": result.get("hotel_lon"),
        "region": result.get("region"),
        "routes": routes,
    }

    if mobile_result.get("num_days") is None:
        mobile_result["num_days"] = len(routes)

    return mobile_result


@router.post("/module1/simulate")
def module1_simulate(payload: Module1Request):
    result = run_module1_simulation(
        payload.user_preference,
        payload.min_rating,
        use_llm_interests=payload.use_llm_interests,
    )
    return {"data": _json_safe(result)}


@router.post("/module2/simulate")
def module2_simulate(payload: Module2Request):
    result = run_module2_simulation(
        payload.num_days,
        payload.min_reviews,
        payload.random_state,
        travel_distance=payload.travel_distance,
        hotel_location=payload.hotel_location,
        hotel_address=payload.hotel_address,
        hotel_lat=payload.hotel_lat,
        hotel_lon=payload.hotel_lon,
        region=payload.region,
        user_preference=payload.user_preference,
    )
    return {"data": _json_safe(result)}


@router.post("/module4/simulate")
def module4_simulate(payload: Module4Request):
    request_payload = payload.model_dump(exclude={"mobile_only"})
    result = run_module4_simulation(request_payload)
    if payload.mobile_only and isinstance(result, dict):
        result = _build_mobile_module4_response(result)
    return {"data": _json_safe(result)}


@router.post("/module4/narrate-day")
def module4_narrate_day(payload: Module4NarrationRequest):
    result = generate_day_narration(payload.model_dump())
    return {"data": _json_safe(result)}


@router.get("/maps/{map_name}")
def get_map(map_name: str):
    path = MAPS_DIR / Path(map_name).name
    if not path.exists():
        raise HTTPException(status_code=404, detail="Map not found")
    return FileResponse(path)


@router.post("/chat/message")
def chat_message(payload: ChatRequest):
    history = [msg.model_dump() for msg in payload.history]
    result = chat_response(
        user_message=payload.message,
        history=history,
        place_names=payload.place_names,
        cluster_poi_names=payload.cluster_poi_names,
        session_id=payload.session_id,
        day_key=payload.day_key,
    )
    return {"data": _json_safe(result)}
