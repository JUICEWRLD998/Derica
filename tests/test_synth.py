import json
from collections import Counter
from pathlib import Path

from derica.schema import PriceEvent
from derica.synth import generate

DATA = Path(__file__).resolve().parents[1] / "data"


def frozen_texts() -> set[str]:
    texts = set()
    for name in ("real/friend_messages.jsonl", "synthetic/trader_messages.jsonl"):
        for line in (DATA / name).read_text(encoding="utf-8").splitlines():
            texts.add(" ".join(json.loads(line)["text"].lower().split()))
    return texts


def test_same_seed_gives_same_rows():
    assert generate(50, seed=1) == generate(50, seed=1)
    assert generate(50, seed=1) != generate(50, seed=2)


def test_every_row_is_marked_generated_and_labelled_validly():
    for row in generate(200, seed=3):
        assert row["source"] == "synthetic_generated"
        if row["kind"] == "event":
            PriceEvent(**row["gold"])
        else:
            assert row["kind"] == "not_price" and row["gold"] is None


def test_no_duplicate_texts():
    texts = [" ".join(r["text"].lower().split()) for r in generate(300, seed=4)]
    assert len(texts) == len(set(texts))


def test_never_reproduces_a_frozen_test_message():
    frozen = frozen_texts()
    for row in generate(400, seed=5, exclude=frozen):
        assert " ".join(row["text"].lower().split()) not in frozen


def test_covers_every_unit_and_the_non_price_case():
    rows = generate(400, seed=6)
    units = {r["gold"]["unit"] for r in rows if r["kind"] == "event"}
    assert units == {"kg", "bag", "mudu", "derica", "paint"}
    assert Counter(r["kind"] for r in rows)["not_price"] > 40


def test_an_omitted_item_always_carries_context_item():
    rows = generate(400, seed=7)
    omitted = [r for r in rows if r["kind"] == "event" and r["gold"]["item"] not in r["text"].lower()]
    assert omitted
    assert all(r["context_item"] == r["gold"]["item"] for r in omitted)
