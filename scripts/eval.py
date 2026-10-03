"""Score five systems on the frozen test sets plus a fresh synthetic set.

Systems: rules baseline, Qwen3.5-4B with a few-shot prompt, Derica LoRA (both Tinker),
gpt-oss-120b and Gemini 2.5 Flash-Lite (OpenRouter, comparison only).
A reply that is not a valid event or null counts as wrong. Writes runs/eval.json.
"""

import json
import os
import re
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx
import tinker
from dotenv import load_dotenv
from tinker import types

from derica.dataset import build_few_shot_prompt, build_prompt, parse_completion
from derica.rules_baseline import parse_message
from derica.schema import PriceEvent
from derica.synth import generate

load_dotenv()
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
BASE = "Qwen/Qwen3.5-4B"
sampler_path = json.loads((ROOT / "runs" / "train_run.json").read_text(encoding="utf-8"))["sampler_path"]


def read(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


real = read(DATA / "frozen" / "real_test.jsonl")
supplied = read(DATA / "frozen" / "supplied_test.jsonl")
hard = read(DATA / "frozen" / "hard_test.jsonl")
hard2 = read(DATA / "frozen" / "hard2_test.jsonl")
exclude = {r["text"] for r in real + supplied + hard + hard2 + read(DATA / "synthetic" / "train.jsonl")}
fresh = generate(300, seed=99, exclude=exclude)
SETS = {"real (Amina, 18)": real, "supplied synthetic (43)": supplied, "fresh generated (300)": fresh, "hard hand-written (39)": hard, "hard2 hand-written (29)": hard2}

service = tinker.ServiceClient()
zero_shot = service.create_sampling_client(base_model=BASE)
derica = service.create_sampling_client(model_path=sampler_path)
sampler_v2 = json.loads((ROOT / "runs" / "train_run_v2.json").read_text(encoding="utf-8"))["sampler_path"]
derica_v2 = service.create_sampling_client(model_path=sampler_v2)
tokenizer = zero_shot.get_tokenizer() if hasattr(zero_shot, "get_tokenizer") else None
if tokenizer is None:
    tokenizer = service.create_lora_training_client(base_model=BASE, rank=16).get_tokenizer()
PARAMS = types.SamplingParams(max_tokens=80, temperature=0.0, stop=["\n"])


def tinker_system(client, prompt_fn):
    def run(row):
        prompt = types.ModelInput.from_ints(tokenizer.encode(prompt_fn(row["text"], row.get("context_item")) + " ", add_special_tokens=False))
        started = time.time()
        out = client.sample(prompt, 1, PARAMS).result()
        return tokenizer.decode(out.sequences[0].tokens), time.time() - started
    return run


def openrouter_system(model, prompt_fn, extra=None):
    headers = {"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"}

    def run(row):
        body = {"model": model, "temperature": 0, "max_tokens": 600,
                "messages": [{"role": "user", "content": prompt_fn(row["text"], row.get("context_item"))}]}
        body.update(extra or {})
        started = time.time()
        for attempt in range(3):
            resp = httpx.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body, timeout=120)
            if resp.status_code == 200:
                break
            time.sleep(2 * (attempt + 1))
        else:
            return f"HTTP {resp.status_code}", time.time() - started
        content = resp.json()["choices"][0]["message"].get("content") or ""
        return content, time.time() - started
    return run


def rules(row):
    event = parse_message(row["text"], row.get("context_item"))
    return ("null" if event is None else json.dumps(event.__dict__)), 0.0


def clean(text):
    """Strip code fences. An object whose fields are all null means "no price", the same as null."""
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return text
    if isinstance(value, dict) and value and all(v is None for v in value.values()):
        return "null"
    return text


SYSTEMS = {
    "rules baseline": (rules, 1),
    "Qwen3.5-4B + rules and examples in prompt": (tinker_system(zero_shot, build_few_shot_prompt), 8),
    "Derica LoRA (Qwen3.5-4B)": (tinker_system(derica, build_prompt), 8),
    "Derica LoRA v2 (rich data)": (tinker_system(derica_v2, build_prompt), 8),
    "gpt-oss-120b + rules and examples": (openrouter_system("openai/gpt-oss-120b", build_few_shot_prompt, {"reasoning": {"effort": "low"}}), 6),
    "Gemini 2.5 Flash-Lite + rules and examples": (openrouter_system("google/gemini-2.5-flash-lite", build_few_shot_prompt), 6),
}

results = {}
for name, (fn, workers) in SYSTEMS.items():
    results[name] = {}
    for set_name, rows in SETS.items():
        with ThreadPoolExecutor(workers) as pool:
            outputs = list(pool.map(fn, rows))
        correct = invalid = 0
        misses = []
        for row, (text, _) in zip(rows, outputs):
            want = PriceEvent(**row["gold"]) if row["gold"] else None
            try:
                got = parse_completion(clean(text))
            except ValueError:
                got, invalid = "INVALID", invalid + 1
            if got == want:
                correct += 1
            else:
                misses.append({"id": row.get("id"), "text": row["text"], "want": want and want.__dict__, "got": text[:120]})
        latencies = [t for _, t in outputs if t]
        results[name][set_name] = {"n": len(rows), "correct": correct, "invalid": invalid,
                                   "p50_s": round(statistics.median(latencies), 2) if latencies else None, "misses": misses[:25]}
        print(f"{name:44} {set_name:26} {correct}/{len(rows)}  invalid={invalid}", flush=True)

(ROOT / "runs" / "eval.json").write_text(json.dumps(results, indent=1, ensure_ascii=False), encoding="utf-8")
