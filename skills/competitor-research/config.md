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

Where SKUs and prices are tracked. `needs feed` = only available through the shared scrape.

| channel | status |
|---|---|
| Brand D2C site | on |
| Amazon.in | on |
| Blinkit | needs feed |
| Zepto | needs feed |
| Swiggy Instamart | needs feed |
| BigBasket | needs feed |

## Modules

`on` = run every week. `off` = skip. `needs feed` = depends on a data source that isn't connected yet; report as "not connected" and don't improvise it.

| module | status | phase | data source |
|---|---|---|---|
| news | on | v1 | web search |
| claims | on | v1 | brand sites, Amazon listings |
| gifting | on | v1 | brand sites, LinkedIn (public posts) |
| paid_ads | on | v1 | Meta Ad Library |
| content | on | v1 | Instagram (public profiles) |
| content_posts | on | v1 | Instagram (public profiles) |
| reviews | off | v2 | Amazon.in reviews |
| sku_tracker | needs feed | v2 | shared scrape |
| price | needs feed | v2 | shared scrape |

## Shared scrape

- Owner: TODO
- Where the data lands (sheet / folder / file name): TODO
- Refresh frequency: TODO
- Format (columns): TODO

When these are filled in, switch `sku_tracker` and `price` to `on` and add the mapping to `references/modules.md`.

## Snapshot sheet

- Google Sheet name: `Marketing Agents: Competitor Snapshots`
- Link: TODO (create the sheet with one tab per module, headers per `references/snapshot-schema.md`)

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
