"""D2C catalogue collector for Shopify stores: SKUs, MRP, selling price, price per 100g.

Reads the store's public /products.json feed, which is the catalogue the site itself
serves, so no scraping of rendered pages is needed. Stores that are not Shopify are
reported as a collection failure, not guessed.

    python shopify_d2c.py --config ../../config.md --out snapshot_sku_price.csv
    python shopify_d2c.py --site https://snackible.com --brand Snackible --out x.csv
"""

import argparse
import re
import time

import requests

from common import Snapshot, UA, md_table, parse_grams, price_rows, real, utf8_stdout

SKIP = re.compile(r"\b(gift ?card|e-?gift|sample|trial pack|free snack)\b", re.I)


def fetch_products(site, session):
    products, page = [], 1
    while page <= 20:
        r = session.get(f"{site.rstrip('/')}/products.json", params={"limit": 250, "page": page}, timeout=30)
        r.raise_for_status()
        if "json" not in r.headers.get("content-type", ""):
            raise ValueError("not a Shopify products feed")
        batch = r.json().get("products", [])
        products += batch
        if len(batch) < 250:
            break
        page += 1
        time.sleep(1)
    return products


def collect_site(snap, brand, site, module_sku="sku_tracker", module_price="price", channel="Brand D2C", own=False):
    session = requests.Session()
    session.headers["User-Agent"] = UA
    try:
        products = fetch_products(site, session)
    except Exception as e:
        for m in (module_sku, module_price):
            snap.status(m, f"{brand} | {channel}", "failed", f"{site}: {e}", "brand site")
        return 0
    n = 0
    for p in products:
        if SKIP.search(p["title"]) or not p.get("variants"):
            continue
        url = f"{site.rstrip('/')}/products/{p['handle']}"
        multi = len(p["variants"]) > 1
        for v in p["variants"]:
            vt = (v.get("title") or "").strip()
            name = p["title"] + (f" ({vt})" if multi and vt.lower() != "default title" else "")
            entity = f"{brand} | {name} | {channel}"
            grams = parse_grams(vt) or parse_grams(p["title"]) or (v.get("grams") or None)
            try:
                selling = float(v["price"])
                mrp = float(v["compare_at_price"]) if v.get("compare_at_price") else selling
            except (TypeError, ValueError):
                continue
            if selling <= 0:
                continue  # free-gift and placeholder products
            mrp = max(mrp, selling)
            note = "" if grams else "pack size not found"
            if own:
                entity = f"{name} | {channel} | all"
                snap.add(module_sku, entity, "in_stock", 1 if v.get("available") else 0, "", "brand site", url)
                snap.add(module_sku, entity, "pack_size_g", grams, "g", "brand site", url, note)
                price_rows(snap, module_price, entity, mrp, selling, None, "brand site", url, note)
                n += 1
                continue
            snap.add(module_sku, entity, "listed", 1, "", "brand site", url)
            snap.add(module_sku, entity, "pack_size_g", grams, "g", "brand site", url, note)
            snap.add(module_sku, entity, "available", 1 if v.get("available") else 0, "", "brand site", url)
            price_rows(snap, module_price, entity, mrp, selling, grams, "brand site", url, note)
            n += 1
    return n


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", help="competitor-research config.md")
    ap.add_argument("--site")
    ap.add_argument("--brand")
    ap.add_argument("--out", required=True)
    ap.add_argument("--own", action="store_true",
                    help="brand health mode: write listing rows (in_stock, price, MRP) for the brand's own site")
    a = ap.parse_args()
    snap = Snapshot()
    if a.own:
        n = collect_site(snap, a.brand, a.site, "listing", "listing", "Snackible D2C", own=True)
        snap.write(a.out)
        print(f"{a.brand}: {n} listings; wrote {len(snap.rows)} rows -> {a.out}")
        return
    targets = [(a.brand, a.site)] if a.site else [
        (r["brand"], real(r.get("website", ""))) for r in md_table(a.config, "Competitors")
    ]
    for brand, site in targets:
        if not site:
            snap.status("sku_tracker", f"{brand} | Brand D2C", "failed", "website not set in config", "config")
            print(f"{brand}: skipped (no website)")
            continue
        n = collect_site(snap, brand, site)
        print(f"{brand}: {n} variants")
    snap.write(a.out)
    print(f"wrote {len(snap.rows)} rows -> {a.out}")


if __name__ == "__main__":
    main()
