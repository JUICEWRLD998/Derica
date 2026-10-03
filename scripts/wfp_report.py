"""Print median retail-over-wholesale markup by year for rice, gari, groundnuts."""

import csv
from pathlib import Path

from derica.wfp import markup_by_year

FILE = Path(__file__).resolve().parents[1] / "data" / "wfp" / "wfp_food_prices_nga.csv"
WANT = ("Rice (local)", "Gari (white)", "Groundnuts (shelled)")
rows = [r for r in csv.DictReader(FILE.open(encoding="utf-8")) if not r["date"].startswith("#") and r["commodity"] in WANT]
result = markup_by_year(rows)
years = sorted({y for _, y in result if y >= 2015})
print("year   " + "  ".join(f"{c[:12]:>12}" for c in WANT))
for y in years:
    print(y, "  " + "  ".join(f"{result[(c, y)]:>11.1%}" if (c, y) in result else f"{'-':>12}" for c in WANT))
