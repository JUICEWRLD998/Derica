"""The price card: a 1080 x 1920 PNG sized for a WhatsApp Status.

Drawn with Pillow from the same colour tokens as the page (derica/static/tokens.css).
Output is deterministic, so the same prices always give the same bytes.
"""

import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONTS = Path(__file__).parent / "static" / "fonts"
FONT_DISPLAY = FONTS / "BigShouldersStencil.ttf"
FONT_BODY_BOLD = FONTS / "AtkinsonHyperlegible-Bold.ttf"
FONT_BODY = FONTS / "AtkinsonHyperlegible-Regular.ttf"

WIDTH, HEIGHT = 1080, 1920
MAX_ITEMS = 4
MAX_NAME = 40
MEASURES = ("derica", "mudu", "paint")
# Light-theme tokens. A test keeps these equal to tokens.css.
GROUND, INK, ACCENT, MUTED, RULE = "#f3f6f5", "#12202b", "#0e6b5c", "#4b5b66", "#c9d3d0"
ON_INK = "#e8eeec"


def display_font(size: int) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(FONT_DISPLAY), size)
    font.set_variation_by_axes([800, 72])  # wght, opsz
    return font


def body_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT_BODY_BOLD if bold else FONT_BODY), size)


def _check(items: list[dict]) -> None:
    if not items:
        raise ValueError("a card needs at least one item")
    if len(items) > MAX_ITEMS:
        raise ValueError(f"a card holds at most {MAX_ITEMS} items")
    for entry in items:
        if not str(entry.get("item", "")).strip():
            raise ValueError("every item needs a name")
        prices = entry.get("prices") or {}
        if not prices:
            raise ValueError("every item needs at least one price")
        for unit, price in prices.items():
            if unit not in MEASURES:
                raise ValueError(f"unknown measure {unit!r}")
            if not isinstance(price, int) or isinstance(price, bool) or price <= 0:
                raise ValueError(f"{unit}: price must be a positive whole number of naira")


def _fit(draw: ImageDraw.ImageDraw, text: str, start: int, limit: int) -> ImageFont.FreeTypeFont:
    size = start
    while size > 40:
        font = display_font(size)
        if draw.textlength(text, font=font) <= limit:
            return font
        size -= 6
    return display_font(40)


def render_card(shop: str, date_text: str, items: list[dict]) -> bytes:
    _check(items)
    shop = " ".join(shop.split())[:MAX_NAME] or "Price board"
    image = Image.new("RGB", (WIDTH, HEIGHT), GROUND)
    draw = ImageDraw.Draw(image)

    draw.rectangle([0, 0, WIDTH, 330], fill=INK)
    draw.text((60, 70), shop.upper(), font=_fit(draw, shop.upper(), 168, WIDTH - 120), fill=ON_INK)
    draw.text((64, 258), date_text, font=body_font(44), fill=RULE)

    # Full-size layout needs `needed` pixels; shrink everything evenly when it would not fit.
    needed = sum(152 + len(e["prices"]) * 136 + 60 for e in items)
    scale = min(1.0, (HEIGHT - 330 - 40 - 170) / needed)
    pitch, price_size, name_size = int(136 * scale), int(116 * scale), int(104 * scale)
    y = 370
    for entry in items:
        draw.text((60, y), entry["item"].upper(), font=display_font(name_size), fill=ACCENT)
        rule = y + int(130 * scale)
        draw.line([60, rule, WIDTH - 60, rule], fill=RULE, width=4)
        row = y + int(152 * scale)
        price_font = display_font(price_size)
        for unit in MEASURES:
            if unit not in entry["prices"]:
                continue
            draw.text((60, row + int(28 * scale)), f"1 {unit}", font=body_font(max(30, int(50 * scale)), bold=True), fill=MUTED)
            price = f"₦{entry['prices'][unit]:,}"
            draw.text((WIDTH - 60 - draw.textlength(price, font=price_font), row - int(6 * scale)), price, font=price_font, fill=INK)
            row += pitch
        y = row + int(60 * scale)

    draw.text((60, HEIGHT - 110), "Priced with Derica", font=body_font(30), fill=MUTED)
    buffer = io.BytesIO()
    image.save(buffer, "PNG", optimize=False)
    return buffer.getvalue()
