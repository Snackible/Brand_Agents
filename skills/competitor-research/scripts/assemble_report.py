"""Joins the written part of the report with the detail tables and prints the Drive upload reference.

    python scripts/assemble_report.py weekly --data data/competitor --part reports/<date>/part1.html --out reports/<date>/report.html
    python scripts/assemble_report.py daily  --data data/brand_health --part reports/<date>/part1.html --out reports/<date>/report.html

`--part` is the HTML you wrote (title, summary, sections, data freshness, config gaps). The script appends the
"Detail tables" section built by detail_tables.py, wraps it as a full HTML page and saves it to `--out`.
It then prints one line, `FILE_REF sha256:<hash>:<absolute path>`. Pass that string as `base64Content` to the
Drive `create_file` call (with `contentMimeType` text/html) and the app uploads the file itself, so the tables
are never typed into a tool call.
"""

import argparse
import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["weekly", "daily"])
    ap.add_argument("--data", required=True)
    ap.add_argument("--part", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    det = subprocess.run([sys.executable, os.path.join(HERE, "detail_tables.py"), a.mode, "--data", os.path.abspath(a.data)],
                         capture_output=True, env=env, check=True, cwd=HERE).stdout.decode("utf-8")
    body = open(a.part, encoding="utf-8").read()
    html = f"<html><head><meta charset='utf-8'></head><body>\n{body}\n<h2>Detail tables</h2>\n{det}\n</body></html>"
    out = os.path.abspath(a.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)
    digest = hashlib.sha256(open(out, "rb").read()).hexdigest()
    print(f"wrote {out} ({len(html):,} characters)")
    print("FILE_REF sha256:" + digest + ":" + out.replace("\\", "/"))


if __name__ == "__main__":
    main()
