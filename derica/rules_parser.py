"""Rules-based parser for the format the friend actually types: "Rice — ₦2,500 mudu".

This is the floor every model has to beat. A line that does not match is
rejected, never guessed.
"""

import re

from derica.money import parse_naira
from derica.schema import PriceEvent

_LINE = re.compile(
    r"^\s*(?:\d+\s*[.)]\s*)?"
    r"(?P<item>[A-Za-z][A-Za-z ]*?)\s*[—–-]\s*"
    r"(?P<price>(?:₦|NGN|N)?\s*\d[\d,]*(?:\.\d+)?\s*(?:k|thousand)?)\s*"
    r"(?P<unit>mudu|derica|paint|kg|bag)\s*$",
    re.IGNORECASE,
)


def parse_line(line: str, side: str = "sell") -> PriceEvent:
    match = _LINE.match(line)
    if not match:
        raise ValueError(f"not a price message: {line!r}")
    return PriceEvent(
        item=match.group("item"),
        qty=1,
        unit=match.group("unit").lower(),
        price_ngn=parse_naira(match.group("price")),
        side=side,
    )
