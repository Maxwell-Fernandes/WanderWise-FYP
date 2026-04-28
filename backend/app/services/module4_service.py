from __future__ import annotations

import json
import logging
import random
import uuid
from dataclasses import asdict, dataclass, replace
from difflib import SequenceMatcher
from math import asin, ceil, cos, radians, sin, sqrt
from pathlib import Path
from typing import Any, Dict, List, Tuple

import folium
import numpy as np
import requests

from app.config import EXPORTS_DIR, MAPS_DIR, OSRM_BASE_URL
from app.services import ga_config as cfg
from app.services.module1_service import run_module1_simulation
from app.services.module2_service import run_module2_simulation
from app.utils.data_loader import ensure_output_dirs

logger = logging.getLogger(__name__)

POPULATION_SIZE = cfg.POPULATION_SIZE
MAX_GENERATIONS = cfg.MAX_GENERATIONS
CROSSOVER_RATE = cfg.CROSSOVER_RATE
MUTATION_RATE = cfg.MUTATION_RATE
TOURNAMENT_SIZE = cfg.TOURNAMENT_SIZE
ELITE_COUNT = cfg.ELITE_COUNT
EARLY_STOPPING_THRESHOLD = cfg.EARLY_STOPPING_THRESHOLD
INITIAL_CHROMOSOME_LENGTH = cfg.INITIAL_CHROMOSOME_LENGTH
MIN_POIS_PER_ROUTE = cfg.MIN_POIS_PER_ROUTE
MAX_POIS_PER_ROUTE = cfg.MAX_POIS_PER_ROUTE
TOUR_START_TIME = cfg.TOUR_START_TIME
TOUR_END_TIME = cfg.TOUR_END_TIME
LUNCH_START_TIME = cfg.LUNCH_START_TIME
LUNCH_END_TIME = cfg.LUNCH_END_TIME
DAILY_TIME_BUDGET_HOURS = cfg.DAILY_TIME_BUDGET_HOURS
DEFAULT_VISIT_DURATION_MIN = cfg.DEFAULT_VISIT_DURATION_MIN
DEFAULT_OPENING_TIME = cfg.DEFAULT_OPENING_TIME
DEFAULT_CLOSING_TIME = cfg.DEFAULT_CLOSING_TIME
AVERAGE_SPEED_KM_H = cfg.AVERAGE_SPEED_KM_H
HARD_VIOLATION_PENALTY = cfg.HARD_VIOLATION_PENALTY
USER_PREFERENCE_PENALTY_MULTIPLIER = cfg.USER_PREFERENCE_PENALTY_MULTIPLIER
DISTANCE_PENALTY_MULTIPLIER = cfg.DISTANCE_PENALTY_MULTIPLIER
PREFERRED_TAG_MIN_OVERALL = cfg.PREFERRED_TAG_MIN_OVERALL
PREFERRED_TAG_OVERALL_FRACTION = cfg.PREFERRED_TAG_OVERALL_FRACTION
MAX_DAILY_PREFERENCE_TAGS = cfg.MAX_DAILY_PREFERENCE_TAGS
PREFERRED_TAG_DAILY_PENALTY = cfg.PREFERRED_TAG_DAILY_PENALTY
PREFERRED_TAG_GLOBAL_MISSING_PENALTY = cfg.PREFERRED_TAG_GLOBAL_MISSING_PENALTY
PREFERRED_TAG_GLOBAL_REWARD = cfg.PREFERRED_TAG_GLOBAL_REWARD
PREFERRED_TAG_MAX_PER_DAY_CREDIT = cfg.PREFERRED_TAG_MAX_PER_DAY_CREDIT

CURRENT_DISTANCE_KM = None
CURRENT_DURATION_MIN = None
CURRENT_POI_INDEX = {}

EXCLUDED_TYPES = {
    "lodging",
    "hotel",
    "resort",
    "motel",
    "hostel",
    "guest_house",
    "restaurant",
    "cafe",
    "bar",
    "food",
    "bakery",
    "meal_takeaway",
    "meal_delivery",
    "night_club",
    "liquor_store",
    "store",
    "shop",
    "supermarket",
    "grocery_or_supermarket",
    "shopping_mall",
    "hospital",
    "pharmacy",
    "doctor",
    "dentist",
    "health",
    "gas_station",
    "parking",
    "car_rental",
    "taxi_stand",
    "bank",
    "atm",
    "finance",
    "insurance_agency",
    "real_estate_agency",
    "moving_company",
    "storage",
}

# Enhanced fitness constants from notebook
MUST_SEE_WPI_THRESHOLD = 0.85
DISTANCE_PENALTY_WEIGHT = 0.5
LUNCH_INVASION_PENALTY = 10.0
UNDERTIME_PENALTY_PER_MIN = 0.15
OVERTIME_PENALTY_PER_MIN = 0.20
WRONG_TIME_PENALTY = 8.0
EXTRA_WATERFALL_PENALTY = 30.0
PHYSICAL_FATIGUE_PENALTY = 5.0
TIME_UTILIZATION_WEIGHT = 2.0
ROUTE_LENGTH_BONUS_PER_POI = 0.05
MUST_SEE_REWARD = 0.3
MUST_SEE_NEIGHBOUR_REWARD = 0.15
CORRECT_TIME_REWARD = 0.1
DISTANCE_QUADRATIC_WEIGHT = 0.08
BACKTRACK_PENALTY_WEIGHT = 0.5
OVERTIME_HARD_THRESHOLD_MIN = 45
OVERTIME_STEEP_MULTIPLIER = 1.8
BEACH_STREAK_PENALTY = 20.0
# Beach visits should not overlap 12:00–16:00 (half-open visit [start,end) vs [scorch_start, scorch_end)).
BEACH_SCORCH_START = "12:00"
BEACH_SCORCH_END = "16:00"
BEACH_SCORCH_PENALTY_PER_MIN = 0.35
# Per flagged POI when Groq retry uses penalty-only mode (still in candidate pool).
ITINERARY_QA_FLAGGED_POI_PENALTY = 18.0
DAY_TYPE_COVERAGE_BONUS = 0.12
DAY_MISSING_TYPE_PENALTY = 2.0
BEACH_DOMINANCE_THRESHOLD = 0.45
BEACH_DOMINANCE_PENALTY_SCALE = 16.0

ALTERNATIVE_COUNT = 3
ALTERNATIVE_CANDIDATE_POOL = 9

PARK_KEYWORDS = {
    "park",
    "garden",
    "botanical",
    "eco park",
    "national park",
    "wildlife sanctuary",
    "nature park",
    "bird park",
    "amusement park",
    "theme park",
    "water park",
    "adventure park",
    "outdoor park",
    "recreation park",
    "playground",
}

PARK_WRONG_TIME_PENALTY = 6.0
PARK_CORRECT_TIME_REWARD = 0.08

NEARBY_DEDUP_KM = 0.5
NEARBY_REWARD_RADIUS_KM = 0.7
NEARBY_DUPLICATE_PENALTY = 4.0
NEARBY_SUGGESTION_RADIUS_KM = 2.0
NEARBY_SUGGESTIONS_PER_STOP = 3

# Scales per-POI average tag preference (-1..1) into reward / penalty terms.
TAG_PREFERENCE_SCALE = 0.2

WATERFALL_KEYWORDS = {
    "waterfall", "falls", "dhudh", "dudhsagar", "vajra", "vazra", "sakla", "arvalem",
}
BEACH_KEYWORDS = {
    "beach", "praia", "coast", "shore", "sea", "palolem", "vagator", "baga", "anjuna",
    "calangute", "candolim", "morjim", "arambol", "colva", "benaulim", "butterfly",
    "agonda", "patnem", "backwater",
}
STRENUOUS_KEYWORDS = {
    "waterfall", "falls", "trek", "fort", "hill", "ghat", "chorla", "peak", "climb", "hike",
}

# Wildlife / sanctuary-style stops (distinct from generic park for LLM tag preferences).
SANCTUARY_KEYWORDS = (
    "sanctuary",
    "wildlife",
    "bird sanctuary",
    "zoo",
    "aviary",
    "reptile",
)

SHOPPING_KEYWORDS = (
    "shopping mall",
    "mall",
    "bazaar",
    "flea market",
    "emporium",
    "market square",
    "handicraft",
)

VIEWPOINT_KEYWORDS = (
    "viewpoint",
    "sunset point",
    "vista",
    "overlook",
    "hill top",
    "hilltop",
)

SCENIC_KEYWORDS = (
    "scenic",
    "panorama",
    "panoramic",
    "vista",
    "viewpoint",
)

PEACEFUL_KEYWORDS = (
    "peaceful",
    "calm",
    "quiet",
    "serene",
    "tranquil",
)

RELAXATION_KEYWORDS = (
    "relax",
    "relaxation",
    "relaxing",
    "chill",
    "leisure",
)

PHOTOGRAPHY_KEYWORDS = (
    "photography",
    "photo",
    "photogenic",
    "sunset",
    "sunrise",
)

WATER_SPORTS_KEYWORDS = (
    "water sports",
    "watersports",
    "water-sports",
    "jet ski",
    "parasail",
    "parasailing",
    "banana boat",
)

FORT_KEYWORDS = (
    "fort",
    "fortress",
    "citadel",
)

TRAVEL_TYPES = frozenset(
    {"family", "solo", "duo", "couple", "friends", "group"}
)

PREFERENCE_CATEGORY_TAG_MAP = {
    "adventure": ("strenuous", "waterfall", "viewpoint", "water_sports", "fort"),
    "beaches": ("beach",),
    "food": (),
    "fort": ("fort", "historical", "strenuous"),
    "historical": ("historical",),
    "nature": ("nature",),
    "nightlife": (),
    "peaceful": ("peaceful", "relaxation", "park", "nature"),
    "photography": ("photography", "scenic", "viewpoint", "nature"),
    "relaxation": ("relaxation", "peaceful", "beach", "park"),
    "religious": ("religious",),
    "scenic": ("scenic", "viewpoint", "nature"),
    "shopping": ("shopping",),
    "water sports": ("water_sports", "beach"),
}


@dataclass(frozen=True)
class FitnessWeights:
    """Multipliers for each penalty group in delta (travel-type profiles).

    Baseline ``solo`` uses 1.0 on all terms, matching legacy single-profile behavior.
    """

    distance: float = 1.0
    hard_violation: float = 1.0
    undertime: float = 1.0
    overtime: float = 1.0
    wrong_time: float = 1.0
    waterfall: float = 1.0
    fatigue: float = 1.0
    type_coverage: float = 1.0
    beach_dominance: float = 1.0


@dataclass(frozen=True)
class PreferenceState:
    required_day_tags: frozenset[str]
    global_targets: dict[str, int]
    global_counts: dict[str, int]
    remaining_days: int
    remaining_available_days: dict[str, int]


def get_fitness_weights(travel_type: str | None) -> FitnessWeights:
    """Return penalty multipliers for the given travel type (invalid values → solo)."""
    key = (travel_type or "solo").lower()
    if key not in TRAVEL_TYPES:
        key = "solo"
    profiles: dict[str, FitnessWeights] = {
        "solo": FitnessWeights(),
        "family": FitnessWeights(
            distance=1.1,
            hard_violation=1.15,
            overtime=1.25,
            wrong_time=0.95,
            waterfall=1.15,
            fatigue=1.45,
            type_coverage=1.05,
            beach_dominance=0.9,
        ),
        "duo": FitnessWeights(
            distance=0.98,
            overtime=1.08,
            fatigue=0.95,
        ),
        "friends": FitnessWeights(
            distance=0.92,
            wrong_time=0.92,
            fatigue=0.9,
            overtime=1.05,
        ),
        "couple": FitnessWeights(
            distance=0.96,
            overtime=1.05,
            fatigue=0.96,
            wrong_time=0.98,
        ),
        "group": FitnessWeights(
            distance=0.88,
            wrong_time=0.9,
            fatigue=0.85,
            overtime=1.1,
            type_coverage=1.03,
        ),
    }
    return profiles[key]


def get_default_tag_adjustments(travel_type: str | None) -> dict[str, float]:
    """Per-travel-type tag prefs merged into GA fitness (no LLM required).

    Negative values penalize routes that include POIs with those tags; positive rewards them.
    This addresses cases like *family*: deprioritize strenuous waterfalls even if the user
    text still mentions waterfalls (Module1 may keep those POIs in the pool).
    """
    key = (travel_type or "solo").lower()
    if key not in TRAVEL_TYPES:
        key = "solo"
    profiles: dict[str, dict[str, float]] = {
        "solo": {},
        "family": {
            # Strongly discourage hiking-style waterfalls; prefer easy nature (parks, sanctuaries).
            "waterfall": -0.78,
            "strenuous": -0.68,
            "park": 0.42,
            "sanctuary": 0.52,
            "beach": 0.18,
        },
        "duo": {
            "beach": 0.22,
            "historical": 0.18,
            "religious": 0.1,
        },
        "couple": {
            "beach": 0.28,
            "historical": 0.2,
            "viewpoint": 0.35,
            "religious": 0.15,
            "park": 0.12,
        },
        "friends": {
            "beach": 0.2,
            "park": 0.15,
            "historical": 0.1,
        },
        "group": {
            "beach": 0.15,
            "park": 0.2,
            "religious": 0.12,
            "shopping": 0.12,
        },
    }
    return dict(profiles[key])


class POI:
    def __init__(
        self,
        name,
        lat,
        lon,
        normalized_popularity,
        place_id=None,
        rating=3.0,
        user_ratings_total=0,
        poi_type="",
        categories=None,
    ):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.normalized_popularity = normalized_popularity
        self.place_id = place_id or name
        self.rating = rating
        self.user_ratings_total = user_ratings_total
        self.type = poi_type or ""
        self.categories = categories or []
        self.opening_time = DEFAULT_OPENING_TIME
        self.closing_time = DEFAULT_CLOSING_TIME
        self.visit_duration_min = DEFAULT_VISIT_DURATION_MIN

    def __repr__(self):
        return f"POI({self.name}, WPI={self.normalized_popularity:.3f})"


class Individual:
    """Represents a single route chromosome in the GA population."""

    def __init__(
        self,
        route,
        candidate_pois,
        fitness_weights: FitnessWeights | None = None,
        tag_adjustments: dict[str, float] | None = None,
        penalty_place_ids: frozenset[str] | None = None,
        preference_state: PreferenceState | None = None,
    ):
        self.route = route.copy() if isinstance(route, list) else list(route)
        self.candidate_pois = candidate_pois
        self.fitness_weights = fitness_weights or get_fitness_weights("solo")
        self.tag_adjustments = tag_adjustments if tag_adjustments is not None else {}
        self.penalty_place_ids = (
            penalty_place_ids if penalty_place_ids is not None else frozenset()
        )
        self.preference_state = preference_state
        self.fitness = None
        self.evaluation = None
        self.distance_km = 0.0
        self.travel_time_min = 0.0

    def evaluate(self, start_time=TOUR_START_TIME):
        self.evaluation = evaluate_fitness(
            self.route,
            start_time,
            weights=self.fitness_weights,
            tag_adjustments=self.tag_adjustments,
            penalty_place_ids=self.penalty_place_ids,
            preference_state=self.preference_state,
        )
        self.fitness = self.evaluation.fitness
        self.distance_km = self.evaluation.total_distance_km
        self.travel_time_min = self.evaluation.total_travel_time_min
        return self.fitness

    def copy(self):
        new_ind = Individual(
            self.route,
            self.candidate_pois,
            self.fitness_weights,
            self.tag_adjustments,
            self.penalty_place_ids,
            self.preference_state,
        )
        new_ind.fitness = self.fitness
        new_ind.evaluation = self.evaluation
        new_ind.distance_km = self.distance_km
        new_ind.travel_time_min = self.travel_time_min
        return new_ind

    def __repr__(self):
        fit = f"{self.fitness:.3f}" if self.fitness is not None else "None"
        return f"Individual(route_len={len(self.route)}, fitness={fit})"


@dataclass
class RouteEvaluation:
    poi_value_sum: float = 0.0
    distance_penalty: float = 0.0
    user_pref_penalty: float = 0.0
    hard_violation_penalty: float = 0.0
    must_see_penalty: float = 0.0
    restaurant_penalty: float = 0.0
    undertime_penalty: float = 0.0
    overtime_penalty: float = 0.0
    wrong_time_penalty: float = 0.0
    waterfall_penalty: float = 0.0
    fatigue_penalty: float = 0.0
    time_utilization_bonus: float = 0.0
    route_length_bonus: float = 0.0
    must_see_reward: float = 0.0
    neighbour_reward: float = 0.0
    correct_time_reward: float = 0.0
    total_travel_time_min: float = 0.0
    total_visit_time_min: float = 0.0
    total_distance_km: float = 0.0
    closed_poi_count: int = 0
    lunch_invasion_count: int = 0
    overtime_minutes: float = 0.0
    undertime_minutes: float = 0.0
    waterfall_count: int = 0
    strenuous_count: int = 0
    beach_streak_violations: int = 0
    type_coverage_bonus: float = 0.0
    type_coverage_penalty: float = 0.0
    beach_dominance_penalty: float = 0.0
    total_time_min: float = 0.0
    timeline: list = None
    nearby_alternatives: dict = None
    delta: float = 0.0
    fitness: float = 0.0
    total_reward: float = 0.0
    tag_preference_reward: float = 0.0
    beach_scorch_overlap_min: float = 0.0
    itinerary_qa_place_penalty: float = 0.0
    preference_daily_missing: int = 0
    preference_daily_penalty: float = 0.0
    preference_global_penalty: float = 0.0
    preference_global_reward: float = 0.0


def load_pois_for_day(df, day):
    day_data = df[df["day"] == day]
    day_data = day_data.sort_values("normalized_popularity", ascending=False).copy()
    high_value_ids = set(day_data.head(6).get("place_id", day_data.head(6)["name"]).astype(str).tolist())
    top_tier_ids = set(day_data.head(3).get("place_id", day_data.head(3)["name"]).astype(str).tolist())

    pois = []
    for _, row in day_data.iterrows():
        poi = POI(
            name=row["name"],
            lat=float(row["latitude"]),
            lon=float(row["longitude"]),
            normalized_popularity=float(row["normalized_popularity"]),
            place_id=str(row.get("place_id", row["name"])),
            rating=float(row.get("rating", 4.0)),
            user_ratings_total=float(row.get("user_ratings_total", 0.0)),
            poi_type=str(row.get("types", row.get("type", ""))),
            categories=row.get("categories", []),
        )

        poi_id = str(row.get("place_id", row["name"]))
        if _religious_subtype(poi) == "temple" and poi.normalized_popularity < 0.86:
            poi.visit_duration_min = 30
        elif poi_id in top_tier_ids:
            poi.visit_duration_min = 120
        elif poi_id in high_value_ids:
            poi.visit_duration_min = 90

        pois.append(poi)

    return pois


def haversine_distance(coord1, coord2):
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return 6371.0 * c


def time_to_minutes(time_str):
    h, m = map(int, time_str.split(":"))
    return h * 60 + m


def minutes_to_time(total_minutes):
    total_minutes = int(total_minutes)
    h = (total_minutes // 60) % 24
    m = total_minutes % 60
    return f"{h:02d}:{m:02d}"


PARK_TIME_START_MIN = time_to_minutes("10:00")
PARK_TIME_END_MIN = time_to_minutes("16:00")
TOUR_START_MINUTES = time_to_minutes(TOUR_START_TIME)
TOUR_END_MINUTES = time_to_minutes(TOUR_END_TIME)
DAILY_BUDGET_MIN = int(DAILY_TIME_BUDGET_HOURS * 60)
AFTERNOON_END_MIN = time_to_minutes("15:00")
BEACH_SCORCH_START_MIN = time_to_minutes(BEACH_SCORCH_START)
BEACH_SCORCH_END_MIN = time_to_minutes(BEACH_SCORCH_END)


def build_osrm_matrices(pois, osrm_url=OSRM_BASE_URL):
    if len(pois) == 0:
        return np.zeros((0, 0)), np.zeros((0, 0))
    coords_str = ";".join([f"{poi.lon},{poi.lat}" for poi in pois])
    url = f"{osrm_url}/table/v1/driving/{coords_str}?annotations=distance,duration"
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    data = response.json()
    if data.get("code") != "Ok":
        raise RuntimeError(f"OSRM Table API failed: {data}")
    return np.array(data["distances"], dtype=float) / 1000.0, np.array(
        data["durations"], dtype=float
    ) / 60.0


def build_haversine_matrices(pois):
    n = len(pois)
    distance_matrix = np.zeros((n, n), dtype=float)
    duration_matrix = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            d = haversine_distance((pois[i].lat, pois[i].lon), (pois[j].lat, pois[j].lon))
            distance_matrix[i, j] = d
            duration_matrix[i, j] = (d / AVERAGE_SPEED_KM_H) * 60
    return distance_matrix, duration_matrix


def prepare_day_matrices(pois, use_osrm=True):
    global CURRENT_DISTANCE_KM, CURRENT_DURATION_MIN, CURRENT_POI_INDEX
    CURRENT_POI_INDEX = {}
    for i, poi in enumerate(pois):
        CURRENT_POI_INDEX[id(poi)] = i
        place_id = getattr(poi, "place_id", None)
        if place_id is not None:
            CURRENT_POI_INDEX[place_id] = i
    if use_osrm:
        try:
            CURRENT_DISTANCE_KM, CURRENT_DURATION_MIN = build_osrm_matrices(pois)
            return
        except Exception:
            pass
    CURRENT_DISTANCE_KM, CURRENT_DURATION_MIN = build_haversine_matrices(pois)


def _lookup_poi_index(poi) -> int | None:
    """Resolve POI index in current matrix, supporting id and place_id matching."""
    idx = CURRENT_POI_INDEX.get(id(poi))
    if idx is not None:
        return idx

    place_id = getattr(poi, "place_id", None)
    if place_id is not None:
        idx = CURRENT_POI_INDEX.get(place_id)
        if idx is not None:
            return idx
    return None


def _fallback_distance_km(poi1, poi2) -> float:
    return float(haversine_distance((poi1.lat, poi1.lon), (poi2.lat, poi2.lon)))


def _fallback_duration_min(distance_km: float) -> float:
    return float((distance_km / AVERAGE_SPEED_KM_H) * 60)


def get_cached_distance(poi1, poi2):
    i = _lookup_poi_index(poi1)
    j = _lookup_poi_index(poi2)

    if (
        i is None
        or j is None
        or CURRENT_DISTANCE_KM is None
        or i >= CURRENT_DISTANCE_KM.shape[0]
        or j >= CURRENT_DISTANCE_KM.shape[1]
    ):
        return _fallback_distance_km(poi1, poi2)

    return float(CURRENT_DISTANCE_KM[i, j])


def calculate_travel_time(poi1, poi2):
    i = _lookup_poi_index(poi1)
    j = _lookup_poi_index(poi2)

    if (
        i is None
        or j is None
        or CURRENT_DURATION_MIN is None
        or i >= CURRENT_DURATION_MIN.shape[0]
        or j >= CURRENT_DURATION_MIN.shape[1]
    ):
        distance_km = get_cached_distance(poi1, poi2)
        return _fallback_duration_min(distance_km)

    return float(CURRENT_DURATION_MIN[i, j])


def select_top_pois_for_optimization(pois, max_candidates=50, diversity_tracker=None):
    original_count = len(pois)
    tourist_pois = [p for p in pois if not _poi_is_excluded(p)]
    if not tourist_pois:
        return []

    # 1) Exact id dedup
    seen_ids = set()
    id_deduped = []
    for poi in tourist_pois:
        key = getattr(poi, "place_id", None) or f"{poi.name}_{poi.lat:.5f}_{poi.lon:.5f}"
        if key not in seen_ids:
            seen_ids.add(key)
            id_deduped.append(poi)

    # 2) Keep best WPI first
    id_deduped.sort(
        key=lambda p: (p.normalized_popularity, p.rating, p.user_ratings_total),
        reverse=True,
    )

    # 3) Near-duplicate dedup with stricter rule:
    #    only drop if BOTH names are similar AND coordinates are very close.
    fuzzy_deduped = []
    for candidate in id_deduped:
        near_dup = False
        for accepted in fuzzy_deduped:
            if _names_are_similar(candidate.name, accepted.name) and _coords_are_close(
                candidate.lat, candidate.lon, accepted.lat, accepted.lon
            ):
                near_dup = True
                break
        if not near_dup:
            fuzzy_deduped.append(candidate)

    diverse_pois = _enforce_category_diversity(fuzzy_deduped, max_per_type=4)
    if diversity_tracker is not None:
        diverse_pois = _rebalance_global_mix(diverse_pois, diversity_tracker)
        diverse_pois = _rebalance_religious_mix(diverse_pois, diversity_tracker)
    final = diverse_pois[: min(max_candidates, len(diverse_pois))]
    if len(final) < min(6, original_count):
        # If dedup became too aggressive for a cluster, relax by filling from sorted pool.
        used = {id(p) for p in final}
        for p in id_deduped:
            if id(p) not in used:
                final.append(p)
            if len(final) >= min(max_candidates, len(id_deduped)):
                break
    return final[:max_candidates]


def _names_are_similar(name1: str, name2: str, threshold: float = 0.82) -> bool:
    n1 = name1.lower().strip()
    n2 = name2.lower().strip()
    if n1 == n2:
        return True
    if n1 in n2 or n2 in n1:
        return True
    return SequenceMatcher(None, n1, n2).ratio() > threshold


def resolve_qa_flagged_place_ids(
    problematic_places: list[Any],
    route_stops: list[dict[str, Any]],
    day_pois: list[POI],
) -> tuple[frozenset[str], list[dict[str, Any]]]:
    """
    Map Groq ``problematic_places`` entries to ``place_id`` values for GA exclude/penalty.

    Matches each suggestion to route stop names first, then to the day's POI pool.
    """
    if not problematic_places:
        return frozenset(), []

    def _extract_label(item: Any) -> str:
        if isinstance(item, dict):
            return str(item.get("name") or item.get("place") or "").strip()
        return str(item).strip()

    pool_by_id = {str(p.place_id): p for p in day_pois}
    resolved: list[dict[str, Any]] = []
    seen: set[str] = set()

    for raw in problematic_places:
        label = _extract_label(raw)
        if not label:
            continue

        best_stop: dict[str, Any] | None = None
        for stop in route_stops:
            sname = str(stop.get("name") or "")
            if sname.lower().strip() == label.lower().strip():
                best_stop = stop
                break
        if best_stop is None:
            best_ratio = 0.0
            for stop in route_stops:
                sname = str(stop.get("name") or "")
                if not sname:
                    continue
                r = SequenceMatcher(None, label.lower(), sname.lower()).ratio()
                if r > best_ratio:
                    best_ratio = r
                    best_stop = stop
            if best_stop is not None and best_ratio < 0.55:
                best_stop = None

        pid: str | None = None
        via = ""
        matched_name = ""
        if best_stop is not None:
            pid = str(best_stop.get("poi_id") or "")
            matched_name = str(best_stop.get("name") or "")
            via = "route_stop"
        if not pid or pid not in pool_by_id:
            best_poi: POI | None = None
            best_r = 0.0
            for p in day_pois:
                if _names_are_similar(label, p.name, threshold=0.72):
                    r = SequenceMatcher(None, label.lower(), p.name.lower()).ratio()
                    if r > best_r:
                        best_r = r
                        best_poi = p
            if best_poi is not None and best_r >= 0.55:
                pid = str(best_poi.place_id)
                matched_name = best_poi.name
                via = "day_pool"

        if pid and pid in pool_by_id and pid not in seen:
            seen.add(pid)
            resolved.append(
                {
                    "qa_label": label,
                    "place_id": pid,
                    "matched_name": matched_name,
                    "via": via,
                }
            )

    return frozenset(seen), resolved


def _coords_are_close(lat1, lon1, lat2, lon2, threshold_km: float = 0.05) -> bool:
    return haversine_distance((lat1, lon1), (lat2, lon2)) < threshold_km


def _poi_is_excluded(poi) -> bool:
    poi_type = getattr(poi, "type", "") or ""
    poi_type = str(poi_type).lower().strip()
    if poi_type in EXCLUDED_TYPES:
        return True
    name_lower = poi.name.lower()
    name_keywords = [
        "hotel",
        "resort",
        "hostel",
        "inn ",
        " inn",
        "lodge",
        "villa ",
        "restaurant",
        " cafe",
        "bistro",
        "shack",
        "bar ",
        " bar",
        "hospital",
        "clinic",
        "pharmacy",
        "atm",
        "bank",
    ]
    return any(kw in name_lower for kw in name_keywords)


def _enforce_category_diversity(pois, max_per_type: int = 4) -> list:
    type_counts = {}
    diverse = []
    deferred = []
    for poi in pois:
        poi_type = getattr(poi, "type", "unknown") or "unknown"
        count = type_counts.get(poi_type, 0)
        if count < max_per_type:
            diverse.append(poi)
            type_counts[poi_type] = count + 1
        else:
            deferred.append(poi)
    diverse.extend(deferred)
    return diverse


def _religious_subtype(poi) -> str:
    text = f"{poi.name} {getattr(poi, 'type', '')}".lower()
    church_markers = ["church", "basilica", "cathedral", "chapel", "convent"]
    temple_markers = ["temple", "mandir", "mahadev", "shri", "devasthan"]
    if any(k in text for k in church_markers):
        return "church"
    if any(k in text for k in temple_markers):
        return "temple"
    return ""


def _rebalance_religious_mix(candidates, diversity_tracker):
    if not candidates:
        return candidates
    churches = [p for p in candidates if _religious_subtype(p) == "church"]
    temples = [p for p in candidates if _religious_subtype(p) == "temple"]
    if not churches or not temples:
        return candidates

    temple_seen = int(diversity_tracker.get("temple", 0))
    church_seen = int(diversity_tracker.get("church", 0))
    wanted = "church" if temple_seen > church_seen else "temple"
    if abs(temple_seen - church_seen) < 2:
        return candidates

    wanted_items = churches if wanted == "church" else temples
    others = [p for p in candidates if _religious_subtype(p) != wanted]
    max_boost = min(3, len(wanted_items))
    reordered = wanted_items[:max_boost] + others
    return reordered[: len(candidates)]


def _poi_balance_tags(poi) -> set:
    text = f"{poi.name} {getattr(poi, 'type', '')}".lower()
    tags = set()
    if any(k in text for k in BEACH_KEYWORDS):
        tags.add("beach")
    if any(k in text for k in WATERFALL_KEYWORDS):
        tags.add("waterfall")
        tags.add("nature")
    if any(k in text for k in WATER_SPORTS_KEYWORDS):
        tags.add("water_sports")
    if any(k in text for k in SANCTUARY_KEYWORDS):
        tags.add("sanctuary")
        tags.add("nature")
    if any(k in text for k in PARK_KEYWORDS):
        tags.add("park")
        tags.add("nature")
    if any(k in text for k in SCENIC_KEYWORDS):
        tags.add("scenic")
    if any(k in text for k in PEACEFUL_KEYWORDS):
        tags.add("peaceful")
    if any(k in text for k in RELAXATION_KEYWORDS):
        tags.add("relaxation")
    if any(k in text for k in PHOTOGRAPHY_KEYWORDS):
        tags.add("photography")
    if any(k in text for k in SHOPPING_KEYWORDS):
        tags.add("shopping")
    if any(k in text for k in VIEWPOINT_KEYWORDS):
        tags.add("viewpoint")
    if any(k in text for k in ["museum", "heritage", "ancient", "cathedral", "basilica"]):
        tags.add("historical")
    if any(k in text for k in FORT_KEYWORDS):
        tags.add("fort")
        tags.add("historical")
    subtype = _religious_subtype(poi)
    if subtype:
        tags.add("religious")
        tags.add(subtype)
    if not tags:
        tags.add("other")
    return tags


def _rebalance_global_mix(candidates, diversity_tracker):
    if not candidates or not diversity_tracker:
        return candidates
    all_counts = [v for k, v in diversity_tracker.items() if k not in {"church", "temple"}]
    if not all_counts:
        return candidates
    target = min(all_counts)
    scored = []
    for poi in candidates:
        tags = _poi_balance_tags(poi)
        underrep_bonus = 0.0
        for t in tags:
            if t in diversity_tracker:
                underrep_bonus += max(0.0, (target + 2 - diversity_tracker[t])) * 0.08
        score = float(poi.normalized_popularity) + underrep_bonus
        scored.append((score, poi))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored]


def _classify_poi(poi) -> set:
    tags = set()
    name = poi.name.lower()
    ptype = (getattr(poi, "type", "") or "").lower()
    combined = name + " " + ptype
    if any(kw in combined for kw in WATERFALL_KEYWORDS):
        tags.add("waterfall")
        tags.add("strenuous")
    if any(kw in combined for kw in BEACH_KEYWORDS):
        tags.add("beach")
    if any(kw in combined for kw in WATER_SPORTS_KEYWORDS):
        tags.add("water_sports")
    if any(kw in combined for kw in STRENUOUS_KEYWORDS):
        tags.add("strenuous")
    if any(kw in combined for kw in PARK_KEYWORDS):
        tags.add("park")
    if any(kw in combined for kw in SANCTUARY_KEYWORDS):
        tags.add("sanctuary")
    if any(kw in combined for kw in SHOPPING_KEYWORDS):
        tags.add("shopping")
    if any(kw in combined for kw in VIEWPOINT_KEYWORDS):
        tags.add("viewpoint")
    if any(kw in combined for kw in SCENIC_KEYWORDS):
        tags.add("scenic")
    if any(kw in combined for kw in PEACEFUL_KEYWORDS):
        tags.add("peaceful")
    if any(kw in combined for kw in RELAXATION_KEYWORDS):
        tags.add("relaxation")
    if any(kw in combined for kw in PHOTOGRAPHY_KEYWORDS):
        tags.add("photography")
    if any(kw in combined for kw in FORT_KEYWORDS):
        tags.add("fort")
    return tags


def _resolve_preference_tags(
    positive_interests: list[str],
) -> tuple[list[str], list[str]]:
    tags: list[str] = []
    ignored: list[str] = []
    for interest in positive_interests:
        mapped = PREFERENCE_CATEGORY_TAG_MAP.get(str(interest).lower(), ())
        if not mapped:
            ignored.append(str(interest))
            continue
        for tag in mapped:
            if tag not in tags:
                tags.append(tag)
    return tags, ignored


def _collect_preference_tags_for_pois(pois: list[POI]) -> set[str]:
    tags: set[str] = set()
    for poi in pois:
        tags.update(_poi_balance_tags(poi))
        tags.update(_classify_poi(poi))
    return tags


def _count_preference_tags_in_route(route: list[POI]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for poi in route:
        tags = _poi_balance_tags(poi) | _classify_poi(poi)
        for tag in tags:
            counts[tag] = counts.get(tag, 0) + 1
    return counts


def _build_preference_targets(
    preference_tags: list[str],
    day_tag_availability: dict[int, set[str]],
    num_days: int,
) -> dict[str, int]:
    if not preference_tags:
        return {}
    targets: dict[str, int] = {}
    min_target = max(
        PREFERRED_TAG_MIN_OVERALL,
        int(ceil(num_days * PREFERRED_TAG_OVERALL_FRACTION)),
    )
    for tag in preference_tags:
        available_days = sum(1 for tags in day_tag_availability.values() if tag in tags)
        if available_days <= 0:
            targets[tag] = 0
            continue
        targets[tag] = min(available_days, min_target)
    return targets


def _select_daily_required_tags(
    preference_tags: list[str],
    day_tags: set[str],
) -> list[str]:
    if not preference_tags:
        return []
    required = [tag for tag in preference_tags if tag in day_tags]
    return required[:MAX_DAILY_PREFERENCE_TAGS]


def _build_remaining_available_days(
    day_list: list[int],
    day_idx: int,
    day_tag_availability: dict[int, set[str]],
    preference_tags: list[str],
) -> dict[str, int]:
    remaining_days = day_list[day_idx:]
    remaining: dict[str, int] = {tag: 0 for tag in preference_tags}
    for day in remaining_days:
        tags = day_tag_availability.get(day, set())
        for tag in preference_tags:
            if tag in tags:
                remaining[tag] += 1
    return remaining


def _is_must_see(poi) -> bool:
    return poi.normalized_popularity >= MUST_SEE_WPI_THRESHOLD


def _get_neighbours(poi, all_pois_in_route, radius_km: float = 5.0) -> list:
    neighbours = []
    for other in all_pois_in_route:
        if other is poi:
            continue
        dist = haversine_distance((poi.lat, poi.lon), (other.lat, other.lon))
        if dist <= radius_km:
            neighbours.append(other)
    return neighbours


def _dedupe_route_by_distance_keep_high_wpi(route, threshold_km=NEARBY_DEDUP_KM):
    core = []
    nearby = {}
    for poi in route:
        merged = False
        for i, chosen in enumerate(core):
            d = haversine_distance((poi.lat, poi.lon), (chosen.lat, chosen.lon))
            if d <= threshold_km:
                winner, loser = (
                    (poi, chosen)
                    if poi.normalized_popularity > chosen.normalized_popularity
                    else (chosen, poi)
                )
                if winner is poi:
                    core[i] = poi
                key = id(winner)
                nearby.setdefault(key, []).append(
                    {
                        "name": loser.name,
                        "distance_km": round(d, 3),
                        "wpi": round(loser.normalized_popularity, 3),
                    }
                )
                merged = True
                break
        if not merged:
            core.append(poi)
    return core, nearby


def evaluate_fitness(
    route,
    start_time=TOUR_START_TIME,
    weights: FitnessWeights | None = None,
    tag_adjustments: dict[str, float] | None = None,
    penalty_place_ids: frozenset[str] | None = None,
    preference_state: PreferenceState | None = None,
):
    w = weights or FitnessWeights()
    tag_adj = tag_adjustments if tag_adjustments else {}
    penalize_ids = penalty_place_ids if penalty_place_ids else frozenset()
    eval_result = RouteEvaluation(timeline=[])
    if not route:
        return eval_result

    core_route, nearby_alts = _dedupe_route_by_distance_keep_high_wpi(route)
    eval_result.nearby_alternatives = nearby_alts

    current_time_min = time_to_minutes(start_time)
    lunch_start_min = time_to_minutes(LUNCH_START_TIME)
    lunch_end_min = time_to_minutes(LUNCH_END_TIME)
    poi_tags = {id(poi): _classify_poi(poi) for poi in core_route}
    eval_result.waterfall_count = sum(
        1 for poi in core_route if "waterfall" in poi_tags[id(poi)]
    )
    eval_result.strenuous_count = sum(
        1 for poi in core_route if "strenuous" in poi_tags[id(poi)]
    )
    segment_distances = []

    for i, poi in enumerate(core_route):
        tags = poi_tags[id(poi)]
        if i > 0:
            prev = core_route[i - 1]
            d = get_cached_distance(prev, poi)
            t = calculate_travel_time(prev, poi)
            current_time_min += t
            eval_result.total_travel_time_min += t
            eval_result.total_distance_km += d
            eval_result.distance_penalty += (
                DISTANCE_PENALTY_WEIGHT * d + DISTANCE_QUADRATIC_WEIGHT * (d**2)
            )
            segment_distances.append(d)

        if lunch_start_min <= current_time_min < lunch_end_min:
            eval_result.lunch_invasion_count += 1
            eval_result.hard_violation_penalty += LUNCH_INVASION_PENALTY
            current_time_min = lunch_end_min

        arrival_time = current_time_min
        open_min = time_to_minutes(poi.opening_time)
        close_min = time_to_minutes(poi.closing_time)
        if current_time_min < open_min:
            current_time_min = open_min
        elif current_time_min >= close_min:
            eval_result.closed_poi_count += 1
            eval_result.hard_violation_penalty += HARD_VIOLATION_PENALTY

        visit_start = current_time_min
        visit_end = current_time_min + poi.visit_duration_min
        current_time_min = visit_end
        eval_result.total_visit_time_min += poi.visit_duration_min
        if visit_end > close_min and visit_start < close_min:
            eval_result.hard_violation_penalty += HARD_VIOLATION_PENALTY * 0.5

        if penalize_ids and str(poi.place_id) in penalize_ids:
            eval_result.itinerary_qa_place_penalty += ITINERARY_QA_FLAGGED_POI_PENALTY
            eval_result.wrong_time_penalty += ITINERARY_QA_FLAGGED_POI_PENALTY

        if "waterfall" in tags:
            if visit_start <= time_to_minutes("11:00"):
                eval_result.correct_time_reward += CORRECT_TIME_REWARD
            elif visit_start >= AFTERNOON_END_MIN:
                eval_result.wrong_time_penalty += WRONG_TIME_PENALTY
        if "beach" in tags:
            # Overlap minutes between visit [visit_start, visit_end) and scorch [12:00, 16:00).
            scorch_lo = max(visit_start, BEACH_SCORCH_START_MIN)
            scorch_hi = min(visit_end, BEACH_SCORCH_END_MIN)
            overlap = max(0.0, float(scorch_hi - scorch_lo))
            if overlap > 0:
                eval_result.beach_scorch_overlap_min += overlap
                eval_result.wrong_time_penalty += overlap * BEACH_SCORCH_PENALTY_PER_MIN
            elif visit_end <= BEACH_SCORCH_START_MIN or visit_start >= BEACH_SCORCH_END_MIN:
                if visit_start >= BEACH_SCORCH_END_MIN:
                    eval_result.correct_time_reward += CORRECT_TIME_REWARD * 1.5
                else:
                    eval_result.correct_time_reward += CORRECT_TIME_REWARD * 0.5
            if i >= 2:
                prev1_tags = poi_tags[id(core_route[i - 1])]
                prev2_tags = poi_tags[id(core_route[i - 2])]
                if "beach" in prev1_tags and "beach" in prev2_tags:
                    eval_result.beach_streak_violations += 1
                    eval_result.wrong_time_penalty += BEACH_STREAK_PENALTY
        if "park" in tags:
            if PARK_TIME_START_MIN <= visit_start <= PARK_TIME_END_MIN:
                eval_result.correct_time_reward += PARK_CORRECT_TIME_REWARD
            else:
                eval_result.wrong_time_penalty += PARK_WRONG_TIME_PENALTY

        eval_result.timeline.append(
            (
                poi,
                minutes_to_time(int(arrival_time)),
                minutes_to_time(int(visit_start)),
                minutes_to_time(int(visit_end)),
            )
        )

    eval_result.total_time_min = current_time_min - TOUR_START_MINUTES
    if current_time_min > TOUR_END_MINUTES:
        eval_result.overtime_minutes = current_time_min - TOUR_END_MINUTES
        base_over = eval_result.overtime_minutes * OVERTIME_PENALTY_PER_MIN
        if eval_result.overtime_minutes > OVERTIME_HARD_THRESHOLD_MIN:
            base_over *= OVERTIME_STEEP_MULTIPLIER
        eval_result.overtime_penalty = base_over

    undertime_buffer_min = 45
    time_remaining = TOUR_END_MINUTES - current_time_min
    if time_remaining > undertime_buffer_min:
        eval_result.undertime_minutes = time_remaining - undertime_buffer_min
        eval_result.undertime_penalty = (
            eval_result.undertime_minutes * UNDERTIME_PENALTY_PER_MIN
        )
    if eval_result.waterfall_count > 1:
        eval_result.waterfall_penalty = (
            eval_result.waterfall_count - 1
        ) * EXTRA_WATERFALL_PENALTY
    if eval_result.strenuous_count > 2:
        eval_result.fatigue_penalty = (
            eval_result.strenuous_count - 2
        ) * PHYSICAL_FATIGUE_PENALTY

    if len(segment_distances) >= 2:
        avg_d = sum(segment_distances) / len(segment_distances)
        peaks = sum(max(0.0, d - avg_d) for d in segment_distances)
        eval_result.wrong_time_penalty += peaks * BACKTRACK_PENALTY_WEIGHT

    for i in range(len(core_route)):
        for j in range(i + 1, len(core_route)):
            d = haversine_distance(
                (core_route[i].lat, core_route[i].lon),
                (core_route[j].lat, core_route[j].lon),
            )
            if d <= NEARBY_DEDUP_KM:
                eval_result.wrong_time_penalty += NEARBY_DUPLICATE_PENALTY

    route_type_presence = {
        "historical": 0,
        "religious": 0,
        "nature": 0,
        "beach": 0,
        "waterfall": 0,
        "park": 0,
    }
    for poi in core_route:
        for tag in _poi_balance_tags(poi):
            if tag in route_type_presence:
                route_type_presence[tag] += 1

    covered_types = sum(1 for v in route_type_presence.values() if v > 0)
    eval_result.type_coverage_bonus = covered_types * DAY_TYPE_COVERAGE_BONUS
    missing_types = len(route_type_presence) - covered_types
    eval_result.type_coverage_penalty = missing_types * DAY_MISSING_TYPE_PENALTY

    beach_ratio = (
        route_type_presence["beach"] / len(core_route) if core_route else 0.0
    )
    if beach_ratio > BEACH_DOMINANCE_THRESHOLD:
        eval_result.beach_dominance_penalty = (
            (beach_ratio - BEACH_DOMINANCE_THRESHOLD) * BEACH_DOMINANCE_PENALTY_SCALE
        )

    route_pref_counts = _count_preference_tags_in_route(core_route)
    route_pref_tags = set(route_pref_counts.keys())
    if preference_state:
        required_tags = preference_state.required_day_tags
        if required_tags:
            missing = [t for t in required_tags if t not in route_pref_tags]
            eval_result.preference_daily_missing = len(missing)
            eval_result.preference_daily_penalty = (
                len(missing) * PREFERRED_TAG_DAILY_PENALTY
            )
        remaining_days = max(1, preference_state.remaining_days)
        remaining_avail = preference_state.remaining_available_days or {}
        for tag, target in preference_state.global_targets.items():
            if target <= 0:
                continue
            avail_days = remaining_avail.get(tag, remaining_days)
            if avail_days <= 0:
                continue
            current = preference_state.global_counts.get(tag, 0)
            shortfall = max(0, target - current)
            if shortfall <= 0:
                continue
            if tag in route_pref_tags:
                credit = min(
                    route_pref_counts.get(tag, 0), PREFERRED_TAG_MAX_PER_DAY_CREDIT
                )
                if credit:
                    eval_result.preference_global_reward += (
                        credit
                        * PREFERRED_TAG_GLOBAL_REWARD
                        * (shortfall / avail_days)
                    )
            else:
                eval_result.preference_global_penalty += (
                    PREFERRED_TAG_GLOBAL_MISSING_PENALTY * (shortfall / avail_days)
                )

    eval_result.poi_value_sum = sum(poi.normalized_popularity for poi in core_route)
    time_used = min(eval_result.total_time_min, DAILY_BUDGET_MIN)
    time_ratio = time_used / DAILY_BUDGET_MIN if DAILY_BUDGET_MIN else 0.0
    eval_result.time_utilization_bonus = time_ratio * TIME_UTILIZATION_WEIGHT
    target_pois = 8 if DAILY_BUDGET_MIN >= 480 else 6
    length_gap = abs(len(core_route) - target_pois)
    eval_result.route_length_bonus = max(0.0, 0.6 - 0.08 * length_gap)
    must_see_pois = [p for p in core_route if _is_must_see(p)]
    eval_result.must_see_reward = len(must_see_pois) * MUST_SEE_REWARD
    neighbour_ids = set()
    for anchor in must_see_pois:
        for n in _get_neighbours(anchor, core_route, radius_km=5.0):
            neighbour_ids.add(id(n))
    eval_result.neighbour_reward = len(neighbour_ids) * MUST_SEE_NEIGHBOUR_REWARD

    tag_pref_reward = 0.0
    tag_pref_penalty = 0.0
    if tag_adj:
        for poi in core_route:
            tags = _poi_balance_tags(poi) | _classify_poi(poi)
            if not tags:
                continue
            avg = sum(tag_adj.get(t, 0.0) for t in tags) / len(tags)
            if avg >= 0.0:
                tag_pref_reward += avg * TAG_PREFERENCE_SCALE
            else:
                tag_pref_penalty += -avg * TAG_PREFERENCE_SCALE
    eval_result.tag_preference_reward = tag_pref_reward

    eval_result.delta = (
        w.distance * eval_result.distance_penalty
        + w.hard_violation * eval_result.hard_violation_penalty
        + w.undertime * eval_result.undertime_penalty
        + w.overtime * eval_result.overtime_penalty
        + w.wrong_time * eval_result.wrong_time_penalty
        + w.waterfall * eval_result.waterfall_penalty
        + w.fatigue * eval_result.fatigue_penalty
        + w.type_coverage * eval_result.type_coverage_penalty
        + w.beach_dominance * eval_result.beach_dominance_penalty
        + eval_result.preference_daily_penalty
        + eval_result.preference_global_penalty
        + tag_pref_penalty
    )
    total_reward = (
        eval_result.poi_value_sum
        + eval_result.time_utilization_bonus
        + eval_result.route_length_bonus
        + eval_result.must_see_reward
        + eval_result.neighbour_reward
        + eval_result.correct_time_reward
        + eval_result.type_coverage_bonus
        + tag_pref_reward
        + eval_result.preference_global_reward
    )
    eval_result.total_reward = total_reward
    eval_result.fitness = total_reward / (1.0 + eval_result.delta)
    eval_result.travel_penalty = eval_result.distance_penalty
    eval_result.constraint_penalty = eval_result.hard_violation_penalty
    eval_result.user_pref_penalty = tag_pref_penalty
    eval_result.must_see_penalty = (
        eval_result.waterfall_penalty + eval_result.fatigue_penalty
    )
    eval_result.restaurant_penalty = 0.0
    return eval_result


def initialize_population(
    candidate_pois,
    population_size,
    fitness_weights: FitnessWeights | None = None,
    tag_adjustments: dict[str, float] | None = None,
    penalty_place_ids: frozenset[str] | None = None,
    preference_state: PreferenceState | None = None,
):
    """Initialize population with random routes of varying lengths."""
    population = []
    if not candidate_pois:
        return population

    fw = fitness_weights or get_fitness_weights("solo")
    tag_adj = tag_adjustments if tag_adjustments is not None else {}
    for _ in range(population_size):
        route_len = random.randint(
            MIN_POIS_PER_ROUTE, min(MAX_POIS_PER_ROUTE, len(candidate_pois))
        )
        sorted_pois = sorted(
            candidate_pois, key=lambda p: p.normalized_popularity, reverse=True
        )
        mid = len(sorted_pois) // 2
        route = []
        for _ in range(route_len):
            if random.random() < 0.7 and mid > 0:
                poi = random.choice(sorted_pois[:mid])
            else:
                poi = random.choice(sorted_pois)
            if poi not in route:
                route.append(poi)

        while len(route) < MIN_POIS_PER_ROUTE:
            unvisited = [p for p in candidate_pois if p not in route]
            if unvisited:
                route.append(random.choice(unvisited))
            else:
                break

        population.append(
            Individual(
                route,
                candidate_pois,
                fw,
                tag_adj,
                penalty_place_ids,
                preference_state,
            )
        )
    return population


def tournament_selection(population, tournament_size=TOURNAMENT_SIZE):
    tournament = random.sample(population, min(tournament_size, len(population)))
    return max(tournament, key=lambda ind: ind.fitness if ind.fitness is not None else -1.0)


def swap_mutation(individual):
    """Swap mutation: randomly swap two POIs in route."""
    if random.random() > MUTATION_RATE:
        return individual
    if len(individual.route) < 2:
        return individual
    mutated = individual.copy()
    idx1, idx2 = random.sample(range(len(mutated.route)), 2)
    mutated.route[idx1], mutated.route[idx2] = (
        mutated.route[idx2],
        mutated.route[idx1],
    )
    mutated.fitness = None
    return mutated


def single_point_crossover(parent1, parent2):
    """Single-point crossover adapted for variable-length chromosomes."""
    size1 = len(parent1.route)
    size2 = len(parent2.route)
    min_size = min(size1, size2)
    if min_size < 2:
        return parent1.copy(), parent2.copy()

    cx_point = random.randint(1, min_size - 1)
    offspring1_route = parent1.route[:cx_point].copy()
    offspring2_route = parent2.route[:cx_point].copy()

    for poi in parent2.route[cx_point:]:
        if poi not in offspring1_route:
            offspring1_route.append(poi)
    for poi in parent1.route[cx_point:]:
        if poi not in offspring2_route:
            offspring2_route.append(poi)

    all_pois = parent1.candidate_pois
    while len(offspring1_route) < MIN_POIS_PER_ROUTE and all_pois:
        unvisited = [p for p in all_pois if p not in offspring1_route]
        if not unvisited:
            break
        unvisited_sorted = sorted(
            unvisited, key=lambda p: p.normalized_popularity, reverse=True
        )
        offspring1_route.append(
            random.choice(unvisited_sorted[: min(5, len(unvisited_sorted))])
        )
    while len(offspring2_route) < MIN_POIS_PER_ROUTE and all_pois:
        unvisited = [p for p in all_pois if p not in offspring2_route]
        if not unvisited:
            break
        unvisited_sorted = sorted(
            unvisited, key=lambda p: p.normalized_popularity, reverse=True
        )
        offspring2_route.append(
            random.choice(unvisited_sorted[: min(5, len(unvisited_sorted))])
        )

    return (
        Individual(
            offspring1_route,
            parent1.candidate_pois,
            parent1.fitness_weights,
            parent1.tag_adjustments,
            parent1.penalty_place_ids,
            parent1.preference_state,
        ),
        Individual(
            offspring2_route,
            parent2.candidate_pois,
            parent2.fitness_weights,
            parent2.tag_adjustments,
            parent2.penalty_place_ids,
            parent2.preference_state,
        ),
    )


def optimize_route_ga(
    pois,
    start_time=TOUR_START_TIME,
    keep_top_n=3,
    diversity_tracker=None,
    fitness_weights: FitnessWeights | None = None,
    tag_adjustments: dict[str, float] | None = None,
    penalty_place_ids: frozenset[str] | None = None,
    preference_state: PreferenceState | None = None,
):
    """
    Genetic Algorithm for route optimization (TPOS-aligned main loop).
    """
    if not pois or len(pois) == 0:
        raise ValueError("Cannot optimize route: No POIs provided")

    fw = fitness_weights or get_fitness_weights("solo")
    tag_adj = tag_adjustments if tag_adjustments is not None else {}
    pen_ids = penalty_place_ids if penalty_place_ids is not None else frozenset()
    candidate_pois = select_top_pois_for_optimization(
        pois, diversity_tracker=diversity_tracker
    )
    if not candidate_pois:
        return [], []

    if len(candidate_pois) < MIN_POIS_PER_ROUTE:
        only = Individual(
            candidate_pois,
            candidate_pois,
            fw,
            tag_adj,
            pen_ids,
            preference_state,
        )
        only.evaluate(start_time)
        fit = float(only.fitness) if only.fitness is not None else 0.0
        return [only], [fit]

    population = initialize_population(
        candidate_pois, POPULATION_SIZE, fw, tag_adj, pen_ids, preference_state
    )
    for ind in population:
        ind.evaluate(start_time)

    best_individual = max(population, key=lambda ind: ind.fitness)
    best_fitness_history = [best_individual.fitness]
    no_improvement_count = 0

    for _generation in range(1, MAX_GENERATIONS + 1):
        new_population = [best_individual.copy()]

        while len(new_population) < POPULATION_SIZE:
            parent1 = tournament_selection(population)
            parent2 = tournament_selection(population)
            if random.random() < CROSSOVER_RATE:
                offspring1, offspring2 = single_point_crossover(parent1, parent2)
            else:
                offspring1, offspring2 = parent1.copy(), parent2.copy()
            offspring1 = swap_mutation(offspring1)
            offspring2 = swap_mutation(offspring2)
            new_population.extend([offspring1, offspring2])

        population = new_population[:POPULATION_SIZE]
        for ind in population:
            if ind.fitness is None:
                ind.evaluate(start_time)

        generation_best = max(population, key=lambda ind: ind.fitness)
        if generation_best.fitness > best_individual.fitness:
            best_individual = generation_best.copy()
            no_improvement_count = 0
        else:
            no_improvement_count += 1

        best_fitness_history.append(best_individual.fitness)
        if no_improvement_count >= EARLY_STOPPING_THRESHOLD:
            break

    best_individual.evaluate(start_time)

    unique: Dict[tuple, Individual] = {}
    for ind in population:
        key = tuple(p.place_id for p in ind.route)
        if key not in unique or (
            unique[key].fitness is None or ind.fitness > unique[key].fitness
        ):
            unique[key] = ind

    sorted_unique = sorted(
        unique.values(), key=lambda x: x.fitness if x.fitness is not None else -1.0, reverse=True
    )
    # Ensure best_individual is included first.
    if sorted_unique:
        best_key = tuple(p.place_id for p in best_individual.route)
        sorted_unique = [best_individual] + [
            ind for ind in sorted_unique if tuple(p.place_id for p in ind.route) != best_key
        ]

    def route_set_difference(a: Individual, b: Individual) -> float:
        a_ids = {p.place_id for p in a.route}
        b_ids = {p.place_id for p in b.route}
        union = a_ids | b_ids
        if not union:
            return 0.0
        inter = a_ids & b_ids
        return 1.0 - (len(inter) / len(union))

    min_diff = 0.40
    selected = []
    for candidate in sorted_unique:
        if not selected:
            selected.append(candidate)
            if len(selected) >= keep_top_n:
                break
            continue
        if all(route_set_difference(candidate, s) >= min_diff for s in selected):
            selected.append(candidate)
        if len(selected) >= keep_top_n:
            break

    if len(selected) < keep_top_n:
        for candidate in sorted_unique:
            if candidate in selected:
                continue
            selected.append(candidate)
            if len(selected) >= keep_top_n:
                break

    return selected[:keep_top_n], best_fitness_history


def _extract_must_visit_pois(individual: Individual) -> list[POI]:
    return [poi for poi in individual.route if _is_must_see(poi)]


def _route_place_ids(individual: Individual) -> set[str]:
    return {str(p.place_id) for p in individual.route}


def select_exclusive_must_visit_alternatives(
    candidates: list[Individual],
    *,
    desired_count: int,
) -> list[tuple[Individual, str | None]]:
    """Pick alternatives with exclusive must-visit POIs when possible.

    Returns a list of (Individual, exclusive_must_visit_id | None).
    """
    selected: list[tuple[Individual, str | None]] = []
    used_exclusive_ids: set[str] = set()
    remaining: list[Individual] = []

    for candidate in candidates:
        must_visits = _extract_must_visit_pois(candidate)
        if not must_visits:
            remaining.append(candidate)
            continue
        must_visit_ids = {str(p.place_id) for p in must_visits}
        if must_visit_ids & used_exclusive_ids:
            remaining.append(candidate)
            continue
        chosen = max(must_visits, key=lambda p: p.normalized_popularity)
        chosen_id = str(chosen.place_id)
        selected.append((candidate, chosen_id))
        used_exclusive_ids.add(chosen_id)
        if len(selected) >= desired_count:
            return selected

    if len(selected) < desired_count:
        no_must_visit = []
        for cand in remaining:
            if not _extract_must_visit_pois(cand):
                no_must_visit.append(cand)
        for candidate in no_must_visit:
            if len(selected) >= desired_count:
                break
            selected.append((candidate, None))

    if len(selected) < desired_count:
        for candidate in remaining:
            if len(selected) >= desired_count:
                break
            if any(candidate is s[0] for s in selected):
                continue
            must_visit_pois = _extract_must_visit_pois(candidate)
            must_visit_ids = {str(p.place_id) for p in must_visit_pois}
            if must_visit_ids & used_exclusive_ids:
                continue
            selected.append((candidate, None))

    if len(selected) < desired_count:
        for candidate in remaining:
            if len(selected) >= desired_count:
                break
            if any(candidate is s[0] for s in selected):
                continue
            selected.append((candidate, None))

    return selected


def select_secondary_itinerary_alternatives(
    candidates: list[Individual],
    *,
    desired_count: int,
    preferred_must_visit_ids: set[str] | None = None,
    disjoint_ids: set[str] | None = None,
) -> list[tuple[Individual, str | None]]:
    """Pick secondary alternatives, preferring remaining must-visits.

    If disjoint_ids are provided, prefer routes that avoid those POIs.
    """
    filtered = candidates
    if disjoint_ids:
        disjoint_candidates = []
        for candidate in filtered:
            if not (_route_place_ids(candidate) & disjoint_ids):
                disjoint_candidates.append(candidate)
        if disjoint_candidates:
            filtered = disjoint_candidates

    if preferred_must_visit_ids:
        preferred_candidates = []
        for candidate in filtered:
            if _route_place_ids(candidate) & preferred_must_visit_ids:
                preferred_candidates.append(candidate)
        if preferred_candidates:
            filtered = preferred_candidates

    return select_exclusive_must_visit_alternatives(
        filtered, desired_count=desired_count
    )


def _resolve_exclusive_must_visit_name(
    individual: Individual, poi_id: str | None
) -> str | None:
    if not poi_id:
        return None
    for poi in individual.route:
        if str(poi.place_id) == poi_id:
            return poi.name
    return None


def create_route_map_from_json(
    day_key: str,
    route_data: Dict[str, Any],
    hotel: Dict[str, Any] | None = None,
) -> str:
    route = route_data.get("route") or []
    if not route:
        m = folium.Map(location=[15.4, 73.9], zoom_start=9)
    else:
        center_lat = float(route[0]["latitude"])
        center_lon = float(route[0]["longitude"])
        if hotel and hotel.get("latitude") is not None and hotel.get("longitude") is not None:
            try:
                center_lat = float(hotel["latitude"])
                center_lon = float(hotel["longitude"])
            except (TypeError, ValueError):
                pass

        m = folium.Map(location=[center_lat, center_lon], zoom_start=11)

        hotel_coord: Tuple[float, float] | None = None
        if hotel and hotel.get("latitude") is not None and hotel.get("longitude") is not None:
            try:
                hotel_lat = float(hotel["latitude"])
                hotel_lon = float(hotel["longitude"])
                hotel_coord = (hotel_lat, hotel_lon)
            except (TypeError, ValueError):
                hotel_coord = None
            if hotel_coord:
                label = str(hotel.get("label") or "Hotel")
                address = hotel.get("address")
                popup = f"<b>{label}</b>" + (f"<br>{address}" if address else "")
                folium.Marker(
                    location=[hotel_coord[0], hotel_coord[1]],
                    popup=popup,
                    tooltip="Hotel",
                    icon=folium.Icon(color="black", icon="home", prefix="fa"),
                ).add_to(m)

        coords: list[list[float]] = []
        for stop in route:
            coords.append([float(stop["latitude"]), float(stop["longitude"])])
            popup = (
                f"{stop['name']}<br>"
                f"Arrive: {stop.get('arrival_time', '-')}"
                f"<br>Visit: {stop.get('visit_start', '-')} - {stop.get('visit_end', '-')}"
                f"<br>Duration: {stop.get('visit_duration_min', '-')} min"
            )
            folium.Marker(
                location=[stop["latitude"], stop["longitude"]],
                popup=popup,
                tooltip=f"{stop['sequence']}. {stop['name']}",
            ).add_to(m)
            for suggestion in stop.get("nearby_suggestions", []):
                s_popup = (
                    f"Nearby: {suggestion.get('name', '')}<br>"
                    f"Distance: {suggestion.get('distance_km', '-')} km"
                    f"<br>WPI: {suggestion.get('wpi', '-')}"
                )
                folium.CircleMarker(
                    location=[suggestion["latitude"], suggestion["longitude"]],
                    radius=5,
                    color="orange",
                    fill=True,
                    fill_opacity=0.8,
                    popup=s_popup,
                    tooltip=f"Nearby to {stop['sequence']}",
                ).add_to(m)

        if len(coords) > 1:
            route_geom = build_full_route_geometry(coords)
            folium.PolyLine(route_geom or coords, color="blue", weight=4).add_to(m)

        # Hotel -> first, last -> hotel legs
        if hotel_coord and coords:
            first_coord = (float(coords[0][0]), float(coords[0][1]))
            last_coord = (float(coords[-1][0]), float(coords[-1][1]))

            leg1_geom = get_osrm_segment_route(hotel_coord, first_coord) or [
                [hotel_coord[0], hotel_coord[1]],
                [first_coord[0], first_coord[1]],
            ]
            folium.PolyLine(
                leg1_geom,
                color="green",
                weight=4,
                opacity=0.9,
                dash_array="8, 8",
                tooltip="Hotel → first stop",
            ).add_to(m)

            leg2_geom = get_osrm_segment_route(last_coord, hotel_coord) or [
                [last_coord[0], last_coord[1]],
                [hotel_coord[0], hotel_coord[1]],
            ]
            folium.PolyLine(
                leg2_geom,
                color="red",
                weight=4,
                opacity=0.9,
                dash_array="8, 8",
                tooltip="Last stop → hotel",
            ).add_to(m)

        # Round-trip summary overlay (only if the distances were computed upstream)
        if route_data.get("round_trip_total_distance_km") is not None:
            try:
                poi_distance = float(route_data.get("total_distance_km") or 0.0)
            except (TypeError, ValueError):
                poi_distance = 0.0
            h2f = route_data.get("hotel_to_first_distance_km")
            l2h = route_data.get("last_to_hotel_distance_km")
            rt = route_data.get("round_trip_total_distance_km")
            if h2f is not None and l2h is not None and rt is not None:
                summary_html = f'''\
                <div style="position: fixed; bottom: 20px; left: 20px;\
                            background: rgba(255,255,255,0.95); padding: 12px;\
                            border-radius: 8px; border: 1px solid #cbd5e1;\
                            font-family: system-ui; font-size: 13px; z-index: 9999;\
                            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">\
                    <b style="color: #1e293b; font-size: 14px;">Round Trip Summary</b><br>\
                    <div style="margin-top: 8px; color: #475569; line-height: 1.4;">\
                        POI route: {poi_distance:.1f} km<br>\
                        Hotel → first: {float(h2f):.1f} km<br>\
                        Last → hotel: {float(l2h):.1f} km<br>\
                        <b>Total: {float(rt):.1f} km</b>\
                    </div>\
                </div>\
                '''
                m.get_root().html.add_child(folium.Element(summary_html))

    name = f"{day_key}_{uuid.uuid4().hex[:8]}.html"
    m.save(MAPS_DIR / name)
    return name


def get_osrm_segment_route(start_coord, end_coord, profile="driving"):
    geom, _dist = get_osrm_segment_route_and_distance_km(
        start_coord, end_coord, profile=profile
    )
    return geom


def get_osrm_segment_route_and_distance_km(
    start_coord: Tuple[float, float],
    end_coord: Tuple[float, float],
    profile: str = "driving",
) -> tuple[list[list[float]] | None, float | None]:
    lat1, lon1 = start_coord
    lat2, lon2 = end_coord
    url = (
        f"{OSRM_BASE_URL}/route/v1/{profile}/{lon1},{lat1};{lon2},{lat2}"
        "?overview=full&geometries=geojson"
    )

    try:
        res = requests.get(url, timeout=8)
        if res.status_code != 200:
            return None, None
        data = res.json()
        routes = data.get("routes", [])
        if not routes:
            return None, None
        geom = [[c[1], c[0]] for c in routes[0]["geometry"]["coordinates"]]
        distance_m = routes[0].get("distance")
        distance_km = (
            float(distance_m) / 1000.0
            if isinstance(distance_m, (int, float))
            else None
        )
        return geom, distance_km
    except Exception:
        return None, None


def get_osrm_segment_distance_km(
    start_coord: Tuple[float, float],
    end_coord: Tuple[float, float],
    profile: str = "driving",
) -> float | None:
    _geom, dist = get_osrm_segment_route_and_distance_km(
        start_coord, end_coord, profile=profile
    )
    return dist


def compute_round_trip_distance_km(
    route_distance_km: float | None,
    hotel_to_first_km: float | None,
    last_to_hotel_km: float | None,
) -> float | None:
    """Compute total round-trip distance in km.

    Round trip is defined as: hotel → first POI → ... → last POI → hotel.
    """

    if route_distance_km is None:
        return None
    if hotel_to_first_km is None or last_to_hotel_km is None:
        return None
    return float(route_distance_km) + float(hotel_to_first_km) + float(last_to_hotel_km)


def _resolve_hotel_anchor(
    payload: Dict[str, Any], module2_result: Dict[str, Any]
) -> Dict[str, Any] | None:
    """Resolve hotel coordinates/label to use on maps.

    Priority:
    1) Explicit `hotel_lat`/`hotel_lon` in payload (if within Goa bounds)
    2) Module 2 resolved anchor (from region/hotel_location match)
    """

    hotel_lat = payload.get("hotel_lat")
    hotel_lon = payload.get("hotel_lon")
    hotel_address = payload.get("hotel_address")
    hotel_location = payload.get("hotel_location")

    try:
        if hotel_lat is not None and hotel_lon is not None:
            lat = float(hotel_lat)
            lon = float(hotel_lon)
            if 14.8 <= lat <= 15.9 and 73.6 <= lon <= 74.4:
                return {
                    "latitude": lat,
                    "longitude": lon,
                    "label": hotel_address or hotel_location or "hotel",
                    "address": hotel_address,
                    "source": "payload",
                }
    except (TypeError, ValueError):
        pass

    radius_filter = module2_result.get("radius_filter") or {}
    anchor = radius_filter.get("anchor") if isinstance(radius_filter, dict) else None
    if isinstance(anchor, dict) and anchor.get("latitude") is not None and anchor.get("longitude") is not None:
        try:
            lat = float(anchor.get("latitude"))
            lon = float(anchor.get("longitude"))
        except (TypeError, ValueError):
            return None
        if 14.8 <= lat <= 15.9 and 73.6 <= lon <= 74.4:
            return {
                "latitude": lat,
                "longitude": lon,
                "label": anchor.get("address") or anchor.get("label") or hotel_location or "hotel",
                "address": anchor.get("address"),
                "source": anchor.get("source") or "module2_anchor",
            }

    return None


def _augment_day_json_with_hotel_round_trip(
    day_json: Dict[str, Any],
    hotel: Dict[str, Any] | None,
    use_osrm: bool,
) -> Dict[str, Any]:
    if not hotel:
        return day_json

    out = dict(day_json)
    out["hotel"] = {
        k: hotel.get(k)
        for k in ("latitude", "longitude", "label", "address", "source")
    }

    route = day_json.get("route") or []
    if not isinstance(route, list) or not route:
        return out

    hotel_coord = (float(hotel["latitude"]), float(hotel["longitude"]))
    first = route[0]
    last = route[-1]
    first_coord = (float(first["latitude"]), float(first["longitude"]))
    last_coord = (float(last["latitude"]), float(last["longitude"]))

    hotel_to_first_km: float | None = None
    last_to_hotel_km: float | None = None

    if use_osrm:
        hotel_to_first_km = get_osrm_segment_distance_km(hotel_coord, first_coord)
        last_to_hotel_km = get_osrm_segment_distance_km(last_coord, hotel_coord)

    if hotel_to_first_km is None:
        hotel_to_first_km = float(haversine_distance(hotel_coord, first_coord))
    if last_to_hotel_km is None:
        last_to_hotel_km = float(haversine_distance(last_coord, hotel_coord))

    route_distance_val = day_json.get("total_distance_km")
    try:
        route_distance_km = float(route_distance_val) if route_distance_val is not None else None
    except (TypeError, ValueError):
        route_distance_km = None

    round_trip_km = compute_round_trip_distance_km(
        route_distance_km, hotel_to_first_km, last_to_hotel_km
    )

    out["hotel_to_first_distance_km"] = round(float(hotel_to_first_km), 3)
    out["last_to_hotel_distance_km"] = round(float(last_to_hotel_km), 3)
    out["round_trip_total_distance_km"] = (
        round(float(round_trip_km), 3) if round_trip_km is not None else None
    )
    return out


def build_full_route_geometry(poi_coords, profile="driving"):
    if len(poi_coords) < 2:
        return poi_coords
    full = []
    for i in range(len(poi_coords) - 1):
        seg = get_osrm_segment_route(poi_coords[i], poi_coords[i + 1], profile=profile)
        if seg:
            if full and seg:
                full.extend(seg[1:])
            else:
                full.extend(seg)
        else:
            if not full:
                full.append(poi_coords[i])
            full.append(poi_coords[i + 1])
    return full


def _build_nearby_suggestions_for_route(route, day_pool, max_per_stop=NEARBY_SUGGESTIONS_PER_STOP):
    route_ids = {p.place_id for p in route}
    outside = [p for p in day_pool if p.place_id not in route_ids]
    suggestions_by_anchor = {}
    for anchor in route:
        scored = []
        for cand in outside:
            d = haversine_distance((anchor.lat, anchor.lon), (cand.lat, cand.lon))
            if d <= NEARBY_SUGGESTION_RADIUS_KM:
                score = (1.4 * float(cand.normalized_popularity)) - (0.35 * d)
                scored.append((score, d, cand))
        scored.sort(key=lambda x: x[0], reverse=True)
        suggestions_by_anchor[anchor.place_id] = [
            {
                "poi_id": c.place_id,
                "name": c.name,
                "latitude": c.lat,
                "longitude": c.lon,
                "distance_km": round(dist, 3),
                "wpi": round(c.normalized_popularity, 3),
            }
            for _, dist, c in scored[:max_per_stop]
        ]
    return suggestions_by_anchor


def build_fitness_breakdown(
    evaluation: RouteEvaluation, weights: FitnessWeights
) -> Dict[str, Any]:
    """Serializable GA fitness terms for API/UI transparency."""
    return {
        "formula": "reward_over_one_plus_delta",
        "fitness": evaluation.fitness,
        "delta": evaluation.delta,
        "total_reward": evaluation.total_reward,
        "weights": asdict(weights),
        "raw_components": {
            "distance_penalty": evaluation.distance_penalty,
            "hard_violation_penalty": evaluation.hard_violation_penalty,
            "undertime_penalty": evaluation.undertime_penalty,
            "overtime_penalty": evaluation.overtime_penalty,
            "wrong_time_penalty": evaluation.wrong_time_penalty,
            "waterfall_penalty": evaluation.waterfall_penalty,
            "fatigue_penalty": evaluation.fatigue_penalty,
            "type_coverage_penalty": evaluation.type_coverage_penalty,
            "beach_dominance_penalty": evaluation.beach_dominance_penalty,
            "user_pref_penalty": evaluation.user_pref_penalty,
            "poi_value_sum": evaluation.poi_value_sum,
            "time_utilization_bonus": evaluation.time_utilization_bonus,
            "route_length_bonus": evaluation.route_length_bonus,
            "must_see_reward": evaluation.must_see_reward,
            "neighbour_reward": evaluation.neighbour_reward,
            "correct_time_reward": evaluation.correct_time_reward,
            "type_coverage_bonus": evaluation.type_coverage_bonus,
            "tag_preference_reward": evaluation.tag_preference_reward,
            "beach_scorch_overlap_min": evaluation.beach_scorch_overlap_min,
            "itinerary_qa_place_penalty": evaluation.itinerary_qa_place_penalty,
            "preference_daily_missing": evaluation.preference_daily_missing,
            "preference_daily_penalty": evaluation.preference_daily_penalty,
            "preference_global_penalty": evaluation.preference_global_penalty,
            "preference_global_reward": evaluation.preference_global_reward,
        },
    }


def build_day_json(
    day_num: int,
    best_individual,
    day_pool=None,
    ga_convergence: list[float] | None = None,
):
    sequence = []
    evaluation = best_individual.evaluation or evaluate_fitness(
        best_individual.route,
        weights=best_individual.fitness_weights,
        tag_adjustments=best_individual.tag_adjustments,
        penalty_place_ids=best_individual.penalty_place_ids,
        preference_state=best_individual.preference_state,
    )
    fitness_breakdown = build_fitness_breakdown(
        evaluation, best_individual.fitness_weights
    )
    timeline = evaluation.timeline or []
    day_pool = day_pool or best_individual.candidate_pois or best_individual.route
    nearby_by_anchor = _build_nearby_suggestions_for_route(best_individual.route, day_pool)
    for i, timeline_item in enumerate(timeline, start=1):
        poi, arrival_time, visit_start, visit_end = timeline_item
        sequence.append(
            {
                "sequence": i,
                "poi_id": poi.place_id,
                "name": poi.name,
                "latitude": poi.lat,
                "longitude": poi.lon,
                "wpi_score": poi.normalized_popularity,
                "rating": poi.rating,
                "user_ratings_total": poi.user_ratings_total,
                "arrival_time": arrival_time,
                "visit_start": visit_start,
                "visit_end": visit_end,
                "visit_duration_min": poi.visit_duration_min,
                "nearby_suggestions": nearby_by_anchor.get(poi.place_id, []),
            }
        )

    out: Dict[str, Any] = {
        "day": day_num,
        "route": sequence,
        "fitness_score": best_individual.fitness,
        "fitness_breakdown": fitness_breakdown,
        "poi_value_sum": evaluation.poi_value_sum,
        "total_distance_km": best_individual.distance_km,
        "total_travel_time_min": best_individual.travel_time_min,
        "total_time_min": evaluation.total_time_min,
        "constraint_violations": {
            "closed_poi": evaluation.closed_poi_count,
            "lunch_invasion": evaluation.lunch_invasion_count,
            "overtime_min": evaluation.overtime_minutes,
            "beach_streak_violations": evaluation.beach_streak_violations,
            "beach_scorch_overlap_min": evaluation.beach_scorch_overlap_min,
        },
        "nearby_alternatives": evaluation.nearby_alternatives or {},
        "nearby_suggestions_total": int(
            sum(len(s) for s in nearby_by_anchor.values())
        ),
    }
    if ga_convergence is not None:
        out["ga_convergence"] = ga_convergence
    return out


def save_days_separately(results: Dict, trip_name: str = "trip"):
    paths = []
    for day_key, data in results["routes"].items():
        p = EXPORTS_DIR / f"{trip_name}_{day_key}.json"
        with open(p, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        paths.append(str(p.name))
    return paths


def verify_saved_files():
    return {"exports": [x.name for x in EXPORTS_DIR.glob("*.json")], "maps": [x.name for x in MAPS_DIR.glob("*.html")]}


def run_module4_simulation(payload: Dict[str, Any]) -> Dict[str, Any]:
    ensure_output_dirs()
    random.seed(payload.get("random_state", 42))
    np.random.seed(payload.get("random_state", 42))
    global POPULATION_SIZE, MAX_GENERATIONS, MUTATION_RATE, CROSSOVER_RATE, EARLY_STOPPING_THRESHOLD
    POPULATION_SIZE = int(payload.get("population_size", POPULATION_SIZE))
    MAX_GENERATIONS = int(payload.get("max_generations", MAX_GENERATIONS))
    MUTATION_RATE = float(payload.get("mutation_rate", MUTATION_RATE))
    CROSSOVER_RATE = float(payload.get("crossover_rate", CROSSOVER_RATE))
    EARLY_STOPPING_THRESHOLD = int(
        payload.get("early_stopping_patience", EARLY_STOPPING_THRESHOLD)
    )

    travel_type = str(payload.get("travel_type", "solo"))
    from app.services.preference_fitness_llm import resolve_fitness_profile

    module1 = run_module1_simulation(
        payload["user_preference"],
        payload.get("min_rating", 3.0),
        use_llm_interests=bool(payload.get("use_llm_interests", False)),
    )

    raw_extraction = module1.get("preference_extraction")
    module1_context: str | None = None
    if isinstance(raw_extraction, dict) and raw_extraction:
        module1_context = json.dumps(raw_extraction, ensure_ascii=False)

    fitness_profile = resolve_fitness_profile(
        travel_type,
        str(payload.get("user_preference", "")),
        use_llm=bool(payload.get("use_llm_fitness_profile", False)),
        module1_context=module1_context,
    )
    fitness_weights = fitness_profile.weights
    tag_adjustments = fitness_profile.tag_adjustments
    positive_interests = module1.get("positive_interests") or []
    negative_interests = module1.get("negative_interests") or []
    if "religious" not in positive_interests:
        base_penalty = -0.2
        if "religious" in negative_interests:
            base_penalty = -0.45
        for tag in ("religious", "church", "temple"):
            current = tag_adjustments.get(tag)
            if current is None or current > base_penalty:
                tag_adjustments[tag] = base_penalty
    module2 = run_module2_simulation(
        payload["num_days"],
        min_reviews=payload.get("min_reviews", 1),
        random_state=payload.get("random_state", 42),
        input_places=module1.get("places"),
        travel_distance=payload.get("travel_distance"),
        hotel_location=payload.get("hotel_location"),
        hotel_address=payload.get("hotel_address"),
        hotel_lat=payload.get("hotel_lat"),
        hotel_lon=payload.get("hotel_lon"),
        region=payload.get("region"),
        user_preference=payload.get("user_preference"),
        positive_interests=positive_interests,
    )

    hotel_anchor = _resolve_hotel_anchor(payload, module2)

    df_places = module2["places"]
    import pandas as pd

    df = pd.DataFrame(df_places)
    routes = {}
    route_maps = {}
    day_list = sorted(df["day"].unique())
    available_days = len(day_list)
    day_pois_map = {int(day): load_pois_for_day(df, int(day)) for day in day_list}
    day_tag_availability = {
        int(day): _collect_preference_tags_for_pois(pois)
        for day, pois in day_pois_map.items()
    }
    global_diversity_tracker = {
        "historical": 0,
        "religious": 0,
        "nature": 0,
        "beach": 0,
        "waterfall": 0,
        "park": 0,
        "fort": 0,
        "scenic": 0,
        "peaceful": 0,
        "relaxation": 0,
        "photography": 0,
        "water_sports": 0,
        "other": 0,
        "church": 0,
        "temple": 0,
    }

    use_osrm = payload.get("use_osrm", True)
    include_ga_history = bool(payload.get("include_ga_history", False))
    use_llm_itinerary_qa = bool(payload.get("use_llm_itinerary_qa", False))
    use_llm_itinerary_retry = bool(payload.get("use_llm_itinerary_retry", False))
    use_llm_secondary_itinerary_qa = bool(
        payload.get("use_llm_secondary_itinerary_qa", False)
    )

    preference_tags, preference_ignored = _resolve_preference_tags(positive_interests)
    preference_targets = _build_preference_targets(
        preference_tags, day_tag_availability, available_days
    )
    preference_tracker = {tag: 0 for tag in preference_tags}

    from app.services.itinerary_qa_llm import evaluate_itinerary_qa

    for day_idx, day in enumerate(day_list):
        day = int(day)
        pois = day_pois_map.get(day, [])
        if not pois:
            continue
        prepare_day_matrices(pois, use_osrm=use_osrm)
        preference_state = None
        if preference_tags:
            remaining_days = max(1, len(day_list) - day_idx)
            required_tags = _select_daily_required_tags(
                preference_tags, day_tag_availability.get(day, set())
            )
            preference_state = PreferenceState(
                required_day_tags=frozenset(required_tags),
                global_targets=preference_targets,
                global_counts=dict(preference_tracker),
                remaining_days=remaining_days,
                remaining_available_days=_build_remaining_available_days(
                    day_list, day_idx, day_tag_availability, preference_tags
                ),
            )
        day_fitness_weights = fitness_weights
        top_candidates, best_fitness_history = optimize_route_ga(
            pois,
            keep_top_n=ALTERNATIVE_CANDIDATE_POOL,
            diversity_tracker=global_diversity_tracker,
            fitness_weights=day_fitness_weights,
            tag_adjustments=tag_adjustments,
            preference_state=preference_state,
        )
        selected = select_exclusive_must_visit_alternatives(
            top_candidates, desired_count=ALTERNATIVE_COUNT
        )
        recommended_individual = selected[0][0] if selected else None
        itinerary_qa: dict[str, Any] | None = None
        itinerary_retry_attempted = False
        itinerary_retry_details: dict[str, Any] | None = None
        if use_llm_itinerary_qa and recommended_individual:
            preview = build_day_json(day, recommended_individual, day_pool=pois)
            itinerary_qa = evaluate_itinerary_qa(preview["route"], day)
            if (
                use_llm_itinerary_retry
                and itinerary_qa.get("ok") is False
                and itinerary_qa.get("source") == "groq"
            ):
                flagged_ids, resolved = resolve_qa_flagged_place_ids(
                    itinerary_qa.get("problematic_places") or [],
                    preview["route"],
                    pois,
                )
                penalty_ids: frozenset[str] = frozenset()
                pois_for_ga: list = pois
                strategy: str | None = None
                if flagged_ids:
                    filtered = [p for p in pois if str(p.place_id) not in flagged_ids]
                    if len(filtered) >= MIN_POIS_PER_ROUTE:
                        pois_for_ga = filtered
                        strategy = "excluded_from_pool"
                    else:
                        penalty_ids = flagged_ids
                        strategy = "penalty_only"
                        logger.info(
                            "Module4 day %s: QA retry penalty_only; excluded pool would leave %s POIs (< %s)",
                            day,
                            len(filtered),
                            MIN_POIS_PER_ROUTE,
                        )
                else:
                    strategy = "weights_only"

                if strategy == "excluded_from_pool":
                    prepare_day_matrices(pois_for_ga, use_osrm=use_osrm)

                day_fitness_weights = replace(
                    fitness_weights,
                    wrong_time=min(fitness_weights.wrong_time * 1.2, 3.0),
                )
                logger.info(
                    "Module4 day %s: itinerary QA retry strategy=%s wrong_time=%.3f penalized_ids=%s",
                    day,
                    strategy,
                    day_fitness_weights.wrong_time,
                    len(penalty_ids),
                )
                top_candidates, best_fitness_history = optimize_route_ga(
                    pois_for_ga,
                    keep_top_n=ALTERNATIVE_CANDIDATE_POOL,
                    diversity_tracker=global_diversity_tracker,
                    fitness_weights=day_fitness_weights,
                    tag_adjustments=tag_adjustments,
                    penalty_place_ids=penalty_ids,
                    preference_state=preference_state,
                )
                itinerary_retry_attempted = True
                itinerary_retry_details = {
                    "strategy": strategy,
                    "flagged_place_ids": sorted(flagged_ids),
                    "resolved_flagged_places": resolved,
                    "raw_problematic_places": itinerary_qa.get("problematic_places"),
                }
                prepare_day_matrices(pois, use_osrm=use_osrm)
                selected = select_exclusive_must_visit_alternatives(
                    top_candidates, desired_count=ALTERNATIVE_COUNT
                )
                recommended_individual = selected[0][0] if selected else None
                if recommended_individual:
                    preview = build_day_json(day, recommended_individual, day_pool=pois)
                    itinerary_qa = evaluate_itinerary_qa(preview["route"], day)

        alternatives = []
        for rank, (ind, exclusive_id) in enumerate(selected, start=1):
            ga_conv = (
                best_fitness_history
                if (rank == 1 and include_ga_history and best_fitness_history)
                else None
            )
            day_json = build_day_json(
                day, ind, day_pool=pois, ga_convergence=ga_conv
            )
            day_json = _augment_day_json_with_hotel_round_trip(
                day_json, hotel_anchor, use_osrm=use_osrm
            )
            map_name = create_route_map_from_json(
                f"module4_day_{day}_rank_{rank}",
                day_json,
                hotel=hotel_anchor,
            )
            exclusive_name = _resolve_exclusive_must_visit_name(ind, exclusive_id)
            alternatives.append(
                {
                    "rank": rank,
                    "recommended": rank == 1,
                    "map": str(Path("maps") / map_name),
                    "exclusive_must_visit_poi_id": exclusive_id,
                    "exclusive_must_visit_name": exclusive_name,
                    **day_json,
                }
            )

        primary_route_ids = (
            _route_place_ids(selected[0][0]) if selected else set()
        )
        remaining_pois = [
            p for p in pois if str(p.place_id) not in primary_route_ids
        ]
        remaining_must_visit_ids = {
            str(p.place_id) for p in remaining_pois if _is_must_see(p)
        }
        secondary_itinerary = None
        disjoint_pool = (
            remaining_pois
            if len(remaining_pois) >= MIN_POIS_PER_ROUTE
            else []
        )
        secondary_pool = disjoint_pool or pois
        secondary_candidates: list[Individual] = []
        secondary_history: list[float] = []
        if selected and secondary_pool:
            if secondary_pool is not pois:
                prepare_day_matrices(secondary_pool, use_osrm=use_osrm)
            secondary_candidates, secondary_history = optimize_route_ga(
                secondary_pool,
                keep_top_n=ALTERNATIVE_CANDIDATE_POOL,
                diversity_tracker=global_diversity_tracker,
                fitness_weights=day_fitness_weights,
                tag_adjustments=tag_adjustments,
                preference_state=preference_state,
            )
            secondary_selected = select_secondary_itinerary_alternatives(
                secondary_candidates,
                desired_count=ALTERNATIVE_COUNT,
                preferred_must_visit_ids=remaining_must_visit_ids,
                disjoint_ids=primary_route_ids if disjoint_pool else None,
            )
            secondary_alternatives = []
            for rank, (ind, exclusive_id) in enumerate(secondary_selected, start=1):
                ga_conv = (
                    secondary_history
                    if (
                        rank == 1
                        and include_ga_history
                        and secondary_history
                    )
                    else None
                )
                day_json = build_day_json(
                    day, ind, day_pool=secondary_pool, ga_convergence=ga_conv
                )
                day_json = _augment_day_json_with_hotel_round_trip(
                    day_json, hotel_anchor, use_osrm=use_osrm
                )
                map_name = create_route_map_from_json(
                    f"module4_day_{day}_secondary_rank_{rank}",
                    day_json,
                    hotel=hotel_anchor,
                )
                exclusive_name = _resolve_exclusive_must_visit_name(
                    ind, exclusive_id
                )
                secondary_alternatives.append(
                    {
                        "rank": rank,
                        "recommended": rank == 1,
                        "map": str(Path("maps") / map_name),
                        "exclusive_must_visit_poi_id": exclusive_id,
                        "exclusive_must_visit_name": exclusive_name,
                        **day_json,
                    }
                )
            secondary_itinerary_qa = None
            if use_llm_secondary_itinerary_qa and secondary_alternatives:
                secondary_itinerary_qa = evaluate_itinerary_qa(
                    secondary_alternatives[0].get("route") or [],
                    day,
                )
            secondary_itinerary = {
                "alternatives": secondary_alternatives,
                "recommended_route": (
                    secondary_alternatives[0]
                    if secondary_alternatives
                    else None
                ),
                "disjoint_from_primary": bool(disjoint_pool),
                "remaining_must_visit_ids": sorted(remaining_must_visit_ids),
                "itinerary_qa": secondary_itinerary_qa,
            }

        routes[f"day_{day}"] = {
            "day": day,
            "alternatives": alternatives,
            "recommended_route": alternatives[0] if alternatives else None,
            "secondary_itinerary": secondary_itinerary,
            "itinerary_qa": itinerary_qa,
            "itinerary_retry_attempted": itinerary_retry_attempted,
            "itinerary_retry_details": itinerary_retry_details,
        }

        if alternatives:
            route_maps[f"day_{day}"] = alternatives[0]["map"]
            best_route = selected[0][0].route if selected else []
            for poi in best_route:
                for tag in _poi_balance_tags(poi):
                    if tag in global_diversity_tracker:
                        global_diversity_tracker[tag] += 1
                subtype = _religious_subtype(poi)
                if subtype in global_diversity_tracker:
                    global_diversity_tracker[subtype] += 1
            if preference_tracker:
                pref_counts = _count_preference_tags_in_route(best_route)
                for tag, count in pref_counts.items():
                    if tag in preference_tracker:
                        preference_tracker[tag] += count

    result = {
        "num_days": payload["num_days"],
        "travel_type": travel_type,
        "travel_distance": payload.get("travel_distance"),
        "hotel_location": payload.get("hotel_location"),
        "hotel_address": payload.get("hotel_address"),
        "hotel_lat": payload.get("hotel_lat"),
        "hotel_lon": payload.get("hotel_lon"),
        "region": payload.get("region"),
        "fitness_profile_source": fitness_profile.source,
        "routes": routes,
        "module1_run_id": module1["run_id"],
        "module1_interests_source": module1.get("interests_source", "keyword"),
        "preference_extraction": module1.get("preference_extraction"),
        "module2_run_id": module2["run_id"],
        "module2_radius_filter": module2.get("radius_filter"),
        "route_maps": route_maps,
        "global_diversity_tracker": global_diversity_tracker,
        "preference_targets": preference_targets,
        "preference_ignored": preference_ignored,
        "preference_tracker": preference_tracker,
    }

    run_id = uuid.uuid4().hex[:8]
    out_file = EXPORTS_DIR / f"optimized_routes_{run_id}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    result["generated_files"] = {
        "optimized_routes": str(Path("exports") / out_file.name),
        "separate_days": save_days_separately({"routes": {k: v["recommended_route"] for k, v in routes.items()}}, trip_name=f"trip_{run_id}"),
        "verify": verify_saved_files(),
    }
    return result
