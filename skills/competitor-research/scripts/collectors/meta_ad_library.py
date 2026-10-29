"""Meta Ad Library collector: active ads per competitor, how long they have run, hooks and offers.

Uses the public Ad Library site (the source named in the build plan). Keyword search also
returns retailers advertising a brand's products, so only ads whose advertiser name matches
the brand are counted. Scrolling loads more ads; if the scroll limit is reached before the
list ends, the count is recorded as a lower bound in notes.

    python meta_ad_library.py --config ../../config.md --out ads.csv
    python meta_ad_library.py --brand Farmley --out ads.csv
"""

import argparse
import datetime as dt
import random
import re
from urllib.parse import quote_plus

from playwright.sync_api import sync_playwright

from common import Snapshot, UA, md_table, real, utf8_stdout

URL = ("https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=IN"
       "&q={q}&search_type=keyword_unordered&media_type=all")
OFFER = re.compile(r"(\d+\s*%\s*off|flat\s*[₹rs.]*\s*\d+|buy\s*\d+\s*get\s*\d+|free (?:shipping|delivery|gift)|"
                   r"use code \w+|code:?\s*[A-Z0-9]{4,}|upto \d+%|up to \d+%|₹\s?\d[\d,]*)", re.I)
NOISE = {"", "Sponsored", "Platforms", "Open Drop-down", "See ad details", "This ad has multiple versions",
         "Order Now", "Shop Now", "Learn More", "Sign Up", "Get Offer", "Buy Now", "Send message", "Download",
         "​", "Active", "Inactive"}


def parse_ads(text):
    """Split page text into ad dicts using the 'Library ID:' markers."""
    ads = []
    parts = re.split(r"(?=Library ID: \d+)", text)
    for part in parts:
        m = re.match(r"Library ID: (\d+)", part)
        if not m:
            continue
        lines = [l.strip() for l in part.splitlines()]
        started = re.search(r"Started running on (\d{1,2} \w{3} \d{4})", part)
        try:
            start = dt.datetime.strptime(started.group(1), "%d %b %Y").date() if started else None
        except ValueError:
            start = None
        advertiser, body = "", []
        if "See ad details" in lines:
            rest = lines[lines.index("See ad details") + 1:]
            rest = [l for l in rest if l not in NOISE and not re.fullmatch(r"\d+ ads? use this creative.*", l)]
            if rest:
                advertiser, body = rest[0], rest[1:]
        ads.append({"id": m.group(1), "start": start, "advertiser": advertiser,
                    "body": [b for b in body if b.upper() != b or len(b) > 14][:6],
                    "versions": "multiple versions" in part})
    return ads


PAGE_URL = ("https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=IN"
            "&view_all_page_id={pid}&search_type=page&media_type=all")


def collect_brand(page, brand, max_scrolls=10, page_id=""):
    # With a Page ID the search is limited to that advertiser, which fixes generic brand names.
    page.goto(PAGE_URL.format(pid=page_id) if page_id else URL.format(q=quote_plus(brand)),
              timeout=60000, wait_until="domcontentloaded")
    page.wait_for_timeout(7000)
    total_match = re.search(r"~?([\d,]+)\s+results?", page.inner_text("body"))
    total = int(total_match.group(1).replace(",", "")) if total_match else None
    seen, stable = 0, 0
    for _ in range(max_scrolls):
        page.mouse.wheel(0, 4000)
        page.wait_for_timeout(2500 + random.randint(0, 800))
        n = page.inner_text("body").count("Library ID:")
        stable = stable + 1 if n == seen else 0
        seen = n
        if stable >= 2 or (total and n >= total):
            break
    ads = parse_ads(page.inner_text("body"))
    return ads, total, seen


def run(a):
    snap = Snapshot()
    today = dt.date.today()
    if a.brand:
        targets = [(a.brand, "")]
    else:
        targets = [(r["brand"], real(r.get("meta page id", ""))) for r in md_table(a.config, "Competitors")]
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(locale="en-US", user_agent=UA, viewport={"width": 1366, "height": 900},
                            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"})
        page = ctx.new_page()
        for brand, page_id in targets:
            try:
                ads, total, loaded = collect_brand(page, brand, page_id=page_id)
            except Exception as e:
                snap.status("paid_ads", brand, "failed", f"Ad Library did not load: {str(e)[:120]}", "Meta Ad Library")
                print(f"{brand}: FAILED {str(e)[:80]}")
                continue
            key = brand.lower().replace("!", "").replace(" ", "")
            own = [x for x in ads if key in x["advertiser"].lower().replace("!", "").replace(" ", "")]
            url = PAGE_URL.format(pid=page_id) if page_id else URL.format(q=quote_plus(brand))
            partial = bool(total and loaded < total)
            note = f"advertiser-matched ads among {loaded} loaded of ~{total} keyword results" + (
                "; scroll limit reached, count is a lower bound" if partial else "")
            snap.add("paid_ads", brand, "active_ads", len(own), "count", "Meta Ad Library", url, note)
            if partial:
                snap.status("paid_ads", brand, "partial", "scroll limit reached before end of results", "Meta Ad Library")
            for ad in own:
                ent = f"{brand} | {ad['id']}"
                aurl = f"https://www.facebook.com/ads/library/?id={ad['id']}"
                days = (today - ad["start"]).days if ad["start"] else None
                copy = " ".join(ad["body"])
                offer = OFFER.search(copy)
                snap.add("paid_ads", ent, "days_live", days, "days", "Meta Ad Library", aurl,
                         f"started {ad['start']}" + ("; multiple versions" if ad["versions"] else ""))
                snap.add("paid_ads", ent, "hook", (ad["body"][0] if ad["body"] else "")[:200], "", "Meta Ad Library", aurl)
                snap.add("paid_ads", ent, "offer", offer.group(0) if offer else "none", "", "Meta Ad Library", aurl)
                snap.add("paid_ads", ent, "product", (ad["body"][1] if len(ad["body"]) > 1 else "")[:140], "", "Meta Ad Library", aurl)
            print(f"{brand}: {len(own)} own ads ({len(ads)} parsed, ~{total} results)")
            page.wait_for_timeout(random.randint(3000, 6000))
        b.close()
    snap.write(a.out)
    print(f"wrote {len(snap.rows)} rows -> {a.out}")


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config")
    ap.add_argument("--brand")
    ap.add_argument("--out", required=True)
    run(ap.parse_args())


if __name__ == "__main__":
    main()
