"""Synthetic WhatsApp-style price messages for training.

Every row is marked source="synthetic_generated". These never go into the test
set: generate() takes the frozen test texts as `exclude` and will not reproduce
them. The message styles come from what Amina's chats look like, with extra hard
shapes (a price in a sentence, an old and a new price, the item left out).
"""

import random

ITEMS = ("rice", "beans", "garri", "groundnut")
# (low, high) naira ranges. Bag prices round to 500, measure prices to 50.
_KG50 = {"rice": (70_000, 85_000), "beans": (85_000, 100_000), "garri": (50_000, 60_000), "groundnut": (98_000, 112_000)}
_MUDU = {"rice": (2_800, 3_200), "beans": (3_200, 3_700), "garri": (1_800, 2_200), "groundnut": (3_600, 4_100)}
_MEASURE_FACTOR = {"mudu": 1.0, "derica": 0.5, "paint": 4.4}

_KG_TEMPLATES = (
    "{I} {Q}kg {P}", "{I} {Q}kg now {P}", "{I} na {P} for {Q}kg", "{P} for {Q}kg {i}",
    "{I} {Q} kg don reach {P}", "Abeg {I} {Q}kg na {P} today",
    "{I} was {O} last week, {Q}kg now {P}", "Just checked, {I} {Q}kg dey {P}",
)
_BARE_TEMPLATES = (
    "{I} {P} now", "{I} no dey cheap again, {P} now", "Supplier say {I} {P} final", "{I} don reach {P} o",
)
_BAG_TEMPLATES = ("{I} {P} per bag", "{I} na {P} per bag today", "{I} {P} per bag, no delivery")
_MEASURE_TEMPLATES = (
    "{I} na {P} {U}", "{I} {P} {U} today", "{I} {U} na {P}", "{I} was {O} {U}, now {P}",
)
_CONTEXT_TEMPLATES = ("I fit give you {P} {U}", "{P} {U}", "Na {P} {U} I fit do", "{P} {U} final")
_NOT_PRICE = (
    "If you take {n} bags I fit reduce am", "How many {U} you want?", "{I} price don change",
    "Supplier say {i} go increase", "I get {n} bags of {i} left", "Come before {t}pm abeg",
    "Abeg check {i} price for me", "Bring money make I reserve {n} bags", "Na {n} {U} you want?",
    "{I} don finish", "You want {n} bags of {i}?", "If na {n} {U} I go give you better price",
    "{I} supplier dey come tomorrow", "Make I know before {t}pm",
)


def _round_to(value: float, step: int = 50) -> int:
    return int(round(value / step) * step)


def _price_text(rng: random.Random, naira: int) -> str:
    forms = [f"{naira:,}", str(naira)]
    if naira % 1000 == 0:
        forms += [f"{naira // 1000}k"] * 3
    elif naira % 500 == 0 and naira >= 10_000:
        forms.append(f"{naira / 1000:g}k")
    text = rng.choice(forms)
    return f"₦{text}" if rng.random() < 0.1 else text


def _casing(rng: random.Random, word: str) -> str:
    return rng.choice((word.capitalize(), word.capitalize(), word, word.upper()))


def _event(rng: random.Random):
    item = rng.choice(ITEMS)
    roll = rng.random()
    context = None
    if roll < 0.35:
        qty = rng.choice((50, 50, 50, 25, 100))
        price = _round_to(rng.uniform(*_KG50[item]) * qty / 50, 500)
        old = price - rng.choice((1000, 1500, 2000, 3000))
        template, unit = rng.choice(_KG_TEMPLATES), "kg"
    elif roll < 0.5:
        qty, unit = 50, "kg"
        price = _round_to(rng.uniform(*_KG50[item]), 500)
        old = price - 2000
        template = rng.choice(_BARE_TEMPLATES)
    elif roll < 0.62:
        qty, unit = 1, "bag"
        price = _round_to(rng.uniform(*_KG50[item]), 500)
        old = price - 2000
        template = rng.choice(_BAG_TEMPLATES)
    else:
        unit = rng.choice(("mudu", "mudu", "derica", "paint"))
        qty = 1
        price = _round_to(rng.uniform(*_MUDU[item]) * _MEASURE_FACTOR[unit])
        old = price - rng.choice((100, 150, 200, 300))
        if rng.random() < 0.3:
            template, context = rng.choice(_CONTEXT_TEMPLATES), item
        else:
            template = rng.choice(_MEASURE_TEMPLATES)
    text = template.format(
        I=_casing(rng, item), i=item, Q=qty if unit == "kg" else "", P=_price_text(rng, price),
        O=_price_text(rng, old), U=unit,
    )
    row = {"text": text, "kind": "event", "gold": {"item": item, "qty": qty, "unit": unit, "price_ngn": price}}
    if context:
        row["context_item"] = context
    return row


def _not_price(rng: random.Random):
    text = rng.choice(_NOT_PRICE).format(
        I=_casing(rng, rng.choice(ITEMS)), i=rng.choice(ITEMS), n=rng.choice((2, 3, 5, 10, 20)),
        U=rng.choice(("mudu", "bags", "derica", "paint")), t=rng.choice((2, 3, 4, 5, 6)),
    )
    return {"text": text, "kind": "not_price", "gold": None}


def generate(n: int, seed: int, exclude: set[str] | None = None) -> list[dict]:
    rng = random.Random(seed)
    seen = {" ".join(t.lower().split()) for t in (exclude or ())}
    rows = []
    for _ in range(n * 200):
        if len(rows) == n:
            break
        row = _not_price(rng) if rng.random() < 0.22 else _event(rng)
        key = " ".join(row["text"].lower().split())
        if key in seen:
            continue
        seen.add(key)
        row["text"] = " ".join(row["text"].split())
        row["source"] = "synthetic_generated"
        rows.append(row)
    return rows
