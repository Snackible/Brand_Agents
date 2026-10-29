#!/usr/bin/env python3
"""Compare the latest snapshot against the previous one and flag changes.

Input is one or more CSV files exported from the snapshot sheet (one tab per
module is fine; pass them all). Required columns:

    snapshot_date, module, entity, metric, value

Optional columns (passed through to the output): unit, source, source_url, notes

Thresholds are read from the "## Thresholds" markdown table in config.md, so
the Marketing team edits one human-readable file. Table columns:

    | module | metric | rule | value |

`module` and `metric` accept `*` as a wildcard. Supported rules:

    pct_change X     |change| >= X percent
    pct_drop X       fell by >= X percent
    pct_rise X       rose by >= X percent
    abs_change X     |change| >= X (absolute units)
    drop X           fell by >= X (absolute units)
    rise X           rose by >= X (absolute units)
    crosses_above X  moved from <= X to > X (or appeared already above X)
    crosses_below X  moved from >= X to < X (or appeared already below X)
    any_change       any change in value, numeric or text
    ignore_removed   (metric `*`) do not report entities that disappeared;
                     use for event-style modules such as news, where each
                     snapshot only holds what was found that week

New entities are always reported; entities that disappeared are reported
unless the module has an ignore_removed rule.

Usage:
    python diff_snapshots.py --config config.md snapshots/*.csv
    python diff_snapshots.py --config config.md --current 2026-10-29 --previous 2026-10-22 all.csv
    python diff_snapshots.py --config config.md --format json all.csv > diff.json
"""

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from fnmatch import fnmatch

REQUIRED = ["snapshot_date", "module", "entity", "metric", "value"]
# A module whose row count falls below this share of the previous snapshot is
# flagged as possibly partial (a scrape that broke halfway, a missing page).
PARTIAL_RATIO = 0.7


def read_rows(paths):
    rows = []
    for path in paths:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            header = [h.strip() for h in (reader.fieldnames or [])]
            missing = [c for c in REQUIRED if c not in header]
            if missing:
                sys.exit(f"{path}: missing columns {missing}")
            for raw in reader:
                row = {k.strip(): (v or "").strip() for k, v in raw.items() if k}
                if row.get("snapshot_date") and row.get("module"):
                    rows.append(row)
    return rows


def read_thresholds(config_path):
    """Parse the markdown table under a '## Thresholds' heading."""
    if not config_path:
        return []
    with open(config_path, encoding="utf-8") as f:
        text = f.read()
    m = re.search(r"^##\s+Thresholds\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    if not m:
        return []
    rules = []
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3 or cells[0].lower() == "module" or set(cells[0]) <= set("-: "):
            continue
        module, metric, rule = cells[0], cells[1], cells[2]
        value = cells[3] if len(cells) > 3 else ""
        try:
            value = float(value) if value else None
        except ValueError:
            value = None
        rules.append({"module": module, "metric": metric, "rule": rule, "value": value})
    return rules


def to_num(v):
    if v is None:
        return None
    s = str(v).replace(",", "").replace("₹", "").replace("%", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


def check_rule(rule, prev, cur):
    """Return a short reason string if the rule fires, else None."""
    kind, x = rule["rule"], rule["value"]
    p, c = to_num(prev), to_num(cur)
    if kind == "any_change":
        return "changed" if (prev or "") != (cur or "") else None
    if kind == "crosses_above" and c is not None and x is not None:
        if c > x and (p is None or p <= x):
            return f"now above {x:g}"
        return None
    if kind == "crosses_below" and c is not None and x is not None:
        if c < x and (p is None or p >= x):
            return f"now below {x:g}"
        return None
    if p is None or c is None or x is None:
        return None
    delta = c - p
    pct = (delta / p * 100) if p else None
    if kind == "abs_change" and abs(delta) >= x:
        return f"{delta:+g}"
    if kind == "drop" and -delta >= x:
        return f"{delta:+g}"
    if kind == "rise" and delta >= x:
        return f"{delta:+g}"
    if pct is not None:
        if kind == "pct_change" and abs(pct) >= x:
            return f"{pct:+.1f}%"
        if kind == "pct_drop" and -pct >= x:
            return f"{pct:+.1f}%"
        if kind == "pct_rise" and pct >= x:
            return f"{pct:+.1f}%"
    return None


def matching_rules(rules, module, metric):
    return [r for r in rules if fnmatch(module, r["module"]) and fnmatch(metric, r["metric"])]


def diff(rows, rules, current=None, previous=None):
    by_module = defaultdict(lambda: defaultdict(list))
    for r in rows:
        by_module[r["module"]][r["snapshot_date"]].append(r)

    result = {"current": current, "previous": previous, "modules": {}}
    for module, dates in sorted(by_module.items()):
        ordered = sorted(dates)
        cur_date = current if current in dates else (None if current else ordered[-1])
        if cur_date is None:
            result["modules"][module] = {"status": "no data for current date", "latest": ordered[-1]}
            continue
        if previous:
            prev_date = previous if previous in dates else None
        else:
            earlier = [d for d in ordered if d < cur_date]
            prev_date = earlier[-1] if earlier else None

        cur_rows = dates[cur_date]
        prev_rows = dates.get(prev_date, []) if prev_date else []
        cur = {(r["entity"], r["metric"]): r for r in cur_rows}
        prev = {(r["entity"], r["metric"]): r for r in prev_rows}
        cur_entities = {e for e, _ in cur}
        prev_entities = {e for e, _ in prev}

        flagged, minor = [], 0
        if prev_date:
            for e in sorted(cur_entities - prev_entities):
                sample = next(r for (en, _), r in cur.items() if en == e)
                flagged.append({"type": "new", "entity": e, "metric": "", "previous": "",
                                "current": sample["value"], "reason": "new entity",
                                "source_url": sample.get("source_url", "")})
            ignore_removed = any(r["rule"] == "ignore_removed" for r in matching_rules(rules, module, "*"))
            for e in sorted(set() if ignore_removed else prev_entities - cur_entities):
                sample = next(r for (en, _), r in prev.items() if en == e)
                flagged.append({"type": "removed", "entity": e, "metric": "",
                                "previous": sample["value"], "current": "",
                                "reason": "not seen in current snapshot",
                                "source_url": sample.get("source_url", "")})
        for key in sorted(set(cur) & set(prev) if prev_date else set(cur)):
            entity, metric = key
            c_val = cur[key]["value"]
            p_val = prev[key]["value"] if key in prev else None
            applicable = matching_rules(rules, module, metric)
            if not prev_date:
                # No baseline: only absolute rules ("now below 4.0") mean anything.
                applicable = [r for r in applicable if r["rule"] in ("crosses_above", "crosses_below")]
            reasons = [x for x in (check_rule(r, p_val, c_val) for r in applicable) if x]
            if reasons:
                flagged.append({"type": "changed", "entity": entity, "metric": metric,
                                "previous": p_val if p_val is not None else "", "current": c_val,
                                "reason": "; ".join(reasons),
                                "source_url": cur[key].get("source_url", "")})
            elif p_val is not None and p_val != c_val:
                minor += 1

        status = "ok"
        if not prev_date:
            status = "first snapshot (no baseline yet)"
        elif prev_rows and len(cur_rows) < PARTIAL_RATIO * len(prev_rows):
            status = f"possibly partial: {len(cur_rows)} rows vs {len(prev_rows)} previously"
        result["modules"][module] = {
            "status": status, "current_date": cur_date, "previous_date": prev_date,
            "rows_current": len(cur_rows), "rows_previous": len(prev_rows),
            "flagged": flagged, "minor_changes_below_threshold": minor,
        }
    return result


def cell(v):
    return str(v).replace("|", r"\|")


def to_markdown(result):
    out = []
    for module, m in result["modules"].items():
        if "flagged" not in m:
            out.append(f"## {module}\nStatus: {m['status']} (latest data {m.get('latest')})\n")
            continue
        out.append(f"## {module}")
        out.append(f"Status: {m['status']} | current {m['current_date']} ({m['rows_current']} rows)"
                   f" vs previous {m['previous_date']} ({m['rows_previous']} rows)"
                   f" | {m['minor_changes_below_threshold']} minor changes below threshold")
        if m["flagged"]:
            out.append("| type | entity | metric | previous | current | reason |")
            out.append("|---|---|---|---|---|---|")
            for f in m["flagged"]:
                out.append("| " + " | ".join(cell(f[k]) for k in ("type", "entity", "metric", "previous", "current", "reason")) + " |")
        else:
            out.append("No changes above threshold.")
        out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", nargs="+", help="snapshot CSV export(s)")
    ap.add_argument("--config", help="config.md containing a '## Thresholds' table")
    ap.add_argument("--current", help="snapshot_date to treat as current (default: latest per module)")
    ap.add_argument("--previous", help="snapshot_date to compare against (default: the one before current)")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    args = ap.parse_args()
    # Windows consoles default to cp1252, which can't print ₹ in passed-through values.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    result = diff(read_rows(args.csv), read_thresholds(args.config), args.current, args.previous)
    if args.format == "json":
        json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    else:
        print(to_markdown(result))


if __name__ == "__main__":
    main()
