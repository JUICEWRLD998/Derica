# Claims

Every claim made in the README or the post maps to a command that reproduces it. Status is VERIFIED (the command was run and the output matched) or UNVERIFIED (not yet run).

| Claim | Status | Command |
|---|---|---|
| The units table holds Amina's own weights for rice, beans, garri and groundnut (derica, mudu, paint, 50kg bag) | VERIFIED | `uv run pytest tests/test_units.py` |
| A 50kg rice bag at ₦78,000 costs ₦2,496 per mudu | VERIFIED | `uv run pytest tests/test_repricer.py` |
| A rise to ₦82,000 moves her ₦2,900 rice mudu to ₦3,050 at the same markup | VERIFIED | `uv run pytest tests/test_repricer.py` |
| Her 18 real messages are labelled: 11 prices, 7 non-prices | VERIFIED | `uv run pytest tests/test_gold_labels.py` |
| The strict rules parser reads 0 of the 11 price messages | UNVERIFIED as a test | One-off run on 2026-10-03; becomes a row of `derica/eval.py` |
| A fine-tuned model beats the rules baseline and the closed baseline on real messages | UNVERIFIED | Not run yet |
| The model never sets a price | VERIFIED by construction | `derica/repricer.py` imports no model code |
