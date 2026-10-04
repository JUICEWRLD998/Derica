# Derica

**Live: https://derica.onrender.com/**

Derica helps a market trader fix her selling prices the moment her supplier's price changes.

Built for the DEV Hacktoberfest Weekend Challenge, "Build for a Friend".

## The problem

My friend Amina sells rice, beans, garri and groundnut in a Nigerian market. She buys by the 50kg bag. She sells by the derica, the mudu and the paint (three local tins of different sizes).

When the supplier raises the bag price, Amina has to work out a new price for every tin. That is slow maths done in her head, so her tin prices usually change later than they should. Every sale in between earns her less than she planned.

The supplier's news arrives as a WhatsApp message, for example "Rice 50kg now 78k" or "Beans no dey cheap again, 92k now".

## What Derica does

1. **You paste the supplier's message.** Plain English or Nigerian Pidgin both work.
2. **Derica reads it.** It picks out the item, the size and the price, and shows you what it understood.
3. **Derica works out new prices.** Using the weight of each of her tins and the price she charges today, it finds the new price per tin that keeps her profit the same. Prices round up to the next ₦50, so rounding never costs her money.
4. **You get a price card.** One tap makes a picture of the new prices, ready to share on WhatsApp.

Example: a 50kg bag of rice goes from ₦78,000 to ₦82,000. Her ₦2,900 mudu becomes ₦3,050, with the same profit as before.

## Why you can trust the numbers

The AI only reads the message. **It never sets a price.** All price maths is ordinary code that anyone can check.

Two more safety checks:

- If the AI reads something that makes no sense (for example ₦15,000,000 for a bag of rice), Derica refuses to show it and says why.
- If the AI is down or gives a bad answer, a simple set of rules reads the message instead, and the page says which one answered.

Amina's stall details are saved only in her own browser. There are no accounts and nothing is stored on a server.

## What I used

| Part | What it is |
|---|---|
| Reading messages | A small AI model, Qwen3.5-4B, which I trained further (fine-tuned) on Tinker with about 3,500 practice messages I generated. Training took about 19 minutes. |
| Backup reader | A hand-written set of rules for price messages. |
| Price maths | Plain Python using exact fractions, so there are no rounding surprises. |
| Server | Python with FastAPI. |
| Page | Plain HTML, CSS and JavaScript. No framework. |
| Price card | A picture drawn by Python (Pillow). |
| Hosting | Render. |
| Fonts | Big Shoulders Stencil and Atkinson Hyperlegible (both free to use). |

## How well does it read messages?

I tested on message sets I locked before testing. Score is the number read exactly right.

| Reader | Amina's real messages (18) | Hand-written hard set (39) | Second hard set (29) |
|---|---|---|---|
| Rules only | 18 | 28 | 18 |
| **Derica model (the one in the app)** | 18 | 35 | 29 |
| gpt-oss-120b, a much larger model, given detailed instructions | 18 | 39 | 28 |
| Gemini 2.5 Flash-Lite, given detailed instructions | 17 | 38 | 27 |

What this shows, and what it does not:

- Derica's small model reads messy messages much better than rules alone.
- It does **not** beat the big models. It matches them to within a few messages.
- What it does have is size. It needs a prompt about a sixth the length, so each reading costs about $0.00004 (roughly 24,000 readings per dollar).
- Amina's 18 real messages are too few to tell the readers apart. The second hard set is not fully independent: I used the same list of "other goods" to build it and the training data.

## Honest limits

- It covers four items only: rice, beans, garri and groundnut.
- A bag means a 50kg bag.
- The tin sizes and prices come from one seller, Amina. The "sample stall" button fills in made-up numbers and says so.
- The live site runs on a free Render plan, so the first visit after a quiet period can take about a minute to wake up.
- The 18 real messages come from one person. The other test messages are ones I wrote.

## Run it yourself

You need Python 3.12 and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/JUICEWRLD998/Derica.git
cd Derica
uv sync
uv run pytest                                  # run the tests
export TINKER_API_KEY=your_key_here            # optional, see below
uv run uvicorn derica.server:app               # open http://127.0.0.1:8000
```

Without a Tinker key the page still works. The rules reader answers alone and the page tells you so.

To repeat the comparison table: `PYTHONPATH=. uv run python scripts/eval.py` (needs a Tinker key and an OpenRouter key). Results are saved in `runs/eval.json`.

## Where things are

| Path | What is in it |
|---|---|
| `derica/server.py` | The web service |
| `derica/readers.py` | Model first, rules as backup, plus the sanity check |
| `derica/stall.py`, `derica/repricer.py` | The price maths |
| `derica/card.py` | The price card picture |
| `derica/static/` | The page |
| `data/real/` | Amina's 18 real messages |
| `data/frozen/` | The test sets, locked before testing |
| `scripts/` | Training, testing and cost scripts |
| `runs/` | Saved results: scores, training cost, cost per reading |

 MIT licence.
