import pytest

from derica.schema import PriceEvent


def test_valid_event_is_kept_as_given():
    event = PriceEvent(item="Rice", qty=1, unit="mudu", price_ngn=2500, side="sell")
    assert event.item == "rice"
    assert event.qty == 1
    assert event.unit == "mudu"
    assert event.price_ngn == 2500
    assert event.side == "sell"


def test_event_can_be_built_from_model_json():
    event = PriceEvent.from_json('{"item": "garri", "qty": 2, "unit": "paint", "price_ngn": 9000, "side": "buy"}')
    assert event == PriceEvent(item="garri", qty=2, unit="paint", price_ngn=9000, side="buy")


@pytest.mark.parametrize(
    "field, value",
    [
        ("qty", 0),
        ("qty", -1),
        ("price_ngn", 0),
        ("price_ngn", -500),
        ("price_ngn", 2500.5),
        ("unit", "bucket"),
        ("side", "swap"),
        ("item", "   "),
    ],
)
def test_garbage_fields_are_rejected(field, value):
    good = {"item": "rice", "qty": 1, "unit": "mudu", "price_ngn": 2500, "side": "sell"}
    good[field] = value
    with pytest.raises(ValueError):
        PriceEvent(**good)


@pytest.mark.parametrize(
    "text",
    ["not json", "[]", '{"item": "rice"}', '{"item": "rice", "qty": 1, "unit": "mudu", "price_ngn": 2500, "side": "sell", "extra": 1}'],
)
def test_json_with_wrong_shape_is_rejected(text):
    with pytest.raises(ValueError):
        PriceEvent.from_json(text)
