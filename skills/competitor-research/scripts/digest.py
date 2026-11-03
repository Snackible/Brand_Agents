"""One-command summary of a run, so the report can be written without ad-hoc analysis.

    python scripts/digest.py daily  --data data/brand_health
    python scripts/digest.py weekly --data data/competitor

Compares the newest snapshot folder with the one before it (or `--date` / `--previous`) and prints a short,
capped list of facts: data freshness, what changed, and candidates for the "needs attention" section.
It only reports what the snapshots contain; it makes no judgement about importance. That is for the report.
"""

import argparse
import csv
import glob
import json
import os
import re
import statistics as st
from collections import defaultdict

CAP = 8


def days(data):
    return sorted(d for d in os.listdir(data) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d))


def load(data, day):
    idx, status, runlog = {}, [], {}
    for f in sorted(glob.glob(os.path.join(data, day, "*.csv"))):
        with open(f, encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r["metric"] == "_collection_status":
                    status.append((r["entity"], r["value"], r["notes"]))
                else:
                    idx[(r["module"], r["entity"], r["metric"])] = r
    p = os.path.join(data, day, "_run.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as fh:
            runlog = json.load(fh)
    return idx, status, runlog


def num(x):
    try:
        return float(str(x).replace(",", ""))
    except (TypeError, ValueError):
        return None


def ents(idx, module):
    """entity -> {metric: value}, plus '_url'."""
    out = defaultdict(dict)
    for (m, e, k), r in idx.items():
        if m == module:
            out[e][k] = r["value"]
            out[e]["_url"] = r["source_url"]
    return out


def pct(new, old):
    return None if not old else (new - old) / old * 100


def cap(items, n=CAP):
    items = list(items)
    return "; ".join(items[:n]) + (f" (+{len(items) - n} more)" if len(items) > n else "") if items else "none"


def short(s, n=46):
    return s if len(s) <= n else s[: n - 1] + "..."


def out_freshness(cur_s, runlog):
    failed = [k for k, v in runlog.items() if not v.get("ok")]
    print(f"collectors failed: {', '.join(failed) if failed else 'none'}")
    seen, lines = set(), []
    for e, v, n in cur_s:
        key = (v, n[:60])
        if key in seen:
            continue
        seen.add(key)
        same = [x[0] for x in cur_s if (x[1], x[2][:60]) == key]
        lines.append(f"{v}: {cap(same, 6)} ({n[:70]})")
    print("source problems: " + (cap(lines, 10) if lines else "none"))


# ---------------------------------------------------------------- daily
def daily(cur, prev, cur_s, runlog, today, before):
    print(f"== DAILY DIGEST {today} (compared with {before or 'nothing: BASELINE'}) ==")
    out_freshness(cur_s, runlog)
    mods = defaultdict(int)
    for (m, _, _) in cur:
        mods[m] += 1
    print("rows by module: " + ", ".join(f"{m} {n}" for m, n in sorted(mods.items())))
    attention = []

    L = ents(cur, "listing")
    LP = ents(prev, "listing") if prev else {}
    d2c = {e: v for e, v in L.items() if e.endswith("| Snackible D2C | all")}
    d2cp = {e: v for e, v in LP.items() if e.endswith("| Snackible D2C | all")}
    oos = sorted(e.split(" | ")[0] for e, v in d2c.items() if v.get("in_stock") == "0")
    oosp = {e.split(" | ")[0] for e, v in d2cp.items() if v.get("in_stock") == "0"}
    print(f"\n-- snackible.com: {len(d2c)} listings, {len(oos)} out of stock, "
          f"{sum(1 for v in d2c.values() if (num(v.get('discount_pct')) or 0) > 0)} on discount")
    print("out of stock: " + cap(oos))
    if prev:
        newly = [n for n in oos if n not in oosp]
        back = [n for n in oosp if n not in oos]
        print("newly out of stock: " + cap(newly) + " | back in stock: " + cap(back))
        print("new listings: " + cap([short(e.split(' | ')[0]) for e in d2c if e not in d2cp]) +
              " | removed: " + cap([short(e.split(' | ')[0]) for e in d2cp if e not in d2c]))
        ch = []
        for e, v in d2c.items():
            a, b = num(v.get("selling_price")), num((d2cp.get(e) or {}).get("selling_price"))
            if a is not None and b and abs(pct(a, b)) >= 5:
                ch.append((abs(pct(a, b)), f"{short(e.split(' | ')[0], 34)} {b:g}->{a:g}"))
        print("price changes >=5%: " + cap([t for _, t in sorted(ch, reverse=True)]))
        attention += [f"newly out of stock on snackible.com: {n}" for n in newly[:CAP]]
    else:
        attention += [f"out of stock on snackible.com: {n}" for n in oos[:CAP]]

    amz = {e: v for e, v in L.items() if e.endswith("| Amazon.in | all")}
    amzp = {e: v for e, v in LP.items() if e.endswith("| Amazon.in | all")}
    unpriced = [short(v.get("title", e), 40) for e, v in amz.items() if "selling_price" not in v]
    rated = [num(v.get("rating")) for v in amz.values() if num(v.get("rating"))]
    print(f"\n-- Amazon: {len(amz)} listings, {len(amz) - len(unpriced)} priced, avg rating "
          f"{(st.mean(rated) if rated else 0):.2f}")
    print("no buy price shown: " + cap(unpriced))
    attention += [f"Amazon listing with no buy price: {u}" for u in unpriced[:CAP]]
    above = [short(v.get("title", e), 36) for e, v in amz.items()
             if num(v.get("selling_price")) and num(v.get("mrp")) and num(v["selling_price"]) > num(v["mrp"])]
    if above:
        print("priced above MRP: " + cap(above))
        attention += [f"priced above MRP on Amazon: {a}" for a in above[:CAP]]
    seen_low, lowd = set(), {}
    for e, v in amz.items():
        r, n, t = num(v.get("rating")), num(v.get("review_count")) or 0, v.get("title", e)
        if r and r < 4.0 and n >= 40 and (t[:40], r, n) not in seen_low:
            seen_low.add((t[:40], r, n))
            lowd[e] = (r, int(n), short(t, 38))
    low = sorted(lowd.values(), key=lambda t: -t[1])
    print("rated <4.0 with 40+ reviews: " + cap([f"{t} {r} ({n})" for r, n, t in low]))
    if prev:
        drops = []
        for e, v in amz.items():
            a, b = num(v.get("rating")), num((amzp.get(e) or {}).get("rating"))
            if a is not None and b is not None and b - a >= 0.1:
                drops.append(f"{short(v.get('title', e), 34)} {b}->{a}")
        print("rating drops >=0.1: " + cap(drops))
        attention += [f"Amazon rating drop: {d}" for d in drops[:CAP]]
        pc = []
        for e, v in amz.items():
            a, b = num(v.get("selling_price")), num((amzp.get(e) or {}).get("selling_price"))
            if a and b and abs(pct(a, b)) >= 5:
                pc.append(f"{short(v.get('title', e), 30)} {b:g}->{a:g}")
        print("Amazon price changes >=5%: " + cap(pc))
    else:
        attention += [f"low Amazon rating with many reviews: {t} {r} ({n} reviews)" for r, n, t in low[:4]]

    for ch in ("Blinkit", "Zepto", "Swiggy Instamart"):
        qc = {e: v for e, v in L.items() if f"| {ch} |" in e}
        if not qc:
            continue
        qp = {e: v for e, v in LP.items() if f"| {ch} |" in e}
        sp = []
        for e, v in qc.items():
            a, b = num(v.get("selling_price")), num((qp.get(e) or {}).get("selling_price"))
            if a and b and abs(pct(a, b)) >= 5:
                sp.append(f"{short(e.split(' | ')[0], 30)} {b:g}->{a:g}")
        gone = [short(e.split(" | ")[0], 30) for e in qp if e not in qc]
        print(f"\n-- {ch}: {len(qc)} Snackible items found" + (f"; price changes >=5%: {cap(sp)}; no longer seen: {cap(gone)}" if prev else ""))

    R, RP = ents(cur, "search_rank"), (ents(prev, "search_rank") if prev else {})
    by = defaultdict(list)
    for e, v in R.items():
        kw, ch = e.split(" | ")[0], e.split(" | ")[1]
        by[ch].append((kw, int(num(v.get("rank")) or 99), (int(num((RP.get(e) or {}).get("rank")) or 0) or None)))
    for ch, rows in by.items():
        notfound = [k for k, r, _ in rows if r == 99]
        found = [f"{k} #{r}" + (f" (was #{p})" if p and p != r else "") for k, r, p in rows if r != 99]
        print(f"\n-- keyword rank on {ch}: {len(rows)} keywords, not found for {len(notfound)}")
        print("found: " + cap(found, 12))
        print("not found: " + cap(notfound, 12))
        if prev:
            mv = [f"{k} #{p}->#{'not found' if r == 99 else r}" for k, r, p in rows if p and ((r - p) >= 3 or (p <= 10 < r))]
            print("got worse: " + cap(mv))
            attention += [f"rank worse on {ch}: {m}" for m in mv[:CAP]]
    M, MP = ents(cur, "mention_items"), (ents(prev, "mention_items") if prev else {})
    new = [short(v.get("summary", e), 50) for e, v in M.items() if e not in MP]
    neg = [short(v.get("summary", e), 50) for e, v in M.items() if v.get("sentiment") == "negative"]
    print(f"\n-- mentions: {len(M)} items, {len(new)} new" + f"; negative: {cap(neg)}; new: {cap(new, 4)}")
    attention += [f"negative mention: {n}" for n in neg[:4]]
    print("\n== ATTENTION CANDIDATES (you decide what really needs attention) ==")
    print("\n".join(f"- {a}" for a in attention) if attention else "- none")


# ---------------------------------------------------------------- weekly
CLAIMS = ["high protein", "no added sugar", "gluten free", "cholesterol free", "no palm oil", "olive oil", "baked",
          "vegan", "no maida", "millet", "probiotic", "whey", "plant protein", "zero sugar"]


def brand(e):
    return e.split(" | ")[0]


def weekly(cur, prev, cur_s, runlog, today, before):
    print(f"== WEEKLY DIGEST {today} (compared with {before or 'nothing: BASELINE'}) ==")
    out_freshness(cur_s, runlog)
    P, PP = ents(cur, "price"), (ents(prev, "price") if prev else {})
    S, SP = ents(cur, "sku_tracker"), (ents(prev, "sku_tracker") if prev else {})
    RV, RVP = ents(cur, "reviews"), (ents(prev, "reviews") if prev else {})
    brands = sorted({brand(e) for e in list(P) + list(S) if " | " in e})
    for b in brands:
        print(f"\n-- {b}")
        for chn, label in (("Brand D2C", "D2C"), ("Amazon.in", "Amazon"), ("Blinkit", "Blinkit"), ("Zepto", "Zepto"), ("Swiggy Instamart", "Instamart")):
            cs = {e: v for e, v in P.items() if brand(e) == b and e.endswith("| " + chn)}
            if not cs:
                continue
            ps = {e: v for e, v in PP.items() if brand(e) == b and e.endswith("| " + chn)}
            disc = [num(v.get("discount_pct")) for v in cs.values() if num(v.get("discount_pct")) is not None]
            pp = [num(v.get("price_per_100g")) for v in cs.values() if num(v.get("price_per_100g"))]
            line = f"{label}: {len(cs)} priced"
            if pp:
                line += f", median Rs{st.median(pp):.0f}/100g"
            if disc:
                line += f", median discount {st.median(disc):.0f}%"
            ratings = [num(RV[e].get("rating")) for e in cs if e in RV and num(RV[e].get("rating"))]
            if ratings:
                line += f", avg rating {st.mean(ratings):.2f}"
            if prev and ps:
                pb = [num(v.get("price_per_100g")) for v in ps.values() if num(v.get("price_per_100g"))]
                if pb and pp:
                    line += f" (median/100g was {st.median(pb):.0f})"
            print(line)
            if prev and ps:
                ch = []
                for e, v in cs.items():
                    a, o = num(v.get("selling_price")), num((ps.get(e) or {}).get("selling_price"))
                    if a and o and abs(pct(a, o)) >= 5:
                        name = (S.get(e, {}).get("title") or e.split(" | ")[1])
                        ch.append((abs(pct(a, o)), f"{short(name, 34)} {o:g}->{a:g}"))
                new = [short(S.get(e, {}).get("title") or e.split(" | ")[1], 34) for e in cs if e not in ps]
                gone = [short(SP.get(e, {}).get("title") or e.split(" | ")[1], 34) for e in ps if e not in cs]
                print("   price changes >=5%: " + cap([t for _, t in sorted(ch, reverse=True)], 5))
                print(f"   new in results: {cap(new, 4)} | no longer in results: {cap(gone, 4)}"
                      + (" (Amazon and delivery-app results are searches, so 'no longer in results' is not proof of delisting)" if chn != "Brand D2C" else ""))
    A, AP = ents(cur, "paid_ads"), (ents(prev, "paid_ads") if prev else {})
    print("\n-- Meta ads")
    for b in sorted({brand(e) for e in A}):
        ads = {e: v for e, v in A.items() if brand(e) == b and " | " in e}
        act = num(A.get(b, {}).get("active_ads"))
        days_ = [num(v.get("days_live")) for v in ads.values() if num(v.get("days_live")) is not None]
        offers = defaultdict(int)
        for v in ads.values():
            if v.get("offer") and v["offer"] != "none":
                offers[v["offer"]] += 1
        line = f"{b}: {int(act) if act is not None else len(ads)} active, {sum(1 for d in days_ if d > 7)} live >7 days, oldest {int(max(days_)) if days_ else '-'}d, offers {dict(sorted(offers.items(), key=lambda x: -x[1])[:3])}"
        if prev:
            pa = {e for e in AP if brand(e) == b and " | " in e}
            ne = [e for e in ads if e not in pa]
            gone = [e for e in pa if e not in ads]
            hooks = [short(ads[e].get("hook", ""), 40) for e in ne]
            line += f" | new ads {len(ne)} ({cap(hooks, 3)}), stopped {len(gone)}"
        print(line)
    print("   (ad counts are lower bounds when the source problems above say 'partial')")
    gift = [(brand(e), short(e.split(" | ")[1], 40), v.get("selling_price")) for e, v in P.items()
            if e.endswith("| Brand D2C") and re.search(r"gift|hamper|diwali|festive", e, re.I)]
    giftp = {e for e in PP if re.search(r"gift|hamper|diwali|festive", e, re.I)}
    print(f"\n-- gifting on brand sites: {len(gift)} listings" + (f", {sum(1 for e in P if re.search(r'gift|hamper|diwali|festive', e, re.I) and e not in giftp)} new" if prev else ""))
    print("   " + cap([f"{b} {n} Rs{p}" for b, n, p in gift]))
    print("\n-- claims seen in product titles (observations only)")
    tcur, tprev = defaultdict(list), defaultdict(list)
    for e, v in S.items():
        if v.get("title"):
            tcur[brand(e)].append(v["title"].lower())
    for e, v in SP.items():
        if v.get("title"):
            tprev[brand(e)].append(v["title"].lower())
    for b, ts in sorted(tcur.items()):
        c = {k: sum(k in t for t in ts) for k in CLAIMS if any(k in t for t in ts)}
        pc = {k: sum(k in t for t in tprev.get(b, [])) for k in c} if prev else {}
        new = [k for k in c if prev and not pc.get(k)]
        print(f"   {b}: {c}" + (f" | new this week: {new}" if new else ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("agent", choices=["daily", "weekly"])
    ap.add_argument("--data", required=True)
    ap.add_argument("--date")
    ap.add_argument("--previous")
    a = ap.parse_args()
    ds = days(a.data)
    if not ds:
        raise SystemExit("no snapshot folders found")
    today = a.date or ds[-1]
    earlier = [d for d in ds if d < today]
    before = a.previous or (earlier[-1] if earlier else None)
    cur, cur_s, runlog = load(a.data, today)
    prev = load(a.data, before)[0] if before else None
    (daily if a.agent == "daily" else weekly)(cur, prev, cur_s, runlog, today, before)


if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
