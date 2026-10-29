# Snapshot sheet schema

The snapshot sheet is the source of truth and the history. One Google Sheet, **one tab per module** (tab name = module name: `news`, `claims`, `gifting`, `paid_ads`, `content`, `content_posts`, `reviews`, `sku_tracker`, `price`, plus `_runs`).

## Columns (every module tab)

| column | required | meaning |
|---|---|---|
| snapshot_date | yes | Run date, `YYYY-MM-DD`. The same for every row in one run. |
| module | yes | Module name, same as the tab name. |
| entity | yes | What the row is about, e.g. `Happilo \| Peri Peri Makhana 75g \| Amazon.in`. Must be stable week to week. |
| metric | yes | What is measured, e.g. `selling_price`, `days_live`, `claim`. |
| value | yes | Number (no ₹ or % signs) or short text. |
| unit | no | `INR`, `g`, `%`, `days`, `count`, or blank for text. |
| source | no | Short source name: `Meta Ad Library`, `brand site`, `Amazon.in`, `shared scrape`. |
| source_url | no, but expected | Link to the evidence. |
| notes | no | Anything a reader needs: partial data, second source, pincode. |

Long format (one metric per row) keeps every tab the same shape, so the diff script works on all of them and new metrics can be added without changing columns.

## Rules

- **Append, never overwrite.** Each run adds rows with a new `snapshot_date`. Old rows are the history.
- **Write the snapshot before writing the report.**
- **Numbers as plain numbers**: `249`, not `₹249`; `12.5`, not `12.5%`.
- **Collection failures are rows too.** If a source failed for an entity, add a row with metric `_collection_status`, value `failed` or `partial`, and the reason in `notes`. This keeps "we couldn't see it" distinct from "it disappeared".

## `_runs` tab

One row per run: `run_date, report_period, modules_run, modules_failed, rows_written, report_link, notes`. This gives the team a quick audit trail and lets the next run find the previous snapshot date.

## Example rows

```
snapshot_date,module,entity,metric,value,unit,source,source_url,notes
2026-10-26,paid_ads,Farmley,active_ads,14,count,Meta Ad Library,https://www.facebook.com/ads/library/?...,
2026-10-26,paid_ads,Farmley | 1234567890,days_live,9,days,Meta Ad Library,https://www.facebook.com/ads/library/?id=1234567890,
2026-10-26,paid_ads,Farmley | 1234567890,hook,"Diwali gifting that isn't mithai",,Meta Ad Library,https://www.facebook.com/ads/library/?id=1234567890,video
2026-10-26,news,Happilo | new-gcc-distribution,headline,Happilo announces distribution deal in UAE,,Inc42,https://inc42.com/...,
2026-10-26,claims,The Whole Truth | Protein Bar Coffee Cocoa | no added sugar,claim,No added sugar,,brand site,https://thewholetruthfoods.com/...,pack front
```
