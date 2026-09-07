#!/usr/bin/env python3
"""Exhaustive Google Analytics 4 Data API extraction.

    source ~/.config/mosaic-seo/env
    ~/.config/mosaic-seo/venv/bin/python3 .claude/seo/ga4-extract.py [days|--selftest]

Pulls everything the GA4 Data API v1beta exposes that is useful for organic
search work, writes the raw bundle to seo-reports/ga4/<date>.json, and prints a
gap analysis.

The Data API has exactly these surfaces and no more:
    properties.getMetadata        every dimension/metric this property allows,
                                  including custom event/user-scoped ones
    properties.runReport          the workhorse: <=9 dimensions, <=10 metrics,
                                  filters, ordering, multiple date ranges
    properties.batchRunReports    up to 5 runReports in one round trip
    properties.runPivotReport     same, pivoted; batchRunPivotReports batches it
    properties.runRealtimeReport  last 30 minutes, tiny dimension set
    properties.checkCompatibility which dims/metrics can legally co-occur
    properties.audienceExports    create/list *user-level* exports; requires a
                                  write call to create one, so not used here

Deliberately NOT available through the Data API, despite being in the UI — do
not promise them in a report:
    - search queries / keywords (that is Search Console, see gsc-extract.py)
    - which events are configured as key events, custom dimension config, data
      streams, retention settings (Admin API v1beta, a different service)
    - Explorations: funnel, path, segment overlap, cohort builder
      (funnels/segments are v1alpha only and unstable)
    - Google Ads cost/ROAS
    - the GSC query text. If the GA4<->Search Console link is live (it is on this
      property) the API does join organicGoogleSearch{Clicks,Impressions,
      ClickThroughRate,AveragePosition} onto landingPagePlusQueryString, but those
      metrics are incompatible with every session-scoped dimension, so they need
      their own report and can never be split by channel or device.
    - anything user-level or PII; rows can also be silently withheld by
      thresholding when Google Signals is on (we record that flag)
    - attribution model comparison and conversion paths

Freshness: GA4 event data is only "mostly complete" after ~24-48h, so this
script ends its window 2 days before today. Never trust the last two days.
"""
import datetime as dt
import json
import os
import pathlib
import subprocess
import sys

from google.oauth2 import service_account
from googleapiclient.discovery import build


def missing_months(months):
    """YYYYMM strings absent between the first and last observed month."""
    if not months:
        return []
    y, m, gaps = int(months[0][:4]), int(months[0][4:]), []
    while f"{y}{m:02d}" <= months[-1]:
        if f"{y}{m:02d}" not in months:
            gaps.append(f"{y}{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return gaps


if "--selftest" in sys.argv:
    assert missing_months([]) == []
    assert missing_months(["202601"]) == []
    assert missing_months(["202511", "202512", "202602"]) == ["202601"]
    assert missing_months(["202510", "202601"]) == ["202511", "202512"]
    print("selftest ok")
    sys.exit(0)

DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 90
SA = os.path.expanduser("~/.config/mosaic-seo/gcp-sa.json")
PID = os.environ.get("GA4_PROPERTY_ID") or sys.exit(
    "GA4_PROPERTY_ID not set — source ~/.config/mosaic-seo/env")
PROP = f"properties/{PID}"
ROOT = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                   capture_output=True, text=True).stdout.strip())

creds = service_account.Credentials.from_service_account_file(
    SA, scopes=["https://www.googleapis.com/auth/analytics.readonly"])
svc = build("analyticsdata", "v1beta", credentials=creds, cache_discovery=False).properties()

# GA4 processing lag is up to 48h; asking for yesterday returns a partial day.
END = (dt.date.today() - dt.timedelta(days=2)).isoformat()
START = (dt.date.today() - dt.timedelta(days=2 + DAYS)).isoformat()
RANGE = [{"startDate": START, "endDate": END}]
ORGANIC = "Organic Search"

bundle = {"property": PROP, "start": START, "end": END,
          "generated": dt.datetime.now().isoformat(timespec="seconds")}

print(f"GA4 extract — {PROP}   {START} .. {END}\n")


def report(dims, mets, *, ranges=None, dim_filter=None, limit=1000, order=None):
    """One runReport, flattened to {'rows': [...], 'meta': {...}} or {'error': ...}."""
    body = {"dateRanges": ranges or RANGE,
            "dimensions": [{"name": d} for d in dims],
            "metrics": [{"name": m} for m in mets],
            "limit": limit, "returnPropertyQuota": True,
            "keepEmptyRows": False}
    if dim_filter:
        body["dimensionFilter"] = dim_filter
    if order:
        body["orderBys"] = order
    elif mets:
        body["orderBys"] = [{"metric": {"metricName": mets[0]}, "desc": True}]
    try:
        r = svc.runReport(property=PROP, body=body).execute()
    except Exception as e:                       # noqa: BLE001 — surface, never mask
        return {"error": str(e)[:300], "dimensions": dims, "metrics": mets}
    dh = [d["name"] for d in r.get("dimensionHeaders", [])]
    mh = [m["name"] for m in r.get("metricHeaders", [])]
    rows = []
    for row in r.get("rows", []):
        d = dict(zip(dh, [v["value"] for v in row["dimensionValues"]]))
        for k, v in zip(mh, [v["value"] for v in row["metricValues"]]):
            d[k] = float(v) if "." in v or "Rate" in k or "average" in k else int(v)
        rows.append(d)
    return {"rows": rows, "rowCount": r.get("rowCount", 0),
            "totals": [[v["value"] for v in t["metricValues"]] for t in r.get("totals", [])],
            "meta": r.get("metadata", {}), "quota": r.get("propertyQuota", {})}


def channel_filter(value):
    return {"filter": {"fieldName": "sessionDefaultChannelGroup",
                       "stringFilter": {"matchType": "EXACT", "value": value}}}


# --- 1. metadata: what this property actually allows -------------------------
try:
    md = svc.getMetadata(name=f"{PROP}/metadata").execute()
except Exception as e:                            # noqa: BLE001
    sys.exit(f"getMetadata failed — check GA4 access for the service account: {e}")
bundle["metadata"] = {
    "dimension_count": len(md.get("dimensions", [])),
    "metric_count": len(md.get("metrics", [])),
    "custom_dimensions": [{"api": d["apiName"], "ui": d.get("uiName"),
                           "scope": d.get("customDefinition") and d.get("category")}
                          for d in md.get("dimensions", []) if d.get("customDefinition")],
    "custom_metrics": [{"api": m["apiName"], "ui": m.get("uiName")}
                       for m in md.get("metrics", []) if m.get("customDefinition")],
    "deprecated": [d["apiName"] for d in md.get("dimensions", []) + md.get("metrics", [])
                   if d.get("deprecatedApiNames")],
}

# --- 2. compatibility: prove the core report is legal before relying on it ---
CORE_DIMS = ["landingPagePlusQueryString", "sessionDefaultChannelGroup"]
CORE_METS = ["sessions", "engagedSessions", "engagementRate", "bounceRate",
             "averageSessionDuration", "screenPageViews", "keyEvents", "totalUsers"]
try:
    comp = svc.checkCompatibility(property=PROP, body={
        "dimensions": [{"name": d} for d in CORE_DIMS],
        "metrics": [{"name": m} for m in CORE_METS],
        "compatibilityFilter": "INCOMPATIBLE"}).execute()
except Exception as e:                            # noqa: BLE001
    comp = {"error": str(e)[:300]}
bundle["compatibility"] = comp

# --- 3. trend, channels, sources --------------------------------------------
SESSION_METS = ["sessions", "engagedSessions", "engagementRate", "bounceRate",
                "averageSessionDuration", "screenPageViews", "keyEvents",
                "totalUsers", "newUsers", "userEngagementDuration"]

bundle["daily"] = report(["date"], SESSION_METS[:8],
                         order=[{"dimension": {"dimensionName": "date"}}], limit=400)
bundle["monthly_lifetime"] = report(["yearMonth"], ["sessions", "totalUsers", "screenPageViews"],
                                    ranges=[{"startDate": "2015-08-14", "endDate": END}],
                                    order=[{"dimension": {"dimensionName": "yearMonth"}}])
bundle["channels"] = report(["sessionDefaultChannelGroup"], SESSION_METS)
bundle["source_medium"] = report(["sessionSourceMedium"], SESSION_METS[:8])
bundle["organic_source"] = report(["sessionSource"], SESSION_METS[:6],
                                  dim_filter=channel_filter(ORGANIC))

# --- 4. landing pages, sliced by channel ------------------------------------
# One report, sliced in Python: organic rows, all-channel rows and the SXO
# comparison all come out of the same pull.
bundle["landing_by_channel"] = report(
    ["landingPagePlusQueryString", "sessionDefaultChannelGroup"], SESSION_METS[:8], limit=2000)
bundle["landing_all"] = report(["landingPagePlusQueryString"], SESSION_METS[:8])
# If the property is linked to Search Console, the Data API joins GSC clicks /
# impressions / position onto landing pages. It never exposes the query itself.
bundle["gsc_linked_landing"] = report(
    ["landingPagePlusQueryString"],
    ["organicGoogleSearchClicks", "organicGoogleSearchImpressions",
     "organicGoogleSearchClickThroughRate", "organicGoogleSearchAveragePosition"])
bundle["site_search"] = report(["searchTerm"], ["eventCount"])
bundle["pages"] = report(["pagePath"],
                         ["screenPageViews", "sessions", "userEngagementDuration",
                          "engagementRate", "bounceRate", "totalUsers"])
bundle["page_title"] = report(["pageTitle"], ["screenPageViews", "sessions"])

# --- 5. audience splits, organic-only where it matters ----------------------
for name, dims in [("device", ["deviceCategory"]), ("country", ["country"]),
                   ("city", ["city"]), ("new_vs_returning", ["newVsReturning"]),
                   ("browser", ["browser"]), ("os", ["operatingSystem"]),
                   ("language", ["language"])]:
    bundle[name] = report(dims, SESSION_METS[:6])
    bundle[f"organic_{name}"] = report(dims, SESSION_METS[:6], dim_filter=channel_filter(ORGANIC))

# --- 6. events / key events --------------------------------------------------
bundle["events"] = report(["eventName"], ["eventCount", "keyEvents", "totalUsers"])
bundle["organic_events"] = report(["eventName"], ["eventCount", "keyEvents"],
                                  dim_filter=channel_filter(ORGANIC))
bundle["key_event_by_channel"] = report(
    ["sessionDefaultChannelGroup"], ["keyEvents", "sessionKeyEventRate", "sessions"])

# --- 7. week over week (two date ranges in one call) -------------------------
wow_ranges = [
    {"startDate": (dt.date.today() - dt.timedelta(days=8)).isoformat(),
     "endDate": END, "name": "current"},
    {"startDate": (dt.date.today() - dt.timedelta(days=15)).isoformat(),
     "endDate": (dt.date.today() - dt.timedelta(days=9)).isoformat(), "name": "prior"},
]
bundle["wow_channels"] = report(["sessionDefaultChannelGroup"], SESSION_METS[:6],
                                ranges=wow_ranges)
bundle["wow_landing_organic"] = report(["landingPagePlusQueryString"], ["sessions", "engagementRate"],
                                       ranges=wow_ranges, dim_filter=channel_filter(ORGANIC))

# --- 8. pivot + realtime -----------------------------------------------------
try:
    bundle["pivot_channel_device"] = svc.runPivotReport(property=PROP, body={
        "dateRanges": RANGE,
        "dimensions": [{"name": "sessionDefaultChannelGroup"}, {"name": "deviceCategory"}],
        "metrics": [{"name": "sessions"}, {"name": "engagementRate"}],
        "pivots": [{"fieldNames": ["sessionDefaultChannelGroup"], "limit": 20},
                   {"fieldNames": ["deviceCategory"], "limit": 5}],
    }).execute()
except Exception as e:                            # noqa: BLE001
    bundle["pivot_channel_device"] = {"error": str(e)[:300]}

try:
    bundle["realtime"] = svc.runRealtimeReport(property=PROP, body={
        "dimensions": [{"name": "unifiedScreenName"}, {"name": "country"}],
        "metrics": [{"name": "activeUsers"}], "limit": 50}).execute()
except Exception as e:                            # noqa: BLE001
    bundle["realtime"] = {"error": str(e)[:300]}

outdir = ROOT / "seo-reports" / "ga4"
outdir.mkdir(parents=True, exist_ok=True)
outfile = outdir / f"{dt.date.today().isoformat()}.json"
outfile.write_text(json.dumps(bundle, indent=1))

# --- gap analysis ------------------------------------------------------------
print(f"raw bundle -> {outfile.relative_to(ROOT)}\n")


def hdr(t):
    print(f"\n## {t}")


def rows(key):
    r = bundle.get(key) or {}
    return r.get("rows", []) if isinstance(r, dict) else []


def err(key):
    r = bundle.get(key) or {}
    return r.get("error") if isinstance(r, dict) else None


def pct(x):
    return f"{x * 100:5.1f}%"


def mmss(sec):
    return f"{int(sec) // 60}:{int(sec) % 60:02d}"


ch = rows("channels")
total_sessions = sum(r["sessions"] for r in ch)
organic = next((r for r in ch if r["sessionDefaultChannelGroup"] == ORGANIC), None)

hdr("Property scale (read this before believing any percentage below)")
print(f"  window          {START} .. {END}  ({DAYS} days, ends 2 days back for GA4 lag)")
print(f"  sessions        {total_sessions}")
print(f"  users           {sum(r['totalUsers'] for r in ch)}")
print(f"  custom dims     {bundle['metadata']['custom_dimensions'] or 'none'}")
print(f"  custom metrics  {bundle['metadata']['custom_metrics'] or 'none'}")
inc = [c.get("dimensionMetadata", c.get("metricMetadata", {})).get("apiName")
       for c in (bundle["compatibility"] or {}).get("dimensionCompatibilities", []) +
       (bundle["compatibility"] or {}).get("metricCompatibilities", [])]
print(f"  fields incompatible with the core landing-page report: {len(inc)} "
      "(all Ads/DV360/SA360/CM360, ecommerce item scope, cohorts, and the "
      "Search-Console-joined metrics — those need their own report)")
thr = (bundle.get("channels") or {}).get("meta", {})
if thr.get("subjectToThresholding"):
    print("  WARNING: rows withheld by thresholding (Google Signals) — counts are partial")
if thr.get("dataLossFromOtherRow"):
    print("  WARNING: cardinality overflow — some rows collapsed into (other)")
if total_sessions < 500:
    print(f"  NOTE: {total_sessions} sessions in {DAYS} days is a low-traffic property. "
          "Every split below is small-sample; treat single-page numbers as anecdotes, "
          "not signal. Do not compute CTR-style ratios on <30-session rows.")

hdr("Channel mix")
for r in ch:
    print(f"  {r['sessionDefaultChannelGroup']:18} sess={r['sessions']:5} "
          f"users={r['totalUsers']:5} new={r['newUsers']:5} eng={pct(r['engagementRate'])} "
          f"bounce={pct(r['bounceRate'])} avgdur={mmss(r['averageSessionDuration'])} "
          f"keyEvents={r['keyEvents']}")
if organic:
    share = organic["sessions"] / total_sessions if total_sessions else 0
    print(f"  organic share of sessions: {pct(share)}")
else:
    print("  no Organic Search sessions in the window at all")
ai = next((r for r in ch if "AI" in r["sessionDefaultChannelGroup"]), None)
if ai:
    print(f"  GA4 attributes {ai['sessions']} sessions to the 'AI Assistant' channel "
          "(ChatGPT/Perplexity/Copilot referrers) — that is the AEO/LLMO number")

hdr("Top organic sources")
for r in rows("organic_source")[:10]:
    print(f"  {r['sessionSource']:24} sess={r['sessions']:4} eng={pct(r['engagementRate'])} "
          f"bounce={pct(r['bounceRate'])}")

hdr("Organic landing pages")
lbc = rows("landing_by_channel")
org_lp = sorted([r for r in lbc if r["sessionDefaultChannelGroup"] == ORGANIC],
                key=lambda r: -r["sessions"])
if not org_lp:
    print("  none")
for r in org_lp:
    print(f"  sess={r['sessions']:4} eng={pct(r['engagementRate'])} bounce={pct(r['bounceRate'])} "
          f"dur={mmss(r['averageSessionDuration'])} views={r['screenPageViews']:4} "
          f"key={r['keyEvents']:3}  {r['landingPagePlusQueryString']}")

hdr("SXO findings — organic entries with weak engagement")
site_eng = (sum(r["engagedSessions"] for r in ch) / total_sessions) if total_sessions else 0
print(f"  site-wide engagement rate baseline: {pct(site_eng)}")
weak = [r for r in org_lp if r["sessions"] >= 3 and r["engagementRate"] < site_eng]
if weak:
    for r in sorted(weak, key=lambda r: r["engagementRate"]):
        gap = (site_eng - r["engagementRate"]) * 100
        print(f"  -{gap:4.1f}pp vs site   sess={r['sessions']:4} eng={pct(r['engagementRate'])} "
              f"dur={mmss(r['averageSessionDuration'])}  {r['landingPagePlusQueryString']}")
    print("  ^ these rank well enough to be entered from search and then fail to hold the "
          "visitor — content/intent mismatch, slow LCP, or a weak above-the-fold offer")
else:
    print("  no organic landing page with >=3 sessions underperforms the site baseline")

hdr("Landing pages: organic vs everything else")
by_lp = {}
for r in lbc:
    e = by_lp.setdefault(r["landingPagePlusQueryString"], {"organic": 0, "other": 0})
    e["organic" if r["sessionDefaultChannelGroup"] == ORGANIC else "other"] += r["sessions"]
for lp, e in sorted(by_lp.items(), key=lambda x: -(x[1]["organic"] + x[1]["other"]))[:25]:
    if e["organic"] + e["other"] < 2:
        continue                      # one-session ?fbclid=... permutations, not pages
    tag = "ORGANIC-DEPENDENT" if e["organic"] > e["other"] else ""
    print(f"  organic={e['organic']:4} other={e['other']:4}  {lp}  {tag}")
zero_org = [lp for lp, e in by_lp.items() if e["organic"] == 0 and e["other"] >= 5]
if zero_org:
    print("  entry pages with real traffic but ZERO organic entries "
          "(indexed? titled for search? linked internally?):")
    for lp in zero_org:
        print(f"    {lp}")

hdr("Search Console join (only present when the GA4<->GSC link is live)")
gsc = rows("gsc_linked_landing")
if err("gsc_linked_landing"):
    print(f"  not available: {err('gsc_linked_landing')}")
    print("  -> the property is not linked to Search Console; link it in GA4 Admin so landing")
    print("     pages carry clicks/impressions/position without a second API call")
elif not gsc:
    print("  link exists but returned no rows in this window")
else:
    org_sess = {r["landingPagePlusQueryString"]: r["sessions"] for r in org_lp}
    print("  clicks/impr/position come from GSC; sessions from GA4. A page with clicks but")
    print("  far fewer organic sessions is losing users before the tag fires (redirect, slow")
    print("  load, consent block) or GA4 is misattributing the entry.")
    for r in gsc[:20]:
        lp = r["landingPagePlusQueryString"]
        s = org_sess.get(lp, 0)
        flag = "  <-- clicks >> sessions" if r["organicGoogleSearchClicks"] >= 5 and \
            s < r["organicGoogleSearchClicks"] * 0.6 else ""
        print(f"  clk={r['organicGoogleSearchClicks']:5} imp={r['organicGoogleSearchImpressions']:6} "
              f"ctr={pct(r['organicGoogleSearchClickThroughRate'])} "
              f"pos={r['organicGoogleSearchAveragePosition']:5.1f} ga4sess={s:4}  {lp}{flag}")

hdr("Most-viewed pages (any entry point)")
for r in rows("pages")[:20]:
    per = r["userEngagementDuration"] / r["sessions"] if r["sessions"] else 0
    print(f"  views={r['screenPageViews']:5} sess={r['sessions']:4} eng={pct(r['engagementRate'])} "
          f"engdur/sess={mmss(per)}  {r['pagePath']}")

hdr("Device / country / new vs returning (all traffic | organic only)")
for name, key in [("device", "deviceCategory"), ("country", "country"),
                  ("new_vs_returning", "newVsReturning")]:
    org = {r[key]: r for r in rows(f"organic_{name}")}
    for r in rows(name)[:8]:
        o = org.get(r[key])
        os_ = f"org sess={o['sessions']:4} eng={pct(o['engagementRate'])}" if o else "org sess=   0"
        print(f"  {name:16} {r[key][:20]:20} all sess={r['sessions']:5} "
              f"eng={pct(r['engagementRate'])} | {os_}")

hdr("Events and key events")
for r in rows("events"):
    print(f"  {r['eventName']:22} count={r['eventCount']:6} keyEvents={r['keyEvents']:5}")
if not any(r["keyEvents"] for r in rows("events")):
    print("  NO key events recorded. GA4 cannot report conversions until an event is marked")
    print("  as a key event in Admin > Events (Data API can only read the keyEvents metric,")
    print("  it cannot list or create the configuration — that is the Admin API).")
    print("  Nothing here can be tied to a booking until then: no revenue, no conversion rate,")
    print("  no per-landing-page value. This is the single biggest gap in the property.")

ss = rows("site_search")
print(f"  site-search terms (searchTerm): {[(r['searchTerm'], r['eventCount']) for r in ss[:10]] or 'none — no on-site search tracked'}")

hdr("Week over week")
wow = {}
for r in rows("wow_channels"):
    wow.setdefault(r["sessionDefaultChannelGroup"], {})[r["dateRange"]] = r
for c, v in sorted(wow.items(), key=lambda x: -x[1].get("current", {}).get("sessions", 0)):
    cur = v.get("current", {}).get("sessions", 0)
    pri = v.get("prior", {}).get("sessions", 0)
    d = cur - pri
    print(f"  {c:18} current={cur:4} prior={pri:4} delta={d:+4} "
          f"({'n/a' if not pri else f'{d / pri * 100:+.0f}%'})")
print("  (7-day windows on a property this small: a swing of a few sessions is noise)")

hdr("Lifetime monthly sessions — data continuity")
ml = rows("monthly_lifetime")
for r in ml:
    print(f"  {r['yearMonth']}  sess={r['sessions']:5} users={r['totalUsers']:5} "
          f"views={r['screenPageViews']:6}")
gaps = missing_months([r["yearMonth"] for r in ml])
if gaps:
    print(f"  MISSING MONTHS (zero sessions recorded): {', '.join(gaps)} — either the tag "
          "was removed/broken or the site genuinely had no traffic; check the deploy history")

hdr("Realtime (last 30 min)")
rt = bundle.get("realtime") or {}
if rt.get("error"):
    print(f"  error: {rt['error']}")
elif not rt.get("rows"):
    print("  nobody on the site right now")
else:
    for row in rt["rows"][:10]:
        print(f"  {[v['value'] for v in row['dimensionValues']]} "
              f"active={row['metricValues'][0]['value']}")

hdr("Requests that failed")
bad = {k: err(k) for k in bundle if err(k)}
print("  " + ("none" if not bad else json.dumps(bad, indent=2)))

hdr("What GA4 still cannot tell you (pair with other sources)")
print("  - which query brought the session            -> gsc-extract.py (the GSC join above")
print("    gives clicks/impressions/position per landing page but never the query text)")
print("  - whether the page is indexed / rich results -> gsc-extract.py URL inspection")
print("  - Core Web Vitals of real users              -> CrUX / PageSpeed")
print("  - whether ChatGPT et al. can fetch the page  -> ai-visibility.sh")
print("  - key-event configuration, custom dim setup  -> GA4 Admin API (not this one)")
