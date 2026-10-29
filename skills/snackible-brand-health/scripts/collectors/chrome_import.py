"""Turn extract_qc.js output (collected through Claude in Chrome) into snapshot rows.

Claude runs scripts/chrome/extract_qc.js on a loaded quick-commerce search page, saves the
JSON it returns to a file (one file per page), then runs this script on those files.

    competitors mode: items of known competitor brands -> sku_tracker + price rows
    own mode:         Snackible items -> listing rows + search_rank for the searched keyword

    python chrome_import.py competitors --config ../../config.md --out qc.csv page1.json page2.json
    python chrome_import.py own --brand Snackible --out qc_own.csv page1.json
"""

import argparse
import json
import re
from urllib.parse import parse_qs, quote_plus, urlparse

from common import Snapshot, md_table, parse_grams, price_rows, utf8_stdout


SEARCH_URL = {"Blinkit": "https://blinkit.com/s/?q={q}", "Zepto": "https://www.zepto.com/search?query={q}",
              "Swiggy Instamart": "https://www.swiggy.com/instamart/search?query={q}"}


def url_of(d):
    """Source link for a page: the extractor no longer returns the URL, so rebuild the search link."""
    if d.get("url") and "?" in d["url"]:
        return d["url"]
    tpl = SEARCH_URL.get(d["channel"])
    return tpl.format(q=quote_plus(query_of(d))) if tpl else d.get("url", "")


def query_of(d):
    """Search term: the extractor returns it as 'query'; older files only had it in the url."""
    if d.get("query"):
        return d["query"]
    qs = parse_qs(urlparse(d.get("url", "")).query)
    return (qs.get("q") or qs.get("query") or [""])[0]


def brand_of(name, brands):
    low = re.sub(r"[^a-z0-9 ]", "", name.lower())
    for b in brands:
        if re.sub(r"[^a-z0-9 ]", "", b.lower()) in low:
            return b
    return None


def load(paths):
    """Read extractor files and merge the chunks of one page (same channel and query)."""
    chunks = []
    for p in paths:
        d = json.load(open(p, encoding="utf-8"))
        if isinstance(d, str):
            d = json.loads(d)
        chunks.append(d)
    pages = {}
    for d in sorted(chunks, key=lambda c: c.get("from", 0)):
        key = (d["channel"], query_of(d))
        if key not in pages:
            pages[key] = dict(d, items=list(d["items"]))
        else:
            pages[key]["items"] += d["items"]
            pages[key]["total"] = max(pages[key].get("total", 0), d.get("total", 0))
    return list(pages.values())


def run_competitors(a, pages):
    snap = Snapshot()
    brands = [r["brand"] for r in md_table(a.config, "Competitors")]
    for d in pages:
        ch, url = d["channel"], url_of(d)
        if not d.get("total", len(d["items"])):
            snap.status("price", f"all | {ch}", "failed", f"no products parsed from {url} (login wall or layout change)", ch)
            continue
        note = f"query '{query_of(d)}'; location: {d.get('location', '')}"
        for name, weight, price, mrp, sponsored, *_ in d["items"]:
            b = brand_of(name, brands)
            if not b:
                continue
            grams = parse_grams(weight) or parse_grams(name)
            entity = f"{b} | {name[:80]} {weight} | {ch}".replace("  ", " ")
            snap.add("sku_tracker", entity, "listed", 1, "", ch, url, note)
            snap.add("sku_tracker", entity, "pack_size_g", grams, "g", ch, url)
            price_rows(snap, "price", entity, max(mrp, price), price, grams, ch, url, note)
    snap.write(a.out)
    print(f"wrote {len(snap.rows)} rows -> {a.out}")


def run_own(a, pages):
    snap = Snapshot()
    for d in pages:
        ch, url = d["channel"], url_of(d)
        kw = query_of(d)
        if not d.get("total", len(d["items"])):
            snap.status("listing", f"{a.brand} | {ch}", "failed", f"no products parsed from {url} (login wall or layout change)", ch)
            continue
        mine = [it for it in d["items"] if a.brand.lower() in it[0].lower()]
        positions = [it[5] for it in mine if len(it) > 5 and it[5]]
        rank = min(positions) if positions else 99
        snap.add("search_rank", f"{kw} | {ch} | default", "rank", rank, "position", ch, url,
                 f"location: {d.get('location', '')}; {d.get('total', 0)} products on page")
        for name, weight, price, mrp, sponsored, *_ in d["items"]:
            if a.brand.lower() not in name.lower():
                continue
            entity = f"{name[:80]} {weight} | {ch} | default".replace("  ", " ")
            note = f"found via '{kw}'; location: {d.get('location', '')}"
            snap.add("listing", entity, "in_stock", 1, "", ch, url, note)
            price_rows(snap, "listing", entity, max(mrp, price), price, None, ch, url, note)
    snap.write(a.out)
    print(f"wrote {len(snap.rows)} rows -> {a.out}")


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["competitors", "own"])
    ap.add_argument("files", nargs="+")
    ap.add_argument("--config")
    ap.add_argument("--brand", default="Snackible")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    pages = load(a.files)
    (run_competitors if a.mode == "competitors" else run_own)(a, pages)


if __name__ == "__main__":
    main()
