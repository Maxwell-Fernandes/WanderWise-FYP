from __future__ import annotations

import json
import re
import uuid
from pathlib import Path
from typing import Any

import folium
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

from app.config import EXPORTS_DIR, MAPS_DIR
from app.services.ga_config import MIN_POIS_PER_ROUTE
from app.services.module1_service import classify_place, simulate_nlc_classification
from app.utils.data_loader import ensure_output_dirs, load_dataset, parse_categories

QUALITY_WEIGHT = 0.6
QUANTITY_WEIGHT = 0.4
MUST_SEE_WPI_THRESHOLD = 0.85
TRAVEL_LESS_BASE_RADIUS_KM = 20.0
TRAVEL_LESS_STEP_KM = 5.0
TRAVEL_LESS_MAX_RADIUS_KM = 60.0
MIN_EXCEPTION_CAP = 10
HOTEL_DISTANCE_FEATURE_WEIGHT = 0.05
TRAVEL_LESS_EXCEPTION_PER_DAY = 2
FIRST_STOP_RADIUS_BUFFER_KM = 0.0

HOTEL_LOCATION_TERMS = {
    "panjim": ["panjim", "panaji"],
    "margao": ["margao", "madgaon"],
    "mapusa": ["mapusa", "mapuca"],
    "canacona": ["canacona", "cancona"],
}

REGION_TERMS = {
    "north": [
        "pernem",
        "bardez",
        "mapusa",
        "bicholim",
        "calangute",
        "candolim",
        "anjuna",
        "vagator",
        "arambol",
        "morjim",
        "mandrem",
    ],
    "central": [
        "panjim",
        "panaji",
        "tiswadi",
        "ponda",
        "porvorim",
        "old goa",
        "mormugao",
        "vasco",
        "dona paula",
    ],
    "south": [
        "margao",
        "madgaon",
        "salcete",
        "sanguem",
        "canacona",
        "palolem",
        "agonda",
        "colva",
        "benaulim",
        "cavelossim",
        "quepe",
        "quepem",
    ],
}


def check_location(row: pd.Series) -> bool:
    return 14.8 <= float(row["latitude"]) <= 15.9 and 73.6 <= float(row["longitude"]) <= 74.4


def _is_within_goa(lat: float, lon: float) -> bool:
    return 14.8 <= lat <= 15.9 and 73.6 <= lon <= 74.4


def _normalize_text(value: object) -> str:
    return str(value or "").strip().lower()


def _normalize_terms(values: list[str]) -> list[str]:
    return [v for v in (_normalize_text(x) for x in values) if v]


def _interest_forms(term: str) -> list[str]:
    base = _normalize_text(term)
    if not base:
        return []
    forms = {base}
    if base.endswith("es"):
        forms.add(base[:-2])
    if base.endswith("s"):
        forms.add(base[:-1])
    return [f for f in forms if f]


def _tokenize_types(value: object) -> list[str]:
    if isinstance(value, list):
        return _normalize_terms([str(v) for v in value])
    text = _normalize_text(value)
    if not text:
        return []
    parts = [p.strip() for p in text.replace(";", ",").split(",")]
    tokens: list[str] = []
    for part in parts:
        part = part.replace("_", " ").strip()
        if part:
            tokens.append(part)
    return _normalize_terms(tokens)


def _interest_match_score(row: pd.Series, interests: list[str]) -> int:
    if not interests:
        return 0
    categories = row.get("categories", [])
    if not isinstance(categories, list):
        categories = parse_categories(categories)
    categories = _normalize_terms([str(c) for c in categories])
    types_tokens = _tokenize_types(row.get("types", row.get("type", "")))
    search_space = categories + types_tokens
    score = 0
    for interest in interests:
        matched = False
        for form in _interest_forms(interest):
            if any(form in token for token in search_space):
                matched = True
                break
        if matched:
            score += 1
    return score


def _match_terms_mask(df: pd.DataFrame, terms: list[str]) -> pd.Series:
    if not terms:
        return pd.Series(False, index=df.index)
    pattern = "|".join(re.escape(term) for term in terms if term)
    if not pattern:
        return pd.Series(False, index=df.index)
    address = df["address"] if "address" in df.columns else pd.Series("", index=df.index)
    taluka = df["taluka"] if "taluka" in df.columns else pd.Series("", index=df.index)
    name = df["name"] if "name" in df.columns else pd.Series("", index=df.index)
    text = (
        address.fillna("") + " " + taluka.fillna("") + " " + name.fillna("")
    ).str.lower()
    return text.str.contains(pattern, case=False, na=False)


def _resolve_anchor(
    df: pd.DataFrame,
    hotel_location: str | None,
    region: str | None,
    hotel_lat: float | None,
    hotel_lon: float | None,
    hotel_address: str | None,
) -> tuple[float, float, str, int, str | None, str | None]:
    warning: str | None = None
    if hotel_lat is not None or hotel_lon is not None:
        try:
            lat = float(hotel_lat) if hotel_lat is not None else float("nan")
            lon = float(hotel_lon) if hotel_lon is not None else float("nan")
        except (TypeError, ValueError):
            warning = "Invalid hotel coordinates; using fallback anchor."
        else:
            if np.isfinite(lat) and np.isfinite(lon) and _is_within_goa(lat, lon):
                label = hotel_address or "custom_hotel"
                return (lat, lon, "hotel_coordinates", 1, label, None)
            warning = "Hotel coordinates outside Goa bounds; using fallback anchor."

    if hotel_location:
        key = _normalize_text(hotel_location)
        terms = HOTEL_LOCATION_TERMS.get(key, [key])
        mask = _match_terms_mask(df, terms)
        if mask.any():
            subset = df[mask]
            return (
                float(subset["latitude"].mean()),
                float(subset["longitude"].mean()),
                "hotel_location",
                int(mask.sum()),
                key,
                warning,
            )

    if region:
        key = _normalize_text(region)
        terms = REGION_TERMS.get(key, [key])
        mask = _match_terms_mask(df, terms)
        if mask.any():
            subset = df[mask]
            return (
                float(subset["latitude"].mean()),
                float(subset["longitude"].mean()),
                "region",
                int(mask.sum()),
                key,
                warning,
            )

    return (
        float(df["latitude"].mean()),
        float(df["longitude"].mean()),
        "dataset_mean",
        int(len(df)),
        None,
        warning,
    )


def _haversine_km_array(lat_series: pd.Series, lon_series: pd.Series, lat: float, lon: float) -> pd.Series:
    lat1 = np.radians(lat_series.astype(float))
    lon1 = np.radians(lon_series.astype(float))
    lat2 = np.radians(lat)
    lon2 = np.radians(lon)
    dlat = lat1 - lat2
    dlon = lon1 - lon2
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    return 6371.0 * c


def _build_cluster_features(
    df: pd.DataFrame, anchor_lat: float | None, anchor_lon: float | None
) -> tuple[np.ndarray, pd.Series | None]:
    coords = df[["latitude", "longitude"]].to_numpy()
    if anchor_lat is None or anchor_lon is None:
        return coords, None

    anchor_distance_km = _haversine_km_array(
        df["latitude"], df["longitude"], anchor_lat, anchor_lon
    )
    distance_feature = (anchor_distance_km.to_numpy() * HOTEL_DISTANCE_FEATURE_WEIGHT).reshape(-1, 1)
    features = np.hstack([coords, distance_feature])
    return features, anchor_distance_km


def _apply_first_stop_ordering(
    df: pd.DataFrame,
    radius_km: float,
    anchor_lat: float,
    anchor_lon: float,
    buffer_km: float = FIRST_STOP_RADIUS_BUFFER_KM,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    if "anchor_distance_km" not in df.columns:
        df = df.copy()
        df["anchor_distance_km"] = _haversine_km_array(
            df["latitude"], df["longitude"], anchor_lat, anchor_lon
        )
    threshold_km = radius_km + max(buffer_km, 0.0)
    df["within_anchor_radius"] = df["anchor_distance_km"] <= threshold_km
    df["day_rank"] = 1

    missing_days: list[int] = []
    first_stop_map: dict[str, Any] = {}

    for day in sorted(df["day"].unique()):
        day_df = df[df["day"] == day]
        within = day_df[day_df["within_anchor_radius"]]
        if not within.empty:
            first_idx = int(within["anchor_distance_km"].idxmin())
            first_stop_map[str(day)] = {
                "first_place_index": first_idx,
                "first_within_radius": True,
            }
        else:
            first_idx = int(day_df["anchor_distance_km"].idxmin())
            first_stop_map[str(day)] = {
                "first_place_index": first_idx,
                "first_within_radius": False,
            }
            missing_days.append(int(day))
        df.loc[first_idx, "day_rank"] = 0

    df = df.sort_values(
        by=["day", "day_rank", "within_anchor_radius", "anchor_distance_km"],
        ascending=[True, True, False, True],
    )

    metadata = {
        "radius_km": float(radius_km),
        "threshold_km": float(threshold_km),
        "missing_days": missing_days,
        "first_stop_by_day": first_stop_map,
    }
    return df, metadata


def _derive_positive_interests(
    user_preference: str | None, positive_interests: list[str] | None
) -> list[str]:
    if positive_interests:
        return _normalize_terms(positive_interests)
    if not user_preference:
        return []
    classification = simulate_nlc_classification(user_preference)
    return [k for k, v in classification.items() if v]


def _apply_travel_radius_filter(
    df: pd.DataFrame,
    num_days: int,
    min_reviews: int,
    random_state: int,
    hotel_location: str | None,
    hotel_address: str | None,
    hotel_lat: float | None,
    hotel_lon: float | None,
    region: str | None,
    user_preference: str | None,
    positive_interests: list[str] | None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    radius_km = min(
        TRAVEL_LESS_BASE_RADIUS_KM + TRAVEL_LESS_STEP_KM * max(num_days - 1, 0),
        TRAVEL_LESS_MAX_RADIUS_KM,
    )
    anchor_lat, anchor_lon, source, match_count, label, anchor_warning = _resolve_anchor(
        df, hotel_location, region, hotel_lat, hotel_lon, hotel_address
    )
    if source == "dataset_mean" and (hotel_location or region or hotel_lat is not None or hotel_lon is not None):
        if not anchor_warning:
            anchor_warning = "Anchor not found for provided hotel or region; using dataset mean."

    df_base = df.copy()
    features = df_base[["latitude", "longitude"]].to_numpy()
    labels, _, _ = perform_kmeans_clustering(features, num_days, random_state=random_state)
    df_base["cluster"] = labels
    df_pop, _ = calculate_popularity_score(df_base, min_reviews=min_reviews)
    df_norm = normalize_popularity_by_cluster(df_pop)
    df_norm["baseline_wpi"] = df_norm["normalized_popularity"]
    df_norm["anchor_distance_km"] = _haversine_km_array(
        df_norm["latitude"], df_norm["longitude"], anchor_lat, anchor_lon
    )

    interests = _derive_positive_interests(user_preference, positive_interests)
    min_count = max(num_days * MIN_POIS_PER_ROUTE, num_days)
    min_within = num_days
    exception_cap = max(num_days, min(min_count, num_days * TRAVEL_LESS_EXCEPTION_PER_DAY))
    radius_used = radius_km
    fallback_reason: str | None = None
    selected_idx = pd.Index([])
    exceptions_added = 0
    within_count = 0
    expanded_beyond_max = False

    while True:
        within_mask = df_norm["anchor_distance_km"] <= radius_used
        within = df_norm[within_mask]
        within_count = int(len(within))

        exceptions_added = 0
        selected_idx = within.index

        if len(selected_idx) >= min_count and within_count >= min_within:
            break
        if radius_used >= TRAVEL_LESS_MAX_RADIUS_KM:
            break
        radius_used = min(radius_used + TRAVEL_LESS_STEP_KM, TRAVEL_LESS_MAX_RADIUS_KM)

    if len(selected_idx) < min_count:
        fallback_reason = "insufficient_within_max_radius"
        filtered = df.loc[selected_idx].copy()
    else:
        filtered = df.loc[selected_idx].copy()

    metadata = {
        "enabled": True,
        "travel_distance": "less",
        "anchor": {
            "source": source,
            "label": label,
            "latitude": anchor_lat,
            "longitude": anchor_lon,
            "matched_rows": match_count,
            "address": hotel_address,
        },
        "anchor_warning": anchor_warning,
        "radius_km": float(radius_used),
        "base_radius_km": float(TRAVEL_LESS_BASE_RADIUS_KM),
        "step_km": float(TRAVEL_LESS_STEP_KM),
        "max_radius_km": float(TRAVEL_LESS_MAX_RADIUS_KM),
        "within_radius": within_count,
        "exceptions_added": exceptions_added,
        "exception_cap": int(exception_cap),
        "exception_policy": "none",
        "fallback_reason": fallback_reason,
        "expanded_beyond_max": expanded_beyond_max,
        "interest_terms": interests,
    }
    return filtered, metadata


def perform_kmeans_clustering(features: np.ndarray, num_clusters: int, random_state: int = 42):
    kmeans = KMeans(n_clusters=num_clusters, random_state=random_state, n_init=10, max_iter=300)
    labels = kmeans.fit_predict(features)
    centroids = kmeans.cluster_centers_
    return labels, centroids, kmeans


def calculate_popularity_score(df_with_clusters: pd.DataFrame, min_reviews: int = 1):
    df_pop = df_with_clusters.copy()
    df_pop["normalized_google_rating"] = (df_pop["rating"] - 1) / 4

    global_mean_rating = df_pop["rating"].mean()
    global_mean_normalized = (global_mean_rating - 1) / 4

    v = df_pop["user_ratings_total"]
    r = df_pop["normalized_google_rating"]
    m = min_reviews
    c = global_mean_normalized

    df_pop["weighted_rating"] = (v / (v + m)) * r + (m / (v + m)) * c

    cluster_max_reviews = df_pop.groupby("cluster")["user_ratings_total"].transform("max")
    df_pop["quantity_factor"] = np.log1p(df_pop["user_ratings_total"]) / np.log1p(cluster_max_reviews)
    df_pop["popularity_score"] = (QUALITY_WEIGHT * df_pop["weighted_rating"]) + (QUANTITY_WEIGHT * df_pop["quantity_factor"])

    return df_pop, float(global_mean_rating)


def normalize_popularity_by_cluster(df_with_popularity: pd.DataFrame):
    df_normalized = df_with_popularity.copy()
    cluster_max_popularity = df_normalized.groupby("cluster")["popularity_score"].transform("max")
    df_normalized["cluster_max_popularity"] = cluster_max_popularity
    
    # Handle division by zero: when cluster_max_popularity is 0 (e.g., single low-rated POI),
    # use 0.5 as default normalized popularity instead of NaN.
    # This ensures:
    # 1. No NaN values propagate to fitness calculations
    # 2. Low-value POIs get a reasonable baseline score
    # 3. GA fitness comparisons work correctly (NaN > x always False)
    def safe_normalize(row):
        if row["cluster_max_popularity"] == 0:
            return 0.5  # Default middle-ground value for zero-max clusters
        return row["popularity_score"] / row["cluster_max_popularity"]
    
    df_normalized["normalized_popularity"] = df_normalized.apply(safe_normalize, axis=1)
    return df_normalized


def create_cluster_map(
    df_clustered: pd.DataFrame,
    centroids,
    title: str = "K-Means Clustering Results",
    anchor: dict[str, Any] | None = None,
):
    m = folium.Map(location=[df_clustered["latitude"].mean(), df_clustered["longitude"].mean()], zoom_start=10)

    if anchor and anchor.get("latitude") is not None and anchor.get("longitude") is not None:
        try:
            lat = float(anchor.get("latitude"))
            lon = float(anchor.get("longitude"))
        except (TypeError, ValueError):
            lat = None
            lon = None
        if lat is not None and lon is not None:
            label = str(anchor.get("address") or anchor.get("label") or "Hotel")
            folium.Marker(
                location=[lat, lon],
                tooltip="Hotel",
                popup=f"<b>{label}</b>",
                icon=folium.Icon(color="black", icon="home", prefix="fa"),
            ).add_to(m)

    colors = ["red", "blue", "green", "purple", "orange", "darkred", "lightred", "cadetblue", "darkgreen", "pink"]
    for _, row in df_clustered.iterrows():
        c = int(row["cluster"]) % len(colors)
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=4,
            color=colors[c],
            fill=True,
            fill_opacity=0.7,
            popup=f"Day {int(row['day'])}: {row['name']}<br>WPI: {row.get('normalized_popularity', 0):.3f}",
        ).add_to(m)

    for i, centroid in enumerate(centroids):
        folium.Marker(location=[centroid[0], centroid[1]], icon=folium.Icon(color="black", icon="flag"), tooltip=f"Cluster {i+1} centroid").add_to(m)

    return m


def run_module2_simulation(
    num_days: int,
    min_reviews: int = 1,
    random_state: int = 42,
    input_places=None,
    travel_distance: str | None = None,
    hotel_location: str | None = None,
    hotel_address: str | None = None,
    hotel_lat: float | None = None,
    hotel_lon: float | None = None,
    region: str | None = None,
    user_preference: str | None = None,
    positive_interests: list[str] | None = None,
):
    ensure_output_dirs()
    if input_places is not None:
        df = pd.DataFrame(input_places).copy()
    else:
        df = load_dataset().copy()
        df = df[df.apply(check_location, axis=1)].copy()
    if "categories" in df.columns:
        df["categories"] = df["categories"].apply(parse_categories)
    else:
        df["categories"] = df.apply(
            lambda row: classify_place(
                str(row["name"]),
                str(row.get("types", "")),
                str(row.get("address", "")),
            ),
            axis=1,
        )

    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df.dropna(subset=["latitude", "longitude"]).copy()

    radius_filter: dict[str, Any] = {"enabled": False}
    travel_choice = _normalize_text(travel_distance) or "more"
    has_anchor_request = bool(
        hotel_location or region or hotel_lat is not None or hotel_lon is not None
    )
    anchor_meta: dict[str, Any] | None = None
    anchor_lat: float | None = None
    anchor_lon: float | None = None
    if travel_choice == "less":
        if len(df) >= num_days:
            df, radius_filter = _apply_travel_radius_filter(
                df,
                num_days,
                min_reviews,
                random_state,
                hotel_location,
                hotel_address,
                hotel_lat,
                hotel_lon,
                region,
                user_preference,
                positive_interests,
            )
        else:
            radius_filter = {
                "enabled": True,
                "travel_distance": "less",
                "fallback_reason": "insufficient_points",
            }

    if travel_choice == "less" and has_anchor_request and radius_filter.get("anchor"):
        anchor_meta = radius_filter["anchor"]
        anchor_lat = float(anchor_meta.get("latitude"))
        anchor_lon = float(anchor_meta.get("longitude"))
    elif has_anchor_request:
        resolved_lat, resolved_lon, source, match_count, label, anchor_warning = _resolve_anchor(
            df, hotel_location, region, hotel_lat, hotel_lon, hotel_address
        )
        if source != "dataset_mean":
            anchor_meta = {
                "source": source,
                "label": label,
                "latitude": resolved_lat,
                "longitude": resolved_lon,
                "matched_rows": match_count,
                "address": hotel_address,
            }
            anchor_lat = float(resolved_lat)
            anchor_lon = float(resolved_lon)

    if anchor_meta and not radius_filter.get("anchor"):
        radius_filter["anchor"] = anchor_meta

    cluster_count = min(num_days, len(df)) if len(df) else num_days
    features, anchor_distance = _build_cluster_features(df, anchor_lat, anchor_lon)
    if anchor_distance is not None:
        df["anchor_distance_km"] = anchor_distance
    labels, centroids, _ = perform_kmeans_clustering(
        features, cluster_count, random_state=random_state
    )
    df["cluster"] = labels
    df["day"] = labels + 1

    df_pop, global_mean = calculate_popularity_score(df, min_reviews=min_reviews)
    df_norm = normalize_popularity_by_cluster(df_pop)

    if anchor_meta and "anchor_distance_km" not in df_norm.columns:
        df_norm["anchor_distance_km"] = _haversine_km_array(
            df_norm["latitude"], df_norm["longitude"], anchor_lat, anchor_lon
        )

    if (
        travel_choice == "less"
        and anchor_meta
        and anchor_lat is not None
        and anchor_lon is not None
        and radius_filter.get("radius_km") is not None
    ):
        df_norm, first_stop_meta = _apply_first_stop_ordering(
            df_norm,
            float(radius_filter["radius_km"]),
            anchor_lat,
            anchor_lon,
        )
        radius_filter["first_stop"] = first_stop_meta

    run_id = uuid.uuid4().hex[:8]
    csv_name = f"module2_clustered_normalized_places_{run_id}.csv"
    json_name = f"module2_clusters_for_ga_{run_id}.json"
    map_name = f"module2_clustered_places_map_{run_id}.html"

    df_norm.to_csv(EXPORTS_DIR / csv_name, index=False)

    clusters = {str(day): df_norm[df_norm["day"] == day].index.tolist() for day in sorted(df_norm["day"].unique())}
    payload = {
        "trip_id": f"trip_{run_id}",
        "metadata": {"num_days": num_days, "num_locations": int(len(df_norm)), "created_by": "module2_clustering_normalization"},
        "clusters": clusters,
        "places": df_norm.to_dict(orient="records"),
    }
    with open(EXPORTS_DIR / json_name, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)

    cluster_map = create_cluster_map(df_norm, centroids, anchor=anchor_meta)
    cluster_map.save(MAPS_DIR / map_name)

    return {
        "run_id": run_id,
        "global_mean": global_mean,
        "cluster_counts": df_norm.groupby("day").size().to_dict(),
        "centroids": centroids.tolist(),
        "places": payload["places"],
        "radius_filter": radius_filter,
        "generated_files": {
            "csv": str(Path("exports") / csv_name),
            "json": str(Path("exports") / json_name),
            "map": str(Path("maps") / map_name),
        },
    }
