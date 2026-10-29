# Weekly report template

Use this structure. Keep the whole report readable in about five minutes: roughly 600–1,200 words before the appendix. Put detail in the appendix or the snapshot sheet, not in the top sections.

```markdown
# Competitor Weekly: W<week> <year> (<Mon d> – <Sun d>)

_Compared with snapshot of <previous date>. Modules: <n> ok, <n> partial, <n> not connected. See Data freshness._

## Top changes this week
<3–7 numbered items, ranked by likely impact on Snackible. Each item: one bold sentence saying
what changed, then one or two sentences of context (why it might matter), then source links.
Merge related signals from different modules into one item (launch + ads + price cut = one story).>

1. **<Brand> <what changed>.** <Context.> [source](url)

## By competitor
<One short block per competitor with at least one change, in config priority order.
Skip competitors with no changes and list them in one line at the end: "No notable change: X, Y.">

### <Brand>
- **Launches / delistings:** ...
- **Pricing:** ...
- **Ads:** <new ads, hooks, offers; ads live > 7 days>
- **Content:** ...
- **Claims (observed):** "<verbatim claim>" on <product>. [source](url)
- **Gifting:** ...
- **Reviews:** <top complaint themes>
- **News:** ...
<Only include lines that have something.>

## Patterns across competitors
<Optional, 2–4 bullets. e.g. "Three of six brands are pushing corporate Diwali hampers under ₹1,000.">

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

## Appendix
<Full list of flagged changes from the diff script, grouped by module, and a link to the snapshot sheet.>
```

## Style

- Plain, factual sentences. Name the brand, product and channel.
- Numbers with units and direction: "₹249 → ₹219 (−12%) on Amazon.in".
- Claims are quoted and attributed, never evaluated.
- If something is uncertain (e.g. one source only), say so in the item.
- First run (no baseline): title the top section "Baseline snapshot" and summarise the current state per competitor instead of changes.
