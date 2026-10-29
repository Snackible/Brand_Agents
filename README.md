# Snackible Brand Agents

> **Setting this up for someone?** Give them [the setup guide](docs/Setup_Guide_Adding_the_Agents_to_a_New_Claude.pdf) (plain language, two pages). They paste one message to Claude, and Claude follows [SETUP_FOR_CLAUDE.md](SETUP_FOR_CLAUDE.md) to do every step.

Two Claude agents for Snackible Marketing, built from Snackible Marketing's internal build plan.

| Agent | Skill | Cadence | What it reports |
|---|---|---|---|
| 1. Competitor Research | [`skills/competitor-research`](skills/competitor-research/SKILL.md) | Weekly | What changed across competitors: SKUs, price per 100g, Meta ads, Amazon ratings, quick-commerce prices, claims, gifting, news |
| 2. Snackible Brand Health | [`skills/snackible-brand-health`](skills/snackible-brand-health/SKILL.md) | Daily | Snackible's own listings (stock, price, MRP), keyword rank, ratings, mentions, led by "Needs attention today" |

## How a run works

1. **Headless collectors** (`scripts/collectors/run_headless.py`) pull what can be read without a login: D2C catalogues (Shopify feeds), Amazon.in search pages, the Meta Ad Library, YouTube mentions.
2. **Claude in Chrome** reads what blocks headless access but loads in a normal browser: Blinkit, Zepto and Instamart search pages (via `scripts/chrome/extract_qc.js`, imported with `chrome_import.py`) and Instagram follower counts.
3. **Claude** does the research modules (news, claims, gifting), runs `scripts/diff_snapshots.py` against the thresholds in `config.md`, writes the report, and drafts the Doc and email.

History is stored as dated CSV folders: `data/competitor/<date>/` and `data/brand_health/<date>/`. The diff compares the latest date with the one before it. `data/` is git-ignored (it is scraped data); back it up or sync it if more than one machine runs the agents.

```
skills/<agent>/
├── SKILL.md                       workflow Claude follows
├── config.md                      what the team edits: competitors / keywords, modules on/off, thresholds, recipients
├── references/                    module guides, report template, snapshot schema
└── scripts/
    ├── collectors/                headless collectors, run_headless.py, chrome_import.py
    ├── chrome/extract_qc.js       in-page extractor run through Claude in Chrome
    └── diff_snapshots.py          snapshot comparison (standard library only)
dist/*.skill                       packaged skills, ready to upload
```

## What is connected today

| Source | Status | Notes |
|---|---|---|
| D2C catalogues (Farmley, Happilo, Snackible) | Working | Public Shopify product feeds. The Whole Truth is not Shopify; covered via Amazon. Three competitors have no website in config yet. |
| Amazon.in | Working | Search pages: price, MRP, rating, review count, keyword rank. Delivery location is the machine's default. |
| Meta Ad Library | Working, partial for generic names | Counts ads whose advertiser matches the brand. Open Secret, Yoga Bar and others are flagged `partial` because keyword search is crowded; set a Page ID to tighten it. |
| Blinkit, Zepto | Working through Chrome | Prices are for the location the browser has set (no pincode matrix). |
| Instamart | Working through Chrome | A login prompt can pop up a few seconds after load; the agent reads the page first and does not sign in. |
| YouTube mentions | Working | Public search, undercounts. |
| BigBasket | Not connected | Blocks automated access. Needs the shared scrape. |
| Instagram posts and engagement | Not connected | Needs a login. Public profiles give follower counts only. |
| Reddit, X mentions | Not connected | Reddit blocks the scripted search and the Chrome tool; X needs a login. |
| Google Search Console | Not connected | Needs property access. |
| Amazon review themes | Not collected | Review pages need a signed-in Amazon session. |

The agents never enter passwords, OTPs or CAPTCHAs. For any source behind a login, the person signs in to Chrome themselves once and the agent reuses that session.

## Running it

Install from GitHub: <https://github.com/Snackible/Brand_Agents> (public, no GitHub account needed to download).

1. Download it (**Code, Download ZIP**, or `git clone https://github.com/Snackible/Brand_Agents.git`).
2. From inside the folder: `pip install -r requirements.txt`, then `python -m playwright install chromium`.
3. Open `dist/competitor-research.skill` and `dist/snackible-brand-health.skill` in Claude and click **Save skill**.
4. Enable the Google Drive and Gmail connectors and connect Claude in Chrome, and open the downloaded folder as Claude's working folder.
5. Ask Claude:

- "Run the weekly competitor report"
- "Run the daily brand health report"

Or run only the headless part yourself (after step 2 above):

```bash
python skills/competitor-research/scripts/collectors/run_headless.py weekly --config skills/competitor-research/config.md --data data/competitor
python skills/snackible-brand-health/scripts/collectors/run_headless.py daily --config skills/snackible-brand-health/config.md --data data/brand_health
```

**Recipients are asked once.** The first time an agent runs in a new Claude it asks who should get the report by email, whether to send automatically or leave a draft, and an optional Drive folder. It saves the answer to a Drive file (`Snackible Agents Settings: competitor_weekly` or `...: brand_health_daily`) and never asks again; every later run creates the Doc, shares it with those people as viewers, and emails them. Recipients are only taken from the person's own chat messages. Say "change report recipients" to update them.

**It schedules itself.** The same one-time question asks when to run (default: brand health daily at 08:30, competitor report Mondays at 09:00, local time), and after the person's yes the agent creates the scheduled task, so there is nothing to set up by hand. Scheduled runs never ask questions, and they only happen while the computer is on and the Claude app is open (a missed run happens when the app next opens).

**Setting up another Claude:** give the person [docs/Setup_Guide_Adding_the_Agents_to_a_New_Claude.pdf](docs/Setup_Guide_Adding_the_Agents_to_a_New_Claude.pdf) (it is also bundled in each skill as `assets/Setup_Guide.pdf`). On its first run in any new environment each agent runs `scripts/preflight.py` and lists everything that is missing (Python packages, headless Chromium, a persistent data folder, the Drive, Gmail and Chrome connections) in one message.

The diff needs at least two dates of data before it reports changes; the first run is a baseline.

## Still to decide (marked `TODO` in the two `config.md` files)

- Competitor list (the current list is a draft) with websites and Instagram handles for the three missing ones.
- Which brands on snackible.com count as Snackible's own (the site also lists GoatLife, Bubz, JoySpoon, Gul Jaipur and hampers).
- The tracked keywords (a draft of 15 is in the daily config), the quick-commerce search queries, and any pincodes if the shared scrape is connected.
- Recipients, Drive folder, `report only` vs `report + recommendations`, and an owner for each agent.
- Scheduling: the plan says to schedule only after a few reviewed manual runs.
