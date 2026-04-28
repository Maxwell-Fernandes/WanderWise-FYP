import ast
import json
from functools import lru_cache

import pandas as pd
from shapely.geometry import Point, shape

from app.config import DATASET_PATH, EXPORTS_DIR, GOA_GEOJSON_PATH, MAPS_DIR


@lru_cache(maxsize=1)
def load_dataset() -> pd.DataFrame:
    df = pd.read_csv(DATASET_PATH)
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0)
    df["user_ratings_total"] = pd.to_numeric(df["user_ratings_total"], errors="coerce").fillna(0)
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    if "categories" in df.columns:
        df["categories"] = df["categories"].apply(parse_categories)
    return df.dropna(subset=["latitude", "longitude", "name"]).copy()


def parse_categories(value: object) -> list[str]:
    if isinstance(value, list):
        return value
    if not isinstance(value, str):
        return []
    try:
        parsed = ast.literal_eval(value)
        if isinstance(parsed, list):
            return [str(x).strip().lower() for x in parsed]
    except (SyntaxError, ValueError):
        pass
    parts = [x.strip().lower() for x in value.split(",") if x.strip()]
    return parts


def ensure_output_dirs() -> None:
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    MAPS_DIR.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def load_goa_boundary():
    with open(GOA_GEOJSON_PATH, encoding="utf-8") as f:
        geo = json.load(f)
    return shape(geo["features"][0]["geometry"])


def filter_within_goa(df: pd.DataFrame) -> pd.DataFrame:
    goa = load_goa_boundary()
    mask = df.apply(
        lambda r: goa.contains(Point(float(r["longitude"]), float(r["latitude"]))), axis=1
    )
    return df[mask].copy()
