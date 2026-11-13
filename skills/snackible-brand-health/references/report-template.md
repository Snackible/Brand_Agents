# Daily report template

Two parts. The **written part** (about 600 to 1,200 words) is readable in five minutes: the top section does the work, then a short paragraph per module that explains what the numbers mean, not just what they are. The **detail part** is full tables for looking things up. Written part first; detail after config gaps.

Be specific: SKU and pack, channel, before → after, link. Give context for every flagged item (how long it has been like this, whether it recurs, what else changed at the same time).

```markdown
# Brand Health: <Day, d Mon YYYY>

_Compared with snapshot of <previous date>. Modules: <n> ok, <n> partial, <n> not connected._

## Needs attention today
<0–5 numbered items, ranked by urgency × revenue impact. Each: one bold sentence with SKU, channel
(and pincode if relevant) and the change, then one sentence of context, then the link.
Merge related signals across modules into one item.
If nothing qualifies, write: "Nothing needs attention today.">

1. **<SKU> out of stock on Blinkit in 3 of 4 Bengaluru pincodes (was in stock yesterday).** Also 2 "not available" complaints since yesterday. [source](url)

## Listing health (A)
<Start with two to four sentences on overall health by channel: share in stock, median discount, anything above MRP. Then:>
<One line summary: "<n> SKU × channel combinations checked; <n> out of stock, <n> price issues, <n> compliance issues.">
<Short table of issues only (not every SKU):>
| SKU | channel | pincode | issue | before → after |
|---|---|---|---|---|
<Search rank: keywords that moved ≥ threshold, one line each.>

## Reviews and sentiment (B)
<If review themes could not be collected this run, say so plainly and why. Otherwise a short paragraph on the biggest themes, then:>
- New reviews since yesterday: <n> (<n> negative), by channel.
- Top complaint themes (7-day): <theme (count) per SKU>.
- Rating changes: <SKU / channel: 4.3 → 4.2>.

## Mentions (C)
- <n> mentions yesterday (<n> negative), <n> creator posts this week.
- Notable: <one line each with link>.

## SEO / web (D)
- Clicks (7-day): <n> (<±%> vs previous). Branded <n> (<±%>), non-branded <n> (<±%>). Data through <date>.
- Keywords that moved: <keyword: 6 → 11>.
- Broken pages / collections: <path: status or "0 products">.

## Detail tables
<Paste the output of `python scripts/detail_tables.py daily --data $DATA` here, unedited: every listing by channel
(stock, MRP, price, discount, price vs yesterday, rating, reviews, link), search rank by keyword with movement, and
mentions found. It is built from the snapshots, so do not retype or summarise it.>

## Data freshness
| module | status | snapshot date | rows | note |
|---|---|---|---|---|

## Config gaps
<TODO items from config.md that limited this run. Omit if none.>

## Appendix
<Full flagged-change list from the diff script, grouped by module, and the snapshot sheet link.>
```

## Style

- Lead with the change and where it is; numbers with units and direction (₹199 → ₹229, +15%).
- Leave out sections for modules that are off. Show "not connected" modules only in Data freshness.
- No recommendations unless config Report mode is `report + recommendations`; in that mode add a `Suggested next step:` line under each attention item.
- First run (no baseline): replace "Needs attention today" with "Baseline: current issues" and list absolute problems that exist right now (out of stock, above MRP, broken pages, non-compliant listings). These matter even without a comparison.
