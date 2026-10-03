# Decisions

Newest first. Each entry carries what was measured or learned, the alternative that was rejected, and where to look.

## 2026-10-03: eval result. The fine-tune does not beat a well-prompted model on accuracy

`scripts/eval.py`, `runs/eval.json`. Exact-match on the full parse (or null). Frozen real set (Amina, 18), supplied synthetic set (43), fresh generated set (300, seed 99, no overlap with training).

| System | real 18 | supplied 43 | fresh 300 |
|---|---|---|---|
| Rules baseline (fitted to the real 18) | 18 | 43 | 248 |
| Derica LoRA (Qwen3.5-4B, 3 epochs, 1,500 synthetic examples) | 17 | 42 | 300 |
| gpt-oss-120b, rules and 10 examples in the prompt | 18 | 43 | 300 |
| Gemini 2.5 Flash-Lite, rules and 10 examples in the prompt | 18 | 43 | 299 |
| Qwen3.5-4B base, rules and 10 examples, raw prompt | 1 | 1 | 28 |

- First run was unfair: the comparison models were not told Amina's conventions and lost on that. I gave them a full prompt and reran. Two of my first few-shot examples were copies of test messages. I replaced them and added a test (`test_no_few_shot_example_is_a_frozen_test_message`).
- Result: with the conventions in the prompt, gpt-oss-120b and Gemini Flash-Lite match or beat the fine-tune. The 300/300 on the fresh set is the same generator that made the training data, so it shows the model learned the generator's styles, not that it generalises.
- Qwen3.5-4B base scores 1/18 because it often starts with `<think>` or a bare number under a raw prompt. That is a harness limit for a thinking model, not a capability measure, and I did not tune it further.
- The fine-tune's one real miss: `Rice na 78k for the 50kg bag` came back as unit `bag`. The training generator never wrote "for the 50kg bag". I did not add that phrasing to training, because that would be tuning to a test message.
- What the fine-tune still has: a ~264-character prompt against ~1544 characters, and a small model whose weights are ours. Median latency is network-bound and about equal (2.2 s vs 0.8-2.1 s), so no latency claim.
- Sample size caveat: 18 real messages. One miss is 5.6 points.

## 2026-10-03: WFP markup dropped as evidence

Re-ran the WFP Nigeria retail-over-wholesale markup with unit cleaning to naira per kg and a planted control (`derica/wfp.py`, `scripts/wfp_report.py`; the control recovers a planted 10% markup exactly). The real numbers are not usable. Rice (local) shows negative markups for 2018-2023 (-0.8% to -17.9%), gari 33-64%, groundnuts 5-12%. Retail and wholesale rows are different product forms or markets, so the ratio does not mean a seller's markup. The earlier 5-9% figure came from a method without unit cleaning and is retracted.
- The post will not cite WFP for markup. Amina's own scale readings and prices are the only markup evidence, and they are one seller.
- Where: `derica/wfp.py`, `tests/test_wfp.py`, `scripts/wfp_report.py`. The csv itself is gitignored.

## 2026-10-03: synthetic training data, generated and labelled as such

`derica/synth.py` generates WhatsApp-style price messages for training (seeded, deduplicated, `source: synthetic_generated`). `data/synthetic/train.jsonl` holds 1,500 of them (seed 2026). It excludes every text in the real set and the supplied trader set, and `tests/test_synth.py` checks that.
- I did not write messages in Amina's voice and call them hers. The test set stays real (her 18 plus anything she collects) and the post will say how small it is.
- The generator includes shapes her chats did not show: an old and a new price in one message, `Rice 71k per bag`, `{item} {unit} na {price}`, the item left out. The rules baseline reads 81.7% of the 1,500. That gap is a property of shapes I chose to add, so it is not evidence that a model beats rules on her real chats.
- Rejected: generating "test" messages tuned so the model wins.
- Where: `derica/synth.py`, `data/synthetic/train.jsonl`, `tests/test_synth.py`.

## 2026-10-03: the three "trader" message sets are synthetic, and the baseline reads all of them

Three sets of 15 messages arrived labelled "Trader 1/2/3", with a note that they are synthetic examples with fictional prices created for testing. They are stored in `data/synthetic/trader_messages.jsonl` with `source: synthetic_supplied_for_testing`, apart from `data/real/`. They are not real traders and must never be described as such in the post.
- Labels follow Amina's rules (bare bag-sized price is a 50 kg bag, bag price is a cost). Two messages (`Garri 2,100`, `Groundnut 3,800`) have no unit and no topic, so they are marked ambiguous and excluded from scoring until Amina says what she would read.
- The rules baseline was frozen before these arrived. It reads 43 of 43 scored messages correctly (27 prices, 16 non-prices).
- Consequence: these messages have the same shape as Amina's, so a regex already solves them. They cannot show a model beating the baseline. A fine-tune needs harder messages (several numbers, mixed units, odd spelling, a price in a sentence) or the honest result is that rules are enough for this message style.
- Where: `data/synthetic/trader_messages.jsonl`, `tests/test_trader_messages.py`.

## 2026-10-03: the messy-message rules baseline reads 18 of 18, and that proves little

`derica/rules_baseline.py` takes a message plus an optional `context_item` and returns a `PriceEvent` or `None`. It reads all 18 of Amina's messages correctly (11 prices, 7 non-prices). I wrote it after reading those same 18 messages, so the score is fitted to them and says nothing about messages it has not seen.
- Consequence: the eval cannot use these 18 as the test set. The frozen test set must be messages collected after this baseline was written (other traders via Amina), and the baseline must not be edited after that set is frozen.
- Rejected: reporting 18 of 18 as a result, or tuning the baseline until a model looks better against it.
- Where: `derica/rules_baseline.py`, `tests/test_rules_baseline.py` (the gold-set test was added after the code passed, as a pin, not as a first failing test).

## 2026-10-03: Entire installed, session push off

Entire CLI 0.11.3 installed (official installer, checksum verified) and enabled for Claude Code in this repo with `--local --skip-push-sessions`. Checkpoints are captured locally. Session logs are not pushed to the public repo yet, because a transcript can contain anything that appeared in a session.
- Decision still open: when to turn session push on for the Entire category, after the keys have been rotated and the logs checked.
- Where: `.entire/settings.local.json` (ignored).

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

## 2026-10-03: hard set of 39 hand-written messages (synthetic, frozen before scoring)

The 18 real messages are too few, and the fine-tune's 300/300 comes from the generator that made its training data. I wrote 39 harder messages by hand: number words ("seventy eight thousand"), `N` and `₦` prefixes, a `#` naira sign, typos in the item name (`Bean`, `Gari`), a delivery fee beside the price, a unit buried in the sentence, and two out-of-scope items (`groundnut oil`, `Yam`). They are synthetic: I wrote them, Amina did not. Gold follows her stated conventions. The file was hashed and frozen before any system ran on it (`data/frozen/hard_test.jsonl`, `scripts/build_hard_set.py`).

Result, exact match out of 39:

| System | Score |
|---|---|
| Rules baseline | 28 |
| Derica LoRA (Qwen3.5-4B) | 35 |
| Gemini 2.5 Flash-Lite, rules and examples in the prompt | 36 |
| gpt-oss-120b, rules and examples in the prompt | 37 |
| Qwen3.5-4B, same prompt, no fine-tune | 3 (36 invalid replies, it starts with `<think>`) |

- The fine-tune beats the rules by 7 messages and trails the 120B model by 2. It does not beat the prompted large models. This keeps the earlier finding.
- The LoRA's four misses: `Rice 25 kg bag now 41k` came back as unit `bag` (the same slip as the one real miss), `groundnut oil` and `Yam` were read as grain at 50 kg (it was never trained to refuse an item outside the four), and the 3k delivery fee was added to the price (81,000).
- Two things were fixed after seeing the scores, and both are product fixes, not tuning on the answer: (1) the rules baseline crashed on `N82,000` with a `ValueError`; it now returns `None`. (2) `normalize_item` did not map `gari` to `garri` or `bean` to `beans`, so a correct model reply was scored wrong; it does now. The second fix moved gpt-oss from 36 to 37 and Gemini from 35 to 36. The LoRA and rules scores did not change.
- Not done: the training data was not changed to cover these messages. Doing that and re-scoring on the same set would measure memory, not skill.
