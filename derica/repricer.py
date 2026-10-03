"""Deterministic pricing. No model is involved in any number computed here.

Exact fractions are used throughout, so the only rounding is the one the
seller sees: up to her naira step.
"""

from fractions import Fraction

from derica.schema import PriceEvent
from derica.units import Units, grams


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
