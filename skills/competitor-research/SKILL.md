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
- `scripts/collectors/` — headless collectors and the Chrome importer; `scripts/chrome/extract_qc.js` — in-page extractor run through Claude in Chrome.
- `scripts/digest.py` — one-command summary of a run (what changed, freshness, attention candidates). Read this instead of querying the CSVs.
- `references/first-run-setup.md` — one-time setup: preflight, recipients, schedule. Read only on a first run.
- `scripts/preflight.py` — checks a new environment and says exactly what to fix; `assets/Setup_Guide.pdf` — the setup guide to give the person installing this in another Claude.
- `scripts/diff_snapshots.py` — compares the current snapshot to the previous one using the thresholds in `config.md`.

## 0. First run in a new environment

If this is the first run here, or the saved delivery settings (section 6) cannot be found, read `references/first-run-setup.md` before collecting: it has the preflight check, the one-time recipients and schedule questions, and how to create the automatic run. Otherwise skip it. Assume the person is not technical: plain words, one step at a time.

## 1. Load config

Read `config.md`. Note:
- Which modules are `on`, `off` or `needs feed` (a module marked `needs feed` depends on a data source that isn't connected yet, such as the shared scrape; don't try to improvise it with ad-hoc scraping, report it as not connected).
- Any entries still marked `TODO`. Don't invent values for them. Run with what is confirmed and list the gaps under "Config gaps" at the end of the report so the owner can fix them.
- The report week: Monday–Sunday of the week that just ended, unless the user names a different period.

## 2. Collect

Snapshots live in a data folder, one subfolder per run date: `data/competitor/<YYYY-MM-DD>/`, one CSV per collector. In the project repo that is `data/competitor/` at the repo root; if the skill is installed on its own, use `./data/competitor/` in the working directory. Call it `$DATA` below.

**Step A: headless collectors (one command).** Run from the skill folder:

```bash
python scripts/collectors/run_headless.py weekly --config config.md --data $DATA
```

This collects D2C catalogues and prices (Shopify feeds), Amazon.in listings, prices, ratings and review counts for each brand, and active Meta ads with days live, hooks and offers. It takes several minutes. Read `$DATA/<date>/_run.json`: any collector marked `ok: false` is a failed module for the data-freshness section. Rows with metric `_collection_status` inside the CSVs are partial or failed sources; carry them into the report too.

**Step B: quick commerce through Claude in Chrome.** Blinkit and Zepto block scripts but load in the person's own Chrome. If Claude in Chrome is not connected, skip this step and report these channels as not connected. Otherwise, for each channel marked `chrome` in `config.md` (Instamart is off by default), do this once per channel, not once per keyword:
1. Open the first query's search page (`https://blinkit.com/s/?q=<query>` or `https://www.zeptonow.com/search?query=<query>`), wait about 5 seconds, and `find` the page's search box to get its ref.
2. Run the contents of `scripts/chrome/extract_qc.js` with `window.__qcBrands = [the competitor brands from `config.md`]; window.__qcFrom = 0;` in front. It defines `window.__qc()` and reads the page on screen.
3. For every other query, in ONE `browser_batch` call: triple-click the search box ref, type the query, press Return, wait 4 seconds, run `window.__qc()` and then `window.__qc2()` (which returns the rest if the first result was cut short, otherwise just `{"done":true}`). Repeat that group for each query. Never reload or navigate to a new URL in between: that loses the function, whereas typing in the site's own search box does not.
4. Save every response for the channel in ONE file, `$DATA/<date>/chrome/<channel>.json`, as a JSON list. A `total` of 0 means that page failed (a larger `total` with no items just means none of the tracked brands appeared). If a response ends in `[TRUNCATED]`, set `window.__qcFrom` to its `from` and call `window.__qc()` again.
5. Import: `python scripts/collectors/chrome_import.py competitors --config config.md --out $DATA/<date>/quick_commerce.csv $DATA/<date>/chrome/*.json`
Use the queries in `config.md` (at most 5 per channel). Prices are for the location the browser has set; say so in the report. Never enter credentials, one-time codes or addresses, and stop and tell the person if a CAPTCHA or sign-in wall blocks you.

**Step C: Instagram followers through Claude in Chrome.** For each competitor with an Instagram handle in `config.md`, open `https://www.instagram.com/<handle>/` and read the follower count from the page text ("430K followers"). Write rows `content | <brand> | followers | <number>` to `$DATA/<date>/instagram.csv` (snapshot schema, `source` = Instagram). Only the public profile is readable without a login, so post cadence and engagement are collected only through step C2, and only if Chrome is already signed in to Instagram. Never sign in yourself.

**Step C2: sources behind a login, using the person's own Chrome session.** Competitor Instagram posts and Amazon review pages need a signed-in session. The agent never signs in by itself: it reuses a session that Chrome already holds, and says so when there is none.
1. For each such site (`config.md` marks them `chrome, if signed in`), open one of its pages in Claude in Chrome and run `scripts/chrome/check_login.js`. It only reports whether a "Log in" prompt is showing.
2. If `signedIn` is `true`, collect with that session by reading the page text: for Instagram, open each competitor's profile and its latest few posts and record likes and comments to work out engagement; for Amazon, open `https://www.amazon.in/product-reviews/<ASIN>/` with the critical-reviews filter for each brand's top listings and tag complaint themes as described under `reviews` in `references/modules.md`. Keep it small and slow (a few pages per site, with pauses between them), and treat anything you cannot read as not collected.
3. If `signedIn` is `false` or `null`, do not try to sign in. Write a `_collection_status` row with value `needs_login` that names the site, and carry on with the other sources.
4. If a person is present, tell them which sites need a sign-in and ask them to sign in themselves in the Chrome window. They must never give you a password or a code. Wait until they say it is done, then run the check again. If the site offers "Continue with Google" and the person says yes for that site in this run, you may click that button and let them approve Google's own screen; do not do this without a yes for that specific site in this run. Never use saved passwords or autofill, and never accept a browser prompt to save or fill credentials.
5. If this is an unattended scheduled run, never attempt a sign-in. List the sites that need one in the report's data-freshness section and config gaps, so someone present can fix it. Sessions expire, so a site that worked last week may need signing in again.

**Step D: web research (news, claims, gifting).** Follow the news, claims and gifting sections of `references/modules.md` using web search and page reads, and write the rows to `$DATA/<date>/manual.csv` using the snapshot schema. Claims can also be read from the D2C/Amazon titles already collected.

General rules:
- **Prefer official and existing sources** (Meta Ad Library, brand feeds). Do not try to get around bot checks, CAPTCHAs or login walls; record the module as failed or partial and move on.
- **Capture a source URL for every row.** The report links to evidence.
- **Record what you observed, not what you infer.** A page that did not load is a collection failure, not a change.
- Keep a short collection log for the data-freshness section.

## 3. Store the snapshot

The files from step 2 in `$DATA/<date>/` are the snapshot; there is nothing to upload for the diff to work. Check that every file uses the columns in `references/snapshot-schema.md`. If the team also wants the Google Sheet, append the same rows there as a second copy, but the CSV folder stays the source of truth.

## 4. Diff against last week

**Start with the digest.** Run `python scripts/digest.py weekly --data $DATA`. It compares the newest snapshot folder with the one before it and prints a short, capped summary: data freshness, what changed, and candidates for the attention section. Read that instead of querying the CSVs yourself, which costs far more and is easy to get wrong. Use `scripts/diff_snapshots.py` below only if you need the full threshold-based list of changes.

Run the diff over every snapshot folder (it compares the latest date with the one before it, per module):

```bash
python scripts/diff_snapshots.py --config config.md $DATA/*/*.csv
```

Add `--format json` for structured output. The script reports, per module: status (ok / first snapshot / possibly partial), new entities, removed entities, and metric changes that crossed a threshold in `config.md`. Sub-threshold changes are counted, not listed, to keep the weekly read short. Note that Amazon and quick-commerce results are search results, so a "removed" listing there means it dropped out of the results, not necessarily that it was delisted; say so rather than reporting a delisting.

Then add judgment on top of the script output:
- **Text modules** (news, claims, gifting, ad hooks) mostly show up as "new entity" rows. Read them and decide which matter for Snackible.
- **Cross-module patterns** are the most useful part of the report: e.g. a competitor launching a SKU, running new ads for it and cutting its price in the same week is one story, not three bullets.
- On the **first run** there is no baseline. Say so plainly, report the current state as a baseline, and keep it short.

## 5. Write the report

**Write the report once, as the HTML you will pass to Google Docs** (`h1`, `h2`, `h3`, `ul`, `ol`, `table`, `a`). The email body is its top section as plain text. Do not also write a Markdown copy unless Drive is unavailable.

Follow `references/report-template.md` exactly. The main principles, so you can handle cases the template doesn't cover:

- **Lead with what changed and matters.** The reader is a marketer with five minutes. The top section is the 3–7 changes worth acting on or knowing, ranked by likely impact on Snackible.
- **Every claim links to its source.**
- **Health and nutrition claims are observations only.** Report what a competitor states on its pack or listing, verbatim where short, with the link. Don't assess whether a claim is valid, and don't suggest claims Snackible could make: Snackible's own claims are reviewed by the team, not by this report.
- **Report or recommend** depends on `config.md` → `Report mode`. In `report only` mode (the default), describe changes and why they might matter, but don't add a "Recommended actions" section.
- **Always include the data-freshness section**, listing each module's status. Missing data is flagged, never papered over.

## 6. Deliver

Recipients and the schedule are asked for once and then remembered. Whoever installs this skill in a new Claude is asked a single time; after that the agent runs by itself on schedule, creates the Doc and emails it, with no further questions.

Delivery settings live in the Drive file `Snackible Agents Settings: competitor_weekly` (newest file wins). If it is missing and a person is present, do the first-run setup in `references/first-run-setup.md` now; if the run is unattended, do not email anyone and save the report as a file instead.

### Each run

Every run after setup, scheduled or not:
1. Create a Google Doc titled `Competitor Weekly: W<ISO week> <YYYY> (<Mon d> - <Sun d>)` (in `folder_id` if set) containing the report.
2. **Share the Doc** with each recipient as a viewer (Drive `share_file`), so the emailed link opens for them. The Doc stays private to everyone else.
3. **Email** with Gmail: if `mode` is `send`, `send_message` to the saved recipients; if `draft`, `create_draft` and say it is waiting. Subject: the Doc title. Body: the "Top changes" (or "Baseline: what stands out" on the first run) section as plain text plus the Doc link. No attachments and no raw data. Send only to the saved addresses (no extra Cc or Bcc).
4. If Docs, Drive sharing or Gmail is unavailable, write the report as Markdown, save `competitor_weekly_<YYYY-MM-DD>.md`, and say which delivery steps did not happen. Do not send a partial or unsourced report.

Finish by telling the person running it: the Doc link, who it was sent to (or that a draft is waiting), the snapshot status, and any config gaps.
