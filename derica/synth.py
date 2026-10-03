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


# --- rich shapes (generate(..., rich=True)) -------------------------------------------
# More ways people really type a price, and goods Amina does not sell. The out-of-scope
# goods deliberately exclude the two the hard test set uses (yam, groundnut oil).
_OTHER_GOODS = ("tomato", "pepper", "sugar", "salt", "onion", "maize", "millet", "palm oil", "plantain", "cassava", "egg")
_OTHER_TEMPLATES = ("{X} {P} each", "{X} {Q}kg {P}", "{X} na {P} today", "{X} {P} per bag", "Abeg {X} price na {P}")
_FEE_TEMPLATES = ("{I} {Q}kg, {P}, delivery {D} extra", "{I} {Q}kg {P} plus {D} for delivery", "{I} {P} for {Q}kg, delivery na {D}")
_SPELLINGS = {"garri": ("garri", "gari"), "beans": ("beans", "bean"), "groundnut": ("groundnut", "groundnuts"), "rice": ("rice",)}
_ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
_TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def _words_thousand(thousands: int) -> str:
    if thousands < 20:
        return _ONES[thousands]
    if thousands < 100:
        tens, ones = divmod(thousands, 10)
        return _TENS[tens] + (f" {_ONES[ones]}" if ones else "")
    hundreds, rest = divmod(thousands, 100)
    return f"{_ONES[hundreds]} hundred" + (f" {_words_thousand(rest)}" if rest else "")


def _rich_price(rng: random.Random, naira: int) -> str:
    roll = rng.random()
    if roll < 0.15:
        return f"N{naira:,}"
    if roll < 0.28:
        return f"{naira:,} naira"
    if roll < 0.36:
        return f"#{naira:,}"
    if roll < 0.46 and naira % 1000 == 0:
        return f"{_words_thousand(naira // 1000)} thousand"
    return _price_text(rng, naira)


def _rich_event(rng: random.Random):
    item = rng.choice(ITEMS)
    spelled = rng.choice(_SPELLINGS[item])
    roll = rng.random()
    if roll < 0.2:
        row = _event(rng)
        return row
    qty = rng.choice((50, 50, 50, 25, 100))
    price = _round_to(rng.uniform(*_KG50[item]) * qty / 50, 500)
    if roll < 0.45:
        fee = rng.choice((1000, 1500, 2000, 3000, 5000))
        text = rng.choice(_FEE_TEMPLATES).format(
            I=_casing(rng, spelled), Q=qty, P=_price_text(rng, price), D=_price_text(rng, fee))
        return {"text": text, "kind": "event", "gold": {"item": item, "qty": qty, "unit": "kg", "price_ngn": price}}
    kilo = rng.choice((f"{qty}kg", f"{qty} kilo", f"{qty}kgs", f"{qty} kg bag"))
    template = rng.choice((
        "{I} {K} {P}", "{I} {P} for {K}", "{I} na {P} for {K}", "{P} for {I} ({K})", "price of {i} for {K} is {P}",
        "{I} - {K} - {P}", "{I}: {P} / {K}", "{I} {K} don become {P}", "I buy {i} {P} yesterday",
    ))
    if "{K}" not in template:
        qty, kilo = 50, ""
        price = _round_to(rng.uniform(*_KG50[item]), 500)
    text = template.format(I=_casing(rng, spelled), i=spelled, K=kilo, P=_rich_price(rng, price))
    return {"text": text, "kind": "event", "gold": {"item": item, "qty": qty, "unit": "kg", "price_ngn": price}}


def _out_of_scope(rng: random.Random):
    text = rng.choice(_OTHER_TEMPLATES).format(
        X=_casing(rng, rng.choice(_OTHER_GOODS)), Q=rng.choice((5, 10, 25, 50)), P=_price_text(rng, rng.choice((2000, 3500, 5000, 12000, 18000, 45000))))
    return {"text": text, "kind": "out_of_scope", "gold": None}


def generate(n: int, seed: int, exclude: set[str] | None = None, rich: bool = False) -> list[dict]:
    rng = random.Random(seed)
    seen = {" ".join(t.lower().split()) for t in (exclude or ())}
    rows = []
    for _ in range(n * 200):
        if len(rows) == n:
            break
        if rich:
            roll = rng.random()
            row = _not_price(rng) if roll < 0.15 else _out_of_scope(rng) if roll < 0.25 else _rich_event(rng) if roll < 0.7 else _event(rng)
        else:
            row = _not_price(rng) if rng.random() < 0.22 else _event(rng)
        key = " ".join(row["text"].lower().split())
        if key in seen:
            continue
        seen.add(key)
        row["text"] = " ".join(row["text"].split())
        row["source"] = "synthetic_generated"
        rows.append(row)
    return rows
