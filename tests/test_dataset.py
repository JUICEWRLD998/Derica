import pytest

from derica.dataset import build_completion, build_prompt, make_examples, parse_completion
from derica.schema import PriceEvent

ROW = {"text": "Rice 50kg now 78k", "kind": "event", "gold": {"item": "rice", "qty": 50, "unit": "kg", "price_ngn": 78000}}
NOT_PRICE = {"text": "How many bags you want?", "kind": "not_price", "gold": None}


def test_prompt_carries_the_message_and_the_topic():
    assert "Message: Rice 50kg now 78k" in build_prompt("Rice 50kg now 78k", None)
    assert "Topic: none" in build_prompt("Rice 50kg now 78k", None)
    assert "Topic: rice" in build_prompt("2,900 mudu", "rice")


def test_completion_round_trips_through_the_strict_parser():
    assert parse_completion(build_completion(ROW)) == PriceEvent("rice", 50, "kg", 78000)


def test_a_non_price_completes_to_null():
    assert build_completion(NOT_PRICE) == "null"
    assert parse_completion("null") is None


@pytest.mark.parametrize("bad", ["", "rice 78k", '{"item": "rice"}', '{"item":"rice","qty":50,"unit":"kg","price_ngn":78000,"x":1}', "[1]"])
def test_model_output_that_is_not_a_valid_event_is_rejected(bad):
    with pytest.raises(ValueError):
        parse_completion(bad)


def test_examples_pair_each_row_with_prompt_and_completion():
    examples = make_examples([ROW, NOT_PRICE])
    assert [e["completion"] for e in examples] == [build_completion(ROW), "null"]
    assert all(set(e) == {"prompt", "completion"} for e in examples)


def test_few_shot_prompt_states_the_conventions_and_ends_with_the_message():
    from derica.dataset import build_few_shot_prompt

    prompt = build_few_shot_prompt("Rice 50kg now 78k", None)
    assert "50 kg bag" in prompt and "qty is 1" in prompt
    assert prompt.count("Message:") == 11  # ten worked examples plus the real message
    assert prompt.rstrip().endswith("JSON:")
    assert "Message: Rice 50kg now 78k\nJSON:" in prompt


def test_no_few_shot_example_is_a_frozen_test_message():
    import json
    from pathlib import Path

    from derica.dataset import _SHOTS

    frozen = Path(__file__).resolve().parents[1] / "data" / "frozen"
    texts = {
        " ".join(json.loads(line)["text"].lower().split())
        for name in ("real_test.jsonl", "supplied_test.jsonl")
        for line in (frozen / name).read_text(encoding="utf-8").splitlines()
    }
    for message, _topic, _answer in _SHOTS:
        assert " ".join(message.lower().split()) not in texts
