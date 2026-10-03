# Decisions

Newest first. Each entry carries what was measured or learned, the alternative that was rejected, and where to look.

## 2026-10-03: Tinker and OpenRouter access verified

Ran `scripts/access_spike.py` with the real keys. Both calls worked.
- Tinker: `tinker.ServiceClient()` reads `TINKER_API_KEY` from the environment (confirmed in the SDK docs and by the live call). `get_server_capabilities()` returned 31 models, including `Qwen/Qwen3.5-4B`, `Qwen/Qwen3.5-9B` and `openai/gpt-oss-120b`.
- OpenRouter: key accepted. Exact IDs for the comparison rows: `openai/gpt-oss-120b`, `google/gemini-2.5-flash-lite`, `google/gemini-2.5-flash`. A one-word chat call to `google/gemini-2.5-flash-lite` returned `ok`.
- Nothing was trained yet, so no training cost is recorded.
- Where: `scripts/access_spike.py`.

## 2026-10-03: conversation context is part of the input

Amina (the friend, first name used with permission) says most WhatsApp price messages leave the item out when both people already know it, and a bare bag-sized price such as `92k` means a 50kg bag. So `I fit give you 2,900 mudu` is rice because rice was the topic, and with no topic she asks first.
- Relabelled messages 8 and 9 from "incomplete" to prices. Message 9 carries `context_item: rice`.
- Rejected: treating them as unparseable. That would have scored a model as "correct" for refusing something the seller reads without effort.
- Where: `data/real/friend_messages.jsonl`, `tests/test_gold_labels.py`.

## 2026-10-03: the strict rules parser reads 0 of 9 messy price messages

The first parser was built on the tidy list Amina first sent (`Rice — ₦2,500 mudu`). Run against her 18 real chat messages it accepted none of the 9 prices that were labelled at the time, and rejected the 9 non-prices correctly (9 of 18 overall). Two of those messages have since been relabelled as prices (see the entry above), which makes the strict parser 0 of 11.
- A better regex baseline will be written before the eval. It will be written after seeing these messages, so it is an optimistic baseline, and the post will say so.
- Where: `derica/rules_parser.py`, `data/real/friend_messages.jsonl`.

## 2026-10-03: `side` removed from the schema

Whether a bag price is "buy" or "sell" is rarely stated and Amina says she uses the same figure for both. The unit already carries the role: kg or bag is a cost, derica, mudu or paint is a selling price.
- Rejected: keeping `side` and asking the model to guess it, which would score arbitrary labels.
- Where: `derica/schema.py` (`PriceEvent.is_cost`), `tests/test_schema.py`.

## 2026-10-03: exact fractions in the repricer

All cost and markup arithmetic uses `Fraction`. The only rounding is the one the seller sees, up to her naira step (default 50), so rounding never lowers her margin.
- Rejected: floats, which can land a price one step low.
- Where: `derica/repricer.py`, `tests/test_repricer.py`.
