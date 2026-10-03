from fractions import Fraction
from pathlib import Path

import pytest

from derica.repricer import cost_per_measure, markup
from derica.schema import PriceEvent
from derica.units import load_units

EXAMPLE = Path(__file__).resolve().parents[1] / "data" / "units.example.json"


@pytest.fixture(scope="module")
def table():
    return load_units(EXAMPLE)


def cost(item, qty, unit, price):
    return PriceEvent(item=item, qty=qty, unit=unit, price_ngn=price)


def test_rice_mudu_costs_2496_when_a_50kg_bag_costs_78000(table):
    # 78,000 / 50,000 g * 1,600 g
    assert cost_per_measure(cost("rice", 50, "kg", 78000), "mudu", table) == 2496


def test_a_bag_price_and_a_50kg_price_give_the_same_cost(table):
    by_bag = cost_per_measure(cost("garri", 1, "bag", 55000), "mudu", table)
    by_kg = cost_per_measure(cost("garri", 50, "kg", 55000), "mudu", table)
    assert by_bag == by_kg == 1210


def test_cost_is_exact_not_a_rounded_float(table):
    assert cost_per_measure(cost("groundnut", 50, "kg", 105000), "derica", table) == Fraction(105000 * 650, 50000)


def test_only_a_cost_event_can_be_priced_per_measure(table):
    with pytest.raises(ValueError):
        cost_per_measure(cost("rice", 1, "mudu", 2900), "mudu", table)


def test_markup_is_selling_price_over_cost_minus_one():
    assert markup(2900, Fraction(2496)) == Fraction(2900, 2496) - 1


def test_markup_rejects_a_non_positive_cost():
    with pytest.raises(ValueError):
        markup(2900, Fraction(0))
