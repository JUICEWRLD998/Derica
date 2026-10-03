from pathlib import Path

import pytest

from derica.rules_parser import parse_line
from derica.schema import PriceEvent

REAL = Path(__file__).resolve().parents[1] / "data" / "real" / "friend_sell_prices.txt"

# Written by hand from what the friend sent, independent of the parser.
EXPECTED = [
    ("rice", 2500), ("beans", 3200), ("garri", 1800), ("maize", 2000), ("millet", 2300),
    ("groundnut", 3500), ("soya beans", 2800), ("yam flour", 2700), ("semovita", 3000),
    ("millet", 2400), ("white beans", 3300), ("brown beans", 3100), ("garri", 1900),
    ("rice", 2600), ("groundnut", 3600),
]


def test_parses_all_fifteen_real_messages_from_the_friend():
    lines = REAL.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 15
    events = [parse_line(line) for line in lines]
    assert [(e.item, e.price_ngn) for e in events] == EXPECTED
    assert all(e.unit == "mudu" and e.qty == 1 and e.side == "sell" for e in events)


def test_numbering_and_dash_style_do_not_matter():
    expected = PriceEvent(item="rice", qty=1, unit="mudu", price_ngn=2500, side="sell")
    assert parse_line("Rice — ₦2,500 mudu") == expected
    assert parse_line("3) rice - N2500 mudu") == expected
    assert parse_line("RICE – 2.5k Mudu") == expected


@pytest.mark.parametrize(
    "line",
    ["", "Rice", "Rice — mudu", "Rice — ₦2,500", "hello how are you", "Rice — ₦0 mudu", "Rice — ₦2,500 bucket"],
)
def test_lines_that_are_not_price_messages_are_rejected_not_guessed(line):
    with pytest.raises(ValueError):
        parse_line(line)
