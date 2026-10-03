"""Parse a naira amount the way people type it: ₦2,500, N2500, 82k, 82 thousand."""

import re
from decimal import Decimal

_AMOUNT = re.compile(
    r"^(?:₦|NGN|N)?\s*(\d[\d,]*(?:\.\d+)?)\s*(k|thousand)?$",
    re.IGNORECASE,
)


def parse_naira(text: str) -> int:
    """Return a positive whole-naira price, or raise ValueError.

    Never guesses: anything that is not a clear positive amount is rejected.
    """
    match = _AMOUNT.match(text.strip())
    if not match:
        raise ValueError(f"not a naira amount: {text!r}")
    amount = Decimal(match.group(1).replace(",", ""))
    if match.group(2):
        amount *= 1000
    if amount != amount.to_integral_value() or amount <= 0:
        raise ValueError(f"not a positive whole-naira amount: {text!r}")
    return int(amount)
