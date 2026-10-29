# Daily report template

Readable in two to three minutes. The top section does the work; everything else is reference. Aim for 300–700 words before the appendix.

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
<One line summary: "<n> SKU × channel combinations checked; <n> out of stock, <n> price issues, <n> compliance issues.">
<Short table of issues only (not every SKU):>
| SKU | channel | pincode | issue | before → after |
|---|---|---|---|---|
<Search rank: keywords that moved ≥ threshold, one line each.>

## Reviews and sentiment (B)
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
