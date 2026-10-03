"""The Derica web service: /parse, /reprice, /card.png, /health and the one-page UI.

The model proposes a reading, the schema and plausibility checks decide whether it is
shown, and plain code sets every price. Run: uv run uvicorn derica.server:app
"""

import time
from collections import defaultdict, deque
from pathlib import Path
import threading
from contextlib import asynccontextmanager
from threading import Lock

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from derica.card import render_card
from derica.readers import read_message
from derica.schema import PriceEvent
from derica.stall import reprice
from derica.tinker_model import TinkerModel

STATIC = Path(__file__).parent / "static"
_UNSET = object()


class RateLimiter:
    """At most `allowance` calls per `window` seconds for each client."""

    def __init__(self, allowance: int, window: float, clock=time.monotonic):
        self.allowance, self.window, self.clock = allowance, window, clock
        self._calls: dict[str, deque] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, who: str) -> bool:
        now = self.clock()
        with self._lock:
            calls = self._calls[who]
            while calls and now - calls[0] > self.window:
                calls.popleft()
            if len(calls) >= self.allowance:
                return False
            calls.append(now)
            return True


class ParseIn(BaseModel):
    text: str
    context_item: str | None = None


class EventIn(BaseModel):
    item: str
    qty: float
    unit: str
    price_ngn: int


class MeasureIn(BaseModel):
    grams: int
    old_price: int


class RepriceIn(BaseModel):
    item: str
    old_cost: EventIn
    new_cost: EventIn
    measures: dict[str, MeasureIn]
    step: int = 50


class CardItem(BaseModel):
    item: str
    prices: dict[str, int]


class CardIn(BaseModel):
    shop: str
    date: str
    items: list[CardItem]


def _quietly(model, text: str) -> None:
    try:
        model(text, None)
    except Exception:
        pass  # warm-up only; a real request reports its own failure


def _event(raw: EventIn) -> PriceEvent:
    return PriceEvent(raw.item, int(raw.qty) if float(raw.qty).is_integer() else raw.qty, raw.unit, raw.price_ngn)


def create_app(model=_UNSET, limiter: RateLimiter | None = None, warm: bool = False) -> FastAPI:
    reader_model = TinkerModel.from_env() if model is _UNSET else model
    limit = limiter or RateLimiter(30, 60)

    @asynccontextmanager
    async def lifespan(_app):
        # The first sampler call builds the client and tokenizer (about 19 s measured). Do it before a visitor arrives.
        if warm and reader_model is not None:
            threading.Thread(target=_quietly, args=(reader_model, "Rice 50kg 80k"), daemon=True).start()
        yield

    app = FastAPI(title="Derica", docs_url=None, redoc_url=None, lifespan=lifespan)

    def guard(request: Request) -> None:
        forwarded = request.headers.get("x-forwarded-for", "")
        who = forwarded.split(",")[0].strip() or (request.client.host if request.client else "unknown")
        if not limit.allow(who):
            raise HTTPException(429, "Too many messages. Wait a minute and try again.")

    @app.get("/health")
    def health():
        return {"status": "ok", "model": reader_model is not None}

    @app.post("/parse")
    def parse(body: ParseIn, request: Request):
        guard(request)
        try:
            return read_message(body.text, body.context_item, reader_model).to_dict()
        except ValueError as error:
            raise HTTPException(422, str(error)) from error

    @app.post("/reprice")
    def reprice_route(body: RepriceIn, request: Request):
        guard(request)
        try:
            measures = {unit: {"grams": m.grams, "old_price": m.old_price} for unit, m in body.measures.items()}
            return reprice(body.item, _event(body.old_cost), _event(body.new_cost), measures, body.step)
        except ValueError as error:
            raise HTTPException(422, str(error)) from error

    @app.post("/card.png")
    def card(body: CardIn, request: Request):
        guard(request)
        try:
            png = render_card(body.shop, body.date, [i.model_dump() for i in body.items])
        except ValueError as error:
            raise HTTPException(422, str(error)) from error
        return Response(png, media_type="image/png", headers={"Cache-Control": "no-store"})

    @app.get("/")
    def home():
        return FileResponse(STATIC / "index.html")

    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    return app


app = create_app(warm=True)
