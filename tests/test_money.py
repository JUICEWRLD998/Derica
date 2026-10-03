import pytest

from derica.money import parse_naira


@pytest.mark.parametrize(
    "text, expected",
    [
        ("₦2,500", 2500),
        ("2500", 2500),
        ("N2,500", 2500),
        ("NGN 2,500", 2500),
        ("82k", 82000),
        ("82K", 82000),
        ("2.5k", 2500),
        ("82 thousand", 82000),
        ("82,000", 82000),
    ],
)
def test_parses_the_ways_people_write_naira(text, expected):
    assert parse_naira(text) == expected


def test_k_and_comma_forms_agree():
    assert parse_naira("82k") == parse_naira("82,000") == parse_naira("82 thousand")


@pytest.mark.parametrize("text", ["", "abc", "₦", "k", "0", "-500", "₦0"])
def test_rejects_anything_that_is_not_a_positive_price(text):
    with pytest.raises(ValueError):
        parse_naira(text)
