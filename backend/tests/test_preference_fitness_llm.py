"""Tests for Groq one-shot fitness profile resolution (mocked HTTP)."""

import sys
from unittest.mock import patch

sys.path.append("/home/maxwell/Desktop/WanderWise/backend")

from app.services.module4_service import (
    FitnessWeights,
    POI,
    evaluate_fitness,
    get_default_tag_adjustments,
    prepare_day_matrices,
)
from app.services.preference_fitness_llm import merge_fitness_weights, resolve_fitness_profile


def test_merge_fitness_weights_clamps_deltas_and_magnitude():
    base = FitnessWeights(distance=1.0, fatigue=2.0)
    merged = merge_fitness_weights(
        base,
        {"distance": 0.5, "fatigue": -99.0, "wrong_time": "bad"},
    )
    assert merged.distance == 1.5
    # fatigue delta clamped to -0.5 -> 2.0 * 0.5 = 1.0
    assert merged.fatigue == 1.0


def test_merge_fitness_weights_invalid_field_ignored():
    base = FitnessWeights()
    merged = merge_fitness_weights(base, {"distance": 0.1})
    assert merged.distance == 1.1
    assert merged.fatigue == 1.0


def test_resolve_without_llm_or_key_returns_baseline_with_travel_type_tags():
    r = resolve_fitness_profile("family", "beaches only", use_llm=False)
    assert r.source == "baseline"
    assert r.tag_adjustments.get("waterfall", 0) < 0
    assert r.tag_adjustments.get("sanctuary", 0) > 0

    with patch("app.services.preference_fitness_llm.GROQ_API_KEY", ""):
        r2 = resolve_fitness_profile("family", "beaches only", use_llm=True)
        assert r2.source == "baseline"
        assert r2.tag_adjustments.get("waterfall", 0) < 0


@patch("app.services.preference_fitness_llm.groq_chat_json")
def test_resolve_with_mocked_groq_merges_and_tags(mock_chat):
    mock_chat.return_value = (
        '{"weight_deltas": {"waterfall": 0.2, "fatigue": -0.1}, '
        '"tag_preference": {"waterfall": -0.9, "sanctuary": 0.8, "invalid": 9}}'
    )
    with patch("app.services.preference_fitness_llm.GROQ_API_KEY", "test-key"):
        r = resolve_fitness_profile("solo", "easy day", use_llm=True)
    assert r.source == "groq"
    assert "invalid" not in r.tag_adjustments
    assert r.tag_adjustments.get("waterfall") == -0.9
    assert r.tag_adjustments.get("sanctuary") == 0.8
    assert r.weights.waterfall > 1.0
    assert r.weights.fatigue < 1.0


@patch("app.services.preference_fitness_llm.groq_chat_json")
def test_resolve_groq_failure_falls_back(mock_chat):
    mock_chat.side_effect = RuntimeError("network")
    with patch("app.services.preference_fitness_llm.GROQ_API_KEY", "test-key"):
        r = resolve_fitness_profile("duo", "anything", use_llm=True)
    assert r.source == "fallback"
    assert r.tag_adjustments.get("beach", 0) > 0


def test_family_defaults_lower_fitness_for_waterfall_route_than_solo():
    p1 = POI(
        "Dudhsagar Falls Viewpoint",
        15.3,
        74.25,
        0.92,
        place_id="wf-1",
        rating=4.5,
        poi_type="natural_feature",
    )
    p2 = POI(
        "Museum Goa",
        15.45,
        73.95,
        0.75,
        place_id="m-1",
        rating=4.0,
        poi_type="museum",
    )
    route = [p1, p2]
    prepare_day_matrices(route, use_osrm=False)
    neutral = evaluate_fitness(route, weights=FitnessWeights(), tag_adjustments={})
    family_adj = get_default_tag_adjustments("family")
    family = evaluate_fitness(
        route, weights=FitnessWeights(), tag_adjustments=family_adj
    )
    assert family.fitness < neutral.fitness


def test_tag_adjustments_change_fitness_for_tagged_poi():
    p1 = POI(
        "Bird Sanctuary X",
        15.4,
        73.9,
        0.88,
        place_id="san-1",
        rating=4.0,
        poi_type="zoo",
    )
    p2 = POI(
        "Other",
        15.41,
        73.91,
        0.8,
        place_id="o-1",
        rating=4.0,
        poi_type="tourist_attraction",
    )
    route = [p1, p2]
    prepare_day_matrices(route, use_osrm=False)
    base = evaluate_fitness(route, weights=FitnessWeights())
    boosted = evaluate_fitness(
        route,
        weights=FitnessWeights(),
        tag_adjustments={"sanctuary": 1.0},
    )
    assert boosted.tag_preference_reward > base.tag_preference_reward
    assert boosted.fitness != base.fitness
