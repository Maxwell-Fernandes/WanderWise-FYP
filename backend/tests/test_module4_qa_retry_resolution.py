"""Groq QA retry: resolve flagged names and fitness penalties for flagged place_ids."""

import sys

sys.path.append("/home/maxwell/Desktop/WanderWise/backend")

from app.services.module4_service import (
    FitnessWeights,
    POI,
    evaluate_fitness,
    prepare_day_matrices,
    resolve_qa_flagged_place_ids,
)


def test_resolve_qa_flagged_matches_route_stop():
    pois = [
        POI("Calangute Beach", 15.5, 73.8, 0.9, place_id="p1"),
        POI("Fort Aguada", 15.49, 73.78, 0.85, place_id="p2"),
    ]
    route = [
        {"name": "Calangute Beach", "poi_id": "p1"},
        {"name": "Fort Aguada", "poi_id": "p2"},
    ]
    ids, resolved = resolve_qa_flagged_place_ids(
        [{"name": "Calangute Beach", "reason": "redundant"}],
        route,
        pois,
    )
    assert "p1" in ids
    assert len(resolved) == 1
    assert resolved[0]["place_id"] == "p1"


def test_evaluate_fitness_qa_flagged_penalty():
    p1 = POI("A", 15.4, 73.9, 0.9, place_id="id-a")
    p2 = POI("B", 15.5, 74.0, 0.85, place_id="id-b")
    route = [p1, p2]
    prepare_day_matrices(route, use_osrm=False)
    base = evaluate_fitness(route, weights=FitnessWeights())
    pen = evaluate_fitness(
        route,
        weights=FitnessWeights(),
        penalty_place_ids=frozenset({"id-a"}),
    )
    assert pen.itinerary_qa_place_penalty > 0
    assert pen.wrong_time_penalty > base.wrong_time_penalty
