"""Her stall book applied to a new cost: the new price per measure, row by row.

Pure arithmetic over derica.repricer. The model is not involved.
"""

from fractions import Fraction

from derica.repricer import cost_per_measure, lost_per_sale, markup, new_sell_price
from derica.schema import PriceEvent
from derica.units import normalize_item

MEASURES = ("derica", "mudu", "paint")
BAG_GRAMS = 50_000  # Amina: a bag is a 50 kg bag.


def reprice(item: str, old_cost: PriceEvent, new_cost: PriceEvent, measures: dict, step: int = 50) -> dict:
    if not measures:
        raise ValueError("give at least one measure with its weight and current price")
    if not 10 <= step <= 500:
        raise ValueError("step must be between 10 and 500 naira")
    item = normalize_item(item)
    table = {item: {"bag": BAG_GRAMS}}
    sells = {}
    for unit, spec in measures.items():
        if unit not in MEASURES:
            raise ValueError(f"unknown measure {unit!r}; use derica, mudu or paint")
        grams, old_price = spec.get("grams"), spec.get("old_price")
        if not isinstance(grams, int) or isinstance(grams, bool) or grams <= 0:
            raise ValueError(f"{unit}: weight must be a positive whole number of grams")
        if not isinstance(old_price, int) or isinstance(old_price, bool) or old_price <= 0:
            raise ValueError(f"{unit}: current price must be a positive whole number of naira")
        table[item][unit] = grams
        sells[unit] = PriceEvent(item, 1, unit, old_price)

    rows = []
    for unit, old_sell in sells.items():
        new_price = new_sell_price(old_sell, old_cost, new_cost, table, step)
        kept = markup(old_sell.price_ngn, cost_per_measure(old_cost, unit, table))
        rows.append({
            "unit": unit,
            "grams": table[item][unit],
            "old_price": old_sell.price_ngn,
            "new_price": new_price,
            "lost_per_sale": lost_per_sale(old_sell.price_ngn, new_price),
            "markup_pct": round(float(kept) * 100, 1),
        })
    return {"item": item, "rows": rows}
