#!/usr/bin/env python3
"""Exhaustive Google Search Console extraction.

    ~/.config/mosaic-seo/venv/bin/python3 .claude/seo/gsc-extract.py [days]

Pulls everything the Search Console API exposes, writes the raw bundle to
seo-reports/gsc/<date>.json, and prints a gap analysis.

The API has exactly four surfaces and no more:
    sites.list                  properties this credential can read
    sitemaps.list               submission state, errors, warnings
    searchanalytics.query       6 dimensions x 6 result types
    urlInspection.index.inspect per-URL index state + rich results

Deliberately NOT available through any API, despite being in the UI — do not
promise them in a report:
    - the aggregate Coverage / Page indexing report
    - the Enhancements reports (rich result summaries, breadcrumbs, FAQ, ...)
    - Core Web Vitals (use CrUX instead)
    - manual actions, security issues, links report, removals
URL Inspection is the closest substitute: it returns per-URL coverage state and
detected rich results, one URL at a time, capped at 2000 inspections/day.
"""
import datetime as dt
import json
import os
import pathlib
import re
import subprocess
import sys
import time

from google.oauth2 import service_account
from googleapiclient.discovery import build

DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 90
SA = os.path.expanduser("~/.config/mosaic-seo/gcp-sa.json")
PROP = os.environ.get("GSC_PROPERTY") or sys.exit("GSC_PROPERTY not set — source ~/.config/mosaic-seo/env")
ROOT = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                   capture_output=True, text=True).stdout.strip())

creds = service_account.Credentials.from_service_account_file(
    SA, scopes=["https://www.googleapis.com/auth/webmasters"])
svc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)

# GSC data lags ~2-3 days; asking for yesterday returns a misleading partial day.
END = (dt.date.today() - dt.timedelta(days=3)).isoformat()
START = (dt.date.today() - dt.timedelta(days=3 + DAYS)).isoformat()
bundle = {"property": PROP, "start": START, "end": END,
          "generated": dt.datetime.now().isoformat(timespec="seconds")}

print(f"GSC extract — {PROP}   {START} .. {END}\n")

# --- 1. sites ---------------------------------------------------------------
bundle["sites"] = svc.sites().list().execute().get("siteEntry", [])

# --- 2. sitemaps ------------------------------------------------------------
bundle["sitemaps"] = svc.sitemaps().list(siteUrl=PROP).execute().get("sitemap", [])

# --- 3. search analytics ----------------------------------------------------
def sa(dims, limit=1000, dtype="web"):
    try:
        return svc.searchanalytics().query(siteUrl=PROP, body={
            "startDate": START, "endDate": END, "dimensions": dims,
            "rowLimit": limit, "type": dtype}).execute().get("rows", [])
    except Exception as e:
        return {"error": str(e)[:200]}

bundle["search_analytics"] = {}
for name, dims in [("query", ["query"]), ("page", ["page"]), ("country", ["country"]),
                   ("device", ["device"]), ("searchAppearance", ["searchAppearance"]),
                   ("date", ["date"]), ("query_page", ["query", "page"]),
                   ("page_device", ["page", "device"]), ("date_country", ["date", "country"])]:
    bundle["search_analytics"][name] = sa(dims)

bundle["search_types"] = {t: sa(["date"], 500, t)
                          for t in ("web", "image", "video", "news", "discover", "googleNews")}

# --- 4. URL inspection ------------------------------------------------------
# Every sitemap URL, plus any URL GSC reports impressions for that the sitemap
# omits — those are exactly the ones nobody is watching.
sitemap_urls = re.findall(r"<loc>([^<]+)</loc>", (ROOT / "sitemap.xml").read_text())
rows = bundle["search_analytics"]["page"]
gsc_urls = [r["keys"][0] for r in rows if isinstance(rows, list) and "keys" in r]
targets = list(dict.fromkeys(sitemap_urls + gsc_urls))

bundle["url_inspection"] = {}
for i, u in enumerate(targets, 1):
    try:
        bundle["url_inspection"][u] = svc.urlInspection().index().inspect(body={
            "inspectionUrl": u, "siteUrl": PROP, "languageCode": "en-US"
        }).execute().get("inspectionResult", {})
    except Exception as e:
        bundle["url_inspection"][u] = {"error": str(e)[:200]}
    if i % 10 == 0:
        print(f"  inspected {i}/{len(targets)}")
    time.sleep(1.0)          # 600/min per property; 1/s is comfortably under

outdir = ROOT / "seo-reports" / "gsc"
outdir.mkdir(parents=True, exist_ok=True)
outfile = outdir / f"{dt.date.today().isoformat()}.json"
outfile.write_text(json.dumps(bundle, indent=1))

# --- gap analysis -----------------------------------------------------------
print(f"\nraw bundle -> {outfile.relative_to(ROOT)}\n")
sm = set(sitemap_urls)
pages = {r["keys"][0]: r for r in rows if isinstance(rows, list) and "keys" in r}

def hdr(t): print(f"\n## {t}")

hdr("Sitemaps")
for s in bundle["sitemaps"]:
    print(f"  {s.get('path')}  errors={s.get('errors',0)} warnings={s.get('warnings',0)} "
          f"lastSubmitted={s.get('lastSubmitted','?')[:10]}")

hdr("Indexation")
states = {}
for u, r in bundle["url_inspection"].items():
    cs = r.get("indexStatusResult", {}).get("coverageState", r.get("error", "?"))
    states.setdefault(cs, []).append(u)
for cs, us in sorted(states.items(), key=lambda x: -len(x[1])):
    print(f"  {len(us):3}  {cs}")
    if "indexed" not in cs.lower():
        for u in us:
            print(f"         {u}")

hdr("Rich results detected (Enhancements equivalent)")
rich = {}
for u, r in bundle["url_inspection"].items():
    for it in (r.get("richResultsResult") or {}).get("detectedItems", []):
        rich.setdefault(it.get("richResultType", "?"), []).append(u)
if rich:
    for t, us in sorted(rich.items(), key=lambda x: -len(x[1])):
        print(f"  {len(us):3}  {t}")
else:
    print("  none detected on any URL")
apps = bundle["search_analytics"]["searchAppearance"]
print(f"  searchAppearance rows: {len(apps) if isinstance(apps, list) else 'error'} "
      f"(0 means no rich result has ever appeared in a SERP)")

hdr("URLs with impressions but NOT in sitemap")
extra = {u: r for u, r in pages.items() if u not in sm}
for u, r in sorted(extra.items(), key=lambda x: -x[1]["impressions"]):
    ins = bundle["url_inspection"].get(u, {}).get("indexStatusResult", {})
    print(f"  imp={r['impressions']:5} clk={r['clicks']:3} pos={r['position']:5.1f}  "
          f"{u}  [{ins.get('coverageState','?')}]")
print("  (a URL that 301s to a canonical page is correct here — never add a redirect to a sitemap)")

hdr("In sitemap, zero impressions")
for u in sorted(sm - set(pages)):
    print(f"  {u}")

hdr("Striking distance (position 5-20)")
qs = bundle["search_analytics"]["query"]
if isinstance(qs, list):
    sd = [r for r in qs if "keys" in r and 5 <= r["position"] <= 20]
    for r in sorted(sd, key=lambda x: -x["impressions"])[:15]:
        print(f"  imp={r['impressions']:5} clk={r['clicks']:3} ctr={r['ctr']*100:5.1f}% "
              f"pos={r['position']:5.1f}  {r['keys'][0]}")

hdr("Ranked well but not clicked (position <=3, CTR <10%)")
if isinstance(qs, list):
    for r in sorted([r for r in qs if "keys" in r and r["position"] <= 3 and r["ctr"] < 0.10],
                    key=lambda x: -x["impressions"])[:15]:
        print(f"  imp={r['impressions']:5} clk={r['clicks']:3} ctr={r['ctr']*100:5.1f}% "
              f"pos={r['position']:5.1f}  {r['keys'][0]}")

hdr("Segments")
for k in ("device", "country"):
    seg = bundle["search_analytics"][k]
    if isinstance(seg, list):
        for r in sorted([x for x in seg if "keys" in x], key=lambda x: -x["impressions"])[:5]:
            print(f"  {k:8} {r['keys'][0]:10} imp={r['impressions']:6} clk={r['clicks']:4} "
                  f"ctr={r['ctr']*100:5.1f}% pos={r['position']:5.1f}")

hdr("Result types")
for t, rws in bundle["search_types"].items():
    if isinstance(rws, list):
        print(f"  {t:12} clicks={sum(r.get('clicks',0) for r in rws):5} "
              f"impressions={sum(r.get('impressions',0) for r in rws):7}")
