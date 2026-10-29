"""Amazon.in collector: competitor SKUs and prices, Snackible keyword rank and listing health.

Reads public search result pages in a headless browser at a polite pace (a few seconds
between pages). If Amazon shows a robot check, the run records a collection failure and
stops; it does not try to get past it.

Modes
    competitors  per brand: top N listings -> sku_tracker + price rows (+ rating/review_count)
    rank         per tracked keyword: rank of the first Snackible listing -> search_rank rows
    own          Snackible brand search -> listing rows (price, MRP parity, rating, reviews)

    python amazon_in.py competitors --config ../../config.md --out amz_comp.csv
    python amazon_in.py rank --config ../../../snackible-brand-health/config.md --out amz_rank.csv
"""

import argparse
import random
import re
import sys
import time
from urllib.parse import quote_plus

from playwright.sync_api import sync_playwright

from common import Snapshot, UA, md_table, parse_grams, price_rows, real, utf8_stdout

CARD_JS = r"""
() => [...document.querySelectorAll('div[data-component-type="s-search-result"][data-asin]')].map((el, i) => {
  const t = (sel) => { const n = el.querySelector(sel); return n ? n.innerText.trim() : ''; };
  const h2 = [...el.querySelectorAll('h2')].map(h => h.innerText.trim()).filter(Boolean);
  const rating = el.querySelector('i[class*="a-icon-star"] .a-icon-alt, span.a-icon-alt');
  const reviews = el.querySelector('a[href*="customerReviews"]');
  return {
    asin: el.getAttribute('data-asin'),
    // Current layout: the first h2 is the brand, the last is the product title.
    brand: h2.length > 1 ? h2[0] : '',
    title: h2.length ? h2[h2.length - 1] : '',
    price: t('.a-price:not(.a-text-price) .a-offscreen') || t('.a-price .a-price-whole'),
    // The struck-through list price; the per-100g unit price is also an a-text-price, so match data-a-strike.
    mrp: t('.a-price.a-text-price[data-a-strike="true"] .a-offscreen'),
    rating: rating ? rating.textContent : '',
    reviews: reviews ? (reviews.getAttribute('aria-label') || reviews.innerText) : '',
    sponsored: /sponsored/i.test(el.innerText.slice(0, 120)),
    position: i + 1,
  };
}).filter(c => c.asin)
"""


def num(text):
    m = re.search(r"[\d,]+(?:\.\d+)?", (text or "").replace("₹", ""))
    return float(m.group(0).replace(",", "")) if m else None


def count(text):
    t = (text or "").lower().replace(",", "")
    m = re.search(r"(\d+(?:\.\d+)?)\s*(k|m)?", t)
    if not m:
        return None
    n = float(m.group(1))
    return int(n * {"k": 1000, "m": 1_000_000}.get(m.group(2), 1))


class Amazon:
    def __init__(self, playwright):
        self.browser = playwright.chromium.launch(headless=True)
        self.ctx = self.browser.new_context(locale="en-IN", user_agent=UA, viewport={"width": 1366, "height": 900})
        self.page = self.ctx.new_page()
        self.blocked = False

    def search(self, query):
        """Return (cards, delivery_text) or raise RuntimeError on robot check."""
        url = f"https://www.amazon.in/s?k={quote_plus(query)}"
        for attempt in (1, 2):
            self.page.goto(url, timeout=60000, wait_until="domcontentloaded")
            self.page.wait_for_timeout(2500)
            body = self.page.inner_text("body")[:600].lower()
            if "robot check" in body or "enter the characters" in body or "captcha" in body:
                self.blocked = True
                raise RuntimeError("Amazon robot check shown")
            try:
                self.page.wait_for_selector('div[data-component-type="s-search-result"]', timeout=15000)
            except Exception:
                if attempt == 2:
                    return [], ""
                continue
            break
        cards = self.page.evaluate(CARD_JS)
        try:
            delivery = self.page.inner_text("#glow-ingress-block").replace("\n", " ").strip()
        except Exception:
            delivery = ""
        time.sleep(random.uniform(3, 6))
        return cards, url if False else delivery

    def close(self):
        self.browser.close()


def match_brand(card, brand):
    text = (card.get("brand", "") + " " + card["title"]).lower().replace("!", "")
    return brand.lower().replace("!", "") in text


def run_competitors(a):
    snap = Snapshot()
    n_per = int(a.per_brand)
    brands = [r["brand"] for r in md_table(a.config, "Competitors")]
    with sync_playwright() as p:
        amz = Amazon(p)
        for brand in brands:
            try:
                cards, delivery = amz.search(brand)
            except RuntimeError as e:
                snap.status("price", f"{brand} | Amazon.in", "failed", str(e), "Amazon.in")
                print(f"{brand}: {e}; stopping Amazon run")
                break
            own = [c for c in cards if match_brand(c, brand) and not c["sponsored"]][:n_per]
            if not own:
                snap.status("price", f"{brand} | Amazon.in", "partial", "no matching organic listings on page 1", "Amazon.in")
            for c in own:
                url = f"https://www.amazon.in/dp/{c['asin']}"
                entity = f"{brand} | {c['asin']} | Amazon.in"  # ASIN keeps the key stable when titles change
                grams = parse_grams(c["title"])
                selling, mrp = num(c["price"]), num(c["mrp"])
                if selling is None:
                    continue
                note = f"ASIN {c['asin']}; delivery: {delivery}" if delivery else f"ASIN {c['asin']}"
                snap.add("sku_tracker", entity, "listed", 1, "", "Amazon.in", url, note)
                snap.add("sku_tracker", entity, "title", c["title"][:140], "", "Amazon.in", url)
                snap.add("sku_tracker", entity, "pack_size_g", grams, "g", "Amazon.in", url, "" if grams else "pack size not in title")
                price_rows(snap, "price", entity, max(mrp or selling, selling), selling, grams, "Amazon.in", url, note)
                snap.add("reviews", entity, "rating", num(c["rating"]), "", "Amazon.in", url)
                snap.add("reviews", entity, "review_count", count(c["reviews"]), "count", "Amazon.in", url)
            print(f"{brand}: {len(own)} listings")
        amz.close()
    snap.write(a.out)
    print(f"wrote {len(snap.rows)} rows -> {a.out}")


def run_rank(a):
    snap = Snapshot()
    keywords = [r for r in md_table(a.config, "Tracked keywords (about 15)") if real(r.get("keyword", ""))]
    if not keywords:
        print("no tracked keywords in config; nothing to do")
        snap.status("search_rank", "all keywords", "failed", "no keywords set in config (TODO)", "config")
        snap.write(a.out)
        return
    with sync_playwright() as p:
        amz = Amazon(p)
        for k in keywords:
            kw = k["keyword"]
            try:
                cards, delivery = amz.search(kw)
            except RuntimeError as e:
                snap.status("search_rank", f"{kw} | Amazon.in", "failed", str(e), "Amazon.in")
                break
            organic = [c for c in cards if not c["sponsored"]]
            rank, who = 99, ""
            for i, c in enumerate(organic, 1):
                if match_brand(c, a.brand):
                    rank, who = i, c["title"][:80]
                    break
            sponsored = [c["title"][:40] for c in cards if c["sponsored"] and match_brand(c, a.brand)]
            note = f"{who}; cluster {k.get('cluster','')}" if who else f"not in first {len(organic)} organic results; cluster {k.get('cluster','')}"
            if sponsored:
                note += "; sponsored placement seen"
            snap.add("search_rank", f"{kw} | Amazon.in | all", "rank", rank, "position", "Amazon.in",
                     f"https://www.amazon.in/s?k={quote_plus(kw)}", note)
            print(f"{kw}: rank {rank}")
        amz.close()
    snap.write(a.out)
    print(f"wrote {len(snap.rows)} rows -> {a.out}")


def run_own(a):
    snap = Snapshot()
    skus = [r for r in md_table(a.config, "SKUs") if real(r.get("sku", ""))]
    with sync_playwright() as p:
        amz = Amazon(p)
        try:
            cards, delivery = amz.search(a.brand)
        except RuntimeError as e:
            snap.status("listing", f"{a.brand} | Amazon.in", "failed", str(e), "Amazon.in")
            cards, delivery = [], ""
        mine = [c for c in cards if match_brand(c, a.brand) and not c["sponsored"]]
        if not mine:
            snap.status("listing", f"{a.brand} | Amazon.in", "partial", "no Snackible listings found on page 1", "Amazon.in")
        for c in mine:
            sku = c["title"][:90]
            for r in skus:
                if r["sku"].lower() in c["title"].lower():
                    sku = r["sku"]
            entity = f"ASIN {c['asin']} | Amazon.in | all"  # ASIN keeps the key stable when titles change
            url = f"https://www.amazon.in/dp/{c['asin']}"
            selling, mrp = num(c["price"]), num(c["mrp"])
            cfg_mrp = next((num(r["mrp (₹)"]) for r in skus if r["sku"] == sku and r.get("mrp (₹)")), None)
            snap.add("listing", entity, "title", sku, "", "Amazon.in", url)
            snap.add("listing", entity, "in_stock", 1 if selling is not None else 0, "", "Amazon.in", url,
                     "" if selling is not None else "no buy price shown on search result")
            if selling is not None:
                price_rows(snap, "listing", entity, mrp or cfg_mrp or selling, selling, None, "Amazon.in", url)
                if cfg_mrp:
                    snap.add("listing", entity, "above_mrp", 1 if selling > cfg_mrp else 0, "", "Amazon.in", url)
            snap.add("listing", entity, "rating", num(c["rating"]), "", "Amazon.in", url)
            snap.add("listing", entity, "review_count", count(c["reviews"]), "count", "Amazon.in", url)
        amz.close()
    snap.write(a.out)
    print(f"{len(mine)} own listings; wrote {len(snap.rows)} rows -> {a.out}")


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["competitors", "rank", "own"])
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--per-brand", default=15)
    ap.add_argument("--brand", default="Snackible")
    a = ap.parse_args()
    {"competitors": run_competitors, "rank": run_rank, "own": run_own}[a.mode](a)


if __name__ == "__main__":
    main()
