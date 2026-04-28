import sys

sys.path.append("/home/maxwell/Desktop/WanderWise/backend")

from app.services.module2_service import run_module2_simulation


def _make_place(
    name: str,
    place_id: str,
    lat: float,
    lon: float,
    rating: float,
    reviews: int,
    address: str,
    categories: list[str],
    types: str,
) -> dict:
    return {
        "name": name,
        "address": address,
        "rating": rating,
        "user_ratings_total": reviews,
        "place_id": place_id,
        "types": types,
        "latitude": lat,
        "longitude": lon,
        "categories": categories,
    }


def test_travel_less_radius_adds_exceptions():
    places = []
    for i in range(8):
        places.append(
            _make_place(
                name=f"Panjim Spot {i}",
                place_id=f"panjim-{i}",
                lat=15.49 + i * 0.002,
                lon=73.82 + i * 0.002,
                rating=4.2,
                reviews=400 + i * 10,
                address="Panjim, Goa",
                categories=["beaches"] if i % 2 == 0 else ["historical"],
                types="tourist_attraction, beach",
            )
        )

    places.append(
        _make_place(
            name="Far Beach",
            place_id="far-beach",
            lat=15.0,
            lon=74.0,
            rating=4.9,
            reviews=5000,
            address="Canacona, Goa",
            categories=["beaches"],
            types="beach",
        )
    )
    places.append(
        _make_place(
            name="Far Fort",
            place_id="far-fort",
            lat=15.02,
            lon=74.05,
            rating=4.8,
            reviews=6000,
            address="Canacona, Goa",
            categories=["historical"],
            types="fort",
        )
    )

    result = run_module2_simulation(
        2,
        min_reviews=1,
        random_state=42,
        input_places=places,
        travel_distance="less",
        hotel_location="panjim",
        positive_interests=["beaches"],
    )

    radius_filter = result.get("radius_filter") or {}
    assert radius_filter.get("enabled") is True
    assert radius_filter.get("anchor", {}).get("source") == "hotel_location"
    assert radius_filter.get("exceptions_added", 0) >= 1
    place_ids = {p.get("place_id") for p in result.get("places", [])}
    assert "far-beach" in place_ids


def test_travel_less_anchor_fallback_warning():
    places = [
        _make_place(
            name="Remote Spot 1",
            place_id="remote-1",
            lat=15.2,
            lon=73.9,
            rating=4.0,
            reviews=200,
            address="Unknown Area, Goa",
            categories=["nature"],
            types="tourist_attraction",
        ),
        _make_place(
            name="Remote Spot 2",
            place_id="remote-2",
            lat=15.25,
            lon=73.95,
            rating=4.1,
            reviews=220,
            address="Unknown Area, Goa",
            categories=["historical"],
            types="fort",
        ),
    ]

    result = run_module2_simulation(
        1,
        min_reviews=1,
        random_state=42,
        input_places=places,
        travel_distance="less",
        hotel_location="panjim",
        positive_interests=["nature"],
    )

    radius_filter = result.get("radius_filter") or {}
    assert radius_filter.get("enabled") is True
    assert radius_filter.get("anchor", {}).get("source") == "dataset_mean"
    assert radius_filter.get("anchor_warning")
