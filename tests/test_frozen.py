import hashlib
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
FROZEN = DATA / "frozen"


def norm(text):
    return " ".join(text.lower().split())


def test_frozen_files_match_their_recorded_hash():
    manifest = json.loads((FROZEN / "MANIFEST.json").read_text(encoding="utf-8"))
    assert set(manifest["files"]) == {"real_test.jsonl", "supplied_test.jsonl", "hard_test.jsonl"}
    for name, digest in manifest["files"].items():
        assert hashlib.sha256((FROZEN / name).read_bytes()).hexdigest() == digest, name


def test_no_training_message_is_in_a_frozen_test_set():
    test_texts = set()
    for name in ("real_test.jsonl", "supplied_test.jsonl", "hard_test.jsonl"):
        for line in (FROZEN / name).read_text(encoding="utf-8").splitlines():
            test_texts.add(norm(json.loads(line)["text"]))
    for line in (DATA / "synthetic" / "train.jsonl").read_text(encoding="utf-8").splitlines():
        assert norm(json.loads(line)["text"]) not in test_texts
