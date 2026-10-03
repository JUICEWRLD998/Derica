import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import contrast  # noqa: E402
from derica import card  # noqa: E402

CSS = (ROOT / "derica" / "static" / "tokens.css").read_text(encoding="utf-8")


def test_every_colour_pair_meets_its_contrast_threshold_in_both_themes():
    assert contrast.check(CSS) == []


def test_the_contrast_check_fails_on_a_planted_bad_pair():
    # Control: make secondary text the same colour as the page. The check must notice.
    broken = CSS.replace("--color-muted: #4b5b66;", "--color-muted: #f3f6f5;")
    assert any("secondary text" in line for line in contrast.check(broken))


def test_the_card_uses_the_light_tokens():
    light = contrast.themes(CSS)["light"]
    assert (card.GROUND, card.INK, card.ACCENT, card.MUTED, card.RULE, card.ON_INK) == (
        light["ground"], light["ink"], light["accent"], light["muted"], light["rule"], light["on-band"],
    )


def test_the_system_dark_block_matches_the_explicit_dark_block():
    explicit = re.search(r':root\[data-theme="dark"\]\s*\{(.*?)\}', CSS, re.S).group(1)
    media = re.search(r"@media \(prefers-color-scheme: dark\) \{\s*:root:not\(\[data-theme=\"light\"\]\) \{(.*?)\}", CSS, re.S).group(1)
    pick = lambda block: dict(re.findall(r"--color-([\w-]+):\s*(#[0-9a-f]{6})", block))
    assert pick(explicit) == pick(media)
