"""Tests for travel-type fitness weight profiles in Module 4 GA."""

import sys

sys.path.append("/home/maxwell/Desktop/WanderWise/backend")

from app.services.module4_service import (
    FitnessWeights,
    Individual,
    POI,
    build_day_json,
    evaluate_fitness,
    get_fitness_weights,
    prepare_day_matrices,
)


def test_get_fitness_weights_defaults_invalid_to_solo():
    w = get_fitness_weights("not_a_type")
    assert w == FitnessWeights()


def test_get_fitness_weights_family_stronger_fatigue_than_solo():
    solo = get_fitness_weights("solo")
    family = get_fitness_weights("family")
    assert family.fatigue > solo.fatigue


def test_evaluate_fitness_scales_delta_by_weights():
    p1 = POI(
        "Test A",
        15.4,
        73.9,
        0.9,
        place_id="t-a",
        rating=4.0,
        poi_type="tourist_attraction",
    )
    p2 = POI(
        "Test B",
        15.5,
        74.0,
        0.85,
        place_id="t-b",
        rating=4.0,
        poi_type="tourist_attraction",
    )
    route = [p1, p2]
    prepare_day_matrices(route, use_osrm=False)

    base = evaluate_fitness(route, weights=FitnessWeights())
    boosted_distance = evaluate_fitness(
        route,
        weights=FitnessWeights(distance=3.0),
    )

    assert boosted_distance.delta > base.delta
    assert boosted_distance.fitness < base.fitness


def test_family_and_solo_produce_different_fitness_same_route():
    p1 = POI(
        "Test A",
        15.4,
        73.9,
        0.9,
        place_id="t-a2",
        rating=4.0,
        poi_type="tourist_attraction",
    )
    p2 = POI(
        "Test B",
        15.5,
        74.0,
        0.85,
        place_id="t-b2",
        rating=4.0,
        poi_type="tourist_attraction",
    )
    route = [p1, p2]
    prepare_day_matrices(route, use_osrm=False)

    solo_eval = evaluate_fitness(route, weights=get_fitness_weights("solo"))
    family_eval = evaluate_fitness(route, weights=get_fitness_weights("family"))

    assert family_eval.delta != solo_eval.delta
    assert family_eval.fitness != solo_eval.fitness


def test_build_day_json_includes_fitness_breakdown():
    p1 = POI(
        "Test A",
        15.4,
        73.9,
        0.9,
        place_id="t-a3",
        rating=4.0,
        poi_type="tourist_attraction",
    )
    route = [p1]
    prepare_day_matrices(route, use_osrm=False)
    ind = Individual(route, route, fitness_weights=FitnessWeights())
    ind.evaluate()
    day = build_day_json(1, ind, day_pool=route, ga_convergence=[0.1, 0.2, 0.3])
    assert day["fitness_breakdown"]["formula"] == "reward_over_one_plus_delta"
    assert "delta" in day["fitness_breakdown"]
    assert day["fitness_breakdown"]["total_reward"] == ind.evaluation.total_reward
    assert "raw_components" in day["fitness_breakdown"]
    assert day["ga_convergence"] == [0.1, 0.2, 0.3]
    assert "beach_scorch_overlap_min" in day["constraint_violations"]
