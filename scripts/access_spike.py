"""Phase 0 access check. Makes one small call to Tinker and one to OpenRouter.

Prints status and model ids only. Never prints a key.
Run: uv run python scripts/access_spike.py
"""

import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv()


def check_openrouter() -> None:
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        print("openrouter: OPENROUTER_API_KEY is empty")
        return
    headers = {"Authorization": f"Bearer {key}"}
    auth = httpx.get("https://openrouter.ai/api/v1/auth/key", headers=headers, timeout=30)
    print("openrouter key check: HTTP", auth.status_code)
    if auth.status_code == 200:
        data = auth.json().get("data", {})
        print("  limit_remaining:", data.get("limit_remaining"))
    models = httpx.get("https://openrouter.ai/api/v1/models", headers=headers, timeout=60)
    print("openrouter models: HTTP", models.status_code)
    ids = [m["id"] for m in models.json().get("data", [])]
    for needle in ("gpt-oss-120b", "qwen3", "gemini-2.5-flash"):
        print(f"  {needle}:", sorted(i for i in ids if needle in i))
    chat = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json={
            "model": "google/gemini-2.5-flash-lite",
            "messages": [{"role": "user", "content": "Reply with the single word: ok"}],
            "max_tokens": 5,
        },
        timeout=60,
    )
    print("openrouter chat (gemini-2.5-flash-lite): HTTP", chat.status_code)
    if chat.status_code == 200:
        print("  reply:", chat.json()["choices"][0]["message"]["content"].strip())
    else:
        print("  body:", chat.text[:300])


def check_tinker() -> None:
    if not os.environ.get("TINKER_API_KEY"):
        print("tinker: TINKER_API_KEY is empty")
        return
    import tinker

    client = tinker.ServiceClient()
    caps = client.get_server_capabilities()
    models = [m.model_name for m in caps.supported_models]
    print("tinker: capabilities call OK,", len(models), "models")
    for name in models:
        if "Qwen3.5" in name or "gpt-oss" in name:
            print("  ", name)


if __name__ == "__main__":
    for fn in (check_openrouter, check_tinker):
        try:
            fn()
        except Exception as exc:  # report, never hide
            print(f"{fn.__name__} FAILED: {type(exc).__name__}: {str(exc)[:300]}")
            sys.exit(1)
