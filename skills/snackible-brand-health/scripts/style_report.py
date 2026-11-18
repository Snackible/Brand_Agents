"""Turns the plain report HTML into a styled one, so reports look good in Google Docs without the agent
writing any styling. Google Docs keeps inline styles (fonts, colours, table borders and shading) but ignores
most stylesheet rules, so everything is applied inline here.

Used by assemble_report.py; it can also be run on its own:  python scripts/style_report.py in.html out.html
"""

import re
import sys

TEAL = "#0f766e"
INK = "#1f2937"
MUTED = "#6b7280"
RULE = "#d1d5db"
BAND = "#f3f4f6"
FONT = "font-family:Arial,Helvetica,sans-serif;"

STATUS = {  # cell text -> (background, text colour)
    "ok": ("#dcfce7", "#166534"),
    "partial": ("#fef3c7", "#92400e"),
    "failed": ("#fee2e2", "#991b1b"),
    "needs_login": ("#fee2e2", "#991b1b"),
    "not connected": ("#e5e7eb", "#374151"),
    "not collected": ("#e5e7eb", "#374151"),
}
CALLOUTS = {  # h2 title start -> (background, accent)
    "Needs attention today": ("#fff7ed", "#ea580c"),
    "Baseline: current issues": ("#fff7ed", "#ea580c"),
    "Top changes this week": ("#ecfdf5", TEAL),
    "Baseline: what stands out": ("#ecfdf5", TEAL),
}
NUMERIC = re.compile(r"^[+\-−]?\s*[₹]?\s*[\d,]+(\.\d+)?\s*(%|g|K|M)?(\s*\([+\-−]?\d+%\))?$")


def style_cell(inner, tag):
    t = re.sub(r"<[^>]+>", "", inner).strip()
    low = t.lower()
    css = f"{FONT}font-size:10pt;padding:5px 7px;border:1px solid {RULE};vertical-align:top;"
    if tag == "th":
        return css + f"background-color:{TEAL};color:#ffffff;font-weight:bold;text-align:left;"
    if low in STATUS:
        bg, fg = STATUS[low]
        return css + f"background-color:{bg};color:{fg};font-weight:bold;"
    if t == "NO":
        return css + "background-color:#fee2e2;color:#991b1b;font-weight:bold;text-align:center;"
    if t == "yes":
        return css + "color:#166534;text-align:center;"
    if re.match(r"^(down|dropped out)", low):
        return css + "color:#b91c1c;font-weight:bold;"
    if re.match(r"^(up |entered)", low):
        return css + "color:#15803d;font-weight:bold;"
    if re.match(r"^[-−]\s*[₹\d]", t) and ("%" in t or "₹" in t):
        return css + "color:#b91c1c;text-align:right;"
    if re.match(r"^\+\s*[₹\d]", t) and ("%" in t or "₹" in t):
        return css + "color:#15803d;text-align:right;"
    if NUMERIC.match(t):
        return css + "text-align:right;"
    return css


def column_widths(rows):
    """Percent width per column from the text length in it (long text gets more room)."""
    cols = max(len(r) for r in rows)
    score = []
    for c in range(cols):
        lens = [len(re.sub(r"<[^>]+>", "", r[c])) for r in rows if c < len(r)]
        avg = sum(lens) / len(lens) if lens else 1
        score.append(min(max(avg, 9), 60) ** 0.55)
    total = sum(score)
    return [max(9, round(x / total * 100)) for x in score]


def style_tables(html):
    html = html.replace("<table>", f"<table style='border-collapse:collapse;width:100%;margin:6px 0 10px 0;{FONT}'>")
    out, pos = [], 0
    for tm in re.finditer(r"<table[^>]*>.*?</table>", html, re.S):
        out.append(html[pos:tm.start()])
        tbl = tm.group(0)
        rows = [re.findall(r"<(?:td|th)>(.*?)</(?:td|th)>", r, re.S) for r in re.findall(r"<tr>(.*?)</tr>", tbl, re.S)]
        rows = [r for r in rows if r]
        widths = column_widths(rows) if rows and len(rows[0]) > 2 else None
        count = 0

        def tr(m):
            nonlocal count
            count += 1
            inner = m.group(1)
            is_head = "<th" in inner
            zebra = not is_head and count % 2 == 0
            col = [-1]

            def cell(c):
                col[0] += 1
                css = style_cell(c.group(2), c.group(1))
                if zebra and "background-color" not in css:
                    css += f"background-color:{BAND};"
                w = ""
                if widths and is_head and col[0] < len(widths):
                    w = f" width='{widths[col[0]]}%'"
                    css += f"width:{widths[col[0]]}%;"
                return f"<td{w} style='{css}'>{c.group(2)}</td>"
            return "<tr>" + re.sub(r"<(td|th)>(.*?)</\1>", cell, inner, flags=re.S) + "</tr>"

        out.append(re.sub(r"<tr>(.*?)</tr>", tr, tbl, flags=re.S))
        pos = tm.end()
    out.append(html[pos:])
    return "".join(out)


def kpi(html):
    """A table right after the h2 "At a glance" (header row = labels, second row = values) becomes a row of big-number tiles."""
    pat = re.compile(r"(<h2>At a glance</h2>\s*)<table>(.*?)</table>", re.S)

    def tiles(m):
        rows = re.findall(r"<tr>(.*?)</tr>", m.group(2), re.S)
        if len(rows) < 2:
            return m.group(0)
        labels = re.findall(r"<(?:td|th)>(.*?)</(?:td|th)>", rows[0], re.S)
        values = re.findall(r"<(?:td|th)>(.*?)</(?:td|th)>", rows[1], re.S)
        w = max(1, 100 // max(len(values), 1))
        cells = "".join(
            f"<td width='{w}%' style='background-color:#f0fdfa;border:1px solid #99f6e4;padding:10px 6px;text-align:center;width:{w}%;'>"
            f"<span style='{FONT}font-size:22pt;font-weight:bold;color:{TEAL};'>{v}</span><br>"
            f"<span style='{FONT}font-size:10pt;color:{MUTED};'>{l}</span></td>"
            for l, v in zip(labels, values))
        return m.group(1) + f"<table style='border-collapse:collapse;width:100%;margin:6px 0 12px 0;'><tr>{cells}</tr></table>"
    return pat.sub(tiles, html, count=1)


def callouts(html):
    for title, (bg, accent) in CALLOUTS.items():
        pat = re.compile(rf"(<h2>{re.escape(title)}[^<]*</h2>\s*)(<ol>.*?</ol>|<p>.*?</p>)", re.S)

        def wrap(m, bg=bg, accent=accent):
            body = m.group(2)
            body = body.replace("<li>", f"<li style='{FONT}font-size:12.5pt;line-height:1.5;margin-bottom:8px;color:{INK};'>")
            cell = (f"<table style='border-collapse:collapse;width:100%;margin:6px 0 12px 0;'><tr>"
                    f"<td style='background-color:{bg};border:1px solid {accent};padding:10px 14px;'>{body}</td></tr></table>")
            return m.group(1) + cell
        html = pat.sub(wrap, html, count=1)
    return html


def headings(html):
    def h1(m):
        return (f"<table style='border-collapse:collapse;width:100%;margin:0 0 6px 0;'><tr><td style='background-color:{TEAL};padding:14px 16px;'>"
                f"<span style='{FONT}font-size:24pt;font-weight:bold;color:#ffffff;'>{m.group(1)}</span></td></tr></table>")
    html = re.sub(r"<h1>(.*?)</h1>", h1, html, count=1, flags=re.S)
    html = re.sub(r"<h2>(.*?)</h2>", lambda m: f"<h2 style='{FONT}font-size:18pt;font-weight:bold;color:{TEAL};margin:20px 0 6px 0;'>{m.group(1)}</h2>", html, flags=re.S)
    html = re.sub(r"<h3>(.*?)</h3>", lambda m: f"<h3 style='{FONT}font-size:14pt;font-weight:bold;color:{INK};margin:14px 0 4px 0;'>{m.group(1)}</h3>", html, flags=re.S)
    return html


def text(html):
    html = re.sub(r"<p><i>(.*?)</i></p>", lambda m: f"<p style='{FONT}font-size:10.5pt;color:{MUTED};margin:2px 0 8px 0;'><i>{m.group(1)}</i></p>", html, flags=re.S)
    html = html.replace("<p>", f"<p style='{FONT}font-size:12pt;line-height:1.5;color:{INK};margin:4px 0 8px 0;'>")
    html = html.replace("<li>", f"<li style='{FONT}font-size:12pt;line-height:1.5;color:{INK};margin-bottom:5px;'>")
    html = html.replace("<a href=", f"<a style='color:{TEAL};' href=")
    return html


def style(html):
    m = re.search(r"<body>(.*)</body>", html, re.S)
    body = m.group(1) if m else html
    body = kpi(body)
    body = callouts(body)   # before headings: it looks for the plain <h2> titles
    body = headings(body)
    body = style_tables(body)
    body = text(body)
    return f"<html><head><meta charset='utf-8'></head><body style='{FONT}color:{INK};'>{body}</body></html>"


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    open(dst, "w", encoding="utf-8").write(style(open(src, encoding="utf-8").read()))
