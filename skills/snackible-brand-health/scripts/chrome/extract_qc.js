// Quick-commerce extractor, run inside Claude in Chrome (javascript_tool) on Blinkit, Zepto or Instamart
// search results that are already on screen. It reads the visible text only.
//
// Run it ONCE per channel, prefixed with the brands to keep, e.g.
//   window.__qcBrands = ["Snackible"]; window.__qcFrom = 0;   <this file>
// That defines window.__qc() and runs it for the page on screen. For every further keyword, do NOT reload
// the page (a reload loses the function): type the keyword into the site's own search box, press Enter,
// wait about 4 seconds, and call `window.__qc()` again. One browser_batch can do all keywords:
//   [triple_click search box, type keyword, key Return, wait 4, javascript window.__qc()] x keywords.
//
// Only products whose name contains one of the brands come back (the browser tool cuts output at about
// 1,000 characters). `pos` is the product's position among organic (non-sponsored) results, so search
// rank can be worked out; `total` is how many products the page showed, so a page that failed to load
// (total 0) is distinguishable from a brand that is not in the results.
// Returns {"channel","query","from","total","items":[[name,weight,price,mrp,sponsored,pos],...]}.
// If a response ends in [TRUNCATED], set window.__qcFrom to its `from` and call window.__qc() again.
// Save all responses for a channel in ONE file as a JSON list; scripts/collectors/chrome_import.py reads it.
// Layouts change: if total is 0, report that channel as failed.
window.__qc = () => {
  const host = location.hostname;
  const channel = host.includes("blinkit") ? "Blinkit"
    : host.includes("zepto") ? "Zepto"
    : host.includes("swiggy") ? "Swiggy Instamart"
    : host.includes("bigbasket") ? "BigBasket" : host;
  const lines = document.body.innerText.split("\n").map(s => s.trim()).filter(Boolean);
  const isRupee = s => /^₹\s?[\d,]+(\.\d+)?$/.test(s);
  const isNum = s => /^[\d,]+(\.\d+)?$/.test(s);
  const rupee = s => parseFloat(s.replace(/[^\d.]/g, ""));
  const isWeight = s => /^(\d+\s*x\s*)?\d+(\.\d+)?\s*(g|gm|gms|kg|ml|l)\b/i.test(s) || /^1 pack \(/i.test(s);
  const all = [];

  if (channel === "Blinkit") {
    // ... name, weight, price, [mrp], ADD
    lines.forEach((l, i) => {
      if (l !== "ADD") return;
      let j = i - 1;
      const prices = [];
      while (j >= 0 && isRupee(lines[j]) && prices.length < 2) prices.unshift(rupee(lines[j--]));
      const weight = lines[j] && isWeight(lines[j]) ? lines[j--] : "";
      const name = lines[j] || "";
      if (name && prices.length) all.push([name, weight, prices[0], prices[1] || prices[0], false]);
    });
  } else if (channel === "Zepto") {
    // ADD, price, [mrp], name, [tags...], "1 pack (77 g)"
    lines.forEach((l, i) => {
      if (l !== "ADD") return;
      let j = i + 1;
      const prices = [];
      while (j < lines.length && isRupee(lines[j]) && prices.length < 2) prices.push(rupee(lines[j++]));
      const name = (lines[j] || "").split("|")[0].trim();
      let weight = "";
      for (let k = j + 1; k < Math.min(j + 6, lines.length); k++) {
        if (isWeight(lines[k])) { weight = lines[k]; break; }
        if (lines[k] === "ADD") break;
      }
      if (name && prices.length) all.push([name, weight, prices[0], prices[1] || prices[0], false]);
    });
  } else if (channel === "Swiggy Instamart") {
    // "NN MINS", name, [description...], weight, ["x% OFF"], price, [mrp], ["Ad"|"Sponsored"]
    const starts = lines.map((l, i) => (/^\d+\s*MINS?$/i.test(l) ? i : -1)).filter(i => i >= 0);
    starts.forEach((s, n) => {
      const end = starts[n + 1] ?? Math.min(lines.length, s + 14);
      const block = lines.slice(s + 1, end);
      const name = (block[0] || "").split("|")[0].trim();
      const w = block.findIndex(isWeight);
      if (!name || w < 0) return;
      const nums = block.slice(w + 1).filter(isNum).map(rupee);
      const sponsored = block.some(b => /^(ad|sponsored)$/i.test(b));
      if (nums.length) all.push([name, block[w], nums[0], nums[1] || nums[0], sponsored]);
    });
  }

  let organic = 0;
  all.forEach(it => { it.push(it[4] ? 0 : ++organic); });

  const norm = s => s.toLowerCase().replace(/[^a-z0-9 ]/g, "");
  const brands = (window.__qcBrands || []).map(norm);
  const keep = all.filter(it => !brands.length || brands.some(b => norm(it[0]).includes(b)));

  const from = window.__qcFrom || 0;
  const items = [];
  let size = 0;
  for (let i = from; i < keep.length; i++) {
    const it = [keep[i][0].slice(0, 44), keep[i][1].replace(/^1 pack /, ""), keep[i][2], keep[i][3], keep[i][4], keep[i][5]];
    const len = JSON.stringify(it).length + 1;
    if (size + len > 800 && items.length) break;
    items.push(it);
    size += len;
  }
  window.__qcFrom = from + items.length >= keep.length ? 0 : from + items.length;

  const sp = new URLSearchParams(location.search);
  const query = sp.get("q") || sp.get("query") || "";
  const loc = lines.find(l => /^(delivering to|deliver to|delivery to)/i.test(l)) || "";
  // The query is returned as its own field; a URL with ?q= in the output can be blocked by the browser tool.
  const out = { channel, query, from, total: all.length, items };
  if (loc) out.location = loc;
  return JSON.stringify(out);
};
window.__qc()
