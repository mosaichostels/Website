#!/usr/bin/env python3
"""Bing keyword demand for ad-hoc seed phrases (read only).

    source ~/.config/mosaic-seo/env
    ~/.config/mosaic-seo/venv/bin/python3 .claude/seo/bing-keywords.py "varanasi hostel" "ganga aarti"

Why this exists: the mosaic-bing MCP's get_keyword_stats / get_related_keywords /
get_keyword_data send no country, language or date range, so Bing answers with
nothing. GetRelatedKeywords and GetKeyword work when those four parameters are
sent (same call as bing-extract.py section 6). Prints Bing impressions per
related phrase, highest first. GetKeyword is exact match: a phrase Bing has no
record of reads 0 and is not a sign the topic has no demand.
Never echoes the apikey.
"""
import datetime as dt
import os
import sys
import time

import requests

KEY = os.environ.get("BING_WEBMASTER_API_KEY") or sys.exit("BING_WEBMASTER_API_KEY not set")
BASE = "https://ssl.bing.com/webmaster/api.svc/json"
today = dt.date.today()
KW = {"country": "in", "language": "en-IN",
      "startDate": (today - dt.timedelta(days=90)).isoformat(), "endDate": today.isoformat()}


def api(method, **params):
    for attempt in range(4):
        r = requests.get(f"{BASE}/{method}", params={**params, "apikey": KEY},
                         headers={"User-Agent": "mosaic-seo/1.0"}, timeout=15)
        if r.status_code == 400 and "Throttle" in r.text and attempt < 3:
            time.sleep(8 * (attempt + 1))
            continue
        break
    if r.status_code != 200:
        return {"error": f"HTTP {r.status_code}"}
    return r.json().get("d")


for seed in sys.argv[1:] or sys.exit(__doc__):
    exact = api("GetKeyword", q=seed, **KW)
    rel = api("GetRelatedKeywords", q=seed, **KW)
    exact = exact if isinstance(exact, dict) and "error" not in exact else {}
    rel = rel if isinstance(rel, list) else []
    print(f"\n== {seed}: exact {exact.get('Impressions', 0)} impressions "
          f"(broad {exact.get('BroadImpressions', 0)}), {len(rel)} related")
    for k in sorted(rel, key=lambda k: -k.get("Impressions", 0))[:15]:
        print(f"  {k.get('Impressions', 0):>6} {k.get('BroadImpressions', 0):>6}  {k.get('Query')}")
