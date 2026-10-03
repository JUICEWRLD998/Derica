"""Freeze the two test sets with SHA256 hashes and write the Tinker training file.

Run once. After the freeze, nothing in data/frozen/ may change; the hash test fails if it does.
"""

import hashlib
import json
from pathlib import Path

from derica.dataset import make_examples

DATA = Path(__file__).resolve().parents[1] / "data"
FROZEN = DATA / "frozen"
FROZEN.mkdir(exist_ok=True)


def read(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def write(path, rows):
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")


write(FROZEN / "real_test.jsonl", read(DATA / "real" / "friend_messages.jsonl"))
supplied = [r for r in read(DATA / "synthetic" / "trader_messages.jsonl") if r["kind"] != "ambiguous"]
write(FROZEN / "supplied_test.jsonl", supplied)
manifest = {
    "note": "Frozen 2026-10-03 after the rules baseline was written. Do not edit.",
    "files": {n: hashlib.sha256((FROZEN / n).read_bytes()).hexdigest() for n in ("real_test.jsonl", "supplied_test.jsonl")},
}
(FROZEN / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

(DATA / "tinker").mkdir(exist_ok=True)
write(DATA / "tinker" / "train.jsonl", make_examples(read(DATA / "synthetic" / "train.jsonl")))
print(manifest["files"], len(read(DATA / "tinker" / "train.jsonl")), "training examples")
