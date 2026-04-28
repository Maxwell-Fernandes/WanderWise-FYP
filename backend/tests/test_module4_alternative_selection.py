import sys

sys.path.append("/home/maxwell/Desktop/WanderWise/backend")

from app.services.module4_service import (
    Individual,
    POI,
    select_exclusive_must_visit_alternatives,
    select_secondary_itinerary_alternatives,
)


def _make_poi(name: str, wpi: float) -> POI:
    return POI(name=name, lat=15.0, lon=73.0, normalized_popularity=wpi, place_id=name)


def _make_individual(route: list[POI]) -> Individual:
    return Individual(route, route)


def test_select_exclusive_must_visit_alternatives_unique():
    poi_a = _make_poi("A", 0.9)
    poi_b = _make_poi("B", 0.92)
    poi_c = _make_poi("C", 0.95)
    filler = _make_poi("X", 0.4)

    candidates = [
        _make_individual([poi_a, filler]),
        _make_individual([poi_b, filler]),
        _make_individual([poi_c, filler]),
    ]

    selected = select_exclusive_must_visit_alternatives(candidates, desired_count=3)
    assert len(selected) == 3
    exclusive_ids = [pair[1] for pair in selected]
    assert exclusive_ids == ["A", "B", "C"]


def test_select_exclusive_must_visit_skips_used_exclusive():
    poi_a = _make_poi("A", 0.9)
    poi_b = _make_poi("B", 0.91)

    cand1 = _make_individual([poi_a])
    cand2 = _make_individual([poi_a, poi_b])
    cand3 = _make_individual([poi_b])

    selected = select_exclusive_must_visit_alternatives(
        [cand1, cand2, cand3], desired_count=2
    )

    assert [pair[0] for pair in selected] == [cand1, cand3]
    assert [pair[1] for pair in selected] == ["A", "B"]


def test_select_exclusive_must_visit_fallback_without_must_visit():
    poi_a = _make_poi("A", 0.9)
    filler = _make_poi("X", 0.2)

    cand1 = _make_individual([poi_a])
    cand2 = _make_individual([filler])

    selected = select_exclusive_must_visit_alternatives([cand1, cand2], desired_count=2)

    assert len(selected) == 2
    assert selected[0][1] == "A"
    assert selected[1][1] is None


def test_select_secondary_prefers_disjoint_and_remaining_must_visits():
    poi_a = _make_poi("A", 0.9)
    poi_c = _make_poi("C", 0.91)

    cand_overlap = _make_individual([poi_a])
    cand_disjoint = _make_individual([poi_c])

    selected = select_secondary_itinerary_alternatives(
        [cand_overlap, cand_disjoint],
        desired_count=1,
        preferred_must_visit_ids={"C"},
        disjoint_ids={"A"},
    )

    assert selected[0][0] is cand_disjoint
    assert selected[0][1] == "C"


def test_select_secondary_falls_back_when_no_disjoint():
    poi_a = _make_poi("A", 0.9)
    cand_overlap = _make_individual([poi_a])

    selected = select_secondary_itinerary_alternatives(
        [cand_overlap],
        desired_count=1,
        preferred_must_visit_ids={"A"},
        disjoint_ids={"A"},
    )

    assert selected[0][0] is cand_overlap
