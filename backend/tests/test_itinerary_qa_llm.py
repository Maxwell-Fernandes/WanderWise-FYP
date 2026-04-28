"""Groq itinerary QA (mocked)."""

import sys
from unittest.mock import patch

sys.path.append("/home/maxwell/Desktop/WanderWise/backend")

from app.services.itinerary_qa_llm import evaluate_itinerary_qa


@patch("app.services.itinerary_qa_llm.GROQ_API_KEY", "")
def test_itinerary_qa_skipped_without_key():
    r = evaluate_itinerary_qa(
        [{"name": "Calangute", "visit_start": "13:00", "visit_end": "14:00"}],
        day_num=1,
    )
    assert r["source"] == "skipped"
    assert r["ok"] is True
    assert r["problematic_places"] == []


@patch("app.services.itinerary_qa_llm.groq_chat_json")
@patch("app.services.itinerary_qa_llm.GROQ_API_KEY", "x")
def test_itinerary_qa_parses_groq_json(mock_chat):
    mock_chat.return_value = (
        '{"ok": false, "issues": ["beach at noon"], "summary": "Bad timing", '
        '"problematic_places": [{"name": "Baga Beach", "reason": "midday sun"}]}'
    )
    r = evaluate_itinerary_qa(
        [{"name": "Baga Beach", "visit_start": "13:00", "visit_end": "14:30"}],
        day_num=2,
    )
    assert r["source"] == "groq"
    assert r["ok"] is False
    assert "beach at noon" in r["issues"][0]
    assert len(r["problematic_places"]) == 1


@patch("app.services.itinerary_qa_llm.groq_chat_json", side_effect=ValueError("bad"))
@patch("app.services.itinerary_qa_llm.GROQ_API_KEY", "x")
def test_itinerary_qa_error_source(mock_chat):
    r = evaluate_itinerary_qa([], day_num=1)
    assert r["source"] == "error"
    assert r["ok"] is True
