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


def test_default_generator_still_reproduces_the_committed_training_file():
    committed = [json.loads(l) for l in (DATA / "synthetic" / "train.jsonl").read_text(encoding="utf-8").splitlines()]
    assert generate(1500, seed=2026, exclude=frozen_texts())[:50] == committed[:50]


def test_rich_generator_adds_out_of_scope_items_with_a_null_label():
    rows = [r for r in generate(800, seed=7, rich=True) if r["kind"] == "out_of_scope"]
    assert len(rows) > 40
    for row in rows:
        assert row["gold"] is None
        assert not set(row["text"].lower().replace(",", " ").split()) & {"rice", "beans", "garri", "groundnut"}


def test_rich_generator_keeps_a_delivery_fee_out_of_the_price():
    rows = [r for r in generate(800, seed=8, rich=True) if "delivery" in r["text"].lower() and r["kind"] == "event"]
    assert rows
    assert all(r["gold"]["price_ngn"] >= 10_000 for r in rows)


def test_rich_generator_never_uses_the_hard_set_out_of_scope_items():
    text = " ".join(r["text"].lower() for r in generate(1500, seed=9, rich=True))
    assert "yam" not in text and "groundnut oil" not in text


def test_rich_generator_prices_a_message_with_no_size_as_a_fifty_kilo_bag():
    for row in generate(1500, seed=10, rich=True):
        if row["kind"] == "event" and row["gold"]["unit"] == "kg" and row["gold"]["qty"] == 50:
            low = {"rice": 70_000, "beans": 85_000, "garri": 50_000, "groundnut": 98_000}[row["gold"]["item"]]
            assert row["gold"]["price_ngn"] >= low - 500, row
