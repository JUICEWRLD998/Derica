import pytest

from derica.readers import MAX_TEXT, plausible, read_message
from derica.schema import PriceEvent


def model_says(reply):
    return lambda text, context_item: reply


def raises(text, context_item):
    raise RuntimeError("sampler down")


RICE = PriceEvent("rice", 50, "kg", 78000)


def test_a_fifteen_million_naira_bag_is_not_plausible():
    assert not plausible(PriceEvent("rice", 50, "kg", 15_000_000))
    assert not plausible(PriceEvent("rice", 1, "mudu", 40))
    assert plausible(RICE)
    assert plausible(PriceEvent("garri", 1, "derica", 1500))


def test_the_model_reply_is_used_when_it_is_valid():
    result = read_message("Rice 50kg 78k", None, model=model_says('{"item":"rice","qty":50,"unit":"kg","price_ngn":78000}'))
    assert result.chosen == RICE and result.reader == "derica"


def test_the_rules_answer_when_the_model_is_down_and_the_page_says_so():
    result = read_message("Rice 50kg now 78k", None, model=raises)
    assert result.chosen == RICE and result.reader == "rules"
    assert "model" in result.note.lower()


def test_the_rules_answer_when_the_model_reply_is_not_valid_json():
    result = read_message("Rice 50kg now 78k", None, model=model_says("<think>"))
    assert result.reader == "rules" and result.chosen == RICE


def test_a_model_null_means_not_a_price_even_if_the_rules_would_guess():
    result = read_message("Rice 50kg now 78k", None, model=model_says("null"))
    assert result.chosen is None and result.reader == "derica"


def test_an_implausible_model_price_is_rejected_not_shown():
    reply = '{"item":"rice","qty":50,"unit":"kg","price_ngn":15000000}'
    result = read_message("how much be your rice?", None, model=model_says(reply))
    assert result.chosen is None
    assert "out of range" in result.note


def test_both_readers_are_reported_for_the_comparison_view():
    result = read_message("Rice 50kg 78k", None, model=model_says("null"))
    assert [r["name"] for r in result.readers] == ["Derica model", "Rules"]


def test_empty_and_too_long_text_are_refused():
    with pytest.raises(ValueError):
        read_message("   ", None, model=raises)
    with pytest.raises(ValueError):
        read_message("x" * (MAX_TEXT + 1), None, model=raises)
