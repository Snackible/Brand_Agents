---
name: competitor-research
description: Weekly competitor research report for Snackible Marketing. Collects what changed across competing snack brands (new or delisted SKUs, price per 100g, Meta ads and offers, Instagram content, new health claims, Diwali/corporate gifting moves, Amazon review complaints, funding and distribution news), stores a dated snapshot, compares it to last week and writes a "what changed" report as a Google Doc plus an email draft. Use this whenever someone asks for the weekly competitor report, a competitor scan or update, "what are competitors doing", competitor ads/pricing/launches/claims for a brand like Farmley, Happilo or The Whole Truth, or when the weekly scheduled run fires — even if they don't say "skill" or "report".
---

# Competitor Research (weekly)

You produce Snackible Marketing's weekly "what changed across competitors" report. The report is only valuable if it shows *change*, and change only exists if last week's snapshot was stored. So every run has the same spine:

1. **Load config** → 2. **Collect** → 3. **Store snapshot** → 4. **Diff against last week** → 5. **Write report** → 6. **Deliver**

Never skip step 3 to save time: a report without a stored snapshot makes next week's report impossible.

## Files in this skill

- `config.md` — competitors, channels, which modules are on, thresholds, snapshot sheet location, recipients. Read it first, every run. The Marketing team edits this file, not SKILL.md.
- `references/modules.md` — for each module: what to collect, where, how to name rows, and known gotchas. Read the section for each module you are running.
- `references/report-template.md` — the exact report structure. Read before writing the report.
- `references/snapshot-schema.md` — the snapshot sheet layout and row conventions. Read before writing or reading snapshot rows.
- `scripts/diff_snapshots.py` — compares the current snapshot to the previous one using the thresholds in `config.md`.

## 1. Load config

Read `config.md`. Note:
- Which modules are `on`, `off` or `needs feed` (a module marked `needs feed` depends on a data source that isn't connected yet, such as the shared scrape; don't try to improvise it with ad-hoc scraping, report it as not connected).
- Any entries still marked `TODO`. Don't invent values for them. Run with what is confirmed and list the gaps under "Config gaps" at the end of the report so the owner can fix them.
- The report week: Monday–Sunday of the week that just ended, unless the user names a different period.

## 2. Collect

For each module that is `on`, follow its section in `references/modules.md`. General rules:

- **Prefer official and existing sources** (Meta Ad Library, brand sites, the shared scrape) over aggressive scraping. Platform terms matter and fragile scraping produces noise.
- **Capture a source URL for every row.** The report links to evidence; a claim without a link is not useful to the team.
- **Record what you observed, not what you infer.** If a page didn't load or a search returned nothing, record that as a collection failure (see snapshot schema), don't fill the gap with a guess. A wrong "competitor dropped prices" line costs more than a missing one.
- If the browser or web tools can't reach a source (quick-commerce sites often block automated access), mark the module `partial` or `failed` and move on.

Keep a short collection log as you go: module, sources tried, rows collected, failures. It feeds the data-freshness section.

## 3. Store the snapshot

Write the collected rows to the snapshot sheet named in `config.md`, following `references/snapshot-schema.md` (one tab per module, long format: `snapshot_date, module, entity, metric, value, unit, source, source_url, notes`). Use today's run date as `snapshot_date` for every row in this run.

If you can't write to the sheet (no Google Sheets access in this session, permission error), save the rows as `competitor_snapshot_<YYYY-MM-DD>.csv`, attach or link it in the delivery, and put "Snapshot not saved to the sheet. Rows attached, please paste them into the sheet" at the top of the report. Don't silently drop the snapshot.

## 4. Diff against last week

Export the snapshot tabs (or read them) as CSV including at least the previous snapshot and the current one, then run:

```bash
python scripts/diff_snapshots.py --config config.md <tab CSVs...>
```

Add `--format json` if you want structured output. The script reports, per module: status (ok / first snapshot / possibly partial), new entities, removed entities, and metric changes that crossed a threshold. Changes below threshold are only counted, not listed, which is deliberate: they are noise for a weekly read.

Then add judgment on top of the script output:
- **Text modules** (news, claims, gifting, ad hooks) mostly show up as "new entity" rows. Read them and decide which matter for Snackible.
- **Cross-module patterns** are the most useful part of the report: e.g. a competitor launching a SKU, running new ads for it and cutting its price in the same week is one story, not three bullets.
- On the **first run** there is no baseline. Say so plainly, report the current state as a baseline, and keep it short.

## 5. Write the report

Follow `references/report-template.md` exactly. The main principles, so you can handle cases the template doesn't cover:

- **Lead with what changed and matters.** The reader is a marketer with five minutes. The top section is the 3–7 changes worth acting on or knowing, ranked by likely impact on Snackible.
- **Every claim links to its source.**
- **Health and nutrition claims are observations only.** Report what a competitor states on its pack or listing, verbatim where short, with the link. Don't assess whether a claim is valid, and don't suggest claims Snackible could make: Snackible's own claims are reviewed by the team, not by this report.
- **Report or recommend** depends on `config.md` → `Report mode`. In `report only` mode (the default), describe changes and why they might matter, but don't add a "Recommended actions" section.
- **Always include the data-freshness section**, listing each module's status. Missing data is flagged, never papered over.

## 6. Deliver

Per `config.md` → Delivery:
1. Create a Google Doc titled `Competitor Weekly — W<ISO week> <YYYY> (<Mon d>–<Sun d>)` in the configured folder, containing the report.
2. Draft an email (or message) to the configured recipients: subject = Doc title, body = the "Top changes" section plus the Doc link.
3. Send it only if `Auto-send` is `yes` in config. Otherwise leave it as a draft and say so. Auto-send stays off until the team has reviewed a few manual runs.

If Google Docs or email isn't available in this session, write the report as Markdown in the response and save it as `competitor_weekly_<YYYY-MM-DD>.md`, and say which delivery steps didn't happen.

Finish by telling the person running it: the Doc link (or file), the draft or sent status, the snapshot status, and any config gaps.
