# Snackible Brand Health: configuration

Edit this file to change what the daily agent tracks. Anything marked `TODO` is an open Phase 0 decision. The agent runs without it and lists it under "Config gaps" in the report.

Owner of this agent: TODO (name)
Last reviewed: 2026-10-29

## SKUs

The whole snackible.com catalogue (about 100 listings) is checked automatically every day for stock and price, so this table is only for SKUs that need extra attention. `Priority 1` SKUs rank higher in "Needs attention today" and are matched on Amazon by name.

Note for the owner: snackible.com also lists other brands (for example GoatLife, Bubz, JoySpoon, Gul Jaipur) and festive hampers. Decide which count as Snackible's own, and list them here or set `Own brands` below so the report separates them.

Own brands: TODO (default: everything on snackible.com is reported)

| sku | pack size (g) | MRP (₹) | priority | D2C URL | Amazon ASIN | notes |
|---|---|---|---|---|---|---|
| TODO | | | 1 | | | |
| TODO | | | 1 | | | |
| TODO | | | 2 | | | |

## Channels

`script` = headless collectors in `scripts/collectors`. `chrome` = Claude in Chrome (the person's own browser) with `scripts/chrome/extract_qc.js`.

| channel | status | data source |
|---|---|---|
| Snackible D2C (snackible.com) | on | script: Shopify product feed (whole catalogue) |
| Amazon.in | on | script: brand search page (price, MRP, rating, review count) and keyword rank |
| Blinkit | on | chrome: search for each tracked keyword, browser's current location |
| Zepto | on | chrome: same |
| Swiggy Instamart | on | chrome: no login needed; read promptly after load (a login prompt can appear later) |
| BigBasket | needs feed | blocks automated access; shared scrape |
| Google reviews | needs feed | Google Business Profile (TODO location link) |

Quick-commerce results are for the location the browser has set (no pincode matrix). The report states the location.

## Pincodes

Quick-commerce availability and price vary by pincode. TODO: confirm the set (for example, two pincodes per priority city).

| pincode | city | notes |
|---|---|---|
| TODO | | |

## Tracked keywords (about 15)

Clusters: `own` = keywords Snackible should rank for and defend; `test` = keywords being tried; `block` = competitor or category terms to watch.

DRAFT list proposed from what snackible.com sells (millet, ragi, jowar, quinoa and chickpea snacks, protein chakli, no-refined-sugar cookies and spreads). Confirm or replace. Rank is checked on Amazon.in and, through Chrome, Blinkit and Zepto.

| keyword | cluster | channel(s) |
|---|---|---|
| snackible | own | Amazon.in |
| ragi chips | own | Amazon.in |
| jowar puffs | own | Amazon.in |
| quinoa puffs | own | Amazon.in |
| millet snacks | own | Amazon.in |
| protein chakli | own | Amazon.in |
| baked pizza sticks | own | Amazon.in |
| no refined sugar cookies | own | Amazon.in |
| chickpea puffs | test | Amazon.in |
| healthy chips | test | Amazon.in |
| high protein snacks | test | Amazon.in |
| chocolate hazelnut spread | test | Amazon.in |
| healthy snacks | block | Amazon.in |
| yoga bar | block | Amazon.in |
| the whole truth | block | Amazon.in |

## Listing compliance rules

What "title / image compliance" means for Snackible listings. TODO: confirm with the team.

- Title contains brand name "Snackible", product name and pack size in grams.
- Main image is the current pack design (TODO: link to the approved image set).
- No unapproved claims in title or bullets (compare against the approved claims list: TODO link).

## Data feeds

| feed | used by | status | owner | where it lands |
|---|---|---|---|---|
| Shared scrape (quick commerce) | A listing health | TODO | TODO | TODO |
| Google Search Console (property: TODO) | D SEO | TODO | TODO | GSC export / connector |
| Listening tool (Instagram, Reddit, X, YouTube) | C mentions | TODO (which tool exists today?) | TODO | TODO |

## Modules

| module | status | plan phase |
|---|---|---|
| reviews (B) | on | rating and review count come from the listing collectors; complaint themes are read from Amazon review pages in Chrome when signed in |
| seo (D) | needs feed | needs GSC access (property TODO) |
| seo_keywords (D) | needs feed | needs GSC access |
| mentions (C) | on | YouTube public search (script); Reddit, X, Instagram not connected |
| mention_items (C) | on | same |
| listing (A) | on | D2C + Amazon (script), Blinkit + Zepto (chrome) |
| search_rank (A) | on | Amazon (script), Blinkit + Zepto (chrome) |

## Snapshot sheet

- Google Sheet name: `Marketing Agents: Brand Health Snapshots`
- History is stored as dated CSV files in `data/brand_health/<YYYY-MM-DD>/` (one file per collector). The diff reads these directly.
- Optional: mirror to the Google Sheet. Link: TODO

## Report mode

`report only`

(Options: `report only` or `report + recommendations`.)

## Delivery

Recipients, send mode and the Drive folder are not kept here. On the first run the agent asks once and saves them to the Drive file `Snackible Agents Settings: brand_health_daily` (see SKILL.md, section 6), so they carry over to any Claude on the same Google account. To change them, tell the agent "change report recipients".

- Channel: email (Gmail), with the report as a Google Doc shared with the recipients as viewers
- Schedule: created automatically on the first run (every day at 08:30, local time) and saved in the same settings file. Say "change the report schedule" to move it.

## Thresholds

Used by `scripts/diff_snapshots.py`. `*` matches anything. Rules: `pct_change`, `pct_drop`, `pct_rise`, `abs_change`, `drop`, `rise`, `crosses_above`, `crosses_below`, `any_change`, `ignore_removed`. For `rank` and `position`, a higher number is worse, so `rise` means the rank got worse.

| module | metric | rule | value |
|---|---|---|---|
| listing | in_stock | any_change | |
| listing | selling_price | pct_change | 5 |
| listing | discount_pct | abs_change | 5 |
| listing | above_mrp | any_change | |
| listing | parity_gap_pct | abs_change | 5 |
| listing | title_compliant | any_change | |
| listing | image_compliant | any_change | |
| listing | rating | drop | 0.1 |
| search_rank | rank | rise | 3 |
| search_rank | rank | crosses_above | 10 |
| reviews | rating | drop | 0.1 |
| reviews | negative_reviews_1d | rise | 2 |
| reviews | count_7d | rise | 3 |
| mentions | negative_mentions_1d | rise | 2 |
| mentions | mentions_7d | pct_change | 50 |
| mention_items | * | ignore_removed | |
| seo | clicks_7d | pct_drop | 15 |
| seo | nonbranded_clicks_7d | pct_drop | 15 |
| seo | branded_clicks_7d | pct_drop | 20 |
| seo | http_status | any_change | |
| seo_keywords | position | rise | 3 |
| seo_keywords | position | crosses_above | 10 |
