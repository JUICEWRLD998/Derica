"""LoRA fine-tune of Qwen3.5-4B on data/tinker/train.jsonl through Tinker.

Plain prompt + completion text, loss on the completion only. Writes the sampler
path and loss curve to runs/train_run.json.
Run: uv run python scripts/train_tinker.py
"""

import json
import random
import time
from pathlib import Path

import numpy as np
import tinker
from dotenv import load_dotenv
from tinker import types

load_dotenv()
ROOT = Path(__file__).resolve().parents[1]
BASE_MODEL = "Qwen/Qwen3.5-4B"
RANK, EPOCHS, BATCH, LR = 16, 3, 32, 2e-4

rows = [json.loads(line) for line in (ROOT / "data" / "tinker" / "train.jsonl").read_text(encoding="utf-8").splitlines()]
service = tinker.ServiceClient()
client = service.create_lora_training_client(base_model=BASE_MODEL, rank=RANK)
tokenizer = client.get_tokenizer()


def datum(row):
    prompt = tokenizer.encode(row["prompt"] + " ", add_special_tokens=False)
    completion = tokenizer.encode(row["completion"] + "\n", add_special_tokens=False)
    ids = prompt + completion
    weights = [0.0] * (len(prompt) - 1) + [1.0] * len(completion)
    return types.Datum(
        model_input=types.ModelInput.from_ints(ids[:-1]),
        loss_fn_inputs={
            "target_tokens": types.TensorData.from_numpy(np.array(ids[1:], dtype=np.int64)),
            "weights": types.TensorData.from_numpy(np.array(weights, dtype=np.float32)),
        },
    ), sum(weights)


data = [datum(r) for r in rows]
rng = random.Random(0)
losses, started = [], time.time()
step = 0
for epoch in range(EPOCHS):
    rng.shuffle(data)
    for i in range(0, len(data), BATCH):
        batch = data[i : i + BATCH]
        fwd = client.forward_backward([d for d, _ in batch], loss_fn="cross_entropy")
        opt = client.optim_step(types.AdamParams(learning_rate=LR))
        result = fwd.result()
        opt.result()
        completion_tokens = sum(w for _, w in batch)
        loss = sum(
            float((-out["logprobs"].to_numpy() * d.loss_fn_inputs["weights"].to_numpy()).sum())
            for out, (d, _) in zip(result.loss_fn_outputs, batch)
        ) / completion_tokens
        losses.append(loss)
        step += 1
        if step % 10 == 0 or step == 1:
            print(f"epoch {epoch} step {step} loss/token {loss:.4f} ({time.time() - started:.0f}s)", flush=True)

sampler = client.save_weights_for_sampler(name="derica-v1").result()
(ROOT / "runs" / "train_run.json").write_text(
    json.dumps({"base_model": BASE_MODEL, "rank": RANK, "epochs": EPOCHS, "batch": BATCH, "lr": LR, "examples": len(rows),
                "steps": step, "seconds": round(time.time() - started), "sampler_path": sampler.path, "loss": losses}, indent=1),
    encoding="utf-8",
)
print("sampler path:", sampler.path)
