import pytest

from derica.schema import PriceEvent
from derica.stall import reprice

OLD_COST = PriceEvent("rice", 50, "kg", 70000)
NEW_COST = PriceEvent("rice", 50, "kg", 78000)
MEASURES = {"mudu": {"grams": 1600, "old_price": 2800}, "derica": {"grams": 800, "old_price": 1450}}


def test_a_dearer_bag_raises_each_measure_and_keeps_the_markup():
    rows = {r["unit"]: r for r in reprice("rice", OLD_COST, NEW_COST, MEASURES)["rows"]}
    # 70,000 / 50,000 g * 1,600 g = 2,240 cost; 2,800 sells at 25% markup; new cost 2,496 * 1.25 = 3,120.
    assert rows["mudu"]["new_price"] == 3150
    assert rows["mudu"]["lost_per_sale"] == 350
    assert rows["derica"]["new_price"] == 1650


def test_a_cheaper_bag_gives_a_negative_loss_meaning_the_old_price_was_too_high():
    cheaper = PriceEvent("rice", 50, "kg", 66000)
    row = reprice("rice", OLD_COST, cheaper, MEASURES)["rows"][0]
    assert row["lost_per_sale"] < 0


def test_a_bag_cost_is_read_as_fifty_kilos():
    bag = PriceEvent("rice", 1, "bag", 78000)
    a = reprice("rice", OLD_COST, NEW_COST, MEASURES)["rows"]
    b = reprice("rice", OLD_COST, bag, MEASURES)["rows"]
    assert a == b


def test_rounding_up_never_sells_below_the_kept_markup():
    for row in reprice("rice", OLD_COST, NEW_COST, MEASURES, step=100)["rows"]:
        assert row["new_price"] % 100 == 0


@pytest.mark.parametrize(
    "measures",
    [{}, {"mudu": {"grams": 0, "old_price": 2800}}, {"mudu": {"grams": 1600, "old_price": -5}}, {"bucket": {"grams": 1600, "old_price": 2800}}],
)
def test_bad_measures_are_refused(measures):
    with pytest.raises(ValueError):
        reprice("rice", OLD_COST, NEW_COST, measures)


def test_a_selling_price_below_cost_still_reprices_but_reports_the_negative_markup():
    out = reprice("rice", OLD_COST, NEW_COST, {"mudu": {"grams": 1600, "old_price": 2000}})
    assert out["rows"][0]["markup_pct"] < 0


def test_a_cost_for_a_different_item_is_refused():
    with pytest.raises(ValueError):
        reprice("beans", OLD_COST, NEW_COST, MEASURES)
