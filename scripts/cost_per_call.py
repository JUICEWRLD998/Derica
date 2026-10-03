"""Cost of one /parse call on the Derica LoRA, from Tinker's billed rates.

Token counts come from the sampler's own tokenizer over Amina's 18 real messages (prompt, and the
gold JSON as the completion). Rates are the effective USD per token that Tinker billed in
runs/billing.json (sampling_prefill and sampling_sample), not list prices.
Also prices the long few-shot prompt the non-fine-tuned systems need, for comparison.
Run: uv run python scripts/billing_report.py && uv run python scripts/cost_per_call.py
"""

import json
from pathlib import Path

import tinker
from dotenv import load_dotenv

from derica.dataset import build_completion, build_few_shot_prompt, build_prompt

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

billing = json.loads((ROOT / "runs" / "billing.json").read_text(encoding="utf-8"))["by_type"]
prefill_rate = billing["sampling_prefill"]["usd"] / billing["sampling_prefill"]["tokens"]
sample_rate = billing["sampling_sample"]["usd"] / billing["sampling_sample"]["tokens"]

run = json.loads((ROOT / "runs" / "train_run_v2.json").read_text(encoding="utf-8"))
tokenizer = tinker.ServiceClient().create_sampling_client(model_path=run["sampler_path"]).get_tokenizer()
rows = [json.loads(l) for l in (ROOT / "data" / "frozen" / "real_test.jsonl").read_text(encoding="utf-8").splitlines()]


def count(text: str) -> int:
    return len(tokenizer.encode(text, add_special_tokens=False))


tuned_prompt = [count(build_prompt(r["text"], r.get("context_item"))) for r in rows]
few_shot_prompt = [count(build_few_shot_prompt(r["text"], r.get("context_item"))) for r in rows]
completion = [count(build_completion(r) + "\n") for r in rows]
mean = lambda xs: sum(xs) / len(xs)

result = {
    "messages": len(rows),
    "billed_rate_usd_per_million": {"prefill": round(prefill_rate * 1e6, 3), "sample": round(sample_rate * 1e6, 3)},
    "mean_tokens": {"tuned_prompt": round(mean(tuned_prompt), 1), "few_shot_prompt": round(mean(few_shot_prompt), 1), "completion": round(mean(completion), 1)},
    "usd_per_call": {
        "derica_lora": round(mean(tuned_prompt) * prefill_rate + mean(completion) * sample_rate, 7),
        "base_model_with_few_shot_prompt_same_rates": round(mean(few_shot_prompt) * prefill_rate + mean(completion) * sample_rate, 7),
    },
}
result["calls_per_dollar_derica_lora"] = round(1 / result["usd_per_call"]["derica_lora"])
(ROOT / "runs" / "cost_per_call.json").write_text(json.dumps(result, indent=1), encoding="utf-8")
print(json.dumps(result, indent=1))
