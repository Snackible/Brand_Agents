# Weekly report template

Use this structure. The report has two parts: a **written part** (about 1,200 to 2,000 words: top changes, a section for every competitor, how Snackible compares, patterns) that a marketer can read in ten minutes, and a **detail part** of full tables for looking things up. The written part comes first; the detail part follows the config-gaps section.

Be specific and complete rather than short: name the product, pack size, channel, before and after numbers and the source link in every claim. Cover every competitor in the config, including those with no change (say where they stand now: price per 100 g, discount depth, active ads, rating).

```markdown
# Competitor Weekly: W<week> <year> (<Mon d> – <Sun d>)

_Compared with snapshot of <previous date>. Modules: <n> ok, <n> partial, <n> not connected. See Data freshness._

## Top changes this week
<3–7 numbered items, ranked by likely impact on Snackible. Each item: one bold sentence saying
what changed, then one or two sentences of context (why it might matter), then source links.
Merge related signals from different modules into one item (launch + ads + price cut = one story).>

1. **<Brand> <what changed>.** <Context.> [source](url)

## By competitor
<One block for EVERY competitor, in config priority order. Start each block with a "Where they stand" line
(price per 100 g vs Snackible, discount depth, ad intensity, rating), then the lines below. For a competitor with
no change, write the "Where they stand" line and "No notable change this week." Do not drop them.>

### <Brand>
**Where they stand:** <e.g. "Median ₹190 per 100 g across 80 items (13% off); 11 active Meta ads; Amazon rating 4.3 over 34K reviews.">
- **Launches / delistings:** ...
- **Pricing:** ...
- **Ads:** <new ads, hooks, offers; ads live > 7 days>
- **Content:** ...
- **Claims (observed):** "<verbatim claim>" on <product>. [source](url)
- **Gifting:** ...
- **Reviews:** <top complaint themes>
- **News:** ...
<Only include lines that have something.>

## How Snackible compares
<3–6 bullets placing Snackible against the competitor set where comparable data exists: price per 100 g in the same
category and channel, discount depth, ad activity, rating. Observations only; no claims advice.>

## Patterns across competitors
<3–6 bullets. e.g. "Three of six brands are pushing corporate Diwali hampers under ₹1,000.">

## Recommended actions
<Only when config Report mode is "report + recommendations". Otherwise leave this section out entirely.>

## Data freshness
| module | status | snapshot date | rows | note |
|---|---|---|---|---|
| news | ok | 2026-10-26 | 7 | |
| paid_ads | partial | 2026-10-26 | 31 | Ad Library timed out for Open Secret |
| price | not connected | | | waiting for shared scrape |

## Config gaps
<List TODO items from config.md that limited this run. Omit the section if none.>

## Detail tables
<Paste the output of `python scripts/detail_tables.py weekly --data $DATA` here, unedited: competitor scorecard,
price per 100 g by brand and channel, every price change of 5% or more, new and removed listings, Meta ads by brand,
delivery apps, top Amazon products, Instagram. It is built from the snapshots, so do not retype or summarise it.>

## Appendix
<Full list of flagged changes from the diff script, grouped by module, and a link to the snapshot sheet.>
```

## Style

- Plain, factual sentences. Name the brand, product and channel.
- Numbers with units and direction: "₹249 → ₹219 (−12%) on Amazon.in".
- Claims are quoted and attributed, never evaluated.
- If something is uncertain (e.g. one source only), say so in the item.
- First run (no baseline): title the top section "Baseline snapshot" and summarise the current state per competitor instead of changes.
