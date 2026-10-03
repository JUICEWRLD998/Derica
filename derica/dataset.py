"""Prompt and completion format shared by training, the eval and the service.

The model answers with one JSON object or the word null. Anything else is
rejected by parse_completion, never repaired.
"""

import json

from derica.schema import PriceEvent

_INSTRUCTION = (
    "Read this WhatsApp message from a grain seller in a Nigerian market. "
    "Reply with one JSON object with keys item, qty, unit, price_ngn "
    "(unit is one of kg, derica, mudu, paint, bag), or null if the message states no price."
)


def build_prompt(text: str, context_item: str | None) -> str:
    return f"{_INSTRUCTION}\nTopic: {context_item or 'none'}\nMessage: {text}\nJSON:"


def build_completion(row: dict) -> str:
    if row["gold"] is None:
        return "null"
    return json.dumps(row["gold"], separators=(",", ":"))


def parse_completion(text: str) -> PriceEvent | None:
    stripped = text.strip()
    if stripped == "null":
        return None
    try:
        return PriceEvent.from_json(stripped)
    except json.JSONDecodeError as error:
        raise ValueError(f"not JSON: {stripped!r}") from error


def make_examples(rows: list[dict]) -> list[dict]:
    return [
        {"prompt": build_prompt(r["text"], r.get("context_item")), "completion": build_completion(r)}
        for r in rows
    ]
