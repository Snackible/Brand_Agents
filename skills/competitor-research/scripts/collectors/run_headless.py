"""Run every headless collector for one agent and save the day's snapshot files.

    python run_headless.py weekly --config ../../config.md --data ../../../../data/competitor
    python run_headless.py daily  --config ../../config.md --data ../../../../data/brand_health

Each collector writes its own CSV under <data>/<date>/. A collector that crashes is recorded
as a failed module in <data>/<date>/_run.json and the others still run. The sources that need
the person's own browser (quick commerce, Instagram) are not run here; the skill collects
those through Claude in Chrome and adds their files to the same folder.
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from common import today, utf8_stdout

HERE = Path(__file__).parent


def run_one(name, args, out_dir, log):
    out = out_dir / f"{name}.csv"
    cmd = [sys.executable, str(HERE / args[0]), *args[1:], "--out", str(out)]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=1500)
        ok = p.returncode == 0 and out.exists()
        log[name] = {"ok": ok, "seconds": round(time.time() - t0), "output": (p.stdout + p.stderr).strip()[-600:]}
    except subprocess.TimeoutExpired:
        log[name] = {"ok": False, "seconds": round(time.time() - t0), "output": "timed out"}
    print(f"{name}: {'ok' if log[name]['ok'] else 'FAILED'} ({log[name]['seconds']}s)")


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument("agent", choices=["weekly", "daily"])
    ap.add_argument("--config", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--date", default=today())
    a = ap.parse_args()
    out_dir = Path(a.data) / a.date
    out_dir.mkdir(parents=True, exist_ok=True)
    cfg = a.config
    log = {}

    if a.agent == "weekly":
        run_one("d2c_competitors", ["shopify_d2c.py", "--config", cfg], out_dir, log)
        run_one("amazon_competitors", ["amazon_in.py", "competitors", "--config", cfg], out_dir, log)
        run_one("meta_ads", ["meta_ad_library.py", "--config", cfg], out_dir, log)
    else:
        site = "https://snackible.com"
        run_one("d2c_own", ["shopify_d2c.py", "--own", "--site", site, "--brand", "Snackible"], out_dir, log)
        run_one("amazon_own", ["amazon_in.py", "own", "--config", cfg], out_dir, log)
        run_one("amazon_rank", ["amazon_in.py", "rank", "--config", cfg], out_dir, log)
        run_one("mentions", ["mentions.py", "--brand", "Snackible"], out_dir, log)

    (out_dir / "_run.json").write_text(json.dumps(log, indent=2), encoding="utf-8")
    failed = [k for k, v in log.items() if not v["ok"]]
    print(f"done -> {out_dir}" + (f"; failed: {', '.join(failed)}" if failed else ""))
    sys.exit(0)


if __name__ == "__main__":
    main()
