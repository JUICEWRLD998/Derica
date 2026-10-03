import json
from collections import Counter
from pathlib import Path

from derica.schema import PriceEvent

FILE = Path(__file__).resolve().parents[1] / "data" / "real" / "friend_messages.jsonl"


def load():
    return [json.loads(line) for line in FILE.read_text(encoding="utf-8").splitlines()]


def test_all_eighteen_messages_are_present_in_order():
    rows = load()
    assert [r["id"] for r in rows] == list(range(1, 19))
    assert all(r["text"].strip() for r in rows)


def test_every_message_has_exactly_one_known_kind():
    kinds = Counter(r["kind"] for r in load())
    assert set(kinds) <= {"event", "incomplete", "not_price"}
    assert kinds == {"event": 11, "not_price": 7}


def test_an_item_missing_from_the_message_comes_from_the_conversation_context():
    # Amina leaves the item out when both people already know it ("2,900 mudu").
    for row in load():
        if row["kind"] == "event" and row["gold"]["item"] not in row["text"].lower():
            assert row.get("context_item") == row["gold"]["item"], row["id"]
        else:
            assert "context_item" not in row, row["id"]


def test_event_labels_build_valid_price_events():
    for row in load():
        if row["kind"] == "event":
            PriceEvent(**row["gold"])
        else:
            assert row["gold"] is None


def test_event_price_is_actually_written_in_the_message():
    # Guards labelling typos: 78000 must appear as 78k or 78,000 in the text.
    for row in load():
        if row["kind"] != "event":
            continue
        price = row["gold"]["price_ngn"]
        text = row["text"].lower().replace(" ", "")
        spellings = {f"{price:,}", f"{price // 1000}k"}
        assert any(s in text for s in spellings), row["id"]
