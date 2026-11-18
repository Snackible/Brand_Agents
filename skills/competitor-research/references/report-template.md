# Weekly report template

Use this structure. The report has two parts: a **written part** (about 600 to 1,000 words) that a marketer can read in three to five minutes, and a **detail part** of full tables for looking things up. Nothing is lost by keeping the written part tight, because every number is in the detail tables. The written part comes first; the detail part follows the config-gaps section.

**Make it snappy.**
- Bullets, not paragraphs. One idea per bullet, 25 words or fewer, starting with a bold lead-in (brand, product or topic).
- Put the number and the change first (₹249 → ₹219, −12%), the reason it matters second, the link last.
- Do not repeat what a detail table already shows. Point to it instead ("full list: Price changes table"). Mention only what matters or what a table cannot say.
- Say each caveat once, in a single italic line under the title or in Config gaps, not inside every bullet.
- A competitor with no change gets its "Where they stand" line and nothing else.
- Still cover every competitor, and still name product, pack, channel, before and after, and the source link for every claim.

```markdown
# Competitor Weekly: W<week> <year> (<Mon d> – <Sun d>)

_Compared with snapshot of <previous date>. Modules: <n> ok, <n> partial, <n> not connected. <One short caveat line if needed.>_

## At a glance
<A table of 4 to 6 headline numbers: first row is the label, second row is the value. Plain th and td. For example:>
| Price moves of 5% or more | New listings | Removed listings | New Meta ads | Competitors with a change |
|---|---|---|---|---|
| 12 | 4 | 2 | 9 | 5 of 6 |

## Top changes this week
<3–7 numbered items, ranked by likely impact on Snackible. Each item: one bold sentence saying
what changed, then one short sentence of context (why it might matter), then the source link.
Two lines at most per item.
Merge related signals from different modules into one item (launch + ads + price cut = one story).>

1. **<Brand> <what changed>.** <Context.> [source](url)

## By competitor
<One block for EVERY competitor, in config priority order. Start each block with a one-line "Where they stand"
(price per 100 g, discount depth, ad count, rating), then at most four one-line bullets for what changed. For a
competitor with no change, write the "Where they stand" line only. Do not drop competitors.>

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
<3–5 bullets placing Snackible against the competitor set where comparable data exists: price per 100 g in the same
category and channel, discount depth, ad activity, rating. Observations only; no claims advice.>

## Patterns across competitors
<3–4 bullets. e.g. "Three of six brands are pushing corporate Diwali hampers under ₹1,000.">

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
