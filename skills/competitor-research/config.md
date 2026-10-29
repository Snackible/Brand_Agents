# Competitor Research: configuration

Edit this file to change what the weekly agent tracks. Anything marked `TODO` is an open Phase 0 decision. The agent runs without it and lists it under "Config gaps" in the report until it's filled in.

Owner of this agent: TODO (name)
Last reviewed: 2026-10-29

## Competitors

DRAFT list, to be confirmed by Marketing. Remove, add or reorder freely. `Priority` decides ordering in the report (1 = always cover in depth).

| brand | priority | website | instagram | amazon brand store | notes |
|---|---|---|---|---|---|
| Farmley | 1 | https://farmley.com | TODO | TODO | TODO confirm |
| Happilo | 1 | https://happilo.com | TODO | TODO | TODO confirm |
| The Whole Truth | 1 | https://thewholetruthfoods.com | TODO | TODO | TODO confirm |
| Too Yumm! | 2 | TODO | TODO | TODO | TODO confirm |
| Yoga Bar | 2 | TODO | TODO | TODO | TODO confirm |
| Open Secret | 2 | TODO | TODO | TODO | TODO confirm |

## Channels

Where SKUs and prices are tracked. `script` = collected by `scripts/collectors` (headless). `chrome` = collected through Claude in Chrome (the person's own browser), using `scripts/chrome/extract_qc.js`. `needs feed` = not reachable; reported as "not connected".

| channel | status | how |
|---|---|---|
| Brand D2C site | on | script: Shopify product feed (The Whole Truth is not Shopify, so it is covered via Amazon only) |
| Amazon.in | on | script: search pages, top 15 per brand |
| Blinkit | on | chrome, browser's current location |
| Zepto | on | chrome, browser's current location |
| Swiggy Instamart | on | chrome, no login needed; read the page promptly after it loads, because a login prompt can appear a few seconds later |
| BigBasket | needs feed | blocks automated access; use the shared scrape |

Quick-commerce prices vary by location. The Chrome collectors read whatever location the browser has set. Note it in the report; a per-pincode matrix needs the shared scrape.

## Quick-commerce queries

Searched on each `chrome` channel; every result for a competitor brand is recorded. DRAFT, adjust to the categories that matter.

| query |
|---|
| roasted makhana |
| protein bar |
| millet chips |
| ragi chips |
| healthy snacks |

## Modules

`on` = run every week. `off` = skip. `needs feed` = depends on a data source that isn't connected yet; report as "not connected" and don't improvise it.

| module | status | phase | data source |
|---|---|---|---|
| news | on | v1 | web search |
| claims | on | v1 | brand sites, Amazon listings |
| gifting | on | v1 | brand sites, LinkedIn (public posts) |
| paid_ads | on | v1 | Meta Ad Library |
| content | on | v1 | chrome: Instagram public profile, followers only (post feed needs a login) |
| content_posts | needs feed | v1 | Instagram post feed needs a login; not connected |
| reviews | on | v2 | script: Amazon.in rating and review count; complaint themes read from review pages through Chrome when time allows |
| sku_tracker | on | v2 | script (D2C, Amazon) + chrome (Blinkit, Zepto, Instamart) |
| price | on | v2 | script (D2C, Amazon) + chrome (Blinkit, Zepto, Instamart) |

## Shared scrape

- Owner: TODO
- Where the data lands (sheet / folder / file name): TODO
- Refresh frequency: TODO
- Format (columns): TODO

Optional now: D2C, Amazon, Blinkit and Zepto are collected directly. The shared scrape would add BigBasket and a per-pincode view. Add its mapping to `references/modules.md` when it is connected.

## Snapshot sheet

- Google Sheet name: `Marketing Agents: Competitor Snapshots`
- History is stored as dated CSV files in `data/competitor/<YYYY-MM-DD>/` (one file per collector). The diff reads these directly.
- Optional: mirror to the Google Sheet. Link: TODO

## Report mode

`report only`

(Options: `report only` or `report + recommendations`. Phase 0 decision. Keep `report only` until the team decides.)

## Delivery

- Google Doc folder: TODO (Drive folder link)
- Recipients: TODO (start with a small group, per Phase 5)
- Channel: email
- Auto-send: no

## Thresholds

Used by `scripts/diff_snapshots.py`. A change is listed in the report only if it meets a rule here; smaller changes are counted but not listed. `*` matches anything. Rules: `pct_change`, `pct_drop`, `pct_rise`, `abs_change`, `drop`, `rise`, `crosses_above`, `crosses_below`, `any_change`, `ignore_removed`.

| module | metric | rule | value |
|---|---|---|---|
| price | price_per_100g | pct_change | 5 |
| price | selling_price | pct_change | 5 |
| price | discount_pct | abs_change | 5 |
| sku_tracker | pack_size_g | any_change | |
| paid_ads | days_live | crosses_above | 7 |
| paid_ads | offer | any_change | |
| paid_ads | active_ads | abs_change | 3 |
| content | posts_7d | abs_change | 3 |
| content | reels_share_pct | abs_change | 20 |
| content | avg_engagement_rate_pct | pct_change | 25 |
| content | followers | pct_change | 2 |
| content_posts | * | ignore_removed | |
| reviews | rating | drop | 0.1 |
| reviews | share_pct | abs_change | 10 |
| claims | * | ignore_removed | |
| gifting | * | ignore_removed | |
| news | * | ignore_removed | |
