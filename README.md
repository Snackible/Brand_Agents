# Snackible Brand Agents

Two Claude agents for Snackible Marketing, built from [Marketing_Agents_Build_Plan.docx](Marketing_Agents_Build_Plan.docx).

| Agent | Skill | Cadence | What it reports |
|---|---|---|---|
| 1. Competitor Research | [`skills/competitor-research`](skills/competitor-research/SKILL.md) | Weekly | What changed across competitors: SKUs, price per 100g, Meta ads, Instagram content, claims, gifting, review complaints, news |
| 2. Snackible Brand Health | [`skills/snackible-brand-health`](skills/snackible-brand-health/SKILL.md) | Daily | Snackible's own listing health, reviews, mentions and SEO, led by "Needs attention today" |

## How they work

Both use the two-layer design from the plan:

1. **Data layer:** each run appends dated rows to a Google Sheet (one tab per module, long format: `snapshot_date, module, entity, metric, value, ...`). That sheet is the history.
2. **Claude layer:** the skill collects data, writes the snapshot, runs `scripts/diff_snapshots.py` to compare with the previous snapshot against the thresholds in `config.md`, and writes the report.
3. **Delivery:** a Google Doc plus an email draft to the configured recipients. Auto-send is off until the team has reviewed some manual runs.

```
skills/<agent>/
├── SKILL.md                     workflow Claude follows
├── config.md                    what the team edits: competitors / SKUs, modules on/off, thresholds, recipients
├── references/modules.md        per-module sources, collection steps, row naming
├── references/report-template.md
├── references/snapshot-schema.md
└── scripts/diff_snapshots.py    snapshot comparison (Python, standard library only)
dist/*.skill                     packaged skills, ready to upload
```

## Install in Marketing's Claude

Upload `dist/competitor-research.skill` and `dist/snackible-brand-health.skill` in claude.ai (Settings → Capabilities → Skills), or open the file card in Claude and click **Save skill**. The session needs web search, a browser, and Google Drive / Gmail connectors for the snapshot sheet, Doc and email draft.

After editing a skill, re-package it:

```bash
python -m scripts.package_skill skills/competitor-research dist
```

(run from the skill-creator skill folder), or zip the skill folder.

## Before the first run (Phase 0)

Every open decision is marked `TODO` in the two `config.md` files. The agents run without them and list the gaps at the end of each report. The ones that matter most:

- Confirm the competitor list (the current list is a draft) and their Instagram / Amazon handles.
- Snackible SKU list with MRP and pack size, the pincode set, and the ~15 tracked keywords (own / test / block).
- Shared scrape: owner, location, format, refresh rate. This unlocks `sku_tracker`, `price` and listing health.
- GSC property access and any listening tool for mentions.
- Create the two snapshot sheets and the Doc folder, and add their links.
- Recipients, and `report only` vs `report + recommendations`.

## Rollout (Phases 2–5)

1. **First milestone:** a manual run of Agent 1 (news, claims, gifting, Meta ads, Instagram), asking Claude to "run the weekly competitor report". Review it against what the team already knows.
2. Run it manually for two weeks and adjust thresholds in `config.md` to cut noise.
3. Agent 2: start with reviews (B) and SEO (D), then mentions (C), then listing health (A) once the feed is dependable.
4. Schedule only after the manual runs look right: Agent 1 weekly (e.g. Monday 9:00), Agent 2 daily (e.g. 8:30). Then name an owner for each agent in its `config.md`.
