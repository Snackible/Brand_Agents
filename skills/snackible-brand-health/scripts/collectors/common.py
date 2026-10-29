"""Shared helpers for the collectors: config parsing, snapshot rows, CSV output."""

import csv
import datetime as dt
import re
import sys

COLUMNS = ["snapshot_date", "module", "entity", "metric", "value", "unit", "source", "source_url", "notes"]
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")


def today():
    return dt.date.today().isoformat()


def md_table(config_path, heading):
    """Return the rows (as dicts) of the first markdown table under '## <heading>'."""
    text = open(config_path, encoding="utf-8").read()
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    if not m:
        return []
    header, rows = None, []
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if set("".join(cells)) <= set("-: "):
            continue
        if header is None:
            header = [c.lower() for c in cells]
            continue
        rows.append(dict(zip(header, cells)))
    return rows


def real(value):
    """Config cells still marked TODO (or empty) are not usable values."""
    return value if value and "TODO" not in value.upper() else ""


class Snapshot:
    """Collects rows for one run and writes them as a snapshot CSV."""

    def __init__(self, date=None):
        self.date = date or today()
        self.rows = []

    def add(self, module, entity, metric, value, unit="", source="", url="", notes=""):
        if value is None or value == "":
            return
        if isinstance(value, float):
            value = round(value, 2)
        self.rows.append([self.date, module, entity, metric, value, unit, source, url, notes])

    def status(self, module, entity, state, reason, source=""):
        """Record a collection failure so 'could not see it' is distinct from 'it disappeared'."""
        self.add(module, entity, "_collection_status", state, source=source, notes=reason)

    def write(self, path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(COLUMNS)
            w.writerows(self.rows)
        return path


def parse_grams(text):
    """Pack size in grams from strings like '75g', '1 kg', '4 x 18 g'. None if not found."""
    if not text:
        return None
    t = text.lower().replace(",", "")
    # "Pack of 4 (77g)": the size is per unit, so the pack total is 4 x 77g.
    m = re.search(r"pack of (\d+)\D{0,12}?(\d+(?:\.\d+)?)\s*(kg|gm|gms|g|gram|grams)\b", t)
    if m:
        return int(m.group(1)) * float(m.group(2)) * (1000 if m.group(3) == "kg" else 1)
    m = re.search(r"(\d+)\s*(?:x|×)\s*(\d+(?:\.\d+)?)\s*(kg|gm|gms|g|gram|grams)\b", t)
    if m:
        n, size, unit = int(m.group(1)), float(m.group(2)), m.group(3)
        return n * size * (1000 if unit == "kg" else 1)
    nutrition = re.compile(r"\s*(?:of\s+)?(protein|fibre|fiber|sugar|fat|carb|carbs|calories|added)")
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*(kg|gm|gms|g|gram|grams)\b", t):
        if nutrition.match(t[m.end():m.end() + 14]):
            continue  # "7g protein" is a nutrition fact, not the pack size
        return float(m.group(1)) * (1000 if m.group(2) == "kg" else 1)
    return None


def price_rows(snap, module, entity, mrp, selling, grams, source, url, notes=""):
    """Write the standard price metrics for one SKU."""
    snap.add(module, entity, "mrp", mrp, "INR", source, url, notes)
    snap.add(module, entity, "selling_price", selling, "INR", source, url, notes)
    if mrp and selling is not None and mrp > 0:
        snap.add(module, entity, "discount_pct", (mrp - selling) / mrp * 100, "%", source, url, notes)
    if grams and selling is not None:
        snap.add(module, entity, "price_per_100g", selling / grams * 100, "INR", source, url, notes)


def utf8_stdout():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
