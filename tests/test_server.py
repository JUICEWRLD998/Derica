from fastapi.testclient import TestClient

from derica.server import RateLimiter, create_app

RICE_REPLY = '{"item":"rice","qty":50,"unit":"kg","price_ngn":78000}'


def client(model=lambda text, ctx: RICE_REPLY, limiter=None):
    return TestClient(create_app(model=model, limiter=limiter or RateLimiter(100, 60)))


def test_health_reports_whether_the_model_is_configured():
    assert client().get("/health").json() == {"status": "ok", "model": True}
    assert TestClient(create_app(model=None, limiter=RateLimiter(5, 60))).get("/health").json() == {"status": "ok", "model": False}


def test_parse_returns_the_event_and_which_reader_answered():
    body = client().post("/parse", json={"text": "Rice 50kg 78k"}).json()
    assert body["event"] == {"item": "rice", "qty": 50, "unit": "kg", "price_ngn": 78000}
    assert body["reader"] == "derica"


def test_parse_falls_back_to_rules_when_the_model_raises_and_says_so():
    def down(text, ctx):
        raise RuntimeError("down")

    body = client(model=down).post("/parse", json={"text": "Rice 50kg now 78k"}).json()
    assert body["reader"] == "rules" and body["event"]["price_ngn"] == 78000 and "rules" in body["note"]


def test_parse_of_a_non_price_is_a_null_event_not_an_error():
    r = client(model=lambda t, c: "null").post("/parse", json={"text": "how much be your rice?"})
    assert r.status_code == 200 and r.json()["event"] is None


def test_parse_refuses_empty_long_and_malformed_input_with_a_plain_message():
    c = client()
    for payload in ({"text": "  "}, {"text": "x" * 500}, {}, {"text": 5}):
        r = c.post("/parse", json=payload)
        assert r.status_code == 422 and r.json()["detail"]


def test_double_submit_of_the_same_message_gives_the_same_answer():
    c = client()
    assert c.post("/parse", json={"text": "Rice 50kg 78k"}).json()["event"] == c.post("/parse", json={"text": "Rice 50kg 78k"}).json()["event"]


def test_the_rate_limiter_answers_429_after_the_allowance():
    c = client(limiter=RateLimiter(2, 60))
    codes = [c.post("/parse", json={"text": "Rice 50kg 78k"}).status_code for _ in range(3)]
    assert codes == [200, 200, 429]


def test_reprice_returns_rows_with_the_loss_per_sale():
    payload = {
        "item": "rice",
        "old_cost": {"item": "rice", "qty": 50, "unit": "kg", "price_ngn": 70000},
        "new_cost": {"item": "rice", "qty": 50, "unit": "kg", "price_ngn": 78000},
        "measures": {"mudu": {"grams": 1600, "old_price": 2800}},
    }
    body = client().post("/reprice", json=payload).json()
    assert body["rows"][0]["new_price"] == 3150 and body["rows"][0]["lost_per_sale"] == 350


def test_reprice_rejects_garbage_with_422():
    r = client().post("/reprice", json={"item": "rice", "old_cost": {}, "new_cost": {}, "measures": {}})
    assert r.status_code == 422


def test_card_endpoint_returns_a_png():
    payload = {"shop": "Amina Grains", "date": "3 Oct 2026", "items": [{"item": "rice", "prices": {"mudu": 3150}}]}
    r = client().post("/card.png", json=payload)
    assert r.status_code == 200 and r.headers["content-type"] == "image/png" and r.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_card_endpoint_rejects_an_empty_board():
    r = client().post("/card.png", json={"shop": "S", "date": "d", "items": []})
    assert r.status_code == 422


def test_the_home_page_is_served():
    r = client().get("/")
    assert r.status_code == 200 and "text/html" in r.headers["content-type"]


def test_the_model_is_warmed_once_at_startup_so_the_first_visitor_is_not_slow():
    import threading

    called = threading.Event()
    with TestClient(create_app(model=lambda t, c: called.set() or "null", limiter=RateLimiter(5, 60), warm=True)):
        assert called.wait(timeout=3)
