# Snapshot sheet schema

One Google Sheet, **one tab per module**: `listing`, `search_rank`, `reviews`, `mentions`, `mention_items`, `seo`, `seo_keywords`, plus `_runs`.

## Columns (every module tab)

| column | required | meaning |
|---|---|---|
| snapshot_date | yes | Run date `YYYY-MM-DD`, the same for all rows in a run. (For GSC rows, put the data date in `notes`.) |
| module | yes | Module name, same as the tab. |
| entity | yes | e.g. `Peri Peri Makhana 75g \| Blinkit \| 560102`. Stable day to day. |
| metric | yes | e.g. `in_stock`, `rating`, `clicks_7d`. |
| value | yes | Plain number (no ₹ or %) or short text. Booleans as `1` / `0`. |
| unit | no | `INR`, `%`, `count`, `position`, blank for text. |
| source | no | `shared scrape`, `Amazon.in`, `GSC`, `Reddit search`… |
| source_url | no, expected | Link to the evidence. |
| notes | no | Partial data, reason for non-compliance, data date. |

## Rules

- **Append, never overwrite.** History is what makes the diff possible.
- **Write the snapshot before the report.**
- **Collection failures are rows**: metric `_collection_status`, value `failed` / `partial`, reason in `notes`. This keeps "couldn't load" separate from "out of stock" or "removed".
- Keep only what the report needs; with SKU × channel × pincode the listing tab grows fast. If it gets large, the team can archive older months to a separate sheet. The diff only needs the last two snapshots.

## `_runs` tab

`run_date, compared_with, modules_run, modules_failed, rows_written, attention_items, report_link, notes`

## Example rows

```
snapshot_date,module,entity,metric,value,unit,source,source_url,notes
2026-10-29,listing,Peri Peri Makhana 75g | Blinkit | 560102,in_stock,0,,shared scrape,,shows "notify me"
2026-10-29,listing,Peri Peri Makhana 75g | Amazon.in | all,selling_price,179,INR,Amazon.in,https://www.amazon.in/dp/...,
2026-10-29,reviews,Peri Peri Makhana 75g | Amazon.in | theme:stale/rancid,count_7d,3,count,Amazon.in,https://www.amazon.in/product-reviews/...,"tasted old, packet date fine"
2026-10-29,seo,site,nonbranded_clicks_7d,4120,count,GSC,,data through 2026-10-27
2026-10-29,mention_items,Reddit | r/IndianFood/abc123,sentiment,negative,,Reddit search,https://www.reddit.com/r/IndianFood/comments/abc123,
```
