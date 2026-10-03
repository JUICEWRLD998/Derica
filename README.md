# Derica

Work in progress for the DEV Hacktoberfest Weekend Challenge, "Build for a Friend".

A friend of mine sells grains and flour in a Nigerian market. She buys by the bag and sells by the derica, mudu and paint. When the bag price moves, her per-measure price usually moves later than it should.

Derica reads a price message the way she types it, checks it against her own measures, and works out the new price per measure with plain code. A small open model proposes the parse. It never sets a price.

Status vocabulary used in this repo: LIVE / NEXT / NOT LIVE.

| Piece | Status |
|---|---|
| Money parsing, units table, schema, repricer (tested) | LIVE |
| Strict rules parser (tidy format only) | LIVE as a library |
| Rules baseline for messy WhatsApp messages (fitted to the first 18, not yet scored on unseen messages) | LIVE as a library |
| Tinker fine-tune (Qwen3.5-4B, LoRA) and the five-system eval, results in `DECISIONS.md` and `runs/eval.json` | LIVE |
| Web page, `/parse`, `/reprice`, price card PNG, run locally with `uv run uvicorn derica.server:app` | LIVE locally |
| Public URL | NOT LIVE |

The full README (thesis, evidence, how to verify) is written before submission.

Started during the challenge window (2026-10-02 02:00 UTC to 2026-10-05 06:59 UTC).
