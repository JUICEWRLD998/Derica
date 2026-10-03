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


_CONVENTIONS = (
    "Rules the seller uses: a bare bag-sized price with no unit, such as 92k, is a 50 kg bag, so unit is kg and qty is 50. "
    "A price per derica, mudu or paint has qty is 1. A price per bag is unit bag and qty is 1. "
    "When the message names no item, use the Topic. Use lowercase item names. "
    "A message with no price, only a quantity or talk about prices, is null."
)
_SHOTS = (
    ("Rice 50kg 80k today", None, '{"item":"rice","qty":50,"unit":"kg","price_ngn":80000}'),
    ("Garri 2,200 mudu", None, '{"item":"garri","qty":1,"unit":"mudu","price_ngn":2200}'),
    ("Do you still have beans?", None, "null"),
    ("Beans 3,500 derica", None, '{"item":"beans","qty":1,"unit":"derica","price_ngn":3500}'),
    ("Supplier say groundnut 105k final", None, '{"item":"groundnut","qty":50,"unit":"kg","price_ngn":105000}'),
    ("Na 3,400 mudu I fit do", "beans", '{"item":"beans","qty":1,"unit":"mudu","price_ngn":3400}'),
    ("Beans price don change", None, "null"),
    ("Rice 72k per bag", None, '{"item":"rice","qty":1,"unit":"bag","price_ngn":72000}'),
    ("If you take 8 bags I go reduce", None, "null"),
    ("Groundnut 4k paint", None, '{"item":"groundnut","qty":1,"unit":"paint","price_ngn":4000}'),
)


def build_few_shot_prompt(text: str, context_item: str | None) -> str:
    """The prompt given to systems that were not fine-tuned: same task, plus the rules and worked examples."""
    shots = "\n\n".join(
        f"Topic: {topic or 'none'}\nMessage: {message}\nJSON: {answer}" for message, topic, answer in _SHOTS
    )
    return f"{_INSTRUCTION}\n{_CONVENTIONS}\n\n{shots}\n\nTopic: {context_item or 'none'}\nMessage: {text}\nJSON:"
