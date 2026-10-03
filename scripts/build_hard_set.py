"""Write and freeze the hard test set: 40 hand-written messy messages.

These are SYNTHETIC. I wrote them, not Amina, to stress spellings and layouts that the
training generator never produced: number words, "#" for naira, typos in the item name,
a delivery fee beside the price, a non-grain item, Pidgin phrasing. Gold follows Amina's
stated conventions. They were written before any model or rule saw them and are not to be
tuned on. Run once; the hash test fails if the file changes afterwards.
"""

import hashlib
import json
from pathlib import Path

FROZEN = Path(__file__).resolve().parents[1] / "data" / "frozen"
SOURCE = "synthetic_hand_written_hard"


def ev(item, qty, unit, price):
    return {"item": item, "qty": qty, "unit": unit, "price_ngn": price}


# (text, gold, context_item, kind)
ROWS = [
    ("rice na seventy eight thousand for 50kg", ev("rice", 50, "kg", 78000), None, "event"),
    ("abeg beans don reach 95k o, e no easy", ev("beans", 50, "kg", 95000), None, "event"),
    ("Garri now na 2500 per derica", ev("garri", 1, "derica", 2500), None, "event"),
    ("groundnut paint na 1,800", ev("groundnut", 1, "paint", 1800), None, "event"),
    ("rice 78,000 naira", ev("rice", 50, "kg", 78000), None, "event"),
    ("N82,000 for beans (50 kilo)", ev("beans", 50, "kg", 82000), None, "event"),
    ("garri 25kg 28k", ev("garri", 25, "kg", 28000), None, "event"),
    ("Rice 25 kg bag now 41k", ev("rice", 25, "kg", 41000), None, "event"),
    ("oga rice don cost, na 80k bag", ev("rice", 1, "bag", 80000), None, "event"),
    ("how much be your rice?", None, None, "not_price"),
    ("rice dey, come collect", None, None, "not_price"),
    ("I wan buy 20 bags of garri", None, None, "not_price"),
    ("Garri 52k, I dey pay am cash", ev("garri", 50, "kg", 52000), None, "event"),
    ("beans is 3k a mudu now", ev("beans", 1, "mudu", 3000), None, "event"),
    ("rice 50kg #77,500", ev("rice", 50, "kg", 77500), None, "event"),
    ("Rice - 50kg - 77.5k", ev("rice", 50, "kg", 77500), None, "event"),
    ("Groundnut 104k oo, supplier just call me", ev("groundnut", 50, "kg", 104000), None, "event"),
    ("garri na 1,500 paint", ev("garri", 1, "paint", 1500), None, "event"),
    ("price of rice for 50kg is 79k", ev("rice", 50, "kg", 79000), None, "event"),
    ("I buy beans 88k yesterday", ev("beans", 50, "kg", 88000), None, "event"),
    ("Rice price na 78k, abeg no go lower", ev("rice", 50, "kg", 78000), None, "event"),
    ("garri 2,200 derica, e don cheap", ev("garri", 1, "derica", 2200), None, "event"),
    ("Thank you ma, I go send money tomorrow", None, None, "not_price"),
    ("rice 100kg 150k", ev("rice", 100, "kg", 150000), None, "event"),
    ("beans 1 bag 91k", ev("beans", 1, "bag", 91000), None, "event"),
    ("groundnut oil 5 litres 18k", None, None, "out_of_scope"),
    ("Yam 5k each", None, None, "out_of_scope"),
    ("Bean 90k", ev("beans", 50, "kg", 90000), None, "event"),
    ("Gari 50kg 55k", ev("garri", 50, "kg", 55000), None, "event"),
    ("groundnuts 100k", ev("groundnut", 50, "kg", 100000), None, "event"),
    ("e be 2,700 derica", ev("garri", 1, "derica", 2700), "garri", "event"),
    ("na 94k now", ev("beans", 50, "kg", 94000), "beans", "event"),
    ("Ok na 2,800 paint then", ev("rice", 1, "paint", 2800), "rice", "event"),
    ("send me your account number", None, "rice", "not_price"),
    ("Rice: ₦78,000 / 50kg bag", ev("rice", 50, "kg", 78000), None, "event"),
    ("rice 50kg, 78k, delivery 3k extra", ev("rice", 50, "kg", 78000), None, "event"),
    ("garri price: 50kg = 56k", ev("garri", 50, "kg", 56000), None, "event"),
    ("Na 2,500 I dey sell rice derica", ev("rice", 1, "derica", 2500), None, "event"),
    ("Rice 50kg don become 81k", ev("rice", 50, "kg", 81000), None, "event"),
]

rows = []
for i, (text, gold, context_item, kind) in enumerate(ROWS, 1):
    row = {"id": f"h-{i:02d}", "text": text, "kind": kind, "gold": gold, "source": SOURCE}
    if context_item:
        row["context_item"] = context_item
    rows.append(row)

path = FROZEN / "hard_test.jsonl"
path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")

manifest_path = FROZEN / "MANIFEST.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["files"]["hard_test.jsonl"] = hashlib.sha256(path.read_bytes()).hexdigest()
manifest["hard_note"] = "hard_test.jsonl frozen 2026-10-03 before any system was run on it. Synthetic, hand-written."
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(len(rows), "rows", manifest["files"]["hard_test.jsonl"])
