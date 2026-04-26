#!/usr/bin/env python3
"""
build.py — Fetches fresh TLE data from Celestrak and injects it
into index.html. Run locally or via GitHub Actions weekly.
"""

import urllib.request
import json
import re
import sys
import time
from datetime import datetime, timezone

# ── Celestrak group URLs ──────────────────────────────────────────
GROUPS = {
    "stations": "https://celestrak.org/NORAD/elements/gp.php?GROUP=stations&FORMAT=JSON",
    "weather":  "https://celestrak.org/NORAD/elements/gp.php?GROUP=weather&FORMAT=JSON",
    "nav":      "https://celestrak.org/NORAD/elements/gp.php?GROUP=gnss&FORMAT=JSON",
    "starlink": "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=JSON",
    "oneweb":   "https://celestrak.org/NORAD/elements/gp.php?GROUP=oneweb&FORMAT=JSON",
    "science":  "https://celestrak.org/NORAD/elements/gp.php?GROUP=science&FORMAT=JSON",
    "debris":   "https://celestrak.org/NORAD/elements/gp.php?GROUP=1999-025&FORMAT=JSON",
}

# Max satellites per group to keep file size reasonable
MAX_PER_GROUP = {
    "stations": 20,
    "weather":  40,
    "nav":      60,
    "starlink": 120,
    "oneweb":   80,
    "science":  60,
    "debris":   40,
}

HEADERS = {
    "User-Agent": "OrbitWatch/1.0 (github-actions; educational)",
    "Accept": "application/json",
}


def fetch_group(key, url):
    """Fetch TLE JSON from Celestrak. Returns list of dicts."""
    print(f"  Fetching {key}...", end=" ", flush=True)
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8"))
        if not isinstance(data, list) or len(data) == 0:
            print(f"EMPTY")
            return []
        print(f"{len(data)} satellites")
        return data
    except Exception as e:
        print(f"FAILED ({e})")
        return []


def sats_to_js(key, sats, max_count):
    """Convert list of Celestrak JSON objects to JS array literal."""
    lines = [f"{key}:["]
    count = 0
    for sat in sats:
        if count >= max_count:
            break
        name  = sat.get("OBJECT_NAME", "").strip()
        line1 = sat.get("TLE_LINE1", "").strip()
        line2 = sat.get("TLE_LINE2", "").strip()
        if not name or not line1 or not line2:
            continue
        # Escape single quotes in name
        name = name.replace("'", "\\'")
        lines.append(f"['{name}','{line1}','{line2}'],")
        count += 1
    lines.append("],")
    print(f"    → wrote {count} satellites for {key}")
    return "\n".join(lines)


def build():
    # ── 1. Read template ────────────────────────────────────────
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        print("ERROR: index.html not found. Run this script from the repo root.")
        sys.exit(1)

    # ── 2. Fetch all groups ──────────────────────────────────────
    print("\n[1/3] Fetching TLE data from Celestrak...")
    fetched = {}
    total = 0
    for key, url in GROUPS.items():
        sats = fetch_group(key, url)
        fetched[key] = sats
        total += min(len(sats), MAX_PER_GROUP[key])
        time.sleep(1.0)   # be polite to Celestrak

    print(f"\n  Total satellites to embed: {total}")

    # ── 3. Build JS TLE_DB replacement ──────────────────────────
    print("\n[2/3] Building TLE_DB block...")
    js_groups = []
    for key in GROUPS:
        sats = fetched[key]
        if not sats:
            print(f"    Skipping {key} (no data fetched, keeping old data)")
            # Extract existing block for this group from current HTML so we
            # don't lose data on a partial failure
            m = re.search(
                rf"(?s){re.escape(key)}:\[.*?\],\n",
                html
            )
            if m:
                js_groups.append(m.group(0).rstrip(",\n"))
            continue
        js_groups.append(sats_to_js(key, sats, MAX_PER_GROUP[key]))

    new_db = "const TLE_DB = {\n" + "\n\n".join(js_groups) + "\n};"

    # ── 4. Inject into HTML ──────────────────────────────────────
    print("\n[3/3] Injecting into index.html...")

    # Replace TLE_DB block
    pattern = r"(?s)const TLE_DB = \{.*?\};"
    if not re.search(pattern, html):
        print("ERROR: Could not find 'const TLE_DB = {' in index.html")
        sys.exit(1)

    html = re.sub(pattern, new_db, html)

    # Update build timestamp comment in <title> or near top
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    # Inject/update a meta comment just after <head>
    stamp_comment = f"<!-- TLE data refreshed: {stamp} -->"
    if "<!-- TLE data refreshed:" in html:
        html = re.sub(r"<!-- TLE data refreshed:.*?-->", stamp_comment, html)
    else:
        html = html.replace("<head>", f"<head>\n{stamp_comment}", 1)

    # ── 5. Write output ──────────────────────────────────────────
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = len(html.encode()) // 1024
    print(f"\n✓ Done! index.html updated ({size_kb} KB, {total} satellites, {stamp})")


if __name__ == "__main__":
    build()
