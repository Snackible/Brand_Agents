# Daily report template

Two parts. The **written part** (about 350 to 650 words) is readable in two to three minutes: a row of headline numbers, then the items that need attention, then a few bullets per module. The **detail part** is full tables for looking things up. Nothing is lost by keeping the written part tight, because every number is in the detail tables. Written part first; detail after config gaps.

**Make it snappy.**
- Bullets, not paragraphs. One idea per bullet, 25 words or fewer, starting with a bold lead-in (SKU, channel or topic).
- Number and change first (₹65 → ₹74, +14%), context second, link last.
- Do not repeat what a detail table already shows (search ranks, every listing). Name only the movers and point to the table.
- Say each caveat once (under the title or in Config gaps), not inside every bullet.
- Still give SKU and pack, channel, before → after and the link for every flagged item, with one line of context (how long, whether it recurs).

```markdown
# Brand Health: <Day, d Mon YYYY>

_Compared with snapshot of <previous date>. Modules: <n> ok, <n> partial, <n> not connected. <One short caveat line if needed.>_

## At a glance
<A table of 4 to 6 headline numbers: first row is the label, second row is the value. Plain th and td. For example:>
| In stock on snackible.com | Amazon avg rating | Out of stock | Price moves of 5% or more | New mentions |
|---|---|---|---|---|
| 97 of 99 | 3.91 | 2 | 2 | 1 |

## Needs attention today
<0–5 numbered items, ranked by urgency × revenue impact. Each: one bold sentence with SKU, channel
(and pincode if relevant) and the change, then one short sentence of context, then the link. Two lines at most.
Merge related signals across modules into one item.
If nothing qualifies, write: "Nothing needs attention today.">

1. **<SKU> out of stock on Blinkit in 3 of 4 Bengaluru pincodes (was in stock yesterday).** Also 2 "not available" complaints since yesterday. [source](url)

## Listing health (A)
<Three to five bullets: stock by channel, price moves, ratings below the threshold, anything above MRP.>
<Search rank: one bullet per channel naming only the keywords that moved or were lost; the full list is in the Search rank table.>

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
