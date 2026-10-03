"""The live reader: the Derica LoRA served from Tinker's sampler.

Lazy by design: importing this module makes no network call. The first message builds the
sampling client. If TINKER_API_KEY is missing the server runs without a model and the page
says the rules are answering.
"""

import json
import os
import threading
from pathlib import Path

from derica.dataset import build_prompt

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN = ROOT / "runs" / "train_run_v2.json"
TIMEOUT_SECONDS = 25


class TinkerModel:
    def __init__(self, sampler_path: str):
        self.sampler_path = sampler_path
        self._client = None
        self._tokenizer = None
        self._lock = threading.Lock()

    @classmethod
    def from_env(cls) -> "TinkerModel | None":
        if not os.environ.get("TINKER_API_KEY"):
            return None
        path = os.environ.get("DERICA_SAMPLER_PATH") or json.loads(DEFAULT_RUN.read_text(encoding="utf-8"))["sampler_path"]
        return cls(path)

    def _ensure(self):
        with self._lock:
            if self._client is None:
                import tinker

                self._client = tinker.ServiceClient().create_sampling_client(model_path=self.sampler_path)
                self._tokenizer = self._client.get_tokenizer()

    def __call__(self, text: str, context_item: str | None) -> str:
        from tinker import types

        self._ensure()
        prompt = build_prompt(text, context_item) + " "
        model_input = types.ModelInput.from_ints(self._tokenizer.encode(prompt, add_special_tokens=False))
        params = types.SamplingParams(max_tokens=80, temperature=0.0, stop=["\n"])
        out = self._client.sample(model_input, 1, params).result(timeout=TIMEOUT_SECONDS)
        return self._tokenizer.decode(out.sequences[0].tokens)
