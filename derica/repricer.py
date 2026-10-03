"""Deterministic pricing. No model is involved in any number computed here.

Exact fractions are used throughout, so the only rounding is the one the
seller sees: up to her naira step.
"""

import math
from fractions import Fraction

from derica.schema import PriceEvent
from derica.units import Units, grams, normalize_item


def cost_per_measure(cost_event: PriceEvent, measure_unit: str, table: Units) -> Fraction:
    """What one derica, mudu or paint costs, given a kg or bag cost price."""
    if not cost_event.is_cost:
        raise ValueError("need a cost price in kg or bag, got a per-measure price")
    total_grams = Fraction(cost_event.qty).limit_denominator() * grams(cost_event.item, cost_event.unit, table)
    return Fraction(cost_event.price_ngn) / total_grams * grams(cost_event.item, measure_unit, table)


def markup(selling_price: int, cost: Fraction) -> Fraction:
    """Selling price over cost, minus one. 0.16 means a 16% markup."""
    if cost <= 0:
        raise ValueError("cost must be positive")
    return Fraction(selling_price) / cost - 1


def new_sell_price(
    old_sell: PriceEvent,
    old_cost: PriceEvent,
    new_cost: PriceEvent,
    table: Units,
    step: int = 50,
) -> int:
    """The selling price for one measure that keeps her current markup at the new cost.

    Rounded up to `step` naira, so rounding never costs her margin.
    """
    if step <= 0:
        raise ValueError("step must be positive")
    if old_sell.is_cost:
        raise ValueError("old_sell must be a per-measure selling price")
    if not (normalize_item(old_sell.item) == normalize_item(old_cost.item) == normalize_item(new_cost.item)):
        raise ValueError("all three prices must be for the same item")
    per_measure = Fraction(old_sell.price_ngn) / Fraction(old_sell.qty).limit_denominator()
    kept = markup(per_measure, cost_per_measure(old_cost, old_sell.unit, table))
    exact = cost_per_measure(new_cost, old_sell.unit, table) * (1 + kept)
    return math.ceil(exact / step) * step


def lost_per_sale(old_price: int, new_price: int) -> int:
    """Naira lost on every measure sold if she stays at the old price. Negative means the old price was too high."""
    return new_price - old_price
