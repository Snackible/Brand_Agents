# Competitor Weekly: Baseline, 29 Oct 2026

_First run, so there is no previous snapshot to compare against. This is the starting picture; from next week the report lists what changed. Modules: 1 fully collected, 3 partial, 5 not run or not connected (see Data freshness)._

## Baseline: what stands out

1. **Farmley is the heaviest advertiser we can see on Meta, and it is leaning on discounts.** 14 active ads found (a lower bound), 12 of them running longer than 7 days, the oldest 168 days. Six carry "10% OFF" and five push a discount code. Two new ads started 7 days ago: one with the hook "Still thinking about it?" and one with "Better snacking starts with better ingredients." [ad 1](https://www.facebook.com/ads/library/?id=4582206175439807), [ad 2](https://www.facebook.com/ads/library/?id=2949507202071858)

2. **Amazon discounting is deep across most of the set.** Median discount off MRP on the listings we read: Yoga Bar 28%, Farmley 23%, Open Secret 22%, Happilo 21%, The Whole Truth 15%, Too Yumm! 6%. Farmley's deepest listing is 52% off and Happilo's 46%. Yoga Bar has only 4 listings in the results, so treat its figure as thin.

3. **Farmley sells its 77g makhana at about 16–19% off MRP on quick commerce.** ₹200 on Blinkit and ₹193–200 on Zepto against an MRP of ₹239. The 20g packs sell at ₹35–47 against ₹50. Its price per 100g on quick commerce (median ₹246–260) is well above its own site (₹150) and Amazon (₹161), but that mostly reflects small packs, so it is not a like-for-like gap. [Blinkit search](https://blinkit.com/s/?q=roasted%20makhana)

4. **Customer ratings split into two groups.** Average rating across each brand's listings: The Whole Truth 4.24, Farmley 4.21, Happilo 4.15, then Open Secret 3.88, Too Yumm! 3.62 and Yoga Bar 3.52. The lowest single listings are 3.0 (Yoga Bar), 3.1 (Too Yumm!, Open Secret) and 3.6 (The Whole Truth).

5. **Happilo is already merchandising Diwali gifting on its own site.** A "Ramayana Gift Box, A Festive Diwali Hamper" at ₹3,300, plus dry-fruit celebration gift boxes from ₹220 to ₹1,912. [Happilo site](https://happilo.com)

6. **Yoga Bar and The Whole Truth are advertising protein, not snacking.** Yoga Bar has 29 ads found (lower bound), with the longest running 272 days; its hooks centre on whey and plant protein, including "26g Protein. ₹999." The Whole Truth has 18 ads, longest 143 days, with hooks such as "Drink protein. Not chemicals."

## By competitor

### Farmley
- **Ads:** 14 found, 12 live >7 days, offers "10% OFF" and a discount code.
- **Pricing:** D2C median ₹150 per 100g (45 variants); Amazon ₹161; Blinkit ₹260; Zepto ₹246. Amazon median discount 23%.
- **Rating:** 4.21 average over 15 Amazon listings.

### Happilo
- **Ads:** none found, but the search was incomplete (see Data freshness), so this is not a confirmed zero.
- **Pricing:** D2C median ₹158 per 100g across 171 variants; Amazon ₹139 per 100g, median 21% off; one Zepto listing at ₹250 per 100g.
- **Gifting:** festive and gift boxes listed on its site (see above).
- **Claims (observed):** "high protein" appears in 2 of 15 Amazon titles.

### The Whole Truth
- **Ads:** 18 found, all live >7 days.
- **Pricing:** Amazon median ₹413 per 100g (mostly protein bars); median discount 15%, up to 28%.
- **Claims (observed):** product titles mention whey (6 of 15), plant protein (2), "high protein" (2), "gluten free" (1) and "no palm oil" (1).
- **D2C site:** not collected; it is not a Shopify store.

### Yoga Bar, Too Yumm!, Open Secret
- **Yoga Bar:** 29 ads found (see above); Amazon median ₹108 per 100g, 4 listings only.
- **Too Yumm!:** 12 ads found, longest 44 days; Amazon median ₹57 per 100g, median 6% off; titles mention "no palm oil" (3 of 5).
- **Open Secret:** no ads found, but the search was incomplete; Amazon median ₹132 per 100g; titles mention "high protein", "no palm oil" and "baked" (2 each) and "no added sugar" and "no maida" (1 each).

## Data freshness

| module | status | note |
|---|---|---|
| D2C prices and SKUs | partial | Farmley and Happilo collected. The Whole Truth is not a Shopify store; Too Yumm!, Yoga Bar and Open Secret have no website set in the config |
| Amazon.in listings, prices, ratings | ok | top 15 listings per brand from search results (4 for Yoga Bar); the delivery location is the machine's default |
| Meta ad library | partial | all six brands hit the scroll limit. Counts are lower bounds, and Happilo and Open Secret returning zero is unreliable |
| Quick commerce (Blinkit, Zepto) | partial | one query ("roasted makhana") only; location is the browser's current one |
| Instamart | not run | readable in Chrome when signed in or when read promptly; not captured this run |
| BigBasket | not connected | blocks automated access |
| Instagram | not run | handles not set in the config, and the post feed needs a login |
| News, claims research, gifting research | partly run | claims and gifting above come from product titles and the D2C catalogues; no news search was done |
| Amazon review themes | not collected | review pages need a signed-in session |

## Config gaps

- Websites and Instagram handles for Too Yumm!, Yoga Bar and Open Secret; Instagram handles for the other three.
- Competitor list is still a draft and needs confirming.
- Report owner, recipients and Drive folder are unset, so this report was saved as a file and not emailed.

## Appendix

Raw snapshot files are in `data/competitor/2026-10-29/`.
