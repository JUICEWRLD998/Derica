from fractions import Fraction
from pathlib import Path

import pytest

from derica.repricer import cost_per_measure, lost_per_sale, markup, new_sell_price
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


OLD_COST = ("rice", 50, "kg", 78000)
OLD_SELL = ("rice", 1, "mudu", 2900)


def reprice(new_bag_price, table, step=50, old_sell=OLD_SELL):
    return new_sell_price(cost(*old_sell), cost(*OLD_COST), cost("rice", 50, "kg", new_bag_price), table, step=step)


def test_a_dearer_bag_raises_the_mudu_price_and_keeps_her_markup(table):
    # exact 2624 * 2900 / 2496 = 3048.72, rounded up to the next 50
    assert reprice(82000, table) == 3050


def test_a_cheaper_bag_lowers_the_price(table):
    # exact 2240 * 2900 / 2496 = 2602.56, rounded up to the next 50
    assert reprice(70000, table) == 2650


def test_an_unchanged_bag_price_leaves_her_price_alone(table):
    assert reprice(78000, table) == 2900


def test_the_price_is_always_a_multiple_of_the_step_and_never_below_the_exact_value(table):
    for bag in range(60000, 120000, 1700):
        exact = cost_per_measure(cost("rice", 50, "kg", bag), "mudu", table) * Fraction(2900, 2496)
        result = reprice(bag, table)
        assert result % 50 == 0
        assert result >= exact


def test_a_dearer_bag_never_lowers_the_price(table):
    prices = [reprice(bag, table) for bag in range(60000, 120000, 1700)]
    assert prices == sorted(prices)


def test_the_step_is_honoured(table):
    assert reprice(82000, table, step=100) == 3100


def test_a_selling_price_for_several_measures_is_priced_per_measure(table):
    # 2 mudu sold for 5,800 is the same 2,900 each
    assert reprice(82000, table, old_sell=("rice", 2, "mudu", 5800)) == 3050


def test_items_must_match(table):
    with pytest.raises(ValueError):
        new_sell_price(cost("beans", 1, "mudu", 3400), cost(*OLD_COST), cost("rice", 50, "kg", 82000), table)


def test_a_cost_price_cannot_stand_in_for_a_selling_price(table):
    with pytest.raises(ValueError):
        new_sell_price(cost("rice", 50, "kg", 78000), cost(*OLD_COST), cost("rice", 50, "kg", 82000), table)


def test_a_selling_price_cannot_stand_in_for_a_cost_price(table):
    with pytest.raises(ValueError):
        new_sell_price(cost(*OLD_SELL), cost(*OLD_SELL), cost("rice", 50, "kg", 82000), table)


def test_step_must_be_positive(table):
    with pytest.raises(ValueError):
        reprice(82000, table, step=0)


def test_lost_per_sale_is_what_staying_at_the_old_price_costs():
    assert lost_per_sale(old_price=2900, new_price=3050) == 150
    assert lost_per_sale(old_price=2900, new_price=2650) == -250
