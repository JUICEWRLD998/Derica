"""Retail-over-wholesale markup from the WFP Nigeria food price file.

National context only. WFP markets are not Amina's market and the pairs are
retail and wholesale of the same market and month.
"""

import re
from statistics import median


def per_kg(row: dict) -> float:
    size = re.match(r"^\s*([\d.]+)?\s*KG\s*$", row["unit"], re.IGNORECASE)
    if not size:
        raise ValueError(f"unit is not a kilogram size: {row['unit']!r}")
    return float(row["price"]) / float(size.group(1) or 1)


def markup_by_year(rows: list[dict]) -> dict[tuple[str, int], float]:
    """Median of retail/wholesale - 1 over market-months, per commodity and year."""
    sides: dict[tuple[str, str, str], dict[str, float]] = {}
    for row in rows:
        if row["currency"] != "NGN" or row["pricetype"] not in ("Retail", "Wholesale"):
            continue
        try:
            value = per_kg(row)
        except ValueError:
            continue
        key = (row["commodity"], row["market"], row["date"][:7])
        sides.setdefault(key, {})[row["pricetype"]] = value
    ratios: dict[tuple[str, int], list[float]] = {}
    for (commodity, _market, month), pair in sides.items():
        if len(pair) == 2 and pair["Wholesale"] > 0:
            ratios.setdefault((commodity, int(month[:4])), []).append(pair["Retail"] / pair["Wholesale"] - 1)
    return {key: median(values) for key, values in ratios.items()}
