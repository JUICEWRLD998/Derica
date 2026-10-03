# Claims

Every claim made in the README or the post maps to a command that reproduces it. Status is VERIFIED (the command was run and the output matched) or UNVERIFIED (not yet run).

| Claim | Status | Command |
|---|---|---|
| The units table holds Amina's own weights for rice, beans, garri and groundnut (derica, mudu, paint, 50kg bag) | VERIFIED | `uv run pytest tests/test_units.py` |
| A 50kg rice bag at ₦78,000 costs ₦2,496 per mudu | VERIFIED | `uv run pytest tests/test_repricer.py` |
| A rise to ₦82,000 moves her ₦2,900 rice mudu to ₦3,050 at the same markup | VERIFIED | `uv run pytest tests/test_repricer.py` |
| Her 18 real messages are labelled: 11 prices, 7 non-prices | VERIFIED | `uv run pytest tests/test_gold_labels.py` |
| The strict rules parser reads 0 of the 11 price messages | UNVERIFIED as a test (a regex baseline written later reads all 18) | One-off run on 2026-10-03; becomes a row of `derica/eval.py` |
| RETRACTED: "A fine-tuned model beats the rules baseline and the closed baseline on real messages". Measured result: on Amina's 18 real messages the v2 LoRA scores 18, the same as rules and the prompted models, so that set cannot separate them | VERIFIED (the retraction) | `PYTHONPATH=. uv run python scripts/eval.py` (needs both API keys), output in `runs/eval.json` |
| On 39 hand-written messy messages (synthetic, frozen before scoring) the LoRA v2 scores 35, rules 28, Gemini 2.5 Flash-Lite 38, gpt-oss-120b 39. The fine-tune beats rules and does not beat the prompted large models | VERIFIED, one run; gpt-oss moved by 2 between runs at temperature 0 | same command, `runs/eval.json`, set `hard hand-written (39)` |
| On a second 29-message hand-written set the LoRA v2 scores 29, gpt-oss 28, Gemini 27, rules 18. Not independent evidence: the generator and this set use the same list of other goods | VERIFIED, with that caveat | same command, set `hard2 hand-written (29)` |
| The frozen test files cannot change without a test failing | VERIFIED | `uv run pytest tests/test_frozen.py` |
| A model reading of 15,000,000 naira for a 50 kg bag is refused, not shown | VERIFIED | `uv run pytest tests/test_readers.py` |
| When the model is down or invalid, the page still answers with the rules and says so | VERIFIED | `uv run pytest tests/test_readers.py tests/test_server.py` |
| The price card is a 1080 x 1920 PNG and the same input gives the same bytes | VERIFIED | `uv run pytest tests/test_card.py` |
| Every text and border colour pair in both themes meets WCAG AA (3:1 for borders and focus), and the check fails on a planted bad pair | VERIFIED | `uv run python scripts/contrast.py` and `uv run pytest tests/test_tokens.py` |
| The page has no horizontal clipping from 320 to 1920 px, and the probe detects a planted wide element | VERIFIED once, by a headless Chrome drive on 2026-10-04; the driver is not in the repo | not reproducible from the repo yet |
| Live URL works from a phone | UNVERIFIED, not deployed | `render.yaml` is ready; deploy needs the owner's Render account and `TINKER_API_KEY` |
| The model never sets a price | VERIFIED by construction | `derica/repricer.py` imports no model code |
