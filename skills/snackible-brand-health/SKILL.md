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
- `scripts/collectors/` — headless collectors and the Chrome importer; `scripts/chrome/extract_qc.js` — in-page extractor run through Claude in Chrome.
- `scripts/digest.py` — one-command summary of a run (what changed, freshness, attention candidates). Read this instead of querying the CSVs.
- `references/first-run-setup.md` — one-time setup: preflight, recipients, schedule. Read only on a first run.
- `scripts/preflight.py` — checks a new environment and says exactly what to fix; `assets/Setup_Guide.pdf` — the setup guide to give the person installing this in another Claude.
- `scripts/diff_snapshots.py` — compares the current snapshot with the previous one using the thresholds in `config.md`.

## 0. First run in a new environment

If this is the first run here, or the saved delivery settings (section 6) cannot be found, read `references/first-run-setup.md` before collecting: it has the preflight check, the one-time recipients and schedule questions, and how to create the automatic run. Otherwise skip it. Assume the person is not technical: plain words, one step at a time.

## 1. Load config

Read `config.md`. Note which modules are `on`, `off` or `needs feed`, and any `TODO` entries. Don't invent SKUs, pincodes or keywords. Run with what is confirmed and list gaps under "Config gaps" at the end of the report.

The report date is today; the comparison is the most recent earlier snapshot (normally yesterday; after a weekend or outage it may be older, so say which date you compared against).

## 1b. Stop and ask when you need the person

Never skip a source silently and never work around a block. Whenever a step needs something only a person can do, stop, say in plain words exactly what to do, and wait for their reply before going on. Ask again on every run: an earlier "skip" does not carry over.

**Up front, in one message, before collecting** (use the question tool if this Claude has one, otherwise plain text; offer "I've done it" and "Skip this time" for each item):
- Claude in Chrome connected and responding (needed for Blinkit and Zepto).
- Signed in, in that Chrome, to each login-gated site in `config.md` (Amazon). Open one page of the site and run `scripts/chrome/check_login.js`; never sign in yourself.
- Google Drive and Gmail connected (needed to create and send the report).
- Anything listed in `$DATA/pending_actions.md` from an earlier unattended run.
Wait for the answer, re-check whatever they say they did, and only then collect. If they skip something, mark that module `needs_login` or not connected in the report; do not guess.

**Mid-run blockers** (a CAPTCHA, a sign-in wall that appears, a site refusing the page, a connector or Chrome dropping out): stop at that moment, say what happened and what to do, and wait.

**Unattended runs (started by a schedule):** nobody can answer, so do not wait and do not hang. Skip what is blocked, put a "Needs your help" box at the top of the report listing exactly what to do, start the email subject with `ACTION NEEDED: `, append the same list to `$DATA/pending_actions.md` (one line per item, with the date), and send a push notification if that tool exists. The next attended run asks about those first. Remove a line once it is done.

## 2. Collect

Snapshots live in a data folder, one subfolder per run date: `data/brand_health/<YYYY-MM-DD>/`, one CSV per collector. In the project repo that is `data/brand_health/` at the repo root; if the skill is installed on its own, use `./data/brand_health/` in the working directory. Call it `$DATA` below.

**Step A: headless collectors (one command).** Run from the skill folder:

```bash
python scripts/collectors/run_headless.py daily --config config.md --data $DATA
```

This collects: the whole snackible.com catalogue (stock, price, MRP), Snackible's Amazon.in listings (price, MRP, rating, review count), Amazon keyword ranks for the tracked keywords, and public YouTube mentions. Read `$DATA/<date>/_run.json`: a collector with `ok: false` is a failed module for the data-freshness section, and `_collection_status` rows inside the CSVs mark partial or failed sources. Reddit, X and Instagram mentions need a login and are reported as not connected.

**Step B: quick commerce through Claude in Chrome.** Blinkit and Zepto block scripts but load in the person's own Chrome. If Claude in Chrome is not connected, handle it as in section 1b (ask the person to open Chrome with the extension and wait; if they skip, or the run is unattended, report these channels as not connected). Otherwise, for each channel marked `chrome` in `config.md` (Instamart is off by default), do this once per channel, not once per keyword:
1. Open the first query's search page (`https://blinkit.com/s/?q=<query>` or `https://www.zeptonow.com/search?query=<query>`), wait about 5 seconds, and `find` the page's search box to get its ref.
2. Run the contents of `scripts/chrome/extract_qc.js` with `window.__qcBrands = ["Snackible"]; window.__qcFrom = 0;` in front. It defines `window.__qc()` and reads the page on screen.
3. For every other query, in ONE `browser_batch` call: triple-click the search box ref, type the query, press Return, wait 4 seconds, run `window.__qc()` and then `window.__qc2()` (which returns the rest if the first result was cut short, otherwise just `{"done":true}`). Repeat that group for each query. Never reload or navigate to a new URL in between: that loses the function, whereas typing in the site's own search box does not.
4. Save every response for the channel in ONE file, `$DATA/<date>/chrome/<channel>.json`, as a JSON list. A `total` of 0 means that page failed (a larger `total` with no items just means none of the tracked brands appeared). If a response ends in `[TRUNCATED]`, set `window.__qcFrom` to its `from` and call `window.__qc()` again.
5. Import: `python scripts/collectors/chrome_import.py own --brand Snackible --config config.md --out $DATA/<date>/quick_commerce.csv $DATA/<date>/chrome/*.json`
Search the `own` and `test` keywords from `config.md`, at most 6 per channel; skip the `block` keywords on delivery apps. Prices are for the location the browser has set; say so in the report. Never enter credentials, one-time codes or addresses, and stop and tell the person if a CAPTCHA or sign-in wall blocks you.

**Step C: reviews.** Rating and review count per listing come from step A. For complaint themes, open the Amazon review pages of the top Snackible listings in Chrome only if the person is already signed in to Amazon; otherwise report themes as not collected. Follow the reviews section of `references/modules.md`, and write rows to `$DATA/<date>/manual.csv`.

**Step C2: sources behind a login, using the person's own Chrome session.** Amazon review pages (complaint themes for Snackible's listings) need a signed-in session. The agent never signs in by itself: it reuses a session that Chrome already holds, and says so when there is none.
1. For each such site (`config.md` marks them `chrome, if signed in`), open one of its pages in Claude in Chrome and run `scripts/chrome/check_login.js`. It only reports whether a "Log in" prompt is showing.
2. If `signedIn` is `true`, collect with that session by reading the page text: open `https://www.amazon.in/product-reviews/<ASIN>/` with the critical-reviews filter for Snackible's most-reviewed listings and tag complaint themes as described under `reviews` in `references/modules.md`. Keep it small and slow (a few pages per site, with pauses between them), and treat anything you cannot read as not collected.
3. If `signedIn` is `false` or `null`, do not try to sign in. Stop and ask as in section 1b. If the person skips, or the run is unattended, write a `_collection_status` row with value `needs_login` that names the site, and carry on with the other sources.
4. If a person is present, tell them which sites need a sign-in and ask them to sign in themselves in the Chrome window. They must never give you a password or a code. Wait until they say it is done, then run the check again. If the site offers "Continue with Google" and the person says yes for that site in this run, you may click that button and let them approve Google's own screen; do not do this without a yes for that specific site in this run. Never use saved passwords or autofill, and never accept a browser prompt to save or fill credentials.
5. If this is an unattended scheduled run, never attempt a sign-in and do not wait: follow the unattended rule in section 1b (Needs your help box, ACTION NEEDED subject, pending_actions.md). Sessions expire, so a site that worked last week may need signing in again.

**Step D: SEO.** Google Search Console is not connected unless `config.md` says a property and feed are set. If it is, follow the seo section of `references/modules.md`; otherwise report SEO as "not connected". Check the main collection pages of snackible.com for status and product count only if you have time; the D2C catalogue already shows missing products.

General rules:
- **Use connected feeds and official sources first.** Do not try to get around bot checks, CAPTCHAs or login walls; mark the module failed or partial and move on.
- **Every row gets a source URL or source name.**
- **Record observations, not inferences.** A page that failed to load is a collection failure, not "out of stock".
- Keep a short collection log for the data-freshness section.

## 3. Store the snapshot

The files from step 2 in `$DATA/<date>/` are the snapshot. Check that every file uses the columns in `references/snapshot-schema.md`. If the team also wants the Google Sheet, append the same rows there as a second copy, but the CSV folder stays the source of truth.

## 4. Diff against yesterday

**Start with the digest.** Run `python scripts/digest.py daily --data $DATA`. It compares the newest snapshot folder with the one before it and prints a short, capped summary: data freshness, what changed, and candidates for the attention section. Read that instead of querying the CSVs yourself, which costs far more and is easy to get wrong. Use `scripts/diff_snapshots.py` below only if you need the full threshold-based list of changes.

```bash
python scripts/diff_snapshots.py --config config.md $DATA/*/*.csv
```

The script compares the latest snapshot date with the one before it, per module, and lists new and removed entities and threshold-crossing changes, and counts sub-threshold changes without listing them.

Then apply judgment:
- **Decide what goes in "Needs attention today".** Include something there only if someone on the team should do something today: a top SKU out of stock on a major channel, a price above MRP or broken parity, a rating drop, a cluster of complaints on the same theme, a negative mention gaining traction, a broken collection page, a sharp drop in non-branded clicks. Rank by revenue impact and urgency. If nothing qualifies, say "Nothing needs attention today". That is a useful report, not a failure.
- **Connect signals.** A stock-out on Blinkit plus "not available" complaints plus a rank drop is one item.
- **Smooth daily noise.** SEO and mention metrics swing day to day; do not call a one-day wobble a trend.
- On the **first run** there is no baseline: use the "Baseline: current issues" form from the report template.

## 5. Write the report

**Write the report once, as the HTML you will pass to Google Docs** (`h1`, `h2`, `h3`, `ul`, `ol`, `table`, `a`). The email body is its top section as plain text. Do not also write a Markdown copy unless Drive is unavailable.

Follow `references/report-template.md`. Principles:
- **Short.** "Needs attention today" first, at most ~5 items, then one compact section per module, then data freshness. Detail stays in the sheet.
- **Specific.** SKU, channel, pincode, before → after, link.
- **Claims and compliance**: flag title/image compliance issues on Snackible's listings as observed facts against the configured rules. Don't rewrite or propose health claims; the team reviews Snackible's claims.
- **Report mode** from config: in `report only` mode, describe the issue and its impact but don't prescribe actions.
- **Always include data freshness** for each module (ok / partial / failed / not connected) with the snapshot date. Never present stale data as today's.

## 6. Deliver

Recipients and the schedule are asked for once and then remembered. Whoever installs this skill in a new Claude is asked a single time; after that the agent runs by itself on schedule, creates the Doc and emails it, with no further questions.

Delivery settings live in the Drive file `Snackible Agents Settings: brand_health_daily` (newest file wins). If it is missing and a person is present, do the first-run setup in `references/first-run-setup.md` now; if the run is unattended, do not email anyone and save the report as a file instead.

### Each run

Every run after setup, scheduled or not:
1. Create a Google Doc titled `Brand Health: <Day, d Mon YYYY>` (in `folder_id` if set) containing the report.
2. **Share the Doc** with each recipient as a viewer (Drive `share_file`), so the emailed link opens for them. The Doc stays private to everyone else.
3. **Email** with Gmail: if `mode` is `send`, `send_message` to the saved recipients; if `draft`, `create_draft` and say it is waiting. Subject: the Doc title plus ` (<n> need attention)`. Body: the "Needs attention today" (or "Baseline: current issues" on the first run) section as plain text plus the Doc link. No attachments and no raw data. If this run left open items for the person (section 1b), start the subject with `ACTION NEEDED: ` and list them at the top of the body. Send only to the saved addresses (no extra Cc or Bcc).
4. If Docs, Drive sharing or Gmail is unavailable, write the report as Markdown, save `brand_health_<YYYY-MM-DD>.md`, and say which delivery steps did not happen. Do not send a partial or unsourced report.

Finish by telling the person running it: the Doc link, who it was sent to (or that a draft is waiting), the snapshot status, the number of attention items, and any config gaps.
