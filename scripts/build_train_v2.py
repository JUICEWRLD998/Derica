"""Training file v2: the v1 rows plus 2,000 rich rows (out-of-scope goods, delivery fees,
spelling variants, number words). Excludes every frozen test text, so nothing leaks."""

import json
from pathlib import Path

from derica.dataset import make_examples
from derica.synth import generate

DATA = Path(__file__).resolve().parents[1] / "data"


def read(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


frozen = [r for name in ("real_test", "supplied_test", "hard_test", "hard2_test") for r in read(DATA / "frozen" / f"{name}.jsonl")]
v1 = read(DATA / "synthetic" / "train.jsonl")
exclude = {r["text"] for r in frozen + v1}
rich = generate(2000, seed=2027, exclude=exclude, rich=True)
rows = v1 + rich
(DATA / "synthetic" / "train_v2.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
(DATA / "tinker").mkdir(exist_ok=True)
(DATA / "tinker" / "train_v2.jsonl").write_text(
    "\n".join(json.dumps(r, ensure_ascii=False) for r in make_examples(rows)) + "\n", encoding="utf-8")
print(len(rows), "rows;", sum(r["gold"] is None for r in rows), "null")
