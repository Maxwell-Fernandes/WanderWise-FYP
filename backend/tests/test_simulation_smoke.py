import sys

sys.path.append("/home/maxwell/Desktop/WanderWise/backend")

from app.services.module1_service import run_module1_simulation
from app.services.module2_service import run_module2_simulation
from app.services.module4_service import run_module4_simulation


def test_module1_smoke():
    result = run_module1_simulation(
        "I like beaches and historical places but not nightlife", 3.0
    )
    assert result["counts"]["original"] > 0
    assert result["counts"]["filtered"] > 0
    assert result["generated_files"]["map"].endswith(".html")


def test_module2_smoke():
    result = run_module2_simulation(3, min_reviews=100, random_state=42)
    assert len(result["cluster_counts"]) == 3
    assert result["generated_files"]["json"].endswith(".json")
    assert result["generated_files"]["map"].endswith(".html")


def test_module4_smoke():
    result = run_module4_simulation(
        {
            "num_days": 2,
            "user_preference": "I love beaches, waterfalls, forts",
            "travel_type": "family",
            "min_rating": 3.0,
            "population_size": 20,
            "max_generations": 5,
            "mutation_rate": 0.2,
            "crossover_rate": 0.7,
            "random_state": 42,
            "use_osrm": False,
        }
    )
    assert result["num_days"] == 2
    assert result["travel_type"] == "family"
    assert result["fitness_profile_source"] == "baseline"
    assert len(result["routes"]) >= 1
    assert "global_diversity_tracker" in result

    def route_diff_percent(a, b):
        a_ids = {x.get("poi_id") for x in (a or [])}
        b_ids = {x.get("poi_id") for x in (b or [])}
        union = a_ids | b_ids
        if not union:
            return 0.0
        inter = a_ids & b_ids
        return (1.0 - (len(inter) / len(union))) * 100.0

    for _, day_data in result["routes"].items():
        assert "itinerary_qa" in day_data
        assert "itinerary_retry_details" in day_data
        assert day_data.get("itinerary_retry_attempted") is False
        alternatives = day_data.get("alternatives", [])
        if not alternatives:
            continue
        chosen = alternatives[0]
        assert "nearby_suggestions_total" in chosen
        assert "fitness_breakdown" in chosen
        assert chosen["fitness_breakdown"]["formula"] == "reward_over_one_plus_delta"
        assert "constraint_violations" in chosen
        assert "beach_streak_violations" in chosen["constraint_violations"]
        assert "beach_scorch_overlap_min" in chosen["constraint_violations"]
        for stop in chosen.get("route", []):
            assert "nearby_suggestions" in stop
            for s in stop["nearby_suggestions"]:
                assert s["poi_id"] != stop["poi_id"]

        if len(alternatives) >= 2:
            diff = route_diff_percent(
                alternatives[0].get("route", []), alternatives[1].get("route", [])
            )
            assert diff >= 40.0
