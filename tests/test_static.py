import re
from pathlib import Path

STATIC = Path(__file__).resolve().parents[1] / "derica" / "static"
CSS = (STATIC / "app.css").read_text(encoding="utf-8")
HTML = (STATIC / "index.html").read_text(encoding="utf-8")
JS = (STATIC / "app.js").read_text(encoding="utf-8")


def test_page_css_uses_tokens_only_for_colour_and_font():
    # Hallmark "locked tokens": no raw colour literal and no font-family outside tokens.css.
    body = re.sub(r"@font-face\s*\{.*?\}", "", CSS, flags=re.S)
    assert not re.search(r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(|oklch\(", body)
    assert not re.search(r"font-family:\s*(?!var\()", body)


def test_no_transition_all_and_no_italic_headings():
    assert "transition: all" not in CSS and "transition-property: all" not in CSS
    assert "font-style: italic" not in CSS


def test_motion_has_a_reduced_motion_fallback_in_css_and_js():
    assert "prefers-reduced-motion: reduce" in CSS
    assert "prefers-reduced-motion" in JS


def test_every_asset_the_page_links_exists():
    for ref in re.findall(r'(?:href|src)="/static/([^"]+)"', HTML) + re.findall(r'url\("/static/([^"]+)"\)', CSS):
        assert (STATIC / ref).is_file(), ref


def test_the_page_never_assigns_user_text_through_innerhtml():
    assert "innerHTML" not in JS


def test_every_focus_target_has_a_visible_focus_style():
    assert ":focus-visible" in CSS and "outline: 2px solid var(--color-focus)" in CSS
