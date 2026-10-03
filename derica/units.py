"""A seller's own measures: how many grams one derica, mudu or paint of each item weighs.

Weights differ per item, so there is no global derica. An item with no
calibration is rejected, never guessed.
"""

import json
from pathlib import Path

Units = dict[str, dict[str, int]]

# Only these units need no calibration, because a kilogram is a kilogram.
_ABSOLUTE_GRAMS = {"kg": 1000}

_ALIASES = {"groundnuts": "groundnut", "ground nut": "groundnut", "ground nuts": "groundnut"}


class UnknownMeasure(ValueError):
    """The item or unit has no calibrated weight."""


def normalize_item(name: str) -> str:
    cleaned = " ".join(name.lower().split())
    return _ALIASES.get(cleaned, cleaned)


def load_units(path: str | Path) -> Units:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    table: Units = {}
    for item, measures in raw.items():
        for unit, weight in measures.items():
            if not isinstance(weight, int) or weight <= 0:
                raise ValueError(f"{item}/{unit}: weight must be a positive whole number of grams")
        table[normalize_item(item)] = dict(measures)
    return table


def grams(item: str, unit: str, table: Units) -> int:
    unit = unit.lower().strip()
    if unit in _ABSOLUTE_GRAMS:
        return _ABSOLUTE_GRAMS[unit]
    key = normalize_item(item)
    if key not in table:
        raise UnknownMeasure(f"no calibration for item {item!r}")
    if unit not in table[key]:
        raise UnknownMeasure(f"no {unit!r} weight for item {item!r}")
    return table[key][unit]
