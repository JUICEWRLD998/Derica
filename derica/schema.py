"""The one shape every parser must produce, whether rules or a model.

Anything that does not fit is rejected, never repaired by guessing.
"""

import json
from dataclasses import dataclass

from derica.units import normalize_item

UNITS = ("kg", "derica", "mudu", "paint", "bag")
SIDES = ("buy", "sell")


@dataclass(frozen=True)
class PriceEvent:
    item: str
    qty: float
    unit: str
    price_ngn: int
    side: str

    def __post_init__(self) -> None:
        if not isinstance(self.item, str) or not self.item.strip():
            raise ValueError("item must be a non-empty string")
        object.__setattr__(self, "item", normalize_item(self.item))
        if isinstance(self.qty, bool) or not isinstance(self.qty, (int, float)) or self.qty <= 0:
            raise ValueError("qty must be a positive number")
        if self.unit not in UNITS:
            raise ValueError(f"unit must be one of {UNITS}")
        if isinstance(self.price_ngn, bool) or not isinstance(self.price_ngn, int) or self.price_ngn <= 0:
            raise ValueError("price_ngn must be a positive whole number")
        if self.side not in SIDES:
            raise ValueError(f"side must be one of {SIDES}")

    @classmethod
    def from_json(cls, text: str) -> "PriceEvent":
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("expected a JSON object")
        try:
            return cls(**data)
        except TypeError as error:
            raise ValueError(f"wrong fields: {error}") from error
