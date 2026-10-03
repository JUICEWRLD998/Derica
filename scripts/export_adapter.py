"""Download the Derica LoRA adapter from Tinker and record its size and SHA256.

The archive goes to artifacts/ (gitignored). runs/adapter.json records the file name, size,
SHA256 and the archive's file list. The signed download URL is never printed or saved.
Run: uv run python scripts/export_adapter.py [train_run_v2.json]
"""

import hashlib
import json
import sys
import tarfile
from pathlib import Path

import httpx
import tinker
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

run_file = sys.argv[1] if len(sys.argv) > 1 else "train_run_v2.json"
run = json.loads((ROOT / "runs" / run_file).read_text(encoding="utf-8"))
tinker_path = run["sampler_path"]

rest = tinker.ServiceClient().create_rest_client()
url = rest.get_checkpoint_archive_url_from_tinker_path(tinker_path).result()
url = getattr(url, "url", url)

out_dir = ROOT / "artifacts"
out_dir.mkdir(exist_ok=True)
target = out_dir / (tinker_path.rsplit("/", 1)[-1] + ".tar")
digest = hashlib.sha256()
with httpx.stream("GET", url, timeout=300, follow_redirects=True) as response:
    response.raise_for_status()
    with target.open("wb") as handle:
        for chunk in response.iter_bytes(1 << 20):
            handle.write(chunk)
            digest.update(chunk)

with tarfile.open(target) as archive:
    members = [{"name": m.name, "bytes": m.size} for m in archive.getmembers() if m.isfile()]

record = {
    "base_model": run["base_model"],
    "rank": run["rank"],
    "tinker_path": tinker_path,
    "file": target.name,
    "bytes": target.stat().st_size,
    "sha256": digest.hexdigest(),
    "contents": members,
}
(ROOT / "runs" / "adapter.json").write_text(json.dumps(record, indent=1), encoding="utf-8")
print(json.dumps({k: v for k, v in record.items() if k != "tinker_path"}, indent=1))
