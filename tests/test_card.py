import io

import pytest
from PIL import Image

from derica.card import MAX_ITEMS, render_card

ITEMS = [
    {"item": "rice", "prices": {"mudu": 3150, "derica": 1650, "paint": 13850}},
    {"item": "beans", "prices": {"mudu": 3800}},
]


def decode(data):
    return Image.open(io.BytesIO(data))


def test_the_card_is_a_whatsapp_status_sized_png():
    image = decode(render_card("Amina Grains", "3 Oct 2026", ITEMS))
    assert image.format == "PNG" and image.size == (1080, 1920)


def test_the_same_input_gives_the_same_bytes():
    assert render_card("Amina Grains", "3 Oct 2026", ITEMS) == render_card("Amina Grains", "3 Oct 2026", ITEMS)


def test_a_different_price_changes_the_picture():
    other = [{"item": "rice", "prices": {"mudu": 3200}}]
    assert render_card("Amina Grains", "3 Oct 2026", ITEMS[:1]) != render_card("Amina Grains", "3 Oct 2026", other)


def test_the_card_has_ink_on_it_and_is_not_blank():
    image = decode(render_card("Amina Grains", "3 Oct 2026", ITEMS)).convert("L")
    dark = sum(image.histogram()[:90])
    assert dark > 5_000


def test_no_items_is_refused_instead_of_drawing_an_empty_board():
    with pytest.raises(ValueError):
        render_card("Amina Grains", "3 Oct 2026", [])


def test_too_many_items_and_a_bad_price_are_refused():
    with pytest.raises(ValueError):
        render_card("S", "d", [{"item": "rice", "prices": {"mudu": 1}}] * (MAX_ITEMS + 1))
    with pytest.raises(ValueError):
        render_card("S", "d", [{"item": "rice", "prices": {"mudu": -4}}])
    with pytest.raises(ValueError):
        render_card("S", "d", [{"item": "rice", "prices": {"bucket": 400}}])


def test_a_very_long_shop_name_still_fits_inside_the_card():
    render_card("A" * 200, "3 Oct 2026", ITEMS)  # must not raise; the name is shortened


def test_the_naira_sign_is_drawn_not_a_missing_glyph_box():
    from PIL import ImageFont

    from derica.card import FONT_DISPLAY, display_font

    font = display_font(80)
    naira = font.getmask("₦").getbbox()
    missing = font.getmask("￿").getbbox()
    assert naira is not None and naira != missing


def test_a_full_card_of_four_items_keeps_every_price_above_the_footer():
    full = [{"item": n, "prices": {"derica": 1650, "mudu": 3150, "paint": 13850}} for n in ("rice", "beans", "garri", "groundnut")]
    image = decode(render_card("Amina Grains", "3 Oct 2026", full)).convert("L")
    band = image.crop((0, 1740, 1080, 1800))  # the gap just above the footer text must be empty ground
    assert min(band.getdata()) > 200
