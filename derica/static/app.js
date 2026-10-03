"use strict";

// Derica page. Reads a message through /parse, reprices through /reprice, and builds the
// card through /card.png. Every price shown comes from the server's plain-code repricer.

const MEASURES = ["derica", "mudu", "paint"];
const ITEMS = ["rice", "beans", "garri", "groundnut"];
const STORE_KEY = "derica.book.v1";
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

// Made-up numbers, offered only through the labelled "sample stall" button.
const SAMPLE = {
  rice: { cost: 70000, derica: [800, 1400], mudu: [1600, 2800], paint: [7000, 12250] },
  beans: { cost: 85000, derica: [750, 1600], mudu: [1500, 3200], paint: [6500, 13800] },
  garri: { cost: 52000, derica: [550, 700], mudu: [1100, 1450], paint: [4500, 5850] },
  groundnut: { cost: 100000, derica: [650, 1650], mudu: [1300, 3250], paint: [5500, 13750] },
};

const $ = (id) => document.getElementById(id);
const state = { shop: "", book: {}, picked: "rice", boards: [], busy: false };

function load() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORE_KEY) || "{}");
    state.shop = typeof saved.shop === "string" ? saved.shop : "";
    state.book = saved.book && typeof saved.book === "object" ? saved.book : {};
  } catch (error) {
    state.shop = "";
    state.book = {};
  }
}

function save() {
  try {
    localStorage.setItem(STORE_KEY, JSON.stringify({ shop: state.shop, book: state.book }));
  } catch (error) {
    /* private window or blocked storage: the page works without saving */
  }
}

const naira = (n) => "₦" + Number(n).toLocaleString("en-NG");
const whole = (text) => {
  const digits = String(text).replace(/[^\d]/g, "");
  return digits ? parseInt(digits, 10) : null;
};

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function money(n) {
  return el("span", "money", naira(n));
}

/* ---------- stall book ---------- */

function bookFor(item) {
  if (!state.book[item]) state.book[item] = { cost: null, measures: {} };
  return state.book[item];
}

function renderBook() {
  const host = $("book-form");
  host.replaceChildren();

  const picker = el("fieldset", "picker");
  picker.appendChild(el("legend", "", "Item"));
  ITEMS.forEach((item) => {
    const label = document.createElement("label");
    const input = document.createElement("input");
    input.type = "radio";
    input.name = "picked";
    input.value = item;
    input.checked = item === state.picked;
    input.addEventListener("change", () => {
      state.picked = item;
      renderBook();
renderBoards();
    });
    label.append(input, el("span", "", item[0].toUpperCase() + item.slice(1)));
    picker.appendChild(label);
  });
  host.appendChild(picker);

  const entry = bookFor(state.picked);
  const cost = el("div", "field");
  const costLabel = el("label", "", `What you last paid for a 50 kg bag of ${state.picked} (₦)`);
  costLabel.htmlFor = "book-cost";
  const costInput = document.createElement("input");
  costInput.type = "text";
  costInput.id = "book-cost";
  costInput.inputMode = "numeric";
  costInput.autocomplete = "off";
  costInput.value = entry.cost ? String(entry.cost) : "";
  costInput.addEventListener("input", () => {
    entry.cost = whole(costInput.value);
    save();
  });
  cost.append(costLabel, costInput);
  host.appendChild(cost);

  const grid = el("div", "measure-grid");
  grid.append(el("span", "head", "Measure"), el("span", "head", "Weight in grams"), el("span", "head", "Price now (₦)"));
  MEASURES.forEach((unit) => {
    const spec = entry.measures[unit] || (entry.measures[unit] = { grams: null, price: null });
    grid.appendChild(el("span", "unit", unit));
    [["grams", "Weight in grams"], ["price", "Price now"]].forEach(([key, name]) => {
      const input = document.createElement("input");
      input.type = "text";
      input.inputMode = "numeric";
      input.autocomplete = "off";
      input.setAttribute("aria-label", `${name} for one ${unit} of ${state.picked}`);
      input.value = spec[key] ? String(spec[key]) : "";
      input.addEventListener("input", () => {
        spec[key] = whole(input.value);
        save();
      });
      grid.appendChild(input);
    });
  });
  host.appendChild(grid);
}

function fillSample() {
  ITEMS.forEach((item) => {
    const s = SAMPLE[item];
    state.book[item] = {
      cost: s.cost,
      measures: Object.fromEntries(MEASURES.map((u) => [u, { grams: s[u][0], price: s[u][1] }])),
    };
  });
  if (!state.shop) {
    state.shop = "Sample stall";
    $("shop").value = state.shop;
  }
  $("sample-note").hidden = false;
  save();
  renderBook();
}

function tryExample() {
  fillSample();
  $("message").value = "abeg rice na seventy eight thousand for 50kg";
  $("count").textContent = String($("message").value.length);
  $("context").value = "";
  $("read-form").requestSubmit();
}

/* ---------- reading ---------- */

function describe(event) {
  const unit = event.unit === "kg" ? `${event.qty} kg` : `${event.qty} ${event.unit}`;
  return [event.item, unit];
}

function eventLine(event) {
  if (!event) return "no price found";
  const [item, unit] = describe(event);
  return `${item}, ${unit}, ${naira(event.price_ngn)}`;
}

function renderReading(result) {
  const host = $("reading");
  host.replaceChildren();
  const verdict = el("p", result.event ? "verdict" : "verdict none");
  if (result.event) {
    const [item, unit] = describe(result.event);
    verdict.append(`Read as ${item}, ${unit}, `, money(result.event.price_ngn), ".");
  } else {
    verdict.textContent = result.note ? "No safe reading. Nothing changed." : "Not a price. Nothing changed.";
  }
  host.appendChild(verdict);

  const seconds = (result.readers.find((r) => r.name === "Derica model") || {}).ms;
  if (result.reader === "derica") {
    host.appendChild(el("p", "by", `Read by the Derica model in ${(seconds / 1000).toFixed(1)} s.`));
  } else {
    host.appendChild(el("p", "by fallback", "The model gave no usable answer, so the rules read this message."));
  }
  if (result.note && result.reader === "derica") host.appendChild(el("p", "by fallback", result.note));

  const details = el("details", "readers");
  details.appendChild(el("summary", "", "How each reader answered"));
  const list = el("ul");
  result.readers.forEach((reader) => {
    const row = el("li");
    const outcome =
      reader.status === "ok" ? eventLine(reader.event) : reader.status === "invalid" ? "gave an answer that was not valid" : "did not answer";
    row.append(el("span", "", reader.name), el("span", "", outcome));
    list.appendChild(row);
  });
  details.appendChild(list);
  host.appendChild(details);
}

function showNote(text) {
  $("reading").appendChild(el("p", "by fallback", text));
}

async function call(path, body) {
  let response;
  try {
    response = await fetch(path, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
  } catch (error) {
    throw new Error("Could not reach the server. Check your connection and try again.");
  }
  if (!response.ok) {
    let detail = "Something went wrong. Try again.";
    try {
      const data = await response.json();
      if (typeof data.detail === "string") detail = data.detail;
      else if (Array.isArray(data.detail) && data.detail.length) detail = "That input was not accepted.";
    } catch (error) {
      /* keep the generic message */
    }
    throw new Error(detail);
  }
  return response;
}

function busy(button, on, label) {
  button.setAttribute("aria-busy", on ? "true" : "false");
  button.disabled = on;
  if (label) button.textContent = label;
}

async function onRead(event) {
  event.preventDefault();
  if (state.busy) return;
  const text = $("message").value.trim();
  const error = $("message-error");
  error.textContent = "";
  $("message").removeAttribute("aria-invalid");
  if (!text) {
    error.textContent = "Paste a message first.";
    $("message").setAttribute("aria-invalid", "true");
    $("message").focus();
    return;
  }
  state.busy = true;
  const button = $("read-button");
  button.removeAttribute("data-state");
  busy(button, true, "Reading…");
  try {
    const context = $("context").value || null;
    const result = await (await call("/parse", { text, context_item: context })).json();
    renderReading(result);
    button.dataset.state = "success";
    if (result.event) await maybeReprice(result.event);
  } catch (failure) {
    button.dataset.state = "error";
    error.textContent = failure.message;
  } finally {
    busy(button, false, "Read message");
    state.busy = false;
  }
}

async function maybeReprice(event) {
  if (!["kg", "bag"].includes(event.unit)) {
    showNote(`That is a selling price for one ${event.unit}, not a bag price. Paste the supplier's bag price to work out new prices.`);
    return;
  }
  const entry = state.book[event.item];
  const measures = {};
  if (entry) {
    MEASURES.forEach((unit) => {
      const spec = entry.measures[unit];
      if (spec && spec.grams && spec.price) measures[unit] = { grams: spec.grams, old_price: spec.price };
    });
  }
  if (!entry || !entry.cost || !Object.keys(measures).length) {
    state.picked = event.item;
    renderBook();
    $("stall-book").open = true;
    showNote(`Fill in your stall for ${event.item} to see the new prices.`);
    return;
  }
  const body = {
    item: event.item,
    old_cost: { item: event.item, qty: 50, unit: "kg", price_ngn: entry.cost },
    new_cost: event,
    measures,
  };
  const priced = await (await call("/reprice", body)).json();
  const newBag = event.unit === "kg" ? Math.round((event.price_ngn / event.qty) * 50) : event.price_ngn;
  addBoard({ item: event.item, oldBag: entry.cost, newBag, rows: priced.rows });
}

/* ---------- board ---------- */

function addBoard(board) {
  state.boards = [board, ...state.boards.filter((b) => b.item !== board.item)].slice(0, 4);
  renderBoards(board.item);
}

function renderBoards(animateItem) {
  const host = $("boards");
  host.replaceChildren();
  if (!state.boards.length) {
    const empty = el("div", "empty");
    empty.id = "boards-empty";
    empty.appendChild(el("p", "", "Prices you read appear here."));
    const example = el("button", "quiet", "Try an example");
    example.type = "button";
    example.addEventListener("click", tryExample);
    empty.append(example, el("p", "help", "Fills in a made-up message and made-up stall prices, then reads them."));
    host.appendChild(empty);
    $("card-actions").hidden = true;
    return;
  }
  state.boards.forEach((board) => {
    const sheet = el("article", "sheet");
    const head = el("header", "sheet-head");
    head.appendChild(el("h3", "item", board.item));
    const bag = el("p", "bag");
    const tag = money(board.newBag);
    tag.classList.add("tag");
    bag.append("50 kg bag, was ", money(board.oldBag), " now ", tag);
    head.appendChild(bag);
    sheet.appendChild(head);

    const rows = el("ul", "rows");
    board.rows.forEach((row) => {
      const li = el("li");
      li.appendChild(el("span", "measure", `1 ${row.unit}`));
      const now = el("span", "now", naira(row.new_price));
      li.appendChild(now);
      const was = el("span", "was");
      was.append("was ");
      const strike = el("s");
      strike.appendChild(money(row.old_price));
      was.appendChild(strike);
      li.appendChild(was);
      const gap = el("span", row.lost_per_sale > 0 ? "gap lose" : "gap hold");
      gap.textContent =
        row.lost_per_sale > 0
          ? `Losing ${naira(row.lost_per_sale)} on each sale`
          : row.lost_per_sale < 0
            ? `${naira(-row.lost_per_sale)} above what you need`
            : "Old price already right";
      li.appendChild(gap);
      rows.appendChild(li);
      li._now = now;
      li._gap = gap;
      li._final = row.new_price;
      li._start = row.old_price;
    });
    sheet.appendChild(rows);
    host.appendChild(sheet);
    if (board.item === animateItem && !reduceMotion.matches) playSheet(tag, rows);
  });
  $("card-actions").hidden = false;
}

// The signature moment: the new bag price tag settles into the header, then each measure
// ticks from the old price to the new one, and the loss for that sale is shown last.
function playSheet(tag, rows) {
  tag.animate(
    [{ transform: "translateY(-14px)", opacity: 0 }, { transform: "none", opacity: 1 }],
    { duration: 220, easing: "cubic-bezier(0.22, 1, 0.36, 1)", fill: "backwards" },
  );
  [...rows.children].forEach((li, index) => {
    const delay = 240 + index * 110;
    const duration = 460;
    li._gap.style.opacity = "0";
    li._now.textContent = naira(li._start);
    const begin = performance.now() + delay;
    const tick = (now) => {
      const progress = Math.min(1, Math.max(0, (now - begin) / duration));
      const eased = 1 - Math.pow(1 - progress, 3);
      const value = progress >= 1 ? li._final : Math.round(li._start + (li._final - li._start) * eased);
      li._now.textContent = naira(value);
      if (progress < 1) {
        requestAnimationFrame(tick);
      } else {
        li._gap.style.opacity = "";
        li._gap.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 180 });
      }
    };
    requestAnimationFrame(tick);
  });
}

/* ---------- card ---------- */

async function makeCard() {
  const button = $("card-button");
  const error = $("card-error");
  error.textContent = "";
  button.removeAttribute("data-state");
  busy(button, true, "Making card…");
  try {
    const items = state.boards.map((b) => ({
      item: b.item,
      prices: Object.fromEntries(b.rows.map((r) => [r.unit, r.new_price])),
    }));
    const date = new Date().toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
    const response = await call("/card.png", { shop: state.shop || "Price board", date, items });
    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const image = $("card-image");
    if (image.dataset.url) URL.revokeObjectURL(image.dataset.url);
    image.dataset.url = url;
    image.src = url;
    $("card-save").href = url;
    $("card-figure").hidden = false;
    const file = new File([blob], "price-card.png", { type: "image/png" });
    $("card-share").hidden = !(navigator.canShare && navigator.canShare({ files: [file] }));
    $("card-share").onclick = () => navigator.share({ files: [file], title: "Prices today" }).catch(() => {});
    button.dataset.state = "success";
  } catch (failure) {
    button.dataset.state = "error";
    error.textContent = failure.message;
  } finally {
    busy(button, false, "Make price card");
  }
}

/* ---------- start ---------- */

load();
$("shop").value = state.shop;
$("shop").addEventListener("input", () => {
  state.shop = $("shop").value;
  save();
});
$("message").addEventListener("input", () => {
  $("count").textContent = String($("message").value.length);
  $("message-error").textContent = "";
  $("message").removeAttribute("aria-invalid");
});
$("read-form").addEventListener("submit", onRead);
$("sample-stall").addEventListener("click", fillSample);
$("card-button").addEventListener("click", makeCard);
if (window.matchMedia("(min-width: 760px)").matches) $("stall-book").open = true;
renderBook();
renderBoards();
