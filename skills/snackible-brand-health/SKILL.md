---
name: snackible-brand-health
description: Daily Snackible brand health report for Marketing. Checks Snackible's own listings (stock, price vs MRP parity, title/image compliance, rating, review count and search rank by SKU × channel × pincode), new reviews and complaint themes (Amazon, quick commerce, D2C, Google), unprompted mentions and creator posts (Instagram, Reddit, X, YouTube), and SEO / web health (GSC clicks, branded vs non-branded, keyword ranks, broken collections). Stores a dated snapshot, compares with yesterday and writes a short report led by "Needs attention today", delivered as a Google Doc plus email draft. Use this whenever someone asks for the daily brand health report, how Snackible's listings, ratings, reviews, mentions or SEO are doing, whether any SKU is out of stock or mispriced, or when the daily scheduled run fires — even if they don't name the skill.
---

# Snackible Brand Health (daily)

You produce Snackible Marketing's daily brand health report. It is read quickly, every morning, so the job is to separate the few things that **need attention today** from the steady state. That only works with history: each run stores a dated snapshot and compares it to the previous day.

Spine of every run:

1. **Load config** → 2. **Collect** → 3. **Store snapshot** → 4. **Diff against yesterday** → 5. **Write report** → 6. **Deliver**

Don't skip step 3: tomorrow's report depends on today's snapshot.

## Files in this skill

- `config.md` — SKUs, channels, pincodes, tracked keywords, data feeds, module status, thresholds, sheet location, recipients. Read it first, every run. The team edits this file.
- `references/modules.md` — per module (A listing health, B reviews, C mentions, D SEO): what to collect, sources, row naming, gotchas. Read the sections you are running.
- `references/report-template.md` — the exact report structure.
- `references/snapshot-schema.md` — snapshot sheet layout and conventions.
- `scripts/diff_snapshots.py` — compares the current snapshot with the previous one using the thresholds in `config.md`.

## 1. Load config

Read `config.md`. Note which modules are `on`, `off` or `needs feed`, and any `TODO` entries. Don't invent SKUs, pincodes or keywords. Run with what is confirmed and list gaps under "Config gaps" at the end of the report.

The report date is today; the comparison is the most recent earlier snapshot (normally yesterday; after a weekend or outage it may be older, so say which date you compared against).

## 2. Collect

Build order from the plan, which is also the reliability order: **B reviews and D SEO** (easiest to source), then **C mentions**, then **A listing health** (heaviest: SKU × channel × pincode, needs a dependable feed). Follow each module's section in `references/modules.md`.

General rules:
- **Use connected feeds and official sources first**: GSC, the shared scrape, platform seller dashboards or exports, listening-tool exports. Daily ad-hoc scraping of quick-commerce sites is fragile and often blocked, so if a module needs a feed that isn't connected, report it as "not connected" instead of improvising.
- **Every row gets a source URL or source name.**
- **Record observations, not inferences.** If a page failed to load, that's a collection failure row, not "out of stock". Confusing the two would send the team chasing a stock-out that doesn't exist.
- Keep a short collection log (module, sources, rows, failures) for the data-freshness section.

## 3. Store the snapshot

Append today's rows to the snapshot sheet named in `config.md` per `references/snapshot-schema.md` (one tab per module, long format). If the sheet can't be written, save `brand_health_snapshot_<YYYY-MM-DD>.csv`, attach or link it, and say so at the top of the report.

## 4. Diff against yesterday

Export the relevant tabs as CSV (at least the previous and current snapshot) and run:

```bash
python scripts/diff_snapshots.py --config config.md <tab CSVs...>
```

The script lists new and removed entities and threshold-crossing changes per module, and counts sub-threshold changes without listing them.

Then apply judgment:
- **Decide what goes in "Needs attention today".** Include something there only if someone on the team should do something today: a top SKU out of stock on a major channel, a price above MRP or broken parity, a rating drop, a cluster of complaints on the same theme, a negative mention gaining traction, a broken collection page, a sharp drop in non-branded clicks. Rank by revenue impact and urgency. If nothing qualifies, say "Nothing needs attention today" — that is a useful report, not a failure.
- **Connect signals.** A stock-out on Blinkit plus "not available" complaints plus a rank drop is one item.
- **Smooth daily noise.** SEO and mention metrics swing day to day; the config stores 7-day rolling values for exactly this reason. Don't call a one-day wobble a trend.

## 5. Write the report

Follow `references/report-template.md`. Principles:
- **Short.** "Needs attention today" first, at most ~5 items, then one compact section per module, then data freshness. Detail stays in the sheet.
- **Specific.** SKU, channel, pincode, before → after, link.
- **Claims and compliance**: flag title/image compliance issues on Snackible's listings as observed facts against the configured rules. Don't rewrite or propose health claims; the team reviews Snackible's claims.
- **Report mode** from config: in `report only` mode, describe the issue and its impact but don't prescribe actions.
- **Always include data freshness** for each module (ok / partial / failed / not connected) with the snapshot date. Never present stale data as today's.

## 6. Deliver

Per `config.md` → Delivery:
1. Create a Google Doc titled `Brand Health — <Day, d Mon YYYY>` in the configured folder.
2. Draft an email (or message) to the recipients: subject = Doc title plus `(<n> need attention)`, body = the "Needs attention today" section plus the Doc link.
3. Send only if `Auto-send` is `yes`; otherwise leave it as a draft and say so.

If Docs or email aren't available, output the report as Markdown, save `brand_health_<YYYY-MM-DD>.md`, and state which delivery steps didn't happen.

Finish by telling the person running it: the Doc link (or file), draft or sent status, snapshot status, number of attention items, and config gaps.
