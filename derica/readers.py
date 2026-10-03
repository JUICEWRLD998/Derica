"""Read one pasted message: the Derica model first, the rules parser as the labelled fallback.

The model only proposes. Its answer is parsed strictly, then checked for plausibility, and
only then shown. A model that is down, slow or wrong never blocks the page: the rules
answer, and the page says which reader answered.
"""

import time
from dataclasses import dataclass, field
from typing import Callable

from derica.dataset import parse_completion
from derica.rules_baseline import parse_message
from derica.schema import PriceEvent

MAX_TEXT = 280
ITEMS = ("rice", "beans", "garri", "groundnut")
# Naira bands a real grain price falls in. Outside them the reading is refused, not shown.
_BANDS = {"kg_per_kg": (300, 4_000), "bag": (10_000, 400_000), "measure": (100, 30_000)}

Model = Callable[[str, str | None], str]


@dataclass
class ReadResult:
    chosen: PriceEvent | None
    reader: str
    note: str = ""
    readers: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "event": self.chosen and self.chosen.__dict__,
            "reader": self.reader,
            "note": self.note,
            "readers": self.readers,
        }


def refusal(event: PriceEvent) -> str:
    """Why an event is not shown, or an empty string when it is plausible."""
    if event.item not in ITEMS:
        return f"{event.item} is not one of the four items in this stall"
    if event.unit == "kg":
        low, high = _BANDS["kg_per_kg"]
        ok = low <= event.price_ngn / event.qty <= high
    elif event.unit == "bag":
        low, high = _BANDS["bag"]
        ok = low <= event.price_ngn <= high
    else:
        low, high = _BANDS["measure"]
        ok = low <= event.price_ngn <= high
    return "" if ok else f"price out of range for {event.unit} (₦{low:,} to ₦{high:,})"


def plausible(event: PriceEvent) -> bool:
    return refusal(event) == ""


def _entry(name: str, event: PriceEvent | None, status: str, started: float) -> dict:
    return {"name": name, "event": event and event.__dict__, "status": status, "ms": round((time.time() - started) * 1000)}


def read_message(text: str, context_item: str | None, model: Model | None) -> ReadResult:
    text = " ".join(text.split())
    if not text:
        raise ValueError("message is empty")
    if len(text) > MAX_TEXT:
        raise ValueError(f"message is longer than {MAX_TEXT} characters")

    started = time.time()
    rules_event = parse_message(text, context_item)
    rules_entry = _entry("Rules", rules_event, "ok", started)

    started = time.time()
    model_event, model_entry, note = None, None, ""
    try:
        if model is None:
            raise RuntimeError("no model configured")
        model_event = parse_completion(model(text, context_item))
        model_entry = _entry("Derica model", model_event, "ok", started)
    except Exception as error:  # the model is never allowed to take the page down
        status = "invalid" if isinstance(error, ValueError) else "unavailable"
        model_entry = _entry("Derica model", None, status, started)
        note = "The model gave no usable answer, so the rules read this message."

    readers = [model_entry, rules_entry]
    if model_entry["status"] == "ok":
        reader, chosen = "derica", model_event
    else:
        reader, chosen = "rules", rules_event

    if chosen is not None:
        why = refusal(chosen)
        if why:
            return ReadResult(None, reader, f"Not shown: {why}.", readers)
    return ReadResult(chosen, reader, note, readers)
