"""Tinker billing for this project, summed from the account's own usage events.

Writes runs/billing.json: totals by event type, and the training and sampling cost with
token counts. Uses Tinker's estimated_cost_usd as reported; nothing is computed from list prices.
Run: uv run python scripts/billing_report.py
"""

import json
from collections import defaultdict
from datetime import date
from pathlib import Path

import tinker
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

rest = tinker.ServiceClient().create_rest_client()
response = rest.get_billing_usage(starting_on=date(2026, 10, 1), ending_before=date(2026, 10, 7)).result()

totals = defaultdict(lambda: {"events": 0, "tokens": 0, "usd": 0.0})
training = []
for event in response.data:
    kind = event.event_info.type + ("_cached" if getattr(event.event_info, "cached", False) else "")
    row = totals[kind]
    row["events"] += 1
    row["tokens"] += event.event_info.token_count if hasattr(event.event_info, "token_count") else 0
    row["usd"] += event.estimated_cost_usd or 0.0
    if event.event_info.type == "training":
        training.append({"bucket_start": event.bucket_start.isoformat(), "tokens": event.event_info.token_count,
                         "usd": round(event.estimated_cost_usd, 4), "rate_per_million": event.effective_rate_usd_per_million_tokens})

summary = {
    "window": "2026-10-01 to 2026-10-06",
    "by_type": {k: {**v, "usd": round(v["usd"], 4)} for k, v in sorted(totals.items())},
    "total_usd": round(sum(v["usd"] for v in totals.values()), 4),
    "training_events": sorted(training, key=lambda t: t["bucket_start"]),
}
(ROOT / "runs" / "billing.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
print(json.dumps({k: v for k, v in summary.items() if k != "training_events"}, indent=1))
print("training events:", len(training))
