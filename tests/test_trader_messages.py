import json
from collections import Counter
from pathlib import Path

from derica.schema import PriceEvent

FILE = Path(__file__).resolve().parents[1] / "data" / "synthetic" / "trader_messages.jsonl"


def load():
    return [json.loads(line) for line in FILE.read_text(encoding="utf-8").splitlines()]


def test_forty_five_messages_all_marked_synthetic():
    rows = load()
    assert len(rows) == 45
    assert {r["source"] for r in rows} == {"synthetic_supplied_for_testing"}


def test_kinds_and_labels_are_consistent():
    rows = load()
    assert Counter(r["kind"] for r in rows) == {"event": 26, "not_price": 17, "ambiguous": 2}
    for r in rows:
        if r["kind"] == "event":
            PriceEvent(**r["gold"])
        else:
            assert r["gold"] is None
