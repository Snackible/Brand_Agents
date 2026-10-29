"""Check that this environment can run the agent, and say exactly how to fix what is missing.

    python scripts/preflight.py --config config.md --data data/competitor

Prints a checklist. Exit code 0 means every required check passed; 1 means something must be
fixed first. It installs nothing: the fix commands are for the person to approve and run.
"""

import argparse
import importlib
import re
import sys
from pathlib import Path

OK, BAD, WARN = "[ok]  ", "[FIX] ", "[note]"


def check_python():
    v = sys.version_info
    if v >= (3, 10):
        return True, f"Python {v.major}.{v.minor}.{v.micro}", ""
    return False, f"Python {v.major}.{v.minor} is too old", "Install Python 3.10 or newer from python.org"


def check_module(name, pip_name=None):
    try:
        importlib.import_module(name)
        return True, f"Python package '{pip_name or name}' installed", ""
    except Exception:
        return False, f"Python package '{pip_name or name}' missing", f"pip install {pip_name or name}"


def check_browser():
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        return False, "Playwright not importable, so the headless browser cannot be checked", "pip install playwright"
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(headless=True)
            b.close()
        return True, "Headless Chromium launches (Playwright)", ""
    except Exception as e:
        first = str(e).strip().splitlines()[0][:100] if str(e).strip() else "launch failed"
        return False, f"Headless Chromium will not start ({first})", "python -m playwright install chromium"


def check_data_dir(path):
    try:
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        t = p / ".write_test"
        t.write_text("ok", encoding="utf-8")
        t.unlink()
        n = len([d for d in p.iterdir() if d.is_dir()])
        msg = f"Data folder {p} is writable; {n} earlier snapshot day(s) found"
        if n == 0:
            msg += " (this run will be a baseline: changes show from the next run)"
        return True, msg, ""
    except Exception as e:
        return False, f"Cannot write to data folder {path} ({e})", "Pick a folder that persists between runs and pass it with --data"


def todo_count(config):
    try:
        text = Path(config).read_text(encoding="utf-8")
    except Exception:
        return None
    return len(re.findall(r"\bTODO\b", text))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.md")
    ap.add_argument("--data", required=True)
    a = ap.parse_args()

    required = [check_python(), check_module("requests"), check_module("playwright"), check_browser(), check_data_dir(a.data)]
    failed = 0
    for ok, msg, fix in required:
        print((OK if ok else BAD) + msg + (f"\n        fix: {fix}" if fix else ""))
        failed += 0 if ok else 1

    n = todo_count(a.config)
    if n is None:
        print(WARN + f"Config file {a.config} not found; run from the skill folder")
    elif n:
        print(WARN + f"{n} item(s) in {a.config} are still marked TODO. The agent runs without them and lists them as config gaps.")

    print(WARN + "Not checkable from here, and for Claude to confirm with the person: Google Drive and Gmail connectors enabled, "
          "and the Claude in Chrome extension connected (needed for Blinkit, Zepto, Instamart).")
    print("\nResult: " + ("ready" if not failed else f"{failed} thing(s) to fix before the first run"))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
