#!/usr/bin/env python3
"""Resubmit sitemap.xml and sitemap-images.xml to Search Console, or list their state read-only.

    ~/.config/mosaic-seo/venv/bin/python3 .claude/seo/gsc-sitemap-submit.py --self-check
    ~/.config/mosaic-seo/venv/bin/python3 .claude/seo/gsc-sitemap-submit.py --submit

Replaces Google Indexing API submission for ordinary pages: that API is limited
to JobPosting and BroadcastEvent markup. A sitemap resubmit is the supported
way to tell Google that pages changed. Submission needs an explicit --submit.
"""
import os
import sys

from google.oauth2 import service_account
from googleapiclient.discovery import build

USAGE = "usage: gsc-sitemap-submit.py (--self-check | --submit)"
if len(sys.argv) != 2 or sys.argv[1] not in ("--self-check", "--submit"):
    print(USAGE, file=sys.stderr)
    sys.exit(2)
mode = sys.argv[1]

PROP = os.environ.get("GSC_PROPERTY")
if not PROP:
    print("GSC_PROPERTY not set — source ~/.config/mosaic-seo/env", file=sys.stderr)
    sys.exit(1)

SA = os.path.expanduser("~/.config/mosaic-seo/gcp-sa.json")
BASE = os.environ.get("SITE_URL", "https://www.mosaichostels.com").rstrip("/")
FEEDS = [f"{BASE}/sitemap.xml", f"{BASE}/sitemap-images.xml"]

creds = service_account.Credentials.from_service_account_file(
    SA, scopes=["https://www.googleapis.com/auth/webmasters"])
svc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)

if mode == "--submit":
    for feed in FEEDS:
        svc.sitemaps().submit(siteUrl=PROP, feedpath=feed).execute()
        print(f"submitted {feed}")

for sm in svc.sitemaps().list(siteUrl=PROP).execute().get("sitemap", []):
    print(f"{sm.get('path')}  lastSubmitted={sm.get('lastSubmitted')}  "
          f"errors={sm.get('errors')} warnings={sm.get('warnings')} "
          f"pending={sm.get('isPending')}")
