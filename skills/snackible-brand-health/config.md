# Snackible Brand Health: configuration

Edit this file to change what the daily agent tracks. Anything marked `TODO` is an open Phase 0 decision. The agent runs without it and lists it under "Config gaps" in the report.

Owner of this agent: TODO (name)
Last reviewed: 2026-10-29

## SKUs

The Snackible SKUs to track. `Priority 1` SKUs are always covered and their issues rank higher in "Needs attention today". Use the same SKU name everywhere (it becomes part of the snapshot entity).

| sku | pack size (g) | MRP (₹) | priority | D2C URL | Amazon ASIN | notes |
|---|---|---|---|---|---|---|
| TODO | | | 1 | | | |
| TODO | | | 1 | | | |
| TODO | | | 2 | | | |

## Channels

| channel | status | data source |
|---|---|---|
| Snackible D2C (snackible.com) | on | site pages |
| Amazon.in | on | listing pages / Seller Central export (TODO which) |
| Blinkit | needs feed | shared scrape |
| Zepto | needs feed | shared scrape |
| Swiggy Instamart | needs feed | shared scrape |
| BigBasket | needs feed | shared scrape |
| Google reviews | on | Google Business Profile (TODO location link) |

## Pincodes

Quick-commerce availability and price vary by pincode. TODO: confirm the set (for example, two pincodes per priority city).

| pincode | city | notes |
|---|---|---|
| TODO | | |

## Tracked keywords (about 15)

Clusters: `own` = keywords Snackible should rank for and defend; `test` = keywords being tried; `block` = competitor or category terms to watch. TODO: confirm the list.

| keyword | cluster | channel(s) |
|---|---|---|
| TODO | own | Amazon.in, Google |
| TODO | test | Amazon.in |
| TODO | block | Amazon.in |

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
| reviews (B) | on | Phase 4, first |
| seo (D) | needs feed | Phase 4, first (needs GSC access) |
| seo_keywords (D) | needs feed | Phase 4, first |
| mentions (C) | on | Phase 4, second (public search only until a listening feed exists) |
| mention_items (C) | on | Phase 4, second |
| listing (A) | needs feed | Phase 4, last |
| search_rank (A) | needs feed | Phase 4, last |

## Snapshot sheet

- Google Sheet name: `Marketing Agents: Brand Health Snapshots`
- Link: TODO (one tab per module, headers per `references/snapshot-schema.md`)

## Report mode

`report only`

(Options: `report only` or `report + recommendations`.)

## Delivery

- Google Doc folder: TODO
- Recipients: TODO (small group first, per Phase 5)
- Channel: email
- Auto-send: no

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
