"""Rules baseline for messy WhatsApp price messages.

Written after reading Amina's 18 real messages, so it is an optimistic baseline:
the rules were shaped by the test data. A message it cannot read returns None,
it is never guessed.
"""

import re

from derica.money import parse_naira
from derica.schema import PriceEvent

_NUMBER = re.compile(
    r"(?<![\w.])(?P<number>\d[\d,]*(?:\.\d+)?)\s*(?P<k>k\b)?\s*(?P<unit>kg|bags?|mudu|derica|paint)?",
    re.IGNORECASE,
)
_ITEMS = ("rice", "beans", "garri", "groundnut")
_BAG_WORD = re.compile(r"\bbags?\b", re.IGNORECASE)
# Below this a number is a count ("5 bags", "10 mudu"), at or above it a naira price.
_SMALLEST_PRICE = 500
# Amina: a bare bag-sized price means a 50 kg bag.
_BARE_BAG_FLOOR = 10_000


def _quantity(number: str) -> float:
    value = float(number.replace(",", ""))
    return int(value) if value.is_integer() else value


def parse_message(text: str, context_item: str | None = None) -> PriceEvent | None:
    item = next((word for word in _ITEMS if word in text.lower()), context_item)
    if item is None:
        return None

    prices, counts = [], []
    for match in _NUMBER.finditer(text):
        number, k, unit = match.group("number", "k", "unit")
        try:
            naira = parse_naira(number + (k or ""))
        except ValueError:
            return None
        if k or naira >= _SMALLEST_PRICE:
            prices.append((naira, unit))
        else:
            counts.append((_quantity(number), unit))
    if len(prices) != 1:
        return None
    price, price_unit = prices[0]

    kilos = next((qty for qty, unit in counts if unit and unit.lower() == "kg"), None)
    if kilos is None and price_unit and price_unit.lower() == "kg":
        kilos = 50
    if kilos is not None:
        return PriceEvent(item, kilos, "kg", price)
    if price_unit and price_unit.lower() in ("mudu", "derica", "paint"):
        return PriceEvent(item, 1, price_unit.lower(), price)
    if _BAG_WORD.search(text):
        return PriceEvent(item, 1, "bag", price)
    if price >= _BARE_BAG_FLOOR:
        return PriceEvent(item, 50, "kg", price)
    return None
