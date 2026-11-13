"""Full detail tables for the report, as HTML, built from the snapshots (no tokens spent on typing tables).

    python scripts/detail_tables.py weekly --data data/competitor
    python scripts/detail_tables.py daily  --data data/brand_health

Prints HTML fragments (h2/h3, table) to paste into the report after the written summary. Every number comes
from the newest snapshot; "change" columns compare it with the snapshot before it. Missing values show as "-".
Add `--date` / `--previous` to pick snapshots, `--max-rows N` to cap long tables (default 40).
"""

import argparse
import html
import statistics as st
import sys
from collections import defaultdict

from digest import days, ents, load, num

sys.stdout.reconfigure(encoding="utf-8")

MAX_ROWS = 40


def esc(x):
    return html.escape(str(x)) if x is not None else "-"


def fmt(v, nd=0, prefix=""):
    if v is None:
        return "-"
    return f"{prefix}{v:,.{nd}f}"


def delta(new, old, nd=0, prefix="", pct=False):
    if new is None or old is None or new == old:
        return "-" if new is None or old is None else "no change"
    d = new - old
    s = f"{'+' if d > 0 else '-'}{prefix}{abs(d):,.{nd}f}"
    if pct and old:
        s += f" ({'+' if d > 0 else '-'}{abs(d) / old * 100:.0f}%)"
    return s


def med(xs):
    xs = [x for x in xs if x is not None]
    return st.median(xs) if xs else None


def table(head, rows, note=None, limit=None):
    limit = limit or MAX_ROWS
    if not rows:
        return f"<p>None.</p>"
    out = ["<table><tr>" + "".join(f"<th>{esc(h)}</th>" for h in head) + "</tr>"]
    for r in rows[:limit]:
        out.append("<tr>" + "".join(f"<td>{c if str(c).startswith('<a ') else esc(c)}</td>" for c in r) + "</tr>")
    out.append("</table>")
    if len(rows) > limit:
        out.append(f"<p><i>Showing {limit} of {len(rows)} rows.</i></p>")
    if note:
        out.append(f"<p><i>{esc(note)}</i></p>")
    return "\n".join(out)


def link(url, text):
    return f"<a href='{html.escape(url)}'>{esc(text)}</a>" if url else esc(text)


def parts(entity):
    return [p.strip() for p in entity.split(" | ")]


# ---------------------------------------------------------------- weekly

def weekly(cur, prev):
    out = []
    price, prev_price = ents(cur, "price"), ents(prev, "price") if prev else {}
    sku, prev_sku = ents(cur, "sku_tracker"), ents(prev, "sku_tracker") if prev else {}
    revs = ents(cur, "reviews")
    ads, prev_ads = ents(cur, "paid_ads"), ents(prev, "paid_ads") if prev else {}
    content = ents(cur, "content")

    def brand_channel(e):
        p = parts(e)
        return p[0], p[-1]

    by_bc = defaultdict(list)
    for e, m in price.items():
        if "selling_price" in m and e.count(" | ") >= 2:
            by_bc[brand_channel(e)].append((e, m))
    brands = sorted({b for b, _ in by_bc} | {parts(e)[0] for e in ads if " | " in e or e in ads} | {e.split(" | ")[0] for e in content})
    channels = sorted({c for _, c in by_bc})

    # 1 Scorecard
    out.append("<h2>Detail: competitor scorecard</h2>")
    rows = []
    for b in brands:
        items = [(e, m) for (bb, c), v in by_bc.items() if bb == b for e, m in v]
        ppg = med([num(m.get("price_per_100g")) for _, m in items])
        disc = med([num(m.get("discount_pct")) for _, m in items])
        rev_items = [(e, m) for e, m in revs.items() if parts(e)[0] == b and "rating" in m]
        rating = med([num(m.get("rating")) for _, m in rev_items])
        rcount = sum(num(m.get("review_count")) or 0 for _, m in rev_items)
        active = next((num(m.get("active_ads")) for e, m in ads.items() if e == b and "active_ads" in m), None)
        fol = next((num(m.get("followers")) for e, m in content.items() if e.split(" | ")[0] == b and "followers" in m), None)
        rows.append([b, len(items), fmt(ppg, 0, "₹"), fmt(disc, 0) + ("%" if disc is not None else ""), fmt(rating, 1),
                     fmt(rcount), fmt(active), fmt(fol)])
    out.append(table(["brand", "priced items seen", "median ₹/100g", "median discount", "median Amazon rating",
                      "Amazon reviews (sum)", "active Meta ads", "Instagram followers"], rows,
                     "Medians are across every priced item found for that brand in all channels. Amazon and delivery-app "
                     "items are search results, not full catalogues."))

    # 2 Price per 100g by brand x channel
    out.append("<h2>Detail: price per 100 g by brand and channel</h2>")
    rows = []
    for (b, c), items in sorted(by_bc.items()):
        v = [num(m.get("price_per_100g")) for _, m in items]
        v = [x for x in v if x is not None]
        if not v:
            continue
        pv = [num(m.get("price_per_100g")) for e, m in prev_price.items()
              if e.count(" | ") >= 2 and brand_channel(e) == (b, c)] if prev else []
        pv = [x for x in pv if x is not None]
        d = delta(med(v), med(pv), 0, "₹") if pv else "no earlier data"
        disc = med([num(m.get("discount_pct")) for _, m in items])
        rows.append([b, c, len(v), fmt(min(v), 0, "₹"), fmt(med(v), 0, "₹"), fmt(max(v), 0, "₹"),
                     fmt(disc, 0) + ("%" if disc is not None else ""), d])
    out.append(table(["brand", "channel", "items", "min", "median", "max", "median discount", "median change vs last"], rows,
                     "The change compares medians of whichever items each snapshot found, so on Amazon and delivery apps it can move because the search results changed, not because prices did. The price-change table below compares the same product."))

    # 3 Every price move >= 5% (uncapped)
    out.append("<h2>Detail: every price change of 5% or more</h2>")
    rows = []
    for e, m in price.items():
        pm = prev_price.get(e)
        a, b = num(m.get("selling_price")), num(pm.get("selling_price")) if pm else None
        if a and b and abs(a - b) / b >= 0.05:
            title = (sku.get(e, {}).get("title") or (parts(e)[1] if len(parts(e)) > 1 else e))[:60]
            rows.append([parts(e)[0], parts(e)[-1], title, fmt(b, 0, "₹"), fmt(a, 0, "₹"), f"{(a - b) / b * 100:+.0f}%",
                         link(m.get("_url"), "link") if m.get("_url") else "-"])
    rows.sort(key=lambda r: float(r[5].rstrip("%")))
    out.append(table(["brand", "channel", "product", "before", "now", "change", "source"], rows) if prev else "<p>No earlier snapshot to compare with.</p>")

    # 4 Launches and removals
    out.append("<h2>Detail: new and removed listings</h2>")
    rows = []
    QC = ("Blinkit", "Zepto", "Swiggy Instamart")
    if prev:
        for e in sku:
            if parts(e)[-1] in QC:
                continue
            if e not in prev_sku and "listed" in sku[e] or (e in sku and e not in prev_sku):
                rows.append(["new", parts(e)[0], parts(e)[-1], (sku[e].get("title") or parts(e)[1] if len(parts(e)) > 2 else parts(e)[1])[:70]])
        for e in prev_sku:
            if parts(e)[-1] in QC:
                continue
            if e not in sku and "listed" in prev_sku[e]:
                rows.append(["gone", parts(e)[0], parts(e)[-1], (prev_sku[e].get("title") or parts(e)[1])[:70]])
    rows.sort(key=lambda r: (r[1], r[0]))
    out.append(table(["", "brand", "channel", "product"], rows,
                     "Brand D2C sites and Amazon only. On Amazon, 'gone' means it dropped out of the search results, not that it was delisted. Delivery-app items are not compared this way because their search results change between sessions.")
               if prev else "<p>No earlier snapshot to compare with.</p>")

    # 5 Paid ads
    out.append("<h2>Detail: Meta ads by brand</h2>")
    rows = []
    for b in brands:
        mine = [(e, m) for e, m in ads.items() if e.startswith(b + " | ") and "days_live" in m]
        active = next((num(m.get("active_ads")) for e, m in ads.items() if e == b and "active_ads" in m), None)
        d = [num(m["days_live"]) for _, m in mine if num(m.get("days_live")) is not None]
        offers = defaultdict(int)
        hooks = defaultdict(int)
        for _, m in mine:
            if m.get("offer"):
                offers[m["offer"]] += 1
            if m.get("hook"):
                hooks[m["hook"][:50]] += 1
        top = lambda dct, n: "; ".join(f"{k} (x{v})" for k, v in sorted(dct.items(), key=lambda x: -x[1])[:n]) or "-"
        prev_n = len([1 for e in prev_ads if e.startswith(b + " | ") and "days_live" in prev_ads[e]]) if prev else None
        rows.append([b, fmt(active), len(mine) if mine else 0, sum(1 for x in d if x > 7), fmt(max(d)) if d else "-",
                     top(hooks, 3), top(offers, 3), "-" if prev_n is None else f"{len(mine) - prev_n:+d}"])
    out.append(table(["brand", "active ads (count)", "ads read", "live over 7 days", "oldest (days)", "top hooks", "top offers",
                      "ads read vs last"], rows,
                     "Ad counts are lower bounds when the Ad Library scroll limit was hit (see Data freshness)."))

    # 6 Delivery apps
    qc = ents(cur, "price")
    q_rows = []
    for (b, c), items in sorted(by_bc.items()):
        if c in ("Blinkit", "Zepto", "Swiggy Instamart"):
            v = [num(m.get("price_per_100g")) for _, m in items]
            v = [x for x in v if x is not None]
            names = ", ".join(sorted({parts(e)[1][:28] for e, _ in items})[:4])
            q_rows.append([b, c, len(items), fmt(med(v), 0, "₹"), names])
    if q_rows:
        out.append("<h2>Detail: delivery apps (Blinkit, Zepto)</h2>")
        out.append(table(["brand", "app", "items found", "median ₹/100g", "examples"], q_rows,
                         "Prices are for the location set in the browser; they vary by pincode."))

    # 7 Top Amazon products per brand
    out.append("<h2>Detail: top Amazon products per brand (by review count)</h2>")
    rows = []
    for b in brands:
        mine = [(e, m) for e, m in revs.items() if parts(e)[0] == b and "review_count" in m]
        mine.sort(key=lambda x: -(num(x[1].get("review_count")) or 0))
        for e, m in mine[:3]:
            pr = price.get(e, {})
            title = (sku.get(e, {}).get("title") or "")[:60]
            rows.append([b, title, fmt(num(pr.get("selling_price")), 0, "₹"), fmt(num(pr.get("price_per_100g")), 0, "₹"),
                         fmt(num(m.get("rating")), 1), fmt(num(m.get("review_count"))),
                         link(m.get("_url") or pr.get("_url"), "link")])
    out.append(table(["brand", "product", "price", "₹/100g", "rating", "reviews", "source"], rows, limit=60))

    # 8 Instagram
    ig = [(e, m) for e, m in content.items() if "followers" in m]
    if ig:
        out.append("<h2>Detail: Instagram</h2>")
        pc = ents(prev, "content") if prev else {}
        rows = [[e.split(" | ")[0], fmt(num(m["followers"])), delta(num(m["followers"]), num(pc.get(e, {}).get("followers")), 0, "", True)
                 if prev else "-"] for e, m in sorted(ig, key=lambda x: -(num(x[1]["followers"]) or 0))]
        out.append(table(["brand", "followers", "change vs last"], rows))
    return "\n".join(out)


# ---------------------------------------------------------------- daily

def daily(cur, prev):
    out = []
    L, PL = ents(cur, "listing"), ents(prev, "listing") if prev else {}

    def where(e):
        p = parts(e)
        return p[-2] if len(p) >= 2 else e

    def name(e, m):
        p = parts(e)
        if p[0].startswith("ASIN "):
            return (m.get("title") or p[0])[:58], p[0][5:]
        return p[0][:58], ""

    out.append("<h2>Detail: every listing</h2>")
    for ch in sorted({where(e) for e in L}):
        rows = []
        for e, m in sorted(L.items(), key=lambda x: name(x[0], x[1])[0]):
            if where(e) != ch or "selling_price" not in m and "in_stock" not in m:
                continue
            t, asin = name(e, m)
            pm = PL.get(e, {})
            sp, psp = num(m.get("selling_price")), num(pm.get("selling_price"))
            stock = m.get("in_stock")
            rows.append([t, "yes" if stock == "1" else ("NO" if stock == "0" else "-"), fmt(num(m.get("mrp")), 0, "₹"),
                         fmt(sp, 0, "₹"), fmt(num(m.get("discount_pct")), 0) + ("%" if m.get("discount_pct") else ""),
                         delta(sp, psp, 0, "₹", True) if prev else "-", fmt(num(m.get("rating")), 1), fmt(num(m.get("review_count"))),
                         link(m.get("_url"), "link")])
        out.append(f"<h3>{esc(ch)} ({len(rows)} listings)</h3>")
        out.append(table(["product", "in stock", "MRP", "price", "discount", "price vs last", "rating", "reviews", "source"], rows, limit=60))

    # search rank
    R, PR = ents(cur, "search_rank"), ents(prev, "search_rank") if prev else {}
    out.append("<h2>Detail: search rank by keyword</h2>")
    rows = []
    for e, m in sorted(R.items()):
        r, p = num(m.get("rank")), num(PR.get(e, {}).get("rank"))
        shown = "not in first 48" if r == 99 else fmt(r)
        before = "-" if p is None else ("not in first 48" if p == 99 else fmt(p))
        move = "-" if r is None or p is None else ("no change" if r == p else (f"{'up' if r < p else 'down'} {abs(r - p):.0f}" if r != 99 and p != 99 else ("dropped out" if r == 99 else "entered results")))
        note = (cur.get(("search_rank", e, "rank"), {}) and cur[("search_rank", e, "rank")]["notes"] or "")
        note = "" if note.startswith(("location:", "not in first")) else note[:70]
        rows.append([parts(e)[0], where(e), shown, before, move, note])
    rows.sort(key=lambda r: (r[1], r[0]))
    out.append(table(["keyword", "channel", "position now", "position before", "move", "top Snackible result"], rows, limit=80))

    # mentions
    M = ents(cur, "mention_items")
    out.append("<h2>Detail: mentions found</h2>")
    rows = [[parts(e)[0], m.get("summary", "")[:90], m.get("sentiment", "-"), (m.get("reach_hint") or "-"), link(m.get("_url"), "link")]
            for e, m in M.items()]
    out.append(table(["source", "what", "sentiment (keyword-based)", "reach / age", "link"], rows) if rows else "<p>None found.</p>")
    return "\n".join(out)


def main():
    global MAX_ROWS
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["weekly", "daily"])
    ap.add_argument("--data", required=True)
    ap.add_argument("--date")
    ap.add_argument("--previous")
    ap.add_argument("--max-rows", type=int, default=MAX_ROWS)
    a = ap.parse_args()
    MAX_ROWS = a.max_rows
    ds = days(a.data)
    cur_day = a.date or ds[-1]
    earlier = [d for d in ds if d < cur_day]
    prev_day = a.previous or (earlier[-1] if earlier else None)
    cur = load(a.data, cur_day)[0]
    prev = load(a.data, prev_day)[0] if prev_day else None
    print(f"<!-- snapshot {cur_day}, compared with {prev_day or 'nothing'} -->")
    print((weekly if a.mode == "weekly" else daily)(cur, prev))


if __name__ == "__main__":
    main()
