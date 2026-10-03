import json
from pathlib import Path

import pytest

from derica.units import UnknownMeasure, grams, load_units

EXAMPLE = Path(__file__).resolve().parents[1] / "data" / "units.example.json"


@pytest.fixture(scope="module")
def table():
    return load_units(EXAMPLE)


def test_rice_measures_match_what_the_friend_weighed(table):
    assert grams("rice", "derica", table) == 800
    assert grams("rice", "mudu", table) == 1600
    assert grams("rice", "paint", table) == 7000


def test_every_item_has_a_mudu_that_is_two_dericas(table):
    for item in ("rice", "beans", "garri", "groundnut"):
        assert grams(item, "mudu", table) == 2 * grams(item, "derica", table)


def test_bag_is_fifty_kg_for_all_four_items(table):
    for item in ("rice", "beans", "garri", "groundnut"):
        assert grams(item, "bag", table) == 50_000


def test_kg_works_for_any_item_without_calibration(table):
    assert grams("rice", "kg", table) == 1000
    assert grams("yam flour", "kg", table) == 1000


def test_item_names_are_normalised(table):
    assert grams("  RICE ", "derica", table) == 800
    assert grams("Groundnuts", "mudu", table) == grams("groundnut", "mudu", table)


def test_uncalibrated_item_is_rejected_not_guessed(table):
    with pytest.raises(UnknownMeasure):
        grams("yam flour", "mudu", table)


def test_unknown_unit_is_rejected(table):
    with pytest.raises(UnknownMeasure):
        grams("rice", "bucket", table)


def test_load_units_rejects_non_positive_weights(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"rice": {"derica": 0}}), encoding="utf-8")
    with pytest.raises(ValueError):
        load_units(bad)
