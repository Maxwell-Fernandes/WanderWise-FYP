"""Beach scorch window (12:00–16:00) overlap penalties in Module 4 fitness."""

import sys

sys.path.append("/home/maxwell/Desktop/WanderWise/backend")

from app.services.module4_service import POI, evaluate_fitness, prepare_day_matrices


def _beach_poi(name: str = "Test Beach", vid: str = "beach-1") -> POI:
    return POI(
        name,
        15.5,
        73.8,
        0.9,
        place_id=vid,
        rating=4.0,
        poi_type="beach",
    )


def test_beach_no_scorch_overlap_morning():
    p = _beach_poi(vid="b-morn")
    prepare_day_matrices([p], use_osrm=False)
    ev = evaluate_fitness([p], start_time="09:00")
    assert ev.beach_scorch_overlap_min == 0.0
    assert ev.wrong_time_penalty == 0.0


def test_beach_no_scorch_overlap_ends_at_noon_half_open():
    p = _beach_poi(vid="b-noon")
    p.visit_duration_min = 180  # 09:00 + 180min = 12:00 end → no overlap with [12:00,16:00)
    prepare_day_matrices([p], use_osrm=False)
    ev = evaluate_fitness([p], start_time="09:00")
    assert ev.beach_scorch_overlap_min == 0.0


def test_beach_scorch_overlap_midday():
    p = _beach_poi(vid="b-mid")
    prepare_day_matrices([p], use_osrm=False)
    ev = evaluate_fitness([p], start_time="12:30")
    # 12:30–13:30 default 60min → 60 min in scorch window
    assert ev.beach_scorch_overlap_min >= 60.0
    assert ev.wrong_time_penalty > 0.0


def test_non_beach_midday_no_beach_scorch_metric():
    p = POI(
        "Some Fort",
        15.5,
        73.8,
        0.9,
        place_id="fort-1",
        rating=4.0,
        poi_type="tourist_attraction",
    )
    prepare_day_matrices([p], use_osrm=False)
    ev = evaluate_fitness([p], start_time="13:00")
    assert ev.beach_scorch_overlap_min == 0.0
