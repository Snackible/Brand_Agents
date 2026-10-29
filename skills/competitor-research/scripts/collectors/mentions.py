"""Public mention search for a brand: Reddit and YouTube.

X and Instagram need a login to search, so they are reported as not connected rather than
worked around. Counts come from public search results only and undercount; the report says so.

    python mentions.py --brand Snackible --out mentions.csv
"""

import argparse
import re
from urllib.parse import quote_plus

from playwright.sync_api import sync_playwright

from common import Snapshot, UA, utf8_stdout

NEG = re.compile(r"\b(stale|rancid|bad|worst|awful|disappoint\w*|fake|scam|waste|expired|fungus|hair|insect|"
                 r"worm|sick|vomit\w*|food poisoning|not worth|terrible|avoid|broken|rotten|refund)\b", re.I)
POS = re.compile(r"\b(love|loved|great|best|amazing|tasty|delicious|good|favourite|favorite|recommend\w*|worth)\b", re.I)


def sentiment(text):
    neg, pos = len(NEG.findall(text)), len(POS.findall(text))
    return "negative" if neg > pos else "positive" if pos > neg else "neutral"


def reddit(page, brand):
    url = f"https://old.reddit.com/search?q={quote_plus(brand)}&sort=new&t=month"
    page.goto(url, timeout=45000, wait_until="domcontentloaded")
    page.wait_for_timeout(2500)
    if "blocked" in page.inner_text("body")[:300].lower() or page.query_selector("div.search-result") is None:
        if "no results" in page.inner_text("body").lower()[:2000]:
            return [], url
        raise RuntimeError("Reddit search did not return results (blocked or layout change)")
    items = page.evaluate(r"""() => [...document.querySelectorAll('div.search-result-link')].map(el => ({
        title: (el.querySelector('a.search-title')||{}).innerText || '',
        href: (el.querySelector('a.search-title')||{}).href || '',
        sub: (el.querySelector('a.search-subreddit-link')||{}).innerText || '',
        meta: (el.querySelector('.search-result-meta')||{}).innerText || '',
        time: (el.querySelector('time')||{}).dateTime || '',
        body: (el.querySelector('.search-result-body')||{}).innerText || ''
    }))""")
    return [i for i in items if brand.lower() in (i["title"] + i["body"]).lower()], url


def youtube(page, brand):
    url = f"https://www.youtube.com/results?search_query={quote_plus(brand)}&sp=CAI%253D"
    page.goto(url, timeout=45000, wait_until="domcontentloaded")
    page.wait_for_timeout(4500)
    try:
        page.get_by_role("button", name=re.compile("reject all|accept all", re.I)).first.click(timeout=2000)
    except Exception:
        pass
    items = page.evaluate(r"""() => [...document.querySelectorAll('ytd-video-renderer')].slice(0, 20).map(el => ({
        title: (el.querySelector('#video-title')||{}).innerText || '',
        href: (el.querySelector('#video-title')||{}).href || '',
        channel: (el.querySelector('ytd-channel-name')||{}).innerText || '',
        meta: [...el.querySelectorAll('#metadata-line span')].map(s => s.innerText).join(' | ')
    }))""")
    return [i for i in items if brand.lower() in (i["title"] + i["channel"]).lower()], url


def run(a):
    snap = Snapshot()
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(locale="en-IN", user_agent=UA, viewport={"width": 1366, "height": 900})
        page = ctx.new_page()
        for platform, fn in (("Reddit", reddit), ("YouTube", youtube)):
            try:
                items, url = fn(page, a.brand)
            except Exception as e:
                snap.status("mentions", platform, "failed", str(e)[:160], f"{platform} public search")
                print(f"{platform}: FAILED {str(e)[:100]}")
                continue
            sents = [sentiment(i["title"] + " " + i.get("body", "")) for i in items]
            snap.add("mentions", platform, "mentions_7d", len(items), "count", f"{platform} public search", url,
                     "last month of public results, newest first; undercounts")
            snap.add("mentions", platform, "negative_mentions_1d", sents.count("negative"), "count",
                     f"{platform} public search", url, "keyword sentiment, review before acting")
            for i, s in zip(items, sents):
                m = re.search(r"(?:/comments/|v=)([\w-]+)", i["href"])
                ent = f"{platform} | {m.group(1) if m else i['href'][-24:]}"
                snap.add("mention_items", ent, "sentiment", s, "", f"{platform} public search", i["href"])
                snap.add("mention_items", ent, "summary", i["title"][:160], "", f"{platform} public search", i["href"],
                         i.get("sub") or i.get("channel", ""))
                snap.add("mention_items", ent, "reach_hint", i.get("meta", "")[:80], "", f"{platform} public search", i["href"])
            print(f"{platform}: {len(items)} mentions")
        b.close()
    for platform in ("X", "Instagram"):
        snap.status("mentions", platform, "failed", "search requires login; not connected", "config")
    snap.write(a.out)
    print(f"wrote {len(snap.rows)} rows -> {a.out}")


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", default="Snackible")
    ap.add_argument("--out", required=True)
    run(ap.parse_args())


if __name__ == "__main__":
    main()
