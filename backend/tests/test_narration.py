import sys

from fastapi.testclient import TestClient

sys.path.append("/home/maxwell/Desktop/WanderWise/backend")

from app.main import app
from app.services.description_context_service import get_place_context
from app.services.itinerary_narration_service import generate_day_narration


def test_description_context_matching():
    ctx = get_place_context("Baga Beach", categories=["beaches"])
    assert "matched" in ctx
    assert "summary" in ctx
    assert "match_score" in ctx


def test_narration_fallback_generation():
    payload = {
        "day": 1,
        "rank": 1,
        "user_preference": "I love forts and beaches",
        "route": [
            {
                "sequence": 1,
                "name": "Baga Beach",
                "arrival_time": "09:20",
                "visit_start": "09:20",
                "visit_end": "10:20",
            },
            {
                "sequence": 2,
                "name": "Aguada Fort",
                "arrival_time": "11:00",
                "visit_start": "11:00",
                "visit_end": "12:00",
            },
        ],
    }
    result = generate_day_narration(payload)
    assert result["provider"] in {"fallback", "modal"}
    assert isinstance(result["narration_text"], str)
    assert len(result["narration_text"]) > 20


def test_narration_endpoint_smoke():
    client = TestClient(app)
    response = client.post(
        "/api/module4/narrate-day",
        json={
            "day": 1,
            "rank": 1,
            "user_preference": "historical forts and beaches",
            "route": [
                {
                    "sequence": 1,
                    "poi_id": "a",
                    "name": "Baga Beach",
                    "arrival_time": "09:15",
                    "visit_start": "09:15",
                    "visit_end": "10:15",
                }
            ],
        },
    )
    assert response.status_code == 200
    body = response.json()["data"]
    assert "narration_text" in body
    assert "provider" in body
