"""WCAG 2.x contrast ratios for the colour pairs in derica/static/tokens.css.

Run: uv run python scripts/contrast.py   (exit 1 if any required pair fails)
"""

import re
import sys
from pathlib import Path

TOKENS = Path(__file__).resolve().parents[1] / "derica" / "static" / "tokens.css"
# (foreground, background, minimum ratio, what it is)
PAIRS = [
    ("ink", "ground", 4.5, "body text"),
    ("muted", "ground", 4.5, "secondary text"),
    ("muted", "surface", 4.5, "secondary text on a panel"),
    ("ink", "surface", 4.5, "text on a panel"),
    ("accent", "ground", 4.5, "accent text on the page"),
    ("accent", "surface", 4.5, "accent text on a panel"),
    ("accent-ink", "accent", 4.5, "button label"),
    ("loss", "ground", 4.5, "loss text on the page"),
    ("loss", "surface", 4.5, "loss text on a panel"),
    ("on-band", "band", 4.5, "wordmark on the header band"),
    ("band-muted", "band", 4.5, "line on the header band"),
    ("focus", "ground", 3.0, "focus ring"),
    ("focus", "surface", 3.0, "focus ring on a panel"),
    ("edge", "ground", 3.0, "field border"),
    ("edge", "surface", 3.0, "field border on a panel"),
]


def channel(v: float) -> float:
    return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4


def luminance(hex_colour: str) -> float:
    r, g, b = (int(hex_colour[i : i + 2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def ratio(fg: str, bg: str) -> float:
    a, b = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def themes(css: str) -> dict[str, dict[str, str]]:
    """Return {'light': {...}, 'dark': {...}} from the :root and the dark blocks."""
    out = {}
    for name, pattern in (("light", r":root\s*\{(.*?)\}"), ("dark", r':root\[data-theme="dark"\]\s*\{(.*?)\}')):
        block = re.search(pattern, css, re.S).group(1)
        out[name] = {k: v for k, v in re.findall(r"--color-([\w-]+):\s*(#[0-9a-fA-F]{6})", block)}
    return out


def check(css: str) -> list[str]:
    failures = []
    for theme, colours in themes(css).items():
        for fg, bg, minimum, what in PAIRS:
            value = ratio(colours[fg], colours[bg])
            if value < minimum:
                failures.append(f"{theme}: {what} ({fg} on {bg}) {value:.2f}:1 < {minimum}:1")
    return failures


if __name__ == "__main__":
    css = TOKENS.read_text(encoding="utf-8")
    for theme, colours in themes(css).items():
        for fg, bg, minimum, what in PAIRS:
            print(f"{theme:5} {what:32} {ratio(colours[fg], colours[bg]):5.2f}:1  (needs {minimum})")
    problems = check(css)
    print("\n".join(problems) or "all pairs pass")
    sys.exit(1 if problems else 0)
