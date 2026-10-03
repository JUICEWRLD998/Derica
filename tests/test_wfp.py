from derica.wfp import markup_by_year, per_kg


def row(date, market, commodity, unit, pricetype, price):
    return {"date": date, "market": market, "commodity": commodity, "unit": unit, "pricetype": pricetype, "currency": "NGN", "price": str(price)}


def test_price_is_converted_to_naira_per_kilogram():
    assert per_kg(row("2020-01-15", "A", "Rice (local)", "100 KG", "Wholesale", 50000)) == 500
    assert per_kg(row("2020-01-15", "A", "Rice (local)", "2.7 KG", "Retail", 1485)) == 550
    assert per_kg(row("2020-01-15", "A", "Gari (white)", "KG", "Retail", 400)) == 400


def test_a_planted_ten_percent_markup_is_recovered():
    rows = []
    for month in ("2020-01-15", "2020-02-15", "2020-03-15"):
        rows.append(row(month, "A", "Rice (local)", "100 KG", "Wholesale", 50000))
        rows.append(row(month, "A", "Rice (local)", "2.7 KG", "Retail", 1485))
    assert round(markup_by_year(rows)[("Rice (local)", 2020)], 4) == 0.10


def test_months_with_only_one_side_are_skipped_and_an_empty_input_is_empty():
    rows = [row("2020-01-15", "A", "Rice (local)", "100 KG", "Wholesale", 50000)]
    assert markup_by_year(rows) == {}
    assert markup_by_year([]) == {}
