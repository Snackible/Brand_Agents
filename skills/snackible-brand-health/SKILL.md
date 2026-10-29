---
name: snackible-brand-health
description: Daily Snackible brand health report for Marketing. Checks Snackible's own listings (stock, price vs MRP parity, title/image compliance, rating, review count and search rank by SKU × channel × pincode), new reviews and complaint themes (Amazon, quick commerce, D2C, Google), unprompted mentions and creator posts (Instagram, Reddit, X, YouTube), and SEO / web health (GSC clicks, branded vs non-branded, keyword ranks, broken collections). Stores a dated snapshot, compares with yesterday and writes a short report led by "Needs attention today", delivered as a Google Doc plus email draft. Use this whenever someone asks for the daily brand health report, how Snackible's listings, ratings, reviews, mentions or SEO are doing, whether any SKU is out of stock or mispriced, or when the daily scheduled run fires — even if they don't name the skill.
---

# Snackible Brand Health (daily)

You produce Snackible Marketing's daily brand health report. It is read quickly, every morning, so the job is to separate the few things that **need attention today** from the steady state. That only works with history: each run stores a dated snapshot and compares it to the previous day.

Spine of every run:

1. **Load config** → 2. **Collect** → 3. **Store snapshot** → 4. **Diff against yesterday** → 5. **Write report** → 6. **Deliver**

Don't skip step 3: tomorrow's report depends on today's snapshot.

## Files in this skill

- `config.md` — SKUs, channels, pincodes, tracked keywords, data feeds, module status, thresholds, sheet location, recipients. Read it first, every run. The team edits this file.
- `references/modules.md` — per module (A listing health, B reviews, C mentions, D SEO): what to collect, sources, row naming, gotchas. Read the sections you are running.
- `references/report-template.md` — the exact report structure.
- `references/snapshot-schema.md` — snapshot sheet layout and conventions.
- `scripts/collectors/` — headless collectors and the Chrome importer; `scripts/chrome/extract_qc.js` — in-page extractor run through Claude in Chrome.
- `scripts/diff_snapshots.py` — compares the current snapshot with the previous one using the thresholds in `config.md`.

## 1. Load config

Read `config.md`. Note which modules are `on`, `off` or `needs feed`, and any `TODO` entries. Don't invent SKUs, pincodes or keywords. Run with what is confirmed and list gaps under "Config gaps" at the end of the report.

The report date is today; the comparison is the most recent earlier snapshot (normally yesterday; after a weekend or outage it may be older, so say which date you compared against).

## 2. Collect

Snapshots live in a data folder, one subfolder per run date: `data/brand_health/<YYYY-MM-DD>/`, one CSV per collector. In the project repo that is `data/brand_health/` at the repo root; if the skill is installed on its own, use `./data/brand_health/` in the working directory. Call it `$DATA` below.

**Step A: headless collectors (one command).** Run from the skill folder:

```bash
python scripts/collectors/run_headless.py daily --config config.md --data $DATA
```

This collects: the whole snackible.com catalogue (stock, price, MRP), Snackible's Amazon.in listings (price, MRP, rating, review count), Amazon keyword ranks for the tracked keywords, and public YouTube mentions. Read `$DATA/<date>/_run.json`: a collector with `ok: false` is a failed module for the data-freshness section, and `_collection_status` rows inside the CSVs mark partial or failed sources. Reddit, X and Instagram mentions need a login and are reported as not connected.

**Step B: quick commerce through Claude in Chrome.** Blinkit and Zepto (and Instamart) block headless access but load in the person's own Chrome. If Claude in Chrome is not connected, skip this step and report these channels as "not connected". Otherwise, for each `chrome` channel in `config.md` and each tracked keyword:
1. Open a tab and go to the search URL (`https://blinkit.com/s/?q=<keyword>`, `https://www.zeptonow.com/search?query=<keyword>`, `https://www.swiggy.com/instamart/search?query=<keyword>`).
2. Wait about 5 seconds, then run the contents of `scripts/chrome/extract_qc.js` with the JavaScript tool, prefixed with `window.__qcBrands = [...]; window.__qcFrom = 0;` listing `["Snackible"]` (this filters in the page so the output stays small) straight away (Instamart can show a login prompt a few seconds after load; do not sign in).
3. Save the returned JSON to `$DATA/<date>/chrome/<channel>_<keyword>_1.json`. The browser tool cuts output at about 1,000 characters, so a long result arrives in chunks: after the first run the extractor stays on the page, so run `window.__qc()` again for the next chunk and keep going until `from` plus the number of items reaches the number of matching products (a response with fewer items than the brand count and no [TRUNCATED] marker is the last one). Save each response as `..._1.json`, `..._2.json` and so on; the importer merges them. If a response ends in `[TRUNCATED]`, set `window.__qcFrom` to its `from` value and run `window.__qc()` again. A `total` of 0 means that page failed (a larger `total` with no items just means Snackible did not appear); say so.
4. Pause a few seconds between pages. Never enter credentials, OTPs or addresses; stop and tell the person if a CAPTCHA or sign-in wall blocks you.
Then convert:

```bash
python scripts/collectors/chrome_import.py own --brand Snackible --out $DATA/<date>/quick_commerce.csv $DATA/<date>/chrome/*.json
```

This writes `listing` rows (in stock, price, MRP) for every Snackible item found, and `search_rank` for each keyword. An item that does not appear in a search is not proof it is out of stock: only the keyword rank is recorded as 99 in that case. Prices are for the location the browser has set; say so in the report.

**Step C: reviews.** Rating and review count per listing come from step A. For complaint themes, open the Amazon review pages of the top Snackible listings in Chrome only if the person is already signed in to Amazon; otherwise report themes as not collected. Follow the reviews section of `references/modules.md`, and write rows to `$DATA/<date>/manual.csv`.

**Step D: SEO.** Google Search Console is not connected unless `config.md` says a property and feed are set. If it is, follow the seo section of `references/modules.md`; otherwise report SEO as "not connected". Check the main collection pages of snackible.com for status and product count only if you have time; the D2C catalogue already shows missing products.

General rules:
- **Use connected feeds and official sources first.** Do not try to get around bot checks, CAPTCHAs or login walls; mark the module failed or partial and move on.
- **Every row gets a source URL or source name.**
- **Record observations, not inferences.** A page that failed to load is a collection failure, not "out of stock".
- Keep a short collection log for the data-freshness section.

## 3. Store the snapshot

The files from step 2 in `$DATA/<date>/` are the snapshot. Check that every file uses the columns in `references/snapshot-schema.md`. If the team also wants the Google Sheet, append the same rows there as a second copy, but the CSV folder stays the source of truth.

## 4. Diff against yesterday

```bash
python scripts/diff_snapshots.py --config config.md $DATA/*/*.csv
```

The script compares the latest snapshot date with the one before it, per module, and lists new and removed entities and threshold-crossing changes, and counts sub-threshold changes without listing them.

Then apply judgment:
- **Decide what goes in "Needs attention today".** Include something there only if someone on the team should do something today: a top SKU out of stock on a major channel, a price above MRP or broken parity, a rating drop, a cluster of complaints on the same theme, a negative mention gaining traction, a broken collection page, a sharp drop in non-branded clicks. Rank by revenue impact and urgency. If nothing qualifies, say "Nothing needs attention today". That is a useful report, not a failure.
- **Connect signals.** A stock-out on Blinkit plus "not available" complaints plus a rank drop is one item.
- **Smooth daily noise.** SEO and mention metrics swing day to day; do not call a one-day wobble a trend.
- On the **first run** there is no baseline: use the "Baseline: current issues" form from the report template.

## 5. Write the report

Follow `references/report-template.md`. Principles:
- **Short.** "Needs attention today" first, at most ~5 items, then one compact section per module, then data freshness. Detail stays in the sheet.
- **Specific.** SKU, channel, pincode, before → after, link.
- **Claims and compliance**: flag title/image compliance issues on Snackible's listings as observed facts against the configured rules. Don't rewrite or propose health claims; the team reviews Snackible's claims.
- **Report mode** from config: in `report only` mode, describe the issue and its impact but don't prescribe actions.
- **Always include data freshness** for each module (ok / partial / failed / not connected) with the snapshot date. Never present stale data as today's.

## 6. Deliver

Per `config.md` → Delivery:
1. Create a Google Doc titled `Brand Health — <Day, d Mon YYYY>` in the configured folder.
2. Draft an email (or message) to the recipients: subject = Doc title plus `(<n> need attention)`, body = the "Needs attention today" section plus the Doc link.
3. Send only if `Auto-send` is `yes`; otherwise leave it as a draft and say so.

If Docs or email aren't available, output the report as Markdown, save `brand_health_<YYYY-MM-DD>.md`, and state which delivery steps didn't happen.

Finish by telling the person running it: the Doc link (or file), draft or sent status, snapshot status, number of attention items, and config gaps.
