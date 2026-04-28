"""Module 1 interest filtering and Groq classification."""

import sys
from unittest.mock import patch

import pandas as pd

sys.path.append("/home/maxwell/Desktop/WanderWise/backend")

from app.services.module1_interests_llm import (
    Module1LlmResult,
    interests_lists_to_dict,
    resolve_module1_interests_llm,
)
from app.services.module1_service import (
    filter_places_by_interests,
    rerank_places_by_extraction,
    run_module1_simulation,
)


def test_filter_places_negatives_only_excludes_categories():
    df = pd.DataFrame(
        {
            "name": ["A", "B", "C"],
            "latitude": [15.0, 15.1, 15.2],
            "longitude": [73.0, 73.1, 73.2],
            "rating": [4.0, 4.0, 4.0],
            "categories": [
                ["nightlife"],
                ["historical"],
                ["beaches", "nature"],
            ],
        }
    )
    out = filter_places_by_interests(
        df, [], ["nightlife"], min_rating=3.0
    )
    assert len(out) == 2
    assert "nightlife" not in out["categories"].iloc[0]


def test_interests_lists_to_dict():
    d = interests_lists_to_dict(["beaches"], ["nightlife"])
    assert d["beaches"] is True
    assert d["nightlife"] is False


@patch("app.services.module1_interests_llm.groq_chat_json")
def test_resolve_module1_interests_llm_parses_json(mock_groq):
    mock_groq.return_value = (
        '{"positive_interests": ["historical", "religious"], '
        '"negative_interests": ["nightlife", "bogus"], '
        '"themes_keywords": ["basilica"], '
        '"mentioned_places": ["old goa"], '
        '"constraints": {"pace": "relaxed", "avoid_strenuous": true}, '
        '"preference_summary": "Churches and heritage, easy pace."}'
    )
    result = resolve_module1_interests_llm("forts and churches, no clubs")
    assert result.positive_interests == ["historical", "religious"]
    assert result.negative_interests == ["nightlife"]
    assert "basilica" in result.preference_extraction.get("themes_keywords", [])
    assert result.preference_extraction.get("constraints", {}).get("pace") == "relaxed"
    assert "preference_summary" in result.preference_extraction


def test_rerank_places_by_extraction_prioritizes_keyword_match():
    df = pd.DataFrame(
        {
            "name": ["Quiet Museum", "Big Fort Aguada"],
            "types": ["museum", "fort"],
            "address": ["", ""],
            "latitude": [15.0, 15.1],
            "longitude": [73.0, 73.1],
            "rating": [4.6, 4.0],
            "user_ratings_total": [200, 200],
            "categories": [["historical"], ["historical"]],
        }
    )
    out = rerank_places_by_extraction(
        df, {"themes_keywords": ["fort"], "mentioned_places": []}
    )
    assert "Fort" in out.iloc[0]["name"]


@patch("app.services.module1_interests_llm.resolve_module1_interests_llm")
def test_run_module1_simulation_uses_groq_when_enabled(mock_resolve):
    mock_resolve.return_value = Module1LlmResult(
        positive_interests=["historical"],
        negative_interests=["shopping"],
        preference_extraction={"themes_keywords": ["museum"]},
    )
    with patch("app.services.module1_service.GROQ_API_KEY", "x" * 20):
        r = run_module1_simulation(
            "museums only",
            min_rating=3.0,
            use_llm_interests=True,
        )
    assert r["interests_source"] == "groq"
    assert r["positive_interests"] == ["historical"]
    assert r["negative_interests"] == ["shopping"]
    assert r["preference_extraction"]["themes_keywords"] == ["museum"]
