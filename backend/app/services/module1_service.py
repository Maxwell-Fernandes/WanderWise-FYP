from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path
from typing import Any, Dict, List

import folium
import pandas as pd

from app.config import EXPORTS_DIR, GROQ_API_KEY, MAPS_DIR
from app.utils.data_loader import ensure_output_dirs, filter_within_goa, load_dataset

logger = logging.getLogger(__name__)

CATEGORY_KEYWORDS = {
    "adventure": [
        "trek",
        "safari",
        "jeep",
        "adventure",
        "zip",
        "paragliding",
        "scuba",
        "diving",
        "kayak",
        "bungee",
        "water sports",
        "watersports",
        "water-sports",
    ],
    "beaches": ["beach", "shore", "coast", "sand", "jetty", "seaside"],
    "food": [
        "market",
        "food",
        "cuisine",
        "restaurant",
        "cafe",
        "shack",
        "spice",
        "plantation",
        "tasting",
    ],
    "fort": ["fort", "fortress", "citadel"],
    "historical": [
        "fort",
        "museum",
        "heritage",
        "historical",
        "old",
        "ancient",
        "colonial",
        "arch",
        "gateway",
        "ruins",
        "palace",
        "cathedral",
        "basilica",
        "se cathedral",
        "tower",
        "archaeological",
    ],
    "nature": [
        "waterfall",
        "falls",
        "wildlife",
        "sanctuary",
        "nature",
        "park",
        "garden",
        "spring",
        "dam",
        "forest",
        "bird",
        "butterfly",
        "plantation",
        "mangrove",
    ],
    "nightlife": ["club", "nightlife", "party", "disco", "bar", "lounge", "casino"],
    "peaceful": ["peaceful", "calm", "quiet", "serene", "tranquil", "laid back"],
    "photography": ["photography", "photo", "photogenic", "sunset", "sunrise"],
    "relaxation": ["relax", "relaxation", "relaxing", "chill", "leisure"],
    "religious": [
        "temple",
        "church",
        "basilica",
        "cathedral",
        "chapel",
        "mosque",
        "shrine",
        "monastery",
        "convent",
        "mahadeva",
        "shri",
        "bom jesus",
    ],
    "scenic": ["scenic", "view", "viewpoint", "vista", "panorama", "panoramic"],
    "shopping": ["market", "shopping", "bazaar", "mall", "store", "flea market"],
    "water sports": ["water sports", "watersports", "water-sports", "jet ski", "parasail"],
}


def classify_place(place_name: str, place_types: str, address: str) -> List[str]:
    text = f"{place_name} {place_types} {address}".lower()
    categories = [cat for cat, kws in CATEGORY_KEYWORDS.items() if any(kw in text for kw in kws)]
    return categories or ["other"]


def simulate_nlc_classification(user_input: str) -> Dict[str, bool]:
    text = user_input.lower()
    negative_words = ["hate", "dislike", "not interested", "avoid", "boring", "no "]
    results: Dict[str, bool] = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        if not any(keyword in text for keyword in keywords):
            continue
        is_negative = False
        for neg_word in negative_words:
            if neg_word not in text:
                continue
            neg_pos = text.find(neg_word)
            for keyword in keywords:
                if keyword in text:
                    kw_pos = text.find(keyword)
                    if 0 <= kw_pos - neg_pos <= 50:
                        is_negative = True
                        break
        results[category] = not is_negative
    return results


def filter_places_by_interests(
    df: pd.DataFrame,
    positive_interests: List[str],
    negative_interests: List[str],
    min_rating: float = 3,
) -> pd.DataFrame:
    """Filter by category interests. Supports negatives-only (exclude categories)."""

    def has_negative_interest(categories: list[str]) -> bool:
        return any(cat in negative_interests for cat in categories)

    base = df["rating"] >= min_rating

    if not positive_interests and not negative_interests:
        return df[base].copy()

    if not positive_interests and negative_interests:
        return df[~df["categories"].apply(has_negative_interest) & base].copy()

    def has_positive_interest(categories: list[str]) -> bool:
        return any(cat in positive_interests for cat in categories)

    return df[
        df["categories"].apply(has_positive_interest)
        & ~df["categories"].apply(has_negative_interest)
        & base
    ].copy()


def _row_search_text(row: pd.Series) -> str:
    parts = [
        str(row.get("name", "")),
        str(row.get("types", "")),
        str(row.get("address", "")),
    ]
    return " ".join(parts).lower()


def _keyword_match_score(text: str, themes: List[str]) -> float:
    return float(sum(1 for k in themes if k and k in text))


def _mentioned_place_boost(text: str, fragments: List[str]) -> float:
    boost = 0.0
    for frag in fragments:
        f = frag.lower().strip()
        if len(f) < 2:
            continue
        if f in text:
            boost += 2.0
            continue
        for part in f.split():
            if len(part) > 3 and part in text:
                boost += 0.5
    return boost


def rerank_places_by_extraction(
    df: pd.DataFrame, preference_extraction: dict[str, Any] | None
) -> pd.DataFrame:
    """Sort filtered rows by theme/mention overlap, then rating (soft rerank)."""
    if df.empty:
        return df
    themes: list[str] = []
    places: list[str] = []
    if preference_extraction:
        themes = preference_extraction.get("themes_keywords") or []
        places = preference_extraction.get("mentioned_places") or []
    if not themes and not places:
        return df.sort_values(["rating", "user_ratings_total"], ascending=[False, False])

    def score_row(row: pd.Series) -> float:
        t = _row_search_text(row)
        return _keyword_match_score(t, themes) + _mentioned_place_boost(t, places)

    out = df.copy()
    out["_extraction_score"] = out.apply(score_row, axis=1)
    out = out.sort_values(
        ["_extraction_score", "rating", "user_ratings_total"],
        ascending=[False, False, False],
    )
    return out.drop(columns=["_extraction_score"])


def get_marker_color(categories: List[str]) -> str:
    if "beaches" in categories:
        return "blue"
    if "historical" in categories:
        return "purple"
    if "nature" in categories:
        return "green"
    if "adventure" in categories:
        return "red"
    return "gray"


def create_folium_map(df: pd.DataFrame, map_name: str) -> str:
    if df.empty:
        m = folium.Map(location=[15.4, 73.9], zoom_start=9)
    else:
        m = folium.Map(location=[df["latitude"].mean(), df["longitude"].mean()], zoom_start=10)
        for _, row in df.iterrows():
            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                popup=f"{row['name']}<br>Rating: {row['rating']}",
                tooltip=row["name"],
                icon=folium.Icon(color=get_marker_color(row["categories"])),
            ).add_to(m)

    path = MAPS_DIR / map_name
    m.save(path)
    return map_name


def run_module1_simulation(
    user_preference: str,
    min_rating: float = 3.0,
    use_llm_interests: bool = False,
) -> dict:
    ensure_output_dirs()
    df = load_dataset().copy()
    # Notebook parity: keep only places inside Goa boundary polygon from goa.geojson.
    df = filter_within_goa(df)
    df["categories"] = df.apply(lambda row: classify_place(str(row["name"]), str(row.get("types", "")), str(row.get("address", ""))), axis=1)

    interests_source = "keyword"
    preference_extraction: dict[str, Any] | None = None
    if use_llm_interests and GROQ_API_KEY.strip():
        from app.services.module1_interests_llm import (
            interests_lists_to_dict,
            resolve_module1_interests_llm,
        )

        try:
            llm_result = resolve_module1_interests_llm(user_preference)
            positive_interests = llm_result.positive_interests
            negative_interests = llm_result.negative_interests
            user_interests = interests_lists_to_dict(positive_interests, negative_interests)
            preference_extraction = (
                llm_result.preference_extraction if llm_result.preference_extraction else None
            )
            interests_source = "groq"
        except Exception as exc:
            logger.warning("Module1 Groq interests failed, using keyword classifier: %s", exc)
            preference_extraction = None
            user_interests = simulate_nlc_classification(user_preference)
            positive_interests = [k for k, v in user_interests.items() if v]
            negative_interests = [k for k, v in user_interests.items() if not v]
            interests_source = "fallback"
    else:
        user_interests = simulate_nlc_classification(user_preference)
        positive_interests = [k for k, v in user_interests.items() if v]
        negative_interests = [k for k, v in user_interests.items() if not v]

    filtered_places = filter_places_by_interests(df, positive_interests, negative_interests, min_rating=min_rating)
    filtered_places = rerank_places_by_extraction(filtered_places, preference_extraction)

    run_id = uuid.uuid4().hex[:8]
    csv_name = f"module1_filtered_places_{run_id}.csv"
    json_name = f"module1_filtered_places_{run_id}.json"
    map_name = f"module1_filtered_places_map_{run_id}.html"

    filtered_places.to_csv(EXPORTS_DIR / csv_name, index=False)
    records = filtered_places.to_dict(orient="records")
    preview_records = filtered_places.head(300).to_dict(orient="records")
    with open(EXPORTS_DIR / json_name, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, default=str)

    saved_map = create_folium_map(filtered_places.head(400), map_name)

    return {
        "run_id": run_id,
        "interests_source": interests_source,
        "preference_extraction": preference_extraction,
        "user_interests": user_interests,
        "positive_interests": positive_interests,
        "negative_interests": negative_interests,
        "counts": {"original": int(len(df)), "filtered": int(len(filtered_places))},
        "places": records,
        "places_preview": preview_records,
        "generated_files": {
            "csv": str(Path("exports") / csv_name),
            "json": str(Path("exports") / json_name),
            "map": str(Path("maps") / saved_map),
        },
    }
