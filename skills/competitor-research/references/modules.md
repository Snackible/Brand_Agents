# Modules: what to collect and how

One section per module. Each lists the signal, sources, how to collect, the row conventions (see `snapshot-schema.md` for columns), and gotchas. Entity names use ` | ` as a separator and must be **stable from week to week**, because the diff matches rows by `entity` + `metric`. Use the brand name exactly as written in `config.md`.

Contents: news · claims · gifting · paid_ads · content · content_posts · reviews · sku_tracker · price

---

## news (v1, easy)

**Signal:** funding rounds, distribution deals (new retailers, exports, quick-commerce tie-ups), M&A, leadership changes, big campaigns or celebrity tie-ups, regulatory action (FSSAI etc.).

**Sources:** web search. Business press (Economic Times, Inc42, YourStory, Entrackr, Moneycontrol, Mint, Business Standard), brand press pages, LinkedIn public posts.

**How:** for each competitor search `"<brand>"` plus terms like `funding`, `raises`, `acquires`, `partnership`, `launch`, `distribution`, `FSSAI`, limited to the report week. Open the article to confirm the date and the facts; headlines exaggerate.

**Rows:** one per distinct story.
- entity: `<brand> | <short-slug-of-story>` (e.g. `Farmley | series-c-raise`). Reuse the same slug if the story is still developing next week, so it doesn't show as new.
- metric: `headline` · value: one-line factual summary · source_url: article.
- Optional extra rows: metric `amount_inr_cr` for funding size.

**Gotchas:** don't record the same story twice from two outlets. Record one row and mention the second source in `notes`. Ignore listicles and sponsored "best snacks" posts.

---

## claims (v1, easy)

**Signal:** new health or nutrition claims on packs, listings or the brand site ("high protein", "no palm oil", "baked not fried", "0g added sugar", "clinically…", "gut-friendly"). Useful competitive context given Snackible's own claim discipline.

**Sources:** brand D2C product pages, Amazon listing titles and bullet points, pack images where readable.

**How:** visit each competitor's bestsellers and new launches (from news / sku_tracker / ads). Note claims as written.

**Rows:** one per claim per product.
- entity: `<brand> | <product> | <claim in 2–5 words>`
- metric: `claim` · value: claim text verbatim (short) · source_url: page.
- notes: where it appears (title, bullet, pack front, ad).

**Gotchas:** observations only. Never judge validity or suggest what Snackible should claim. If you only checked some products this week, say which in the collection log, because unchecked products aren't "claims removed".

---

## gifting (v1, easy)

**Signal:** Diwali, festive and corporate gifting catalogues: new hampers, price points, minimum order quantities, customisation, bulk discounts, corporate landing pages and LinkedIn pushes. Most active Sept–Nov and around Rakhi / New Year.

**Sources:** brand sites (gifting / corporate pages), LinkedIn public posts, Amazon gift-box listings.

**Rows:** one per hamper or corporate offer.
- entity: `<brand> | <hamper or offer name>`
- metrics: `price_from` (₹), `min_order_qty`, `offer` (text, e.g. "10% off 50+ units"), `listed` (1).

---

## paid_ads (v1, medium)

**Signal:** new ads, hooks, offers, formats, and how long ads stay live. An ad running longer than ~7 days is probably performing.

**Sources:** Meta Ad Library (official and public). URL pattern:
`https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=IN&q=<brand>&search_type=keyword_unordered`
Prefer the brand's Page view once you know the page, because keyword search picks up resellers.

**How:** for each competitor, list active ads. For each ad note the library ID, start date, format (image / video / carousel), the hook (first line or opening of the video), and any offer or price. Use the browser; the library is slow, so wait for results to load and scroll.

**Rows:**
- Brand level: entity `<brand>`, metric `active_ads` (count).
- Ad level: entity `<brand> | <ad library id>`, metrics `days_live` (run date − start date), `format`, `hook` (text), `offer` (text or `none`), `product` (what's advertised).

**Gotchas:** the same creative often runs as several IDs. Group them in the report but keep the rows per ID. A removed ad ID means the ad stopped, which is a real signal; keep the row history. If the library won't load or blocks you, mark the module `failed` rather than guessing counts.

---

## content (v1, medium)

**Signal:** posting cadence, format mix, engagement trends.

**Sources:** public Instagram profiles (browser). Reuse the shared scrape if it covers Instagram.

**How:** for each competitor, look at posts from the last 7 days: count, how many are Reels, likes + comments per post. Engagement rate = (likes + comments) / followers × 100.

**Rows:** entity `<brand>`, metrics `posts_7d`, `reels_share_pct`, `avg_engagement_rate_pct`, `followers`.

**Gotchas:** Instagram often limits logged-out viewing. If you can only see part of the week, mark `partial` in notes and the collection log. Hidden like counts → leave `avg_engagement_rate_pct` empty, don't estimate.

## content_posts (v1, medium)

Top 3 posts per competitor in the week by engagement.
- entity: `<brand> | <post shortcode>` · metrics `engagement_rate_pct`, `format`, `theme` (2–5 words: "recipe", "founder story", "creator collab", "offer") · source_url: post link.

---

## reviews (v2, medium)

**Signal:** complaint themes on competitors' bestsellers, which point to gaps Snackible can use.

**Sources:** Amazon.in product reviews (most recent, 1–3 star focus).

**How:** for each competitor's top 2–3 bestsellers, read the 20–30 most recent reviews. Tag complaints into themes: `stale/rancid`, `too salty`, `too sweet`, `small quantity`, `broken/crushed`, `packaging`, `price/value`, `taste changed`, `delivery`, `foreign object`, `other`.

**Rows:**
- entity `<brand> | <product>`: metrics `rating`, `review_count`.
- entity `<brand> | <product> | theme:<theme>`: metric `share_pct` (share of the negative reviews you read that mention it), notes: one short paraphrased example (don't paste long review text).

---

## sku_tracker (v2, hard; needs the shared scrape)

**Signal:** new SKUs, delisted items, pack size changes, by channel.

**Source:** the shared scrape (see `config.md` → Shared scrape). Until it's connected, report "not connected".

**Rows:** entity `<brand> | <sku name> | <channel>`, metrics `listed` (1), `pack_size_g`. New and removed entities are the launches and delistings.

**Mapping from the shared scrape:** TODO, add the column mapping here once the scrape format is confirmed.

## price (v2, hard; needs the shared scrape)

**Signal:** MRP, selling price, discount depth and price per 100g, by channel.

**Rows:** entity `<brand> | <sku name> | <channel>` (same naming as sku_tracker), metrics `mrp`, `selling_price`, `discount_pct` = (mrp − selling_price) / mrp × 100, `price_per_100g` = selling_price / pack_size_g × 100.

**Gotchas:** compare like with like. Multipacks and combos distort price per 100g, so give them their own SKU name. Quick-commerce prices vary by pincode; take the pincode the shared scrape uses and note it.
