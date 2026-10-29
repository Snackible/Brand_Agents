# Modules: what to collect and how

Sections follow the plan's labels A–D, listed in build order (B, D, C, A). Entity names use ` | ` as separator and must stay **identical day to day**, because the diff matches rows on `entity` + `metric`. Use SKU, channel and keyword names exactly as written in `config.md`.

Contents: B reviews · D seo / seo_keywords · C mentions / mention_items · A listing / search_rank

---

## B. reviews

**Tracks:** new reviews and complaint themes per SKU, across Amazon.in, quick commerce (where reviews are visible), Snackible D2C and Google reviews.

**How:** for each SKU × channel, open the reviews sorted by most recent. Read reviews posted since the previous snapshot (and keep a 7-day window for theme counts). Tag negative (1–3 star) reviews into themes: `stale/rancid`, `too salty`, `too sweet`, `taste changed`, `small quantity`, `broken/crushed`, `packaging/leak`, `price/value`, `delivery/late`, `wrong item`, `foreign object`, `health concern`, `other`.

**Rows:**
- entity `<sku> | <channel>`: metrics `rating` (overall), `review_count` (total), `new_reviews_1d`, `negative_reviews_1d`.
- entity `<sku> | <channel> | theme:<theme>`: metric `count_7d` (negative reviews in the last 7 days mentioning the theme). notes: one short paraphrased example.
- Google reviews: entity `Google | <location>`; same metrics.

**Gotchas:**
- `foreign object` and `health concern` complaints go straight to "Needs attention today", even a single one, because they can turn into a food-safety or reputational issue. Paraphrase; never copy personal details of the reviewer into the report.
- Amazon shows ratings rounded to one decimal; use the exact value if a seller export is available.

---

## D. seo (site level) and seo_keywords

**Tracks:** GSC clicks, branded vs non-branded search, keyword positions, broken collection pages.

**Source:** Google Search Console for the property in `config.md` (connector, API export or a CSV the team drops in Drive). GSC data lags about 2 days, so report the latest complete day and say which day that is.

**Rows (`seo`):**
- entity `site`: metrics `clicks_7d`, `impressions_7d`, `ctr_7d_pct`, `avg_position_7d`, `branded_clicks_7d`, `nonbranded_clicks_7d`. Branded = queries containing "snackible" (and common misspellings such as "snakible" or "snackable", TODO confirm the list).
- entity `<collection or key page URL path>`: metric `http_status` (200 / 404 / 301…) and `product_count` (items shown on a collection). Check the main collections and top landing pages from GSC directly in the browser. A collection showing 0 products counts as broken even with status 200.

**Rows (`seo_keywords`):** entity `<keyword> | Google`, metric `position` (GSC average position, 7-day), `clicks_7d`.

**Why 7-day values:** daily GSC numbers swing with weekday patterns; rolling 7-day values make a real drop stand out.

---

## C. mentions and mention_items

**Tracks:** unprompted mentions and creator posts about Snackible on Instagram (tags, mentions), Reddit, X and YouTube.

**Sources:** the listening tool if one exists (`config.md` → Data feeds). Until then, public search: Instagram tagged posts and hashtag `#snackible`, Reddit search for "snackible", X search, YouTube search sorted by upload date. Public search is incomplete; say so in data freshness.

**Rows (`mentions`):** entity `<platform>`: metrics `mentions_1d`, `mentions_7d`, `negative_mentions_1d`, `creator_posts_7d` (accounts with roughly 10k+ followers or a clear creator profile).

**Rows (`mention_items`):** one per notable mention (creator post, negative thread, anything gaining traction). entity `<platform> | <post id or short url>`, metrics `sentiment` (positive / neutral / negative), `reach_hint` (followers, upvotes or views as shown), `summary` (one line, paraphrased).

**Gotchas:** exclude Snackible's own posts, paid collaborations Snackible ran (if marked as paid partnership, note it but don't count it as unprompted), and giveaway spam. A negative Reddit thread or video with rising engagement goes to "Needs attention today".

---

## A. listing and search_rank

**Tracks:** per SKU × channel × pincode: in stock, price vs MRP parity, title/image compliance, rating, review count; and search rank for the ~15 tracked keywords.

**Source:** the shared scrape for quick commerce (Blinkit, Zepto, Swiggy Instamart, BigBasket). Amazon and D2C can be read directly. Quick-commerce sites usually can't be reached from Claude's sandbox, so if the feed isn't connected, report "not connected" rather than attempting it.

**Rows (`listing`):** entity `<sku> | <channel> | <pincode>` (use `all` as pincode for channels without pincode pricing, e.g. D2C, Amazon):
- `in_stock` (1 / 0)
- `mrp`, `selling_price`, `discount_pct` = (mrp − selling_price) / mrp × 100
- `above_mrp` (1 if selling_price > MRP in config, else 0)
- `parity_gap_pct` = (selling_price − D2C selling price) / D2C selling price × 100
- `title_compliant`, `image_compliant` (1 / 0 against the rules in config; reason in notes when 0)
- `rating`, `review_count`

**Rows (`search_rank`):** entity `<keyword> | <channel> | <pincode>`, metric `rank` (organic position of the best-ranked Snackible SKU; record `99` if not in the first 3 pages / first 50 results), notes: which SKU ranked, and sponsored positions seen.

**Gotchas:** an item missing from a page isn't necessarily out of stock. Record `in_stock = 0` only when the page shows "out of stock" or "notify me"; if the page didn't load, write a `_collection_status` row instead. Volume is high (SKUs × channels × pincodes), so in the report summarise by SKU and channel and list pincodes only for issues.
