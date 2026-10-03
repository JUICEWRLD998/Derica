"""Write and freeze the hard test set: second hand-written set.

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
SOURCE = "synthetic_hand_written_hard2"


def ev(item, qty, unit, price):
    return {"item": item, "qty": qty, "unit": unit, "price_ngn": price}


# (text, gold, context_item, kind)
ROWS = [
    ("oga rice 50kg don jump to eighty one thousand", ev("rice", 50, "kg", 81000), None, "event"),
    ("beans na 93,500 naira for the 50 kilo", ev("beans", 50, "kg", 93500), None, "event"),
    ("Gari - 25kg - 27.5k", ev("garri", 25, "kg", 27500), None, "event"),
    ("groundnuts 106k, supplier no gree reduce", ev("groundnut", 50, "kg", 106000), None, "event"),
    ("rice derica now na 1,400", ev("rice", 1, "derica", 1400), None, "event"),
    ("sugar 52k a bag", None, None, "out_of_scope"),
    ("Tomato basket 8k", None, None, "out_of_scope"),
    ("palm oil 25 litres 60k", None, None, "out_of_scope"),
    ("Garri 54k + 2k for transport", ev("garri", 50, "kg", 54000), None, "event"),
    ("Rice 50kg: N79,500", ev("rice", 50, "kg", 79500), None, "event"),
    ("I go sell am 2,600 mudu", ev("rice", 1, "mudu", 2600), "rice", "event"),
    ("how far, wetin be the price now", None, None, "not_price"),
    ("beans don finish, new stock Tuesday", None, None, "not_price"),
    ("I get 40 bags of garri for you", None, None, "not_price"),
    ("rice 100kg na 158k", ev("rice", 100, "kg", 158000), None, "event"),
    ("Groundnut na 3,900 mudu o", ev("groundnut", 1, "mudu", 3900), None, "event"),
    ("bean 25kg 47k", ev("beans", 25, "kg", 47000), None, "event"),
    ("rice is #76,000 now", ev("rice", 50, "kg", 76000), None, "event"),
    ("garri 1 bag 55,500", ev("garri", 1, "bag", 55500), None, "event"),
    ("e don reach 1,900 derica", ev("beans", 1, "derica", 1900), "beans", "event"),
    ("Pepper 4k per paint", None, None, "out_of_scope"),
    ("Please confirm you receive the transfer", None, None, "not_price"),
    ("gari dey 51k, delivery 2.5k", ev("garri", 50, "kg", 51000), None, "event"),
    ("I buy rice seventy seven thousand last week", ev("rice", 50, "kg", 77000), None, "event"),
    ("Beans 50kg ninety thousand five hundred", ev("beans", 50, "kg", 90500), None, "event"),
    ("groundnut 98k for 50kg, no be 100k", ev("groundnut", 50, "kg", 98000), None, "event"),
    ("rice price: 80k (50kg bag)", ev("rice", 50, "kg", 80000), None, "event"),
    ("maize 30k bag", None, None, "out_of_scope"),
    ("garri paint na 1,700 now", ev("garri", 1, "paint", 1700), None, "event"),
]

rows = []
for i, (text, gold, context_item, kind) in enumerate(ROWS, 1):
    row = {"id": f"h-{i:02d}", "text": text, "kind": kind, "gold": gold, "source": SOURCE}
    if context_item:
        row["context_item"] = context_item
    rows.append(row)

path = FROZEN / "hard2_test.jsonl"
path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")

manifest_path = FROZEN / "MANIFEST.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["files"]["hard2_test.jsonl"] = hashlib.sha256(path.read_bytes()).hexdigest()
manifest["hard2_note"] = "hard2_test.jsonl frozen 2026-10-03 before the v2 training data existed or any system ran on it. Synthetic, hand-written."
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(len(rows), "rows", manifest["files"]["hard2_test.jsonl"])
