"""Tests for hotel round-trip distance helpers used in Module 4 map outputs."""

import sys

sys.path.append("/home/maxwell/Desktop/WanderWise/backend")

from app.services.module4_service import (  # noqa: E402
    _augment_day_json_with_hotel_round_trip,
    compute_round_trip_distance_km,
)


def test_compute_round_trip_distance_km_requires_all_parts():
    assert compute_round_trip_distance_km(None, 1.0, 1.0) is None
    assert compute_round_trip_distance_km(10.0, None, 1.0) is None
    assert compute_round_trip_distance_km(10.0, 1.0, None) is None


def test_compute_round_trip_distance_km_sums_values():
    assert compute_round_trip_distance_km(10.0, 2.5, 3.5) == 16.0


def test_augment_day_json_adds_hotel_fields_and_round_trip():
    day_json = {
        "day": 1,
        "route": [
            {"sequence": 1, "name": "A", "latitude": 15.0, "longitude": 74.1},
            {"sequence": 2, "name": "B", "latitude": 15.0, "longitude": 74.2},
        ],
        "total_distance_km": 10.0,
    }
    hotel = {"latitude": 15.0, "longitude": 74.0, "label": "Test Hotel"}

    out = _augment_day_json_with_hotel_round_trip(day_json, hotel, use_osrm=False)

    assert out["hotel"]["label"] == "Test Hotel"
    assert out["hotel_to_first_distance_km"] is not None
    assert out["last_to_hotel_distance_km"] is not None
    assert out["round_trip_total_distance_km"] is not None

    # Sanity: round trip should be larger than the POI-only distance.
    assert out["round_trip_total_distance_km"] > out["total_distance_km"]
