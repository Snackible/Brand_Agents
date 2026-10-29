// Quick-commerce search-page extractor, run inside Claude in Chrome (javascript_tool).
// Works on blinkit.com, zeptonow.com and swiggy.com/instamart search pages that are already
// loaded. It reads the visible text only.
//
// Before running, prefix the call with the brands to keep, for example:
//   window.__qcBrands = ["Farmley", "Happilo"]; window.__qcFrom = 0;
// Only products whose name contains one of those brands come back, which keeps the output small
// (the browser tool truncates long output). `pos` is the product's position among the organic
// (non-sponsored) results, so search rank can still be computed; `total` is how many products
// the page showed, so "page failed to load" (total 0) is distinguishable from "brand not in results".
//
// Returns JSON: {"channel","query","from","total","items":[[name,weight,price,mrp,sponsored,pos],...]}
// The browser tool cuts output at about 1,000 characters, so a long result comes back in chunks: after the
// first run the function stays on the page, so for the next chunk just run `window.__qc()` again (it
// continues where it stopped). If a response ends in [TRUNCATED], set window.__qcFrom to that response's
// `from` and run `window.__qc()` again.
// Save every response to a file; scripts/collectors/chrome_import.py merges the chunks.
// Site layouts change: if total comes back 0, report that channel as failed.
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

  const brands = (window.__qcBrands || []).map(b => b.toLowerCase().replace(/[^a-z0-9 ]/g, ""));
  const keep = all.filter(it => !brands.length ||
    brands.some(b => it[0].toLowerCase().replace(/[^a-z0-9 ]/g, "").includes(b)));

  const from = window.__qcFrom || 0;
  const items = [];
  let size = 0;
  for (let i = from; i < keep.length; i++) {
    const it = [keep[i][0].slice(0, 60), keep[i][1], keep[i][2], keep[i][3], keep[i][4], keep[i][5]];
    const len = JSON.stringify(it).length + 1;
    if (size + len > 650 && items.length) break;
    items.push(it);
    size += len;
  }
  window.__qcFrom = from + items.length >= keep.length ? 0 : from + items.length;

  const sp = new URLSearchParams(location.search);
  const query = sp.get("q") || sp.get("query") || "";
  const loc = lines.find(l => /^(delivering to|deliver to|delivery to)/i.test(l)) || "";
  // Keep the wrapper small: the browser tool cuts output at about 1,000 characters in total.
  const out = { channel, query, from, total: all.length, items };
  if (loc) out.location = loc;
  return JSON.stringify(out);
};
window.__qc()
