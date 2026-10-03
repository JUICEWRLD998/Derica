from derica.rules_baseline import parse_message
from derica.schema import PriceEvent


def test_reads_a_kilogram_price_with_k_suffix():
    assert parse_message("Rice 50kg now 78k") == PriceEvent("rice", 50, "kg", 78000)


def test_reads_a_per_mudu_price_with_a_comma_number():
    assert parse_message("Garri na 2,000 mudu today") == PriceEvent("garri", 1, "mudu", 2000)


def test_takes_the_item_from_the_conversation_when_the_message_omits_it():
    assert parse_message("I fit give you 2,900 mudu", context_item="rice") == PriceEvent(
        "rice", 1, "mudu", 2900
    )


def test_a_message_with_no_item_and_no_context_is_rejected():
    assert parse_message("I fit give you 2,900 mudu") is None


def test_a_bare_bag_sized_price_means_a_fifty_kilo_bag():
    assert parse_message("Beans no dey cheap again, 92k now") == PriceEvent("beans", 50, "kg", 92000)


def test_a_per_bag_price_is_one_bag():
    assert parse_message("Garri 55k per bag, no delivery inside") == PriceEvent("garri", 1, "bag", 55000)


def test_a_quantity_with_no_price_is_not_a_price():
    assert parse_message("If you take 5 bags I fit reduce am small") is None
    assert parse_message("If na 10 mudu I go give you better price") is None


def test_a_message_naming_an_item_without_a_number_is_not_a_price():
    assert parse_message("Abeg check the rice price for me before you come") is None


def test_the_baseline_scores_on_the_real_message_set():
    # Measured, not asserted as a goal: this pins the baseline's current score so a
    # rule change that moves it shows up in review.
    import json
    from pathlib import Path

    rows = [
        json.loads(line)
        for line in (Path(__file__).resolve().parents[1] / "data" / "real" / "friend_messages.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    wrong = []
    for row in rows:
        got = parse_message(row["text"], row.get("context_item"))
        want = PriceEvent(**row["gold"]) if row["gold"] else None
        if got != want:
            wrong.append(row["id"])
    assert wrong == []


def test_a_message_the_rules_cannot_read_returns_none_instead_of_crashing():
    # "N82,000" glues the currency letter to the number, so the scanner sees a stray "000".
    assert parse_message("N82,000 for beans (50 kilo)") is None
